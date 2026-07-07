import unittest

from src.data_loader import load_runtime_data
from src.tools.deterministic_triage import run_deterministic_triage
from src.tools.follow_up_selection import (
    run_controlled_follow_up_selection,
)


class TestControlledFollowUpSelection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = load_runtime_data()

    def test_info_required_claim_selects_catalogue_question(self):
        triage_result = run_deterministic_triage(
            data=self.data,
            claim_id="CLM-000117",
        )

        result = run_controlled_follow_up_selection(
            data=self.data,
            claim_id="CLM-000117",
            deterministic_tool_result=triage_result,
        )

        selection = result["follow_up_selection"]

        self.assertEqual(
            triage_result["deterministic_decision"]["triage_outcome"],
            "INFO_REQUIRED",
        )
        self.assertEqual(
            triage_result["deterministic_decision"]["triggering_rule_id"],
            "EVD-001",
        )
        self.assertTrue(selection["follow_up_required"])
        self.assertEqual(selection["question_ids"], ["FUP-009"])
        self.assertEqual(
            selection["selection_status"],
            "QUESTIONS_SELECTED",
        )
        self.assertEqual(
            result["decision_source"],
            "deterministic_triage:rules_baseline_v1",
        )

    def test_non_info_required_claim_returns_no_questions(self):
        triage_result = run_deterministic_triage(
            data=self.data,
            claim_id="CLM-000001",
        )

        result = run_controlled_follow_up_selection(
            data=self.data,
            claim_id="CLM-000001",
            deterministic_tool_result=triage_result,
        )

        selection = result["follow_up_selection"]

        self.assertEqual(
            triage_result["deterministic_decision"]["triage_outcome"],
            "PROCEED",
        )
        self.assertFalse(selection["follow_up_required"])
        self.assertEqual(selection["question_ids"], [])
        self.assertEqual(
            selection["selection_status"],
            "NOT_REQUIRED",
        )

    def test_claim_id_mismatch_raises_error(self):
        triage_result = run_deterministic_triage(
            data=self.data,
            claim_id="CLM-000117",
        )

        with self.assertRaisesRegex(
            ValueError,
            "claim_id does not match deterministic_decision claim_id",
        ):
            run_controlled_follow_up_selection(
                data=self.data,
                claim_id="CLM-000001",
                deterministic_tool_result=triage_result,
            )

    def test_missing_deterministic_decision_raises_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "must contain deterministic_decision",
        ):
            run_controlled_follow_up_selection(
                data=self.data,
                claim_id="CLM-000117",
                deterministic_tool_result={},
            )

    def test_missing_follow_up_catalogue_raises_error(self):
        triage_result = run_deterministic_triage(
            data=self.data,
            claim_id="CLM-000117",
        )

        incomplete_data = dict(self.data)
        incomplete_data.pop("follow_up_question_catalog")

        with self.assertRaisesRegex(
            ValueError,
            "Runtime data is missing follow_up_question_catalog",
        ):
            run_controlled_follow_up_selection(
                data=incomplete_data,
                claim_id="CLM-000117",
                deterministic_tool_result=triage_result,
            )


if __name__ == "__main__":
    unittest.main()