from __future__ import annotations

import pandas as pd


def _has_value(value: object) -> bool:
    """Return True only when a value is present and non-blank."""
    return pd.notna(value) and str(value).strip() != ""


def get_coverage_record(
    coverage_matrix: pd.DataFrame,
    plan_id: str | None,
    claim_category: str | None,
) -> pd.DataFrame:
    """
    Return the coverage record for a plan and claim category.

    Returns zero or one row in the current matrix design.
    """
    if not _has_value(plan_id) or not _has_value(claim_category):
        return coverage_matrix.iloc[0:0].copy()

    return coverage_matrix[
        (coverage_matrix["plan_id"] == plan_id)
        & (coverage_matrix["claim_category"] == claim_category)
    ].copy()


def classify_coverage_result(coverage_record: pd.DataFrame) -> dict[str, object]:
    """
    Convert a coverage lookup into structured facts.

    This function does not make an overall triage decision.
    """
    if coverage_record.empty:
        return {
            "coverage_lookup_status": "NO_COVERAGE_RECORD",
            "covered_flag": None,
            "evidence_profile_id": None,
        }

    if len(coverage_record) > 1:
        return {
            "coverage_lookup_status": "MULTIPLE_COVERAGE_RECORDS",
            "covered_flag": None,
            "evidence_profile_id": None,
        }

    record = coverage_record.iloc[0]

    return {
        "coverage_lookup_status": "UNIQUE_COVERAGE_RECORD",
        "covered_flag": bool(record["covered_flag"]),
        "evidence_profile_id": (
            record["evidence_profile_id"]
            if pd.notna(record["evidence_profile_id"])
            else None
            ),
    }