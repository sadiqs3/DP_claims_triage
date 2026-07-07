import tempfile
import unittest
from pathlib import Path

import numpy as np
from types import SimpleNamespace

from src.data_loader import load_runtime_data
from src.rag.corpus_builder import build_rag_corpus

from src.rag.faiss_index import (
    INDEX_FILENAME,
    MANIFEST_FILENAME,
    build_persisted_faiss_index_from_openai,
    load_validated_faiss_semantic_index,
    persist_faiss_semantic_index,
)

class TestPersistedFAISSSemanticIndex(unittest.TestCase):
    """Tests for persisted approved-KB embeddings and integrity checks."""

    @classmethod
    def setUpClass(cls):
        runtime_data = load_runtime_data()
        cls.corpus = build_rag_corpus(
            runtime_data["rag_document_registry"].copy()
        )

    @staticmethod
    def _validation_embeddings(
        row_count: int,
        dimension: int = 8,
    ) -> np.ndarray:
        """Create stable numeric vectors for persistence tests only."""
        rng = np.random.default_rng(seed=20260707)

        return rng.normal(
            size=(row_count, dimension),
        ).astype(np.float32)

    def test_persists_and_loads_matching_approved_corpus(self):
        embeddings = self._validation_embeddings(len(self.corpus))

        with tempfile.TemporaryDirectory() as temporary_dir:
            manifest = persist_faiss_semantic_index(
                corpus=self.corpus,
                document_embeddings=embeddings,
                output_dir=temporary_dir,
            )

            loaded = load_validated_faiss_semantic_index(
                corpus=self.corpus,
                output_dir=temporary_dir,
            )

            artifact_dir = Path(temporary_dir)

            self.assertTrue(
                (artifact_dir / INDEX_FILENAME).is_file()
            )
            self.assertTrue(
                (artifact_dir / MANIFEST_FILENAME).is_file()
            )
            self.assertEqual(loaded.manifest, manifest)
            self.assertEqual(loaded.index.ntotal, len(self.corpus))
            self.assertEqual(
                loaded.index.d,
                manifest.embedding_dimension,
            )

            expected_chunk_ids = (
                self.corpus.sort_values(
                    by=[
                        "registry_priority",
                        "document_id",
                        "section_index",
                    ],
                    kind="stable",
                )
                .reset_index(drop=True)["chunk_id"]
                .tolist()
            )

            self.assertEqual(
                loaded.corpus["chunk_id"].tolist(),
                expected_chunk_ids,
            )

    def test_blocks_loading_when_corpus_fingerprint_changes(self):
        embeddings = self._validation_embeddings(len(self.corpus))

        # A missing chunk represents a changed approved corpus.
        changed_corpus = self.corpus.iloc[:-1].copy()

        with tempfile.TemporaryDirectory() as temporary_dir:
            persist_faiss_semantic_index(
                corpus=self.corpus,
                document_embeddings=embeddings,
                output_dir=temporary_dir,
            )

            with self.assertRaisesRegex(
                ValueError,
                "corpus fingerprint",
            ):
                load_validated_faiss_semantic_index(
                    corpus=changed_corpus,
                    output_dir=temporary_dir,
                )

    def test_blocks_loading_when_embedding_model_changes(self):
        embeddings = self._validation_embeddings(len(self.corpus))

        with tempfile.TemporaryDirectory() as temporary_dir:
            persist_faiss_semantic_index(
                corpus=self.corpus,
                document_embeddings=embeddings,
                output_dir=temporary_dir,
            )

            with self.assertRaisesRegex(
                ValueError,
                "embedding model",
            ):
                load_validated_faiss_semantic_index(
                    corpus=self.corpus,
                    output_dir=temporary_dir,
                    embedding_model="text-embedding-3-large",
                )

    def test_rejects_embedding_row_count_mismatch(self):
        too_few_embeddings = self._validation_embeddings(
            row_count=len(self.corpus) - 1,
        )

        with tempfile.TemporaryDirectory() as temporary_dir:
            with self.assertRaisesRegex(
                ValueError,
                "row count must match corpus size",
            ):
                persist_faiss_semantic_index(
                    corpus=self.corpus,
                    document_embeddings=too_few_embeddings,
                    output_dir=temporary_dir,
                )

    def test_rejects_zero_norm_embedding_vectors(self):
        zero_embeddings = np.zeros(
            (len(self.corpus), 8),
            dtype=np.float32,
        )

        with tempfile.TemporaryDirectory() as temporary_dir:
            with self.assertRaisesRegex(
                ValueError,
                "non-zero L2 norms",
            ):
                persist_faiss_semantic_index(
                    corpus=self.corpus,
                    document_embeddings=zero_embeddings,
                    output_dir=temporary_dir,
                )

    def test_rejects_non_finite_embedding_vectors(self):
        invalid_embeddings = self._validation_embeddings(
            row_count=len(self.corpus),
        )
        invalid_embeddings[0, 0] = np.nan

        with tempfile.TemporaryDirectory() as temporary_dir:
            with self.assertRaisesRegex(
                ValueError,
                "non-finite",
            ):
                persist_faiss_semantic_index(
                    corpus=self.corpus,
                    document_embeddings=invalid_embeddings,
                    output_dir=temporary_dir,
                )

    def test_builds_persisted_index_from_ordered_approved_chunks(self):
        """
        The wrapper must embed only approved KB chunks in deterministic order.

        Fake embeddings keep this test offline and independent of OpenAI.
        """

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
                                float(index + 4),
                            ],
                        )
                        for index, _ in enumerate(texts)
                    ]
                )

        fake_endpoint = FakeEmbeddingsEndpoint()
        fake_client = SimpleNamespace(embeddings=fake_endpoint)

        with tempfile.TemporaryDirectory() as temporary_dir:
            manifest = build_persisted_faiss_index_from_openai(
                corpus=self.corpus,
                output_dir=temporary_dir,
                client=fake_client,
            )

            loaded = load_validated_faiss_semantic_index(
                corpus=self.corpus,
                output_dir=temporary_dir,
            )

        self.assertEqual(len(fake_endpoint.calls), 1)
        self.assertEqual(
            fake_endpoint.calls[0]["input"],
            loaded.corpus["chunk_text"].tolist(),
        )
        self.assertEqual(loaded.index.ntotal, len(self.corpus))
        self.assertEqual(loaded.index.d, 4)
        self.assertEqual(
            manifest.embedding_model,
            "text-embedding-3-small",
        )

if __name__ == "__main__":
    unittest.main()