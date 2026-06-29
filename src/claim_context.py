from __future__ import annotations

import pandas as pd

from src.tools.claims_history import (
    calculate_claim_usage,
    get_policy_claim_history,
)
from src.tools.coverage_lookup import (
    classify_coverage_result,
    get_coverage_record,
)
from src.tools.evidence_assessment import assess_evidence
from src.tools.evidence_lookup import get_evidence_documents
from src.tools.plan_configuration import assess_plan_configuration
from src.tools.policy_eligibility import assess_policy_for_incident
from src.tools.policy_lookup import (
    classify_lookup_result,
    find_policy_records,
)
from src.tools.risk_lookup import (
    get_claim_risk_results,
    summarise_risk_results,
)


def assemble_claim_context(
    data: dict[str, pd.DataFrame],
    claim_id: str,
) -> dict:
    """
    Assemble structured facts for one claim.

    This function does not make a final triage decision.
    """
    claims = data["development_claims"]

    claim_records = claims[claims["claim_id"] == claim_id].copy()

    if claim_records.empty:
        raise ValueError(f"Claim not found: {claim_id}")

    if len(claim_records) > 1:
        raise ValueError(
            f"Multiple intake records found for claim: {claim_id}"
        )

    claim = claim_records.iloc[0]
    reported_incident_date = claim["reported_incident_date"]

    # 1. Identify applicable policy record(s).
    policy_records = find_policy_records(
        policy_lookup=data["policy_lookup"],
        policy_id=claim["policy_id_provided"],
        customer_id=claim["customer_id_provided"],
        device_identifier=claim["claimed_device_identifier"],
    )

    policy_lookup_status = classify_lookup_result(policy_records)

    policy_record = None
    plan_id = None

    if policy_lookup_status == "UNIQUE_MATCH":
        policy_record = policy_records.iloc[0]
        plan_id = policy_record["plan_id"]

    # 2. Assess plan configuration and supported product scope.
    plan_configuration = assess_plan_configuration(
        plan_master=data["plan_master"],
        plan_id=plan_id,
        incident_date=reported_incident_date,
    )

    # 3. Assess policy eligibility as of the incident date.
    policy_eligibility = assess_policy_for_incident(
        policy_record=policy_record,
        incident_date=reported_incident_date,
    )

    # 4. Determine coverage and applicable evidence profile.
    coverage_record = get_coverage_record(
        coverage_matrix=data["coverage_matrix"],
        plan_id=plan_id,
        claim_category=claim["claim_category_selected"],
    )

    coverage_result = classify_coverage_result(coverage_record)
    evidence_profile_id = coverage_result["evidence_profile_id"]

    # 5. Get prior claim history only for a uniquely identified policy.
    history = data["prior_claims"].iloc[0:0].copy()

    claim_usage = {
        "annual_claims_used": 0,
        "theft_claims_used": 0,
    }

    if policy_record is not None:
        history = get_policy_claim_history(
            prior_claims=data["prior_claims"],
            policy_id=policy_record["policy_id"],
            incident_date=reported_incident_date,
        )
        claim_usage = calculate_claim_usage(history)

    # 6. Retrieve and assess submitted evidence.
    evidence_documents = get_evidence_documents(
        evidence_documents=data["evidence_documents"],
        evidence_bundle_id=claim["evidence_bundle_id"],
    )

    evidence_assessment = assess_evidence(
        evidence_requirements=data["evidence_requirements"],
        evidence_documents=evidence_documents,
        evidence_profile_id=evidence_profile_id,
    )

    # 7. Assess whether the claimed device matches the covered device.
    claimed_device_identifier = claim["claimed_device_identifier"]
    device_match_status = "NOT_ASSESSED"

    if policy_record is not None:
        if (
            pd.isna(claimed_device_identifier)
            or str(claimed_device_identifier).strip() == ""
        ):
            device_match_status = "DEVICE_IDENTIFIER_MISSING"

        elif (
            claimed_device_identifier
            != policy_record["covered_device_identifier"]
        ):
            device_match_status = "DEVICE_MISMATCH"

        else:
            device_match_status = "DEVICE_MATCH"

    # 8. Retrieve development-only risk-routing signals.
    risk_records = get_claim_risk_results(
        risk_results=data["risk_results"],
        claim_id=claim["claim_id"],
    )

    risk_assessment = summarise_risk_results(risk_records)

    return {
        "claim": {
            "claim_id": claim["claim_id"],
            "policy_id_provided": claim["policy_id_provided"],
            "customer_id_provided": claim["customer_id_provided"],
            "claimed_device_identifier": claim[
                "claimed_device_identifier"
            ],
            "reported_incident_date": reported_incident_date,
            "claim_category_selected": claim["claim_category_selected"],
            "requested_service_type": claim["requested_service_type"],
            "evidence_bundle_id": claim["evidence_bundle_id"],
        },
        "policy_lookup_status": policy_lookup_status,
        "policy": (
            policy_record.to_dict()
            if policy_record is not None
            else None
        ),
        "policy_eligibility": policy_eligibility,
        "plan_configuration": plan_configuration,
        "device_match": {
            "status": device_match_status,
            "claimed_device_identifier": claimed_device_identifier,
            "covered_device_identifier": (
                policy_record["covered_device_identifier"]
                if policy_record is not None
                else None
            ),
        },
        "coverage": coverage_result,
        "claim_history": {
            "historical_claim_count": len(history),
            **claim_usage,
        },
        "evidence": evidence_assessment,
        "risk": risk_assessment,
    }