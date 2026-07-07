from __future__ import annotations

import operator
from typing import Any, Mapping, Sequence

from langgraph.graph import END, START, StateGraph
from typing_extensions import Annotated, TypedDict

from src.agent.agent_content_guardrail import (
    apply_agent_content_safety_guardrail,
)
from src.agent.orchestrator import (
    ProposalBuilder,
    build_template_proposal,
)
from src.agent.response_guardrail import build_guarded_agent_response
from src.tools.deterministic_triage import run_deterministic_triage
from src.tools.follow_up_selection import (
    run_controlled_follow_up_selection,
)


WORKFLOW_NAME = "langgraph_guarded_claim_triage"
WORKFLOW_VERSION = "langgraph_v3"


class GuardedClaimTriageState(TypedDict, total=False):
    """State shared across the guarded LangGraph workflow."""

    claim_id: str
    questions_already_asked: Sequence[str] | str | None
    tool_result: dict[str, Any]
    follow_up_tool_result: dict[str, Any]
    controlled_follow_up: dict[str, Any]
    agent_proposal: dict[str, Any]
    proposal_source: str
    content_safety: dict[str, Any]
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


def create_guarded_claim_triage_graph(
    data: Mapping[str, Any],
    proposal_builder: ProposalBuilder | None = None,
):
    """
    Create the protected LangGraph claim-triage workflow.

    Deterministic triage remains authoritative. Controlled follow-up selection
    may return only approved catalogue questions. Explanation content passes
    through a semantic safety guardrail before the response guardrail protects
    authoritative routing fields.
    """

    def deterministic_triage_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = run_deterministic_triage(
            data=data,
            claim_id=state["claim_id"],
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

    def controlled_follow_up_selection_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = _as_dict(state.get("tool_result"))

        follow_up_tool_result = run_controlled_follow_up_selection(
            data=data,
            claim_id=state["claim_id"],
            deterministic_tool_result=tool_result,
            questions_already_asked=state.get(
                "questions_already_asked"
            ),
        )

        controlled_follow_up = _as_dict(
            follow_up_tool_result.get("follow_up_selection")
        )

        return {
            "follow_up_tool_result": follow_up_tool_result,
            "controlled_follow_up": controlled_follow_up,
            "workflow_trace": [
                {
                    "node": "controlled_follow_up_selection",
                    "status": "COMPLETED",
                    "follow_up_required": controlled_follow_up.get(
                        "follow_up_required"
                    ),
                    "selection_status": controlled_follow_up.get(
                        "selection_status"
                    ),
                    "question_ids": controlled_follow_up.get(
                        "question_ids",
                        [],
                    ),
                }
            ],
        }

    def explanation_proposal_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = _as_dict(state.get("tool_result"))

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

    def agent_content_safety_guardrail_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = _as_dict(state.get("tool_result"))
        agent_proposal = _as_dict(state.get("agent_proposal"))

        content_safety_result = apply_agent_content_safety_guardrail(
            tool_result=tool_result,
            proposed_content=agent_proposal,
        )

        return {
            "content_safety": content_safety_result,
            "workflow_trace": [
                {
                    "node": "agent_content_safety_guardrail",
                    "status": "COMPLETED",
                    "content_safety_status": content_safety_result[
                        "content_safety_status"
                    ],
                    "fallback_used": content_safety_result[
                        "fallback_used"
                    ],
                    "content_safety_violations": content_safety_result[
                        "content_safety_violations"
                    ],
                }
            ],
        }

    def response_guardrail_node(
        state: GuardedClaimTriageState,
    ) -> dict[str, Any]:
        tool_result = _as_dict(state.get("tool_result"))
        agent_proposal = _as_dict(state.get("agent_proposal"))
        content_safety = _as_dict(state.get("content_safety"))
        controlled_follow_up = _as_dict(
            state.get("controlled_follow_up")
        )
        follow_up_tool_result = _as_dict(
            state.get("follow_up_tool_result")
        )

        response_guardrail_input = dict(agent_proposal)
        response_guardrail_input.update(
            _as_dict(content_safety.get("agent_content"))
        )

        final_response = build_guarded_agent_response(
            tool_result=tool_result,
            proposed_response=response_guardrail_input,
        )

        final_response["controlled_follow_up"] = (
            controlled_follow_up
        )
        final_response["controlled_follow_up_source"] = (
            f"{follow_up_tool_result.get('tool_name', 'unknown')}:"
            f"{follow_up_tool_result.get('tool_version', 'unknown')}"
        )
        final_response["controlled_follow_up_notice"] = (
            follow_up_tool_result.get("authority_notice", "")
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

    workflow = StateGraph(GuardedClaimTriageState)

    workflow.add_node(
        "deterministic_triage",
        deterministic_triage_node,
    )
    workflow.add_node(
        "controlled_follow_up_selection",
        controlled_follow_up_selection_node,
    )
    workflow.add_node(
        "explanation_proposal",
        explanation_proposal_node,
    )
    workflow.add_node(
        "agent_content_safety_guardrail",
        agent_content_safety_guardrail_node,
    )
    workflow.add_node(
        "response_guardrail",
        response_guardrail_node,
    )

    workflow.add_edge(START, "deterministic_triage")
    workflow.add_edge(
        "deterministic_triage",
        "controlled_follow_up_selection",
    )
    workflow.add_edge(
        "controlled_follow_up_selection",
        "explanation_proposal",
    )
    workflow.add_edge(
        "explanation_proposal",
        "agent_content_safety_guardrail",
    )
    workflow.add_edge(
        "agent_content_safety_guardrail",
        "response_guardrail",
    )
    workflow.add_edge("response_guardrail", END)

    return workflow.compile()


def run_langgraph_guarded_claim_triage(
    data: Mapping[str, Any],
    claim_id: str,
    proposal_builder: ProposalBuilder | None = None,
    questions_already_asked: Sequence[str] | str | None = None,
) -> dict[str, Any]:
    """Run the protected LangGraph claim-triage workflow."""
    graph = create_guarded_claim_triage_graph(
        data=data,
        proposal_builder=proposal_builder,
    )

    state = graph.invoke(
        {
            "claim_id": claim_id,
            "questions_already_asked": questions_already_asked,
            "workflow_trace": [],
        }
    )

    return {
        "workflow_name": WORKFLOW_NAME,
        "workflow_version": WORKFLOW_VERSION,
        "workflow_status": "COMPLETED",
        "claim_id": state["claim_id"],
        "workflow_trace": state["workflow_trace"],
        "tool_result": state["tool_result"],
        "follow_up_tool_result": state["follow_up_tool_result"],
        "agent_proposal": state["agent_proposal"],
        "proposal_source": state["proposal_source"],
        "content_safety": state["content_safety"],
        "final_response": state["final_response"],
    }