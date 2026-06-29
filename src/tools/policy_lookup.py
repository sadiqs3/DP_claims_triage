from __future__ import annotations

import pandas as pd


def _has_value(value: object) -> bool:
    """Return True only when a lookup value is present and non-blank."""
    return pd.notna(value) and str(value).strip() != ""


def find_policy_records(
    policy_lookup: pd.DataFrame,
    policy_id: str | None = None,
    customer_id: str | None = None,
    device_identifier: str | None = None,
) -> pd.DataFrame:
    """
    Retrieve policy eligibility records using available identifiers.

    Lookup precedence:
    1. policy_id
    2. customer_id + device_identifier
    3. customer_id only

    Returns all matching records. The calling rules layer decides whether
    zero, one, or multiple matches require follow-up or manual review.
    """
    records = policy_lookup.copy()

    if _has_value(policy_id):
        return records[records["policy_id"] == policy_id].copy()

    if _has_value(customer_id) and _has_value(device_identifier):
        return records[
            (records["customer_id"] == customer_id)
            & (records["covered_device_identifier"] == device_identifier)
        ].copy()

    if _has_value(customer_id):
        return records[records["customer_id"] == customer_id].copy()

    return records.iloc[0:0].copy()

def classify_lookup_result(records: pd.DataFrame) -> str:
    """
    Classify the result of a policy lookup without making a final triage decision.
    """
    if records.empty:
        return "NO_MATCH"

    if len(records) == 1:
        return "UNIQUE_MATCH"

    return "MULTIPLE_MATCH"
