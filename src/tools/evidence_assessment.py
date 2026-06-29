from __future__ import annotations

import pandas as pd


VALID_STATUS = "RECEIVED_VALID"
CONTRADICTORY_STATUS = "RECEIVED_CONTRADICTORY"
UNREADABLE_STATUS = "RECEIVED_UNREADABLE"

def assess_evidence(
    evidence_requirements: pd.DataFrame,
    evidence_documents: pd.DataFrame,
    evidence_profile_id: str | None,
) -> dict:
    """
    Assess submitted evidence against the applicable evidence profile.

    This function returns structured evidence facts only. It does not make
    the final claim-triage decision.
    """
    if not evidence_profile_id or pd.isna(evidence_profile_id):
        return {
            "evidence_profile_id": None,
            "required_evidence_types": [],
            "missing_required_evidence_types": [],
            "unreadable_required_evidence_types": [],
            "has_contradictory_evidence": False,
            "evidence_assessment_status": "NOT_APPLICABLE",
        }

    profile_requirements = evidence_requirements[
        evidence_requirements["evidence_profile_id"] == evidence_profile_id
    ].copy()

    required_types = profile_requirements.loc[
        profile_requirements["requirement_level"] == "REQUIRED",
        "evidence_type",
    ].tolist()

    submitted_types = set(evidence_documents["evidence_type"].dropna())

    missing_required = []
    unreadable_required = []

    for evidence_type in required_types:
        matching_docs = evidence_documents[
            evidence_documents["evidence_type"] == evidence_type
        ]

        if matching_docs.empty:
            missing_required.append(evidence_type)
            continue

        has_valid_document = (
            matching_docs["document_status"] == VALID_STATUS
        ).any()

        if (matching_docs["document_status"] == UNREADABLE_STATUS).any():
            unreadable_required.append(evidence_type)

    has_contradictory_evidence = (
        evidence_documents["document_status"] == CONTRADICTORY_STATUS
    ).any()

    if has_contradictory_evidence:
        assessment_status = "CONTRADICTORY"
    elif missing_required or unreadable_required:
        assessment_status = "INCOMPLETE"
    else:
        assessment_status = "SUFFICIENT"

    return {
        "evidence_profile_id": evidence_profile_id,
        "required_evidence_types": required_types,
        "submitted_evidence_types": sorted(submitted_types),
        "missing_required_evidence_types": missing_required,
        "unreadable_required_evidence_types": unreadable_required,
        "has_contradictory_evidence": bool(has_contradictory_evidence),
        "evidence_assessment_status": assessment_status,
    }