from __future__ import annotations

import pandas as pd


EXPECTED_COLUMNS = {
    "plan_master": {
        "plan_id",
        "annual_claim_limit",
        "maximum_theft_claims",
    },
    "coverage_matrix": {
        "plan_id",
        "claim_category",
        "covered_flag",
        "evidence_profile_id",
    },
    "policy_lookup": {
        "customer_id",
        "policy_id",
        "plan_id",
        "covered_device_identifier",
        "coverage_start_date",
        "coverage_end_date",
    },
    "prior_claims": {
        "historical_claim_id",
        "policy_id",
        "claim_category",
        "claim_limit_consumed_flag",
        "theft_limit_consumed_flag",
    },
    "development_claims": {
        "claim_id",
        "policy_id_provided",
        "customer_id_provided",
        "claim_category_selected",
        "evidence_bundle_id",
        "customer_statement",
    },
}


def validate_required_columns(data: dict[str, pd.DataFrame]) -> list[str]:
    """
    Check that the core runtime datasets contain required columns.

    Returns a list of human-readable validation messages.
    Raises KeyError if a required dataset is missing.
    """
    results: list[str] = []

    for dataset_name, required_columns in EXPECTED_COLUMNS.items():
        if dataset_name not in data:
            raise KeyError(f"Required dataset missing: {dataset_name}")

        available_columns = set(data[dataset_name].columns)
        missing_columns = required_columns - available_columns

        if missing_columns:
            raise ValueError(
                f"{dataset_name} is missing required columns: "
                f"{sorted(missing_columns)}"
            )

        results.append(
            f"PASS - {dataset_name}: required columns available "
            f"({len(required_columns)} checked)"
        )

    return results


def validate_basic_record_counts(data: dict[str, pd.DataFrame]) -> list[str]:
    """
    Confirm that core datasets are not empty.
    """
    results: list[str] = []

    for dataset_name in EXPECTED_COLUMNS:
        row_count = len(data[dataset_name])

        if row_count == 0:
            raise ValueError(f"{dataset_name} contains zero rows")

        results.append(f"PASS - {dataset_name}: {row_count} rows")

    return results