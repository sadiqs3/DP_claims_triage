from __future__ import annotations

from typing import Any

from src.rag.lexical_retriever import (
    ControlledLexicalRetriever,
    _validate_top_k,
)
from src.rag.semantic_retriever import ControlledSemanticRetriever


TOOL_NAME = "hybrid_sop_retrieval"
TOOL_VERSION = "rrf_v1"

DEFAULT_RRF_K = 60


def _validate_rrf_k(value: object) -> int:
    """Validate the reciprocal-rank-fusion constant."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("rrf_k must be a positive integer.")

    if value < 1:
        raise ValueError("rrf_k must be a positive integer.")

    return value


class ControlledHybridRetriever:
    """
    Hybrid retriever over approved analyst-guidance chunks.

    Combines lexical and semantic rankings using reciprocal-rank fusion.
    Output is operational guidance only and cannot change deterministic
    routing, policy eligibility, evidence requirements, or follow-up wording.
    """

    def __init__(
        self,
        lexical_retriever: ControlledLexicalRetriever,
        semantic_retriever: ControlledSemanticRetriever,
        rrf_k: int = DEFAULT_RRF_K,
    ) -> None:
        self._lexical_retriever = lexical_retriever
        self._semantic_retriever = semantic_retriever
        self._rrf_k = _validate_rrf_k(rrf_k)

        if (
            lexical_retriever.corpus_size
            != semantic_retriever.corpus_size
        ):
            raise ValueError(
                "Lexical and semantic retrievers must use the same "
                "corpus size."
            )

        if (
            lexical_retriever.corpus_fingerprint
            != semantic_retriever.corpus_fingerprint
        ):
            raise ValueError(
                "Lexical and semantic retrievers must use the same "
                "corpus fingerprint."
            )

    @property
    def corpus_size(self) -> int:
        """Return the number of chunks represented by both retrievers."""
        return self._lexical_retriever.corpus_size

    @property
    def rrf_k(self) -> int:
        """Return the reciprocal-rank-fusion constant."""
        return self._rrf_k

    @property
    def corpus_fingerprint(self) -> str:
        """Return the verified shared corpus fingerprint."""
        return self._semantic_retriever.corpus_fingerprint

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        candidate_k: int = 5,
        min_semantic_relevance_score: float = 0.20,
        semantic_client: object | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve and fuse lexical and semantic analyst-guidance results.

        candidate_k controls the number of ranked candidates drawn from each
        retrieval method before fusion. It must be at least top_k.
        """
        validated_top_k = _validate_top_k(top_k)

        if isinstance(candidate_k, bool) or not isinstance(
            candidate_k,
            int,
        ):
            raise ValueError("candidate_k must be a positive integer.")

        if candidate_k < 1:
            raise ValueError("candidate_k must be a positive integer.")

        if candidate_k < validated_top_k:
            raise ValueError(
                "candidate_k must be greater than or equal to top_k."
            )

        lexical_result = self._lexical_retriever.retrieve(
            query=query,
            top_k=candidate_k,
        )

        semantic_result = self._semantic_retriever.retrieve(
            query=query,
            top_k=candidate_k,
            min_relevance_score=min_semantic_relevance_score,
            client=semantic_client,
        )

        candidates: dict[str, dict[str, Any]] = {}

        for source_name, retrieval_result in [
            ("lexical", lexical_result),
            ("semantic", semantic_result),
        ]:
            for item in retrieval_result["results"]:
                chunk_id = item["chunk_id"]

                if chunk_id not in candidates:
                    candidates[chunk_id] = {
                        "item": item,
                        "rrf_score": 0.0,
                        "retrieval_methods": [],
                        "method_ranks": {},
                        "method_scores": {},
                    }

                candidate = candidates[chunk_id]

                candidate["rrf_score"] += 1 / (
                    self._rrf_k + item["rank"]
                )

                candidate["retrieval_methods"].append(source_name)

                candidate["method_ranks"][source_name] = item["rank"]

                candidate["method_scores"][source_name] = (
                    item["relevance_score"]
                )

        ranked_candidates = sorted(
            candidates.values(),
            key=lambda candidate: (
                -candidate["rrf_score"],
                candidate["item"]["chunk_id"],
            ),
        )[:validated_top_k]

        results: list[dict[str, Any]] = []

        for rank, candidate in enumerate(
            ranked_candidates,
            start=1,
        ):
            item = dict(candidate["item"])

            item.update(
                {
                    "rank": rank,
                    "fusion_score": round(
                        float(candidate["rrf_score"]),
                        8,
                    ),
                    "retrieval_methods": sorted(
                        candidate["retrieval_methods"]
                    ),
                    "method_ranks": candidate["method_ranks"],
                    "method_scores": candidate["method_scores"],
                }
            )

            results.append(item)

        retrieval_status = (
            "RESULTS_FOUND"
            if results
            else "NO_HYBRID_MATCH"
        )

        return {
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "retrieval_status": retrieval_status,
            "query": query,
            "requested_top_k": validated_top_k,
            "candidate_k": candidate_k,
            "rrf_k": self._rrf_k,
            "corpus_fingerprint": self.corpus_fingerprint,
            "result_count": len(results),
            "results": results,
            "lexical_retrieval_status": lexical_result[
                "retrieval_status"
            ],
            "semantic_retrieval_status": semantic_result[
                "retrieval_status"
            ],
            "retrieval_notice": (
                "Retrieved content is analyst-facing operational guidance "
                "only. It cannot override deterministic triage, policy "
                "eligibility, evidence requirements, or controlled "
                "customer follow-up."
            ),
        }