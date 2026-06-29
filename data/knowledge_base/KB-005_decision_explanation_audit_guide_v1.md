# Decision Explanation and Audit Guide

**Document ID:** KB-005  
**Version:** 1.0  
**Effective date:** 2026-06-23  
**Purpose:** Define the minimum explanation and traceability requirements for every triage recommendation.

## 1. Explanation principles

Every result must distinguish:

- **Verified facts:** retrieved from structured sources or validated evidence.
- **Customer-reported facts:** taken from claim intake and not yet independently verified.
- **Unknown or unresolved facts:** missing, ambiguous, or conflicting information.
- **Rule-based result:** the disposition and the applicable rule references.

The agent must not expose hidden reasoning or invent a rationale. It should provide an auditable, concise summary grounded in source data and configured rules.

## 2. Required result fields

For every claim, log or return:

- `claim_id`
- `recommended_disposition`
- `reason_summary`
- `facts_used`
- `rules_applied`
- `evidence_status_summary`
- `missing_information` (when applicable)
- `manual_review_reason` (when applicable)
- `source_references`
- `human_review_required`
- `audit_timestamp`
- `workflow_version`

## 3. Disposition wording

### PROCEED
Use: “The claim appears eligible for standard processing based on the available information and configured policy checks.”

### INFO_REQUIRED
Use: “Additional information is required before the claim can be assessed further.”

### MANUAL_REVIEW
Use: “The claim requires analyst review because a material conflict, exception, or configured review trigger was identified.”

### NOT_ELIGIBLE
Use: “Based on the verified information and configured policy rules, the claim is recommended for decline confirmation.”

The agent must not state final approval, final payment, final denial, or fraud conclusions.

## 4. Evidence of traceability

Source references should point to records rather than reproduce unnecessary content. Examples include policy ID, plan ID, evidence bundle ID, historical claim IDs, and rule IDs. This supports auditability while minimizing exposure of synthetic or future production PII.

## 5. References

- Decision Taxonomy v1: Item #1
- Policy Rule Catalog v1: Item #3
- Claims Triage SOP: KB-001
- Safety, Privacy, and Scope Boundaries: KB-006
