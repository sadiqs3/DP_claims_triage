from __future__ import annotations

from typing import Any, Callable, Mapping

from src.agent.response_guardrail import build_guarded_agent_response
from src.tools.deterministic_triage import run_deterministic_triage


WORKFLOW_NAME = "guarded_claim_triage_orchestrator"
WORKFLOW_VERSION = "reference_v1"

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
    this function, but its output must still pass through the guardrail.
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
            "Continue with standard processing. This routing result is "
            "decision support only and is not a payment approval."
        ),
        "INFO_REQUIRED": (
            "Request only the missing, invalid, or unreadable information "
            "identified in the authoritative rule trace."
        ),
        "MANUAL_REVIEW": (
            "Route the case to an analyst for review. Do not infer fraud, "
            "customer fault, or a final denial from this routing outcome."
        ),
        "NOT_ELIGIBLE": (
            "Do not continue standard eligibility processing unless an "
            "authoritative policy-data correction or additional verified "
            "information changes the underlying facts."
        ),
    }

    next_step_messages = {
        "PROCEED": (
            "Continue the claim through the standard downstream workflow."
        ),
        "INFO_REQUIRED": (
            "Obtain the required information and reassess the claim."
        ),
        "MANUAL_REVIEW": (
            "Assign the claim to the appropriate reviewer queue."
        ),
        "NOT_ELIGIBLE": (
            "Follow the documented policy-process handling for this "
            "eligibility outcome."
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
    provide explanation content only; the response guardrail protects all
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

    final_response = build_guarded_agent_response(
        tool_result=tool_result,
        proposed_response=agent_proposal,
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
        "final_response": final_response,
    }