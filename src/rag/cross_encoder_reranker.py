from __future__ import annotations

# Cross-encoder reranking for controlled RAG candidates.
# This module may only reorder approved KB chunks retrieved by the controlled
# retrieval tool. It must not create new guidance or alter triage outcomes.

from copy import deepcopy
from typing import Any, Mapping, Protocol, Sequence


RERANKER_NAME = "cross_encoder_reranker"
RERANKER_VERSION = "v1"

EXPECTED_AUTHORITY = "non_authoritative_guidance"
DEFAULT_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderScorer(Protocol):
    """Minimal interface expected from a cross-encoder scorer."""

    def predict(
        self,
        pairs: Sequence[tuple[str, str]],
    ) -> Sequence[float]:
        """Return one score per query-document pair."""


class SentenceTransformersCrossEncoderScorer:
    """
    Lazy wrapper for sentence-transformers CrossEncoder.

    This class is intentionally not required for unit tests. Tests should use
    a fake scorer so they do not download models or call external services.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_CROSS_ENCODER_MODEL,
        model: object | None = None,
    ) -> None:
        self.model_name = model_name

        if model is not None:
            self.model = model
            return

        try:
            from sentence_transformers import CrossEncoder
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for the real "
                "cross-encoder scorer. Install it before running live "
                "reranking validation."
            ) from exc

        self.model = CrossEncoder(model_name)

    def predict(
        self,
        pairs: Sequence[tuple[str, str]],
    ) -> Sequence[float]:
        """Score query-document pairs with the wrapped CrossEncoder."""
        return self.model.predict(list(pairs))


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _as_list(value: object, field_name: str) -> list[Any]:
    """Validate that a field is a list."""
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")

    return value


def _clean_text(value: object) -> str:
    """Return compact text."""
    if value is None:
        return ""

    return " ".join(str(value).split())


def _clean_rank(value: object, fallback: int) -> int:
    """Return a positive integer rank."""
    if isinstance(value, bool):
        return fallback

    try:
        rank = int(value)
    except (TypeError, ValueError):
        return fallback

    return rank if rank > 0 else fallback


def _normalise_scores(raw_scores: object) -> list[float]:
    """Convert scorer output to a list of floats."""
    if hasattr(raw_scores, "tolist"):
        raw_scores = raw_scores.tolist()

    if not isinstance(raw_scores, Sequence) or isinstance(
        raw_scores,
        str,
    ):
        raise ValueError("Cross-encoder scorer must return a score list.")

    scores: list[float] = []

    for score in raw_scores:
        if isinstance(score, bool):
            raise ValueError("Cross-encoder scores must be numeric.")

        try:
            scores.append(float(score))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Cross-encoder scores must be numeric."
            ) from exc

    return scores


def _validate_top_n(top_n: int | None) -> int | None:
    """Validate optional reranked output limit."""
    if top_n is None:
        return None

    if isinstance(top_n, bool) or int(top_n) < 1:
        raise ValueError("top_n must be a positive integer.")

    return int(top_n)


def rerank_controlled_rag_result(
    rag_tool_result: Mapping[str, Any],
    scorer: CrossEncoderScorer,
    top_n: int | None = None,
    model_name: str | None = None,
) -> dict[str, Any]:
    """
    Rerank controlled RAG retrieval candidates with a cross-encoder scorer.

    The scorer receives only:
    - the controlled query text built from allow-listed deterministic facts
    - approved KB chunk text returned by the retrieval tool

    The function returns a copy of rag_tool_result with reordered
    retrieved_guidance. It does not mutate the input and does not generate
    any new policy guidance.
    """
    if not isinstance(rag_tool_result, Mapping):
        raise ValueError("rag_tool_result must be a mapping.")

    if not hasattr(scorer, "predict"):
        raise ValueError("scorer must expose a predict method.")

    limit = _validate_top_n(top_n)

    result = deepcopy(dict(rag_tool_result))

    if result.get("authority") != EXPECTED_AUTHORITY:
        raise ValueError(
            "rag_tool_result must contain non-authoritative guidance."
        )

    controlled_query = _as_dict(result.get("controlled_query"))
    query_text = _clean_text(controlled_query.get("query_text"))

    if not query_text:
        raise ValueError(
            "controlled_query.query_text is required for reranking."
        )

    retrieved_guidance = _as_list(
        result.get("retrieved_guidance"),
        "retrieved_guidance",
    )

    candidate_count = len(retrieved_guidance)

    resolved_model_name = (
        model_name
        or getattr(scorer, "model_name", None)
        or scorer.__class__.__name__
    )

    if candidate_count == 0:
        result["retrieved_guidance"] = []
        result["retrieved_guidance_count"] = 0
        result["reranking"] = {
            "reranker_name": RERANKER_NAME,
            "reranker_version": RERANKER_VERSION,
            "reranker_model_name": resolved_model_name,
            "reranking_status": "NO_CANDIDATES",
            "candidate_count": 0,
            "reranked_count": 0,
            "controlled_query_fingerprint": controlled_query.get(
                "query_fingerprint"
            ),
        }

        return result

    pairs: list[tuple[str, str]] = []

    for index, item in enumerate(retrieved_guidance, start=1):
        item_dict = _as_dict(item)
        chunk_text = _clean_text(item_dict.get("chunk_text"))

        if not chunk_text:
            raise ValueError(
                "Each retrieved guidance item must include chunk_text."
            )

        pairs.append((query_text, chunk_text))

    scores = _normalise_scores(scorer.predict(pairs))

    if len(scores) != candidate_count:
        raise ValueError(
            "Cross-encoder scorer returned a different number of scores "
            "than retrieved guidance candidates."
        )

    scored_candidates: list[dict[str, Any]] = []

    for index, item in enumerate(retrieved_guidance, start=1):
        candidate = deepcopy(_as_dict(item))
        original_rank = _clean_rank(candidate.get("rank"), index)

        candidate["original_rank"] = original_rank
        candidate["rerank_score"] = round(scores[index - 1], 6)
        candidate["_tie_break_original_rank"] = original_rank

        scored_candidates.append(candidate)

    scored_candidates.sort(
        key=lambda item: (
            -float(item["rerank_score"]),
            int(item["_tie_break_original_rank"]),
        )
    )

    selected_candidates = (
        scored_candidates
        if limit is None
        else scored_candidates[:limit]
    )

    reranked_guidance: list[dict[str, Any]] = []

    for new_rank, candidate in enumerate(selected_candidates, start=1):
        candidate = deepcopy(candidate)
        candidate["rank"] = new_rank
        candidate.pop("_tie_break_original_rank", None)
        reranked_guidance.append(candidate)

    result["retrieved_guidance"] = reranked_guidance
    result["retrieved_guidance_count"] = len(reranked_guidance)

    nested_retrieval_result = result.get("retrieval_result")

    if isinstance(nested_retrieval_result, Mapping):
        updated_nested_result = deepcopy(dict(nested_retrieval_result))
        updated_nested_result["results"] = deepcopy(reranked_guidance)
        updated_nested_result["result_count"] = len(reranked_guidance)
        result["retrieval_result"] = updated_nested_result

    result["reranking"] = {
        "reranker_name": RERANKER_NAME,
        "reranker_version": RERANKER_VERSION,
        "reranker_model_name": resolved_model_name,
        "reranking_status": "RERANKED",
        "candidate_count": candidate_count,
        "reranked_count": len(reranked_guidance),
        "controlled_query_fingerprint": controlled_query.get(
            "query_fingerprint"
        ),
    }

    return result