import unittest
from unittest.mock import patch

from src.agent.langgraph_orchestrator import (
    WORKFLOW_VERSION,
    run_langgraph_guarded_claim_triage,
)


SAMPLE_TOOL_RESULT = {
    "tool_name": "deterministic_triage",
    "tool_version": "rules_baseline_v1",
    "claim_id": "CLM-TEST-001",
    "authority_notice": (
        "The deterministic decision is authoritative for triage routing."
    ),
    "deterministic_decision": {
        "claim_id": "CLM-TEST-001",
        "triage_outcome": "PROCEED",
        "triggering_rule_id": "OUT-001",
        "precedence_stage": 6,
        "decision_reason": (
            "No deterministic rule requiring a different triage route "
            "was triggered."
        ),
        "rule_trace": [],
        "system_limitations": [
            "Claim-history source completeness cannot be independently verified."
        ],
        "decision_support_only": True,
    },
}


class TestLangGraphGuardedClaimTriage(unittest.TestCase):

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage",
        return_value=SAMPLE_TOOL_RESULT,
    )
    def test_template_workflow_is_safe_and_has_four_nodes(
        self,
        mock_triage,
    ):
        result = run_langgraph_guarded_claim_triage(
            data={},
            claim_id="CLM-TEST-001",
        )

        self.assertEqual(WORKFLOW_VERSION, "langgraph_v2")
        self.assertEqual(result["workflow_status"], "COMPLETED")
        self.assertEqual(result["proposal_source"], "TEMPLATE")

        self.assertEqual(
            [
                item["node"]
                for item in result["workflow_trace"]
            ],
            [
                "deterministic_triage",
                "explanation_proposal",
                "agent_content_safety_guardrail",
                "response_guardrail",
            ],
        )

        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "SAFE",
        )
        self.assertFalse(result["content_safety"]["fallback_used"])

        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
        )

        mock_triage.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
        )

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage",
        return_value=SAMPLE_TOOL_RESULT,
    )
    def test_unsafe_content_and_authority_override_are_blocked(
        self,
        mock_triage,
    ):
        def unsafe_proposal_builder(tool_result):
            return {
                "case_summary": (
                    "The claim is approved for standard processing."
                ),
                "reviewer_note": (
                    "Do not override or reinterpret the outcome."
                ),
                "next_step_message": (
                    "Proceed with standard processing."
                ),
                "triage_outcome": "NOT_ELIGIBLE",
                "triggering_rule_id": "LIM-001",
            }

        result = run_langgraph_guarded_claim_triage(
            data={},
            claim_id="CLM-TEST-001",
            proposal_builder=unsafe_proposal_builder,
        )

        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["content_safety"]["fallback_used"])
        self.assertIn(
            "RESTRICTS_HUMAN_REVIEW",
            result["content_safety"]["content_safety_violations"],
        )

        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "OVERRIDE_BLOCKED",
        )
        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
        )
        self.assertEqual(
            result["final_response"]["triggering_rule_id"],
            "OUT-001",
        )

        self.assertIn(
            "authorised reviewer",
            result["final_response"]["agent_content"][
                "reviewer_note"
            ].casefold(),
        )

        mock_triage.assert_called_once()

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage",
        return_value=SAMPLE_TOOL_RESULT,
    )
    def test_none_custom_proposal_uses_safe_fallback(
        self,
        mock_triage,
    ):
        def empty_proposal_builder(tool_result):
            return None

        result = run_langgraph_guarded_claim_triage(
            data={},
            claim_id="CLM-TEST-001",
            proposal_builder=empty_proposal_builder,
        )

        self.assertEqual(result["proposal_source"], "CUSTOM")
        self.assertEqual(result["agent_proposal"], {})

        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["content_safety"]["fallback_used"])

        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertIn(
            "System triage recommendation",
            result["final_response"]["agent_content"]["case_summary"],
        )

        mock_triage.assert_called_once()

    @patch(
        "src.agent.langgraph_orchestrator.run_deterministic_triage",
        return_value=SAMPLE_TOOL_RESULT,
    )
    def test_invalid_custom_proposal_type_raises_error(
        self,
        mock_triage,
    ):
        def invalid_proposal_builder(tool_result):
            return ["not", "a", "mapping"]

        with self.assertRaisesRegex(
            ValueError,
            "proposal_builder must return a mapping or None.",
        ):
            run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                proposal_builder=invalid_proposal_builder,
            )

        mock_triage.assert_called_once()


if __name__ == "__main__":
    unittest.main()