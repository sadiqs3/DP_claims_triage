from __future__ import annotations

import pandas as pd


def get_claim_risk_results(
    risk_results: pd.DataFrame,
    claim_id: str,
) -> pd.DataFrame:
    """
    Return any triggered risk indicators for a claim.

    Risk indicators are routing signals only. They do not establish fraud,
    fault, or final claim eligibility.
    """
    return risk_results[
        (risk_results["claim_id"] == claim_id)
        & (risk_results["risk_status"] == "TRIGGERED")
    ].copy()


def summarise_risk_results(risk_records: pd.DataFrame) -> dict[str, object]:
    """
    Convert risk records into structured routing facts.
    """
    if risk_records.empty:
        return {
            "has_triggered_risk": False,
            "risk_indicator_ids": [],
            "risk_indicator_names": [],
            "manual_review_reasons": [],
            "recommended_action": None,
        }

    return {
        "has_triggered_risk": True,
        "risk_indicator_ids": sorted(
            risk_records["risk_indicator_id"].dropna().unique().tolist()
        ),
        "risk_indicator_names": sorted(
            risk_records["risk_indicator_name"].dropna().unique().tolist()
        ),
        "manual_review_reasons": sorted(
            risk_records["manual_review_reason"].dropna().unique().tolist()
        ),
        "recommended_action": "MANUAL_REVIEW",
    }