from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from openai import OpenAI

from src.rag.lexical_retriever import (
    _validate_corpus,
    _validate_query,
    _validate_top_k,
)
from src.rag.corpus_builder import compute_corpus_fingerprint

TOOL_NAME = "semantic_sop_retrieval"
TOOL_VERSION = "embedding_v1"

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_MIN_RELEVANCE_SCORE = 0.20


def _prepare_corpus(corpus: pd.DataFrame) -> pd.DataFrame:
    """Validate and consistently order the approved retrieval corpus."""
    _validate_corpus(corpus)

    return (
        corpus.copy()
        .sort_values(
            by=["registry_priority", "document_id", "section_index"],
            kind="stable",
        )
        .reset_index(drop=True)
    )


def _validate_embedding_model(model: object) -> str:
    """Validate the embedding-model identifier."""
    if not isinstance(model, str) or not model.strip():
        raise ValueError("embedding_model must be a non-empty string.")

    return model.strip()


def _validate_min_relevance_score(value: object) -> float:
    """Validate the minimum cosine-similarity threshold."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            "min_relevance_score must be a number between 0 and 1."
        )

    score = float(value)

    if not 0 <= score <= 1:
        raise ValueError(
            "min_relevance_score must be a number between 0 and 1."
        )

    return score


def _resolve_client(client: object | None) -> Any:
    """Use an injected client for tests or construct the OpenAI client."""
    if client is not None:
        return client

    return OpenAI()


def _normalise_rows(matrix: np.ndarray) -> np.ndarray:
    """Return L2-normalised vectors suitable for dot-product similarity."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)

    if np.any(norms == 0):
        raise ValueError(
            "Embedding vectors must have a non-zero L2 norm."
        )

    return matrix / norms


def _extract_embedding_matrix(
    response: object,
    expected_count: int,
) -> np.ndarray:
    """Extract indexed embedding vectors from an OpenAI-style response."""
    response_data = getattr(response, "data", None)

    if not isinstance(response_data, Sequence):
        raise ValueError(
            "Embedding response must contain a sequence of data items."
        )

    if len(response_data) != expected_count:
        raise ValueError(
            "Embedding response count does not match requested input count."
        )

    embeddings_by_index: list[object | None] = [None] * expected_count

    for item in response_data:
        item_index = getattr(item, "index", None)
        embedding = getattr(item, "embedding", None)

        if (
            isinstance(item_index, bool)
            or not isinstance(item_index, int)
            or item_index < 0
            or item_index >= expected_count
        ):
            raise ValueError(
                "Embedding response contains an invalid item index."
            )

        if embeddings_by_index[item_index] is not None:
            raise ValueError(
                "Embedding response contains duplicate item indexes."
            )

        embeddings_by_index[item_index] = embedding

    if any(vector is None for vector in embeddings_by_index):
        raise ValueError(
            "Embedding response is missing one or more item indexes."
        )

    try:
        matrix = np.asarray(
            embeddings_by_index,
            dtype=np.float32,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "Embedding response contains non-numeric vector values."
        ) from error

    if matrix.ndim != 2 or matrix.shape[1] == 0:
        raise ValueError(
            "Embedding response must contain non-empty vectors."
        )

    if not np.isfinite(matrix).all():
        raise ValueError(
            "Embedding response contains non-finite vector values."
        )

    return matrix


def _embed_texts(
    texts: Sequence[str],
    embedding_model: str,
    client: object | None = None,
) -> np.ndarray:
    """Embed a non-empty batch of approved text strings."""
    if not texts:
        raise ValueError("At least one text is required for embedding.")

    normalised_texts = []

    for text in texts:
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Embedding inputs must be non-empty strings."
            )

        normalised_texts.append(text.strip())

    resolved_client = _resolve_client(client)

    response = resolved_client.embeddings.create(
        input=normalised_texts,
        model=embedding_model,
    )

    return _extract_embedding_matrix(
        response=response,
        expected_count=len(normalised_texts),
    )


class ControlledSemanticRetriever:
    """
    In-memory semantic retriever for approved analyst-guidance chunks only.

    Retrieval remains non-authoritative. It cannot alter deterministic triage,
    policy eligibility, evidence requirements, or controlled customer follow-up.
    """

    def __init__(
        self,
        corpus: pd.DataFrame,
        document_embeddings: np.ndarray,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        self._corpus = _prepare_corpus(corpus)
        self._embedding_model = _validate_embedding_model(
            embedding_model
        )

        embedding_matrix = np.asarray(
            document_embeddings,
            dtype=np.float32,
        )

        if embedding_matrix.ndim != 2:
            raise ValueError(
                "document_embeddings must be a two-dimensional matrix."
            )

        if embedding_matrix.shape[0] != len(self._corpus):
            raise ValueError(
                "document_embeddings row count must match corpus size."
            )

        if embedding_matrix.shape[1] == 0:
            raise ValueError(
                "document_embeddings must contain at least one dimension."
            )

        if not np.isfinite(embedding_matrix).all():
            raise ValueError(
                "document_embeddings contains non-finite values."
            )

        self._embedding_matrix = _normalise_rows(embedding_matrix)
        self._corpus_fingerprint = compute_corpus_fingerprint(
            self._corpus
        )
    @classmethod
    def from_openai(
        cls,
        corpus: pd.DataFrame,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        client: object | None = None,
    ) -> "ControlledSemanticRetriever":
        """
        Create an in-memory index by embedding approved corpus chunks only.
        """
        prepared_corpus = _prepare_corpus(corpus)
        validated_model = _validate_embedding_model(
            embedding_model
        )

        document_embeddings = _embed_texts(
            texts=prepared_corpus["chunk_text"].tolist(),
            embedding_model=validated_model,
            client=client,
        )

        return cls(
            corpus=prepared_corpus,
            document_embeddings=document_embeddings,
            embedding_model=validated_model,
        )

    @property
    def corpus_size(self) -> int:
        """Return the number of indexed chunks."""
        return len(self._corpus)

    @property
    def embedding_dimension(self) -> int:
        """Return the embedding-vector size used by the index."""
        return int(self._embedding_matrix.shape[1])

    @property
    def embedding_model(self) -> str:
        """Return the embedding model used to build the index."""
        return self._embedding_model

    @property
    def corpus_fingerprint(self) -> str:
        """Return the stable fingerprint of the indexed corpus."""
        return self._corpus_fingerprint

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_relevance_score: float = DEFAULT_MIN_RELEVANCE_SCORE,
        client: object | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve semantic analyst guidance for a query.

        A result is returned only when its cosine-similarity score meets the
        supplied threshold. The threshold governs guidance availability only;
        it never changes claim routing.
        """
        normalised_query = _validate_query(query)
        validated_top_k = _validate_top_k(top_k)
        validated_threshold = _validate_min_relevance_score(
            min_relevance_score
        )

        query_embedding_matrix = _embed_texts(
            texts=[normalised_query],
            embedding_model=self._embedding_model,
            client=client,
        )

        if query_embedding_matrix.shape[1] != self.embedding_dimension:
            raise ValueError(
                "Query embedding dimension does not match index dimension."
            )

        query_embedding = _normalise_rows(
            query_embedding_matrix
        )[0]

        scores = self._embedding_matrix @ query_embedding

        ranked_indices = np.argsort(
            -scores,
            kind="stable",
        )

        matching_indices = [
            index
            for index in ranked_indices
            if scores[index] >= validated_threshold
        ][:validated_top_k]

        results: list[dict[str, Any]] = []

        for rank, index in enumerate(matching_indices, start=1):
            row = self._corpus.iloc[index]

            results.append(
                {
                    "rank": rank,
                    "relevance_score": round(
                        float(scores[index]),
                        6,
                    ),
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
            "query": normalised_query,
            "embedding_model": self.embedding_model,
            "embedding_dimension": self.embedding_dimension,
            "corpus_fingerprint": self.corpus_fingerprint,
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