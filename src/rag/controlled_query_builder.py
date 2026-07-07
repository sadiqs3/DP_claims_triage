from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable
from hashlib import sha256


_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


def _validate_code(field_name: str, value: str) -> str:
    """Allow only deterministic, uppercase system codes."""
    if not isinstance(value, str) or not _CODE_PATTERN.fullmatch(value):
        raise ValueError(
            f"{field_name} must be an uppercase deterministic code, "
            f"for example: 'MISSING_REQUIRED' or 'MANUAL_REVIEW'."
        )
    return value


def _normalise_codes(field_name: str, values: Iterable[str]) -> tuple[str, ...]:
    """Validate, de-duplicate, and sort codes for deterministic handling."""
    validated = {_validate_code(field_name, value) for value in values}
    return tuple(sorted(validated))


@dataclass(frozen=True)
class AuthoritativeTriageFacts:
    """
    Retrieval-safe deterministic facts only.

    Do not add customer narrative, claim notes, identifiers,
    follow-up wording, or LLM-generated values here.
    """

    claim_type: str
    incident_category: str
    coverage_outcome: str
    evidence_state: str
    manual_review_required: bool

    product_family: str | None = None
    required_evidence_codes: tuple[str, ...] = ()
    manual_review_reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_code("claim_type", self.claim_type)
        _validate_code("incident_category", self.incident_category)
        _validate_code("coverage_outcome", self.coverage_outcome)
        _validate_code("evidence_state", self.evidence_state)

        if self.product_family is not None:
            _validate_code("product_family", self.product_family)

        object.__setattr__(
            self,
            "required_evidence_codes",
            _normalise_codes(
                "required_evidence_codes",
                self.required_evidence_codes,
            ),
        )

        object.__setattr__(
            self,
            "manual_review_reason_codes",
            _normalise_codes(
                "manual_review_reason_codes",
                self.manual_review_reason_codes,
            ),
        )

        if not self.manual_review_required and self.manual_review_reason_codes:
            raise ValueError(
                "manual_review_reason_codes must be empty when "
                "manual_review_required is False."
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
    """Create a deterministic, retrieval-friendly rendering of a system code."""
    return code.replace("_", " ").lower()


class ControlledRAGQueryBuilder:
    """
    Builds retrieval queries only from AuthoritativeTriageFacts.

    This class deliberately has no input for customer narrative, claim notes,
    customer identifiers, free-text extraction, or follow-up wording.
    """

    _RETRIEVAL_INTENT = (
        "Retrieve approved internal knowledge-base guidance for analyst "
        "evidence handling, documentation standards, manual-review procedures, "
        "and appropriate analyst next steps."
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
                f"Claim type: {facts.claim_type} "
                f"({_display_code(facts.claim_type)})."
            ),
            (
                f"Incident category: {facts.incident_category} "
                f"({_display_code(facts.incident_category)})."
            ),
            (
                f"Coverage outcome: {facts.coverage_outcome} "
                f"({_display_code(facts.coverage_outcome)})."
            ),
            (
                f"Evidence state: {facts.evidence_state} "
                f"({_display_code(facts.evidence_state)})."
            ),
        ]

        if facts.product_family:
            parts.append(
                f"Product family: {facts.product_family} "
                f"({_display_code(facts.product_family)})."
            )

        if facts.required_evidence_codes:
            rendered_evidence = ", ".join(
                f"{code} ({_display_code(code)})"
                for code in facts.required_evidence_codes
            )
            parts.append(f"Required evidence codes: {rendered_evidence}.")

        parts.append(
            "Manual review required: "
            f"{'YES' if facts.manual_review_required else 'NO'}."
        )

        if facts.manual_review_reason_codes:
            rendered_reasons = ", ".join(
                f"{code} ({_display_code(code)})"
                for code in facts.manual_review_reason_codes
            )
            parts.append(f"Manual-review reason codes: {rendered_reasons}.")

        parts.append(self._RETRIEVAL_INTENT)

        query_text = " ".join(parts)
        query_fingerprint = sha256(query_text.encode("utf-8")).hexdigest()

        return ControlledRAGQuery(
            query_text=query_text,
            query_fingerprint=query_fingerprint,
        )