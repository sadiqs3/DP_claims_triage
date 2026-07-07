import unittest

from src.rag.hybrid_retriever import ControlledHybridRetriever


CORPUS_FINGERPRINT = (
    "f73f827d3614e2987a7e976c687043f3fe9e2f5faeeb9c6555508089230ebf48"
)


def build_item(
    chunk_id: str,
    rank: int,
    score: float,
) -> dict:
    return {
        "rank": rank,
        "relevance_score": score,
        "chunk_id": chunk_id,
        "document_id": chunk_id.split("::")[0],
        "document_title": "Test SOP",
        "document_version": "1.0",
        "effective_date": "2026-06-23",
        "document_type": "TEST_GUIDANCE",
        "section_title": "Test section",
        "chunk_text": f"Guidance for {chunk_id}",
        "source_reference": {
            "source_relative_path": (
                "data/knowledge_base/test_document.md"
            ),
            "source_document_sha256": "a" * 64,
            "chunk_sha256": "b" * 64,
        },
    }


class StubLexicalRetriever:
    def __init__(
        self,
        results: list[dict],
        corpus_size: int = 21,
        corpus_fingerprint: str = CORPUS_FINGERPRINT,
    ) -> None:
        self.results = results
        self.corpus_size = corpus_size
        self.corpus_fingerprint = corpus_fingerprint
        self.calls = []

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict:
        self.calls.append(
            {
                "query": query,
                "top_k": top_k,
            }
        )

        selected_results = self.results[:top_k]

        return {
            "retrieval_status": (
                "RESULTS_FOUND"
                if selected_results
                else "NO_LEXICAL_MATCH"
            ),
            "results": selected_results,
        }


class StubSemanticRetriever:
    def __init__(
        self,
        results: list[dict],
        corpus_size: int = 21,
        corpus_fingerprint: str = CORPUS_FINGERPRINT,
    ) -> None:
        self.results = results
        self.corpus_size = corpus_size
        self.corpus_fingerprint = corpus_fingerprint
        self.calls = []

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_relevance_score: float = 0.20,
        client=None,
    ) -> dict:
        self.calls.append(
            {
                "query": query,
                "top_k": top_k,
                "min_relevance_score": min_relevance_score,
                "client": client,
            }
        )

        selected_results = self.results[:top_k]

        return {
            "retrieval_status": (
                "RESULTS_FOUND"
                if selected_results
                else "NO_SEMANTIC_MATCH_ABOVE_THRESHOLD"
            ),
            "results": selected_results,
        }


class TestControlledHybridRetriever(unittest.TestCase):

    def setUp(self):
        self.lexical_results = [
            build_item("KB-001::S03", rank=1, score=0.40),
            build_item("KB-002::S02", rank=2, score=0.30),
        ]

        self.semantic_results = [
            build_item("KB-001::S03", rank=1, score=0.75),
            build_item("KB-004::S03", rank=2, score=0.65),
        ]

        self.lexical_retriever = StubLexicalRetriever(
            self.lexical_results
        )

        self.semantic_retriever = StubSemanticRetriever(
            self.semantic_results
        )

        self.retriever = ControlledHybridRetriever(
            lexical_retriever=self.lexical_retriever,
            semantic_retriever=self.semantic_retriever,
        )

    def test_fuses_shared_candidate_and_preserves_method_metadata(self):
        result = self.retriever.retrieve(
            query="manual review escalation guidance",
            top_k=3,
            candidate_k=3,
        )

        self.assertEqual(
            result["retrieval_status"],
            "RESULTS_FOUND",
        )

        self.assertEqual(
            [item["chunk_id"] for item in result["results"]],
            [
                "KB-001::S03",
                "KB-002::S02",
                "KB-004::S03",
            ],
        )

        top_result = result["results"][0]

        self.assertEqual(
            top_result["retrieval_methods"],
            ["lexical", "semantic"],
        )

        self.assertEqual(
            top_result["method_ranks"],
            {
                "lexical": 1,
                "semantic": 1,
            },
        )

        self.assertAlmostEqual(
            top_result["fusion_score"],
            2 / 61,
            places=8,
        )

    def test_single_method_candidate_can_be_returned(self):
        lexical_retriever = StubLexicalRetriever(
            [
                build_item(
                    "KB-005::S03",
                    rank=1,
                    score=0.45,
                )
            ]
        )

        semantic_retriever = StubSemanticRetriever([])

        retriever = ControlledHybridRetriever(
            lexical_retriever=lexical_retriever,
            semantic_retriever=semantic_retriever,
        )

        result = retriever.retrieve(
            query="audit fields",
            top_k=3,
            candidate_k=3,
        )

        self.assertEqual(
            result["retrieval_status"],
            "RESULTS_FOUND",
        )

        self.assertEqual(result["result_count"], 1)

        item = result["results"][0]

        self.assertEqual(item["chunk_id"], "KB-005::S03")
        self.assertEqual(item["retrieval_methods"], ["lexical"])
        self.assertEqual(
            item["method_ranks"],
            {"lexical": 1},
        )

    def test_no_candidates_returns_no_hybrid_match(self):
        retriever = ControlledHybridRetriever(
            lexical_retriever=StubLexicalRetriever([]),
            semantic_retriever=StubSemanticRetriever([]),
        )

        result = retriever.retrieve(
            query="unknown topic",
            top_k=3,
            candidate_k=3,
        )

        self.assertEqual(
            result["retrieval_status"],
            "NO_HYBRID_MATCH",
        )

        self.assertEqual(result["result_count"], 0)
        self.assertEqual(result["results"], [])

    def test_constructor_rejects_mismatched_corpus_size(self):
        with self.assertRaisesRegex(
            ValueError,
            "same corpus size",
        ):
            ControlledHybridRetriever(
                lexical_retriever=StubLexicalRetriever(
                    [],
                    corpus_size=21,
                ),
                semantic_retriever=StubSemanticRetriever(
                    [],
                    corpus_size=20,
                ),
            )

    def test_constructor_rejects_mismatched_corpus_fingerprint(self):
        with self.assertRaisesRegex(
            ValueError,
            "same corpus fingerprint",
        ):
            ControlledHybridRetriever(
                lexical_retriever=StubLexicalRetriever(
                    [],
                    corpus_fingerprint="a" * 64,
                ),
                semantic_retriever=StubSemanticRetriever(
                    [],
                    corpus_fingerprint="b" * 64,
                ),
            )

    def test_candidate_k_must_be_valid_and_at_least_top_k(self):
        invalid_candidate_values = [0, -1, True, "5"]

        for candidate_k in invalid_candidate_values:
            with self.subTest(candidate_k=candidate_k):
                with self.assertRaisesRegex(
                    ValueError,
                    "candidate_k must be a positive integer",
                ):
                    self.retriever.retrieve(
                        query="guidance",
                        top_k=3,
                        candidate_k=candidate_k,
                    )

        with self.assertRaisesRegex(
            ValueError,
            "candidate_k must be greater than or equal to top_k",
        ):
            self.retriever.retrieve(
                query="guidance",
                top_k=3,
                candidate_k=2,
            )

    def test_top_k_validation_is_applied(self):
        for invalid_top_k in [0, -1, True, "3"]:
            with self.subTest(top_k=invalid_top_k):
                with self.assertRaisesRegex(
                    ValueError,
                    "top_k must be a positive integer",
                ):
                    self.retriever.retrieve(
                        query="guidance",
                        top_k=invalid_top_k,
                        candidate_k=3,
                    )

    def test_output_contains_verified_corpus_fingerprint(self):
        result = self.retriever.retrieve(
            query="guidance",
            top_k=2,
            candidate_k=2,
        )

        self.assertEqual(
            result["corpus_fingerprint"],
            CORPUS_FINGERPRINT,
        )

        self.assertEqual(
            self.retriever.corpus_fingerprint,
            CORPUS_FINGERPRINT,
        )


if __name__ == "__main__":
    unittest.main()