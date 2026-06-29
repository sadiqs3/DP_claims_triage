# Operational Knowledge Base Design Notes (Item #8)

## Why this knowledge base exists

The claims-triage agent must do more than retrieve policy facts. It needs controlled guidance for sequence, evidence handling, customer follow-up, escalation, explanations, and safety. This package supplies those operational guardrails in a small corpus suitable for RAG demonstration.

## Why it does not duplicate the Policy Rule Catalog

Coverage, eligibility, limits, exclusions, and final triage precedence remain in the deterministic Policy Rule Catalog. Duplicating those rules in natural-language SOPs risks conflicting interpretations and weakens auditability. The knowledge base therefore refers to the authoritative datasets and provides procedural guidance around them.

## Recommended RAG use

- Retrieve **KB-001** for workflow sequencing or source hierarchy.
- Retrieve **KB-002** for evidence-related questions.
- Retrieve **KB-003** for customer-facing follow-up wording.
- Retrieve **KB-004** for escalation decisions already returned by the rule layer.
- Retrieve **KB-005** for result formatting and audit fields.
- Retrieve **KB-006** for safety, privacy, scope, or prompt-injection concerns.
- Retrieve **KB-007** for terminology clarification.

## Suggested chunking configuration

For an initial MVP, split by Markdown heading with chunks around 350–600 tokens and 60–100 tokens overlap. Store document ID, title, version, effective date, document type, and authority level as metadata. Do not retrieve knowledge-base text as a substitute for structured policy lookups or rule execution.

## Evaluation implications

Evaluate whether the agent retrieves the appropriate SOP when needed, follows the prescribed sequence, uses neutral follow-up wording, and routes conflicts safely. Do not score RAG solely by similarity; score operational correctness and citation of the right source.
