# Item #7 — Claim Evidence and Document Metadata (v1)

## Purpose
This package supplies evidence metadata for the Item #6 claim-intake cases. It simulates document availability and extractable facts without introducing actual files, images, OCR, or sensitive customer information.

## Scope decision
This MVP uses controlled metadata and short synthetic document summaries rather than real photos, PDFs, OCR, or multimodal models. This is deliberate: the capstone demonstrates agentic retrieval, evidence-gap detection, contradiction handling, and traceable triage without creating unnecessary document-processing scope.

## Files
- `data/reference/evidence_profile_requirements_v1.csv` — authoritative requirement profiles for supported covered categories.
- `data/reference/evidence_type_catalog_v1.csv` — definitions of evidence types.
- `data/claims/evidence_bundle_manifest_v1.csv` — one evidence bundle per Item #6 claim.
- `data/claims/claim_evidence_document_metadata_v1.csv` — document-level metadata and controlled summaries.

## Evidence logic
1. Resolve the policy and claim category using Items #2–#6.
2. Determine the applicable evidence profile from the coverage matrix.
3. Retrieve the evidence bundle using `evidence_bundle_id`.
4. For every REQUIRED evidence type, confirm at least one `RECEIVED_VALID` document exists.
5. Required evidence absent/unreadable → `INFO_REQUIRED` under EVD-001.
6. Contradictory evidence → `MANUAL_REVIEW` under EVD-002.
7. Coverage and eligibility failures take precedence over evidence collection where the policy outcome is already conclusive.

## Guardrails
- A document summary supports triage; it does not authorize payment or final claim closure.
- An anomaly or contradiction must be routed to review, never resolved by agent guesswork.
- Evidence metadata does not contain expected dispositions, scenario labels, rules to apply, or evaluation targets.
- Keep `validation/` outside agent retrieval.

## Dependency noted for Item #9
High repair estimates are present for selected scenarios. A device-value/valuation reference and formal high-cost threshold must be introduced in Item #9 before that indicator is automatically derived.
