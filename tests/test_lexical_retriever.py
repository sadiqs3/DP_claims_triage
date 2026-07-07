import unittest

from src.data_loader import load_runtime_data
from src.rag.corpus_builder import build_rag_corpus
from src.rag.lexical_retriever import ControlledLexicalRetriever


class TestControlledLexicalRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_runtime_data()

        cls.corpus = build_rag_corpus(
            cls.data["rag_document_registry"]
        )

        cls.retriever = ControlledLexicalRetriever(cls.corpus)

    def test_evidence_query_returns_approved_guidance_with_provenance(self):
        result = self.retriever.retrieve(
            query=(
                "liquid damage missing required photo "
                "evidence follow-up guidance"
            ),
            top_k=3,
        )

        self.assertEqual(result["retrieval_status"], "RESULTS_FOUND")
        self.assertEqual(result["tool_name"], "lexical_sop_retrieval")
        self.assertEqual(result["tool_version"], "tfidf_v1")
        self.assertEqual(result["result_count"], 3)

        self.assertTrue(
            any(
                item["document_id"] == "KB-002"
                for item in result["results"]
            )
        )

        self.assertTrue(
            all(
                item["source_reference"][
                    "source_relative_path"
                ].startswith("data/knowledge_base/")
                for item in result["results"]
            )
        )

        self.assertTrue(
            all(
                item["section_title"].casefold()
                != "examples of targeted requests"
                for item in result["results"]
            )
        )

    def test_manual_review_query_returns_escalation_guidance(self):
        result = self.retriever.retrieve(
            query=(
                "device identifier mismatch manual review "
                "escalation packet analyst guidance"
            ),
            top_k=3,
        )

        self.assertEqual(result["retrieval_status"], "RESULTS_FOUND")

        self.assertTrue(
            any(
                item["document_id"] == "KB-004"
                for item in result["results"]
            )
        )

        self.assertTrue(
            any(
                item["section_title"]
                in {
                    "Required escalation packet",
                    "Writing the escalation summary",
                    "When to escalate",
                }
                for item in result["results"]
            )
        )

    def test_unknown_vocabulary_returns_no_lexical_match(self):
        result = self.retriever.retrieve(
            query="xyzzynonexistenttoken",
            top_k=3,
        )

        self.assertEqual(
            result["retrieval_status"],
            "NO_LEXICAL_MATCH",
        )
        self.assertEqual(result["result_count"], 0)
        self.assertEqual(result["results"], [])

    def test_top_k_must_be_positive_integer(self):
        invalid_values = [0, -1, True, "3"]

        for invalid_top_k in invalid_values:
            with self.subTest(top_k=invalid_top_k):
                with self.assertRaisesRegex(
                    ValueError,
                    "top_k must be a positive integer",
                ):
                    self.retriever.retrieve(
                        query="evidence guidance",
                        top_k=invalid_top_k,
                    )

    def test_query_must_be_non_empty_string(self):
        invalid_queries = [None, 123, "", "   "]

        for invalid_query in invalid_queries:
            with self.subTest(query=invalid_query):
                with self.assertRaisesRegex(
                    ValueError,
                    "Retrieval query",
                ):
                    self.retriever.retrieve(
                        query=invalid_query,
                        top_k=3,
                    )

    def test_retriever_rejects_unsafe_corpus_scope_or_authority(self):
        invalid_scope_corpus = self.corpus.copy()
        invalid_scope_corpus.loc[
            0,
            "retrieval_scope",
        ] = "DETERMINISTIC_TOOL_ONLY"

        with self.assertRaisesRegex(
            ValueError,
            "non-analyst retrieval scope",
        ):
            ControlledLexicalRetriever(invalid_scope_corpus)

        invalid_authority_corpus = self.corpus.copy()
        invalid_authority_corpus.loc[
            0,
            "authority_role",
        ] = "NON_NEGOTIABLE_SAFETY_CONTROL"

        with self.assertRaisesRegex(
            ValueError,
            "unsupported authority roles",
        ):
            ControlledLexicalRetriever(invalid_authority_corpus)

    def test_retriever_rejects_source_outside_knowledge_base(self):
        invalid_corpus = self.corpus.copy()

        invalid_corpus.loc[
            0,
            "source_relative_path",
        ] = "data/staging/unapproved_document.md"

        with self.assertRaisesRegex(
            ValueError,
            "sources outside data/knowledge_base",
        ):
            ControlledLexicalRetriever(invalid_corpus)

    def test_retrieval_is_deterministic(self):
        query = (
            "manual review analyst escalation "
            "device mismatch"
        )

        first_result = self.retriever.retrieve(
            query=query,
            top_k=3,
        )

        second_result = self.retriever.retrieve(
            query=query,
            top_k=3,
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


if __name__ == "__main__":
    unittest.main()