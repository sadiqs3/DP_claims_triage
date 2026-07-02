import unittest

from src.agent.agent_content_guardrail import (
    apply_agent_content_safety_guardrail,
    build_safe_fallback_content,
)


SAMPLE_TOOL_RESULT = {
    "tool_name": "deterministic_triage",
    "deterministic_decision": {
        "claim_id": "CLM-TEST-001",
        "triage_outcome": "NOT_ELIGIBLE",
        "triggering_rule_id": "LIM-001",
        "precedence_stage": 2,
        "decision_reason": "The annual claim allowance is exhausted.",
        "rule_trace": [],
        "system_limitations": [
            "Claim-history source completeness cannot be independently verified."
        ],
        "decision_support_only": True,
    },
}


class TestAgentContentGuardrail(unittest.TestCase):

    def test_unsafe_human_review_restriction_uses_fallback(self):
        unsafe_content = {
            "case_summary": "The system routed the claim to NOT_ELIGIBLE.",
            "reviewer_note": (
                "Do not override or reinterpret the outcome."
            ),
            "next_step_message": "Continue with the standard workflow.",
        }

        result = apply_agent_content_safety_guardrail(
            tool_result=SAMPLE_TOOL_RESULT,
            proposed_content=unsafe_content,
        )

        self.assertEqual(
            result["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["fallback_used"])
        self.assertIn(
            "RESTRICTS_HUMAN_REVIEW",
            result["content_safety_violations"],
        )
        self.assertIn(
            "HUMAN_REVIEW_BOUNDARY_NOT_STATED",
            result["content_safety_violations"],
        )
        self.assertIn(
            "authorised reviewer",
            result["agent_content"]["reviewer_note"].casefold(),
        )

    def test_safe_content_is_retained(self):
        safe_content = {
            "case_summary": (
                "System triage recommendation: NOT_ELIGIBLE under LIM-001 "
                "because the annual claim allowance is exhausted."
            ),
            "reviewer_note": (
                "This is decision support only. An authorised reviewer may "
                "apply approved review or escalation procedures where appropriate."
            ),
            "next_step_message": (
                "Record the recommendation and follow the approved analyst "
                "review process before final customer communication."
            ),
        }

        result = apply_agent_content_safety_guardrail(
            tool_result=SAMPLE_TOOL_RESULT,
            proposed_content=safe_content,
        )

        self.assertEqual(result["content_safety_status"], "SAFE")
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["content_safety_violations"], [])
        self.assertEqual(result["agent_content"], safe_content)

    def test_missing_required_content_uses_fallback(self):
        incomplete_content = {
            "case_summary": "System triage recommendation is NOT_ELIGIBLE.",
            "reviewer_note": "",
        }

        result = apply_agent_content_safety_guardrail(
            tool_result=SAMPLE_TOOL_RESULT,
            proposed_content=incomplete_content,
        )

        self.assertEqual(
            result["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["fallback_used"])
        self.assertIn(
            "MISSING_OR_INVALID_NEXT_STEP_MESSAGE",
            result["content_safety_violations"],
        )

    def test_fallback_preserves_human_control(self):
        fallback_content = build_safe_fallback_content(SAMPLE_TOOL_RESULT)

        self.assertIn(
            "System triage recommendation",
            fallback_content["case_summary"],
        )
        self.assertIn(
            "authorised reviewer",
            fallback_content["reviewer_note"].casefold(),
        )
        self.assertIn(
            "before any final customer communication",
            fallback_content["next_step_message"].casefold(),
        )


if __name__ == "__main__":
    unittest.main()