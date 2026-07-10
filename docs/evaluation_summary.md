# Evaluation Summary

## 1. Purpose

This document summarises the mid-submission evaluation evidence for the Device Protection Claims Triage project.

The evaluation covers three areas:

1. Retrieval quality for the approved SOP / knowledge-base RAG layer.
2. End-to-end guarded LangGraph workflow behaviour on labelled development claims.
3. Safety and adversarial guardrail behaviour.

The project is intentionally designed as a rule-grounded decision-support system. Deterministic triage rules are authoritative. RAG is non-authoritative and analyst-facing only.

---

## 2. Evaluation Objective

The evaluation is designed to answer three questions:

1. Can the RAG layer retrieve relevant approved SOP / KB guidance?
2. Can the LangGraph workflow complete claim triage while preserving deterministic authority?
3. Can the guardrails block unsafe or unauthorized agent-generated overrides?

Because RAG is non-authoritative, retrieval evaluation and workflow evaluation are reported separately.

---

## 3. Evaluation Scope

### 3.1 Included in Mid-Submission Evaluation

The current evaluation includes:

- Retrieval evaluation on a frozen retrieval query set.
- Lexical TF-IDF retrieval.
- Semantic embedding retrieval.
- Hybrid RRF retrieval.
- Semantic retrieval with cross-encoder reranking.
- Guarded LangGraph workflow evaluation on labelled development claims.
- Follow-up question selection evaluation.
- Response authority preservation checks.
- Agent content safety checks.
- Safety/adversarial evaluation using tool-result fixtures.

### 3.2 Excluded from Mid-Submission Evaluation

The current evaluation excludes:

- Final held-out evaluation.
- Production deployment testing.
- UI testing.
- Real customer data testing.
- Automated claim approval or payout decisioning.
- Fraud determination.
- Live enterprise system integration.

Held-out evaluation is intentionally reserved for the final submission stage.

---

## 4. Metric Definitions

| Metric | Meaning |
|---|---|
| Hit@1 | Whether the expected relevant document/chunk appears as the top retrieved result |
| Hit@3 | Whether the expected relevant document/chunk appears within the top 3 retrieved results |
| MRR@3 | Mean reciprocal rank of the expected relevant result within the top 3 |
| No result rate | Percentage of queries where the retriever returned no results |
| Workflow completion rate | Percentage of claims processed without workflow failure |
| Disposition agreement | Match rate between predicted and gold claim disposition |
| Primary rule exact agreement | Exact match rate between predicted and gold primary rule |
| Primary rule acceptable agreement | Match rate allowing gold-approved alternate primary rules |
| Final response matches deterministic outcome | Whether protected final response preserved the deterministic triage outcome |
| Final response matches deterministic rule | Whether protected final response preserved the deterministic triggering rule |
| Authority guardrail aligned rate | Percentage of workflow cases where the response authority guardrail preserved deterministic authority |
| Follow-up exact match rate | Exact match rate for selected follow-up question IDs |
| Critical safety pass rate | Percentage of adversarial cases passing the critical safety gate |
| Unsafe override block rate | Percentage of adversarial override attempts blocked |
| Mechanical prohibited behavior rate | Percentage of cases where prohibited mechanical behavior leaked into output |

---

## 5. Evaluation Acceptance Summary

| Area | Acceptance Target | Actual Result | Status |
|---|---:|---:|---|
| Workflow completion | 100% | 100.0% | Met |
| Final response preserves deterministic outcome | 100% | 100.0% | Met |
| Final response preserves deterministic rule | 100% | 100.0% | Met |
| Authority guardrail alignment | 100% | 100.0% | Met |
| Safety critical pass rate | 100% | 100.0% | Met |
| Unsafe override blocking | 100% | 100.0% | Met |
| Mechanical prohibited behavior leakage | 0% | 0.0% | Met |
| Retrieval no-result rate | 0% preferred | 0.0% | Met |
| Semantic retrieval Hit@3 | Strong baseline expected | 92.9% | Met |

---

## 6. Retrieval Evaluation

### 6.1 Retrieval Methods Evaluated

The retrieval evaluation compared four methods:

1. Lexical TF-IDF retrieval.
2. Semantic embedding retrieval.
3. Hybrid Reciprocal Rank Fusion retrieval.
4. Semantic retrieval with cross-encoder reranking.

The evaluation used a frozen retrieval query set with:

```text
14 queries
```

The retrieval corpus contains approved SOP / KB chunks only.

### 6.2 Retrieval Results

| Method | Query Count | Top K | Hit@1 | Hit@3 | MRR@3 | No Result Rate |
|---|---:|---:|---:|---:|---:|---:|
| Lexical TF-IDF | 14 | 3 | 57.1% | 85.7% | 0.702 | 0.0% |
| Semantic Embedding | 14 | 3 | 78.6% | 92.9% | 0.857 | 0.0% |
| Hybrid RRF | 14 | 3 | 71.4% | 92.9% | 0.798 | 0.0% |
| Semantic + Cross-Encoder Reranker | 14 | 3 | 78.6% | 92.9% | 0.845 | 0.0% |

### 6.3 Retrieval Interpretation

Semantic embedding retrieval is the strongest baseline by MRR@3.

The cross-encoder reranker was implemented and evaluated. It matched semantic retrieval on Hit@1 and Hit@3, but produced slightly lower aggregate MRR@3 on the small 14-query retrieval evaluation set.

The reranker remains useful as a controlled optional stage because it demonstrates second-stage relevance scoring over retrieved candidates. It does not generate new policy advice and does not modify deterministic claim decisions.

### 6.4 Retrieval Artifacts

Generated artifacts:

```text
data/evaluation/retrieval/retrieval_summary_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_family_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_per_query_results_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_evaluation_with_reranker_manifest_v1.json
```

---

## 7. Workflow Development Evaluation

### 7.1 Workflow Evaluation Setup

The guarded LangGraph workflow was evaluated on labelled development claims.

Development claims evaluated:

```text
165
```

The workflow evaluation was run with:

```text
enable_controlled_rag=False
```

This was intentional because RAG is non-authoritative. Retrieval and reranking are evaluated separately in the retrieval evaluation.

Workflow evaluation measures:

- Deterministic triage execution.
- LangGraph orchestration.
- Follow-up selection.
- Response authority preservation.
- Agent content safety behaviour.
- Final response alignment with deterministic output.

### 7.2 Workflow Results

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

### 7.3 Workflow Interpretation

The workflow completed successfully for all 165 development claims.

The final response preserved deterministic outcome and triggering rule in every evaluated claim. This confirms that LangGraph orchestration, agent content safety checks, and response authority guardrails did not corrupt or override deterministic triage decisions.

The development-label agreement metrics show that the deterministic baseline is strong, while still leaving a defined improvement path for final submission.

---

## 8. Workflow Mismatch Interpretation

The workflow evaluation produced:

```text
91.5% disposition agreement
91.5% acceptable primary-rule agreement
```

The mismatches do not indicate LangGraph or RAG override failures. In all evaluated claims, the final response preserved deterministic triage outcome and triggering rule.

The remaining mismatches are primarily linked to deterministic rule coverage, rule precedence interpretation, or structured data availability. These are documented for final-submission review and will be addressed only where changes are justified by rule logic rather than overfitting to development labels.

### 8.1 Mismatch Summary

Total mismatch rows:

```text
15
```

Mismatch categories:

| Category | Count |
|---|---:|
| Disposition or rule mismatch | 14 |
| Follow-up selection mismatch only | 1 |

Mismatch patterns observed:

- Some mismatches are linked to documented baseline limitations for exclusion-related rules.
- Some mismatches are linked to deterministic precedence differences between coverage, evidence, and manual-review handling.
- One mismatch was limited to follow-up question selection while the disposition and rule were otherwise aligned.

### 8.2 Mismatch Artifact

Detailed mismatch analysis is available in:

```text
data/evaluation/workflow/workflow_development_mismatch_analysis_v1.csv
```

---

## 9. Safety and Adversarial Evaluation

### 9.1 Safety Evaluation Setup

The safety/adversarial evaluation used dedicated adversarial cases and tool-result fixtures.

Safety/adversarial cases evaluated:

```text
24
```

The safety evaluation directly tested the guardrail layers:

```text
deterministic tool-result fixture
→ adversarial proposed agent content
→ agent content safety guardrail
→ response authority guardrail
→ protected final response
```

This approach was used because the adversarial cases are not normal runtime claim records. They are designed to test critical guardrail behaviour directly.

### 9.2 Safety Results

| Metric | Result |
|---|---:|
| Safety/adversarial cases evaluated | 24 |
| Critical safety pass rate | 100.0% |
| Deterministic outcome preservation rate | 100.0% |
| Deterministic rule preservation rate | 100.0% |
| Unsafe override block rate | 100.0% |
| Mechanical prohibited behavior rate | 0.0% |

### 9.3 Safety Interpretation

All adversarial cases passed the critical safety gate.

The safety evaluation demonstrates that:

- Unsafe override attempts were blocked.
- Deterministic decision fields were preserved.
- Prohibited mechanical behavior did not leak into the protected final response.
- Fallback response behaviour worked as expected when unsafe proposed content was detected.

### 9.4 Safety Artifacts

Generated artifacts:

```text
data/evaluation/safety/safety_adversarial_summary_metrics_v1.csv
data/evaluation/safety/safety_adversarial_per_case_results_v1.csv
data/evaluation/safety/safety_adversarial_evaluation_manifest_v1.json
```

---

## 10. RAG Authority Boundary

The RAG layer is intentionally non-authoritative.

RAG can:

- Retrieve approved SOP / KB guidance.
- Support analyst understanding.
- Provide source-grounded references.
- Help explain operational context.

RAG cannot modify:

- `triage_outcome`
- `triggering_rule_id`
- `precedence_stage`
- policy eligibility
- coverage result
- evidence requirements
- controlled follow-up question wording
- final protected response fields

This boundary is central to the project’s safety design.

---

## 11. Generated Evaluation Artifacts

### 11.1 Retrieval

```text
data/evaluation/retrieval/retrieval_summary_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_family_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_per_query_results_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_evaluation_with_reranker_manifest_v1.json
```

### 11.2 Workflow

```text
data/evaluation/workflow/workflow_development_summary_metrics_v1.csv
data/evaluation/workflow/workflow_development_per_claim_results_v1.csv
data/evaluation/workflow/workflow_development_mismatch_analysis_v1.csv
data/evaluation/workflow/workflow_development_evaluation_manifest_v1.json
```

### 11.3 Safety

```text
data/evaluation/safety/safety_adversarial_summary_metrics_v1.csv
data/evaluation/safety/safety_adversarial_per_case_results_v1.csv
data/evaluation/safety/safety_adversarial_evaluation_manifest_v1.json
```

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

## 13. Known Limitations and Final Evaluation Plan

The evaluation completed for mid submission demonstrates that the current baseline is functional, tested, and quantitatively assessed across retrieval, workflow, and safety dimensions.

The following limitations are known and are being carried forward into the final submission plan.

### 13.1 Known Limitations

1. **Held-out labels are not used in the current development evaluation.**  
   This is intentional. Held-out evaluation is reserved for final submission to preserve a clean evaluation boundary.

2. **Some exclusion-related rules are limited by available structured data.**  
   The runtime data package does not currently include a dedicated structured exclusion-status dataset. These cases are documented as deterministic rule/data limitations rather than handled through unsupported inference.

3. **Reranker evaluation uses a small retrieval evaluation set.**  
   The cross-encoder reranker was evaluated on the frozen 14-query retrieval set. It matched semantic retrieval on Hit@1 and Hit@3, but did not improve aggregate MRR@3.

4. **Workflow mismatches are not caused by RAG or LangGraph override.**  
   The final response preserved deterministic triage outcome and triggering rule in every evaluated claim. Remaining mismatches are linked to deterministic rule/data coverage and precedence interpretation.

5. **Safety evaluation focuses on critical guardrail behaviour.**  
   The adversarial evaluation validates unsafe override blocking, deterministic output preservation, and prohibited-behavior leakage. Broader qualitative red-team review can be added during final submission preparation if required.

### 13.2 Final Evaluation Plan

Before final submission, the project will complete the following mandatory evaluation and packaging steps:

1. **Run held-out workflow evaluation.**  
   The final workflow will be evaluated against the locked held-out claim set, with results reported separately from development metrics.

2. **Review deterministic mismatch analysis.**  
   Development mismatches will be reviewed to identify justified rule or data improvements. Any changes will preserve deterministic authority and avoid overfitting to development labels.

3. **Refresh evaluation artifacts if logic changes.**  
   If deterministic logic is updated, retrieval, workflow, and safety artifacts will be regenerated as needed to keep documentation aligned with code.

4. **Prepare final report and presentation.**  
   Final deliverables will summarise the business problem, architecture, data design, implementation, evaluation results, safety controls, limitations, and future scope.

5. **Complete final reproducibility checks.**  
   The final repository will be validated through full regression testing, GitHub link review, documentation review, and secret/cache hygiene checks.

---

## 14. Mid-Submission Evaluation Conclusion

The current baseline demonstrates a functional, modular, and evaluated Version 1 system.

The evaluation evidence shows:

- Strong semantic retrieval performance on the frozen retrieval set.
- Successful LangGraph workflow completion across all development claims.
- 100% preservation of deterministic outcome and triggering rule in final responses.
- 100% authority guardrail alignment.
- 100% critical safety pass rate across adversarial cases.
- No observed mechanical prohibited-behavior leakage.

The system is ready for mid-submission review as a working baseline implementation with a clear final-submission improvement plan.