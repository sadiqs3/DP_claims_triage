from __future__ import annotations

from typing import Any, Mapping


ALLOWED_TRIAGE_OUTCOMES = {
    "PROCEED",
    "INFO_REQUIRED",
    "MANUAL_REVIEW",
    "NOT_ELIGIBLE",
}

AUTHORITATIVE_DECISION_FIELDS = (
    "claim_id",
    "triage_outcome",
    "triggering_rule_id",
    "precedence_stage",
    "decision_reason",
    "rule_trace",
    "system_limitations",
    "decision_support_only",
)

ALLOWED_AGENT_CONTENT_FIELDS = (
    "case_summary",
    "reviewer_note",
    "next_step_message",
)


def _as_mapping(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _clean_optional_text(
    value: object,
    field_name: str,
) -> str | None:
    """Return trimmed optional text or raise for a non-string value."""
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string or None.")

    cleaned_value = value.strip()

    return cleaned_value or None


def _validate_authoritative_tool_result(
    tool_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate and return the authoritative deterministic decision."""
    result = _as_mapping(tool_result)

    if result.get("tool_name") != "deterministic_triage":
        raise ValueError(
            "tool_result must originate from deterministic_triage."
        )

    decision = _as_mapping(result.get("deterministic_decision"))

    missing_fields = [
        field_name
        for field_name in AUTHORITATIVE_DECISION_FIELDS
        if field_name not in decision
    ]

    if missing_fields:
        raise ValueError(
            "deterministic_decision is missing required fields: "
            + ", ".join(missing_fields)
        )

    if decision["triage_outcome"] not in ALLOWED_TRIAGE_OUTCOMES:
        raise ValueError("deterministic_decision has an invalid outcome.")

    if decision["decision_support_only"] is not True:
        raise ValueError(
            "deterministic_decision must be decision-support-only."
        )

    if not isinstance(decision["rule_trace"], list):
        raise ValueError("deterministic_decision.rule_trace must be a list.")

    if not isinstance(decision["system_limitations"], list):
        raise ValueError(
            "deterministic_decision.system_limitations must be a list."
        )

    return decision


def _find_authority_conflicts(
    proposed_response: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> list[str]:
    """
    Identify attempted changes to authoritative decision fields.

    Matching values are allowed but ignored. Conflicting values are recorded
    and blocked from the canonical response.
    """
    conflicts = []

    for field_name in AUTHORITATIVE_DECISION_FIELDS:
        if field_name not in proposed_response:
            continue

        if proposed_response[field_name] != decision[field_name]:
            conflicts.append(field_name)

    return conflicts


def build_guarded_agent_response(
    tool_result: Mapping[str, Any],
    proposed_response: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Combine authoritative deterministic routing with non-authoritative
    agent-generated explanation fields.

    The deterministic decision is always copied from the tool result.
    Any conflicting LLM-supplied decision fields are ignored and recorded.
    """
    result = _as_mapping(tool_result)
    decision = _validate_authoritative_tool_result(result)
    proposal = _as_mapping(proposed_response)

    conflicting_fields = _find_authority_conflicts(
        proposed_response=proposal,
        decision=decision,
    )

    agent_content = {
        field_name: _clean_optional_text(
            proposal.get(field_name),
            field_name,
        )
        for field_name in ALLOWED_AGENT_CONTENT_FIELDS
    }

    agent_content = {
        field_name: value
        for field_name, value in agent_content.items()
        if value is not None
    }

    ignored_fields = sorted(
        field_name
        for field_name in proposal
        if (
            field_name not in AUTHORITATIVE_DECISION_FIELDS
            and field_name not in ALLOWED_AGENT_CONTENT_FIELDS
        )
    )

    return {
        **decision,
        "tool_name": result["tool_name"],
        "tool_version": result["tool_version"],
        "agent_content": agent_content,
        "authority_guardrail": {
            "status": (
                "OVERRIDE_BLOCKED"
                if conflicting_fields
                else "ALIGNED"
            ),
            "authoritative_source": (
                f"{result['tool_name']}:{result['tool_version']}"
            ),
            "conflicting_authority_fields": conflicting_fields,
            "ignored_agent_fields": ignored_fields,
            "authority_notice": (
                "The deterministic triage decision is authoritative for "
                "eligibility routing. Agent-generated content is "
                "non-authoritative explanation only."
            ),
        },
    }