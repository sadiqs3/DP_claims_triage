import copy
import unittest

from src.claim_context import assemble_claim_context
from src.data_loader import load_runtime_data
from src.tools.follow_up_questions import (
    select_follow_up_questions,
)
from src.triage_engine import triage_claim


class TestFollowUpQuestionSelection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_runtime_data()
        cls.catalog = cls.data["follow_up_question_catalog"]

    def _select_for_claim(
        self,
        claim_id: str,
        questions_already_asked=None,
    ):
        context = assemble_claim_context(
            data=self.data,
            claim_id=claim_id,
        )

        decision = triage_claim(context)

        result = select_follow_up_questions(
            context=context,
            deterministic_decision=decision,
            question_catalog=self.catalog,
            questions_already_asked=questions_already_asked,
        )

        return decision, result

    def test_missing_incident_date_selects_fup_002(self):
        decision, result = self._select_for_claim("CLM-000071")

        self.assertEqual(
            decision["triage_outcome"],
            "INFO_REQUIRED",
        )
        self.assertEqual(
            decision["triggering_rule_id"],
            "ELG-001",
        )
        self.assertTrue(result["follow_up_required"])
        self.assertEqual(
            result["question_ids"],
            ["FUP-002"],
        )
        self.assertEqual(
            result["selection_status"],
            "QUESTIONS_SELECTED",
        )

    def test_missing_device_identifier_selects_fup_003(self):
        decision, result = self._select_for_claim("CLM-000098")

        self.assertEqual(
            decision["triggering_rule_id"],
            "DEV-001",
        )
        self.assertEqual(
            result["question_ids"],
            ["FUP-003"],
        )

    def test_missing_and_unreadable_evidence_select_correct_questions(self):
        _, missing_result = self._select_for_claim("CLM-000117")
        _, unreadable_result = self._select_for_claim("CLM-000125")

        self.assertEqual(
            missing_result["question_ids"],
            ["FUP-009"],
        )
        self.assertEqual(
            unreadable_result["question_ids"],
            ["FUP-008"],
        )

    def test_non_info_required_outcome_selects_no_questions(self):
        decision, result = self._select_for_claim("CLM-000001")

        self.assertEqual(
            decision["triage_outcome"],
            "PROCEED",
        )
        self.assertFalse(result["follow_up_required"])
        self.assertEqual(result["question_ids"], [])
        self.assertEqual(
            result["selection_status"],
            "NOT_REQUIRED",
        )

    def test_duplicate_question_is_not_repeated(self):
        _, result = self._select_for_claim(
            claim_id="CLM-000071",
            questions_already_asked=["FUP-002"],
        )

        self.assertFalse(result["follow_up_required"])
        self.assertEqual(result["question_ids"], [])
        self.assertEqual(
            result["selection_status"],
            "NO_NEW_QUESTIONS_AVAILABLE",
        )

    def test_data_001_uses_catalogue_question_without_inventing_text(self):
        synthetic_context = {
            "claim": {
                "claim_id": "CLM-TEST-DATA-001",
                "claim_category_selected": "SCREEN_DAMAGE",
            },
            "evidence": {},
        }

        synthetic_decision = {
            "claim_id": "CLM-TEST-DATA-001",
            "triage_outcome": "INFO_REQUIRED",
            "triggering_rule_id": "DATA-001",
        }

        result = select_follow_up_questions(
            context=synthetic_context,
            deterministic_decision=synthetic_decision,
            question_catalog=self.catalog,
        )

        expected_question = self.catalog.loc[
            self.catalog["question_id"] == "FUP-001"
        ].iloc[0]

        self.assertTrue(result["follow_up_required"])
        self.assertEqual(result["question_ids"], ["FUP-001"])
        self.assertEqual(
            result["selected_questions"][0]["customer_facing_question"],
            expected_question["customer_facing_question"],
        )

    def test_missing_catalogue_mapping_returns_no_invented_question(self):
        inactive_catalog = copy.deepcopy(self.catalog)

        inactive_catalog.loc[
            inactive_catalog["question_id"] == "FUP-009",
            "active_flag",
        ] = "No"

        context = assemble_claim_context(
            data=self.data,
            claim_id="CLM-000117",
        )
        decision = triage_claim(context)

        result = select_follow_up_questions(
            context=context,
            deterministic_decision=decision,
            question_catalog=inactive_catalog,
        )

        self.assertFalse(result["follow_up_required"])
        self.assertEqual(result["question_ids"], [])
        self.assertEqual(
            result["selection_status"],
            "NO_ACTIVE_CATALOGUE_MATCH",
        )
        self.assertIn(
            "No question was invented.",
            " ".join(result["selection_notes"]),
        )


if __name__ == "__main__":
    unittest.main()