# Item #11 — Ground-Truth Labelled Decision Set (v1.0)

## Purpose
This package is the internal evaluation oracle for the DeviceProtect claims-triage capstone. It specifies the expected disposition, decision-driving rule(s), follow-up question(s), manual-review reason, evidence assessment, and next operational action for every Item #6 claim.

## Security boundary — critical
These labels are **not agent knowledge**. Do not ingest them into RAG, pass them in prompts, expose them through tools, show them in the UI, or place them beside agent-readable claim files.

- Development labels: use only for workflow debugging, prompt/tool refinement, and controlled regression tests.
- Held-out labels: lock until final evaluation. Do not inspect individual outcomes while changing agent rules, prompts, retrieval, or orchestration.

## Rule-order nuance
Some cases contain more than one verified hard failure. For example, a loss claim may be both a global exclusion and a coverage-matrix failure. `gold_primary_rule_id` gives a canonical reference, while `gold_acceptable_primary_rule_ids` records all valid primary citations so an agent is not penalized for a logically valid check order.

## Evaluation use
At minimum, evaluate:
1. disposition exact-match accuracy and macro-F1;
2. primary-rule validity against `gold_acceptable_primary_rule_ids`;
3. follow-up question ID precision/recall for INFO_REQUIRED cases;
4. manual-review reason exact match for MANUAL_REVIEW cases;
5. no-question safety rate for NOT_ELIGIBLE and MANUAL_REVIEW cases;
6. explanation traceability: whether the cited rules/facts match the oracle.
