import unittest

from src.rag.controlled_query_builder import (
    AuthoritativeTriageFacts,
    ControlledRAGQueryBuilder,
)


class TestControlledRAGQueryBuilder(unittest.TestCase):

    @staticmethod
    def _valid_facts(**overrides) -> AuthoritativeTriageFacts:
        values = {
            "claim_type": "ACCIDENTAL_DAMAGE",
            "incident_category": "SCREEN_DAMAGE",
            "coverage_outcome": "ELIGIBLE",
            "evidence_state": "MISSING_REQUIRED",
            "manual_review_required": True,
            "product_family": "SMARTPHONE",
            "required_evidence_codes": (
                "DAMAGE_PHOTOS",
                "PROOF_OF_PURCHASE",
            ),
            "manual_review_reason_codes": (
                "SERIAL_MISMATCH",
            ),
        }
        values.update(overrides)
        return AuthoritativeTriageFacts(**values)

    def test_normalises_code_collections_in_deterministic_order(self):
        facts = self._valid_facts(
            required_evidence_codes=(
                "PROOF_OF_PURCHASE",
                "DAMAGE_PHOTOS",
                "DAMAGE_PHOTOS",
            ),
            manual_review_reason_codes=(
                "UNSUPPORTED_SCENARIO",
                "SERIAL_MISMATCH",
                "SERIAL_MISMATCH",
            ),
        )

        self.assertEqual(
            facts.required_evidence_codes,
            (
                "DAMAGE_PHOTOS",
                "PROOF_OF_PURCHASE",
            ),
        )
        self.assertEqual(
            facts.manual_review_reason_codes,
            (
                "SERIAL_MISMATCH",
                "UNSUPPORTED_SCENARIO",
            ),
        )

    def test_rejects_free_text_in_deterministic_fact_fields(self):
        with self.assertRaisesRegex(ValueError, "incident_category"):
            self._valid_facts(
                incident_category=(
                    "Customer says the phone fell and the screen is cracked"
                )
            )

    def test_rejects_review_reasons_when_manual_review_is_not_required(self):
        with self.assertRaisesRegex(
            ValueError,
            "manual_review_reason_codes",
        ):
            self._valid_facts(
                manual_review_required=False,
                manual_review_reason_codes=("SERIAL_MISMATCH",),
            )

    def test_same_facts_produce_same_query_and_fingerprint_despite_input_order(
        self,
    ):
        facts_a = self._valid_facts(
            required_evidence_codes=(
                "DAMAGE_PHOTOS",
                "PROOF_OF_PURCHASE",
            ),
        )
        facts_b = self._valid_facts(
            required_evidence_codes=(
                "PROOF_OF_PURCHASE",
                "DAMAGE_PHOTOS",
            ),
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
                    "claim_type": "ACCIDENTAL_DAMAGE",
                    "customer_narrative": (
                        "My phone screen is badly cracked."
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()