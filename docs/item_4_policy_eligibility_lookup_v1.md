# Item #4 — Policy Eligibility Lookup (v1.0)

## Purpose
This reference dataset provides the factual policy, enrolment, and covered-device context required by the Item #3 policy rules. It is a **lookup source**, not a decision engine.

It answers: which policy and plan does the claimant have, what is its coverage period/status, and which smartphone is enrolled?

## Scope and grain
- Product family: DeviceProtect
- Device scope: Smartphones only
- Record grain: **one policy enrolment + one current covered smartphone per row**
- Dataset snapshot date: **2026-06-23**
- Total records: **120**
- Unique customers: **100**
- Customers with two policies: **20**

## Deliberate privacy boundary
The dataset has no real or synthetic personal names, addresses, emails, phone numbers, payment information, or government identifiers. `customer_id` is a stable synthetic alias, and `covered_device_identifier` is intentionally not a real IMEI.

## Lookup-key priority
1. `policy_id` — preferred; should resolve to exactly one policy record.
2. `customer_id` + `covered_device_identifier` — valid fallback; should resolve to exactly one record.
3. `customer_id` only — valid only when it resolves uniquely. More than one matching policy triggers `MANUAL_REVIEW` under `DATA-001`.

## Policy active-on-incident-date logic
For an incident date `D`, the policy is active only when all conditions are true:

1. `coverage_start_date <= D <= coverage_end_date`
2. `policy_termination_date` is blank **or** `D < policy_termination_date`
3. `D` does not fall within a suspension period. An empty `suspension_end_date` means the suspension is ongoing at the dataset snapshot.

`policy_status` is a snapshot indicator. It must **not** be used alone to decide an incident that occurred in the past. This design prevents wrongly rejecting a claim that happened before an eventual cancellation.

## Relationship to other items
- **Item #1:** Provides facts used to arrive at one of the four permitted triage dispositions.
- **Item #2:** `plan_id` retrieves plan terms and coverage configuration; these are not duplicated here.
- **Item #3:** `ELG-002` evaluates active policy coverage; `DEV-002` compares the current claim device against `covered_device_identifier`.
- **Item #5:** Prior claims history will provide claim-count and limit-consumption information; those fields are intentionally absent here.

## Dataset composition
| Category | Count |
|---|---:|
| ACTIVE | 84 |
| EXPIRED | 18 |
| CANCELLED | 10 |
| SUSPENDED | 8 |
| DP-ESSENTIAL | 32 |
| DP-COMPLETE | 53 |
| DP-PREMIUM | 35 |

## Storage
Store the CSV and JSON files in `data/reference/`. Store this document in `docs/`.
