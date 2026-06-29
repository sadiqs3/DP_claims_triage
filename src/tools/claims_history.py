from __future__ import annotations

import pandas as pd


def get_policy_claim_history(
    prior_claims: pd.DataFrame,
    policy_id: str,
    incident_date: str | None = None,
) -> pd.DataFrame:
    """
    Return historical claims for a policy.

    If incident_date is provided, only returns claims that occurred before
    the current incident date. This avoids using future information.
    """
    history = prior_claims[prior_claims["policy_id"] == policy_id].copy()

    if incident_date:
        current_date = pd.to_datetime(incident_date, errors="coerce")
        history["incident_date"] = pd.to_datetime(
            history["incident_date"],
            errors="coerce",
        )

        if pd.notna(current_date):
            history = history[history["incident_date"] < current_date].copy()

    return history


def calculate_claim_usage(history: pd.DataFrame) -> dict[str, int]:
    """
    Calculate consumed annual and theft claim allowances from historical claims.
    """
    annual_claims_used = int(
        history["claim_limit_consumed_flag"]
        .astype(str)
        .str.upper()
        .eq("TRUE")
        .sum()
    )

    theft_claims_used = int(
        history["theft_limit_consumed_flag"]
        .astype(str)
        .str.upper()
        .eq("TRUE")
        .sum()
    )

    return {
        "annual_claims_used": annual_claims_used,
        "theft_claims_used": theft_claims_used,
    }