from __future__ import annotations

import pandas as pd


EXPECTED_PRODUCT_FAMILY = "DEVICEPROTECT"
EXPECTED_DEVICE_CATEGORY = "SMARTPHONE"


def _has_value(value: object) -> bool:
    """Return True only when a value is present and non-blank."""
    return pd.notna(value) and str(value).strip() != ""


def _normalise_text(value: object) -> str | None:
    """Return uppercase trimmed text, or None when the value is unavailable."""
    if not _has_value(value):
        return None

    return str(value).strip().upper()


def _to_python_value(value: object) -> object:
    """Convert pandas/numpy scalar values to ordinary Python values."""
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def _empty_result(
    plan_configuration_status: str,
    reason: str,
) -> dict[str, object]:
    """Return a standard response when no usable configuration is available."""
    return {
        "plan_configuration_status": plan_configuration_status,
        "plan_configuration_available": None,
        "product_scope_status": "NOT_ASSESSED",
        "product_scope_supported": None,
        "plan_configuration": None,
        "reason": reason,
    }


def _serialise_configuration(record: pd.Series) -> dict[str, object]:
    """Return only configuration fields needed by later rules and audit output."""
    fields = [
        "plan_id",
        "plan_version",
        "plan_name",
        "product_family",
        "covered_device_category",
        "annual_claim_limit",
        "maximum_theft_claims",
        "plan_status",
        "effective_start_date",
        "effective_end_date",
    ]

    return {
        field: _to_python_value(record.get(field))
        for field in fields
    }


def _assess_product_scope(record: pd.Series) -> tuple[str, bool | None]:
    """Assess whether the selected configuration is in project product scope."""
    product_family = _normalise_text(record.get("product_family"))
    device_category = _normalise_text(record.get("covered_device_category"))

    if product_family is None or device_category is None:
        return "SCOPE_FIELDS_UNAVAILABLE", None

    product_family_in_scope = product_family == EXPECTED_PRODUCT_FAMILY
    device_category_in_scope = device_category == EXPECTED_DEVICE_CATEGORY

    if product_family_in_scope and device_category_in_scope:
        return "IN_SCOPE", True

    if not product_family_in_scope and not device_category_in_scope:
        return "PRODUCT_AND_DEVICE_CATEGORY_OUT_OF_SCOPE", False

    if not product_family_in_scope:
        return "PRODUCT_FAMILY_OUT_OF_SCOPE", False

    return "DEVICE_CATEGORY_OUT_OF_SCOPE", False


def assess_plan_configuration(
    plan_master: pd.DataFrame,
    plan_id: str | None,
    incident_date: str | None,
) -> dict[str, object]:
    """
    Assess the plan configuration applicable to a claim incident.

    The function identifies one active configuration effective on the incident
    date and separately assesses DeviceProtect smartphone product scope.

    This function returns facts only. It does not make a final triage decision.
    """
    required_columns = {
        "plan_id",
        "annual_claim_limit",
        "maximum_theft_claims",
        "plan_status",
        "effective_start_date",
        "effective_end_date",
        "product_family",
        "covered_device_category",
    }

    missing_columns = required_columns.difference(plan_master.columns)

    if missing_columns:
        return _empty_result(
            plan_configuration_status="CONFIGURATION_COLUMNS_MISSING",
            reason=(
                "Plan master is missing required columns: "
                + ", ".join(sorted(missing_columns))
            ),
        )

    normalised_plan_id = _normalise_text(plan_id)

    if normalised_plan_id is None:
        return _empty_result(
            plan_configuration_status="NOT_ASSESSED",
            reason="A uniquely matched policy plan ID is required.",
        )

    incident = pd.to_datetime(incident_date, errors="coerce")

    if pd.isna(incident):
        return _empty_result(
            plan_configuration_status="INCIDENT_DATE_MISSING_OR_INVALID",
            reason=(
                "Incident date is required to identify the applicable "
                "plan configuration."
            ),
        )

    configurations = plan_master[
        plan_master["plan_id"].map(_normalise_text) == normalised_plan_id
    ].copy()

    if configurations.empty:
        return _empty_result(
            plan_configuration_status="NO_CONFIGURATION_RECORD",
            reason="No plan configuration was found for the matched plan ID.",
        )

    configurations["_effective_start"] = pd.to_datetime(
        configurations["effective_start_date"],
        errors="coerce",
    )

    configurations["_effective_end"] = pd.to_datetime(
        configurations["effective_end_date"],
        errors="coerce",
    )

    if (
        configurations["_effective_start"].isna().any()
        or configurations["_effective_end"].isna().any()
    ):
        return _empty_result(
            plan_configuration_status="CONFIGURATION_DATES_INVALID",
            reason=(
                "One or more plan configuration records have missing "
                "or invalid effective dates."
            ),
        )

    effective_configurations = configurations[
        (configurations["_effective_start"] <= incident)
        & (incident <= configurations["_effective_end"])
    ].copy()

    if effective_configurations.empty:
        return _empty_result(
            plan_configuration_status="NO_EFFECTIVE_CONFIGURATION",
            reason=(
                "No plan configuration is effective on the reported "
                "incident date."
            ),
        )

    if len(effective_configurations) > 1:
        return _empty_result(
            plan_configuration_status="MULTIPLE_EFFECTIVE_CONFIGURATIONS",
            reason=(
                "More than one plan configuration is effective on the "
                "reported incident date."
            ),
        )

    configuration = effective_configurations.iloc[0]

    annual_claim_limit = pd.to_numeric(
        configuration["annual_claim_limit"],
        errors="coerce",
    )

    maximum_theft_claims = pd.to_numeric(
        configuration["maximum_theft_claims"],
        errors="coerce",
    )

    if (
        pd.isna(annual_claim_limit)
        or pd.isna(maximum_theft_claims)
        or annual_claim_limit < 0
        or maximum_theft_claims < 0
    ):
        return {
            "plan_configuration_status": "CONFIGURATION_INCOMPLETE",
            "plan_configuration_available": False,
            "product_scope_status": "NOT_ASSESSED",
            "product_scope_supported": None,
            "plan_configuration": _serialise_configuration(configuration),
            "reason": (
                "Annual claim limit or theft claim limit is missing, "
                "invalid, or negative."
            ),
        }

    plan_status = _normalise_text(configuration["plan_status"])

    if plan_status != "ACTIVE":
        return {
            "plan_configuration_status": "INACTIVE_CONFIGURATION",
            "plan_configuration_available": False,
            "product_scope_status": "NOT_ASSESSED",
            "product_scope_supported": None,
            "plan_configuration": _serialise_configuration(configuration),
            "reason": (
                "The plan configuration effective on the incident date "
                "is not active."
            ),
        }

    product_scope_status, product_scope_supported = _assess_product_scope(
        configuration
    )

    return {
        "plan_configuration_status": "ACTIVE_CONFIGURATION_AVAILABLE",
        "plan_configuration_available": True,
        "product_scope_status": product_scope_status,
        "product_scope_supported": product_scope_supported,
        "plan_configuration": _serialise_configuration(configuration),
        "reason": (
            "One active plan configuration is effective on the incident date."
        ),
    }