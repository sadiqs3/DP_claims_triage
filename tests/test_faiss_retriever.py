import tempfile
import unittest
from dataclasses import replace
from types import SimpleNamespace

import numpy as np

from src.data_loader import load_runtime_data
from src.rag.controlled_query_builder import (
    AuthoritativeTriageFacts,
    ControlledRAGQueryBuilder,
)
from src.rag.corpus_builder import build_rag_corpus
from src.rag.faiss_index import (
    load_validated_faiss_semantic_index,
    persist_faiss_semantic_index,
)
from src.rag.faiss_retriever import (
    ControlledPersistedFAISSRetriever,
)


class FakeEmbeddingsEndpoint:
    """Returns a fixed embedding vector without calling the OpenAI API."""

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


class TestControlledPersistedFAISSRetriever(unittest.TestCase):
    """Tests persisted analyst-guidance retrieval and its input boundary."""

    @classmethod
    def setUpClass(cls):
        runtime_data = load_runtime_data()

        cls.corpus = build_rag_corpus(
            runtime_data["rag_document_registry"].copy()
        )

        rng = np.random.default_rng(seed=20260707)

        cls.document_embeddings = rng.normal(
            size=(len(cls.corpus), 8),
        ).astype(np.float32)

        cls.facts = AuthoritativeTriageFacts(
            claim_type="ACCIDENTAL_DAMAGE",
            incident_category="SCREEN_DAMAGE",
            coverage_outcome="ELIGIBLE",
            evidence_state="MISSING_REQUIRED",
            manual_review_required=True,
            product_family="SMARTPHONE",
            required_evidence_codes=(
                "DAMAGE_PHOTOS",
                "PROOF_OF_PURCHASE",
            ),
            manual_review_reason_codes=("SERIAL_MISMATCH",),
        )

        cls.controlled_query = (
            ControlledRAGQueryBuilder().build(cls.facts)
        )

    def setUp(self):
        # Each test gets an isolated persisted index artifact.
        self.temporary_directory = tempfile.TemporaryDirectory()

        persist_faiss_semantic_index(
            corpus=self.corpus,
            document_embeddings=self.document_embeddings,
            output_dir=self.temporary_directory.name,
        )

        self.loaded_index = load_validated_faiss_semantic_index(
            corpus=self.corpus,
            output_dir=self.temporary_directory.name,
        )

        self.retriever = ControlledPersistedFAISSRetriever(
            self.loaded_index
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_retrieves_from_valid_controlled_query(self):
        """A valid controlled query retrieves approved KB metadata only."""
        known_query_vector = self.loaded_index.index.reconstruct(0)

        fake_endpoint = FakeEmbeddingsEndpoint(
            known_query_vector.tolist()
        )
        fake_client = SimpleNamespace(embeddings=fake_endpoint)

        response = self.retriever.retrieve(
            query=self.controlled_query,
            top_k=3,
            min_relevance_score=0.0,
            client=fake_client,
        )

        self.assertEqual(
            response["retrieval_status"],
            "RESULTS_FOUND",
        )
        self.assertEqual(response["result_count"], 3)
        self.assertEqual(
            response["results"][0]["chunk_id"],
            self.loaded_index.corpus.iloc[0]["chunk_id"],
        )
        self.assertEqual(
            response["query_source"],
            "authoritative_deterministic_triage_facts",
        )
        self.assertEqual(response["audience"], "analyst")
        self.assertEqual(
            response["authority"],
            "non_authoritative_guidance",
        )
        self.assertEqual(
            fake_endpoint.calls[0]["input"],
            [self.controlled_query.query_text],
        )

    def test_rejects_raw_text_input_before_embedding(self):
        """Raw text cannot bypass the controlled query-builder boundary."""
        with self.assertRaisesRegex(
            TypeError,
            "ControlledRAGQuery",
        ):
            self.retriever.retrieve(
                query="Customer says the phone screen is cracked.",
            )

    def test_rejects_tampered_query_fingerprint_before_embedding(self):
        """Modified query text/fingerprint combinations must be rejected."""
        tampered_query = replace(
            self.controlled_query,
            query_fingerprint="tampered",
        )

        with self.assertRaisesRegex(
            ValueError,
            "fingerprint",
        ):
            self.retriever.retrieve(query=tampered_query)

    def test_rejects_query_embedding_dimension_mismatch(self):
        """A query vector incompatible with the index must not be searched."""
        wrong_dimension_vector = [1.0] * 7

        fake_endpoint = FakeEmbeddingsEndpoint(
            wrong_dimension_vector
        )
        fake_client = SimpleNamespace(embeddings=fake_endpoint)

        with self.assertRaisesRegex(
            ValueError,
            "dimension does not match persisted index",
        ):
            self.retriever.retrieve(
                query=self.controlled_query,
                client=fake_client,
            )

    def test_rejects_query_with_non_authoritative_boundary_changed(self):
        """Analyst-only and non-authoritative labels are enforced."""
        altered_query = replace(
            self.controlled_query,
            authority="authoritative_decision",
        )

        with self.assertRaisesRegex(
            ValueError,
            "non-authoritative",
        ):
            self.retriever.retrieve(query=altered_query)


if __name__ == "__main__":
    unittest.main()