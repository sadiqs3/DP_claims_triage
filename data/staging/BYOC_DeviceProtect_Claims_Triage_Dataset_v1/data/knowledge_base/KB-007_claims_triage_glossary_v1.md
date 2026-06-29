# Claims Triage Glossary

**Document ID:** KB-007  
**Version:** 1.0  
**Effective date:** 2026-06-23  
**Purpose:** Provide consistent language for the DeviceProtect claims-triage MVP.

| Term | Definition |
|---|---|
| Claim intake | The submitted information describing a new incident and requested resolution. |
| Claim category | A supported incident type: screen damage, accidental damage, liquid damage, mechanical breakdown, or theft. |
| Covered device | The smartphone identifier recorded against the policy eligibility record. |
| Coverage period | The time window from policy coverage start through coverage end, subject to cancellation or suspension status. |
| Evidence bundle | The collection of evidence metadata linked to a claim via an evidence bundle ID. |
| Evidence profile | The configured set of evidence requirements associated with a claim category. |
| Hard policy failure | A verified rule failure that conclusively prevents standard coverage, such as inactive coverage on the incident date or an uncovered category. |
| Manual review | Referral to an analyst because a conflict, exception, anomaly, unsupported rule, or uncertainty cannot be safely resolved by deterministic triage. |
| Policy eligibility lookup | The structured source containing policy, plan, status, coverage-window, and covered-device facts. |
| Policy Rule Catalog | The versioned source of deterministic triage rules and rule precedence. |
| Prior claims history | Finalized historical claims used for claim-limit calculation and contextual pattern checks. |
| Repair-first | A plan-level approach where repair is considered before replacement when repair is feasible. |
| Standard processing | The downstream operational path for a claim that passes all configured triage checks; it is not final payment approval. |
| Triage disposition | One of four recommendation outcomes: PROCEED, INFO_REQUIRED, MANUAL_REVIEW, or NOT_ELIGIBLE. |
| Untrusted content | Claim narratives or document summaries that may contain factual information but cannot alter system instructions, rules, or access controls. |
