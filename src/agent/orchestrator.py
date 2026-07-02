from __future__ import annotations

from typing import Any, Callable, Mapping

from src.agent.agent_content_guardrail import (
    apply_agent_content_safety_guardrail,
)
from src.agent.response_guardrail import build_guarded_agent_response
from src.tools.deterministic_triage import run_deterministic_triage


WORKFLOW_NAME = "guarded_claim_triage_orchestrator"
WORKFLOW_VERSION = "reference_v2"

ProposalBuilder = Callable[
    [Mapping[str, Any]],
    Mapping[str, Any] | None,
]


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def build_template_proposal(
    tool_result: Mapping[str, Any],
) -> dict[str, str]:
    """
    Create a deterministic, non-LLM explanation proposal.

    This is a safe reference implementation. A future LLM node may replace
    this function, but its output must still pass through both guardrails.
    """
    result = _as_dict(tool_result)
    decision = _as_dict(result.get("deterministic_decision"))

    required_fields = [
        "triage_outcome",
        "triggering_rule_id",
        "decision_reason",
    ]

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

    outcome = decision["triage_outcome"]
    rule_id = decision["triggering_rule_id"]
    decision_reason = decision["decision_reason"]

    case_summary = (
        f"Deterministic triage returned {outcome} under rule {rule_id}. "
        f"{decision_reason}"
    )

    reviewer_notes = {
        "PROCEED": (
            "This is a system triage recommendation and decision support only. "
            "An authorised reviewer may apply approved review, escalation, or "
            "exception-handling procedures where appropriate."
        ),
        "INFO_REQUIRED": (
            "This is a system triage recommendation. Obtain the missing, "
            "invalid, or unreadable information identified in the "
            "authoritative rule trace. An authorised reviewer may apply "
            "approved review, escalation, or exception-handling procedures "
            "where appropriate."
        ),
        "MANUAL_REVIEW": (
            "This is a system triage recommendation. Route the case for "
            "analyst review without inferring fraud, customer fault, or a "
            "final denial. An authorised reviewer may apply approved review, "
            "escalation, or exception-handling procedures where appropriate."
        ),
        "NOT_ELIGIBLE": (
            "This is a system triage recommendation based on the deterministic "
            "rule result. An authorised reviewer may apply approved review, "
            "escalation, or exception-handling procedures where appropriate."
        ),
    }

    next_step_messages = {
        "PROCEED": (
            "Continue the claim through the approved downstream workflow."
        ),
        "INFO_REQUIRED": (
            "Obtain the required information and reassess the claim through "
            "the approved process."
        ),
        "MANUAL_REVIEW": (
            "Assign the claim to the appropriate reviewer queue."
        ),
        "NOT_ELIGIBLE": (
            "Record the system triage recommendation and follow the approved "
            "analyst review or escalation process before any final customer "
            "communication."
        ),
    }

    return {
        "case_summary": case_summary,
        "reviewer_note": reviewer_notes[outcome],
        "next_step_message": next_step_messages[outcome],
    }


def _build_agent_proposal(
    tool_result: Mapping[str, Any],
    proposal_builder: ProposalBuilder | None,
) -> tuple[dict[str, Any], str]:
    """Build a template or custom explanation proposal."""
    if proposal_builder is None:
        return build_template_proposal(tool_result), "TEMPLATE"

    proposal = proposal_builder(tool_result)

    if proposal is None:
        return {}, "CUSTOM"

    if not isinstance(proposal, Mapping):
        raise ValueError(
            "proposal_builder must return a mapping or None."
        )

    return dict(proposal), "CUSTOM"


def run_guarded_claim_orchestrator(
    data: Mapping[str, Any],
    claim_id: str,
    proposal_builder: ProposalBuilder | None = None,
) -> dict[str, Any]:
    """
    Run the protected claim-triage workflow.

    The deterministic tool remains authoritative. The proposal builder may
    provide explanation content only. The agent-content safety guardrail
    validates explanation wording before the response guardrail protects all
    eligibility-routing fields in the final response.
    """
    tool_result = run_deterministic_triage(
        data=data,
        claim_id=claim_id,
    )

    workflow_trace = [
        {
            "node": "deterministic_triage",
            "status": "COMPLETED",
            "authoritative": True,
            "tool_version": tool_result["tool_version"],
        }
    ]

    agent_proposal, proposal_source = _build_agent_proposal(
        tool_result=tool_result,
        proposal_builder=proposal_builder,
    )

    workflow_trace.append(
        {
            "node": "explanation_proposal",
            "status": "COMPLETED",
            "proposal_source": proposal_source,
            "proposed_field_names": sorted(agent_proposal.keys()),
        }
    )

    content_safety_result = apply_agent_content_safety_guardrail(
        tool_result=tool_result,
        proposed_content=agent_proposal,
    )

    workflow_trace.append(
        {
            "node": "agent_content_safety_guardrail",
            "status": "COMPLETED",
            "content_safety_status": content_safety_result[
                "content_safety_status"
            ],
            "fallback_used": content_safety_result["fallback_used"],
            "content_safety_violations": content_safety_result[
                "content_safety_violations"
            ],
        }
    )

    response_guardrail_input = dict(agent_proposal)
    response_guardrail_input.update(
        content_safety_result["agent_content"]
    )

    final_response = build_guarded_agent_response(
        tool_result=tool_result,
        proposed_response=response_guardrail_input,
    )

    workflow_trace.append(
        {
            "node": "response_guardrail",
            "status": "COMPLETED",
            "guardrail_status": final_response[
                "authority_guardrail"
            ]["status"],
        }
    )

    return {
        "workflow_name": WORKFLOW_NAME,
        "workflow_version": WORKFLOW_VERSION,
        "workflow_status": "COMPLETED",
        "claim_id": tool_result["claim_id"],
        "workflow_trace": workflow_trace,
        "tool_result": tool_result,
        "agent_proposal": agent_proposal,
        "proposal_source": proposal_source,
        "content_safety": content_safety_result,
        "final_response": final_response,
    }