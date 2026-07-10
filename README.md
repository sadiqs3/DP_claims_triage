# Device Protection Claims Triage

## Rule-Grounded Agentic AI Decision-Support System

This project implements a controlled Agentic AI workflow for device protection claim triage.

The system evaluates synthetic device protection claims using deterministic policy rules, controlled follow-up question selection, a guarded LangGraph workflow, and a non-authoritative RAG layer for analyst-facing SOP guidance.

The project is built as a **decision-support system**. It does **not** approve claims, deny claims finally, determine fraud, or make payout decisions.

---

## Executive Snapshot

This repository contains a working mid-submission baseline for a rule-grounded Agentic AI claim-triage system.

Current status:

- End-to-end LangGraph workflow implemented.
- Deterministic policy triage engine implemented.
- Controlled follow-up selection implemented.
- Controlled RAG over approved SOP / KB documents implemented.
- FAISS persisted semantic index implemented.
- Cross-encoder reranker implemented and evaluated.
- Analyst guidance formatter implemented.
- Agent content safety and response authority guardrails implemented.
- Retrieval, workflow, and safety evaluations completed.
- Full regression suite passing with 136 tests.

Core design principle:

```text
Deterministic rules are authoritative.
RAG is non-authoritative and analyst-facing only.
```

---

## 1. Business Problem

Device protection claims often require consistent triage across policy eligibility, coverage status, device match, evidence sufficiency, claim-history limits, and manual-review signals.

Manual triage can become inconsistent when analysts must interpret multiple structured sources and operational SOPs under time pressure.

This project addresses the problem by building a rule-grounded Agentic AI workflow that:

- Applies deterministic policy and eligibility rules.
- Selects approved follow-up questions when information is missing.
- Provides source-grounded analyst guidance from approved SOP / KB documents.
- Preserves human control and deterministic authority.
- Blocks unsafe or unsupported agent-generated content.

---

## 2. Business Objective

The objective is to build a functional Version 1 baseline of an Agentic AI decision-support workflow for device protection claim triage.

The baseline should demonstrate:

- Modular implementation.
- Deterministic rule-grounded triage.
- Appropriate use of GenAI / RAG.
- Controlled information retrieval from approved knowledge sources.
- Guarded response generation.
- Initial evaluation across retrieval, workflow, and safety dimensions.
- Clear documentation and reproducibility for reviewers.

---

## 3. Solution Overview

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

The deterministic triage layer produces the authoritative claim-routing output. The RAG layer retrieves approved SOP / KB guidance for analyst support only.

---

## 4. Dataset Source and Licence

This project uses a synthetic, purpose-built dataset created for the BYOC capstone project.

The dataset represents device protection claim triage scenarios and includes synthetic policy, coverage, evidence, claim-history, risk, follow-up, and knowledge-base records.

No real customer data, production policy data, personal data, or proprietary enterprise records are used.

Dataset details:

- Source: Project-generated synthetic dataset.
- Licence / usage: Academic capstone use within this repository.
- PII status: No real PII included.
- Purpose: Development and evaluation of the baseline claim-triage workflow.

Primary included data areas:

- Runtime reference data.
- Synthetic claim intake records.
- Evidence bundle metadata.
- Prior claim-history records.
- Risk indicator outputs.
- Follow-up question catalogue.
- SOP / knowledge-base documents.
- Development labels for evaluation.
- Safety/adversarial evaluation cases.

---

## 5. Core Components

### 5.1 Deterministic Triage

The deterministic workflow evaluates claims using structured runtime data:

- Policy lookup.
- Policy active-date eligibility.
- Plan configuration.
- Product scope.
- Device match.
- Coverage lookup.
- Evidence assessment.
- Claim-history checks.
- Risk/manual-review signals.
- Decision precedence.

The deterministic output includes:

- `triage_outcome`
- `triggering_rule_id`
- `precedence_stage`
- `decision_reason`
- `rule_trace`
- `decision_support_only`
- `system_limitations`

---

### 5.2 Controlled Follow-up Selection

When a claim requires more information, follow-up questions are selected only from an approved catalogue.

The system does not allow free-form generation of customer follow-up questions.

---

### 5.3 LangGraph Guarded Workflow

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

### 5.4 Controlled RAG Retrieval

The RAG layer retrieves approved SOP / KB guidance for analysts.

Important boundary:

```text
RAG does not change claim routing, eligibility, evidence requirements, triggering rule, or final response.
```

RAG uses:

- Approved KB corpus.
- Controlled query builder.
- OpenAI semantic embeddings.
- FAISS persisted vector index.
- Cross-encoder reranker, optional.
- Analyst guidance formatter.

---

### 5.5 Prompt and Interaction Design

The project avoids uncontrolled customer-facing generation.

Instead, interaction design is implemented through controlled components:

- Deterministic fact projection for RAG queries.
- Controlled query builder using allow-listed fields.
- Approved follow-up question catalogue.
- Analyst guidance formatter with source references.
- Agent content safety guardrail.
- Response authority guardrail.

Customer narrative, identifiers, and arbitrary free text are not used for uncontrolled RAG retrieval.

---

### 5.6 Cross-Encoder Reranker

A cross-encoder reranker was implemented and evaluated as an optional reranking stage.

Model used:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker reorders retrieved KB chunks only. It does not generate policy advice or modify deterministic decisions.

---

### 5.7 Guardrails

Two key guardrails are implemented:

1. **Agent Content Safety Guardrail**
   - Blocks or normalizes unsafe proposed content.
   - Applies fallback content when needed.

2. **Response Authority Guardrail**
   - Preserves deterministic triage fields.
   - Blocks unauthorized overrides from agent-generated content.
   - Ensures final response remains decision-support only.

---

## 6. Repository Structure

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
│   ├── mid_submission_checklist.md
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

## 7. Setup Instructions

### 7.1 Create and activate environment

Example using conda:

```bash
conda create -n dpclaims python=3.11
conda activate dpclaims
```

### 7.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 7.3 Configure environment variables

For live semantic embedding evaluation, create a local `.env` file.

An example file is provided:

```text
.env.example
```

Create your local `.env` file from the example:

```bash
cp .env.example .env
```

Then update `.env` with your OpenAI API key:

```text
OPENAI_API_KEY=<your_key_here>
```

Do not commit `.env`. The actual `.env` file is intentionally excluded from Git.

---

## 8. Execution Modes

The project supports two execution modes.

### Mode 1: Deterministic workflow and unit tests

This mode does not require an OpenAI API key.

Run from the project root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Current expected result:

```text
136 tests passed
```

### Mode 2: Live semantic retrieval / embedding evaluation

Live semantic retrieval uses OpenAI `text-embedding-3-small` embeddings and requires an API key in a local `.env` file.

```text
OPENAI_API_KEY=<your_key_here>
```

The `.env` file is intentionally excluded from Git and must not be committed.

---

## 9. Key Notebooks

### 9.1 RAG Retrieval and Reranking

Notebook:

```text
notebooks/05_sop_rag_retrieval.ipynb
```

Purpose:

- Build approved KB corpus.
- Evaluate lexical, semantic, and hybrid retrieval.
- Persist FAISS semantic index.
- Validate controlled RAG retrieval.
- Validate analyst guidance formatting.
- Validate fake and real cross-encoder reranking.
- Save retrieval evaluation artifacts.

---

### 9.2 Workflow and Safety Evaluation

Notebook:

```text
notebooks/06_workflow_evaluation.ipynb
```

Purpose:

- Evaluate guarded LangGraph workflow on labelled development claims.
- Compare workflow outputs against development labels.
- Analyse mismatches.
- Evaluate safety/adversarial guardrails.
- Save workflow and safety evaluation artifacts.

---

## 10. Evaluation Summary

Detailed evaluation evidence is available in:

```text
docs/evaluation_summary.md
```

### 10.1 Retrieval Evaluation

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

### 10.2 Workflow Development Evaluation

Development claims evaluated:

```text
165
```

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

### 10.3 Safety and Adversarial Evaluation

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
| Planned final enhancements | `docs/mid_submission_summary.md`, README limitation/final plan section |
| Reproducibility | `requirements.txt`, notebooks, tests, generated evaluation artifacts |

---

## 12. Generated Evaluation Artifacts

### 12.1 Retrieval

```text
data/evaluation/retrieval/retrieval_summary_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_family_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_per_query_results_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_evaluation_with_reranker_manifest_v1.json
```

### 12.2 Workflow

```text
data/evaluation/workflow/workflow_development_summary_metrics_v1.csv
data/evaluation/workflow/workflow_development_per_claim_results_v1.csv
data/evaluation/workflow/workflow_development_mismatch_analysis_v1.csv
data/evaluation/workflow/workflow_development_evaluation_manifest_v1.json
```

### 12.3 Safety

```text
data/evaluation/safety/safety_adversarial_summary_metrics_v1.csv
data/evaluation/safety/safety_adversarial_per_case_results_v1.csv
data/evaluation/safety/safety_adversarial_evaluation_manifest_v1.json
```

---

## 13. Reviewer Guide

For a quick review, start with:

1. [Mid Submission Summary](docs/mid_submission_summary.md)
2. [Evaluation Summary](docs/evaluation_summary.md)
3. [Architecture Decisions](docs/architecture_decisions.md)
4. [Mid Submission Checklist](docs/mid_submission_checklist.md)
5. [RAG Retrieval Notebook](notebooks/05_sop_rag_retrieval.ipynb)
6. [Workflow Evaluation Notebook](notebooks/06_workflow_evaluation.ipynb)

Suggested validation command:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 14. Safety and Scope Boundaries

The system does not:

- Approve claims.
- Deny claims finally.
- Determine fraud.
- Make payout decisions.
- Override policy eligibility.
- Generate uncontrolled customer follow-up wording.
- Use RAG to change deterministic decisions.

The system does:

- Provide deterministic decision-support recommendations.
- Select approved follow-up questions.
- Retrieve approved SOP guidance for analysts.
- Preserve deterministic authority in the final response.
- Block unsafe agent-generated overrides.

---

## 15. Intentionally Out of Scope for Mid Submission

The following items are intentionally outside the mid-submission baseline:

- Production deployment.
- User interface.
- Automated claim approval.
- Automated payout decisioning.
- Fraud determination.
- Live integration with enterprise policy systems.
- Use of customer narrative for uncontrolled RAG retrieval.
- Final held-out evaluation.

These are excluded to keep the project aligned with the approved BYOC scope, decision-support boundary, and 30–40 hour capstone effort.

---

## 16. Known Limitations and Final Submission Plan

The current mid-submission baseline is intentionally scoped as a working, tested, and evaluated foundation. The following limitations are known and will be addressed or expanded as part of final submission preparation.

### 16.1 Known Limitations

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

### 16.2 Planned Final Submission Enhancements

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

## 17. Current Mid-Submission Status

Current status:

```text
Baseline end-to-end solution implemented.
LangGraph workflow integrated.
Controlled RAG and reranker implemented.
Evaluation artifacts generated.
Safety/adversarial tests completed.
136 unit tests passing.
```

The project is ready for mid-submission packaging, subject to final GitHub push and repository access verification.