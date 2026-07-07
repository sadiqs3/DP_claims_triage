from __future__ import annotations

from typing import Any, Mapping, Sequence

import pandas as pd

from src.claim_context import assemble_claim_context
from src.tools.follow_up_questions import select_follow_up_questions


TOOL_NAME = "controlled_follow_up_selection"
TOOL_VERSION = "v1"


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dictionary."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def run_controlled_follow_up_selection(
    data: Mapping[str, Any],
    claim_id: str,
    deterministic_tool_result: Mapping[str, Any],
    questions_already_asked: Sequence[str] | str | None = None,
) -> dict[str, Any]:
    """
    Select approved follow-up questions after deterministic triage.

    This adapter does not rerun or alter triage routing. It uses the supplied
    authoritative deterministic decision and structured claim context only to
    select catalogue-based questions for INFO_REQUIRED cases.
    """
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ValueError("claim_id must be a non-empty string.")

    normalised_claim_id = claim_id.strip()

    tool_result = _as_dict(deterministic_tool_result)
    deterministic_decision = _as_dict(
        tool_result.get("deterministic_decision")
    )

    if not deterministic_decision:
        raise ValueError(
            "deterministic_tool_result must contain deterministic_decision."
        )

    decision_claim_id = str(
        deterministic_decision.get("claim_id", "")
    ).strip()

    if decision_claim_id != normalised_claim_id:
        raise ValueError(
            "claim_id does not match deterministic_decision claim_id."
        )

    question_catalog = data.get("follow_up_question_catalog")

    if not isinstance(question_catalog, pd.DataFrame):
        raise ValueError(
            "Runtime data is missing follow_up_question_catalog."
        )

    context = assemble_claim_context(
        data=dict(data),
        claim_id=normalised_claim_id,
    )

    selection_result = select_follow_up_questions(
        context=context,
        deterministic_decision=deterministic_decision,
        question_catalog=question_catalog,
        questions_already_asked=questions_already_asked,
    )

    return {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "claim_id": normalised_claim_id,
        "decision_source": (
            f"{tool_result.get('tool_name', 'deterministic_triage')}:"
            f"{tool_result.get('tool_version', 'unknown')}"
        ),
        "authority_notice": (
            "Follow-up selection is deterministic and uses only approved "
            "catalogue questions. It does not alter the authoritative "
            "triage outcome, triggering rule, or decision rationale."
        ),
        "follow_up_selection": selection_result,
    }