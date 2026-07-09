from __future__ import annotations

# Formats retrieved KB chunks into analyst-only cited guidance.
# This module does not generate new policy advice or alter triage decisions.

from collections.abc import Mapping
from typing import Any


FORMATTER_NAME = "analyst_guidance_formatter"
FORMATTER_VERSION = "v1"

EXPECTED_AUTHORITY = "non_authoritative_guidance"
DEFAULT_MAX_PREVIEW_CHARS = 360


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _as_list(value: object, field_name: str) -> list[Any]:
    """Validate that a field is list-like for retrieved guidance."""
    if value is None:
        return []

    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")

    return value


def _clean_text(value: object) -> str:
    """Return compact single-line text."""
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


def _clean_score(value: object) -> float | None:
    """Return a rounded relevance score when numeric."""
    if isinstance(value, bool) or value is None:
        return None

    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return None


def _preview_text(
    value: object,
    max_preview_chars: int,
) -> str:
    """Return a bounded preview from approved KB text."""
    text = _clean_text(value)

    if not text:
        return ""

    if len(text) <= max_preview_chars:
        return text

    return text[: max_preview_chars - 3].rstrip() + "..."


def _build_source_reference(
    retrieved_item: Mapping[str, Any],
    fallback_rank: int,
) -> dict[str, Any]:
    """Build one stable analyst citation reference."""
    item = _as_dict(retrieved_item)
    source_reference = _as_dict(item.get("source_reference"))

    rank = _clean_rank(item.get("rank"), fallback_rank)
    reference_id = f"S{rank}"

    document_id = _clean_text(item.get("document_id"))
    chunk_id = _clean_text(item.get("chunk_id"))
    section_title = _clean_text(item.get("section_title"))

    return {
        "reference_id": reference_id,
        "rank": rank,
        "document_id": document_id,
        "chunk_id": chunk_id,
        "section_title": section_title,
        "relevance_score": _clean_score(item.get("relevance_score")),
        "source_relative_path": _clean_text(
            source_reference.get("source_relative_path")
        ),
        "source_label": (
            f"{reference_id}: {document_id} / {section_title}"
            if document_id and section_title
            else reference_id
        ),
    }


def format_analyst_guidance(
    rag_tool_result: Mapping[str, Any],
    max_preview_chars: int = DEFAULT_MAX_PREVIEW_CHARS,
) -> dict[str, Any]:
    """
    Format controlled RAG retrieval output for analyst review.

    The output is non-authoritative. It preserves source references but does
    not copy the retrieval query text, projected facts, claim identifiers,
    customer statements, or deterministic decision reasons.
    """
    if not isinstance(rag_tool_result, Mapping):
        raise ValueError("rag_tool_result must be a mapping.")

    if max_preview_chars < 80:
        raise ValueError("max_preview_chars must be at least 80.")

    result = dict(rag_tool_result)
    authority = result.get("authority")

    if authority != EXPECTED_AUTHORITY:
        raise ValueError(
            "rag_tool_result must contain non-authoritative guidance."
        )

    retrieved_guidance = _as_list(
        result.get("retrieved_guidance"),
        "retrieved_guidance",
    )

    controlled_query = _as_dict(result.get("controlled_query"))

    source_references: list[dict[str, Any]] = []
    guidance_items: list[dict[str, Any]] = []

    for index, retrieved_item in enumerate(retrieved_guidance, start=1):
        item = _as_dict(retrieved_item)
        source_reference = _build_source_reference(
            item,
            fallback_rank=index,
        )
        source_references.append(source_reference)

        guidance_items.append(
            {
                "reference_id": source_reference["reference_id"],
                "rank": source_reference["rank"],
                "source_label": source_reference["source_label"],
                "guidance_preview": _preview_text(
                    item.get("chunk_text"),
                    max_preview_chars=max_preview_chars,
                ),
                "use_boundary": (
                    "Use this approved KB source as analyst-facing "
                    "operational context only. Do not override the "
                    "deterministic triage decision, evidence requirements, "
                    "or controlled follow-up wording."
                ),
            }
        )

    retrieved_count = len(guidance_items)

    if retrieved_count:
        guidance_summary = (
            f"Retrieved {retrieved_count} approved KB section(s) for "
            "analyst review. These sources provide non-authoritative "
            "operational guidance only."
        )
    else:
        guidance_summary = (
            "No approved KB guidance was retrieved above the configured "
            "threshold. Do not invent guidance; continue with the "
            "deterministic workflow and approved analyst procedures."
        )

    return {
        "formatter_name": FORMATTER_NAME,
        "formatter_version": FORMATTER_VERSION,
        "authority": EXPECTED_AUTHORITY,
        "authority_notice": result.get("authority_notice", ""),
        "retrieval_status": result.get("retrieval_status"),
        "retrieved_guidance_count": retrieved_count,
        "guidance_summary": guidance_summary,
        "usage_boundary": (
            "This analyst guidance is separate from final_response and "
            "cannot change claim routing, coverage, evidence requirements, "
            "or customer-facing follow-up wording."
        ),
        "controlled_query_fingerprint": controlled_query.get(
            "query_fingerprint"
        ),
        "projection_source": result.get("projection_source"),
        "retrieval_source": result.get("retrieval_source"),
        "source_references": source_references,
        "guidance_items": guidance_items,
    }