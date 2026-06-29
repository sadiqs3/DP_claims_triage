from copy import deepcopy
import unittest

from src.triage_engine import triage_claim


def make_clean_context() -> dict:
    """Return a fully valid baseline context that should PROCEED."""
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


class TestTriageEngine(unittest.TestCase):
    """Regression tests for deterministic triage routing and precedence."""

    def assert_decision(
        self,
        context: dict,
        expected_outcome: str,
        expected_rule: str,
        expected_stage: int,
    ) -> dict:
        decision = triage_claim(context)

        self.assertEqual(
            decision["triage_outcome"],
            expected_outcome,
        )
        self.assertEqual(
            decision["triggering_rule_id"],
            expected_rule,
        )
        self.assertEqual(
            decision["precedence_stage"],
            expected_stage,
        )
        self.assertTrue(decision["decision_support_only"])

        self.assertEqual(
            decision["rule_trace"][-1]["rule_id"],
            expected_rule,
        )
        self.assertEqual(
            decision["rule_trace"][-1]["evaluation"],
            "TRIGGERED",
        )

        return decision

    def test_supported_rule_routing(self):
        """Each supported baseline rule routes to its expected outcome."""

        scenarios = []

        context = make_clean_context()
        scenarios.append(
            (
                "OUT-001 proceed",
                context,
                "PROCEED",
                "OUT-001",
                6,
            )
        )

        context = make_clean_context()
        context["policy_lookup_status"] = "NO_MATCH"
        scenarios.append(
            (
                "DATA-001 no policy match",
                context,
                "INFO_REQUIRED",
                "DATA-001",
                1,
            )
        )

        context = make_clean_context()
        context["policy_lookup_status"] = "MULTIPLE_MATCH"
        scenarios.append(
            (
                "DATA-002 multiple policy match",
                context,
                "MANUAL_REVIEW",
                "DATA-002",
                1,
            )
        )

        context = make_clean_context()
        context["plan_configuration"][
            "plan_configuration_status"
        ] = "CONFIGURATION_INCOMPLETE"
        context["plan_configuration"][
            "plan_configuration_available"
        ] = False
        scenarios.append(
            (
                "DATA-003 incomplete configuration",
                context,
                "MANUAL_REVIEW",
                "DATA-003",
                1,
            )
        )

        context = make_clean_context()
        context["plan_configuration"][
            "product_scope_status"
        ] = "PRODUCT_FAMILY_OUT_OF_SCOPE"
        context["plan_configuration"][
            "product_scope_supported"
        ] = False
        scenarios.append(
            (
                "ELG-003 unsupported scope",
                context,
                "MANUAL_REVIEW",
                "ELG-003",
                1,
            )
        )

        context = make_clean_context()
        context["device_match"]["status"] = "DEVICE_MISMATCH"
        scenarios.append(
            (
                "DEV-002 device mismatch",
                context,
                "MANUAL_REVIEW",
                "DEV-002",
                1,
            )
        )

        context = make_clean_context()
        context["evidence"][
            "evidence_assessment_status"
        ] = "CONTRADICTORY"
        scenarios.append(
            (
                "EVD-002 contradictory evidence",
                context,
                "MANUAL_REVIEW",
                "EVD-002",
                1,
            )
        )

        context = make_clean_context()
        context["policy_eligibility"][
            "policy_incident_status"
        ] = "OUTSIDE_COVERAGE_PERIOD"
        scenarios.append(
            (
                "ELG-002 policy inactive",
                context,
                "NOT_ELIGIBLE",
                "ELG-002",
                2,
            )
        )

        context = make_clean_context()
        context["coverage"]["covered_flag"] = False
        scenarios.append(
            (
                "COV-001 explicitly uncovered",
                context,
                "NOT_ELIGIBLE",
                "COV-001",
                2,
            )
        )

        context = make_clean_context()
        context["claim_history"]["annual_claims_used"] = 1
        scenarios.append(
            (
                "LIM-001 annual limit exhausted",
                context,
                "NOT_ELIGIBLE",
                "LIM-001",
                2,
            )
        )

        context = make_clean_context()
        context["claim"]["claim_category_selected"] = "THEFT"
        context["plan_configuration"]["plan_configuration"][
            "plan_id"
        ] = "DP-PREMIUM"
        context["plan_configuration"]["plan_configuration"][
            "annual_claim_limit"
        ] = 2
        context["plan_configuration"]["plan_configuration"][
            "maximum_theft_claims"
        ] = 1
        context["claim_history"]["theft_claims_used"] = 1
        scenarios.append(
            (
                "LIM-002 theft limit exhausted",
                context,
                "NOT_ELIGIBLE",
                "LIM-002",
                2,
            )
        )

        context = make_clean_context()
        context["policy_eligibility"][
            "policy_incident_status"
        ] = "INCIDENT_DATE_MISSING_OR_INVALID"
        scenarios.append(
            (
                "ELG-001 missing incident date",
                context,
                "INFO_REQUIRED",
                "ELG-001",
                3,
            )
        )

        context = make_clean_context()
        context["claim"]["claim_category_selected"] = "UNSPECIFIED"
        scenarios.append(
            (
                "CLM-001 unspecified category",
                context,
                "INFO_REQUIRED",
                "CLM-001",
                3,
            )
        )

        context = make_clean_context()
        context["device_match"][
            "status"
        ] = "DEVICE_IDENTIFIER_MISSING"
        scenarios.append(
            (
                "DEV-001 missing device identifier",
                context,
                "INFO_REQUIRED",
                "DEV-001",
                3,
            )
        )

        context = make_clean_context()
        context["risk"] = {
            "has_triggered_risk": True,
            "recommended_action": "MANUAL_REVIEW",
            "risk_indicator_ids": ["RSK-001"],
            "manual_review_reasons": ["HIGH_COST_EXCEPTION"],
        }
        scenarios.append(
            (
                "ANM-001 risk trigger",
                context,
                "MANUAL_REVIEW",
                "ANM-001",
                4,
            )
        )

        context = make_clean_context()
        context["evidence"][
            "evidence_assessment_status"
        ] = "INCOMPLETE"
        context["evidence"][
            "missing_required_evidence_types"
        ] = ["DAMAGE_PHOTO"]
        scenarios.append(
            (
                "EVD-001 incomplete evidence",
                context,
                "INFO_REQUIRED",
                "EVD-001",
                5,
            )
        )

        for (
            scenario_name,
            context,
            expected_outcome,
            expected_rule,
            expected_stage,
        ) in scenarios:
            with self.subTest(scenario=scenario_name):
                self.assert_decision(
                    context=deepcopy(context),
                    expected_outcome=expected_outcome,
                    expected_rule=expected_rule,
                    expected_stage=expected_stage,
                )

    def test_precedence_rules(self):
        """Higher-precedence findings must win over later eligible findings."""

        context = make_clean_context()
        context["policy_lookup_status"] = "MULTIPLE_MATCH"
        context["coverage"]["covered_flag"] = False

        self.assert_decision(
            context=context,
            expected_outcome="MANUAL_REVIEW",
            expected_rule="DATA-002",
            expected_stage=1,
        )

        context = make_clean_context()
        context["evidence"][
            "evidence_assessment_status"
        ] = "CONTRADICTORY"
        context["coverage"]["covered_flag"] = False

        self.assert_decision(
            context=context,
            expected_outcome="MANUAL_REVIEW",
            expected_rule="EVD-002",
            expected_stage=1,
        )

        context = make_clean_context()
        context["policy_eligibility"][
            "policy_incident_status"
        ] = "OUTSIDE_COVERAGE_PERIOD"
        context["claim_history"]["annual_claims_used"] = 1

        self.assert_decision(
            context=context,
            expected_outcome="NOT_ELIGIBLE",
            expected_rule="ELG-002",
            expected_stage=2,
        )

        context = make_clean_context()
        context["coverage"]["covered_flag"] = False
        context["claim_history"]["annual_claims_used"] = 1

        self.assert_decision(
            context=context,
            expected_outcome="NOT_ELIGIBLE",
            expected_rule="COV-001",
            expected_stage=2,
        )

    def test_clean_claim_has_complete_trace(self):
        """A clean claim should complete all checks and reach OUT-001."""
        decision = self.assert_decision(
            context=make_clean_context(),
            expected_outcome="PROCEED",
            expected_rule="OUT-001",
            expected_stage=6,
        )

        self.assertEqual(len(decision["rule_trace"]), 17)
        self.assertEqual(
            decision["rule_trace"][0]["rule_id"],
            "DATA-001",
        )
        self.assertEqual(
            decision["rule_trace"][-1]["rule_id"],
            "OUT-001",
        )


if __name__ == "__main__":
    unittest.main()