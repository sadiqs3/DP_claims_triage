from __future__ import annotations

import unittest

from src.agent.response_guardrail import build_guarded_agent_response


def make_tool_result() -> dict:
    """Return a deterministic-triage tool result for testing."""
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


class TestResponseGuardrail(unittest.TestCase):
    """Tests for protecting deterministic decisions from agent override."""

    def test_aligned_agent_content_is_allowed(self):
        tool_result = make_tool_result()

        proposed_response = {
            "case_summary": "The claim reached the annual limit rule.",
            "reviewer_note": "No manual override should be inferred.",
            "next_step_message": "Follow the deterministic decision.",
        }

        guarded_response = build_guarded_agent_response(
            tool_result=tool_result,
            proposed_response=proposed_response,
        )

        self.assertEqual(
            guarded_response["triage_outcome"],
            "NOT_ELIGIBLE",
        )
        self.assertEqual(
            guarded_response["triggering_rule_id"],
            "LIM-001",
        )
        self.assertEqual(
            guarded_response["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertEqual(
            guarded_response["agent_content"]["case_summary"],
            proposed_response["case_summary"],
        )
        self.assertEqual(
            guarded_response["authority_guardrail"][
                "conflicting_authority_fields"
            ],
            [],
        )

    def test_conflicting_agent_decision_is_blocked(self):
        tool_result = make_tool_result()

        proposed_response = {
            "triage_outcome": "PROCEED",
            "triggering_rule_id": "OUT-001",
            "precedence_stage": 6,
            "decision_reason": "The claim is approved.",
            "case_summary": "This explanation is allowed.",
        }

        guarded_response = build_guarded_agent_response(
            tool_result=tool_result,
            proposed_response=proposed_response,
        )

        self.assertEqual(
            guarded_response["triage_outcome"],
            "NOT_ELIGIBLE",
        )
        self.assertEqual(
            guarded_response["triggering_rule_id"],
            "LIM-001",
        )
        self.assertEqual(
            guarded_response["precedence_stage"],
            2,
        )
        self.assertEqual(
            guarded_response["decision_reason"],
            "The plan's annual claim allowance is exhausted.",
        )
        self.assertEqual(
            guarded_response["authority_guardrail"]["status"],
            "OVERRIDE_BLOCKED",
        )
        self.assertEqual(
            guarded_response["authority_guardrail"][
                "conflicting_authority_fields"
            ],
            [
                "triage_outcome",
                "triggering_rule_id",
                "precedence_stage",
                "decision_reason",
            ],
        )
        self.assertEqual(
            guarded_response["agent_content"]["case_summary"],
            "This explanation is allowed.",
        )

    def test_unexpected_agent_fields_are_ignored(self):
        tool_result = make_tool_result()

        proposed_response = {
            "case_summary": "Allowed summary.",
            "payout_authorized": True,
            "fraud_confirmed": True,
        }

        guarded_response = build_guarded_agent_response(
            tool_result=tool_result,
            proposed_response=proposed_response,
        )

        self.assertEqual(
            guarded_response["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertEqual(
            guarded_response["authority_guardrail"][
                "ignored_agent_fields"
            ],
            [
                "fraud_confirmed",
                "payout_authorized",
            ],
        )
        self.assertNotIn("payout_authorized", guarded_response)
        self.assertNotIn("fraud_confirmed", guarded_response)

    def test_invalid_tool_source_is_rejected(self):
        tool_result = make_tool_result()
        tool_result["tool_name"] = "some_other_tool"

        with self.assertRaises(ValueError):
            build_guarded_agent_response(
                tool_result=tool_result,
                proposed_response={},
            )

    def test_invalid_agent_content_type_is_rejected(self):
        tool_result = make_tool_result()

        with self.assertRaises(ValueError):
            build_guarded_agent_response(
                tool_result=tool_result,
                proposed_response={
                    "case_summary": ["not", "a", "string"],
                },
            )


if __name__ == "__main__":
    unittest.main()