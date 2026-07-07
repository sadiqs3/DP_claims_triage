from __future__ import annotations

from copy import deepcopy
import unittest

from src.rag.controlled_query_builder import ControlledRAGQueryBuilder
from src.rag.triage_facts_projection import (
    PROJECTION_NAME,
    PROJECTION_VERSION,
    project_authoritative_rag_facts,
)


class TestAuthoritativeRAGFactsProjection(unittest.TestCase):
    """Tests the boundary from deterministic context to retrieval-safe facts."""

    @staticmethod
    def _valid_context() -> dict:
        return {
            "claim": {
                "claim_id": "CLM-TEST-001",
                "customer_id_provided": "CUS-TEST-001",
                "policy_id_provided": "POL-TEST-001",
                "claimed_device_identifier": "DVC-TEST-001",
                "customer_statement": (
                    "My phone fell in the rain and the screen is cracked."
                ),
                "claim_category_selected": "SCREEN_DAMAGE",
                "requested_service_type": "REPAIR",
            },
            "plan_configuration": {
                "plan_configuration_status": (
                    "ACTIVE_CONFIGURATION_AVAILABLE"
                ),
                "product_scope_status": "IN_SCOPE",
                "plan_configuration": {
                    "plan_id": "DP-ESSENTIAL",
                    "plan_description": "Do not expose this nested detail.",
                },
            },
            "coverage": {
                "coverage_lookup_status": "UNIQUE_COVERAGE_RECORD",
                "covered_flag": True,
                "evidence_profile_id": "EVD-SCREEN-01",
                "coverage_notes": "Do not expose this text.",
            },
            "evidence": {
                "evidence_profile_id": "EVD-SCREEN-01",
                "evidence_assessment_status": "INCOMPLETE",
                "missing_required_evidence_types": [
                    "REPAIR_QUOTE",
                    "DAMAGE_PHOTO",
                ],
                "unreadable_required_evidence_types": [
                    "DIAGNOSTIC_REPORT",
                ],
                "document_summary": "Do not expose this document text.",
            },
            "device_match": {
                "status": "DEVICE_MATCH",
                "claimed_device_identifier": "DVC-TEST-001",
                "covered_device_identifier": "DVC-TEST-001",
            },
            "risk": {
                "risk_indicator_ids": [
                    "RSK-002",
                    "RSK-001",
                ],
                "manual_review_reasons": [
                    "POTENTIAL_DUPLICATE",
                    "HIGH_COST_EXCEPTION",
                ],
                "risk_indicator_names": [
                    "RECENT_RELATED_CLAIM_PATTERN",
                    "HIGH_REPAIR_COST",
                ],
            },
        }

    @staticmethod
    def _valid_decision() -> dict:
        return {
            "claim_id": "CLM-TEST-001",
            "triage_outcome": "MANUAL_REVIEW",
            "triggering_rule_id": "ANM-001",
            "precedence_stage": 4,
            "decision_reason": (
                "A material risk signal requires analyst review."
            ),
            "rule_trace": [
                {
                    "rule_id": "ANM-001",
                    "observed_value": (
                        "Do not expose arbitrary rule-trace text."
                    ),
                }
            ],
            "decision_support_only": True,
        }

    def test_projects_allow_list_facts_from_structured_context(self):
        facts = project_authoritative_rag_facts(
            context=self._valid_context(),
            deterministic_decision=self._valid_decision(),
        )

        self.assertEqual(facts.triage_outcome, "MANUAL_REVIEW")
        self.assertEqual(facts.triggering_rule_id, "ANM-001")
        self.assertEqual(facts.precedence_stage, 4)
        self.assertEqual(facts.claim_category, "SCREEN_DAMAGE")
        self.assertEqual(facts.requested_service_type, "REPAIR")
        self.assertEqual(
            facts.plan_configuration_status,
            "ACTIVE_CONFIGURATION_AVAILABLE",
        )
        self.assertTrue(facts.covered_flag)
        self.assertEqual(
            facts.evidence_profile_id,
            "EVD-SCREEN-01",
        )
        self.assertEqual(
            facts.missing_required_evidence_codes,
            ("DAMAGE_PHOTO", "REPAIR_QUOTE"),
        )
        self.assertEqual(
            facts.risk_indicator_ids,
            ("RSK-001", "RSK-002"),
        )
        self.assertEqual(
            facts.manual_review_reason_codes,
            ("HIGH_COST_EXCEPTION", "POTENTIAL_DUPLICATE"),
        )

    def test_projection_never_carries_identifiers_or_free_text(self):
        facts = project_authoritative_rag_facts(
            context=self._valid_context(),
            deterministic_decision=self._valid_decision(),
        )

        query = ControlledRAGQueryBuilder().build(facts)

        prohibited_fragments = (
            "CLM-TEST-001",
            "CUS-TEST-001",
            "POL-TEST-001",
            "DVC-TEST-001",
            "fell in the rain",
            "Do not expose this document text",
            "Do not expose arbitrary rule-trace text",
            "Do not expose this nested detail",
            "RECENT_RELATED_CLAIM_PATTERN",
            "HIGH_REPAIR_COST",
        )

        for fragment in prohibited_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, query.query_text)

    def test_requires_decision_support_only_true(self):
        decision = self._valid_decision()
        decision["decision_support_only"] = False

        with self.assertRaisesRegex(
            ValueError,
            "decision-support-only",
        ):
            project_authoritative_rag_facts(
                context=self._valid_context(),
                deterministic_decision=decision,
            )

    def test_rejects_missing_required_context_section(self):
        context = self._valid_context()
        context.pop("evidence")

        with self.assertRaisesRegex(
            ValueError,
            "context.evidence must be a mapping",
        ):
            project_authoritative_rag_facts(
                context=context,
                deterministic_decision=self._valid_decision(),
            )

    def test_rejects_scalar_risk_code_input(self):
        context = self._valid_context()
        context["risk"]["risk_indicator_ids"] = "RSK-001"

        with self.assertRaisesRegex(
            ValueError,
            "risk.risk_indicator_ids",
        ):
            project_authoritative_rag_facts(
                context=context,
                deterministic_decision=self._valid_decision(),
            )

    def test_projection_metadata_is_stable(self):
        self.assertEqual(
            PROJECTION_NAME,
            "authoritative_rag_facts_projection",
        )
        self.assertEqual(PROJECTION_VERSION, "v1")


if __name__ == "__main__":
    unittest.main()