# Final Submission Rubric Evidence Matrix

## Purpose

This document is the final evidence-control record for:

**Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System**

It maps the approved proposal commitments and university rubric criteria to:

- implemented repository evidence,
- quantitative evaluation results,
- final technical report evidence,
- executive presentation evidence,
- documented limitations,
- reproducibility and release controls,
- final submission readiness.

It also acts as a scope-control record. No additional feature or model change should be introduced unless it closes a confirmed rubric, documentation, reproducibility, or release gap.

---

## 1. Governing Scope Boundaries

The project remains a **human-controlled decision-support prototype**.

The following boundaries are fixed:

- Deterministic policy, eligibility, coverage, evidence, limit, conflict, anomaly, and exclusion rules remain authoritative.
- The LLM must not override the deterministic triage outcome or triggering rule.
- Retrieval-Augmented Generation provides non-authoritative analyst guidance only.
- Risk indicators may route a case only to `MANUAL_REVIEW`.
- Follow-up questions must be selected from the approved catalogue.
- The system must not approve claims, authorise payments, confirm fraud, or issue final customer-facing denials.
- Final settlement and customer-facing approval or denial remain under authorised human control.
- Narrative text is not treated as verified authoritative policy evidence.
- The accepted business domain and purpose-built synthetic dataset remain unchanged.
- Held-out results must not be used for further tuning.
- The approved 30–40 hour project scope remains the governing effort boundary.
- No UI, deployment platform, additional agents, external datasets, or production integrations are included.
- The project must not be described as production-ready.

The governing design principle is:

> **AI explains. Rules decide. Humans remain accountable.**

---

## 2. Final Submission Status

| Area | Final status |
|---|---|
| Technical implementation | **Complete** |
| Deterministic triage workflow | **Complete** |
| LangGraph orchestration | **Complete** |
| Controlled follow-up selection | **Complete** |
| Controlled RAG and FAISS retrieval | **Complete** |
| Cross-encoder evaluation | **Complete** |
| LLM explanation support | **Complete** |
| Content-safety guardrail | **Complete** |
| Response-authority guardrail | **Complete** |
| Retrieval evaluation | **Complete** |
| Retrieval error analysis | **Complete** |
| Human generation review | **Complete** |
| LLM-as-judge evaluation | **Complete** |
| Human-versus-judge calibration | **Complete** |
| Ragas automated evaluation | **Complete** |
| Frozen held-out evaluation | **Complete** |
| Held-out safety evaluation | **Complete** |
| Final reviewer walkthrough | **Complete** |
| Final technical report | **Complete** |
| Executive presentation | **Complete** |
| Final report diagrams | **Complete** |
| README and reviewer navigation | **Complete** |
| Final evidence matrix | **Complete with this update** |
| Final pre-merge validation | **Complete — 149 tests passed** |
| Merge into `main` | **Complete — PR #1 merged at commit `97531f8`** |
| Final release tag | **Pending** |
| University portal submission | **Pending** |

The implementation, evaluation, report, presentation, and reviewer-facing documentation are complete. Remaining activities are release controls rather than project-development work.

---

## 3. Repository and Evaluation Control Record

| Control item | Verified value |
|---|---|
| Development branch | `final-submission-dev` |
| Target release branch | `main` |
| Frozen mid-submission tag | `mid-submission-v1` |
| Planned final release tag | `final-submission-v1` |
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
| Final recorded regression baseline | 149 tests passed |
| Final reviewer walkthrough regression run | 149 tests passed |
| Development claims | 165 |
| Held-out claims | 55 |
| Total new claims | 220 |
| Policy-device records | 120 |
| Historical claims | 112 |
| Evidence bundles | 220 |
| Evidence document records | 283 |
| Retrieval evaluation queries | 14 |
| Generation evaluation cases | 12 |
| Full adversarial safety cases | 24 |
| Held-out safety cases | 8 |
| Approved knowledge-base documents | 7 |
| Approved knowledge-base chunks | 21 |
| Approved follow-up questions | 14 |
| Held-out prediction SHA-256 | `0a20deead9d8fdcf75b740d39d11f8ff3934cb173da55c02ec61c860c92e2a1f` |
| SHA-256 verified by reviewer walkthrough | Yes |
| Held-out results used for tuning | No |
| Final README | Complete and committed |
| Final reviewer walkthrough | Complete and committed |
| Final technical report | Complete and committed |
| Final executive presentation | Complete as a separate submission artifact |
| Overall proposal assessment | `MET_WITH_DOCUMENTED_LIMITATION` |

The final reviewer walkthrough independently runs the local regression suite and verifies the frozen held-out prediction fingerprint without rerunning claims, retrieval, generation, Ragas, or held-out evaluation.

---

## 4. Final Headline Results

### 4.1 Approved Proposal Success Criteria

| Proposal criterion | Target | Final result | Status |
|---|---:|---:|---|
| Held-out triage-disposition accuracy | At least 80% | 49/55, **89.1%** | **PASS** |
| Policy-rule adherence | Report actual | 49/55, **89.1%** | Reported |
| Exact primary-rule agreement | Report actual | 48/55, **87.3%** | Reported |
| Follow-up requirement accuracy | Report actual | 55/55, **100.0%** | Reported |
| Exact follow-up question selection | Report actual | 14/15, **93.3%** | Reported |
| Manual-review routing recall | Report actual | 11/14, **78.6%** | Reported |
| Manual-review routing precision | Report actual | 11/11, **100.0%** | Reported |
| Unsafe-decision diagnostic | Report actual | 6/55, **10.9%** | **Material limitation** |
| Held-out adversarial safety pass rate | Zero critical failures | 8/8, **100.0%** | **PASS** |
| Critical held-out safety failures | 0 | **0** | **PASS** |
| Authority-guardrail alignment | Preserve authority | 55/55, **100.0%** | **PASS** |
| Human-control boundary | Preserve authorised human control | 55/55, **100.0%** | **PASS** |

### 4.2 Final Interpretation

The primary held-out accuracy target was exceeded by **9.1 percentage points**.

The held-out safety gate also passed:

- 8 of 8 held-out safety cases passed.
- Deterministic outcomes were preserved in all 8 cases.
- Applicable triggering rules were preserved in 6 of 6 cases.
- No rule was fabricated in the 2 cases where no rule was expected.
- Unsafe overrides were blocked in all 8 cases.
- No prohibited behaviour was present in the guarded responses.
- Zero critical held-out safety failures were observed.

A material limitation remains:

- Six ordinary held-out claims were incorrectly routed to `PROCEED`.
- The resulting unsafe-decision diagnostic was 10.9%.
- No claim was incorrectly routed to `NOT_ELIGIBLE`.
- These failures arose from structured-data and deterministic-rule coverage gaps rather than RAG or LLM override.

The final conclusion is:

> **The approved proposal success criteria were met, with a material documented unsafe-routing limitation that must be addressed before production use.**

---

## 5. University Rubric Evidence Matrix

| ID | Rubric area | Max marks | Final status | Repository or submission evidence |
|---:|---|---:|---|---|
| 1 | Business problem and GenAI suitability | 7 | **Complete** | Approved proposal, `README.md`, final technical report, executive presentation, `docs/architecture_decisions.md` |
| 2 | Stakeholders, user experience, ethics, and guardrails | 5 | **Complete** | Analyst workflow, approved follow-up selection, guidance formatter, content-safety guardrail, response-authority guardrail, human-control boundary |
| 3 | Data sourcing, provenance, and legal usability | 4 | **Complete** | Purpose-built synthetic dataset, data dictionaries, validation artifacts, provenance records, PII/IP safeguards, held-out controls |
| 4 | Data parsing, preparation, and cleansing | 5 | **Complete** | `src/data_loader.py`, `src/data_validation.py`, Notebook 01, runtime validation, schema checks, metadata extraction, referential-integrity validation |
| 5 | Semantic chunking and embeddings | 5 | **Complete** | `src/rag/corpus_builder.py`, approved KB registry, section-aware chunking, metadata, corpus fingerprint, semantic embeddings |
| 6 | Vector storage and indexing | 7 | **Complete** | Persisted FAISS index, index manifest, vector dimension, chunk-order fingerprint, corpus fingerprint, stale-index validation |
| 7 | Retrieval and mandatory cross-encoder reranking | 11 | **Complete** | TF-IDF, semantic retrieval, Hybrid RRF, cross-encoder reranker, Notebooks 05 and 08, retrieval metrics and manifests |
| 8 | Generation, orchestration, prompts, and guardrails | 10 | **Complete** | LangGraph workflow, deterministic tools, controlled query builder, follow-up selector, guarded explanation path, content and authority guardrails |
| 9 | Reproducibility | 7 | **Complete at repository-evidence level; final release rerun pending** | Modular repository, pinned requirements, relative paths, manifests, 149-test suite, final reviewer walkthrough, frozen predictions, SHA-256 verification |
| 10 | Architecture, modularity, and index freshness | 7 | **Complete** | Separation across `src/tools`, `src/agent`, and `src/rag`; architecture decisions; fingerprints; stale-index rejection |
| 11 | Automated evaluation framework | 12 | **Complete** | Notebook 09, Ragas 0.3.9, case-level results, summary, rule summary, low-score review, evaluation manifest |
| 12 | LLM-as-judge and documented human baseline | 10 | **Complete** | Notebook 07, human review v2, judge inputs/results v2, calibration summary, disagreement analysis |
| 13 | Technical report | 4 | **Complete** | `docs/final_technical_report.docx` |
| 14 | Executive presentation | 3 | **Complete** | Final 10-slide executive presentation prepared as a separate submission deliverable |
| 15 | GitHub repository and README | 3 | **Complete; final release pending** | Final README, modular source, notebooks, tests, manifests, evaluation artifacts, diagrams, reviewer navigation, walkthrough |
| 16 | Final held-out evaluation and approved proposal success criteria | Proposal commitment | **Complete with documented limitation** | Notebook 10, frozen predictions, SHA-256 fingerprint, metrics, error analysis, safety results, proposal assessment |

No rubric-driven implementation work remains. The remaining actions are final validation, merge, tagging, and submission.

---

## 6. Detailed Evidence Index

### 6.1 Business Problem and Scope

Primary evidence:

- Approved BYOC proposal
- `README.md`
- `docs/architecture_decisions.md`
- `docs/final_rubric_evidence_matrix.md`
- `docs/final_technical_report.docx`
- `notebooks/00_final_submission_reviewer_walkthrough.ipynb`
- Final executive presentation

Final narrative established:

- Device-protection claims triage is a rule-sensitive operational process.
- Deterministic rules are appropriate for authoritative policy and eligibility decisions.
- GenAI is appropriate for controlled explanation, retrieval, narrative support, and analyst assistance.
- Agentic orchestration is appropriate for sequencing tools, rule checks, retrieval, generation, and guardrails.
- Human analysts remain accountable for final operational action.

### 6.2 Synthetic Dataset and Provenance

Primary evidence:

- `data/staging/BYOC_DeviceProtect_Claims_Triage_Dataset_v1/`
- `data/source_zip/`
- `data/runtime/`
- `data/knowledge_base/`
- `data/evaluation/`
- `data/artifacts/`
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
- 7 approved knowledge-base documents
- 21 approved knowledge-base chunks
- 14 approved follow-up questions
- 220 ground-truth labels
- 24 adversarial safety cases
- 8 held-out safety cases

Final position:

- The data is purpose-built synthetic and domain-representative.
- No real customer claims or company-confidential data was used.
- No real customer PII was used.
- Development and held-out partitions remained disjoint.
- Synthetic data limitations are explicitly documented.
- Held-out labels were not used during development or tuning.

### 6.3 Parsing, Validation, and Preparation

Primary evidence:

- `src/data_loader.py`
- `src/data_validation.py`
- `src/rag/corpus_builder.py`
- `notebooks/01_data_inventory.ipynb`
- runtime validation and profiling artifacts

Implemented preparation includes:

- schema validation,
- mandatory-field checks,
- metadata extraction,
- referential-integrity checks,
- record-link validation,
- controlled source registration,
- Markdown section extraction,
- held-out partition validation,
- knowledge-base allow-list enforcement.

The selected sources are structured CSV and JSON records plus controlled Markdown knowledge documents. OCR and complex PDF-layout extraction were therefore not required.

### 6.4 Deterministic Triage and Tools

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

Implemented authority model:

- Policy and eligibility decisions are authoritative and deterministic.
- Rule precedence prevents the LLM from choosing an outcome.
- Risk triggers may route only to `MANUAL_REVIEW`.
- A triage outcome is not equivalent to claim approval, denial, fraud determination, or payment authorisation.
- The final operational action remains under authorised human control.

### 6.5 Agentic Orchestration and Generation

Primary evidence:

- `src/agent/langgraph_orchestrator.py`
- `src/agent/openai_explainer.py`
- `src/agent/controlled_query_builder.py`
- `src/agent/follow_up_selector.py`
- `src/agent/analyst_guidance_formatter.py`
- `src/agent/agent_content_guardrail.py`
- `src/agent/response_guardrail.py`
- Notebooks 03, 04, 06, and 07
- `notebooks/00_final_submission_reviewer_walkthrough.ipynb`

The workflow includes:

1. claim intake,
2. deterministic triage tools,
3. rule precedence and authoritative outcome,
4. controlled follow-up selection,
5. controlled query construction,
6. FAISS semantic retrieval,
7. optional cross-encoder reranking,
8. non-authoritative analyst explanation,
9. analyst-guidance formatting,
10. content-safety guardrail,
11. response-authority guardrail,
12. final recommendation for authorised human review.

The compiled LangGraph workflow is included in the reviewer walkthrough.

### 6.6 Architecture and Claim-Journey Visuals

Primary evidence:

- `docs/figures/figure_1_end_to_end_architecture.svg`
- `docs/figures/figure_2_controlled_retrieval_pipeline.svg`
- `docs/figures/figure_3_langgraph_orchestration_flow.svg`
- `docs/figures/figure_4_one_claim_journey.svg`
- corresponding editable `.mmd` source files

The visuals cover:

- end-to-end governed architecture,
- controlled retrieval pipeline,
- LangGraph orchestration flow,
- representative One Claim Journey.

The One Claim Journey traces a representative claim through:

- claim validation,
- policy lookup,
- plan and product-scope checks,
- policy status on the incident date,
- device match,
- coverage evaluation,
- prior-claims history,
- evidence assessment,
- deterministic triggering rule,
- controlled follow-up,
- controlled RAG query,
- FAISS retrieval,
- optional reranking,
- analyst explanation,
- content-safety guardrail,
- response-authority guardrail,
- final recommendation.

The walkthrough uses actual project outputs rather than hypothetical placeholders.

### 6.7 Retrieval, FAISS, and Reranking

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

Final retrieval decision:

- Semantic Embedding remains the default retrieval method.
- The cross-encoder remains a controlled optional stage.
- No chunking change was justified by the frozen benchmark.
- The reranker was retained because it produced meaningful case-level improvements, but it was not enabled as the default because it did not improve aggregate performance.

### 6.8 Generation Evaluation, Human Review, and LLM Judge

Primary evidence:

- `notebooks/07_generation_quality_evaluation.ipynb`
- `data/evaluation/generation/generation_evaluation_cases_v1.csv`
- `data/evaluation/generation/generation_human_review_v2.csv`
- `data/evaluation/generation/generation_judge_input_v2.csv`
- `data/evaluation/generation/generation_llm_judge_results_v2.csv`
- `data/evaluation/generation/generation_calibration_summary_v2.csv`
- `data/evaluation/generation/generation_calibration_disagreements_v2.csv`
- associated generation manifests

Frozen generation configuration:

- 12 development cases
- Controlled RAG enabled
- Top K = 3
- Minimum score = 0.2
- Reranker enabled for the frozen generation-evaluation configuration
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
- Content-safety status was `SAFE` for all 12 cases.
- Authority-guardrail status was `ALIGNED` for all 12 cases.

Evaluation interpretation:

- Human review measures analyst usefulness, practical relevance, grounding, and safety.
- The LLM judge provides scalable and repeatable scoring.
- Calibration and disagreement analysis are required because the LLM judge is not independent ground truth.
- The judge was more generous than the human reviewer on some context-relevance cases.
- Automated judging supplements rather than replaces human review.

### 6.9 Ragas Automated Evaluation

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

- Retrieval quality was evaluated against retrieved approved-KB chunks.
- Context Precision and Context Recall used rule-level RAG-guidance references.
- Response Faithfulness was evaluated against:
  - complete authoritative structured facts, and
  - retrieved approved-KB guidance.
- Answer Relevancy compared the controlled query with the frozen response.
- Held-out claims were not used.
- Frozen workflow outputs were not regenerated.

Important methodological finding:

The initial KB-only Faithfulness assessment penalised statements derived from legitimate authoritative structured facts that were not contained in the retrieved document chunks.

For the reviewed example:

- KB-only Faithfulness: approximately 0.222
- Complete authoritative support context plus KB: approximately 0.778

The final methodology therefore evaluates faithfulness against the complete legitimate generation context.

Primary Ragas finding:

- Retrieval alignment is the main RAG weakness.
- Exact preferred chunk hit: 3/12.
- Semantically adequate context: 6/12.
- Controlled queries sometimes retrieved generic evidence guidance rather than guidance specific to the triggering rule.
- This affected analyst-guidance relevance but did not alter deterministic outcomes.

### 6.10 Final Held-Out Evaluation

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

1. Confirmed that 55 held-out claims were disjoint from the 165 development claims.
2. Ran the frozen workflow without consulting held-out labels.
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

## 7. Material Limitation and Production-Readiness Improvements

### 7.1 Observed Limitation

All six held-out disposition errors were incorrect `PROCEED` recommendations.

The errors arose when the required business fact was:

- conflicting but not surfaced as a decisive structured conflict,
- present mainly in narrative text,
- related to an exclusion not represented in a validated structured source,
- related to a policy-date eligibility condition not triggered by the frozen runtime rule path,
- or otherwise unsupported by the available deterministic inputs.

The failures were not caused by:

- RAG modifying the authoritative outcome,
- the LLM selecting a disposition,
- the response-authority guardrail failing,
- or an adversarial override.

The final response continued to match the deterministic outcome in every held-out case.

### 7.2 Required Improvements Before Production Use

#### 1. Fail-safe routing

When an authoritative condition cannot be evaluated, the system should route to `MANUAL_REVIEW` rather than allowing the claim to fall through to `OUT-001 → PROCEED`.

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
- duplicate authoritative records,
- multiple authoritative matches,
- inconsistent device identifiers.

These cases should reliably trigger `DATA-002`.

#### 4. Structured exclusion indicators

Important exclusion facts should be converted into controlled structured attributes or validated evidence signals.

The LLM may identify a possible exclusion for human review, but it must not independently apply an exclusion or deny a claim.

#### 5. Eligibility-date coverage

Review and strengthen:

- incident date versus policy start date,
- policy end and cancellation date,
- suspension periods,
- waiting periods,
- missing incident dates,
- contradictory dates,
- timezone and date-format handling.

#### 6. Targeted future regression coverage

Create future regression tests for the six documented failure patterns.

These tests must be treated as post-evaluation production-readiness work. The original held-out result and prediction fingerprint must remain unchanged.

#### 7. Rule-aware retrieval alignment

Improve controlled queries so analyst guidance more directly targets:

- exclusions,
- data conflicts,
- anomalies,
- claim limits,
- unsupported conditions,
- decision boundaries.

This addresses the Ragas Context Recall weakness but does not replace deterministic-rule improvements.

#### 8. Production governance

Production use would additionally require:

- authenticated access,
- role-based permissions,
- audit logging,
- monitoring and alerting,
- operational data-quality controls,
- model and prompt governance,
- controlled rule change management,
- incident management,
- enterprise-system integration controls.

### 7.3 Production-Readiness Position

The capstone demonstrates a working and evaluated decision-support architecture.

It must not be described as production-ready because:

- six held-out cases were incorrectly routed to `PROCEED`,
- some rule families depend on structured facts not yet available,
- synthetic data cannot capture all real operational variation,
- enterprise integration is outside the approved scope,
- production monitoring, access control, audit operations, model governance, and change-management processes are outside the capstone scope.

---

## 8. Final Deliverable Evidence

### 8.1 Technical Report

Status: **Complete**

Primary artifact:

- `docs/final_technical_report.docx`

The final technical report covers:

- executive summary,
- business problem and measurable objectives,
- stakeholders and human-control boundaries,
- synthetic data and provenance,
- validation and preparation,
- solution architecture,
- deterministic tools,
- LangGraph orchestration,
- controlled retrieval,
- FAISS and cross-encoder reranking,
- prompt and guardrail design,
- design evolution and transparency,
- retrieval evaluation,
- human review,
- LLM-as-judge calibration,
- Ragas evaluation,
- frozen held-out evaluation,
- material limitation,
- production-readiness improvements,
- business value and conclusion.

### 8.2 Executive Presentation

Status: **Complete**

The final executive presentation contains 10 slides:

1. Cover
2. Business Problem
3. Authority Model
4. Data Ecosystem
5. System Architecture
6. One Claim Journey
7. Evaluation Framework
8. Results Dashboard
9. Limitations and Roadmap
10. Project Outcomes and Business Value

The presentation:

- highlights 89.1% held-out accuracy against the 80% target,
- shows 8/8 held-out safety cases passed,
- states zero critical held-out safety failures,
- discloses the six incorrect `PROCEED` recommendations,
- distinguishes prototype success from production readiness,
- preserves the conclusion `MET_WITH_DOCUMENTED_LIMITATION`.

The PowerPoint is prepared as a separate university submission artifact.

### 8.3 README and Repository Navigation

Status: **Complete**

The final README includes:

- concise project description,
- project-at-a-glance summary,
- final project-status metrics,
- business problem,
- authority model,
- system architecture,
- architecture highlights,
- representative One Claim Journey,
- data and repository structure,
- evaluation results,
- limitations,
- setup and reviewer guidance.

---

## 9. Final Release and Submission Controls

### 9.1 Actions Completed

- Final implementation completed.
- Final regression baseline recorded: 149 tests passed.
- Final reviewer walkthrough completed.
- Frozen held-out prediction SHA-256 verified.
- Retrieval benchmark completed.
- Retrieval error analysis completed.
- Cross-encoder comparison completed.
- Generation-quality evaluation completed.
- Human review completed.
- LLM-as-judge evaluation completed.
- Human-versus-judge calibration completed.
- Ragas evaluation completed.
- Frozen 55-claim held-out evaluation completed.
- Eight-case held-out safety evaluation completed.
- Six unsafe-routing cases documented transparently.
- Final technical report completed.
- Final executive presentation completed.
- Four final diagrams completed.
- README updated with final visuals and reviewer navigation.
- Final evidence matrix updated to reflect current status.

### 9.2 Final Pre-Merge Actions

Before merging `final-submission-dev` into `main`:

1. Confirm the working tree is clean.
2. Fetch the latest remote branch state.
3. Run:

   `python -m unittest discover -s tests -p "test_*.py" -v`

4. Confirm:

   `Ran 149 tests`  
   `OK`

5. Confirm the final reviewer walkthrough opens successfully.
6. Confirm the frozen held-out SHA-256 remains unchanged.
7. Confirm no `.env`, API key, credential, or secret is committed.
8. Confirm no unintended personal absolute paths are present.
9. Confirm evaluation manifests reference existing committed artifacts.
10. Confirm all intended notebooks are saved with final outputs.
11. Confirm the GitHub pull request reports that the branch is able to merge.

### 9.3 Release Sequence

After final validation:

1. Create a pull request with:
   - base: `main`
   - compare: `final-submission-dev`
2. Merge the validated branch into `main`.
3. Pull the updated `main` branch locally.
4. Run the 149-test suite once against merged `main`.
5. Verify the README and repository through the public GitHub URL.
6. Create the release tag: `final-submission-v1`.
7. Preserve the historical tag: `mid-submission-v1`.
8. Submit the final GitHub URL, report, presentation, and required supporting artifacts through the university portal.
9. Retain the submission acknowledgement or confirmation.

---

## 10. No Further Model or Workflow Tuning

Because the held-out labels have been revealed:

- do not modify the frozen workflow to improve the 55-claim result,
- do not regenerate the frozen prediction artifact,
- do not alter held-out labels,
- do not introduce new rules and report the resulting score as the original held-out result,
- do not hide or rewrite the six held-out errors,
- do not present a post-hoc tuned score as the final result.

Any proposed technical correction must be described as future production-readiness work.

Documentation corrections, release validation, merge activities, and packaging changes are permitted because they do not change the frozen model or evaluation result.

---

## 11. Stop Rules

Do not add new project work when any of the following applies:

- It is not required by the approved proposal or university rubric.
- It introduces a UI, deployment platform, additional agent, external dataset, or live enterprise integration.
- It replaces deterministic authority with LLM judgement.
- It uses held-out labels for tuning.
- It attempts to hide or rewrite the six held-out errors.
- It is intended only to improve an already frozen metric.
- The same rubric evidence can be provided through existing documentation.
- It materially risks exceeding the approved effort boundary.
- It introduces unnecessary changes immediately before submission.

The implementation and evaluation are frozen. Only release validation, merge, tagging, and submission packaging remain.

---

## 12. Final Acceptance Checklist

### Technical Validation

- [x] Final regression test suite completed successfully: 149 tests passed.
- [x] Final test count recorded in the README and evidence matrix.
- [x] Held-out prediction SHA-256 recorded.
- [x] Held-out prediction SHA-256 verified by the final reviewer walkthrough.
- [x] Development and held-out evidence clearly separated.
- [x] Held-out results explicitly marked as not used for tuning.
- [x] Retrieval benchmark completed.
- [x] Cross-encoder comparison completed.
- [x] Retrieval error analysis completed.
- [x] Generation-quality evaluation completed.
- [x] Human generation review completed.
- [x] LLM-as-judge evaluation completed.
- [x] Human-versus-judge calibration completed.
- [x] Ragas evaluation completed.
- [x] Frozen 55-claim held-out evaluation completed.
- [x] Eight-case held-out safety evaluation completed.
- [x] Zero critical held-out safety failures recorded.
- [x] Six unsafe-routing errors documented transparently.
- [ ] Final 149-test run completed immediately before merge.
- [ ] Final 149-test run completed against merged `main`.

### Repository Hygiene

- [x] Final README completed.
- [x] Final reviewer walkthrough completed.
- [x] Actual compiled LangGraph included in the reviewer walkthrough.
- [x] Final evaluation artifacts committed.
- [x] Final diagrams committed and referenced.
- [ ] Confirm no API key, credential, or secret is committed.
- [ ] Confirm no unintended personal absolute path is exposed.
- [ ] Confirm all evaluation manifests reference the correct files.
- [ ] Confirm all notebooks open successfully.
- [ ] Confirm all notebooks are saved with their intended final outputs.
- [ ] Confirm all committed evaluation artifacts are present and non-empty.
- [ ] Confirm final working tree is clean.

### Documentation and Submission Evidence

- [x] Final technical report completed.
- [x] Design-evolution and transparency discussion included.
- [x] Executive presentation completed.
- [x] End-to-end architecture diagram completed.
- [x] Controlled retrieval pipeline diagram completed.
- [x] LangGraph orchestration diagram completed.
- [x] One Claim Journey diagram and walkthrough completed.
- [x] Final held-out limitation carried consistently into the README, report, and presentation.
- [x] Final conclusion stated as `MET_WITH_DOCUMENTED_LIMITATION`.
- [x] Final evidence matrix updated to current status.

### Release Controls

- [ ] Pull request confirms `final-submission-dev` is able to merge into `main`.
- [ ] `final-submission-dev` merged into `main`.
- [ ] Public `main` branch verified after merge.
- [ ] Final release tag `final-submission-v1` created.
- [ ] Historical tag `mid-submission-v1` preserved.
- [ ] Final repository URL verified.
- [ ] Final report and presentation uploaded to the university portal.
- [ ] Submission acknowledgement retained.

---

## 13. Final Assessment

### Approved Proposal Outcome

`MET_WITH_DOCUMENTED_LIMITATION`

### Final Evidence-Based Conclusion

The project successfully demonstrates a governed Agentic AI decision-support architecture for device-protection claims triage.

It combines:

- authoritative deterministic decision logic,
- modular deterministic tools,
- LangGraph orchestration,
- controlled follow-up selection,
- approved knowledge retrieval,
- FAISS semantic search,
- optional cross-encoder reranking,
- grounded LLM analyst explanations,
- content-safety controls,
- response-authority controls,
- frozen evaluation protocols,
- and authorised human decision accountability.

The project exceeded its primary held-out accuracy target, preserved deterministic authority, passed the held-out adversarial safety gate, and produced zero critical safety failures.

The six incorrect `PROCEED` recommendations remain a material production-readiness limitation. They have been retained transparently in the final evidence, report, presentation, and improvement roadmap.

No additional model or workflow development is required for capstone submission.

The validated implementation has been merged into `main` and is ready for final post-merge verification, creation of the `final-submission-v1` tag, and university submission.
