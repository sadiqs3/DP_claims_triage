from __future__ import annotations

import pandas as pd


def assess_policy_for_incident(
    policy_record: pd.Series | None,
    incident_date: str | None,
) -> dict[str, object]:
    """
    Assess whether a uniquely matched policy was active on the incident date.

    The stored policy_status may reflect the later record snapshot date.
    Therefore, coverage dates are treated as authoritative for the claim event.
    """
    if policy_record is None:
        return {
            "policy_incident_status": "NOT_ASSESSED",
            "policy_active_for_incident": None,
            "reason": "No uniquely matched policy record.",
        }

    incident = pd.to_datetime(incident_date, errors="coerce")

    if pd.isna(incident):
        return {
            "policy_incident_status": "INCIDENT_DATE_MISSING_OR_INVALID",
            "policy_active_for_incident": None,
            "reason": "Incident date is required to assess policy eligibility.",
        }

    coverage_start = pd.to_datetime(
        policy_record.get("coverage_start_date"),
        errors="coerce",
    )
    coverage_end = pd.to_datetime(
        policy_record.get("coverage_end_date"),
        errors="coerce",
    )

    if pd.isna(coverage_start) or pd.isna(coverage_end):
        return {
            "policy_incident_status": "COVERAGE_DATES_UNAVAILABLE",
            "policy_active_for_incident": None,
            "reason": "Coverage start or end date is unavailable.",
        }

    if incident < coverage_start or incident > coverage_end:
        return {
            "policy_incident_status": "OUTSIDE_COVERAGE_PERIOD",
            "policy_active_for_incident": False,
            "reason": "Incident date falls outside the policy coverage period.",
        }

    suspension_start = pd.to_datetime(
        policy_record.get("suspension_start_date"),
        errors="coerce",
    )
    suspension_end = pd.to_datetime(
        policy_record.get("suspension_end_date"),
        errors="coerce",
    )

    if (
        pd.notna(suspension_start)
        and pd.notna(suspension_end)
        and suspension_start <= incident <= suspension_end
    ):
        return {
            "policy_incident_status": "SUSPENDED_ON_INCIDENT_DATE",
            "policy_active_for_incident": False,
            "reason": "Policy was suspended on the reported incident date.",
        }

    return {
        "policy_incident_status": "ACTIVE_ON_INCIDENT_DATE",
        "policy_active_for_incident": True,
        "reason": "Incident date falls within the active policy coverage period.",
    }