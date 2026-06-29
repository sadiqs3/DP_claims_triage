from __future__ import annotations

import pandas as pd


def _has_value(value: object) -> bool:
    """Return True only when a value is present and non-blank."""
    return pd.notna(value) and str(value).strip() != ""


def get_evidence_bundle(
    evidence_bundles: pd.DataFrame,
    evidence_bundle_id: str | None,
) -> pd.DataFrame:
    """
    Retrieve the evidence-bundle record for a provided bundle ID.

    Returns zero or one row in the current dataset design.
    """
    if not _has_value(evidence_bundle_id):
        return evidence_bundles.iloc[0:0].copy()

    return evidence_bundles[
        evidence_bundles["evidence_bundle_id"] == evidence_bundle_id
    ].copy()


def get_evidence_documents(
    evidence_documents: pd.DataFrame,
    evidence_bundle_id: str | None = None,
    claim_id: str | None = None,
) -> pd.DataFrame:
    """
    Retrieve evidence-document metadata.

    Lookup precedence:
    1. evidence_bundle_id
    2. claim_id

    Returns all matching document records.
    """
    if _has_value(evidence_bundle_id):
        return evidence_documents[
            evidence_documents["evidence_bundle_id"] == evidence_bundle_id
        ].copy()

    if _has_value(claim_id):
        return evidence_documents[
            evidence_documents["claim_id"] == claim_id
        ].copy()

    return evidence_documents.iloc[0:0].copy()