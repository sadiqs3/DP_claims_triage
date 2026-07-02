from __future__ import annotations

import re
from typing import Any, Mapping

from src.agent.response_guardrail import ALLOWED_AGENT_CONTENT_FIELDS


CONTENT_SAFETY_VERSION = "v1"

PROHIBITED_PATTERNS: dict[str, re.Pattern[str]] = {
    "RESTRICTS_HUMAN_REVIEW": re.compile(
        r"\b(?:do not|don't|must not|should not|cannot)\s+"
        r"(?:override|reinterpret|reassess|reopen|review|challenge|escalate)\b",
        flags=re.IGNORECASE,
    ),
    "IMPLIES_FINAL_DECISION": re.compile(
        r"\b(?:final|definitive|binding)\s+"
        r"(?:approval|denial|rejection|determination|decision)\b",
        flags=re.IGNORECASE,
    ),
    "IMPLIES_CUSTOMER_OUTCOME": re.compile(
        r"\b(?:claim|case)\s+(?:is|was|has been)\s+"
        r"(?:approved|denied|rejected|paid|settled)\b",
        flags=re.IGNORECASE,
    ),
    "IMPLIES_FRAUD_CONCLUSION": re.compile(
        r"\b(?:fraud|fraudulent)\s+(?:is|was|has been)\s+"
        r"(?:confirmed|determined|established)\b",
        flags=re.IGNORECASE,
    ),
}


NEXT_STEP_BY_OUTCOME = {
    "PROCEED": (
        "Continue with the approved processing workflow while completing any "
        "required operational checks."
    ),
    "INFO_REQUIRED": (
        "Request the missing information or evidence through the approved "
        "case-management process before further triage."
    ),
    "MANUAL_REVIEW": (
        "Route the case through the approved manual-review process and "
        "document the escalation reason."
    ),
    "NOT_ELIGIBLE": (
        "Record the system triage recommendation and route the case through "
        "the approved analyst review or escalation process before any final "
        "customer communication."
    ),
}


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dictionary."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _clean_text(value: object) -> str | None:
    """Return non-empty stripped text, otherwise None."""
    if not isinstance(value, str):
        return None

    cleaned_value = value.strip()
    return cleaned_value or None


def _extract_agent_content(
    proposed_content: Mapping[str, Any] | None,
) -> tuple[dict[str, str], list[str]]:
    """Extract only permitted explanation fields and identify invalid content."""
    proposal = _as_dict(proposed_content)
    content: dict[str, str] = {}
    violations: list[str] = []

    for field_name in ALLOWED_AGENT_CONTENT_FIELDS:
        field_value = _clean_text(proposal.get(field_name))

        if field_value is None:
            violations.append(f"MISSING_OR_INVALID_{field_name.upper()}")
        else:
            content[field_name] = field_value

    return content, violations


def _get_deterministic_decision(
    tool_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Extract the required deterministic decision from a tool result."""
    result = _as_dict(tool_result)
    decision = _as_dict(result.get("deterministic_decision"))

    required_fields = (
        "claim_id",
        "triage_outcome",
        "triggering_rule_id",
        "decision_reason",
        "system_limitations",
    )

    missing_fields = [
        field_name
        for field_name in required_fields
        if field_name not in decision
    ]

    if missing_fields:
        raise ValueError(
            "deterministic_decision is missing required fields: "
            + ", ".join(missing_fields)
        )

    return decision


def _format_limitations(system_limitations: object) -> str:
    """Convert known system limitations into concise analyst-facing text."""
    if not isinstance(system_limitations, list) or not system_limitations:
        return "No additional system limitations were supplied."

    limitation_text = "; ".join(
        str(limitation).strip()
        for limitation in system_limitations
        if str(limitation).strip()
    )

    if not limitation_text:
        return "No additional system limitations were supplied."

    return f"System limitations: {limitation_text}"


def build_safe_fallback_content(
    tool_result: Mapping[str, Any],
) -> dict[str, str]:
    """
    Build deterministic, human-controlled fallback explanation content.

    This content never changes the deterministic recommendation and always
    preserves the authorised human-review boundary.
    """
    decision = _get_deterministic_decision(tool_result)

    triage_outcome = str(decision["triage_outcome"])
    rule_id = str(decision["triggering_rule_id"])
    decision_reason = str(decision["decision_reason"])
    limitations = _format_limitations(decision["system_limitations"])

    return {
        "case_summary": (
            f"System triage recommendation: {triage_outcome} under rule "
            f"{rule_id}. {decision_reason}"
        ),
        "reviewer_note": (
            "This is decision support only. An authorised reviewer may apply "
            "approved review, escalation, or exception-handling procedures "
            f"where appropriate. {limitations}"
        ),
        "next_step_message": NEXT_STEP_BY_OUTCOME.get(
            triage_outcome,
            (
                "Follow the approved analyst review process and document the "
                "system triage recommendation."
            ),
        ),
    }


def _find_semantic_violations(
    agent_content: Mapping[str, str],
) -> list[str]:
    """Identify unsafe or governance-incompatible wording."""
    combined_text = " ".join(
        agent_content.get(field_name, "")
        for field_name in ALLOWED_AGENT_CONTENT_FIELDS
    )

    violations: list[str] = []

    for violation_code, pattern in PROHIBITED_PATTERNS.items():
        if pattern.search(combined_text):
            violations.append(violation_code)

    reviewer_note = agent_content.get("reviewer_note", "").casefold()

    has_authorised_reviewer = (
        "authorised reviewer" in reviewer_note
        or "authorized reviewer" in reviewer_note
    )
    has_review_path = any(
        phrase in reviewer_note
        for phrase in (
            "review",
            "escalation",
            "exception-handling",
            "exception handling",
        )
    )

    if not (has_authorised_reviewer and has_review_path):
        violations.append("HUMAN_REVIEW_BOUNDARY_NOT_STATED")

    return violations


def apply_agent_content_safety_guardrail(
    tool_result: Mapping[str, Any],
    proposed_content: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """
    Validate LLM explanation text and apply a deterministic fallback if needed.

    This guardrail handles only non-authoritative explanation content. The
    downstream response guardrail remains responsible for authoritative fields.
    """
    extracted_content, violations = _extract_agent_content(proposed_content)

    if not violations:
        violations.extend(_find_semantic_violations(extracted_content))

    if violations:
        return {
            "agent_content": build_safe_fallback_content(tool_result),
            "content_safety_status": "FALLBACK_APPLIED",
            "content_safety_violations": sorted(set(violations)),
            "fallback_used": True,
            "content_safety_version": CONTENT_SAFETY_VERSION,
        }

    return {
        "agent_content": extracted_content,
        "content_safety_status": "SAFE",
        "content_safety_violations": [],
        "fallback_used": False,
        "content_safety_version": CONTENT_SAFETY_VERSION,
    }