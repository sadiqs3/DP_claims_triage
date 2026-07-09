# Mid Submission Summary

## 1. Project Title

**Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System**

---

## 2. Project Objective

This capstone project builds a controlled Agentic AI workflow to support device protection claim triage.

The system helps evaluate synthetic device protection claims using deterministic policy rules, controlled follow-up selection, a guarded LangGraph workflow, and a non-authoritative RAG layer for analyst-facing SOP guidance.

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

## 4. Current Build Status

The baseline end-to-end solution is implemented.

Completed components:

- Synthetic runtime data loading
- Deterministic triage rule engine
- Rule trace and decision precedence handling
- Controlled follow-up question selection
- LangGraph guarded workflow
- Agent content safety guardrail
- Response authority guardrail
- Approved KB/SOP corpus builder
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

## 5. Architecture Summary

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

## 6. Agentic AI and GenAI Components

The project includes the following Agentic AI / GenAI components:

### 6.1 LangGraph Orchestration

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

### 6.2 RAG Layer

The RAG layer retrieves approved SOP / knowledge-base guidance for analysts.

Implemented RAG components:

- Approved KB allow-list
- Chunked SOP / KB corpus
- Semantic embeddings
- FAISS persisted vector index
- Controlled query generation
- Cross-encoder reranking
- Source-grounded analyst guidance formatting

### 6.3 Guardrails

Implemented guardrails:

- Agent content safety guardrail
- Response authority guardrail
- Controlled follow-up catalogue
- RAG authority boundary
- Decision-support-only response boundary

---

## 7. Dataset Summary

The project uses synthetic, purpose-built device protection claims data.

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

Development claims:

```text
165
```

Evidence bundles:

```text
220
```

Knowledge-base documents:

```text
7
```

Safety/adversarial cases:

```text
24
```

---

## 8. Evaluation Summary

Detailed evaluation evidence is available in:

```text
docs/evaluation_summary.md
```

### 8.1 Retrieval Evaluation

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

### 8.2 Workflow Development Evaluation

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

### 8.3 Safety and Adversarial Evaluation

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

## 9. Current Test Status

Full regression command:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Current status:

```text
136 tests passed
```

---

## 10. Generated Artifacts

### 10.1 RAG / Retrieval

```text
data/artifacts/rag/faiss_semantic_index_v1/
data/evaluation/retrieval/
```

### 10.2 Workflow Evaluation

```text
data/evaluation/workflow/
```

### 10.3 Safety Evaluation

```text
data/evaluation/safety/
```

### 10.4 Documentation

```text
README.md
docs/architecture_decisions.md
docs/evaluation_summary.md
docs/mid_submission_summary.md
```

### 10.5 Notebooks

```text
notebooks/05_sop_rag_retrieval.ipynb
notebooks/06_workflow_evaluation.ipynb
```

---

## 11. Known Limitations

1. Held-out labels have not been used in development evaluation.
2. Some exclusion-related rules are limited because the runtime package does not include a structured exclusion-status dataset.
3. Cross-encoder reranking was evaluated on a small retrieval evaluation set.
4. Development-label mismatches are mostly deterministic rule/data issues, not orchestration failures.
5. Safety evaluation focuses on deterministic preservation, override blocking, and mechanical prohibited-behavior leakage. Broader semantic safety review can be expanded in the final submission.

---

## 12. Remaining Work for Final Submission

Planned next steps:

- Run held-out evaluation at final stage.
- Refine deterministic rule gaps based on development mismatch analysis, without overfitting.
- Add final report and presentation slides.
- Add a concise demo walkthrough.
- Improve documentation for reproducibility and final packaging.
- Optionally expand human-reviewed qualitative examples.

---

## 13. Mid Submission Conclusion

The project has reached a strong mid-submission baseline.

The core end-to-end workflow is implemented, tested, and evaluated. The solution demonstrates deterministic rule-grounding, LangGraph orchestration, controlled RAG, FAISS retrieval, cross-encoder reranking, analyst guidance formatting, and safety guardrails.

The system is ready for mid-submission review as a working baseline implementation with documented evaluation evidence.