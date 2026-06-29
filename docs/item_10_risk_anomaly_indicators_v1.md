# Item #10 — Risk and Anomaly Indicators v1

## Purpose

Risk signals are a **secondary safety layer**. They identify cases that require analyst judgement after deterministic eligibility checks. They do not determine policy coverage, payout, fraud, or final customer communication.

## Indicators in scope

1. `RSK-001 HIGH_REPAIR_COST`
   - Trigger: a valid repair estimate is at least 65% of the synthetic reference value for the covered device.
   - Action: `MANUAL_REVIEW`, reason `HIGH_COST_EXCEPTION`.

2. `RSK-002 RECENT_RELATED_CLAIM_PATTERN`
   - Trigger: a controlled reconciliation service returns a corroborated related-claim event for the same policy and covered device inside a 30-day review window.
   - Action: `MANUAL_REVIEW`, reason `POTENTIAL_DUPLICATE`.
   - Guardrail: timing alone is insufficient. The agent must not infer duplicate submission merely because two claims are close in time.

3. `RSK-003 DEVICE_VALUE_REFERENCE_UNAVAILABLE`
   - Trigger: a valid repair estimate exists but no active value reference is available for the covered device model.
   - Action: `MANUAL_REVIEW`, reason `RULE_NOT_AVAILABLE`.
   - Current v1 data has no triggers because all six models are mapped.

## Decision precedence

1. Apply authoritative eligibility and hard policy-rule checks first.
2. A conclusive policy failure remains `NOT_ELIGIBLE`; risk does not override it.
3. When eligibility is otherwise clear and a triggered risk signal is returned, route to `MANUAL_REVIEW`.
4. Do not ask the customer to resolve a risk signal. Do not accuse the customer of fraud.
5. Explain the objective facts and source reference to the analyst.

## What is deliberately excluded

- Fraud scores or fraud labels
- Automated rejection
- Blacklists, demographic variables, or PII-based risk factors
- Generalized statistical anomaly models
- Any numeric confidence score that could be mistaken for a decision probability

## Why there is no risk score

A score can imply unjustified precision and encourage automatic adverse decisions. v1 uses named, auditable signals with an explicit analyst-routing action instead.
