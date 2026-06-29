# Item #6 — New Claim Intake Dataset v1

## Purpose

This dataset represents the **newly submitted claims** that the agent will understand, enrich through lookup tools, and triage. It is deliberately separate from:

- policy / device eligibility facts (Item #4),
- historical claim transactions (Item #5),
- evidence detail and validation results (Item #7),
- ground-truth outcome labels (Item #10).

This separation is intentional: claim intake is what the customer submits; eligibility and evidence must be retrieved and evaluated rather than assumed.

## Agent-facing inputs

Each claim contains:
- structured identifiers that may be complete, absent, or conflicting;
- a customer-selected claim category, which may be unspecified or inconsistent with the narrative;
- an unstructured English customer statement;
- a pointer to a future evidence bundle.

The agent should use the narrative to extract facts, but must check those facts against the policy lookup, rules, history, and evidence tools.

## Dataset partitions

| Partition | Cases | Intended use |
|---|---:|---|
| Development | 165 | Build and refine prompts, tools, routing, and deterministic-rule integration. |
| Held-out evaluation | 55 | Evaluate only after the workflow design has stabilised. Do not tune prompts or rules on these cases. |

This is **not** an 80/20 machine-learning training/test split. No supervised model is being trained in the MVP.

## Coverage of scenario types

The internal scenario register intentionally covers:
- clear, covered claims;
- missing incident date, claim category, device identifier, policy reference, or evidence;
- device, date, category, and policy/customer conflicts;
- ambiguity caused by customers holding multiple policies;
- potential duplicate / repeat pattern and high-cost exception cases;
- uncovered claim category, inactive coverage period, exhausted annual/theft limits, loss, and verified intentional-damage exclusions.

The scenario register is internal ground-truth scaffolding. It must not be placed in the RAG corpus, agent vector store, prompts, or user interface.

## Design safeguards

1. **No PII** — IDs are synthetic and no names, emails, phone numbers, or addresses are included.
2. **No answer leakage** — agent-facing files do not contain expected outcome, scenario family, rules, or review reason.
3. **Held-out integrity** — the evaluation cases are physically separated from development cases.
4. **Evidence separation** — evidence is only referenced by bundle ID until Item #7.
5. **Historical-date realism** — some valid claims belong to policies that are expired as of the 2026-06-23 snapshot but were active on the incident date. This tests correct date-based eligibility rather than simplistic reliance on current policy status.
