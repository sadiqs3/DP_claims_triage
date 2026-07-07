from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

import pandas as pd


TOOL_NAME = "select_follow_up_questions"
TOOL_VERSION = "v1"

MAX_QUESTIONS_PER_INTERACTION = 3

INFO_REQUIRED_RULE_IDS = {
    "DATA-001",
    "ELG-001",
    "DEV-001",
    "CLM-001",
    "EVD-001",
}

REQUIRED_CATALOG_COLUMNS = {
    "question_id",
    "question_name",
    "trigger_type",
    "source_rule_id",
    "decision_stage",
    "applicable_claim_categories",
    "evidence_profile_id",
    "response_field",
    "response_format",
    "question_priority",
    "customer_facing_question",
    "plain_language_reason",
    "agent_handling_after_response",
    "max_repeats",
    "active_flag",
}

STAGE_PRIORITY = {
    "ELIGIBILITY_FACTS": 1,
    "REQUIRED_EVIDENCE": 2,
}


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dictionary."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _normalise_text(value: object) -> str | None:
    """Return stripped text or None for missing-like values."""
    if value is None:
        return None

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text or text.casefold() in {"nan", "none", "<na>"}:
        return None

    return text


def _normalise_upper(value: object) -> str | None:
    """Return normalised uppercase text or None."""
    text = _normalise_text(value)
    return text.upper() if text else None


def _validate_catalog(question_catalog: pd.DataFrame) -> None:
    """Validate that required catalogue fields are available."""
    missing_columns = sorted(
        REQUIRED_CATALOG_COLUMNS - set(question_catalog.columns)
    )

    if missing_columns:
        raise ValueError(
            "follow_up_question_catalog is missing required columns: "
            + ", ".join(missing_columns)
        )


def _is_active_question(value: object) -> bool:
    """Return True only for active catalogue entries."""
    return _normalise_text(value) in {"Yes", "YES", "True", "TRUE", "1"}


def _matches_claim_category(
    catalogue_category: object,
    claim_category: object,
) -> bool:
    """Check catalogue category applicability."""
    catalogue_value = _normalise_upper(catalogue_category)
    claim_value = _normalise_upper(claim_category)

    return catalogue_value == "ALL" or (
        catalogue_value is not None
        and claim_value is not None
        and catalogue_value == claim_value
    )


def _matches_evidence_profile(
    catalogue_profile: object,
    evidence_profile: object,
) -> bool:
    """Check evidence-profile applicability for evidence questions."""
    catalogue_value = _normalise_upper(catalogue_profile)
    evidence_value = _normalise_upper(evidence_profile)

    return (
        catalogue_value is not None
        and evidence_value is not None
        and catalogue_value == evidence_value
    )


def _normalise_question_history(
    questions_already_asked: Sequence[str] | str | None,
) -> Counter[str]:
    """Convert question history into a question-ID counter."""
    if questions_already_asked is None:
        return Counter()

    if isinstance(questions_already_asked, str):
        raw_values = [questions_already_asked]
    else:
        raw_values = questions_already_asked

    question_ids = [
        question_id
        for value in raw_values
        if (question_id := _normalise_text(value)) is not None
    ]

    return Counter(question_ids)


def _get_evidence_condition_types(
    evidence: Mapping[str, Any],
) -> dict[str, set[str]]:
    """Map evidence conditions to required catalogue trigger types."""
    evidence_data = _as_dict(evidence)

    missing_types = {
        evidence_type
        for value in evidence_data.get(
            "missing_required_evidence_types",
            [],
        )
        if (evidence_type := _normalise_upper(value)) is not None
    }

    unreadable_types = {
        evidence_type
        for value in evidence_data.get(
            "unreadable_required_evidence_types",
            [],
        )
        if (evidence_type := _normalise_upper(value)) is not None
    }

    return {
        "MISSING_REQUIRED_EVIDENCE": missing_types,
        "UNREADABLE_OR_INVALID_EVIDENCE": unreadable_types,
    }


def _candidate_rows_for_decision(
    context: Mapping[str, Any],
    deterministic_decision: Mapping[str, Any],
    question_catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Return active catalogue rows applicable to the current decision."""
    decision = _as_dict(deterministic_decision)
    claim = _as_dict(_as_dict(context).get("claim"))
    evidence = _as_dict(_as_dict(context).get("evidence"))

    triggering_rule_id = _normalise_text(
        decision.get("triggering_rule_id")
    )
    claim_category = claim.get("claim_category_selected")
    evidence_profile_id = evidence.get("evidence_profile_id")

    active_catalogue = question_catalog[
        question_catalog["active_flag"].apply(_is_active_question)
    ].copy()

    rule_candidates = active_catalogue[
        active_catalogue["source_rule_id"].astype(str)
        == str(triggering_rule_id)
    ].copy()

    if rule_candidates.empty:
        return rule_candidates

    selected_rows: list[dict[str, Any]] = []

    if triggering_rule_id == "EVD-001":
        evidence_conditions = _get_evidence_condition_types(evidence)

        for _, row in rule_candidates.iterrows():
            row_data = row.to_dict()

            if not _matches_claim_category(
                row_data["applicable_claim_categories"],
                claim_category,
            ):
                continue

            if not _matches_evidence_profile(
                row_data["evidence_profile_id"],
                evidence_profile_id,
            ):
                continue

            trigger_type = _normalise_upper(
                row_data["trigger_type"]
            )
            response_field = _normalise_upper(
                row_data["response_field"]
            )

            valid_response_fields = evidence_conditions.get(
                trigger_type,
                set(),
            )

            if response_field in valid_response_fields:
                selected_rows.append(row_data)

    else:
        for _, row in rule_candidates.iterrows():
            row_data = row.to_dict()

            if _matches_claim_category(
                row_data["applicable_claim_categories"],
                claim_category,
            ):
                selected_rows.append(row_data)

    if not selected_rows:
        return rule_candidates.iloc[0:0].copy()

    candidate_rows = pd.DataFrame(selected_rows)

    candidate_rows["_stage_priority"] = (
        candidate_rows["decision_stage"]
        .map(STAGE_PRIORITY)
        .fillna(99)
    )

    candidate_rows["_question_priority"] = pd.to_numeric(
        candidate_rows["question_priority"],
        errors="coerce",
    ).fillna(999)

    return candidate_rows.sort_values(
        by=[
            "_stage_priority",
            "_question_priority",
            "question_id",
        ]
    ).reset_index(drop=True)


def _build_selected_question(row: Mapping[str, Any]) -> dict[str, Any]:
    """Create the public selected-question payload."""
    return {
        "question_id": _normalise_text(row.get("question_id")),
        "question_name": _normalise_text(row.get("question_name")),
        "source_rule_id": _normalise_text(row.get("source_rule_id")),
        "decision_stage": _normalise_text(row.get("decision_stage")),
        "response_field": _normalise_text(row.get("response_field")),
        "response_format": _normalise_text(row.get("response_format")),
        "customer_facing_question": _normalise_text(
            row.get("customer_facing_question")
        ),
        "plain_language_reason": _normalise_text(
            row.get("plain_language_reason")
        ),
        "agent_handling_after_response": _normalise_text(
            row.get("agent_handling_after_response")
        ),
    }


def _build_customer_message(
    selected_questions: Sequence[Mapping[str, Any]],
) -> str:
    """Build a neutral message using approved catalogue wording only."""
    if not selected_questions:
        return ""

    acknowledgement = "Thanks for submitting your claim."

    if len(selected_questions) == 1:
        question = selected_questions[0]

        return " ".join(
            [
                acknowledgement,
                question["customer_facing_question"],
                question["plain_language_reason"],
                (
                    "Once we receive the requested information, "
                    "the claim assessment can continue."
                ),
            ]
        )

    question_lines = [
        f"{index}. {question['customer_facing_question']}"
        for index, question in enumerate(selected_questions, start=1)
    ]

    reason_lines = [
        f"{index}. {question['plain_language_reason']}"
        for index, question in enumerate(selected_questions, start=1)
    ]

    return "\n".join(
        [
            acknowledgement,
            "Please provide the following information:",
            *question_lines,
            "Why this is needed:",
            *reason_lines,
            (
                "Once we receive the requested information, "
                "the claim assessment can continue."
            ),
        ]
    )


def _empty_selection_result(
    claim_id: str | None,
    selection_status: str,
    selection_notes: list[str],
    deferred_requirements: list[str] | None = None,
) -> dict[str, Any]:
    """Return a no-question selection response."""
    return {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "claim_id": claim_id,
        "follow_up_required": False,
        "selection_status": selection_status,
        "question_ids": [],
        "selected_questions": [],
        "customer_message": "",
        "deferred_requirements": deferred_requirements or [],
        "selection_notes": selection_notes,
    }


def select_follow_up_questions(
    context: Mapping[str, Any],
    deterministic_decision: Mapping[str, Any],
    question_catalog: pd.DataFrame,
    questions_already_asked: Sequence[str] | str | None = None,
) -> dict[str, Any]:
    """
    Select approved, rule-grounded follow-up questions.

    The function never changes deterministic triage routing. It selects
    questions only when the authoritative outcome is INFO_REQUIRED.
    """
    _validate_catalog(question_catalog)

    context_data = _as_dict(context)
    claim = _as_dict(context_data.get("claim"))
    decision = _as_dict(deterministic_decision)

    claim_id = _normalise_text(
        decision.get("claim_id") or claim.get("claim_id")
    )
    triage_outcome = _normalise_text(
        decision.get("triage_outcome")
    )
    triggering_rule_id = _normalise_text(
        decision.get("triggering_rule_id")
    )

    if triage_outcome != "INFO_REQUIRED":
        return _empty_selection_result(
            claim_id=claim_id,
            selection_status="NOT_REQUIRED",
            selection_notes=[
                (
                    "FSEL-001/FSEL-002: No customer follow-up selected "
                    f"because deterministic outcome is {triage_outcome}."
                )
            ],
        )

    if triggering_rule_id not in INFO_REQUIRED_RULE_IDS:
        return _empty_selection_result(
            claim_id=claim_id,
            selection_status="NO_SUPPORTED_RULE_MAPPING",
            selection_notes=[
                (
                    "No question was generated because the INFO_REQUIRED "
                    "rule is not supported by the approved catalogue."
                ),
                (
                    "Route the missing catalogue mapping for authorised "
                    "analyst review."
                ),
            ],
            deferred_requirements=[
                (
                    "No approved follow-up question is mapped to rule "
                    f"{triggering_rule_id}."
                )
            ],
        )

    candidate_rows = _candidate_rows_for_decision(
        context=context_data,
        deterministic_decision=decision,
        question_catalog=question_catalog,
    )

    if candidate_rows.empty:
        return _empty_selection_result(
            claim_id=claim_id,
            selection_status="NO_ACTIVE_CATALOGUE_MATCH",
            selection_notes=[
                (
                    "No approved active catalogue question matched the "
                    "current rule, category, evidence profile, or evidence "
                    "condition."
                ),
                (
                    "No question was invented. Route this gap for "
                    "authorised analyst review."
                ),
            ],
            deferred_requirements=[
                (
                    "An approved follow-up question could not be selected "
                    f"for rule {triggering_rule_id}."
                )
            ],
        )

    question_history = _normalise_question_history(
        questions_already_asked
    )

    previously_requested_fields = {
        _normalise_upper(response_field)
        for question_id, _ in question_history.items()
        for response_field in question_catalog.loc[
            question_catalog["question_id"].astype(str) == question_id,
            "response_field",
        ].tolist()
        if _normalise_upper(response_field) is not None
    }

    selected_questions: list[dict[str, Any]] = []
    selected_response_fields: set[str] = set()
    deferred_requirements: list[str] = []

    for _, row in candidate_rows.iterrows():
        row_data = row.to_dict()

        question_id = _normalise_text(row_data["question_id"])
        response_field = _normalise_upper(
            row_data["response_field"]
        )

        max_repeats = pd.to_numeric(
            pd.Series([row_data["max_repeats"]]),
            errors="coerce",
        ).fillna(1).iloc[0]

        max_repeats = int(max_repeats)

        if question_history[question_id] >= max_repeats:
            deferred_requirements.append(
                f"{question_id} was already asked the permitted number of times."
            )
            continue

        if response_field in previously_requested_fields:
            deferred_requirements.append(
                (
                    f"Response field {response_field} was already requested "
                    "in a prior interaction."
                )
            )
            continue

        if response_field in selected_response_fields:
            deferred_requirements.append(
                (
                    f"Response field {response_field} is already covered by "
                    "another selected question."
                )
            )
            continue

        selected_questions.append(
            _build_selected_question(row_data)
        )

        selected_response_fields.add(response_field)

        if len(selected_questions) >= MAX_QUESTIONS_PER_INTERACTION:
            break

    if not selected_questions:
        return _empty_selection_result(
            claim_id=claim_id,
            selection_status="NO_NEW_QUESTIONS_AVAILABLE",
            selection_notes=[
                (
                    "FSEL-005: No new question selected because matching "
                    "questions or response fields were already requested."
                ),
                (
                    "Do not repeat the request. Route the unresolved case "
                    "for authorised analyst review."
                ),
            ],
            deferred_requirements=deferred_requirements,
        )

    return {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "claim_id": claim_id,
        "follow_up_required": True,
        "selection_status": "QUESTIONS_SELECTED",
        "question_ids": [
            question["question_id"]
            for question in selected_questions
        ],
        "selected_questions": selected_questions,
        "customer_message": _build_customer_message(
            selected_questions
        ),
        "deferred_requirements": deferred_requirements,
        "selection_notes": [
            (
                "FSEL-002: Questions selected only because deterministic "
                f"outcome is INFO_REQUIRED under rule {triggering_rule_id}."
            ),
            (
                "FSEL-003: Eligibility-fact questions are prioritised before "
                "required-evidence questions."
            ),
            (
                "FSEL-004: At most three questions may be selected per "
                "interaction."
            ),
            (
                "FSEL-005: Previously requested questions and response "
                "fields are not repeated."
            ),
            (
                "FSEL-007: Customer message uses approved catalogue wording "
                "and neutral communication."
            ),
        ],
    }