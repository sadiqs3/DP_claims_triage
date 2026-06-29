# DeviceProtect Plan / Protection Product Master — v1.0

**Status:** Frozen draft — Item #2  
**Product family:** DeviceProtect (fictional)  
**Operating market:** US (single-market MVP context)  
**Covered device category:** Smartphones only

## Capstone scope

The capstone models a narrowly scoped, AI-assisted claims-triage workflow for fictional smartphone-protection plans. The design intentionally uses three plan variants so that the agent must retrieve and apply differentiated coverage, while the synthetic-data workload remains manageable.

## Plan catalogue

| Plan ID | Plan name | Coverage intent | Annual claim limit | Theft-claim limit |
|---|---|---|---:|---:|
| `DP-ESSENTIAL` | DeviceProtect Essential | Screen-damage protection | 1 | 0 |
| `DP-COMPLETE` | DeviceProtect Complete | Accidental, liquid and mechanical-breakdown coverage | 2 | 0 |
| `DP-PREMIUM` | DeviceProtect Premium | Complete cover plus theft protection | 2 | 1 |

## Claim categories

### Supported triage categories

- `SCREEN_DAMAGE`
- `ACCIDENTAL_DAMAGE`
- `LIQUID_DAMAGE`
- `MECHANICAL_BREAKDOWN`
- `THEFT`

### Explicit universal exclusion

- `LOSS` is captured in the coverage matrix as `GLOBAL_EXCLUSION` with `covered_flag=FALSE` for every plan. It is retained so a clear loss claim can later be evaluated as a rule-grounded `NOT_ELIGIBLE` recommendation rather than treated as an unspecified category.

### Other exclusions to introduce in Item #3 policy rules

- Cosmetic-only damage
- Intentional damage
- Data-only issues
- Unauthorized repair or device modification

## Resolution assumptions

All plans use `REPAIR_FIRST`. A replacement may be considered only when repair is not feasible and all plan/rule/evidence requirements are satisfied. For theft under Premium, a replacement is the expected operational pathway after the claim passes required checks.

## Evidence-profile references

The `evidence_profile_id` field intentionally points to future data. Item #3 and the later evidence-metadata dataset will define what each profile means. For example, `EVD-THEFT-01` will require a police-report reference and enrolled-device validation; it is not defined as a detailed rule in this Item #2 package.

## Relationship to the rest of the ecosystem

```text
Plan Master + Coverage Matrix
        ↓
Policy Rules / Decision Tables (Item #3)
        ↓
Policy Eligibility Lookup + Covered Device + Claim History
        ↓
Claim Intake + Evidence State
        ↓
Item #1 Triage Disposition
```

## Synthetic-data guardrails

1. The terms are fictional and must be labelled as synthetic in the project documentation and demo.
2. `covered_flag=TRUE` does not by itself mean `PROCEED`; the claim must still pass eligibility, evidence, and manual-review checks.
3. A risk signal must not override coverage and independently cause `NOT_ELIGIBLE`.
4. Specific denial and evidence logic belongs in Item #3 rules, not in prose fields in this dataset.
