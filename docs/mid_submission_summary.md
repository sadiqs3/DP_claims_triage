# Mid Submission Summary

## 1. Project Title

**Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System**

---

## 2. Mid-Submission Objective

This submission represents **Version 1 baseline** of the capstone project.

The objective of this baseline is to demonstrate a functional, modular, and reproducible Agentic AI solution for device protection claim triage.

The system evaluates synthetic device protection claims using deterministic policy rules, controlled follow-up selection, a guarded LangGraph workflow, and a non-authoritative RAG layer for analyst-facing SOP guidance.

The solution is designed as **decision support only**. It does not approve claims, deny claims finally, determine fraud, or make payout decisions.

---

## 3. Business Problem

Device protection claim triage requires analysts to evaluate multiple structured sources:

- Policy eligibility
- Active coverage period
- Device match
- Plan and coverage rules
- Evidence sufficiency
- Claim-history limits
- Risk and manual-review indicators
- Operational SOP guidance

Manual review can become inconsistent when these checks are spread across different tables, rules, and documents.

This project addresses the problem by creating a traceable workflow that applies deterministic rules first and uses GenAI/RAG only for controlled analyst assistance.

---

## 4. Dataset Source and Licence

This project uses a synthetic, purpose-built dataset created for the BYOC capstone project.

The dataset represents device protection claim triage scenarios and includes synthetic policy, coverage, evidence, claim-history, risk, follow-up, and knowledge-base records.

No real customer data, production policy data, personal data, or proprietary enterprise records are used.

Dataset details:

- Source: Project-generated synthetic dataset
- Licence / usage: Academic capstone use within this repository
- PII status: No real PII included
- Purpose: Development and evaluation of the baseline claim-triage workflow

---

## 5. Current Build Status

The baseline end-to-end solution is implemented.

Completed components:

- Synthetic runtime data loading
- Deterministic triage rule engine
- Rule trace and decision precedence handling
- Controlled follow-up question selection
- LangGraph guarded workflow
- Agent content safety guardrail
- Response authority guardrail
- Approved KB / SOP corpus builder
- Lexical TF-IDF retriever
- Semantic embedding retriever
- Hybrid RRF retriever
- Persisted FAISS semantic index
- Controlled query builder from deterministic facts
- Controlled RAG retrieval tool
- Analyst guidance formatter
- Cross-encoder reranker
- Optional RAG and reranker branch in LangGraph
- Retrieval, workflow, and safety evaluation artifacts
- Unit test suite with 136 passing tests

---

## 6. Architecture Summary

High-level workflow:

```text
Claim Intake
  → Deterministic Triage
  → Controlled Follow-up Selection
  → Optional Controlled RAG Retrieval
  → Optional Cross-Encoder Reranking
  → Analyst Guidance Formatter
  → Agent Content Safety Guardrail
  → Response Authority Guardrail
  → Protected Final Response
```

Core design principle:

```text
Deterministic rules are authoritative.
RAG is non-authoritative and analyst-facing only.
```

---

## 7. Agentic AI and GenAI Components

The project includes the following Agentic AI / GenAI components.

### 7.1 LangGraph Orchestration

The workflow is orchestrated using LangGraph.

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

### 7.2 RAG Layer

The RAG layer retrieves approved SOP / knowledge-base guidance for analysts.

Implemented RAG components:

- Approved KB allow-list
- Chunked SOP / KB corpus
- Semantic embeddings
- FAISS persisted vector index
- Controlled query generation
- Cross-encoder reranking
- Source-grounded analyst guidance formatting

### 7.3 Prompt and Interaction Design

The project avoids uncontrolled customer-facing generation.

Instead, interaction design is implemented through controlled components:

- Deterministic fact projection for RAG queries
- Controlled query builder using allow-listed fields
- Approved follow-up question catalogue
- Analyst guidance formatter with source references
- Agent content safety guardrail
- Response authority guardrail

Customer narrative, identifiers, and arbitrary free text are not used for uncontrolled RAG retrieval.

### 7.4 Guardrails

Implemented guardrails:

- Agent content safety guardrail
- Response authority guardrail
- Controlled follow-up catalogue
- RAG authority boundary
- Decision-support-only response boundary

---

## 8. Dataset Summary

Runtime data includes:

- Plan master
- Coverage matrix
- Evidence requirements
- Policy rule catalog
- Policy eligibility lookup
- Prior claims history
- Evidence bundles
- Evidence document metadata
- Risk indicator results
- Follow-up question catalogue
- Knowledge-base document registry
- Development claim intake records

Key dataset counts:

| Area | Count |
|---|---:|
| Development claims | 165 |
| Evidence bundles | 220 |
| Knowledge-base documents | 7 |
| Safety/adversarial cases | 24 |

---

## 9. Evaluation Summary

Detailed evaluation evidence is available in:

```text
docs/evaluation_summary.md
```

### 9.1 Retrieval Evaluation

The retrieval layer was evaluated on a frozen 14-query retrieval evaluation set.

| Method | Hit@1 | Hit@3 | MRR@3 | No Result Rate |
|---|---:|---:|---:|---:|
| Lexical TF-IDF | 57.1% | 85.7% | 0.702 | 0.0% |
| Semantic Embedding | 78.6% | 92.9% | 0.857 | 0.0% |
| Hybrid RRF | 71.4% | 92.9% | 0.798 | 0.0% |
| Semantic + Cross-Encoder Reranker | 78.6% | 92.9% | 0.845 | 0.0% |

Interpretation:

- Semantic retrieval is the strongest baseline by MRR@3.
- Cross-encoder reranking was implemented and evaluated.
- The reranker matched semantic retrieval on Hit@1 and Hit@3, with slightly lower MRR@3 on the small evaluation set.
- Reranking remains optional and non-authoritative.

---

### 9.2 Workflow Development Evaluation

The guarded LangGraph workflow was evaluated on 165 labelled development claims.

| Metric | Result |
|---|---:|
| Workflow completion rate | 100.0% |
| Disposition agreement | 91.5% |
| Primary rule exact agreement | 89.1% |
| Primary rule acceptable agreement | 91.5% |
| Final response matches deterministic outcome | 100.0% |
| Final response matches deterministic rule | 100.0% |
| Authority guardrail aligned rate | 100.0% |
| Content safety SAFE rate | 100.0% |
| Follow-up exact match rate | 99.4% |

Interpretation:

- The workflow completed for all development claims.
- The final response preserved deterministic decisions in every case.
- Remaining label mismatches are deterministic rule/data gaps, not LangGraph or RAG failures.

---

### 9.3 Safety and Adversarial Evaluation

The safety guardrails were evaluated on 24 adversarial cases.

| Metric | Result |
|---|---:|
| Critical safety pass rate | 100.0% |
| Deterministic outcome preservation rate | 100.0% |
| Deterministic rule preservation rate | 100.0% |
| Unsafe override block rate | 100.0% |
| Mechanical prohibited behavior rate | 0.0% |

Interpretation:

- All adversarial cases passed the critical safety gate.
- Unsafe override attempts were blocked.
- Deterministic decision fields were preserved.
- Content safety fallback and response guardrail controls worked as expected.

---

## 10. Repository Evidence

Key reviewer entry points:

- `README.md`
- `docs/evaluation_summary.md`
- `docs/architecture_decisions.md`
- `docs/mid_submission_checklist.md`
- `notebooks/05_sop_rag_retrieval.ipynb`
- `notebooks/06_workflow_evaluation.ipynb`

Generated artifacts:

```text
data/artifacts/rag/faiss_semantic_index_v1/
data/evaluation/retrieval/
data/evaluation/workflow/
data/evaluation/safety/
```

---

## 11. Rubric Alignment

| Expected Area | Repository Evidence |
|---|---|
| Business problem definition | `README.md`, `docs/mid_submission_summary.md` |
| Project objective | `README.md`, `docs/mid_submission_summary.md` |
| GenAI / Agentic AI implementation | LangGraph workflow in `src/agent/`, controlled RAG in `src/rag/` |
| Data collection and preparation | Synthetic dataset under `data/`, data-loading and validation modules in `src/` |
| Knowledge/context preparation | Approved KB corpus, corpus builder, FAISS index, retrieval notebook |
| Baseline workflow | LangGraph workflow, deterministic tools, guarded response path |
| Prompt / interaction design | Controlled query builder, analyst guidance formatter, follow-up catalogue, guardrails |
| Initial system evaluation | `docs/evaluation_summary.md`, `data/evaluation/` |
| Modular implementation | `src/`, `tests/`, `notebooks/`, `docs/`, `data/` |
| Proposed architecture | `docs/architecture_decisions.md`, architecture overview in README |
| Planned final enhancements | README and this summary |
| Reproducibility | `requirements.txt`, notebooks, tests, generated evaluation artifacts |

---

## 12. Reproducibility

Run the full regression suite from the project root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Current expected result:

```text
136 tests passed
```

Live semantic retrieval and embedding-based evaluation require a local `.env` file containing:

```text
OPENAI_API_KEY=<your_key_here>
```

The `.env` file is excluded from Git and must not be committed.

---

## 13. Known Limitations and Final Submission Plan

The current mid-submission baseline is intentionally scoped as a working, tested, and evaluated foundation.

### 13.1 Known Limitations

1. **Held-out evaluation is reserved for final submission.**  
   Development evaluation has been completed on labelled development claims. Held-out labels are intentionally not used at this stage to preserve a clean final evaluation boundary.

2. **Some exclusion-rule scenarios depend on structured runtime data availability.**  
   The current runtime package does not include a separate structured exclusion-status dataset. As a result, exclusion-related gaps are documented rather than handled through unsupported assumptions.

3. **Reranker evaluation is based on a small frozen retrieval set.**  
   The cross-encoder reranker was implemented and evaluated on the current 14-query retrieval set. It matched semantic retrieval on Hit@1 and Hit@3, with slightly lower MRR@3.

4. **Workflow mismatches are primarily deterministic rule/data gaps.**  
   The LangGraph workflow and guardrails preserved deterministic outputs correctly. Remaining mismatches are linked to deterministic rule coverage, precedence handling, or available structured data.

5. **Safety evaluation focuses on critical control preservation.**  
   The safety/adversarial suite validates deterministic preservation, unsafe override blocking, and prohibited-behavior leakage. Broader semantic red-team review can be expanded during final packaging if required.

### 13.2 Planned Final Submission Enhancements

The following items are planned before final submission:

1. **Run locked held-out evaluation.**  
   Evaluate the final workflow on the held-out claim set and report final generalisation performance separately from development results.

2. **Review development mismatch analysis.**  
   Review deterministic mismatches and make only justified rule/data refinements that do not overfit to development labels.

3. **Refresh evaluation artifacts if logic changes.**  
   If deterministic logic is updated, retrieval, workflow, and safety artifacts will be regenerated as needed to keep documentation aligned with code.

4. **Prepare final report.**  
   Create the final capstone report covering business problem, architecture, dataset, implementation, evaluation, safety controls, limitations, and conclusion.

5. **Prepare final presentation.**  
   Create the final presentation deck summarising the problem, solution, architecture, demo flow, evaluation metrics, and business value.

6. **Add concise demo walkthrough.**  
   Add a short reviewer-friendly walkthrough showing how a sample claim moves through deterministic triage, controlled follow-up, optional RAG guidance, and guardrails.

7. **Complete final repository hygiene.**  
   Re-run tests, confirm GitHub links, verify no secrets/local cache files are tracked, and ensure final documentation is aligned with the submitted code.

---

## 14. Mid Submission Conclusion

The project has reached a strong mid-submission baseline.

The core end-to-end workflow is implemented, tested, and evaluated. The solution demonstrates deterministic rule-grounding, LangGraph orchestration, controlled RAG, FAISS retrieval, cross-encoder reranking, analyst guidance formatting, and safety guardrails.

The repository is ready for mid-submission review as a working Version 1 baseline implementation with documented evaluation evidence and a clear final-submission plan.