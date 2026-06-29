import unittest

import pandas as pd

from src.tools.plan_configuration import assess_plan_configuration


class TestPlanConfiguration(unittest.TestCase):
    """Unit tests for deterministic plan-configuration assessment."""

    def setUp(self) -> None:
        self.plan_master = pd.DataFrame(
            [
                {
                    "plan_id": "DP-ESSENTIAL",
                    "plan_version": 1.1,
                    "plan_name": "DeviceProtect Essential",
                    "product_family": "DeviceProtect",
                    "covered_device_category": "SMARTPHONE",
                    "annual_claim_limit": 1,
                    "maximum_theft_claims": 0,
                    "plan_status": "ACTIVE",
                    "effective_start_date": "2024-01-01",
                    "effective_end_date": "2027-12-31",
                }
            ]
        )

    def test_active_in_scope_configuration_is_available(self) -> None:
        result = assess_plan_configuration(
            plan_master=self.plan_master,
            plan_id="DP-ESSENTIAL",
            incident_date="2025-07-14",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "ACTIVE_CONFIGURATION_AVAILABLE",
        )
        self.assertTrue(result["plan_configuration_available"])
        self.assertEqual(result["product_scope_status"], "IN_SCOPE")
        self.assertTrue(result["product_scope_supported"])
        self.assertEqual(
            result["plan_configuration"]["annual_claim_limit"],
            1,
        )

    def test_missing_plan_id_is_not_assessed(self) -> None:
        result = assess_plan_configuration(
            plan_master=self.plan_master,
            plan_id=None,
            incident_date="2025-07-14",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "NOT_ASSESSED",
        )
        self.assertIsNone(result["plan_configuration_available"])

    def test_invalid_incident_date_is_not_assessed(self) -> None:
        result = assess_plan_configuration(
            plan_master=self.plan_master,
            plan_id="DP-ESSENTIAL",
            incident_date="not-a-date",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "INCIDENT_DATE_MISSING_OR_INVALID",
        )
        self.assertIsNone(result["plan_configuration_available"])

    def test_date_outside_effective_period_has_no_configuration(self) -> None:
        result = assess_plan_configuration(
            plan_master=self.plan_master,
            plan_id="DP-ESSENTIAL",
            incident_date="2023-12-31",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "NO_EFFECTIVE_CONFIGURATION",
        )
        self.assertIsNone(result["plan_configuration_available"])

    def test_overlapping_configurations_are_not_selected(self) -> None:
        overlapping_record = self.plan_master.copy()

        overlapping_record.loc[0, "plan_version"] = 2.0
        overlapping_record.loc[
            0,
            "plan_name",
        ] = "DeviceProtect Essential Test Version"
        overlapping_record.loc[
            0,
            "effective_start_date",
        ] = "2025-01-01"
        overlapping_record.loc[
            0,
            "effective_end_date",
        ] = "2026-12-31"

        plan_master_with_overlap = pd.concat(
            [self.plan_master, overlapping_record],
            ignore_index=True,
        )

        result = assess_plan_configuration(
            plan_master=plan_master_with_overlap,
            plan_id="DP-ESSENTIAL",
            incident_date="2025-07-14",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "MULTIPLE_EFFECTIVE_CONFIGURATIONS",
        )
        self.assertIsNone(result["plan_configuration_available"])

    def test_unsupported_product_family_is_out_of_scope(self) -> None:
        out_of_scope_plan_master = self.plan_master.copy()

        out_of_scope_plan_master.loc[
            0,
            "product_family",
        ] = "OtherProtect"

        result = assess_plan_configuration(
            plan_master=out_of_scope_plan_master,
            plan_id="DP-ESSENTIAL",
            incident_date="2025-07-14",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "ACTIVE_CONFIGURATION_AVAILABLE",
        )
        self.assertEqual(
            result["product_scope_status"],
            "PRODUCT_FAMILY_OUT_OF_SCOPE",
        )
        self.assertFalse(result["product_scope_supported"])

    def test_inactive_configuration_is_not_available(self) -> None:
        inactive_plan_master = self.plan_master.copy()

        inactive_plan_master.loc[0, "plan_status"] = "INACTIVE"

        result = assess_plan_configuration(
            plan_master=inactive_plan_master,
            plan_id="DP-ESSENTIAL",
            incident_date="2025-07-14",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "INACTIVE_CONFIGURATION",
        )
        self.assertFalse(result["plan_configuration_available"])
        self.assertEqual(result["product_scope_status"], "NOT_ASSESSED")

    def test_missing_claim_limit_makes_configuration_incomplete(self) -> None:
        incomplete_plan_master = self.plan_master.copy()

        incomplete_plan_master.loc[
            0,
            "annual_claim_limit",
        ] = None

        result = assess_plan_configuration(
            plan_master=incomplete_plan_master,
            plan_id="DP-ESSENTIAL",
            incident_date="2025-07-14",
        )

        self.assertEqual(
            result["plan_configuration_status"],
            "CONFIGURATION_INCOMPLETE",
        )
        self.assertFalse(result["plan_configuration_available"])
        self.assertEqual(result["product_scope_status"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()