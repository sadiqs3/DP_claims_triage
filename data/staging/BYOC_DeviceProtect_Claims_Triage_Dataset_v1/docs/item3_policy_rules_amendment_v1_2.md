# Item #3 Policy Rules Amendment v1.2

## Change

Rule `ANM-001` is a generic anomaly-routing rule. Its previous `manual_review_reason` field contained four slash-separated values, which violated the controlled reason-catalogue design.

The active catalogue now leaves that field blank for `ANM-001`. When the rule triggers, the specific reason must be supplied by the linked Item #10 risk indicator result (`HIGH_COST_EXCEPTION`, `POTENTIAL_DUPLICATE`, `REPEAT_CLAIM_PATTERN`, or `DATE_ANOMALY`).

## Impact

- No change to the disposition: `ANM-001` continues to route to `MANUAL_REVIEW`.
- No change to claim-intake cases, labels, evidence, or risk-result data.
- This is a data-normalisation correction that restores consistency with the controlled review-reason catalogue.
