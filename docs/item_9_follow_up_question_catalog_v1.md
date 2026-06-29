# Item #9 — Follow-up Question Catalogue

**Version:** 1.0  
**Effective date:** 2026-06-23  
**Purpose:** Provide a controlled set of neutral, rule-grounded customer questions for claims that require additional information.

## 1. Role in the triage workflow

The follow-up catalogue is used only after Item #3 deterministic rules produce `INFO_REQUIRED`.
It does not decide coverage and it must not be used to override a `MANUAL_REVIEW` or `NOT_ELIGIBLE` outcome.

```text
Claim intake + policy + evidence
        ↓
Deterministic rule evaluation
        ↓
INFO_REQUIRED?
   ├── No → retain existing disposition
   └── Yes → select catalogue question(s)
                ↓
          receive response / upload
                ↓
          re-run retrieval and rules
```

## 2. Design principles

- Ask only for the minimum information necessary for the next decision step.
- Ask eligibility facts before evidence.
- Ask no more than three questions in one interaction.
- Do not ask customers to resolve internal data conflicts, ambiguous system matches, contradictory evidence, or policy exceptions.
- Do not promise approval, make a final denial, or accuse a customer of fraud.
- Do not request proof of purchase or repair quotes in Version 1 because they are not mandatory evidence for triage.

## 3. Coverage of the catalogue

The v1 catalogue contains 14 questions covering:
- policy/customer reference;
- incident date;
- covered-device identifier;
- ambiguous incident category;
- missing or unreadable required evidence for screen damage, accidental damage, liquid damage, mechanical breakdown, and theft.

There are intentionally **no questions** for:
- verified coverage exclusions;
- inactive policies;
- claim limits exhausted;
- conflicting policy records;
- device mismatches;
- contradictory evidence;
- anomaly/risk triggers;
- unavailable policy configuration.

Those scenarios require the existing `NOT_ELIGIBLE` or `MANUAL_REVIEW` path.

## 4. Selection sequence

1. Respect Item #1 decision precedence and Item #3 rule outcomes.
2. If a higher-precedence `MANUAL_REVIEW` or `NOT_ELIGIBLE` condition exists, do not ask questions.
3. If `INFO_REQUIRED` is returned, select the matching active catalogue questions.
4. Prioritize eligibility facts (policy/customer reference, date, device ID, category).
5. Ask at most three questions, ordered by `question_priority`.
6. After the response, re-run retrieval and deterministic rules.
7. If a request remains unresolved after the permitted repeat, route the case to manual review rather than looping.

## 5. Agent-facing files

- `data/reference/follow_up_question_catalog_v1.csv`
- `data/reference/follow_up_question_selection_rules_v1.csv`

These may be used as structured retrieval/tool inputs. They should not be placed into the operational RAG corpus as a substitute for the policy rule catalog.

## 6. Relationship to other items

- **Item #1:** Defines `INFO_REQUIRED` and safety boundaries.
- **Item #3:** Supplies rule IDs that trigger follow-up.
- **Item #6:** Contains fields and narratives that may be incomplete.
- **Item #7:** Defines evidence profiles and document states.
- **Item #8:** Defines the approved communication style.

## 7. Versioning

Any change to question wording, trigger condition, or repeat limit should create a new catalogue version and be tested against the held-out evaluation set.
