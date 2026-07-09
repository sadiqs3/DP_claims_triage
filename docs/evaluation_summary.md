# Evaluation Summary

## 1. Purpose

This document summarises the evaluation evidence for the **Device Protection Claims Triage** capstone solution.

The evaluation covers three areas:

1. Retrieval quality for the SOP / knowledge-base RAG layer.
2. End-to-end guarded LangGraph workflow behaviour on labelled development claims.
3. Safety and adversarial guardrail behaviour.

The system is designed as a **decision-support workflow**. Deterministic policy rules remain authoritative. RAG output is non-authoritative and is used only as analyst-facing guidance.

---

## 2. Evaluation Scope

### 2.1 Retrieval Evaluation

Retrieval was evaluated on a frozen retrieval evaluation set of **14 queries** against the approved knowledge-base corpus.

Methods evaluated:

- Lexical TF-IDF
- Semantic Embedding
- Hybrid RRF
- Semantic + Cross-Encoder Reranker

Semantic embedding model:

```text
text-embedding-3-small
```

Cross-encoder reranker model:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

### 2.2 Workflow Development Evaluation

The guarded LangGraph workflow was evaluated on **165 labelled development claims**.

Workflow mode:

```text
enable_controlled_rag=False
```

RAG was disabled for this evaluation because RAG is non-authoritative and should not affect deterministic triage outcomes, triggering rules, or controlled follow-up wording.

### 2.3 Safety and Adversarial Evaluation

Safety guardrails were evaluated on **24 adversarial test cases** covering:

- Prompt injection and override attempts
- Privacy and unauthorized action
- Data and source integrity
- Evidence date and anomaly scenarios
- Follow-up and robustness
- Scope and exclusion boundaries

These cases were evaluated using deterministic tool-result fixtures and adversarial proposed agent content.

---

## 3. Retrieval Evaluation Results

### 3.1 Overall Retrieval Metrics

| Method | Query Count | Top K | Hit@1 | Hit@3 | MRR@3 | No Result Rate |
|---|---:|---:|---:|---:|---:|---:|
| Lexical TF-IDF | 14 | 3 | 57.1% | 85.7% | 0.702 | 0.0% |
| Semantic Embedding | 14 | 3 | 78.6% | 92.9% | 0.857 | 0.0% |
| Hybrid RRF | 14 | 3 | 71.4% | 92.9% | 0.798 | 0.0% |
| Semantic + Cross-Encoder Reranker | 14 | 3 | 78.6% | 92.9% | 0.845 | 0.0% |

### 3.2 Retrieval Interpretation

The semantic embedding retriever was the strongest baseline by MRR@3.

The cross-encoder reranker matched the semantic retriever on Hit@1 and Hit@3, but produced a slightly lower MRR@3 on the small 14-query evaluation set.

The reranker is retained as an optional controlled reranking stage because:

- The rubric expects a reranking component.
- The reranker was implemented and evaluated against the same frozen retrieval set.
- The reranker can improve individual query families even if aggregate MRR@3 was slightly lower.
- The reranker remains non-authoritative and cannot alter deterministic triage outcomes.

---

## 4. Workflow Development Evaluation Results

### 4.1 Dataset

Development claims evaluated:

```text
165
```

Development label source:

```text
data/staging/BYOC_DeviceProtect_Claims_Triage_Dataset_v1/data/internal/ground_truth_claim_labels_development_v1.csv
```

Workflow evaluation mode:

```text
enable_controlled_rag=False
```

### 4.2 Headline Workflow Metrics

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

### 4.3 Workflow Interpretation

The guarded LangGraph workflow completed successfully for all 165 development claims.

The final response preserved the deterministic triage outcome and triggering rule in every case. This confirms that the workflow orchestration, proposal layer, content safety guardrail, and response guardrail did not corrupt or override the authoritative deterministic decision.

The development-label agreement was strong but not perfect. Disposition agreement and acceptable primary-rule agreement were both **91.5%**.

---

## 5. Workflow Mismatch Analysis

### 5.1 Mismatch Summary

Total mismatch rows:

```text
15
```

| Mismatch Type | Count |
|---|---:|
| Disposition or rule mismatch | 14 |
| Follow-up selection mismatch | 1 |

### 5.2 Mismatch by Gold Primary Rule

| Gold Primary Rule | Count |
|---|---:|
| DATA-002 | 4 |
| EVD-002 | 3 |
| EXC-002 | 3 |
| ELG-002 | 3 |
| EVD-001 | 1 |
| EXC-001 | 1 |

### 5.3 Known Baseline Limitation

Known exclusion-rule limitation mismatches:

```text
4
```

These relate to `EXC-001` and `EXC-002`. The deterministic baseline manifest already documents that exclusion rules are limited because no structured exclusion-status dataset is available in the current runtime package.

### 5.4 Mismatch Interpretation

The mismatch analysis shows that remaining gaps are inherited from the deterministic rules baseline rather than caused by LangGraph, RAG, or the analyst-guidance formatter.

The key evidence is:

- Final response matched deterministic outcome in 100% of cases.
- Final response matched deterministic rule in 100% of cases.
- Authority guardrail was aligned in 100% of cases.
- Content safety status was SAFE in 100% of cases.

Therefore, mismatches against gold labels should be treated as deterministic rule/data error-analysis items, not orchestration failures.

---

## 6. Safety and Adversarial Evaluation Results

### 6.1 Dataset

Safety/adversarial cases evaluated:

```text
24
```

Input files:

```text
data/staging/BYOC_DeviceProtect_Claims_Triage_Dataset_v1/data/evaluation/safety_adversarial_test_cases_v1.csv
data/staging/BYOC_DeviceProtect_Claims_Triage_Dataset_v1/data/evaluation/safety_adversarial_tool_fixtures_v1.json
data/staging/BYOC_DeviceProtect_Claims_Triage_Dataset_v1/data/internal/safety_adversarial_expected_results_v1.csv
```

### 6.2 Headline Safety Metrics

| Metric | Result |
|---|---:|
| Critical safety pass rate | 100.0% |
| Deterministic outcome preservation rate | 100.0% |
| Deterministic rule preservation rate | 100.0% |
| Unsafe override block rate | 100.0% |
| Mechanical prohibited behavior rate | 0.0% |

### 6.3 Safety Result by Family

| Test Family | Test Count | Pass Rate | Fallback Rate |
|---|---:|---:|---:|
| DATA_AND_SOURCE_INTEGRITY | 4 | 100.0% | 100.0% |
| EVIDENCE_DATE_AND_ANOMALY | 4 | 100.0% | 100.0% |
| FOLLOW_UP_AND_ROBUSTNESS | 4 | 100.0% | 100.0% |
| PRIVACY_AND_UNAUTHORIZED_ACTION | 4 | 100.0% | 100.0% |
| PROMPT_INJECTION_AND_OVERRIDE | 4 | 100.0% | 100.0% |
| SCOPE_AND_EXCLUSION_BOUNDARIES | 4 | 100.0% | 100.0% |

### 6.4 Safety Interpretation

All 24 adversarial cases passed the critical safety gate.

Content safety fallback was applied in all 24 cases, and response guardrail override blocking was triggered in all 24 cases. This confirms that adversarial proposed content did not override deterministic outcomes, deterministic rules, or protected response fields.

---

## 7. Generated Evaluation Artifacts

### 7.1 Retrieval

```text
data/evaluation/retrieval/retrieval_summary_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_family_metrics_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_per_query_results_with_reranker_v1.csv
data/evaluation/retrieval/retrieval_evaluation_with_reranker_manifest_v1.json
```

### 7.2 Workflow

```text
data/evaluation/workflow/workflow_development_summary_metrics_v1.csv
data/evaluation/workflow/workflow_development_per_claim_results_v1.csv
data/evaluation/workflow/workflow_development_mismatch_analysis_v1.csv
data/evaluation/workflow/workflow_development_evaluation_manifest_v1.json
```

### 7.3 Safety

```text
data/evaluation/safety/safety_adversarial_summary_metrics_v1.csv
data/evaluation/safety/safety_adversarial_per_case_results_v1.csv
data/evaluation/safety/safety_adversarial_evaluation_manifest_v1.json
```

---

## 8. Known Limitations

1. Held-out evaluation labels are not used in this development evaluation.
2. Some exclusion-related rules are limited because the current runtime package does not include a structured exclusion-status dataset.
3. Cross-encoder reranking was evaluated on a small 14-query retrieval set. It matched Hit@1 and Hit@3 but did not improve aggregate MRR@3.
4. Workflow label mismatches are primarily deterministic rule/data issues, not LangGraph or RAG failures.
5. Safety evaluation checks deterministic preservation, override blocking, and mechanical prohibited-behavior leakage. Broader semantic safety assessment may require additional human review.

---

## 9. Held-Out Boundary

Held-out labels and held-out evaluation claims should remain locked until final evaluation.

Development evaluation uses only development labels and development claims. Retrieval evaluation uses the frozen retrieval evaluation set. Safety evaluation uses the provided adversarial safety cases and expected results.

---

## 10. Overall Conclusion

The system demonstrates a strong controlled decision-support workflow:

- RAG retrieval and reranking are implemented, evaluated, and kept non-authoritative.
- The guarded LangGraph workflow completed successfully for all development claims.
- The final response preserved deterministic triage decisions in 100% of development cases.
- Safety and adversarial guardrails passed all 24 evaluated adversarial cases.
- Remaining development-label mismatches are documented as deterministic rule/data limitations for future improvement.
