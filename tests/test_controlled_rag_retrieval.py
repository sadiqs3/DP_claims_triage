from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
import tempfile
import unittest

import numpy as np
import pandas as pd

from src.data_loader import load_runtime_data
from src.rag.corpus_builder import build_rag_corpus
from src.rag.faiss_index import (
    load_validated_faiss_semantic_index,
    persist_faiss_semantic_index,
)
from src.tools.controlled_rag_retrieval import (
    TOOL_NAME,
    TOOL_VERSION,
    run_controlled_rag_retrieval,
)
from src.tools.deterministic_triage import run_deterministic_triage


class FakeEmbeddingsEndpoint:
    """Return a fixed embedding vector without calling OpenAI."""

    def __init__(self, vector):
        self.vector = vector
        self.calls = []

    def create(self, input, model):
        texts = [input] if isinstance(input, str) else list(input)

        self.calls.append(
            {
                "input": texts,
                "model": model,
            }
        )

        return SimpleNamespace(
            data=[
                SimpleNamespace(
                    index=index,
                    embedding=self.vector,
                )
                for index, _ in enumerate(texts)
            ]
        )


class TestControlledRAGRetrievalTool(unittest.TestCase):
    """Tests the tool bridge from deterministic triage to RAG retrieval."""

    @classmethod
    def setUpClass(cls):
        cls.data = load_runtime_data()
        cls.corpus = build_rag_corpus(
            cls.data["rag_document_registry"].copy()
        )

        rng = np.random.default_rng(seed=20260709)
        cls.document_embeddings = rng.normal(
            size=(len(cls.corpus), 8),
        ).astype(np.float32)

        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.artifact_dir = cls.temp_dir.name

        persist_faiss_semantic_index(
            corpus=cls.corpus,
            document_embeddings=cls.document_embeddings,
            output_dir=cls.artifact_dir,
        )

        loaded_index = load_validated_faiss_semantic_index(
            corpus=cls.corpus,
            output_dir=cls.artifact_dir,
        )

        cls.known_query_vector = loaded_index.index.reconstruct(
            0
        ).tolist()

        cls.claim_id = str(
            cls.data["development_claims"]["claim_id"].iloc[0]
        )

        cls.triage_result = run_deterministic_triage(
            data=cls.data,
            claim_id=cls.claim_id,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def _fake_client(self):
        endpoint = FakeEmbeddingsEndpoint(self.known_query_vector)

        return SimpleNamespace(
            embeddings=endpoint,
        ), endpoint

    def test_retrieves_approved_guidance_for_valid_decision(self):
        fake_client, fake_endpoint = self._fake_client()

        result = run_controlled_rag_retrieval(
            data=self.data,
            claim_id=self.claim_id,
            deterministic_tool_result=self.triage_result,
            artifact_dir=self.artifact_dir,
            top_k=3,
            min_relevance_score=0.0,
            client=fake_client,
        )

        self.assertEqual(result["tool_name"], TOOL_NAME)
        self.assertEqual(result["tool_version"], TOOL_VERSION)
        self.assertEqual(result["claim_id"], self.claim_id)
        self.assertEqual(
            result["decision_source"],
            "deterministic_triage:rules_baseline_v1",
        )
        self.assertEqual(
            result["projection_source"],
            "authoritative_rag_facts_projection:v1",
        )
        self.assertEqual(
            result["retrieval_source"],
            "persisted_semantic_sop_retrieval:faiss_embedding_v1",
        )
        self.assertEqual(
            result["authority"],
            "non_authoritative_guidance",
        )
        self.assertEqual(result["retrieval_status"], "RESULTS_FOUND")
        self.assertEqual(result["retrieved_guidance_count"], 3)
        self.assertEqual(len(result["retrieved_guidance"]), 3)
        self.assertEqual(len(fake_endpoint.calls), 1)

    def test_controlled_query_excludes_identifiers_and_free_text(self):
        fake_client, _ = self._fake_client()

        result = run_controlled_rag_retrieval(
            data=self.data,
            claim_id=self.claim_id,
            deterministic_tool_result=self.triage_result,
            artifact_dir=self.artifact_dir,
            top_k=3,
            min_relevance_score=0.0,
            client=fake_client,
        )

        query_text = result["controlled_query"]["query_text"]

        claim_row = self.data["development_claims"][
            self.data["development_claims"]["claim_id"] == self.claim_id
        ].iloc[0]

        prohibited_values = [
            claim_row.get("claim_id"),
            claim_row.get("customer_id_provided"),
            claim_row.get("policy_id_provided"),
            claim_row.get("claimed_device_identifier"),
            claim_row.get("customer_statement"),
            self.triage_result["deterministic_decision"].get(
                "decision_reason"
            ),
        ]

        for value in prohibited_values:
            if value is None or pd.isna(value) or str(value).strip() == "":
                continue

            with self.subTest(value=value):
                self.assertNotIn(str(value), query_text)

    def test_claim_id_mismatch_raises_error(self):
        fake_client, _ = self._fake_client()

        other_claim_id = str(
            self.data["development_claims"]["claim_id"].iloc[1]
        )

        with self.assertRaisesRegex(
            ValueError,
            "claim_id does not match deterministic_decision claim_id",
        ):
            run_controlled_rag_retrieval(
                data=self.data,
                claim_id=other_claim_id,
                deterministic_tool_result=self.triage_result,
                artifact_dir=self.artifact_dir,
                client=fake_client,
            )

    def test_rejects_non_deterministic_tool_source(self):
        fake_client, _ = self._fake_client()

        bad_tool_result = deepcopy(self.triage_result)
        bad_tool_result["tool_name"] = "untrusted_tool"

        with self.assertRaisesRegex(
            ValueError,
            "must originate from deterministic_triage",
        ):
            run_controlled_rag_retrieval(
                data=self.data,
                claim_id=self.claim_id,
                deterministic_tool_result=bad_tool_result,
                artifact_dir=self.artifact_dir,
                client=fake_client,
            )

    def test_missing_rag_registry_raises_error(self):
        fake_client, _ = self._fake_client()

        incomplete_data = dict(self.data)
        incomplete_data.pop("rag_document_registry")

        with self.assertRaisesRegex(
            ValueError,
            "missing rag_document_registry",
        ):
            run_controlled_rag_retrieval(
                data=incomplete_data,
                claim_id=self.claim_id,
                deterministic_tool_result=self.triage_result,
                artifact_dir=self.artifact_dir,
                client=fake_client,
            )


if __name__ == "__main__":
    unittest.main()