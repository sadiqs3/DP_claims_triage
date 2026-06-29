from __future__ import annotations
import math

BASELINE_LIMITATIONS = [
    (
        "DEV-003 is not evaluated because the runtime context does not "
        "provide a verified NOT_ENROLLED device decision."
    ),
    (
        "EXC-001 and EXC-002 are not evaluated because no structured "
        "exclusion-status dataset is available."
    ),
    (
        "Claim-history source completeness cannot be independently "
        "verified from the current runtime package."
    ),
]

ACTIVE_PLAN_CONFIGURATION_STATUS = "ACTIVE_CONFIGURATION_AVAILABLE"
UNIQUE_COVERAGE_STATUS = "UNIQUE_COVERAGE_RECORD"


def _as_dict(value: object) -> dict:
    """Return a dictionary when available; otherwise return an empty dict."""
    return value if isinstance(value, dict) else {}


def _normalise_text(value: object) -> str | None:
    """Return uppercase trimmed text, or None for missing-like values."""
    if value is None:
        return None

    text = str(value).strip()

    if text == "" or text.upper() in {"NAN", "NONE", "<NA>"}:
        return None

    return text.upper()


def _is_missing_or_unspecified(value: object) -> bool:
    """Return True when a claim category is unavailable or not identified."""
    normalised_value = _normalise_text(value)

    return normalised_value is None or normalised_value == "UNSPECIFIED"


def _append_trace(
    trace: list[dict],
    rule_id: str,
    precedence_stage: int,
    observed_value: object,
    triggered: bool,
) -> None:
    """Append one auditable rule-evaluation record."""
    trace.append(
        {
            "rule_id": rule_id,
            "precedence_stage": precedence_stage,
            "evaluation": (
                "TRIGGERED" if triggered else "NOT_TRIGGERED"
            ),
            "observed_value": observed_value,
        }
    )


def _build_decision(
    context: dict,
    triage_outcome: str,
    triggering_rule_id: str,
    precedence_stage: int,
    decision_reason: str,
    rule_trace: list[dict],
) -> dict:
    """Create a standard, auditable decision-support response."""
    claim = _as_dict(context.get("claim"))

    return {
        "claim_id": claim.get("claim_id"),
        "triage_outcome": triage_outcome,
        "triggering_rule_id": triggering_rule_id,
        "precedence_stage": precedence_stage,
        "decision_reason": decision_reason,
        "rule_trace": rule_trace,
        "decision_support_only": True,
        "system_limitations": list(BASELINE_LIMITATIONS),
    }


def _get_data003_observation(
    policy_lookup_status: str | None,
    policy_incident_status: str | None,
    plan_configuration_status: str | None,
    claim_category: object,
    coverage_lookup_status: str | None,
) -> str | None:
    """
    Return a DATA-003 configuration issue description, if applicable.

    Missing incident date and missing claim category are deliberately excluded
    here because ELG-001 and CLM-001 handle them in the later missing-facts
    stage.
    """
    if policy_lookup_status != "UNIQUE_MATCH":
        return None

    if policy_incident_status in {
        "INCIDENT_DATE_MISSING_OR_INVALID",
        "COVERAGE_DATES_UNAVAILABLE",
    }:
        return None

    if plan_configuration_status != ACTIVE_PLAN_CONFIGURATION_STATUS:
        return (
            "Plan configuration status is "
            f"'{plan_configuration_status}'."
        )

    if (
        not _is_missing_or_unspecified(claim_category)
        and coverage_lookup_status != UNIQUE_COVERAGE_STATUS
    ):
        return (
            "Coverage lookup status is "
            f"'{coverage_lookup_status}' for an identified category."
        )

    return None


def evaluate_stage_one(
    context: dict,
    rule_trace: list[dict] | None = None,
) -> dict | None:
    """
    Evaluate Stage 1: data, configuration, ambiguity, and conflict rules.

    Returns a complete triage decision when a Stage 1 rule triggers.
    Returns None when the claim can continue to the next precedence stage.
    """
    claim = _as_dict(context.get("claim"))
    policy_eligibility = _as_dict(context.get("policy_eligibility"))
    plan_configuration = _as_dict(context.get("plan_configuration"))
    device_match = _as_dict(context.get("device_match"))
    coverage = _as_dict(context.get("coverage"))
    evidence = _as_dict(context.get("evidence"))

    policy_lookup_status = _normalise_text(
        context.get("policy_lookup_status")
    )
    policy_incident_status = _normalise_text(
        policy_eligibility.get("policy_incident_status")
    )
    plan_configuration_status = _normalise_text(
        plan_configuration.get("plan_configuration_status")
    )
    product_scope_status = _normalise_text(
        plan_configuration.get("product_scope_status")
    )
    device_match_status = _normalise_text(device_match.get("status"))
    coverage_lookup_status = _normalise_text(
        coverage.get("coverage_lookup_status")
    )
    evidence_assessment_status = _normalise_text(
        evidence.get("evidence_assessment_status")
    )
    claim_category = claim.get("claim_category_selected")

    if rule_trace is None:
        rule_trace = []

    # DATA-001: no policy can be identified.
    data001_triggered = policy_lookup_status == "NO_MATCH"

    _append_trace(
        rule_trace,
        rule_id="DATA-001",
        precedence_stage=1,
        observed_value=policy_lookup_status,
        triggered=data001_triggered,
    )

    if data001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="INFO_REQUIRED",
            triggering_rule_id="DATA-001",
            precedence_stage=1,
            decision_reason=(
                "No policy can be identified from the supplied "
                "customer, policy, or device details."
            ),
            rule_trace=rule_trace,
        )

    # DATA-002: multiple policy records are ambiguous.
    data002_triggered = policy_lookup_status == "MULTIPLE_MATCH"

    _append_trace(
        rule_trace,
        rule_id="DATA-002",
        precedence_stage=1,
        observed_value=policy_lookup_status,
        triggered=data002_triggered,
    )

    if data002_triggered:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="DATA-002",
            precedence_stage=1,
            decision_reason=(
                "Multiple candidate policy records were found. "
                "The system must not choose between them."
            ),
            rule_trace=rule_trace,
        )

    # ELG-002 unknown-data branch: policy dates cannot be assessed safely.
    coverage_dates_unavailable = (
        policy_incident_status == "COVERAGE_DATES_UNAVAILABLE"
    )

    _append_trace(
        rule_trace,
        rule_id="ELG-002",
        precedence_stage=1,
        observed_value=policy_incident_status,
        triggered=coverage_dates_unavailable,
    )

    if coverage_dates_unavailable:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="ELG-002",
            precedence_stage=1,
            decision_reason=(
                "Policy coverage dates are unavailable, so incident-date "
                "eligibility cannot be assessed safely."
            ),
            rule_trace=rule_trace,
        )

    # DATA-003: plan or coverage configuration is unavailable or unclear.
    data003_observation = _get_data003_observation(
        policy_lookup_status=policy_lookup_status,
        policy_incident_status=policy_incident_status,
        plan_configuration_status=plan_configuration_status,
        claim_category=claim_category,
        coverage_lookup_status=coverage_lookup_status,
    )

    data003_triggered = data003_observation is not None

    _append_trace(
        rule_trace,
        rule_id="DATA-003",
        precedence_stage=1,
        observed_value=(
            data003_observation
            if data003_triggered
            else {
                "plan_configuration_status": plan_configuration_status,
                "coverage_lookup_status": coverage_lookup_status,
            }
        ),
        triggered=data003_triggered,
    )

    if data003_triggered:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="DATA-003",
            precedence_stage=1,
            decision_reason=(
                "Plan or coverage configuration is unavailable, incomplete, "
                "or ambiguous. The system must not infer policy terms."
            ),
            rule_trace=rule_trace,
        )

    # ELG-003: product scope must be explicitly supported.
    elg003_triggered = (
        plan_configuration_status == ACTIVE_PLAN_CONFIGURATION_STATUS
        and product_scope_status != "IN_SCOPE"
    )

    _append_trace(
        rule_trace,
        rule_id="ELG-003",
        precedence_stage=1,
        observed_value=product_scope_status,
        triggered=elg003_triggered,
    )

    if elg003_triggered:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="ELG-003",
            precedence_stage=1,
            decision_reason=(
                "The selected plan configuration is outside, or unclear for, "
                "the supported DeviceProtect smartphone scope."
            ),
            rule_trace=rule_trace,
        )

    # DEV-002: device mismatch is an analyst-review issue, not a denial.
    dev002_triggered = device_match_status == "DEVICE_MISMATCH"

    _append_trace(
        rule_trace,
        rule_id="DEV-002",
        precedence_stage=1,
        observed_value=device_match_status,
        triggered=dev002_triggered,
    )

    if dev002_triggered:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="DEV-002",
            precedence_stage=1,
            decision_reason=(
                "The claimed device does not match the enrolled device and "
                "requires analyst validation."
            ),
            rule_trace=rule_trace,
        )

    # EVD-002: contradictory evidence requires human review.
    evd002_triggered = (
        evidence_assessment_status == "CONTRADICTORY"
    )

    _append_trace(
        rule_trace,
        rule_id="EVD-002",
        precedence_stage=1,
        observed_value=evidence_assessment_status,
        triggered=evd002_triggered,
    )

    if evd002_triggered:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="EVD-002",
            precedence_stage=1,
            decision_reason=(
                "Submitted evidence contains a contradiction and requires "
                "human review."
            ),
            rule_trace=rule_trace,
        )

    return None

def _to_non_negative_number(value: object) -> float | None:
    """Return a finite non-negative number, or None when unavailable."""
    if value is None:
        return None

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(numeric_value) or numeric_value < 0:
        return None

    return numeric_value


def evaluate_stage_two(
    context: dict,
    rule_trace: list[dict] | None = None,
) -> dict | None:
    """
    Evaluate Stage 2: verified hard eligibility failures.

    Returns a complete decision when a Stage 2 rule triggers.
    Returns None when the claim can continue to Stage 3.
    """
    if rule_trace is None:
        rule_trace = []

    claim = _as_dict(context.get("claim"))
    policy_eligibility = _as_dict(context.get("policy_eligibility"))
    plan_configuration = _as_dict(context.get("plan_configuration"))
    selected_plan = _as_dict(
        plan_configuration.get("plan_configuration")
    )
    coverage = _as_dict(context.get("coverage"))
    claim_history = _as_dict(context.get("claim_history"))

    policy_incident_status = _normalise_text(
        policy_eligibility.get("policy_incident_status")
    )
    plan_configuration_status = _normalise_text(
        plan_configuration.get("plan_configuration_status")
    )
    coverage_lookup_status = _normalise_text(
        coverage.get("coverage_lookup_status")
    )

    claim_category = _normalise_text(
        claim.get("claim_category_selected")
    )
    plan_id = _normalise_text(selected_plan.get("plan_id"))

    covered_flag = coverage.get("covered_flag")

    annual_claims_used = _to_non_negative_number(
        claim_history.get("annual_claims_used")
    )
    theft_claims_used = _to_non_negative_number(
        claim_history.get("theft_claims_used")
    )
    annual_claim_limit = _to_non_negative_number(
        selected_plan.get("annual_claim_limit")
    )
    maximum_theft_claims = _to_non_negative_number(
        selected_plan.get("maximum_theft_claims")
    )

    # ELG-002: verified policy inactivity on the incident date.
    verified_inactive_statuses = {
        "OUTSIDE_COVERAGE_PERIOD",
        "SUSPENDED_ON_INCIDENT_DATE",
    }

    elg002_triggered = (
        policy_incident_status in verified_inactive_statuses
    )

    _append_trace(
        rule_trace,
        rule_id="ELG-002",
        precedence_stage=2,
        observed_value=policy_incident_status,
        triggered=elg002_triggered,
    )

    if elg002_triggered:
        return _build_decision(
            context=context,
            triage_outcome="NOT_ELIGIBLE",
            triggering_rule_id="ELG-002",
            precedence_stage=2,
            decision_reason=(
                "The policy was not active on the reported incident date."
            ),
            rule_trace=rule_trace,
        )

    # COV-001: coverage must be explicitly confirmed as unavailable.
    cov001_triggered = (
        coverage_lookup_status == UNIQUE_COVERAGE_STATUS
        and covered_flag is False
    )

    _append_trace(
        rule_trace,
        rule_id="COV-001",
        precedence_stage=2,
        observed_value={
            "coverage_lookup_status": coverage_lookup_status,
            "covered_flag": covered_flag,
        },
        triggered=cov001_triggered,
    )

    if cov001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="NOT_ELIGIBLE",
            triggering_rule_id="COV-001",
            precedence_stage=2,
            decision_reason=(
                "The identified claim category is explicitly not covered "
                "by the enrolled plan."
            ),
            rule_trace=rule_trace,
        )

    # Limits are valid only after active policy, active configuration,
    # and explicit category coverage are confirmed.
    limit_checks_ready = (
        policy_incident_status == "ACTIVE_ON_INCIDENT_DATE"
        and plan_configuration_status
        == ACTIVE_PLAN_CONFIGURATION_STATUS
        and coverage_lookup_status == UNIQUE_COVERAGE_STATUS
        and covered_flag is True
    )

    # LIM-001: annual allowance exhausted.
    lim001_triggered = (
        limit_checks_ready
        and annual_claims_used is not None
        and annual_claim_limit is not None
        and annual_claims_used >= annual_claim_limit
    )

    _append_trace(
        rule_trace,
        rule_id="LIM-001",
        precedence_stage=2,
        observed_value={
            "limit_checks_ready": limit_checks_ready,
            "annual_claims_used": annual_claims_used,
            "annual_claim_limit": annual_claim_limit,
        },
        triggered=lim001_triggered,
    )

    if lim001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="NOT_ELIGIBLE",
            triggering_rule_id="LIM-001",
            precedence_stage=2,
            decision_reason=(
                "The plan's annual claim allowance is exhausted."
            ),
            rule_trace=rule_trace,
        )

    # LIM-002: applies only to covered theft under DP-PREMIUM.
    theft_limit_applicable = (
        limit_checks_ready
        and plan_id == "DP-PREMIUM"
        and claim_category == "THEFT"
    )

    lim002_triggered = (
        theft_limit_applicable
        and theft_claims_used is not None
        and maximum_theft_claims is not None
        and theft_claims_used >= maximum_theft_claims
    )

    _append_trace(
        rule_trace,
        rule_id="LIM-002",
        precedence_stage=2,
        observed_value={
            "theft_limit_applicable": theft_limit_applicable,
            "plan_id": plan_id,
            "claim_category": claim_category,
            "theft_claims_used": theft_claims_used,
            "maximum_theft_claims": maximum_theft_claims,
        },
        triggered=lim002_triggered,
    )

    if lim002_triggered:
        return _build_decision(
            context=context,
            triage_outcome="NOT_ELIGIBLE",
            triggering_rule_id="LIM-002",
            precedence_stage=2,
            decision_reason=(
                "The plan's theft claim allowance is exhausted."
            ),
            rule_trace=rule_trace,
        )

    return None

def evaluate_stage_three(
    context: dict,
    rule_trace: list[dict] | None = None,
) -> dict | None:
    """
    Evaluate Stage 3: missing core claim facts.

    Returns a complete decision when a Stage 3 rule triggers.
    Returns None when the claim can continue to Stage 4.
    """
    if rule_trace is None:
        rule_trace = []

    claim = _as_dict(context.get("claim"))
    policy_eligibility = _as_dict(context.get("policy_eligibility"))
    device_match = _as_dict(context.get("device_match"))

    policy_incident_status = _normalise_text(
        policy_eligibility.get("policy_incident_status")
    )
    claim_category = claim.get("claim_category_selected")
    device_match_status = _normalise_text(device_match.get("status"))

    # ELG-001: incident date is required for eligibility assessment.
    elg001_triggered = (
        policy_incident_status == "INCIDENT_DATE_MISSING_OR_INVALID"
    )

    _append_trace(
        rule_trace,
        rule_id="ELG-001",
        precedence_stage=3,
        observed_value=policy_incident_status,
        triggered=elg001_triggered,
    )

    if elg001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="INFO_REQUIRED",
            triggering_rule_id="ELG-001",
            precedence_stage=3,
            decision_reason=(
                "A valid incident date is required before incident-date "
                "eligibility can be assessed."
            ),
            rule_trace=rule_trace,
        )

    # CLM-001: claim category must be identifiable.
    clm001_triggered = _is_missing_or_unspecified(claim_category)

    _append_trace(
        rule_trace,
        rule_id="CLM-001",
        precedence_stage=3,
        observed_value=claim_category,
        triggered=clm001_triggered,
    )

    if clm001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="INFO_REQUIRED",
            triggering_rule_id="CLM-001",
            precedence_stage=3,
            decision_reason=(
                "The claim category is missing or unspecified. A category "
                "is required to determine coverage and evidence needs."
            ),
            rule_trace=rule_trace,
        )

    # DEV-001: device identifier must be provided.
    dev001_triggered = (
        device_match_status == "DEVICE_IDENTIFIER_MISSING"
    )

    _append_trace(
        rule_trace,
        rule_id="DEV-001",
        precedence_stage=3,
        observed_value=device_match_status,
        triggered=dev001_triggered,
    )

    if dev001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="INFO_REQUIRED",
            triggering_rule_id="DEV-001",
            precedence_stage=3,
            decision_reason=(
                "A usable device identifier, such as IMEI or serial number, "
                "is required before device-specific coverage can be assessed."
            ),
            rule_trace=rule_trace,
        )

    return None

def evaluate_stage_four(
    context: dict,
    rule_trace: list[dict] | None = None,
) -> dict | None:
    """
    Evaluate Stage 4: risk and anomaly routing.

    Returns a complete decision when a risk trigger is present.
    Returns None when the claim can continue to Stage 5.
    """
    if rule_trace is None:
        rule_trace = []

    risk = _as_dict(context.get("risk"))

    has_triggered_risk = risk.get("has_triggered_risk") is True

    observed_risk = {
        "has_triggered_risk": risk.get("has_triggered_risk"),
        "recommended_action": risk.get("recommended_action"),
        "risk_indicator_ids": risk.get("risk_indicator_ids"),
        "manual_review_reasons": risk.get("manual_review_reasons"),
    }

    _append_trace(
        rule_trace,
        rule_id="ANM-001",
        precedence_stage=4,
        observed_value=observed_risk,
        triggered=has_triggered_risk,
    )

    if has_triggered_risk:
        return _build_decision(
            context=context,
            triage_outcome="MANUAL_REVIEW",
            triggering_rule_id="ANM-001",
            precedence_stage=4,
            decision_reason=(
                "A material risk or anomaly signal requires analyst review. "
                "This is a routing decision only and does not establish "
                "fraud, customer fault, or claim denial."
            ),
            rule_trace=rule_trace,
        )

    return None

def evaluate_stage_five(
    context: dict,
    rule_trace: list[dict] | None = None,
) -> dict | None:
    """
    Evaluate Stage 5: required evidence gaps.

    Returns a complete decision when required evidence is incomplete.
    Returns None when the claim can continue to the final outcome gate.
    """
    if rule_trace is None:
        rule_trace = []

    evidence = _as_dict(context.get("evidence"))

    evidence_assessment_status = _normalise_text(
        evidence.get("evidence_assessment_status")
    )

    missing_required_evidence_types = evidence.get(
        "missing_required_evidence_types",
        [],
    )

    unreadable_required_evidence_types = evidence.get(
        "unreadable_required_evidence_types",
        [],
    )

    evd001_triggered = evidence_assessment_status == "INCOMPLETE"

    observed_evidence = {
        "evidence_assessment_status": evidence_assessment_status,
        "evidence_profile_id": evidence.get("evidence_profile_id"),
        "missing_required_evidence_types": (
            missing_required_evidence_types
        ),
        "unreadable_required_evidence_types": (
            unreadable_required_evidence_types
        ),
    }

    _append_trace(
        rule_trace,
        rule_id="EVD-001",
        precedence_stage=5,
        observed_value=observed_evidence,
        triggered=evd001_triggered,
    )

    if evd001_triggered:
        return _build_decision(
            context=context,
            triage_outcome="INFO_REQUIRED",
            triggering_rule_id="EVD-001",
            precedence_stage=5,
            decision_reason=(
                "Required evidence is missing or unreadable. Request only "
                "the specific evidence items identified in the rule trace."
            ),
            rule_trace=rule_trace,
        )

    return None

def triage_claim(context: dict) -> dict:
    """
    Apply the complete deterministic baseline triage sequence.

    The function returns one auditable decision-support recommendation.
    It does not approve payment, determine fraud, or issue a final denial.
    """
    rule_trace: list[dict] = []

    evaluators = [
        evaluate_stage_one,
        evaluate_stage_two,
        evaluate_stage_three,
        evaluate_stage_four,
        evaluate_stage_five,
    ]

    for evaluator in evaluators:
        decision = evaluator(
            context,
            rule_trace=rule_trace,
        )

        if decision is not None:
            return decision

    _append_trace(
        rule_trace,
        rule_id="OUT-001",
        precedence_stage=6,
        observed_value="No earlier applicable rule triggered.",
        triggered=True,
    )

    return _build_decision(
        context=context,
        triage_outcome="PROCEED",
        triggering_rule_id="OUT-001",
        precedence_stage=6,
        decision_reason=(
            "All applicable deterministic checks passed. Eligible for "
            "standard processing only; this is not an approval, payout, "
            "fraud determination, or final denial decision."
        ),
        rule_trace=rule_trace,
    )