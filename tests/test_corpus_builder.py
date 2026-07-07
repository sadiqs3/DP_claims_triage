import copy
import unittest
from pathlib import Path

from src.data_loader import load_runtime_data
from src.rag.corpus_builder import build_rag_corpus


class TestControlledRagCorpusBuilder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_runtime_data()
        cls.registry = cls.data["rag_document_registry"].copy()

    def test_builds_only_allowlisted_documents(self):
        corpus = build_rag_corpus(self.registry)

        self.assertEqual(
            set(corpus["document_id"]),
            {"KB-001", "KB-002", "KB-004", "KB-005"},
        )
        self.assertEqual(len(corpus), 21)

        self.assertTrue(corpus["chunk_id"].is_unique)
        self.assertTrue(corpus["chunk_text"].str.len().gt(0).all())

        self.assertFalse(
            corpus["section_title"]
            .str.casefold()
            .eq("references")
            .any()
        )

        self.assertFalse(
            corpus["section_title"]
            .str.casefold()
            .eq("examples of targeted requests")
            .any()
        )


    def test_excluded_document_is_never_read(self):
        registry = self.registry.copy()

        registry.loc[
            registry["document_id"].eq("KB-003"),
            "relative_path",
        ] = "data/staging/this_file_must_not_be_read.md"

        corpus = build_rag_corpus(registry)

        self.assertNotIn("KB-003", set(corpus["document_id"]))
        self.assertEqual(len(corpus), 21)

    def test_included_document_path_must_stay_in_knowledge_base(self):
        registry = self.registry.copy()

        registry.loc[
            registry["document_id"].eq("KB-001"),
            "relative_path",
        ] = "data/staging/KB-001_claims_triage_sop_v1.md"

        with self.assertRaisesRegex(
            ValueError,
            "Included document path must remain inside data/knowledge_base",
        ):
            build_rag_corpus(registry)

    def test_missing_included_document_raises_error(self):
        registry = self.registry.copy()

        registry.loc[
            registry["document_id"].eq("KB-001"),
            "relative_path",
        ] = "data/knowledge_base/not_a_real_document.md"

        with self.assertRaisesRegex(
            FileNotFoundError,
            "Registered RAG document was not found",
        ):
            build_rag_corpus(registry)

    def test_missing_registry_column_raises_error(self):
        invalid_registry = self.registry.drop(columns=["authority_role"])

        with self.assertRaisesRegex(
            ValueError,
            "rag document registry is missing required columns",
        ):
            build_rag_corpus(invalid_registry)

    def test_repeated_builds_preserve_chunk_identity_and_hashes(self):
        first_corpus = build_rag_corpus(self.registry)
        second_corpus = build_rag_corpus(self.registry)

        first_view = first_corpus[
            ["chunk_id", "source_document_sha256", "chunk_sha256"]
        ].reset_index(drop=True)

        second_view = second_corpus[
            ["chunk_id", "source_document_sha256", "chunk_sha256"]
        ].reset_index(drop=True)

        self.assertTrue(first_view.equals(second_view))


if __name__ == "__main__":
    unittest.main()