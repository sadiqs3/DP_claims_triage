# BYOC Claims Triage Decision Taxonomy — v1.0

**Status:** Frozen draft — Item #1  
**Purpose:** Defines permitted triage dispositions for an AI-assisted device-protection claims workflow. The system recommends and routes cases; it does not make final payment, repair authorization, fraud, or customer-closure decisions.

## Primary dispositions

| Code | Display name | Definition | System action |
|---|---|---|---|
| `PROCEED` | Eligible for standard processing | Available facts indicate the claim is within policy coverage, required evidence is present, and no manual-review trigger exists. | Route to the standard repair/replacement/claims-processing path. |
| `INFO_REQUIRED` | Request additional information | The claim may be eligible, but one or more material eligibility facts or required supporting evidence are missing or unclear. | Hold the claim and generate only targeted follow-up questions. |
| `MANUAL_REVIEW` | Refer for manual review | A conflict, exception, anomaly, unsupported scenario, or rule gap means the system should not make a deterministic recommendation. | Route to a claims analyst with facts, applicable rules, and the review reason. |
| `NOT_ELIGIBLE` | Not eligible — decline recommendation | A verified policy rule conclusively shows the claim is not covered. Final decline communication remains subject to human/process confirmation. | Provide rule-grounded reason and route for decline confirmation. |

## Manual-review reasons

| Code | Description |
|---|---|
| `DATA_CONFLICT` | Structured facts, evidence, or claim narrative materially conflict. |
| `DEVICE_MISMATCH` | Claimed device identifier differs from the enrolled covered device. |
| `DATE_ANOMALY` | Incident, quote, repair, or policy dates are inconsistent or require interpretation. |
| `REPEAT_CLAIM_PATTERN` | Claim history indicates a pattern requiring analyst assessment. |
| `HIGH_COST_EXCEPTION` | Repair/replacement value exceeds a defined operational threshold. |
| `POLICY_EXCEPTION` | Goodwill, exception, or special operational handling is requested or required. |
| `RULE_NOT_AVAILABLE` | Product, geography, policy version, or incident scenario is outside the supported rule set. |
| `POTENTIAL_DUPLICATE` | A materially similar recent claim or evidence item is detected. |

## Information distinction

### Eligibility facts
- Policy status on incident date
- Incident date
- Covered-device identity / IMEI / serial number
- Incident category
- Coverage start and end dates
- Waiting-period applicability
- Claim-limit availability

### Supporting evidence
- Damage photos
- Repair quotation
- Proof of purchase where required
- Police report reference where required
- Identity or ownership confirmation where required

**Rule:** A clearly failed coverage rule should produce NOT_ELIGIBLE without requesting irrelevant supporting evidence. Missing information should normally produce INFO_REQUIRED rather than an automatic decline.

## Decision precedence

1. **System conflict, exception, material inconsistency, anomaly, unsupported scenario, or unavailable rule** → `MANUAL_REVIEW`
2. **A minimum eligibility fact is missing or unclear** → `INFO_REQUIRED`
3. **A verified hard policy rule clearly fails** → `NOT_ELIGIBLE`
4. **Eligibility appears met but required supporting evidence is missing or unclear** → `INFO_REQUIRED`
5. **All mandatory checks pass and no review trigger exists** → `PROCEED`

## Safety boundaries

1. The workflow is AI-assisted triage, not autonomous final claims adjudication.
2. LLM confidence alone must not determine a disposition.
3. Structured policy rules are authoritative for coverage determinations.
4. Conflicting sources must be routed to MANUAL_REVIEW; the system must not guess.
5. Risk signals can trigger MANUAL_REVIEW but must never independently trigger NOT_ELIGIBLE.
6. Every result must include disposition, facts used, rules applied, missing information, and manual-review reason where applicable.

## MVP scope

- **Product family:** One device-protection product family
- **Geography:** One geography / operating context
- **Incident categories:** Three to four categories
- **Language:** English claim narratives
- **Out of scope:** Payment decisions; Repair authorization; Fraud confirmation; Direct customer claim closure.

## Recommended agent output contract

```json
{
  "claim_id": "CLM-1001",
  "recommended_disposition": "INFO_REQUIRED",
  "reason_summary": "The policy is active and accidental damage may be covered, but the incident date and damage photos are missing.",
  "facts_used": [
    "policy_status=ACTIVE",
    "coverage_type=ACCIDENTAL_DAMAGE"
  ],
  "rules_applied": [
    "POL-AD-01",
    "EVD-AD-02"
  ],
  "missing_information": [
    "Incident date",
    "Photos showing damage"
  ],
  "manual_review_reason": null,
  "human_review_required": false
}
```
