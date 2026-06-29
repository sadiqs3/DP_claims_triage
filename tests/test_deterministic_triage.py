from __future__ import annotations

from copy import deepcopy
import unittest
from unittest.mock import patch

from src.tools.deterministic_triage import (
    TOOL_NAME,
    TOOL_VERSION,
    run_deterministic_triage,
)
from src.triage_engine import triage_claim


def make_clean_context() -> dict:
    """Return a valid context that should reach OUT-001."""
    return {
        "claim_id": "TEST-000001",
        "policy_lookup_status": "UNIQUE_MATCH",
        "claim": {
            "claim_id": "TEST-000001",
            "claim_category_selected": "SCREEN_DAMAGE",
        },
        "policy_eligibility": {
            "policy_incident_status": "ACTIVE_ON_INCIDENT_DATE",
        },
        "plan_configuration": {
            "plan_configuration_available": True,
            "plan_configuration_status": "ACTIVE_CONFIGURATION_AVAILABLE",
            "product_scope_status": "IN_SCOPE",
            "product_scope_supported": True,
            "plan_configuration": {
                "plan_id": "DP-ESSENTIAL",
                "annual_claim_limit": 1,
                "maximum_theft_claims": 0,
            },
        },
        "coverage": {
            "coverage_lookup_status": "UNIQUE_COVERAGE_RECORD",
            "covered_flag": True,
        },
        "device_match": {
            "status": "DEVICE_MATCH",
        },
        "claim_history": {
            "annual_claims_used": 0,
            "theft_claims_used": 0,
        },
        "risk": {
            "has_triggered_risk": False,
            "recommended_action": None,
            "risk_indicator_ids": [],
            "manual_review_reasons": [],
        },
        "evidence": {
            "evidence_assessment_status": "SUFFICIENT",
            "evidence_profile_id": "EVD-SCREEN-01",
            "missing_required_evidence_types": [],
            "unreadable_required_evidence_types": [],
        },
    }


class TestDeterministicTriageTool(unittest.TestCase):
    """Tests for the controlled deterministic-triage adapter."""

    @patch("src.tools.deterministic_triage.assemble_claim_context")
    def test_returns_authoritative_engine_decision(
        self,
        mock_assemble_claim_context,
    ):
        context = make_clean_context()
        mock_assemble_claim_context.return_value = context

        runtime_data = {"runtime": "test-data"}

        result = run_deterministic_triage(
            data=runtime_data,
            claim_id="  TEST-000001  ",
        )

        expected_decision = triage_claim(context)

        mock_assemble_claim_context.assert_called_once_with(
            data=runtime_data,
            claim_id="TEST-000001",
        )

        self.assertEqual(result["tool_name"], TOOL_NAME)
        self.assertEqual(result["tool_version"], TOOL_VERSION)
        self.assertEqual(result["claim_id"], "TEST-000001")
        self.assertEqual(
            result["deterministic_decision"],
            expected_decision,
        )

        self.assertIn(
            "triage_outcome",
            result["authoritative_fields"],
        )
        self.assertIn(
            "must not override",
            result["authority_notice"],
        )

    @patch("src.tools.deterministic_triage.assemble_claim_context")
    def test_preserves_manual_review_decision(
        self,
        mock_assemble_claim_context,
    ):
        context = make_clean_context()
        context["policy_lookup_status"] = "MULTIPLE_MATCH"

        mock_assemble_claim_context.return_value = deepcopy(context)

        result = run_deterministic_triage(
            data={"runtime": "test-data"},
            claim_id="TEST-000002",
        )

        decision = result["deterministic_decision"]

        self.assertEqual(
            decision["triage_outcome"],
            "MANUAL_REVIEW",
        )
        self.assertEqual(
            decision["triggering_rule_id"],
            "DATA-002",
        )
        self.assertTrue(decision["decision_support_only"])

    def test_rejects_invalid_claim_id(self):
        invalid_claim_ids = [
            None,
            "",
            "   ",
            123,
        ]

        for claim_id in invalid_claim_ids:
            with self.subTest(claim_id=claim_id):
                with self.assertRaises(ValueError):
                    run_deterministic_triage(
                        data={"runtime": "test-data"},
                        claim_id=claim_id,
                    )


if __name__ == "__main__":
    unittest.main()