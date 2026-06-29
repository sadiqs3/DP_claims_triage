# Structured Policy Rules / Decision Tables — Version 1.0

## Scope
This rule set supports a fictional DeviceProtect smartphone-protection product family with plans `DP-ESSENTIAL`, `DP-COMPLETE`, and `DP-PREMIUM`. It supports five claim categories: `SCREEN_DAMAGE`, `ACCIDENTAL_DAMAGE`, `LIQUID_DAMAGE`, `MECHANICAL_BREAKDOWN`, and `THEFT`.

## Design principle
The agent may extract facts, retrieve records, apply the deterministic rule catalog, and produce a traceable explanation. It may not create or override coverage rules.

## Decision precedence amendment to Item #1
The authoritative order for this implementation is:

1. Critical data conflict, unavailable rule, or unsupported scope → `MANUAL_REVIEW`
2. Conclusive hard policy failure based on verified facts → `NOT_ELIGIBLE`
3. Material eligibility fact missing or unclear → `INFO_REQUIRED`
4. Eligibility passed but anomaly/exception needs judgement → `MANUAL_REVIEW`
5. Eligibility passed but mandatory supporting evidence is missing → `INFO_REQUIRED`
6. All applicable rules pass → `PROCEED`

This amendment prevents unnecessary document requests where a claim is already conclusively outside coverage.

## Rule groups

| Group | What it protects |
|---|---|
| Data Validation | A reliable, unique policy and valid plan configuration |
| Eligibility | Coverage period and supported product scope |
| Device Validation | Correct association of the claimed device |
| Claim Classification | Reliable claim-category determination |
| Coverage and Limits | Covered incident types and claim limits |
| Exclusions | Confirmed global exclusions versus unresolved concerns |
| Anomaly | Safe routing of unusual cases without automated adverse decisions |
| Evidence | Mandatory supporting documentation and its consistency |
| Outcome | A controlled standard-processing gate |

## Global exclusions in v1
The following exclusions apply to all plans only where they are **verified**: `LOSS`, `COSMETIC_ONLY_DAMAGE`, `INTENTIONAL_DAMAGE`, `DATA_ONLY_ISSUE`, and `UNAUTHORIZED_MODIFICATION_OR_REPAIR`.

A weak or ambiguous narrative is not enough to apply an exclusion. It requires `MANUAL_REVIEW`.

## Not modelled in v1
Settlement/payment, fraud confirmation, legal compliance, warranty coordination, repair-vendor selection, premium/refund calculations, reimbursement amount calculations, and non-smartphone categories are outside this capstone MVP.
