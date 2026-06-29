# BYOC Claims Triage — Item #5: Prior Claims History

## Purpose
This dataset contains **finalized synthetic historic claims**. It supplies prior-usage facts required to apply the Item #3 policy rules:

- `LIM-001` — annual claim allowance has not been exhausted
- `LIM-002` — theft-specific claim allowance has not been exhausted

It is a transactional history source, not a model-training dataset and not the new-claim intake dataset.

## Scope and boundaries
- 112 finalized historical claims across 70 policies.
- All records link to the Item #4 Policy Eligibility Lookup.
- No customer names, contact information, addresses, payment data, or real-device identifiers are included.
- Claims are dated before the synthetic snapshot date: **2026-06-23**.
- All synthetic incident dates occur within an active coverage interval; they are not generated during suspension or after termination.
- Historic `final_claim_status` represents final processing status and must not be confused with the Item #1 triage dispositions.

## How the rules use this data
For a new claim, retrieve only history for the same `policy_id` where:

```text
claim_reported_date < current_claim_reported_date
```

Then calculate:

```text
annual_claims_consumed = count(claim_limit_consumed_flag == TRUE)
theft_claims_consumed  = count(theft_limit_consumed_flag == TRUE)
```

Compare these values to the plan limits in Item #2.

- A settled claim consumes the relevant allowance.
- A declined or withdrawn claim does **not** consume the allowance.
- Historical volume may be used later to create a review signal, but it must never cause automatic decline.

## Relationships
```text
Item #2 Plan Master
      └── plan limits
Item #4 Policy Eligibility Lookup
      └── policy, customer and covered-device keys
Item #5 Prior Claims History
      └── finalized prior claims and limit-consumption flags
```

## Source-of-truth rule
`data/reference/prior_claims_history_v1.csv` is the source of truth. Any summary returned to an agent should be calculated from this file at retrieval time. Do not maintain a separate editable claim-count summary because it can drift from transaction history.
