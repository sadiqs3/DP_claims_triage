from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from src.rag.controlled_query_builder import AuthoritativeTriageFacts


PROJECTION_NAME = "authoritative_rag_facts_projection"
PROJECTION_VERSION = "v1"


def _require_mapping(
    parent: Mapping[str, Any],
    field_name: str,
    parent_name: str,
) -> Mapping[str, Any]:
    """Return one required structured section from deterministic context."""
    value = parent.get(field_name)

    if not isinstance(value, Mapping):
        raise ValueError(
            f"{parent_name}.{field_name} must be a mapping."
        )

    return value


def _require_decision(
    deterministic_decision: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Validate the deterministic decision fields used for retrieval facts."""
    if not isinstance(deterministic_decision, Mapping):
        raise ValueError(
            "deterministic_decision must be a mapping."
        )

    required_fields = (
        "triage_outcome",
        "triggering_rule_id",
        "precedence_stage",
        "decision_support_only",
    )

    missing_fields = [
        field_name
        for field_name in required_fields
        if field_name not in deterministic_decision
    ]

    if missing_fields:
        raise ValueError(
            "deterministic_decision is missing required fields: "
            + ", ".join(missing_fields)
        )

    if deterministic_decision["decision_support_only"] is not True:
        raise ValueError(
            "deterministic_decision must be decision-support-only."
        )

    return deterministic_decision


def _as_code_tuple(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    """Return a code collection without accepting scalar text."""
    if value is None:
        return ()

    if isinstance(value, (str, bytes)):
        raise ValueError(
            f"{field_name} must be a collection of deterministic codes."
        )

    if not isinstance(value, Iterable):
        raise ValueError(
            f"{field_name} must be a collection of deterministic codes."
        )

    return tuple(value)


def project_authoritative_rag_facts(
    context: Mapping[str, Any],
    deterministic_decision: Mapping[str, Any],
) -> AuthoritativeTriageFacts:
    """
    Project allow-listed structured deterministic facts for RAG retrieval.

    This function deliberately excludes claim/customer/policy/device
    identifiers, customer statements, document text, decision reasons,
    arbitrary rule-trace values, risk names, and nested plan details.
    """
    if not isinstance(context, Mapping):
        raise ValueError("context must be a mapping.")

    decision = _require_decision(deterministic_decision)

    claim = _require_mapping(context, "claim", "context")
    plan_configuration = _require_mapping(
        context,
        "plan_configuration",
        "context",
    )
    coverage = _require_mapping(context, "coverage", "context")
    evidence = _require_mapping(context, "evidence", "context")
    device_match = _require_mapping(
        context,
        "device_match",
        "context",
    )
    risk = _require_mapping(context, "risk", "context")

    return AuthoritativeTriageFacts(
        triage_outcome=decision["triage_outcome"],
        triggering_rule_id=decision["triggering_rule_id"],
        precedence_stage=decision["precedence_stage"],
        claim_category=claim.get("claim_category_selected"),
        requested_service_type=claim.get("requested_service_type"),
        plan_configuration_status=plan_configuration.get(
            "plan_configuration_status"
        ),
        product_scope_status=plan_configuration.get(
            "product_scope_status"
        ),
        coverage_lookup_status=coverage.get(
            "coverage_lookup_status"
        ),
        covered_flag=coverage.get("covered_flag"),
        evidence_profile_id=evidence.get("evidence_profile_id"),
        evidence_assessment_status=evidence.get(
            "evidence_assessment_status"
        ),
        missing_required_evidence_codes=_as_code_tuple(
            evidence.get("missing_required_evidence_types", []),
            "evidence.missing_required_evidence_types",
        ),
        unreadable_required_evidence_codes=_as_code_tuple(
            evidence.get("unreadable_required_evidence_types", []),
            "evidence.unreadable_required_evidence_types",
        ),
        device_match_status=device_match.get("status"),
        risk_indicator_ids=_as_code_tuple(
            risk.get("risk_indicator_ids", []),
            "risk.risk_indicator_ids",
        ),
        manual_review_reason_codes=_as_code_tuple(
            risk.get("manual_review_reasons", []),
            "risk.manual_review_reasons",
        ),
    )