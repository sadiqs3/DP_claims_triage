import unittest
from types import SimpleNamespace

import numpy as np

from src.data_loader import load_runtime_data
from src.rag.corpus_builder import build_rag_corpus
from src.rag.semantic_retriever import (
    ControlledSemanticRetriever,
)

from src.rag.semantic_retriever import (
    ControlledSemanticRetriever,
    embed_approved_corpus_chunks,
)


class FakeEmbeddingsEndpoint:
    def __init__(self, vectors_by_text):
        self.vectors_by_text = vectors_by_text
        self.calls = []

    def create(self, input, model):
        input_texts = [input] if isinstance(input, str) else list(input)

        self.calls.append(
            {
                "input": input_texts,
                "model": model,
            }
        )

        return SimpleNamespace(
            data=[
                SimpleNamespace(
                    index=index,
                    embedding=self.vectors_by_text[text],
                )
                for index, text in enumerate(input_texts)
            ]
        )


class FakeEmbeddingClient:
    def __init__(self, vectors_by_text):
        self.embeddings = FakeEmbeddingsEndpoint(vectors_by_text)


class TestControlledSemanticRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data = load_runtime_data()

        cls.corpus = build_rag_corpus(
            data["rag_document_registry"]
        )

        cls.ordered_corpus = (
            cls.corpus.copy()
            .sort_values(
                by=[
                    "registry_priority",
                    "document_id",
                    "section_index",
                ],
                kind="stable",
            )
            .reset_index(drop=True)
        )

        cls.dimension = len(cls.ordered_corpus) + 1
        cls.vectors_by_text = {}

        for row_index, row in cls.ordered_corpus.iterrows():
            vector = np.zeros(cls.dimension, dtype=float)
            vector[row_index] = 1.0

            cls.vectors_by_text[row["chunk_text"]] = vector.tolist()

        cls.evidence_query = (
            "liquid exposure missing damage image "
            "evidence handling"
        )
        cls.manual_review_query = (
            "IMEI mismatch escalation packet "
            "analyst review"
        )
        cls.no_match_query = "unrelated query with no matching SOP"

        evidence_index = cls.ordered_corpus.index[
            cls.ordered_corpus["chunk_id"].eq("KB-002::S02")
        ][0]

        manual_review_index = cls.ordered_corpus.index[
            cls.ordered_corpus["chunk_id"].eq("KB-004::S03")
        ][0]

        evidence_vector = np.zeros(cls.dimension, dtype=float)
        evidence_vector[evidence_index] = 1.0

        manual_review_vector = np.zeros(cls.dimension, dtype=float)
        manual_review_vector[manual_review_index] = 1.0

        no_match_vector = np.zeros(cls.dimension, dtype=float)
        no_match_vector[-1] = 1.0

        cls.vectors_by_text[cls.evidence_query] = (
            evidence_vector.tolist()
        )
        cls.vectors_by_text[cls.manual_review_query] = (
            manual_review_vector.tolist()
        )
        cls.vectors_by_text[cls.no_match_query] = (
            no_match_vector.tolist()
        )

    def setUp(self):
        self.client = FakeEmbeddingClient(self.vectors_by_text)

        self.retriever = ControlledSemanticRetriever.from_openai(
            corpus=self.corpus,
            client=self.client,
        )

    def test_index_contains_all_approved_chunks(self):
        self.assertEqual(
            self.retriever.corpus_size,
            len(self.corpus),
        )
        self.assertEqual(
            self.retriever.embedding_dimension,
            self.dimension,
        )
        self.assertEqual(
            self.retriever.embedding_model,
            "text-embedding-3-small",
        )
        self.assertEqual(
            len(self.retriever.corpus_fingerprint),
            64,
        )

    def test_index_builds_in_one_batch_request(self):
        self.assertEqual(len(self.client.embeddings.calls), 1)

        call = self.client.embeddings.calls[0]

        self.assertEqual(
            call["model"],
            "text-embedding-3-small",
        )
        self.assertEqual(
            len(call["input"]),
            len(self.corpus),
        )

    def test_evidence_query_returns_expected_chunk_with_provenance(self):
        result = self.retriever.retrieve(
            query=self.evidence_query,
            top_k=3,
            client=self.client,
        )

        self.assertEqual(
            result["retrieval_status"],
            "RESULTS_FOUND",
        )
        self.assertEqual(
            result["results"][0]["chunk_id"],
            "KB-002::S02",
        )
        self.assertEqual(
            result["results"][0]["document_id"],
            "KB-002",
        )
        self.assertTrue(
            result["results"][0]["source_reference"][
                "source_relative_path"
            ].startswith("data/knowledge_base/")
        )

    def test_manual_review_query_returns_expected_chunk(self):
        result = self.retriever.retrieve(
            query=self.manual_review_query,
            top_k=3,
            client=self.client,
        )

        self.assertEqual(
            result["retrieval_status"],
            "RESULTS_FOUND",
        )
        self.assertEqual(
            result["results"][0]["chunk_id"],
            "KB-004::S03",
        )
        self.assertEqual(
            result["results"][0]["section_title"],
            "Required escalation packet",
        )

    def test_no_match_returns_empty_results_above_threshold(self):
        result = self.retriever.retrieve(
            query=self.no_match_query,
            top_k=3,
            min_relevance_score=0.20,
            client=self.client,
        )

        self.assertEqual(
            result["retrieval_status"],
            "NO_SEMANTIC_MATCH_ABOVE_THRESHOLD",
        )
        self.assertEqual(result["result_count"], 0)
        self.assertEqual(result["results"], [])

    def test_query_embedding_dimension_must_match_index(self):
        invalid_query = "invalid embedding dimension"

        self.vectors_by_text[invalid_query] = [1.0, 0.0]

        with self.assertRaisesRegex(
            ValueError,
            "Query embedding dimension does not match index dimension",
        ):
            self.retriever.retrieve(
                query=invalid_query,
                client=self.client,
            )

    def test_invalid_threshold_is_rejected(self):
        for invalid_threshold in [-0.1, 1.1, True, "0.2"]:
            with self.subTest(
                min_relevance_score=invalid_threshold
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "min_relevance_score must be a number between 0 and 1",
                ):
                    self.retriever.retrieve(
                        query=self.evidence_query,
                        min_relevance_score=invalid_threshold,
                        client=self.client,
                    )

    def test_retrieval_is_deterministic(self):
        first_result = self.retriever.retrieve(
            query=self.manual_review_query,
            top_k=3,
            client=self.client,
        )

        second_result = self.retriever.retrieve(
            query=self.manual_review_query,
            top_k=3,
            client=self.client,
        )

        first_view = [
            (
                item["rank"],
                item["chunk_id"],
                item["relevance_score"],
            )
            for item in first_result["results"]
        ]

        second_view = [
            (
                item["rank"],
                item["chunk_id"],
                item["relevance_score"],
            )
            for item in second_result["results"]
        ]

        self.assertEqual(first_view, second_view)

class TestApprovedCorpusEmbeddingHelper(unittest.TestCase):
    """Tests the reusable approved-KB embedding helper only."""

    @classmethod
    def setUpClass(cls):
        runtime_data = load_runtime_data()
        cls.corpus = build_rag_corpus(
            runtime_data["rag_document_registry"].copy()
        )

    def test_embeds_ordered_approved_corpus_chunks(self):
        """Embeddings must align to the deterministic approved corpus order."""

        class FakeEmbeddingsEndpoint:
            def __init__(self):
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
                            embedding=[
                                float(index + 1),
                                float(index + 2),
                                float(index + 3),
                            ],
                        )
                        for index, _ in enumerate(texts)
                    ]
                )

        fake_endpoint = FakeEmbeddingsEndpoint()
        fake_client = SimpleNamespace(embeddings=fake_endpoint)

        prepared_corpus, embeddings = embed_approved_corpus_chunks(
            corpus=self.corpus,
            client=fake_client,
        )

        expected_corpus = (
            self.corpus.sort_values(
                by=[
                    "registry_priority",
                    "document_id",
                    "section_index",
                ],
                kind="stable",
            )
            .reset_index(drop=True)
        )

        self.assertEqual(
            prepared_corpus["chunk_id"].tolist(),
            expected_corpus["chunk_id"].tolist(),
        )
        self.assertEqual(
            embeddings.shape,
            (len(expected_corpus), 3),
        )

        self.assertEqual(len(fake_endpoint.calls), 1)
        self.assertEqual(
            fake_endpoint.calls[0]["input"],
            expected_corpus["chunk_text"].tolist(),
        )

        np.testing.assert_array_equal(
            embeddings[0],
            np.array([1.0, 2.0, 3.0], dtype=np.float32),
        )

if __name__ == "__main__":
    unittest.main()