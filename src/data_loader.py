from pathlib import Path
import pandas as pd


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parents[1]


def load_runtime_data() -> dict[str, pd.DataFrame]:
    """
    Load the core runtime datasets required for the rules-only baseline.
    Returns a dictionary of named DataFrames.
    """
    root = get_project_root()
    reference_dir = root / "data" / "runtime" / "reference"
    claims_dir = root / "data" / "runtime" / "claims"

    return {
        "plan_master": pd.read_csv(
            reference_dir / "protection_plan_master_v1_1.csv"
        ),
        "coverage_matrix": pd.read_csv(
            reference_dir / "plan_coverage_matrix_v1.csv"
        ),
        "evidence_requirements": pd.read_csv(
            reference_dir / "evidence_profile_requirements_v1.csv"
        ),
        "policy_rules": pd.read_csv(
            reference_dir / "policy_rule_catalog_v1_2.csv"
        ),
        "policy_lookup": pd.read_csv(
            reference_dir / "policy_eligibility_lookup_v1_1.csv"
        ),
        "prior_claims": pd.read_csv(
            reference_dir / "prior_claims_history_v1_2.csv"
        ),
        "evidence_bundles": pd.read_csv(
            claims_dir / "evidence_bundle_manifest_v1.csv"
        ),
        "evidence_documents": pd.read_csv(
            claims_dir / "claim_evidence_document_metadata_v1.csv"
        ),
        "development_claims": pd.read_csv(
            claims_dir / "claims_intake_development_v1.csv"
        ),
       "risk_results": (
            pd.read_csv(claims_dir / "claim_risk_indicator_results_v1.csv")
            .query("dataset_partition == 'DEVELOPMENT'")
            .copy()
        ),
    }