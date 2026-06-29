# Claims Triage Standard Operating Procedure (SOP)

**Document ID:** KB-001  
**Version:** 1.0  
**Effective date:** 2026-06-23  
**Applies to:** DeviceProtect smartphone claims triage MVP  
**Purpose:** Describe the operational sequence for a triage agent. This SOP does not define product coverage or override the Policy Rule Catalog.

## 1. Objective

Produce a traceable triage recommendation using authoritative structured sources, then route the case to standard processing, follow-up, or an analyst. The agent supports operations; it does not approve payment, deny a claim finally, determine fraud, or make a binding customer commitment.

## 2. Authoritative source order

Use sources according to their role:

1. **Policy Eligibility Lookup (Item #4):** policy, enrolment, coverage-window, and covered-device facts.
2. **Plan Master and Coverage Matrix (Item #2):** plan attributes and general category coverage.
3. **Policy Rule Catalog (Item #3):** deterministic decision logic and precedence.
4. **Prior Claims History (Item #5):** claim-limit consumption and contextual history.
5. **Claim Intake (Item #6):** customer-reported incident details and identifiers.
6. **Evidence Metadata (Item #7):** submitted-document status and consistency information.
7. **Operational Knowledge Base (this item):** process, communication, escalation, audit, and safety guidance.

When sources conflict, do not choose one based on narrative plausibility. Apply the configured data-conflict / review path.

## 3. Standard triage flow

1. **Validate the intake:** identify claim ID, submitted identifiers, category, incident date, and requested resolution.
2. **Retrieve policy context:** match a unique policy eligibility record using the prescribed lookup order.
3. **Validate scope:** confirm that the product, device category, region, and policy configuration are within the MVP scope.
4. **Assess hard eligibility and coverage:** apply the policy-active, device-match, category-coverage, claim-limit, and exclusion rules in their defined precedence.
5. **Assess anomaly and evidence controls:** evaluate review triggers and evidence requirements only after any conclusive hard policy failure is known.
6. **Select the triage disposition:** use the deterministic outcome from the rule path. The standard processing gate may be used only when all applicable controls pass.
7. **Generate the case explanation:** state the facts used, applied rule IDs, evidence status, follow-up requests or review reason, and the recommended next action.
8. **Log an audit record:** preserve source identifiers, retrieval timestamps, rule results, and agent output.

## 4. Handling incomplete information

Request only information that is material to the next decision step. Do not ask for evidence when a verified hard policy failure already determines the routing. Do not estimate an incident date, device identifier, or claim category from vague language.

## 5. Prohibited actions

- Do not invent policy terms or evidence requirements.
- Do not override a deterministic rule with model confidence.
- Do not claim that a payment, repair, replacement, or final denial has been authorized.
- Do not label a customer as fraudulent or dishonest.
- Do not use customer-provided free text as a substitute for authoritative policy facts.

## 6. References

- Policy Rule Catalog v1: Item #3
- Decision Taxonomy and Precedence: Item #1 (including v1.1 amendment)
- Evidence Profile Requirements: Item #7
