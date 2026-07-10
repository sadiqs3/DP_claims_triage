# Architecture Decisions

## ADR-001 — Persisted Semantic Vector Index

**Status:** Accepted  
**Date:** 2026-07-07

### Context

The project already contains a tested in-memory semantic retriever using OpenAI `text-embedding-3-small` embeddings, L2 normalisation, and cosine-similarity ranking.

The mid-submission baseline requires a reproducible vector storage and indexing capability without changing deterministic triage authority or silently changing the currently evaluated semantic retrieval behaviour.

### Options Considered

1. FAISS `IndexFlatIP`
2. ChromaDB persistent collection
3. Continue with in-memory NumPy retrieval only

### Decision

Use **FAISS `IndexFlatIP`** as the persisted semantic index.

The index uses L2-normalised vectors and inner-product search, which preserves cosine-similarity ranking semantics used by the current in-memory semantic baseline.

A separate manifest stores corpus fingerprint, embedding model, vector dimension, chunk ordering fingerprint, index type, and build metadata.

### Rationale

- Preserves the current tested semantic retrieval behaviour with minimal change.
- Suitable for the approved 21-chunk corpus and local execution.
- Supports deterministic persistence, loading, integrity validation, and rebuild.
- Keeps metadata, authority boundaries, and source lineage explicit.
- Leaves the cross-encoder reranker independent of the vector store.

### Consequences

- The current `ControlledSemanticRetriever` remains the evaluated in-memory baseline.
- A separate persisted FAISS component is used for controlled runtime retrieval.
- Corpus or embedding-configuration mismatches block index loading and require a controlled rebuild.
- RAG retrieval remains analyst-facing and non-authoritative.

---

## ADR-002 — Deterministic Rules Remain Authoritative

**Status:** Accepted  
**Date:** 2026-07-07

### Context

The project supports device protection claim triage. Claim outcomes depend on structured policy, coverage, evidence, device, claim-history, and risk signals.

Because this workflow may influence operational decisions, deterministic rules must remain the authoritative source for routing. GenAI and RAG components must not override policy eligibility, coverage, evidence requirements, risk routing, or final response fields.

### Decision

The deterministic triage layer is authoritative for:

- `triage_outcome`
- `triggering_rule_id`
- `precedence_stage`
- `decision_reason`
- `rule_trace`
- `decision_support_only`
- `system_limitations`

Agent-generated content and RAG output are allowed only as controlled decision-support context.

### Rationale

- Preserves auditability and reproducibility.
- Prevents hallucinated or unsupported policy interpretation.
- Aligns with the project scope: decision support, not automated approval or final denial.
- Allows deterministic outputs to be evaluated directly against development labels.

### Consequences

- Any decision accuracy improvement must come from deterministic rule or structured-data improvements, not from LLM override.
- RAG is evaluated separately from workflow routing.
- The final response must be protected by a response authority guardrail.

---

## ADR-003 — Controlled Follow-Up Wording Only

**Status:** Accepted  
**Date:** 2026-07-07

### Context

Claims that require missing information or clarification may need follow-up questions. Free-form LLM-generated customer wording can introduce unsupported requests, inconsistent language, or privacy/safety risk.

### Decision

Customer follow-up questions are selected only from an approved follow-up question catalogue.

The workflow may select relevant question IDs, but it does not generate uncontrolled follow-up wording.

### Rationale

- Keeps customer communication controlled and auditable.
- Reduces risk of unsupported requests or unsafe wording.
- Allows follow-up selection to be evaluated against gold labels.

### Consequences

- Follow-up quality depends on catalogue coverage and selection rules.
- One development mismatch was observed where disposition and rule matched, but the selected follow-up question differed from the gold label.
- Future improvement should refine catalogue-selection rules rather than allowing free-form generation.

---

## ADR-004 — Guarded LangGraph Workflow

**Status:** Accepted  
**Date:** 2026-07-09

### Context

The capstone requires an agentic workflow. The workflow must coordinate deterministic tools, follow-up selection, optional RAG guidance, explanation proposal, and safety/authority guardrails.

### Decision

Use LangGraph for orchestration.

Current workflow version:

```text
langgraph_v6
```

Workflow nodes:

```text
deterministic_triage
→ controlled_follow_up_selection
→ controlled_rag_retrieval, optional
→ explanation_proposal
→ agent_content_safety_guardrail
→ response_guardrail
```

### Rationale

- Provides a clear graph-based workflow for agentic orchestration.
- Keeps deterministic and non-deterministic components separated.
- Allows optional RAG and reranking branches without changing the core deterministic path.
- Produces a workflow trace for evaluation and audit.

### Consequences

- LangGraph becomes the primary orchestration layer for the mid-submission baseline.
- Workflow evaluation can verify whether the final response preserves deterministic decisions.
- Optional RAG and reranking must remain side branches, not decision-authority paths.

---

## ADR-005 — Controlled Query Builder from Deterministic Facts

**Status:** Accepted  
**Date:** 2026-07-09

### Context

Runtime RAG retrieval should not use customer narrative, claim identifiers, device identifiers, document text, or arbitrary free text. Retrieval should be based only on safe, allow-listed deterministic facts.

### Decision

Build RAG queries from projected deterministic facts only.

The projection excludes:

- claim identifiers from the query text
- customer statements
- device identifiers
- policy identifiers
- document text
- decision reasons
- arbitrary rule-trace observed values

The controlled query includes fields such as:

- `triage_outcome`
- `triggering_rule_id`
- `claim_category`
- `requested_service_type`
- `coverage_lookup_status`
- `evidence_assessment_status`
- `missing_required_evidence_codes`
- `manual_review_reason_codes`

### Rationale

- Prevents prompt injection or customer narrative from influencing retrieval.
- Keeps RAG retrieval grounded in deterministic workflow facts.
- Makes retrieval reproducible and auditable through query fingerprints.

### Consequences

- Runtime RAG queries are less flexible than natural-language user queries.
- Retrieval may miss useful context if a relevant deterministic fact is not projected.
- Safety and auditability are prioritised over free-form retrieval flexibility.

---

## ADR-006 — Keep RAG Guidance Non-Authoritative and Analyst-Facing

**Status:** Accepted  
**Date:** 2026-07-09

### Context

The system uses deterministic policy rules for claim triage and a RAG layer for SOP / knowledge-base guidance. The project requires GenAI/RAG capability, but claim eligibility, evidence requirements, triggering rules, and customer-facing follow-up wording must remain controlled and auditable.

### Decision

RAG output is treated as non-authoritative analyst guidance only.

The RAG branch may retrieve and format approved SOP / KB references, but it cannot modify:

- `triage_outcome`
- `triggering_rule_id`
- `precedence_stage`
- evidence requirements
- policy eligibility
- controlled follow-up question wording
- protected final response fields

The LangGraph workflow stores RAG output separately as `analyst_guidance`. The protected `final_response` remains governed by deterministic triage and the response authority guardrail.

### Rationale

This design preserves the core business safety requirement: deterministic rules remain authoritative, while GenAI/RAG supports analyst understanding through traceable source references.

It also reduces risk from hallucination, prompt injection, and unsupported policy interpretation.

### Consequences

Positive:

- Clear separation between deterministic decisions and RAG support.
- Easier auditability and explainability.
- RAG can be evaluated independently.
- Retrieved SOP content can support analysts without changing claim routing.

Trade-off:

- RAG cannot improve deterministic decision accuracy directly.
- Any rule/data gap must be addressed in deterministic logic or structured runtime data, not by RAG.

---

## ADR-007 — Use Cross-Encoder Reranking as an Optional Controlled Stage

**Status:** Accepted  
**Date:** 2026-07-09

### Context

The rubric expects a reranking component in the RAG pipeline. The project already includes lexical, semantic, hybrid, and FAISS-based retrieval. A reranker was needed to demonstrate second-stage relevance scoring over retrieved candidates.

### Decision

A cross-encoder reranker is implemented as an optional controlled stage after first-stage semantic retrieval.

Model used for validation:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker only reorders retrieved approved KB chunks. It does not generate new policy advice and cannot alter deterministic claim decisions.

### Rationale

Cross-encoder reranking provides a stronger relevance-scoring mechanism than vector similarity alone because it evaluates query-document pairs jointly.

Keeping it optional avoids unnecessary runtime cost and preserves the ability to compare retrieval methods.

### Evaluation Result

The reranker was evaluated on the same frozen 14-query retrieval set.

| Method | Hit@1 | Hit@3 | MRR@3 |
|---|---:|---:|---:|
| Semantic Embedding | 78.6% | 92.9% | 0.857 |
| Semantic + Cross-Encoder Reranker | 78.6% | 92.9% | 0.845 |

The reranker matched semantic retrieval on Hit@1 and Hit@3, but produced slightly lower MRR@3 on the small evaluation set.

### Consequences

Positive:

- Satisfies the reranker requirement.
- Provides a controlled second-stage ranking mechanism.
- Can improve specific query families even if aggregate MRR is slightly lower.

Trade-off:

- Adds dependency on `sentence-transformers`.
- Adds runtime cost if enabled.
- Did not improve aggregate MRR@3 on the current small retrieval evaluation set.

---

## ADR-008 — Evaluate Workflow Separately from RAG

**Status:** Accepted  
**Date:** 2026-07-09

### Context

The system has two different evaluation concerns:

1. Retrieval quality for analyst-facing SOP guidance.
2. Correctness and safety of the end-to-end triage workflow.

Because RAG is non-authoritative, workflow evaluation should not allow RAG to influence deterministic triage outcomes.

### Decision

Workflow development evaluation is run with:

```text
enable_controlled_rag=False
```

Retrieval and reranking are evaluated separately in the RAG notebook and retrieval artifacts.

### Rationale

This separation ensures that workflow metrics measure deterministic routing, guardrail behavior, and controlled follow-up selection without mixing in non-authoritative RAG behavior.

### Evaluation Result

The guarded LangGraph workflow was evaluated on 165 labelled development claims.

Key results:

| Metric | Result |
|---|---:|
| Workflow completion rate | 100.0% |
| Disposition agreement | 91.5% |
| Primary rule acceptable agreement | 91.5% |
| Final response matches deterministic outcome | 100.0% |
| Final response matches deterministic rule | 100.0% |
| Authority guardrail aligned rate | 100.0% |
| Content safety SAFE rate | 100.0% |
| Follow-up exact match rate | 99.4% |

### Consequences

Positive:

- Clean attribution of errors.
- Confirms LangGraph does not corrupt deterministic decisions.
- Keeps RAG evaluation independent and auditable.

Trade-off:

- Workflow evaluation does not measure analyst usefulness of RAG guidance directly.
- RAG usefulness is represented through separate retrieval metrics and examples.

---

## ADR-009 — Use Direct Safety-Control Evaluation for Adversarial Cases

**Status:** Accepted  
**Date:** 2026-07-09

### Context

The safety/adversarial test cases use `SAFCLM-*` identifiers and separate tool fixtures. They are not normal runtime claim records.

Forcing these cases into normal runtime tables would add complexity and risk creating artificial data transformation logic only for tests.

### Decision

Safety/adversarial evaluation is performed directly on the safety-control layers:

```text
deterministic tool-result fixture
→ adversarial proposed agent content
→ agent content safety guardrail
→ response authority guardrail
→ protected final response
```

### Rationale

This directly tests the critical safety promise:

- deterministic outputs must be preserved
- unsafe overrides must be blocked
- prohibited mechanical behavior must not leak into final response

### Evaluation Result

The safety suite evaluated 24 adversarial cases.

| Metric | Result |
|---|---:|
| Critical safety pass rate | 100.0% |
| Deterministic outcome preservation rate | 100.0% |
| Deterministic rule preservation rate | 100.0% |
| Unsafe override block rate | 100.0% |
| Mechanical prohibited behavior rate | 0.0% |

### Consequences

Positive:

- Strong targeted guardrail evidence.
- Avoids distorting runtime data structures.
- Demonstrates protection against adversarial proposed content.

Trade-off:

- This is not a full semantic red-team evaluation.
- Broader human-reviewed adversarial evaluation can be added for final submission.