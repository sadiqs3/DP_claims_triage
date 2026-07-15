# Final Submission Rubric Evidence Matrix

## Purpose

This document is the final evidence-control record for:

**Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System**

It maps the approved proposal commitments and university rubric criteria to:

- implemented repository evidence,
- quantitative evaluation results,
- final report sections,
- presentation evidence,
- remaining submission tasks,
- final acceptance checks.

The document is also a scope-control mechanism. No additional feature should be introduced unless it closes a confirmed rubric, reproducibility, documentation, or implementation gap.

---

## 1. Governing Scope Boundaries

The project remains a human-controlled decision-support system.

The following boundaries are fixed:

- Deterministic policy, eligibility, evidence, limit, conflict, and anomaly rules remain authoritative.
- The LLM must not override the deterministic triage outcome or triggering rule.
- RAG provides non-authoritative analyst guidance only.
- Risk indicators may route a case only to `MANUAL_REVIEW`.
- Follow-up questions must be selected from the approved catalogue.
- The system must not approve claims, authorise payments, confirm fraud, or issue final customer-facing denials.
- Final settlement and customer-facing approval or denial remain under authorised human control.
- The accepted business domain and synthetic dataset remain unchanged.
- The held-out results must not be used for further tuning.
- The approved 30–40 hour project scope remains the governing effort boundary.
- No UI, deployment platform, additional agents, external datasets, or production integrations will be added for final submission.

---

## 2. Repository and Evaluation Control Record

| Control item | Verified value |
|---|---|
| Active development branch | `final-submission-dev` |
| Frozen mid-submission branch | `main` |
| Frozen mid-submission tag | `mid-submission-v1` |
| Python version | 3.11.15 |
| Main project environment | `dpclaims` |
| Isolated Ragas environment | `dpclaims-ragas` |
| FAISS version | 1.14.3 |
| OpenAI SDK | 2.44.0 |
| Embedding model | `text-embedding-3-small` |
| Embedding dimension | 1536 |
| FAISS index type | `IndexFlatIP` |
| Cross-encoder model | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Ragas version | 0.3.9 |
| Latest recorded regression baseline | 149 tests passed |
| Final pre-release regression run | 149 tests passed on 2026-07-14 |
| Development claims | 165 |
| Held-out claims | 55 |
| Retrieval evaluation queries | 14 |
| Generation evaluation cases | 12 |
| Full adversarial safety cases | 24 |
| Held-out safety cases | 8 |
| Knowledge-base chunks | 21 |
| Held-out prediction SHA-256 | `0a20deead9d8fdcf75b740d39d11f8ff3934cb173da55c02ec61c860c92e2a1f` |
| Held-out results used for tuning | No |
| Overall proposal assessment | `MET_WITH_DOCUMENTED_LIMITATION` |

The final pre-release regression run confirmed the existing baseline of 149 passing tests.

---

## 3. Final Headline Results

### 3.1 Approved Proposal Success Criteria

| Proposal criterion | Target | Final result | Status |
|---|---:|---:|---|
| Held-out triage-disposition accuracy | At least 80% | 49/55, **89.1%** | **PASS** |
| Policy-rule adherence | Report actual | 49/55, **89.1%** | Reported |
| Exact primary-rule agreement | Report actual | 48/55, **87.3%** | Reported |
| Follow-up requirement accuracy | Report actual | 55/55, **100%** | Reported |
| Exact follow-up question selection | Report actual | 14/15, **93.3%** | Reported |
| Manual-review routing recall | Report actual | 11/14, **78.6%** | Reported |
| Manual-review routing precision | Report actual | 11/11, **100%** | Reported |
| Unsafe-decision rate | Report actual | 6/55, **10.9%** | **Material limitation** |
| Held-out adversarial safety pass rate | Zero critical failures | 8/8, **100%** | **PASS** |
| Critical held-out safety failures | 0 | **0** | **PASS** |
| Authority-guardrail alignment | Preserve authority | 55/55, **100%** | **PASS** |
| Human-control boundary | Preserve authorised human control | 55/55, **100%** | **PASS** |

### 3.2 Final Interpretation

The primary held-out accuracy target was exceeded by 9.1 percentage points.

The hard held-out safety gate also passed:

- 8 of 8 safety cases passed.
- Deterministic outcomes were preserved in all 8 cases.
- Applicable triggering rules were preserved in 6 of 6 cases.
- No rule was fabricated in the 2 cases where no rule was expected.
- Unsafe overrides were blocked in all 8 cases.
- No prohibited behaviour was present in the guarded responses.
- Zero critical safety failures were observed.

A material limitation remains:

- Six ordinary held-out claims were incorrectly routed to `PROCEED`.
- The resulting unsafe-decision diagnostic was 10.9%.
- No claim was incorrectly routed to `NOT_ELIGIBLE`.
- These failures were caused by structured-data and deterministic-rule coverage gaps rather than RAG or LLM override.

The appropriate final conclusion is:

> The approved proposal success criteria were met, with a material documented unsafe-routing limitation that must be addressed before production use.

---

## 4. University Rubric Evidence Matrix

| ID | Rubric area | Max marks | Final status | Repository evidence | Remaining submission action |
|---:|---|---:|---|---|---|
| 1 | Business problem and GenAI suitability | 7 | Complete | Approved proposal, `README.md`, `docs/mid_submission_summary.md`, `docs/architecture_decisions.md`, deterministic-versus-GenAI boundaries | Present the final business case and technology rationale clearly in the report and presentation |
| 2 | Stakeholders, user experience and guardrails | 5 | Complete | Analyst workflow, controlled follow-up, analyst guidance formatter, content safety guardrail, response authority guardrail | Summarise stakeholder value, analyst workflow, and prohibited autonomous actions |
| 3 | Data sourcing, provenance and legal usability | 4 | Complete | Purpose-built synthetic dataset, data dictionaries, validation artifacts, licence files, PII/IP declaration, dataset partition controls | Consolidate provenance, legal usability, assumptions, and limitations in README and report |
| 4 | Data parsing, preparation and cleansing | 5 | Complete | `src/data_loader.py`, `src/data_validation.py`, `notebooks/01_data_inventory.ipynb`, corpus preparation, runtime validation, held-out disjointness checks | Add a concise preprocessing and validation flow to the report and reviewer walkthrough |
| 5 | Chunking and embeddings | 5 | Complete | `src/rag/corpus_builder.py`, approved KB registry, section-aware chunking, chunk metadata, corpus fingerprint, semantic retriever | Explain section-aware chunking, embedding model choice, and absence of unnecessary overlap |
| 6 | Vector storage and indexing | 7 | Complete | Persisted FAISS index, `semantic_index.faiss`, index manifest, vector dimension, chunk-order fingerprint, corpus fingerprint, stale-index validation | Add exact validation and rebuild instructions to the final README |
| 7 | Retrieval and cross-encoder reranking | 11 | Complete | Lexical TF-IDF, Semantic Embedding, Hybrid RRF, cross-encoder reranker, `notebooks/05_sop_rag_retrieval.ipynb`, `notebooks/08_retrieval_error_analysis.ipynb`, retrieval CSVs and manifests | Present before/after metrics, reranker regressions, and the final semantic-default decision |
| 8 | Generation, orchestration, prompts and guardrails | 10 | Complete | LangGraph workflow, deterministic tools, controlled query builder, OpenAI explanation path, controlled follow-up, analyst guidance formatter, content and response guardrails | Add architecture diagram and the “One Claim Journey” walkthrough |
| 9 | Reproducibility | 7 | Tests complete; clean-copy QA pending | Modular repository, `requirements.txt`, relative paths, environment notebook, manifests, tests, frozen predictions, SHA-256 fingerprint | Complete clean-copy reproducibility, secrets, paths, and link validation |
| 10 | Architecture, modularity and index freshness | 7 | Complete | Separation across `src/tools`, `src/agent`, `src/rag`; architecture decisions; corpus fingerprints; index validation; stale-index rejection | Document controlled index rebuild procedure and model-rotation considerations |
| 11 | Automated evaluation framework | 12 | Complete | `notebooks/09_automated_rag_evaluation.ipynb`, Ragas 0.3.9, case-level results, summary, rule summary, low-score review, manifest | Summarise the hybrid Ragas methodology and limitations in the report |
| 12 | LLM-as-judge and documented human baseline | 10 | Complete | `notebooks/07_generation_quality_evaluation.ipynb`, human review v2, judge input v2, judge results v2, calibration summary, disagreement analysis | Present human-versus-judge calibration and explain why both are needed |
| 13 | Technical report | 4 | Pending | Repository evidence and quantitative results are complete | Produce the required 10–15 page final technical report |
| 14 | Executive presentation | 3 | Pending | Architecture, metrics, claim journey, business value, and limitations are available | Produce the required 8–12 slide executive presentation |
| 15 | GitHub repository and README | 3 | Complete; final repository QA pending| Strong modular repository, notebooks, tests, manifests, artifacts, documentation | Replace mid-submission framing with final status, final metrics, execution sequence, limitations, and reviewer navigation |
| 16 | Final held-out evaluation and approved proposal success criteria | Proposal commitment | Complete | `notebooks/10_final_heldout_evaluation.ipynb`, frozen predictions, SHA-256 fingerprint, case metrics, error analysis, safety results, proposal assessment, manifest | Carry the results and production-readiness limitations into all final artifacts |

---

## 5. Detailed Evidence Index

### 5.1 Business Problem and Scope

Primary evidence:

- Approved BYOC proposal
- `README.md`
- `docs/mid_submission_summary.md`
- `docs/architecture_decisions.md`
- `docs/final_rubric_evidence_matrix.md`

Required final narrative:

- Device-protection claims triage is a high-volume, rule-sensitive process.
- Deterministic rules are appropriate for authoritative policy decisions.
- GenAI is appropriate for controlled explanation, retrieval, narrative support, and analyst assistance.
- Agentic orchestration is appropriate for sequencing tools, rule checks, RAG, generation, and guardrails.
- Human analysts remain accountable for final action.

### 5.2 Synthetic Dataset and Provenance

Primary evidence:

- `data/staging/BYOC_DeviceProtect_Claims_Triage_Dataset_v1/`
- `data/runtime/`
- `data/internal/`
- data dictionaries and validation artifacts
- `notebooks/01_data_inventory.ipynb`
- `src/data_loader.py`
- `src/data_validation.py`

Key dataset volumes:

- 120 policy-device records
- 112 historical claims
- 220 new claims
- 165 development claims
- 55 held-out claims
- 220 evidence bundles
- 283 evidence document records
- 7 approved KB documents
- 14 approved follow-up questions
- 220 ground-truth labels
- 24 adversarial safety cases
- 8 held-out safety cases

Final report requirements:

- Explain why synthetic data was necessary.
- Explain PII and intellectual-property safeguards.
- Explain development and held-out separation.
- State that no real customer or company-confidential claims data was used.
- State the limitations of synthetic data.

### 5.3 Deterministic Triage and Tools

Primary evidence:

- `src/tools/policy_lookup.py`
- `src/tools/policy_eligibility.py`
- `src/tools/coverage_lookup.py`
- `src/tools/plan_configuration.py`
- `src/tools/claims_history.py`
- `src/tools/evidence_lookup.py`
- `src/tools/evidence_assessment.py`
- `src/tools/risk_lookup.py`
- `src/tools/claim_context.py`
- `notebooks/02_deterministic_triage_baseline.ipynb`

Required report narrative:

- Policy and eligibility decisions are authoritative and deterministic.
- Rule precedence prevents the LLM from choosing an outcome.
- Risk triggers may only route to `MANUAL_REVIEW`.
- An outcome is not equivalent to claim approval, denial, or payment authorisation.

### 5.4 Agentic Orchestration and Generation

Primary evidence:

- `src/agent/langgraph_orchestrator.py`
- `src/agent/openai_explainer.py`
- `src/agent/controlled_query_builder.py`
- `src/agent/follow_up_selector.py`
- `src/agent/analyst_guidance_formatter.py`
- `src/agent/agent_content_guardrail.py`
- `src/agent/response_guardrail.py`
- `notebooks/03_openai_guarded_explanation_workflow.ipynb`
- `notebooks/04_controlled_follow_up_questions.ipynb`
- `notebooks/06_workflow_evaluation.ipynb`
- `notebooks/07_generation_quality_evaluation.ipynb`

Required final diagrams:

1. End-to-end architecture diagram
2. LangGraph workflow diagram
3. “One Claim Journey” diagram

The “One Claim Journey” must trace one representative claim through:

- claim validation,
- deterministic policy checks,
- authoritative facts,
- controlled query creation,
- FAISS retrieval,
- optional cross-encoder reranking,
- LLM decision support,
- content guardrail,
- response authority guardrail,
- final recommended disposition.

The walkthrough must use real project outputs such as:

- policy lookup status,
- coverage result,
- evidence requirement,
- retrieved KB chunk,
- triggering rule,
- final analyst recommendation.

### 5.5 Retrieval, FAISS and Reranking

Primary evidence:

- `src/rag/corpus_builder.py`
- `src/rag/lexical_retriever.py`
- `src/rag/semantic_retriever.py`
- `src/rag/hybrid_retriever.py`
- `src/rag/faiss_index.py`
- `src/rag/reranker.py`
- `notebooks/05_sop_rag_retrieval.ipynb`
- `notebooks/08_retrieval_error_analysis.ipynb`
- `data/artifacts/rag/faiss_semantic_index_v1/`
- `data/evaluation/retrieval/`

Frozen retrieval results:

| Method | Hit@1 | Hit@3 | MRR@3 | No-result rate |
|---|---:|---:|---:|---:|
| Lexical TF-IDF | 57.1% | 85.7% | 0.702 | 0.0% |
| Semantic Embedding | 78.6% | 92.9% | 0.857 | 0.0% |
| Hybrid RRF | 71.4% | 92.9% | 0.798 | 0.0% |
| Semantic + Cross-Encoder | 78.6% | 92.9% | 0.845 | 0.0% |

Reranker comparison:

- Improved 2 queries.
- Regressed 2 queries.
- Left 9 top-1 results unchanged.
- Left 1 persistent top-3 miss.
- Aggregate MRR@3 decreased from 0.857 to 0.845.

Final decision:

- Semantic Embedding remains the default retrieval method.
- The cross-encoder remains a controlled optional stage.
- No chunking change was justified by the frozen benchmark.

### 5.6 Generation Evaluation, Human Review and LLM Judge

Primary evidence:

- `notebooks/07_generation_quality_evaluation.ipynb`
- `data/evaluation/generation/generation_evaluation_cases_v1.csv`
- `data/evaluation/generation/generation_human_review_v2.csv`
- `data/evaluation/generation/generation_judge_input_v2.csv`
- `data/evaluation/generation/generation_llm_judge_results_v2.csv`
- `data/evaluation/generation/generation_calibration_summary_v2.csv`
- disagreement and manifest artifacts under `data/evaluation/generation/`

Frozen generation cases:

- 12 development cases
- Controlled RAG enabled
- Top K = 3
- Minimum score = 0.2
- Reranker enabled
- Explanation model configured through the frozen workflow

Human-review results:

| Human metric | Mean score |
|---|---:|
| Context relevance | 2.75 / 4 |
| Groundedness | 3.75 / 4 |
| Answer relevance | 3.67 / 4 |
| Hallucination control | 3.75 / 4 |
| Critical safety failures | 0 |

Additional invariants:

- Deterministic outcome equalled final outcome for all 12 cases.
- Triggering rule equalled final triggering rule for all 12 cases.
- Content safety was `SAFE` for all 12 cases.
- Authority guardrail was `ALIGNED` for all 12 cases.

Required report interpretation:

- Human review measures analyst usefulness, practical relevance, grounding, and safety.
- The LLM judge provides scalable, repeatable scoring.
- Calibration and disagreement analysis are necessary because an LLM judge is not an independent ground truth.
- The judge complements rather than replaces human review.

### 5.7 Ragas Automated Evaluation

Primary evidence:

- `notebooks/09_automated_rag_evaluation.ipynb`
- `data/evaluation/ragas/ragas_case_results_v1.csv`
- `data/evaluation/ragas/ragas_summary_v1.csv`
- `data/evaluation/ragas/ragas_rule_summary_v1.csv`
- `data/evaluation/ragas/ragas_low_score_review_v1.csv`
- `data/evaluation/ragas/ragas_manifest_v1.json`

Final Ragas results:

| Metric | Mean |
|---|---:|
| Context Precision | 0.576 |
| Context Recall | 0.417 |
| Faithfulness | 0.627 |
| Answer Relevancy | 0.533 |

Hybrid evaluation methodology:

- Retrieval quality was evaluated against the three retrieved approved-KB chunks.
- Context Precision and Context Recall used a rule-level RAG-guidance reference.
- Response Faithfulness was evaluated against:
  - complete authoritative structured facts, and
  - retrieved approved-KB guidance.
- Answer Relevancy compared the controlled query with the frozen response.

Important methodological finding:

The original KB-only Faithfulness test scored `GEN-006` at 0.222 because the response also contained authoritative structured facts that were not present in the KB.

When the complete authoritative support context was supplied, the Faithfulness score increased to 0.778.

Required report interpretation:

> Standard RAG evaluation often assumes that a response is supported only by retrieved documents. This project uses a hybrid architecture in which the explanation is generated from deterministic structured facts and retrieved guidance. Faithfulness therefore had to be evaluated against the complete authoritative generation context.

Primary Ragas finding:

- Retrieval alignment is the main weakness.
- Controlled queries often retrieved generic evidence guidance instead of guidance specific to the triggering rule.
- This is an analyst-guidance retrieval issue and did not change deterministic outcomes.

### 5.8 Final Held-Out Evaluation

Primary evidence:

- `notebooks/10_final_heldout_evaluation.ipynb`
- `data/evaluation/heldout/heldout_predictions_frozen_v1.csv`
- `data/evaluation/heldout/heldout_case_results_v1.csv`
- `data/evaluation/heldout/heldout_class_metrics_v1.csv`
- `data/evaluation/heldout/heldout_supporting_metrics_v1.csv`
- `data/evaluation/heldout/heldout_disposition_errors_v1.csv`
- `data/evaluation/heldout/heldout_safety_results_v1.csv`
- `data/evaluation/heldout/heldout_safety_summary_v1.csv`
- `data/evaluation/heldout/heldout_proposal_success_assessment_v1.csv`
- `data/evaluation/heldout/heldout_evaluation_manifest_v1.json`

Evaluation protocol:

1. Confirmed 55 held-out claims were disjoint from the 165 development claims.
2. Ran the frozen deterministic workflow without consulting the labels.
3. Exported the 55 prediction records.
4. Generated a SHA-256 fingerprint.
5. Joined ground truth only after predictions were frozen.
6. Calculated the approved proposal metrics.
7. Documented errors without modifying or retuning the workflow.

Disposition confusion matrix:

| Gold \ Predicted | PROCEED | INFO_REQUIRED | MANUAL_REVIEW | NOT_ELIGIBLE |
|---|---:|---:|---:|---:|
| PROCEED | 17 | 0 | 0 | 0 |
| INFO_REQUIRED | 0 | 15 | 0 | 0 |
| MANUAL_REVIEW | 3 | 0 | 11 | 0 |
| NOT_ELIGIBLE | 3 | 0 | 0 | 6 |

Per-class results:

| Disposition | Precision | Recall | F1 |
|---|---:|---:|---:|
| PROCEED | 0.739 | 1.000 | 0.850 |
| INFO_REQUIRED | 1.000 | 1.000 | 1.000 |
| MANUAL_REVIEW | 1.000 | 0.786 | 0.880 |
| NOT_ELIGIBLE | 1.000 | 0.667 | 0.800 |

Held-out errors:

| Missed rule | Expected outcome | Predicted outcome | Cases |
|---|---|---|---:|
| `DATA-002` | `MANUAL_REVIEW` | `PROCEED` | 2 |
| `EXC-002` | `MANUAL_REVIEW` | `PROCEED` | 1 |
| `ELG-002` | `NOT_ELIGIBLE` | `PROCEED` | 1 |
| `EXC-001` | `NOT_ELIGIBLE` | `PROCEED` | 2 |

Affected claims:

- `CLM-000174`
- `CLM-000175`
- `CLM-000179`
- `CLM-000202`
- `CLM-000219`
- `CLM-000220`

---

## 6. Material Limitation and Production-Readiness Improvements

### 6.1 Observed Limitation

All six held-out disposition errors were incorrect `PROCEED` recommendations.

The errors arose when the required business fact was:

- conflicting but not surfaced as a decisive structured conflict,
- present mainly in narrative text,
- related to an exclusion not represented in a validated structured source,
- related to a policy-date eligibility condition not triggered by the frozen runtime rule path,
- or otherwise unsupported by the available deterministic inputs.

The failures were not caused by:

- RAG modifying the outcome,
- the LLM selecting a disposition,
- the response guardrail failing,
- or adversarial override.

The final outcome continued to match the deterministic outcome in every case.

### 6.2 Required Improvements Before Production Use

#### 1. Fail-safe routing

When an authoritative condition cannot be evaluated, the system should route to:

`MANUAL_REVIEW`

rather than allowing the claim to fall through to:

`OUT-001 → PROCEED`

#### 2. Explicit tool evaluation states

Deterministic tools should distinguish:

- `PASS`
- `FAIL`
- `UNABLE_TO_EVALUATE`

`UNABLE_TO_EVALUATE` must not be treated as equivalent to a passed check.

#### 3. Stronger conflict detection

Add structured validation for:

- conflicting customer identifiers,
- conflicting policy identifiers,
- claim-to-policy mismatches,
- duplicate or multiple authoritative records,
- inconsistent device identifiers.

These cases should reliably trigger `DATA-002`.

#### 4. Structured exclusion indicators

Important exclusion facts should be converted into controlled structured attributes or validated evidence signals.

The LLM may identify a possible exclusion for review, but it must not independently apply an exclusion or deny a claim.

#### 5. Eligibility-date coverage

Review and strengthen:

- incident date versus policy start date,
- policy end and cancellation date,
- waiting periods,
- missing incident dates,
- contradictory dates,
- timezone and date-format handling.

#### 6. Targeted regression coverage

Create future regression tests for the six failure patterns.

These tests must be treated as post-evaluation improvement work. The original held-out result and prediction fingerprint must remain unchanged.

#### 7. Rule-aware retrieval alignment

Improve controlled queries so that analyst guidance better targets:

- exclusions,
- data conflicts,
- anomalies,
- claim limits,
- unsupported conditions,
- decision boundaries.

This addresses the Ragas Context Recall weakness but does not replace deterministic rule improvements.

### 6.3 Production-Readiness Position

The capstone demonstrates a working and evaluated decision-support architecture.

It must not be described as production-ready because:

- six held-out cases were incorrectly routed to `PROCEED`,
- some rule families depend on structured facts not yet available,
- synthetic data does not capture all real operational variation,
- integration, monitoring, access control, audit operations, model governance, and change-management processes are outside the capstone scope.

---

## 7. Final Report Evidence Plan

The final technical report must be 10–15 pages and should use the following structure.

### Section 1 — Business Problem and Objectives

Evidence:

- accepted proposal,
- business problem,
- stakeholders,
- four triage dispositions,
- approved success metrics,
- human-controlled boundary.

### Section 2 — Data and Knowledge Preparation

Evidence:

- synthetic dataset design,
- dataset volumes,
- development and held-out partitioning,
- data validation,
- knowledge-base registry,
- section-aware chunking,
- provenance and privacy controls.

### Section 3 — Solution Architecture and Design Rationale

Evidence:

- deterministic tools,
- LangGraph orchestration,
- controlled follow-up,
- controlled RAG,
- FAISS,
- cross-encoder,
- LLM explanation support,
- content and response guardrails,
- authorised human control.

Required diagrams:

- architecture landscape,
- LangGraph execution flow,
- retrieval pipeline,
- One Claim Journey.

### Section 4 — Implementation

Evidence:

- modular source structure,
- key tools,
- rule precedence,
- corpus builder,
- index persistence and validation,
- prompt and controlled-query design,
- guardrails,
- testing strategy.

### Section 5 — Evaluation and Results

Evidence:

- unit and regression tests,
- retrieval metrics,
- reranker error analysis,
- human review,
- LLM judge calibration,
- Ragas,
- 55-claim held-out evaluation,
- 8-case held-out safety evaluation,
- proposal success assessment.

### Section 6 — Limitations, Business Impact and Conclusion

Evidence:

- 89.1% held-out accuracy,
- 10.9% unsafe-decision diagnostic,
- six incorrect proceeds,
- zero critical held-out safety failures,
- production-readiness improvements,
- business value,
- conclusion: `MET_WITH_DOCUMENTED_LIMITATION`.

---

## 8. Executive Presentation Evidence Plan

The final presentation must contain 8–12 slides.

Recommended 10-slide structure:

1. **Problem and Business Opportunity**
2. **Scope, Users and Human-Control Boundary**
3. **Synthetic Data and Knowledge Sources**
4. **End-to-End Architecture**
5. **One Claim Journey**
6. **Retrieval, FAISS and Reranking**
7. **Evaluation Framework: Human, Judge and Ragas**
8. **Held-Out Results and Proposal Success**
9. **Material Limitation and Production Improvements**
10. **Business Value and Final Conclusion**

The presentation must not hide the six incorrect `PROCEED` recommendations.

---

## 9. Remaining Final-Submission Work

### Mandatory work

1. Final regression test suite completed: 149 tests passed.
2. Update `README.md` from mid-submission to final-submission status.
3. Create or update the final reviewer walkthrough.
4. Prepare the 10–15 page technical report.
5. Prepare the 8–12 slide executive presentation.
6. Perform clean-copy reproducibility validation.
7. Check the repository for secrets, local paths, temporary files, stale references, and broken links.
8. Confirm all notebooks are saved with intended outputs.
9. Confirm evaluation manifests match the committed artifacts.
10. Validate that the held-out prediction SHA-256 remains unchanged.
11. Update the final submission checklist.
12. Merge `final-submission-dev` into `main` only after final QA.
13. Create the final release tag without modifying `mid-submission-v1`.

### No further model or workflow tuning

Because held-out labels have been revealed:

- do not modify the frozen workflow to improve the 55-claim score,
- do not regenerate the frozen prediction artifact,
- do not alter the held-out labels,
- do not present a post-hoc tuned score as the final held-out result.

Any proposed technical correction must be described as future work.

---

## 10. Recommended Remaining Execution Order

1. Update this final evidence matrix.
2. Run and record the final regression test suite.
3. Build the final reviewer walkthrough.
4. Update the README.
5. Draft the final technical report.
6. Create the final diagrams.
7. Create the executive presentation.
8. Perform clean-copy reproducibility validation.
9. Perform secrets, paths, links, filenames, and artifact checks.
10. Complete the final submission checklist.
11. Review the report and slides against this matrix.
12. Merge the validated branch into `main`.
13. Create the final release tag.

---

## 11. Stop Rules

Do not add new work when any of the following applies:

- It is not required by the approved proposal or rubric.
- It introduces a UI, deployment platform, additional agent, external dataset, or live enterprise integration.
- It replaces deterministic authority with LLM judgement.
- It uses held-out labels for tuning.
- It attempts to hide or rewrite the six held-out errors.
- It is intended only to improve an already frozen metric.
- The same rubric evidence can be produced through documentation.
- It materially risks exceeding the approved effort boundary.

---

## 12. Final Acceptance Checklist

The submission is ready only when all applicable items are complete.

### Technical validation

- [x] Final regression test suite passes: 149 tests completed successfully.
- [x] Final test count is recorded in README and this matrix.
- [ ] No API key or secret is committed.
- [ ] No personal local path is exposed in final documentation or manifests where avoidable.
- [ ] All notebooks open successfully.
- [ ] All committed evaluation artifacts exist and are non-empty.
- [ ] Evaluation manifests reference the correct files.
- [ ] Held-out prediction SHA-256 remains unchanged.
- [ ] Development and held-out evidence remain clearly separated.
- [ ] Held-out results are explicitly marked as not used for tuning.

### Evaluation evidence

- [x] Retrieval benchmark completed.
- [x] Cross-encoder comparison completed.
- [x] Retrieval error analysis completed.
- [x] Generation-quality evaluation completed.
- [x] Human review completed.
- [x] LLM judge evaluation completed.
- [x] Human-versus-judge calibration completed.
- [x] Ragas evaluation completed.
- [x] 55-claim held-out evaluation completed.
- [x] Held-out predictions frozen before label comparison.
- [x] 8-case held-out safety evaluation completed.
- [x] Zero critical held-out safety failures recorded.
- [x] Six unsafe-routing errors documented transparently.

### Final artifacts

- [x] README updated for final submission.
- [x] Final reviewer walkthrough completed.
- [ ] Technical report completed and limited to 10–15 pages.
- [ ] Executive presentation completed and limited to 8–12 slides.
- [ ] Architecture diagram included.
- [ ] Retrieval pipeline diagram included.
- [ ] One Claim Journey included.
- [ ] Limitations and production-readiness improvements included.
- [ ] Proposal success assessment included.
- [ ] Final repository links validated.
- [ ] Final submission checklist completed.

### Release control

- [ ] `final-submission-dev` has a clean working tree.
- [ ] Final commit hash is recorded.
- [ ] Final artifacts have been reviewed against the rubric.
- [ ] `final-submission-dev` is merged into `main`.
- [ ] `mid-submission-v1` remains unchanged.
- [ ] Final release tag is created.
- [ ] Submitted repository URL resolves to the final version.

---

## 13. Final Evidence Status Summary

### Completed technical evidence

- Business problem and GenAI suitability
- Synthetic data generation and provenance
- Data validation and preparation
- Deterministic triage engine
- LangGraph orchestration
- Controlled follow-up selection
- Controlled RAG
- FAISS index persistence and validation
- Cross-encoder reranking
- Content and response guardrails
- Development workflow evaluation
- Retrieval evaluation and error analysis
- Human generation review
- LLM judge and calibration
- Ragas automated evaluation
- Full adversarial safety evaluation
- Locked 55-claim held-out evaluation
- Held-out adversarial safety gate
- Approved proposal success assessment
- Documented held-out limitations

### Remaining documentation and packaging evidence

- Final regression-test record
- Final README
- Final reviewer walkthrough
- Technical report
- Executive presentation
- Clean-copy reproducibility proof
- Final repository QA
- Final merge and release tag

---

## 14. Final Project Position

The project has completed its technical implementation and evaluation phases.

The system:

- exceeded the primary held-out accuracy target,
- preserved deterministic authority,
- maintained authorised human control,
- passed the held-out adversarial safety gate,
- provided controlled analyst guidance,
- and produced reproducible evaluation evidence.

The system also demonstrated a material limitation:

- six held-out claims were incorrectly routed to `PROCEED`.

The final submission must therefore present the project as:

> A successful, evaluated capstone decision-support prototype that met the approved proposal criteria, while requiring fail-safe routing and stronger structured rule coverage before production use.