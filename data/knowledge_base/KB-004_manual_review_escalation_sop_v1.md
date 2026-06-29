# Manual Review and Escalation SOP

**Document ID:** KB-004  
**Version:** 1.0  
**Effective date:** 2026-06-23  
**Purpose:** Standardize analyst referral for cases that cannot be safely resolved through deterministic triage.

## 1. When to escalate

Route a case to manual review when the configured rule path returns `MANUAL_REVIEW`. Typical triggers include:

- `DATA_CONFLICT`: multiple or conflicting authoritative records.
- `DEVICE_MISMATCH`: claimed device does not match the enrolled device but the mismatch is not conclusively resolved.
- `DATE_ANOMALY`: material inconsistency among incident, document, policy, or repair dates.
- `REPEAT_CLAIM_PATTERN`: history indicates a repeat pattern requiring human assessment.
- `HIGH_COST_EXCEPTION`: repair estimate or proposed cost exceeds the configured review threshold.
- `POLICY_EXCEPTION`: a suspected exclusion or exception requires judgement.
- `RULE_NOT_AVAILABLE`: product, region, policy version, or rule configuration is outside MVP scope.
- `POTENTIAL_DUPLICATE`: a materially similar recent claim may already exist.

Do not create additional review reasons without updating the authoritative manual-review reason catalogue.

## 2. Required escalation packet

The agent should supply a concise, fact-based packet containing:

- Claim ID and submission timestamp
- Retrieved policy ID, plan ID, and covered-device identifier
- Reported incident category and incident date
- Recommended disposition: `MANUAL_REVIEW`
- Manual-review reason code and plain-language explanation
- Relevant rule IDs and source references
- Evidence status and identified contradiction, if any
- Prior-claim summary used by the system
- Explicit list of unresolved facts or requested analyst decision

## 3. Writing the escalation summary

State only verified facts and clearly label unknowns. Use neutral language such as:

> “The claimed IMEI differs from the enrolled-device identifier. A replacement-device record was not available in the retrieved source. Analyst validation is required before coverage can be determined.”

Avoid statements such as “the customer submitted a false device,” “this is fraud,” or “the claim should be denied.”

## 4. Analyst actions are out of scope

The MVP triage agent does not perform analyst investigation, document forensics, payment authorization, fraud determination, or policy exception approval. It only prepares the referral packet.

## 5. References

- Manual Review Reason Catalogue: Item #1 / Item #3
- Policy Rule Catalog v1: Item #3
- Decision Explanation and Audit Guide: KB-005
