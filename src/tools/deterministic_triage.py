from __future__ import annotations

from typing import Any, Mapping

from src.claim_context import assemble_claim_context
from src.triage_engine import triage_claim


TOOL_NAME = "deterministic_triage"
TOOL_VERSION = "rules_baseline_v1"

AUTHORITATIVE_FIELDS = [
    "triage_outcome",
    "triggering_rule_id",
    "precedence_stage",
    "decision_reason",
    "rule_trace",
    "system_limitations",
]


def run_deterministic_triage(
    data: Mapping[str, Any],
    claim_id: str,
) -> dict[str, Any]:
    """
    Assemble claim context and return the authoritative deterministic triage.

    This adapter does not load evaluation data, infer new facts, approve
    payment, determine fraud, or override the rules-engine decision.
    """
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ValueError("claim_id must be a non-empty string.")

    normalised_claim_id = claim_id.strip()

    context = assemble_claim_context(
        data=data,
        claim_id=normalised_claim_id,
    )

    decision = triage_claim(context)

    return {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "claim_id": decision["claim_id"],
        "authoritative_fields": AUTHORITATIVE_FIELDS,
        "authority_notice": (
            "The deterministic triage decision is authoritative for "
            "eligibility routing. Any later agent layer may explain or "
            "summarise it, but must not override it."
        ),
        "deterministic_decision": decision,
    }