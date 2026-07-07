from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from src.rag.corpus_builder import compute_corpus_fingerprint


TOOL_NAME = "lexical_sop_retrieval"
TOOL_VERSION = "tfidf_v1"

ALLOWED_RETRIEVAL_SCOPE = "ANALYST_GUIDANCE"
ALLOWED_AUTHORITY_ROLE = "OPERATIONAL_GUIDANCE_ONLY"

REQUIRED_CORPUS_COLUMNS = {
    "chunk_id",
    "document_id",
    "document_title",
    "document_version",
    "effective_date",
    "document_type",
    "retrieval_scope",
    "authority_role",
    "registry_priority",
    "source_relative_path",
    "source_document_sha256",
    "section_index",
    "section_title",
    "chunk_text",
    "chunk_char_count",
    "chunk_sha256",
}


def _normalise_text(value: object) -> str:
    """Return stripped text, treating missing values as empty strings."""
    if value is None or pd.isna(value):
        return ""

    return str(value).strip()


def _validate_corpus(corpus: pd.DataFrame) -> None:
    """Validate that the corpus is suitable for controlled analyst retrieval."""
    if not isinstance(corpus, pd.DataFrame):
        raise ValueError("RAG corpus must be a pandas DataFrame.")

    missing_columns = REQUIRED_CORPUS_COLUMNS.difference(corpus.columns)

    if missing_columns:
        raise ValueError(
            "RAG corpus is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if corpus.empty:
        raise ValueError("RAG corpus must not be empty.")

    if corpus["chunk_id"].duplicated().any():
        raise ValueError("RAG corpus contains duplicate chunk_id values.")

    if corpus["chunk_text"].isna().any():
        raise ValueError("RAG corpus contains missing chunk_text values.")

    if corpus["chunk_text"].astype(str).str.strip().eq("").any():
        raise ValueError("RAG corpus contains empty chunk_text values.")

    invalid_scope = corpus.loc[
        corpus["retrieval_scope"]
        .astype(str)
        .str.strip()
        .ne(ALLOWED_RETRIEVAL_SCOPE),
        "retrieval_scope",
    ].unique()

    if len(invalid_scope) > 0:
        raise ValueError(
            "RAG corpus contains non-analyst retrieval scope values: "
            + ", ".join(map(str, invalid_scope))
        )

    invalid_authority_role = corpus.loc[
        corpus["authority_role"]
        .astype(str)
        .str.strip()
        .ne(ALLOWED_AUTHORITY_ROLE),
        "authority_role",
    ].unique()

    if len(invalid_authority_role) > 0:
        raise ValueError(
            "RAG corpus contains unsupported authority roles: "
            + ", ".join(map(str, invalid_authority_role))
        )

    invalid_paths = corpus.loc[
        ~corpus["source_relative_path"]
        .astype(str)
        .str.startswith("data/knowledge_base/"),
        "source_relative_path",
    ].unique()

    if len(invalid_paths) > 0:
        raise ValueError(
            "RAG corpus contains sources outside data/knowledge_base: "
            + ", ".join(map(str, invalid_paths))
        )


def _validate_query(query: object) -> str:
    """Validate and normalise a retrieval query."""
    if not isinstance(query, str):
        raise ValueError("Retrieval query must be a string.")

    normalised_query = query.strip()

    if not normalised_query:
        raise ValueError("Retrieval query must not be empty.")

    return normalised_query


def _validate_top_k(top_k: object) -> int:
    """Validate the requested number of returned chunks."""
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise ValueError("top_k must be a positive integer.")

    if top_k < 1:
        raise ValueError("top_k must be a positive integer.")

    return top_k


class ControlledLexicalRetriever:
    """
    TF-IDF retriever for approved analyst-guidance chunks only.

    Retrieval output is non-authoritative SOP guidance. It cannot alter
    deterministic triage routing, evidence requirements, policy eligibility,
    or controlled customer follow-up wording.
    """

    def __init__(self, corpus: pd.DataFrame) -> None:
        _validate_corpus(corpus)

        self._corpus = (
            corpus.copy()
            .sort_values(
                by=["registry_priority", "document_id", "section_index"],
                kind="stable",
            )
            .reset_index(drop=True)
        )
        self._corpus_fingerprint = compute_corpus_fingerprint(
            self._corpus
        )

        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
            norm="l2",
        )

        self._document_matrix = self._vectorizer.fit_transform(
            self._corpus["chunk_text"].tolist()
        )

    @property
    def corpus_size(self) -> int:
        """Return the number of indexed chunks."""
        return len(self._corpus)

    @property
    def corpus_fingerprint(self) -> str:
        """Return the stable fingerprint of the indexed corpus."""
        return self._corpus_fingerprint


    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Retrieve ranked analyst-guidance chunks for a lexical query.

        Chunks with a zero TF-IDF score are excluded rather than returned as
        arbitrary matches.
        """
        normalised_query = _validate_query(query)
        validated_top_k = _validate_top_k(top_k)

        query_vector = self._vectorizer.transform([normalised_query])

        if query_vector.nnz == 0:
            return {
                "tool_name": TOOL_NAME,
                "tool_version": TOOL_VERSION,
                "retrieval_status": "NO_LEXICAL_MATCH",
                "query": normalised_query,
                "requested_top_k": validated_top_k,
                "result_count": 0,
                "results": [],
                "retrieval_notice": (
                    "Retrieved content is analyst-facing operational guidance "
                    "only. It cannot override deterministic triage, policy "
                    "eligibility, evidence requirements, or controlled "
                    "customer follow-up."
                ),
            }

        scores = (
            self._document_matrix @ query_vector.T
        ).toarray().ravel()

        ranked_indices = np.argsort(
            -scores,
            kind="stable",
        )

        matching_indices = [
            index
            for index in ranked_indices
            if scores[index] > 0
        ][:validated_top_k]

        results: list[dict[str, Any]] = []

        for rank, index in enumerate(matching_indices, start=1):
            row = self._corpus.iloc[index]

            results.append(
                {
                    "rank": rank,
                    "relevance_score": round(float(scores[index]), 6),
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
            else "NO_LEXICAL_MATCH"
        )

        return {
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "retrieval_status": retrieval_status,
            "query": normalised_query,
            "requested_top_k": validated_top_k,
            "result_count": len(results),
            "results": results,
            "retrieval_notice": (
                "Retrieved content is analyst-facing operational guidance "
                "only. It cannot override deterministic triage, policy "
                "eligibility, evidence requirements, or controlled customer "
                "follow-up."
            ),
        }