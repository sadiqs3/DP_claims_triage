# Device Protection Claims Triage

## Rule-Grounded Agentic AI Decision-Support System

This project implements a controlled Agentic AI workflow for device protection claim triage.

The system evaluates synthetic device protection claims using deterministic policy rules, controlled follow-up question selection, a guarded LangGraph workflow, and a non-authoritative RAG layer for analyst-facing SOP guidance.

The project is built as a decision-support system. It does **not** approve claims, deny claims finally, determine fraud, or make payout decisions.

---

## 1. Business Problem

Device protection claims often require consistent triage across policy eligibility, device match, coverage rules, evidence sufficiency, claim-history checks, and manual-review signals.

Manual triage can be inconsistent when analysts must interpret multiple structured sources and operational SOPs under time pressure.

This project addresses the problem by building a rule-grounded Agentic AI workflow that:

- Applies deterministic policy and eligibility rules.
- Selects approved follow-up questions when information is missing.
- Provides source-grounded analyst guidance from approved SOP / KB documents.
- Preserves human control and deterministic authority.
- Blocks unsafe or unsupported agent-generated content.

---

## 2. Solution Overview

The solution combines deterministic rules, LangGraph orchestration, controlled RAG, and guardrails.

High-level flow:

```text
Claim Intake
  → Deterministic Triage Tools
  → Controlled Follow-up Selection
  → Optional Controlled RAG Retrieval
  → Optional Cross-Encoder Reranking
  → Analyst Guidance Formatter
  → Agent Content Safety Guardrail
  → Response Authority Guardrail
  → Protected Final Response
```

Key principle:

```text
Deterministic rules are authoritative.
RAG is non-authoritative and analyst-facing only.
```

---

## 3. Core Components

### 3.1 Deterministic Triage

The deterministic workflow evaluates claims using structured runtime data:

- Policy lookup
- Policy active-date eligibility
- Plan configuration
- Product scope
- Device match
- Coverage lookup
- Evidence assessment
- Claim-history checks
- Risk/manual-review signals
- Decision precedence

The deterministic output includes:

- `triage_outcome`
- `triggering_rule_id`
- `precedence_stage`
- `decision_reason`
- `rule_trace`
- `decision_support_only`

---

### 3.2 Controlled Follow-up Selection

When a claim requires more information, follow-up questions are selected only from an approved catalogue.

The system does not allow free-form generation of customer follow-up questions.

---

### 3.3 LangGraph Guarded Workflow

The project uses LangGraph to orchestrate the guarded claim-triage workflow.

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

---

### 3.4 Controlled RAG Retrieval

The RAG layer retrieves approved SOP / KB guidance for analysts.

Important boundary:

```text
RAG does not change claim routing, eligibility, evidence requirements, triggering rule, or final response.
```

RAG uses:

- Approved KB corpus
- Controlled query builder
- OpenAI semantic embeddings
- FAISS persisted vector index
- Cross-encoder reranker, optional
- Analyst guidance formatter

---

### 3.5 Cross-Encoder Reranker

A cross-encoder reranker was implemented and evaluated as an optional reranking stage.

Model used:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker reorders retrieved KB chunks only. It does not generate policy advice or modify deterministic decisions.

---

### 3.6 Guardrails

Two key guardrails are implemented:

1. **Agent Content Safety Guardrail**
   - Blocks or normalizes unsafe proposed content.
   - Applies fallback content when needed.

2. **Response Authority Guardrail**
   - Preserves deterministic triage fields.
   - Blocks unauthorized overrides from agent-generated content.
   - Ensures final response remains decision-support only.

---

## 4. Repository Structure

```text
DP_claims_triage/
├── data/
│   ├── artifacts/
│   │   └── rag/
│   │       └── faiss_semantic_index_v1/
│   ├── evaluation/
│   │   ├── retrieval/
│   │   ├── workflow/
│   │   └── safety/
│   ├── knowledge_base/
│   └── runtime/
├── docs/
│   ├── architecture_decisions.md
│   ├── evaluation_summary.md
│   └── mid_submission_summary.md
├── notebooks/
│   ├── 05_sop_rag_retrieval.ipynb
│   └── 06_workflow_evaluation.ipynb
├── src/
│   ├── agent/
│   ├── rag/
│   └── tools/
├── tests/
├── requirements.txt
└── README.md
```

---

## 5. Setup Instructions

### 5.1 Create and activate environment

Example using conda:

```bash
conda create -n dpclaims python=3.11
conda activate dpclaims
```

### 5.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 5.3 Configure environment variables

For live semantic embedding evaluation, create a local `.env` file with:

```text
OPENAI_API_KEY=<your_key_here>
```

Do not commit `.env`.

The project can run many deterministic tests without an OpenAI key. Live semantic retrieval/evaluation requires the key.

---

## 6. How to Run Tests

Run the full test suite from the project root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Current regression status:

```text
136 tests passed
```

---

## 7. How to Run Key Notebooks

### 7.1 RAG Retrieval and Reranking

Notebook:

```text
notebooks/05_sop_rag_retrieval.ipynb
```

Purpose:

- Build approved KB corpus
- Evaluate lexical, semantic, and hybrid retrieval
- Persist FAISS semantic index
- Validate controlled RAG retrieval
- Validate analyst guidance formatting
- Validate fake and real cross-encoder reranking
- Save retrieval evaluation artifacts

### 7.2 Workflow and Safety Evaluation

Notebook:

```text
notebooks/06_workflow_evaluation.ipynb
```

Purpose:

- Evaluate guarded LangGraph workflow on labelled development claims
- Compare workflow outputs against development labels
- Analyse mismatches
- Evaluate safety/adversarial guardrails
- Save workflow and safety evaluation artifacts

---

## 8. Evaluation Summary

Detailed evaluation evidence is available in:

```text
docs/evaluation_summary.md
```

### 8.1 Retrieval Evaluation

Frozen retrieval evaluation set:

```text
14 queries
```

| Method | Hit@1 | Hit@3 | MRR@3 | No Result Rate |
|---|---:|---:|---:|---:|
| Lexical TF-IDF | 57.1% | 85.7% | 0.702 | 0.0% |
| Semantic Embedding | 78.6% | 92.9% | 0.857 | 0.0% |
| Hybrid RRF | 71.4% | 92.9% | 0.798 | 0.0% |
| Semantic + Cross-Encoder Reranker | 78.6% | 92.9% | 0.845 | 0.0% |

### 8.2 Workflow Development Evaluation

Development claims evaluated:

```text
165
```

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

### 8.3 Safety and Adversarial Evaluation

Adversarial test cases evaluated:

```text
24
```

| Metric | Result |
|---|---:|
| Critical safety pass rate | 100.0% |
| Deterministic outcome preservation rate | 100.0% |
| Deterministic rule preservation rate | 100.0% |
| Unsafe override block rate | 100.0% |
| Mechanical prohibited behavior rate | 0.0% |

---

## 9. Generated Evaluation Artifacts

### 9.1 Retrieval

```text
data/evaluation/retrieval/retrieval_summary_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_family_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_per_query_results_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_evaluation_with_reranker_manifest_v1.json
```

### 9.2 Workflow

```text
data/evaluation/workflow/workflow_development_summary_metrics_v1.csv
data/evaluation/workflow/workflow_development_per_claim_results_v1.csv
data/evaluation/workflow/workflow_development_mismatch_analysis_v1.csv
data/evaluation/workflow/workflow_development_evaluation_manifest_v1.json
```

### 9.3 Safety

```text
data/evaluation/safety/safety_adversarial_summary_metrics_v1.csv
data/evaluation/safety/safety_adversarial_per_case_results_v1.csv
data/evaluation/safety/safety_adversarial_evaluation_manifest_v1.json
```

---

## 10. Reviewer Guide

For a quick review, start with:

1. [Mid Submission Summary](docs/mid_submission_summary.md)
2. [Evaluation Summary](docs/evaluation_summary.md)
3. [Architecture Decisions](docs/architecture_decisions.md)
4. [RAG Retrieval Notebook](notebooks/05_sop_rag_retrieval.ipynb)
5. [Workflow Evaluation Notebook](notebooks/06_workflow_evaluation.ipynb)

Suggested validation command:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 11. Safety and Scope Boundaries

The system does not:

- Approve claims
- Deny claims finally
- Determine fraud
- Make payout decisions
- Override policy eligibility
- Generate uncontrolled customer follow-up wording
- Use RAG to change deterministic decisions

The system does:

- Provide deterministic decision-support recommendations
- Select approved follow-up questions
- Retrieve approved SOP guidance for analysts
- Preserve deterministic authority in the final response
- Block unsafe agent-generated overrides

---

## 12. Known Limitations

1. Held-out evaluation labels are not used in the development evaluation.
2. Some exclusion-related rules are limited because the runtime package does not include a structured exclusion-status dataset.
3. Cross-encoder reranking was evaluated on a small 14-query retrieval set. It matched Hit@1 and Hit@3 but did not improve aggregate MRR@3.
4. Workflow label mismatches are primarily deterministic rule/data issues, not LangGraph or RAG failures.
5. Safety evaluation checks deterministic preservation, override blocking, and mechanical prohibited-behavior leakage. Broader semantic safety assessment may require additional human review.

---

## 13. Current Status

Current mid-submission status:

```text
Baseline end-to-end solution implemented.
LangGraph workflow integrated.
Controlled RAG and reranker implemented.
Evaluation artifacts generated.
Safety/adversarial tests completed.
136 unit tests passing.
```

The project is ready for mid-submission packaging, subject to final documentation review and repository hygiene checks.