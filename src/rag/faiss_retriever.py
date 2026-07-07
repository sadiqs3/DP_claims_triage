from __future__ import annotations

# Retrieves approved KB guidance from the persisted FAISS index only.
# It accepts a controlled deterministic query and cannot change triage authority.
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.rag.controlled_query_builder import ControlledRAGQuery
from src.rag.faiss_index import (
    LoadedFAISSIndex,
    load_validated_faiss_semantic_index,
)
from src.rag.lexical_retriever import _validate_top_k
from src.rag.semantic_retriever import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_MIN_RELEVANCE_SCORE,
    _embed_texts,
    _normalise_rows,
    _validate_min_relevance_score,
)

TOOL_NAME = "persisted_semantic_sop_retrieval"
TOOL_VERSION = "faiss_embedding_v1"

_REQUIRED_QUERY_SOURCE = "authoritative_deterministic_triage_facts"
_REQUIRED_AUDIENCE = "analyst"
_REQUIRED_AUTHORITY = "non_authoritative_guidance"


def _validate_controlled_query(
    query: object,
) -> ControlledRAGQuery:
    """Validate the query contract before any embedding or FAISS search."""
    if not isinstance(query, ControlledRAGQuery):
        raise TypeError(
            "query must be a ControlledRAGQuery created from "
            "authoritative deterministic triage facts."
        )

    if query.source != _REQUIRED_QUERY_SOURCE:
        raise ValueError(
            "Controlled RAG query source is not authorised."
        )

    if query.audience != _REQUIRED_AUDIENCE:
        raise ValueError(
            "Controlled RAG query audience must be analyst."
        )

    if query.authority != _REQUIRED_AUTHORITY:
        raise ValueError(
            "Controlled RAG query must remain non-authoritative."
        )

    if not isinstance(query.query_text, str) or not query.query_text.strip():
        raise ValueError(
            "Controlled RAG query text must be a non-empty string."
        )

    expected_fingerprint = sha256(
        query.query_text.encode("utf-8")
    ).hexdigest()

    if query.query_fingerprint != expected_fingerprint:
        raise ValueError(
            "Controlled RAG query fingerprint does not match query text."
        )

    return query


class ControlledPersistedFAISSRetriever:
    """
    Persisted semantic retriever for approved analyst-guidance chunks only.

    It accepts only ControlledRAGQuery objects and cannot override
    deterministic triage, eligibility, evidence requirements, or
    controlled customer follow-up wording.
    """

    def __init__(self, loaded_index: LoadedFAISSIndex) -> None:
        if not isinstance(loaded_index, LoadedFAISSIndex):
            raise TypeError(
                "loaded_index must be a validated LoadedFAISSIndex."
            )

        self._loaded_index = loaded_index

    @classmethod
    def from_artifacts(
        cls,
        corpus: pd.DataFrame,
        artifact_dir: str | Path,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> "ControlledPersistedFAISSRetriever":
        """Load the persisted index only after corpus/config validation."""
        loaded_index = load_validated_faiss_semantic_index(
            corpus=corpus,
            output_dir=artifact_dir,
            embedding_model=embedding_model,
        )

        return cls(loaded_index)

    @property
    def corpus_size(self) -> int:
        """Return the approved KB chunk count represented by the index."""
        return int(self._loaded_index.index.ntotal)

    @property
    def embedding_dimension(self) -> int:
        """Return the persisted embedding-vector dimension."""
        return int(self._loaded_index.index.d)

    @property
    def embedding_model(self) -> str:
        """Return the embedding model recorded in the index manifest."""
        return self._loaded_index.manifest.embedding_model

    @property
    def corpus_fingerprint(self) -> str:
        """Return the corpus fingerprint validated during index loading."""
        return self._loaded_index.manifest.corpus_fingerprint

    def retrieve(
        self,
        query: ControlledRAGQuery,
        top_k: int = 3,
        min_relevance_score: float = DEFAULT_MIN_RELEVANCE_SCORE,
        client: object | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve analyst guidance for an authorised controlled query.

        The relevance threshold controls only guidance availability. It never
        changes claim routing, eligibility, evidence requirements, or wording.
        """
        validated_query = _validate_controlled_query(query)
        validated_top_k = _validate_top_k(top_k)
        validated_threshold = _validate_min_relevance_score(
            min_relevance_score
        )

        query_embedding_matrix = _embed_texts(
            texts=[validated_query.query_text],
            embedding_model=self.embedding_model,
            client=client,
        )

        if query_embedding_matrix.shape[1] != self.embedding_dimension:
            raise ValueError(
                "Query embedding dimension does not match persisted index "
                "dimension."
            )

        query_embedding = np.ascontiguousarray(
            _normalise_rows(query_embedding_matrix),
            dtype=np.float32,
        )

        candidate_count = min(validated_top_k, self.corpus_size)

        scores, indices = self._loaded_index.index.search(
            query_embedding,
            candidate_count,
        )

        results: list[dict[str, Any]] = []

        for score, index in zip(scores[0], indices[0]):
            if int(index) < 0 or float(score) < validated_threshold:
                continue

            row = self._loaded_index.corpus.iloc[int(index)]

            results.append(
                {
                    "rank": len(results) + 1,
                    "relevance_score": round(float(score), 6),
                    "chunk_id": row["chunk_id"],
                    "document_id": row["document_id"],
                    "document_title": row["document_title"],
                    "document_version": row["document_version"],
                    "effective_date": row["effective_date"],
                    "document_type": row["document_type"],
                    "section_title": row["section_title"],
                    "chunk_text": row["chunk_text"],
                    "source_reference": {
                        "source_relative_path": row[
                            "source_relative_path"
                        ],
                        "source_document_sha256": row[
                            "source_document_sha256"
                        ],
                        "chunk_sha256": row["chunk_sha256"],
                    },
                }
            )

        retrieval_status = (
            "RESULTS_FOUND"
            if results
            else "NO_SEMANTIC_MATCH_ABOVE_THRESHOLD"
        )

        return {
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "retrieval_status": retrieval_status,
            "query": validated_query.query_text,
            "controlled_query_fingerprint": (
                validated_query.query_fingerprint
            ),
            "query_source": validated_query.source,
            "audience": validated_query.audience,
            "authority": validated_query.authority,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "corpus_fingerprint": self.corpus_fingerprint,
            "index_artifact_version": (
                self._loaded_index.manifest.artifact_version
            ),
            "index_type": self._loaded_index.manifest.index_type,
            "requested_top_k": validated_top_k,
            "min_relevance_score": validated_threshold,
            "result_count": len(results),
            "results": results,
            "retrieval_notice": (
                "Retrieved content is analyst-facing operational guidance "
                "only. It cannot override deterministic triage, policy "
                "eligibility, evidence requirements, or controlled customer "
                "follow-up."
            ),
        }