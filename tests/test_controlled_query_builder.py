import unittest

from src.rag.controlled_query_builder import (
    AuthoritativeTriageFacts,
    ControlledRAGQueryBuilder,
)


class TestControlledRAGQueryBuilder(unittest.TestCase):

    @staticmethod
    def _valid_facts(**overrides) -> AuthoritativeTriageFacts:
        values = {
            "triage_outcome": "MANUAL_REVIEW",
            "triggering_rule_id": "ANM-001",
            "precedence_stage": 4,
            "claim_category": "SCREEN_DAMAGE",
            "requested_service_type": "REPAIR",
            "plan_configuration_status": "ACTIVE_CONFIGURATION_AVAILABLE",
            "product_scope_status": "IN_SCOPE",
            "coverage_lookup_status": "UNIQUE_COVERAGE_RECORD",
            "covered_flag": True,
            "evidence_profile_id": "EVD-SCREEN-01",
            "evidence_assessment_status": "INCOMPLETE",
            "missing_required_evidence_codes": (
                "DAMAGE_PHOTO",
                "REPAIR_QUOTE",
            ),
            "unreadable_required_evidence_codes": (
                "DIAGNOSTIC_REPORT",
            ),
            "device_match_status": "DEVICE_MATCH",
            "risk_indicator_ids": ("RSK-001",),
            "manual_review_reason_codes": (
                "POTENTIAL_DUPLICATE",
            ),
        }
        values.update(overrides)
        return AuthoritativeTriageFacts(**values)

    def test_normalises_code_collections_and_allows_hyphenated_ids(self):
        facts = self._valid_facts(
            missing_required_evidence_codes=(
                "REPAIR_QUOTE",
                "DAMAGE_PHOTO",
                "DAMAGE_PHOTO",
            ),
            risk_indicator_ids=(
                "RSK-002",
                "RSK-001",
                "RSK-001",
            ),
            manual_review_reason_codes=(
                "POTENTIAL_DUPLICATE",
                "HIGH_COST_EXCEPTION",
                "HIGH_COST_EXCEPTION",
            ),
        )

        self.assertEqual(
            facts.missing_required_evidence_codes,
            (
                "DAMAGE_PHOTO",
                "REPAIR_QUOTE",
            ),
        )
        self.assertEqual(
            facts.risk_indicator_ids,
            (
                "RSK-001",
                "RSK-002",
            ),
        )
        self.assertEqual(
            facts.manual_review_reason_codes,
            (
                "HIGH_COST_EXCEPTION",
                "POTENTIAL_DUPLICATE",
            ),
        )
        self.assertEqual(facts.triggering_rule_id, "ANM-001")
        self.assertEqual(facts.evidence_profile_id, "EVD-SCREEN-01")

    def test_rejects_free_text_in_deterministic_fact_fields(self):
        with self.assertRaisesRegex(ValueError, "claim_category"):
            self._valid_facts(
                claim_category=(
                    "Customer says the phone fell and the screen is cracked"
                )
            )

    def test_rejects_invalid_precedence_stage(self):
        with self.assertRaisesRegex(ValueError, "precedence_stage"):
            self._valid_facts(precedence_stage=0)

    def test_rejects_non_boolean_coverage_flag(self):
        with self.assertRaisesRegex(ValueError, "covered_flag"):
            self._valid_facts(covered_flag="YES")

    def test_optional_facts_can_be_omitted_without_inventing_values(self):
        facts = self._valid_facts(
            claim_category=None,
            requested_service_type=None,
            plan_configuration_status=None,
            product_scope_status=None,
            coverage_lookup_status=None,
            covered_flag=None,
            evidence_profile_id=None,
            evidence_assessment_status=None,
            missing_required_evidence_codes=(),
            unreadable_required_evidence_codes=(),
            device_match_status=None,
            risk_indicator_ids=(),
            manual_review_reason_codes=(),
        )

        query = ControlledRAGQueryBuilder().build(facts)

        self.assertNotIn("Claim category:", query.query_text)
        self.assertNotIn("Coverage explicitly confirmed:", query.query_text)
        self.assertIn("Authoritative triage outcome:", query.query_text)

    def test_same_facts_produce_same_query_and_fingerprint_despite_input_order(
        self,
    ):
        facts_a = self._valid_facts(
            missing_required_evidence_codes=(
                "DAMAGE_PHOTO",
                "REPAIR_QUOTE",
            ),
            risk_indicator_ids=("RSK-001", "RSK-002"),
        )
        facts_b = self._valid_facts(
            missing_required_evidence_codes=(
                "REPAIR_QUOTE",
                "DAMAGE_PHOTO",
            ),
            risk_indicator_ids=("RSK-002", "RSK-001"),
        )

        builder = ControlledRAGQueryBuilder()

        query_a = builder.build(facts_a)
        query_b = builder.build(facts_b)

        self.assertEqual(query_a.query_text, query_b.query_text)
        self.assertEqual(
            query_a.query_fingerprint,
            query_b.query_fingerprint,
        )

    def test_query_is_explicitly_analyst_facing_and_non_authoritative(self):
        query = ControlledRAGQueryBuilder().build(self._valid_facts())

        self.assertEqual(
            query.source,
            "authoritative_deterministic_triage_facts",
        )
        self.assertEqual(query.audience, "analyst")
        self.assertEqual(
            query.authority,
            "non_authoritative_guidance",
        )
        self.assertIn(
            "Device protection claim analyst guidance.",
            query.query_text,
        )
        self.assertIn("ANM-001", query.query_text)
        self.assertIn("EVD-SCREEN-01", query.query_text)
        self.assertIn(
            "Retrieve approved internal knowledge-base guidance",
            query.query_text,
        )

    def test_builder_rejects_non_authoritative_input_type(self):
        builder = ControlledRAGQueryBuilder()

        with self.assertRaisesRegex(
            TypeError,
            "AuthoritativeTriageFacts",
        ):
            builder.build(
                {
                    "triage_outcome": "MANUAL_REVIEW",
                    "customer_statement": (
                        "My phone screen is badly cracked."
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
