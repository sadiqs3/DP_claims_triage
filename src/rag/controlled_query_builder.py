from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import re


_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]{0,63}$")
_ALLOWED_TRIAGE_OUTCOMES = {
    "PROCEED",
    "INFO_REQUIRED",
    "MANUAL_REVIEW",
    "NOT_ELIGIBLE",
}


def _validate_code(field_name: str, value: str) -> str:
    """Allow only uppercase deterministic codes, including hyphenated IDs."""
    if not isinstance(value, str) or not _CODE_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must be an uppercase deterministic code using "
            "letters, numbers, underscores, or hyphens."
        )

    return value


def _validate_optional_code(
    field_name: str,
    value: str | None,
) -> str | None:
    """Allow an omitted retrieval fact or one validated deterministic code."""
    if value is None:
        return None

    return _validate_code(field_name, value)


def _normalise_codes(
    field_name: str,
    values: Iterable[str],
) -> tuple[str, ...]:
    """Validate, de-duplicate, and sort code collections deterministically."""
    if values is None or isinstance(values, (str, bytes)):
        raise ValueError(
            f"{field_name} must be an iterable of deterministic codes."
        )

    try:
        validated = {
            _validate_code(field_name, value)
            for value in values
        }
    except TypeError as exc:
        raise ValueError(
            f"{field_name} must be an iterable of deterministic codes."
        ) from exc

    return tuple(sorted(validated))


def _validate_optional_boolean(
    field_name: str,
    value: bool | None,
) -> bool | None:
    """Allow a deterministic boolean or an unassessed value."""
    if value is None:
        return None

    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be True, False, or None.")

    return value


@dataclass(frozen=True)
class AuthoritativeTriageFacts:
    """
    Retrieval-safe facts projected from deterministic claim context only.

    This contract must not contain identifiers, customer statements, document
    text, decision_reason, arbitrary rule-trace values, or LLM-generated text.
    """

    triage_outcome: str
    triggering_rule_id: str
    precedence_stage: int

    claim_category: str | None = None
    requested_service_type: str | None = None
    plan_configuration_status: str | None = None
    product_scope_status: str | None = None
    coverage_lookup_status: str | None = None
    covered_flag: bool | None = None
    evidence_profile_id: str | None = None
    evidence_assessment_status: str | None = None
    missing_required_evidence_codes: tuple[str, ...] = ()
    unreadable_required_evidence_codes: tuple[str, ...] = ()
    device_match_status: str | None = None
    risk_indicator_ids: tuple[str, ...] = ()
    manual_review_reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.triage_outcome not in _ALLOWED_TRIAGE_OUTCOMES:
            raise ValueError(
                "triage_outcome must be one of: "
                + ", ".join(sorted(_ALLOWED_TRIAGE_OUTCOMES))
                + "."
            )

        _validate_code("triggering_rule_id", self.triggering_rule_id)

        if (
            type(self.precedence_stage) is not int
            or not 1 <= self.precedence_stage <= 6
        ):
            raise ValueError(
                "precedence_stage must be an integer between 1 and 6."
            )

        optional_code_fields = (
            "claim_category",
            "requested_service_type",
            "plan_configuration_status",
            "product_scope_status",
            "coverage_lookup_status",
            "evidence_profile_id",
            "evidence_assessment_status",
            "device_match_status",
        )

        for field_name in optional_code_fields:
            object.__setattr__(
                self,
                field_name,
                _validate_optional_code(
                    field_name,
                    getattr(self, field_name),
                ),
            )

        object.__setattr__(
            self,
            "covered_flag",
            _validate_optional_boolean("covered_flag", self.covered_flag),
        )

        collection_fields = (
            "missing_required_evidence_codes",
            "unreadable_required_evidence_codes",
            "risk_indicator_ids",
            "manual_review_reason_codes",
        )

        for field_name in collection_fields:
            object.__setattr__(
                self,
                field_name,
                _normalise_codes(
                    field_name,
                    getattr(self, field_name),
                ),
            )


@dataclass(frozen=True)
class ControlledRAGQuery:
    """
    A retrieval request for analyst-facing, non-authoritative guidance.

    It must not be used to determine or change deterministic triage,
    eligibility, evidence requirements, or controlled customer follow-up.
    """

    query_text: str
    query_fingerprint: str
    source: str = "authoritative_deterministic_triage_facts"
    audience: str = "analyst"
    authority: str = "non_authoritative_guidance"


def _display_code(code: str) -> str:
    """Create a retrieval-friendly rendering while retaining the raw code."""
    return code.replace("_", " ").replace("-", " ").lower()


def _render_code(code: str) -> str:
    """Render one deterministic code with a stable human-readable form."""
    return f"{code} ({_display_code(code)})"


def _render_codes(codes: tuple[str, ...]) -> str:
    """Render an ordered deterministic code collection."""
    return ", ".join(_render_code(code) for code in codes)


class ControlledRAGQueryBuilder:
    """
    Build analyst-guidance retrieval queries from safe deterministic facts only.

    This class has no input for customer narrative, claim notes, identifiers,
    document text, decision reasons, arbitrary rule-trace values, or follow-up
    wording.
    """

    _RETRIEVAL_INTENT = (
        "Retrieve approved internal knowledge-base guidance for analyst "
        "evidence handling, documentation standards, manual-review procedures, "
        "and appropriate analyst next steps. Use this guidance only as "
        "non-authoritative decision support."
    )

    def build(self, facts: AuthoritativeTriageFacts) -> ControlledRAGQuery:
        """Build a stable, analyst-guidance retrieval query."""
        if not isinstance(facts, AuthoritativeTriageFacts):
            raise TypeError(
                "facts must be an AuthoritativeTriageFacts instance."
            )

        parts = [
            "Device protection claim analyst guidance.",
            (
                "Authoritative triage outcome: "
                f"{_render_code(facts.triage_outcome)}."
            ),
            (
                "Triggering deterministic rule: "
                f"{_render_code(facts.triggering_rule_id)}."
            ),
            f"Decision precedence stage: {facts.precedence_stage}.",
        ]

        optional_code_parts = (
            ("Claim category", facts.claim_category),
            ("Requested service type", facts.requested_service_type),
            ("Plan configuration status", facts.plan_configuration_status),
            ("Product scope status", facts.product_scope_status),
            ("Coverage lookup status", facts.coverage_lookup_status),
            ("Evidence profile ID", facts.evidence_profile_id),
            ("Evidence assessment status", facts.evidence_assessment_status),
            ("Device-match status", facts.device_match_status),
        )

        for label, code in optional_code_parts:
            if code is not None:
                parts.append(f"{label}: {_render_code(code)}.")

        if facts.covered_flag is not None:
            parts.append(
                "Coverage explicitly confirmed: "
                f"{'YES' if facts.covered_flag else 'NO'}."
            )

        if facts.missing_required_evidence_codes:
            parts.append(
                "Missing required evidence codes: "
                f"{_render_codes(facts.missing_required_evidence_codes)}."
            )

        if facts.unreadable_required_evidence_codes:
            parts.append(
                "Unreadable required evidence codes: "
                f"{_render_codes(facts.unreadable_required_evidence_codes)}."
            )

        if facts.risk_indicator_ids:
            parts.append(
                "Risk indicator IDs: "
                f"{_render_codes(facts.risk_indicator_ids)}."
            )

        if facts.manual_review_reason_codes:
            parts.append(
                "Manual-review reason codes: "
                f"{_render_codes(facts.manual_review_reason_codes)}."
            )

        parts.append(self._RETRIEVAL_INTENT)

        query_text = " ".join(parts)
        query_fingerprint = sha256(query_text.encode("utf-8")).hexdigest()

        return ControlledRAGQuery(
            query_text=query_text,
            query_fingerprint=query_fingerprint,
        )
