from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from src.agent.langgraph_orchestrator import (
    run_langgraph_guarded_claim_triage,
)


def make_tool_result() -> dict:
    """Return a valid deterministic-tool result for LangGraph tests."""
    return {
        "tool_name": "deterministic_triage",
        "tool_version": "rules_baseline_v1",
        "claim_id": "TEST-000001",
        "authoritative_fields": [
            "triage_outcome",
            "triggering_rule_id",
            "precedence_stage",
            "decision_reason",
            "rule_trace",
            "system_limitations",
        ],
        "authority_notice": (
            "The deterministic triage decision is authoritative."
        ),
        "deterministic_decision": {
            "claim_id": "TEST-000001",
            "triage_outcome": "NOT_ELIGIBLE",
            "triggering_rule_id": "LIM-001",
            "precedence_stage": 2,
            "decision_reason": (
                "The plan's annual claim allowance is exhausted."
            ),
            "rule_trace": [
                {
                    "rule_id": "LIM-001",
                    "precedence_stage": 2,
                    "evaluation": "TRIGGERED",
                    "observed_value": {
                        "annual_claims_used": 1,
                        "annual_claim_limit": 1,
                    },
                }
            ],
            "system_limitations": [
                "DEV-003 is not evaluated in this runtime."
            ],
            "decision_support_only": True,
        },
    }


class TestLangGraphGuardedClaimTriage(unittest.TestCase):
    """Tests for the LangGraph guarded claim-triage workflow."""

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage"
    )
    def test_template_workflow_preserves_authoritative_decision(
        self,
        mock_run_deterministic_triage,
    ):
        mock_run_deterministic_triage.return_value = make_tool_result()

        workflow = run_langgraph_guarded_claim_triage(
            data={"runtime": "test-data"},
            claim_id="TEST-000001",
        )

        final_response = workflow["final_response"]

        self.assertEqual(
            workflow["workflow_name"],
            "langgraph_guarded_claim_triage",
        )
        self.assertEqual(
            workflow["workflow_version"],
            "langgraph_v1",
        )
        self.assertEqual(
            workflow["workflow_status"],
            "COMPLETED",
        )
        self.assertEqual(
            final_response["triage_outcome"],
            "NOT_ELIGIBLE",
        )
        self.assertEqual(
            final_response["triggering_rule_id"],
            "LIM-001",
        )
        self.assertEqual(
            final_response["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertIn(
            "case_summary",
            final_response["agent_content"],
        )
        self.assertEqual(
            workflow["workflow_trace"][1]["proposal_source"],
            "TEMPLATE",
        )
        self.assertEqual(
            len(workflow["workflow_trace"]),
            3,
        )

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage"
    )
    def test_custom_override_attempt_is_blocked(
        self,
        mock_run_deterministic_triage,
    ):
        mock_run_deterministic_triage.return_value = make_tool_result()

        def override_builder(tool_result: dict) -> dict:
            return {
                "triage_outcome": "PROCEED",
                "triggering_rule_id": "OUT-001",
                "precedence_stage": 6,
                "decision_reason": "The claim is approved.",
                "case_summary": "Custom explanation remains allowed.",
            }

        workflow = run_langgraph_guarded_claim_triage(
            data={"runtime": "test-data"},
            claim_id="TEST-000001",
            proposal_builder=override_builder,
        )

        final_response = workflow["final_response"]

        self.assertEqual(
            final_response["triage_outcome"],
            "NOT_ELIGIBLE",
        )
        self.assertEqual(
            final_response["triggering_rule_id"],
            "LIM-001",
        )
        self.assertEqual(
            final_response["authority_guardrail"]["status"],
            "OVERRIDE_BLOCKED",
        )
        self.assertEqual(
            final_response["agent_content"]["case_summary"],
            "Custom explanation remains allowed.",
        )
        self.assertEqual(
            workflow["workflow_trace"][1]["proposal_source"],
            "CUSTOM",
        )

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage"
    )
    def test_none_custom_proposal_returns_empty_agent_content(
        self,
        mock_run_deterministic_triage,
    ):
        mock_run_deterministic_triage.return_value = make_tool_result()

        workflow = run_langgraph_guarded_claim_triage(
            data={"runtime": "test-data"},
            claim_id="TEST-000001",
            proposal_builder=lambda tool_result: None,
        )

        final_response = workflow["final_response"]

        self.assertEqual(final_response["agent_content"], {})
        self.assertEqual(
            final_response["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertEqual(
            workflow["workflow_trace"][1]["proposal_source"],
            "CUSTOM",
        )

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage"
    )
    def test_invalid_custom_proposal_type_is_rejected(
        self,
        mock_run_deterministic_triage,
    ):
        mock_run_deterministic_triage.return_value = deepcopy(
            make_tool_result()
        )

        with self.assertRaises(ValueError):
            run_langgraph_guarded_claim_triage(
                data={"runtime": "test-data"},
                claim_id="TEST-000001",
                proposal_builder=lambda tool_result: [
                    "this",
                    "is",
                    "not",
                    "a mapping",
                ],
            )


if __name__ == "__main__":
    unittest.main()