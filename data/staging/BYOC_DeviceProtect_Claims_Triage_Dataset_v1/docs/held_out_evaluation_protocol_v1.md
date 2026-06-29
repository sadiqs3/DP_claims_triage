# Held-Out Evaluation Protocol (v1.0)

## Purpose
The 55 held-out claims are reserved to demonstrate that the agent was not evaluated only on cases used during design.

## Before final evaluation
- Keep `ground_truth_claim_labels_held_out_evaluation_v1.*` inaccessible to the agent and out of development notebooks used for tuning.
- Freeze the agent configuration: prompts, rule-engine logic, tool contracts, retrieval corpus, and any deterministic parsing heuristics.
- Record the configuration version and run timestamp.

## During evaluation
For each held-out claim, run the normal agent workflow and capture:
- returned disposition;
- rule IDs and factual citations;
- selected follow-up question IDs, if any;
- manual-review reason, if any;
- response text and tool trace.

## Metrics
- Disposition accuracy and macro-F1 across all four outcomes.
- Primary-rule acceptance rate: agent primary rule belongs to `gold_acceptable_primary_rule_ids`.
- Follow-up exact-set match / precision / recall for INFO_REQUIRED cases.
- Manual-review-reason accuracy.
- Safety violations: questions asked for NOT_ELIGIBLE or MANUAL_REVIEW cases; unsupported final approval/denial language; risk signal used as an automatic decline reason.

## After evaluation
Do not modify the held-out labels. If the agent is changed, label the next run as a new evaluation iteration rather than overwriting the initial result.
