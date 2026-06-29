from __future__ import annotations

import operator
from typing import Any, Callable, Mapping

from typing_extensions import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agent.orchestrator import build_template_proposal
from src.agent.response_guardrail import build_guarded_agent_response
from src.tools.deterministic_triage import run_deterministic_triage


WORKFLOW_NAME = "langgraph_guarded_claim_triage"
WORKFLOW_VERSION = "langgraph_v1"

ProposalBuilder = Callable[
    [Mapping[str, Any]],
    Mapping[str, Any] | None,
]


class GuardedClaimTriageState(TypedDict, total=False):
    """Shared state passed between LangGraph workflow nodes."""

    claim_id: str
    tool_result: dict[str, Any]
    agent_proposal: dict[str, Any]
    proposal_source: str
    final_response: dict[str, Any]
    workflow_trace: Annotated[list[dict[str, Any]], operator.add]


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _build_agent_proposal(
    tool_result: Mapping[str, Any],
    proposal_builder: ProposalBuilder | None,
) -> tuple[dict[str, Any], str]:
    """Build a template or custom non-authoritative explanation proposal."""
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


def create_guarded_claim_triage_graph(
    data: Mapping[str, Any],
    proposal_builder: ProposalBuilder | None = None,
):
    """
    Create the fixed LangGraph workflow for guarded claim triage.

    The deterministic tool remains authoritative for all eligibility-routing
    fields. The proposal builder may provide explanation only.
    """

    def deterministic_triage_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        claim_id = state.get("claim_id")

        if not isinstance(claim_id, str) or not claim_id.strip():
            raise ValueError("claim_id must be a non-empty string.")

        tool_result = run_deterministic_triage(
            data=data,
            claim_id=claim_id.strip(),
        )

        return {
            "tool_result": tool_result,
            "workflow_trace": [
                {
                    "node": "deterministic_triage",
                    "status": "COMPLETED",
                    "authoritative": True,
                    "tool_version": tool_result["tool_version"],
                }
            ],
        }

    def explanation_proposal_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = _as_dict(state.get("tool_result"))

        if not tool_result:
            raise ValueError(
                "tool_result is required before explanation generation."
            )

        agent_proposal, proposal_source = _build_agent_proposal(
            tool_result=tool_result,
            proposal_builder=proposal_builder,
        )

        return {
            "agent_proposal": agent_proposal,
            "proposal_source": proposal_source,
            "workflow_trace": [
                {
                    "node": "explanation_proposal",
                    "status": "COMPLETED",
                    "proposal_source": proposal_source,
                    "proposed_field_names": sorted(
                        agent_proposal.keys()
                    ),
                }
            ],
        }

    def response_guardrail_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = _as_dict(state.get("tool_result"))
        agent_proposal = _as_dict(state.get("agent_proposal"))

        if not tool_result:
            raise ValueError(
                "tool_result is required before guardrail evaluation."
            )

        final_response = build_guarded_agent_response(
            tool_result=tool_result,
            proposed_response=agent_proposal,
        )

        return {
            "final_response": final_response,
            "workflow_trace": [
                {
                    "node": "response_guardrail",
                    "status": "COMPLETED",
                    "guardrail_status": final_response[
                        "authority_guardrail"
                    ]["status"],
                }
            ],
        }

    graph_builder = StateGraph(GuardedClaimTriageState)

    graph_builder.add_node(
        "deterministic_triage",
        deterministic_triage_node,
    )
    graph_builder.add_node(
        "explanation_proposal",
        explanation_proposal_node,
    )
    graph_builder.add_node(
        "response_guardrail",
        response_guardrail_node,
    )

    graph_builder.add_edge(START, "deterministic_triage")
    graph_builder.add_edge(
        "deterministic_triage",
        "explanation_proposal",
    )
    graph_builder.add_edge(
        "explanation_proposal",
        "response_guardrail",
    )
    graph_builder.add_edge("response_guardrail", END)

    return graph_builder.compile()


def run_langgraph_guarded_claim_triage(
    data: Mapping[str, Any],
    claim_id: str,
    proposal_builder: ProposalBuilder | None = None,
) -> dict[str, Any]:
    """
    Run the complete LangGraph guarded triage workflow for one claim.
    """
    graph = create_guarded_claim_triage_graph(
        data=data,
        proposal_builder=proposal_builder,
    )

    final_state = graph.invoke(
        {
            "claim_id": claim_id,
            "workflow_trace": [],
        }
    )

    return {
        "workflow_name": WORKFLOW_NAME,
        "workflow_version": WORKFLOW_VERSION,
        "workflow_status": "COMPLETED",
        "claim_id": final_state["claim_id"],
        "workflow_trace": final_state["workflow_trace"],
        "final_response": final_state["final_response"],
    }