# Final Submission Rubric Evidence Matrix

## Purpose

This document is the final evidence-control record for:

**Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System**

It maps the approved proposal commitments and university rubric criteria to:

- implemented repository evidence,
- quantitative evaluation results,
- final report sections,
- executive presentation evidence,
- remaining submission work,
- final acceptance and release controls.

It also acts as a scope-control mechanism. No additional feature should be introduced unless it closes a confirmed rubric, reproducibility, documentation, or final-submission gap.

---

## 1. Governing Scope Boundaries

The project remains a human-controlled decision-support system.

The following boundaries are fixed:

- Deterministic policy, eligibility, evidence, limit, conflict, anomaly, and exclusion rules remain authoritative.
- The LLM must not override the deterministic triage outcome or triggering rule.
- RAG provides non-authoritative analyst guidance only.
- Risk indicators may route a case only to `MANUAL_REVIEW`.
- Follow-up questions must be selected from the approved catalogue.
- The system must not approve claims, authorise payments, confirm fraud, or issue final customer-facing denials.
- Final settlement and customer-facing approval or denial remain under authorised human control.
- Narrative text is not treated as verified authoritative policy evidence.
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
| Final recorded regression baseline | 149 tests passed |
| Final reviewer live regression run | 149 tests passed |
| Development claims | 165 |
| Held-out claims | 55 |
| Retrieval evaluation queries | 14 |
| Generation evaluation cases | 12 |
| Full adversarial safety cases | 24 |
| Held-out safety cases | 8 |
| Knowledge-base chunks | 21 |
| Held-out prediction SHA-256 | `0a20deead9d8fdcf75b740d39d11f8ff3934cb173da55c02ec61c860c92e2a1f` |
| SHA-256 verified by reviewer walkthrough | Yes |
| Held-out results used for tuning | No |
| Final README | Complete and committed |
| Final reviewer walkthrough | Complete and committed |
| Overall proposal assessment | `MET_WITH_DOCUMENTED_LIMITATION` |

The final reviewer walkthrough independently runs the local regression suite and verifies the frozen held-out prediction fingerprint without rerunning claims, retrieval, generation, Ragas, or held-out evaluation.

---

## 3. Final Headline Results

### 3.1 Approved Proposal Success Criteria

| Proposal criterion | Target | Final result | Status |
|---|---:|---:|---|
| Held-out triage-disposition accuracy | At least 80% | 49/55, **89.1%** | **PASS** |
| Policy-rule adherence | Report actual | 49/55, **89.1%** | Reported |
| Exact primary-rule agreement | Report actual | 48/55, **87.3%** | Reported |
| Follow-up requirement accuracy | Report actual | 55/55, **100.0%** | Reported |
| Exact follow-up question selection | Report actual | 14/15, **93.3%** | Reported |
| Manual-review routing recall | Report actual | 11/14, **78.6%** | Reported |
| Manual-review routing precision | Report actual | 11/11, **100.0%** | Reported |
| Unsafe-decision rate | Report actual | 6/55, **10.9%** | **Material limitation** |
| Held-out adversarial safety pass rate | Zero critical failures | 8/8, **100.0%** | **PASS** |
| Critical held-out safety failures | 0 | **0** | **PASS** |
| Authority-guardrail alignment | Preserve authority | 55/55, **100.0%** | **PASS** |
| Human-control boundary | Preserve authorised human control | 55/55, **100.0%** | **PASS** |

### 3.2 Final Interpretation

The primary held-out accuracy target was exceeded by 9.1 percentage points.

The held-out safety gate also passed:

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

| ID | Rubric area | Max marks | Current status | Repository evidence | Remaining submission action |
|---:|---|---:|---|---|---|
| 1 | Business problem and GenAI suitability | 7 | Complete | Approved proposal, final `README.md`, `docs/architecture_decisions.md`, deterministic-versus-GenAI authority boundaries | Present the business problem, measurable objectives, and GenAI rationale clearly in the final report and presentation |
| 2 | Stakeholders, user experience, ethics, and guardrails | 5 | Complete | Analyst workflow, controlled follow-up, analyst-guidance formatter, content-safety guardrail, response-authority guardrail, human-control boundary | Summarise stakeholder value, user journey, ethical boundaries, and prohibited autonomous actions |
| 3 | Data sourcing, provenance, and legal usability | 4 | Complete; report explanation required | Purpose-built synthetic dataset, data dictionaries, validation artifacts, licence and provenance records, PII/IP declaration, held-out controls | Explain why synthetic domain-representative data was used and acknowledge its limitations |
| 4 | Data parsing, preparation, and cleansing | 5 | Complete; report explanation required | `src/data_loader.py`, `src/data_validation.py`, Notebook 01, runtime validation, schema checks, metadata extraction, record-link validation, held-out disjointness checks | Explain why OCR and PDF layout parsing were not required for the selected CSV, JSON, and Markdown sources |
| 5 | Semantic chunking and embeddings | 5 | Complete | `src/rag/corpus_builder.py`, approved KB registry, section-aware chunking, metadata, corpus fingerprint, semantic retriever | Justify section-aware chunking and why overlap was unnecessary for the short structured 21-chunk corpus |
| 6 | Vector storage and indexing | 7 | Complete | Persisted FAISS index, index manifest, vector dimension, chunk-order fingerprint, corpus fingerprint, stale-index validation | Include exact validation and controlled rebuild instructions in the report |
| 7 | Retrieval and mandatory cross-encoder reranking | 11 | Complete | TF-IDF, Semantic Embedding, Hybrid RRF, cross-encoder reranker, Notebooks 05 and 08, retrieval CSVs and manifests | Present four-method metrics, one worked query, reranker improvement, regression, and final semantic-default decision |
| 8 | Generation, orchestration, prompts, and guardrails | 10 | Complete | LangGraph workflow, deterministic tools, controlled query builder, guarded explanation path, follow-up selector, guidance formatter, content and authority guardrails | Include architecture, LangGraph flow, and One Claim Journey diagrams |
| 9 | Reproducibility | 7 | Tests and reviewer validation complete; clean-copy QA pending | Modular repository, requirements, relative paths, manifests, tests, final reviewer walkthrough, frozen predictions, SHA-256 verification | Complete clean-clone installation, notebook, secrets, paths, links, and artifact validation |
| 10 | Architecture, modularity, and index freshness | 7 | Complete | Separation across `src/tools`, `src/agent`, and `src/rag`; ADRs; corpus fingerprints; index validation; stale-index rejection | Document index rebuild, model rotation, monitoring, and production change-control considerations |
| 11 | Automated evaluation framework | 12 | Complete | Notebook 09, Ragas 0.3.9, case-level results, summary, rule summary, low-score review, manifest | Explain the hybrid Ragas methodology and its limitations |
| 12 | LLM-as-judge and documented human baseline | 10 | Complete | Notebook 07, human review v2, judge inputs/results v2, calibration summary, disagreement analysis | Present human-versus-judge calibration and why automated judging supplements rather than replaces human review |
| 13 | Technical report | 4 | Pending | Complete repository and quantitative evidence are available | Produce the required 10–15 page final technical report |
| 14 | Executive presentation | 3 | Pending | Architecture, metrics, claim journey, business value, and limitations are available | Produce the required 8–12 slide executive presentation |
| 15 | GitHub repository and README | 3 | Complete; final repository QA pending | Final README, modular source structure, notebooks, tests, manifests, committed evaluation artifacts, reviewer navigation, final reviewer walkthrough | Complete clean-copy validation, secrets/path/link checks, and final release verification |
| 16 | Final held-out evaluation and approved proposal success criteria | Proposal commitment | Complete | Notebook 10, frozen predictions, SHA-256 fingerprint, case metrics, error analysis, safety results, proposal assessment, manifest | Carry the result and material production-readiness limitation into all final artifacts |

---

## 5. Detailed Evidence Index

### 5.1 Business Problem and Scope

Primary evidence:

- Approved BYOC proposal
- `README.md`
- `docs/architecture_decisions.md`
- `docs/final_rubric_evidence_matrix.md`
- `notebooks/00_final_submission_reviewer_walkthrough.ipynb`

Required final narrative:

- Device-protection claims triage is a high-volume, rule-sensitive operational process.
- Deterministic rules are appropriate for authoritative policy and eligibility decisions.
- GenAI is appropriate for controlled explanation, retrieval, narrative support, and analyst assistance.
- Agentic orchestration is appropriate for sequencing tools, rule checks, RAG, generation, and guardrails.
- Human analysts remain accountable for final operational action.

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
- 7 approved knowledge-base documents
- 21 approved KB chunks
- 14 approved follow-up questions
- 220 ground-truth labels
- 24 adversarial safety cases
- 8 held-out safety cases

Final report requirements:

- Explain why synthetic data was necessary.
- Explain PII and intellectual-property safeguards.
- Explain development and held-out separation.
- State that no real customer or company-confidential claims data was used.
- Describe the data-generation logic, validation, and lineage.
- Acknowledge that synthetic data cannot represent all production variation.
- Refer to the corpus as domain-representative synthetic data, not real customer claims.

### 5.3 Parsing, Validation, and Preparation

Primary evidence:

- `src/data_loader.py`
- `src/data_validation.py`
- `src/rag/corpus_builder.py`
- Notebook 01
- runtime validation and data-profile artifacts

Required final narrative:

- The selected sources are structured CSV and JSON records plus controlled Markdown knowledge documents.
- OCR and complex PDF-layout extraction were not required.
- Preparation included schema checks, mandatory-field checks, metadata extraction, referential-integrity checks, controlled source registration, section extraction, and held-out partition validation.
- The absence of OCR is a design consequence of the selected legally usable data sources, not an omitted processing step.

### 5.4 Deterministic Triage and Tools

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

Required final narrative:

- Policy and eligibility decisions are authoritative and deterministic.
- Rule precedence prevents the LLM from choosing an outcome.
- Risk triggers may only route to `MANUAL_REVIEW`.
- An outcome is not equivalent to claim approval, denial, fraud determination, or payment authorisation.

### 5.5 Agentic Orchestration and Generation

Primary evidence:

- `src/agent/langgraph_orchestrator.py`
- `src/agent/openai_explainer.py`
- `src/agent/controlled_query_builder.py`
- `src/agent/follow_up_selector.py`
- `src/agent/analyst_guidance_formatter.py`
- `src/agent/agent_content_guardrail.py`
- `src/agent/response_guardrail.py`
- Notebooks 03, 04, 06, and 07
- final reviewer walkthrough

Required final diagrams:

1. End-to-end architecture diagram
2. LangGraph orchestration flowchart
3. Retrieval pipeline diagram
4. One Claim Journey diagram and walkthrough

The LangGraph flowchart should show:

- claim intake,
- deterministic triage,
- rule precedence,
- controlled follow-up,
- controlled query construction,
- FAISS retrieval,
- optional cross-encoder reranking,
- explanation and analyst guidance,
- content-safety guardrail,
- response-authority guardrail,
- final recommendation for authorised human review.

The report should use a detailed node-level diagram. The presentation should use a simplified version.

### 5.6 One Claim Journey

The One Claim Journey must trace one representative claim through:

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

The walkthrough must use actual project outputs such as:

- policy lookup status,
- plan configuration status,
- coverage result,
- evidence assessment,
- retrieved KB chunk,
- triggering rule,
- final analyst recommendation.

The concise reviewer-notebook journey is complete. A more visually detailed version remains required for the final report and presentation.

### 5.7 Retrieval, FAISS, and Reranking

Primary evidence:

- `src/rag/corpus_builder.py`
- `src/rag/lexical_retriever.py`
- `src/rag/semantic_retriever.py`
- `src/rag/hybrid_retriever.py`
- `src/rag/faiss_index.py`
- `src/rag/reranker.py`
- Notebooks 05 and 08
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

Final report requirements:

- Explain how the 14 frozen queries were created and manually grounded.
- Include one worked comparison across lexical, semantic, and reranked results.
- Include at least one reranker improvement.
- Include at least one reranker regression.
- Explain why the reranker was retained but not enabled as the default.
- Explain why section-aware chunking remained unchanged.

### 5.8 Generation Evaluation, Human Review, and LLM Judge

Primary evidence:

- `notebooks/07_generation_quality_evaluation.ipynb`
- `data/evaluation/generation/generation_evaluation_cases_v1.csv`
- `data/evaluation/generation/generation_human_review_v2.csv`
- `data/evaluation/generation/generation_judge_input_v2.csv`
- `data/evaluation/generation/generation_llm_judge_results_v2.csv`
- `data/evaluation/generation/generation_calibration_summary_v2.csv`
- `data/evaluation/generation/generation_calibration_disagreements_v2.csv`
- associated generation manifests

Frozen generation cases:

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

Required report interpretation:

- Human review measures analyst usefulness, practical relevance, grounding, and safety.
- The LLM judge provides scalable and repeatable scoring.
- Calibration and disagreement analysis are necessary because an LLM judge is not independent ground truth.
- The judge was more generous than the human reviewer on some context-relevance cases.
- The judge complements rather than replaces human review.

### 5.9 Ragas Automated Evaluation

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

- Retrieval quality was evaluated against the retrieved approved-KB chunks.
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

Required report interpretation:

> Standard RAG evaluation often assumes that a response is supported only by retrieved documents. This project uses a hybrid architecture in which the explanation is generated from deterministic structured facts and retrieved guidance. Faithfulness therefore had to be evaluated against the complete legitimate generation context.

Primary Ragas finding:

- Retrieval alignment is the main weakness.
- Exact preferred chunk hit: 3/12.
- Semantically adequate context: 6/12.
- Controlled queries sometimes retrieved generic evidence guidance rather than guidance specific to the triggering rule.
- This affected analyst-guidance relevance but did not change deterministic outcomes.

### 5.10 Final Held-Out Evaluation

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
- the response-authority guardrail failing,
- or adversarial override.

The final response continued to match the deterministic outcome in every case.

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
- suspension periods,
- waiting periods,
- missing incident dates,
- contradictory dates,
- timezone and date-format handling.

#### 6. Targeted future regression coverage

Create future regression tests for the six documented failure patterns.

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

### Section 1 — Executive Summary

Include:

- business problem,
- solution summary,
- primary result,
- safety result,
- material limitation,
- final assessment.

### Section 2 — Business Problem and Objectives

Include:

- claims-triage problem,
- stakeholders,
- four triage outcomes,
- approved proposal objectives,
- measurable success criteria,
- human-control boundary.

### Section 3 — Data and Knowledge Preparation

Include:

- synthetic dataset design,
- dataset volumes,
- legal and privacy safeguards,
- development and held-out partitioning,
- data validation,
- KB registry,
- section-aware chunking,
- provenance and synthetic-data limitations.

### Section 4 — Solution Architecture and Design Rationale

Include:

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

1. End-to-end architecture
2. LangGraph orchestration
3. Retrieval pipeline
4. One Claim Journey

### Section 5 — Implementation

Include:

- modular repository structure,
- key deterministic tools,
- rule precedence,
- corpus builder,
- FAISS persistence and validation,
- controlled query design,
- follow-up catalogue,
- prompts,
- guardrails,
- testing strategy.

### Section 6 — Design Evolution and Transparency Log

Include:

- why uncontrolled follow-up generation became approved-catalogue selection,
- why customer narrative was excluded from authoritative RAG queries,
- why TF-IDF was used for the lexical baseline,
- why `text-embedding-3-small` and FAISS were selected,
- reranker improvements and regressions,
- why the reranker remained optional,
- initial KB-only Ragas faithfulness limitation,
- move to complete authoritative support context,
- LLM-judge calibration refinement,
- frozen held-out protocol,
- six-case unsafe-routing limitation.

### Section 7 — Evaluation Methodology

Include:

- unit and regression tests,
- retrieval benchmark,
- generation human review,
- LLM-as-judge calibration,
- Ragas,
- frozen held-out evaluation,
- held-out safety gate.

### Section 8 — Results

Include:

- 149 passing tests,
- four-method retrieval metrics,
- reranker comparison,
- human-review scores,
- judge calibration,
- Ragas metrics,
- 55-claim held-out results,
- confusion matrix,
- per-class metrics,
- 8-case safety results.

### Section 9 — Limitations and Production Readiness

Include:

- six incorrect `PROCEED` cases,
- 10.9% unsafe-decision diagnostic,
- root causes,
- fail-safe routing,
- `UNABLE_TO_EVALUATE`,
- stronger structured conflicts and exclusions,
- date logic,
- rule-aware retrieval,
- production governance.

### Section 10 — Business Impact and Conclusion

Include:

- analyst consistency,
- traceability,
- reduced unsupported automation risk,
- human accountability,
- proposal-versus-outcome summary,
- final conclusion: `MET_WITH_DOCUMENTED_LIMITATION`.

---

## 8. Executive Presentation Evidence Plan

The final presentation must contain 8–12 slides.

Recommended 10-slide structure:

1. **Problem and Business Opportunity**
2. **Scope, Users, and Human-Control Boundary**
3. **Synthetic Data and Knowledge Sources**
4. **End-to-End Architecture**
5. **One Claim Journey**
6. **Retrieval, FAISS, and Reranking**
7. **Evaluation Framework: Human Review, LLM Judge, and Ragas**
8. **Held-Out Results and Proposal Success**
9. **Material Limitation and Production Improvements**
10. **Business Value and Final Conclusion**

Presentation rules:

- Use a simplified LangGraph diagram.
- Use visuals rather than dense technical text.
- Highlight 89.1% accuracy against the 80% target.
- Show 8/8 safety cases passed and zero critical failures.
- Do not hide the six incorrect `PROCEED` recommendations.
- Distinguish capstone prototype success from production readiness.
- Close with `MET_WITH_DOCUMENTED_LIMITATION`.

---

## 9. Remaining Final-Submission Work

### Mandatory work

1. Prepare the 10–15 page final technical report.
2. Create the final report diagrams:
   - end-to-end architecture,
   - LangGraph orchestration flow,
   - retrieval pipeline,
   - One Claim Journey.
3. Add a concise design-evolution and transparency-log section to the report.
4. Prepare the 8–12 slide executive presentation.
5. Perform clean-copy reproducibility validation.
6. Check the repository for:
   - API keys and secrets,
   - personal absolute paths,
   - temporary or generated local files,
   - stale references,
   - broken repository links.
7. Confirm all notebooks are saved with their intended final outputs.
8. Confirm evaluation manifests match the committed artifacts.
9. Revalidate that the held-out prediction SHA-256 remains unchanged.
10. Create and complete the final submission checklist.
11. Review the report, presentation, README, and repository against this evidence matrix.
12. Merge `final-submission-dev` into `main` only after final QA.
13. Create the final release tag without modifying `mid-submission-v1`.

### Completed packaging work

- Final regression suite completed: 149 tests passed.
- Final test result recorded in the README and this matrix.
- Final README completed and committed.
- Final reviewer walkthrough completed and committed.
- Actual compiled LangGraph included in the reviewer walkthrough.
- Held-out prediction SHA-256 verified by the reviewer walkthrough.
- Final rubric evidence matrix updated through the held-out evaluation phase.

### No further model or workflow tuning

Because held-out labels have been revealed:

- do not modify the frozen workflow to improve the 55-claim score,
- do not regenerate the frozen prediction artifact,
- do not alter the held-out labels,
- do not present a post-hoc tuned score as the final held-out result.

Any proposed technical correction must be described as future production-readiness work.

---

## 10. Recommended Remaining Execution Order

1. Draft the final technical report.
2. Create the four required report diagrams.
3. Add the design-evolution and transparency-log section.
4. Review the report against the proposal and university rubric.
5. Create the executive presentation using the approved report narrative and diagrams.
6. Perform clean-copy reproducibility validation.
7. Perform secrets, paths, links, filenames, notebook, and artifact checks.
8. Complete the final submission checklist.
9. Review the report, presentation, README, and repository against this matrix.
10. Confirm the final working tree is clean.
11. Merge the validated `final-submission-dev` branch into `main`.
12. Create the final release tag.
13. Verify that the submitted repository URL resolves to the final release.

---

## 11. Stop Rules

Do not add new work when any of the following applies:

- It is not required by the approved proposal or university rubric.
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
- [ ] All notebooks are saved with their intended final outputs.
- [ ] All committed evaluation artifacts exist and are non-empty.
- [ ] Evaluation manifests reference the correct files.
- [x] Held-out prediction SHA-256 remains unchanged and was verified by the final reviewer walkthrough.
- [x] Development and held-out evidence remain clearly separated.
- [x] Held-out results are explicitly marked as not used for tuning.
- [ ] Clean-clone or clean-copy installation and test execution succeeds.

### Evaluation evidence

- [x] Retrieval benchmark completed.
- [x] Cross-encoder comparison completed.
- [x] Retrieval error analysis completed.
- [x] Generation-quality evaluation completed.
- [x] Human review completed.
- [x] LLM-judge evaluation completed.
- [x] Human-versus-judge calibration completed.
- [x] Ragas evaluation completed.
- [x] 55-claim held-out evaluation completed.
- [x] Held-out predictions frozen before label comparison.
- [x] 8-case held-out safety evaluation completed.
- [x] Zero critical held-out safety failures recorded.
- [x] Six unsafe-routing errors documented transparently.

### Documentation and reviewer evidence

- [x] README updated for final submission.
- [x] Final reviewer walkthrough completed.
- [x] Actual compiled LangGraph included in the reviewer walkthrough.
- [x] Final evidence matrix updated through the held-out phase.
- [ ] Design-evolution and transparency log included in the report.
- [ ] Technical report completed and limited to 10–15 pages.
- [ ] Executive presentation completed and limited to 8–12 slides.
- [ ] End-to-end architecture diagram included.
- [ ] LangGraph orchestration flowchart included.
- [ ] Retrieval pipeline diagram included.
- [ ] One Claim Journey diagram and walkthrough included.
- [ ] Limitations and production-readiness improvements included.
- [ ] Proposal-versus-outcome assessment included.
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
- Frozen 55-claim held-out evaluation
- Held-out adversarial safety gate
- Approved proposal success assessment
- Documented held-out limitations
- Final regression validation
- Final README
- Final reviewer walkthrough
- Actual compiled LangGraph visualisation
- Frozen prediction SHA-256 verification

### Remaining documentation and packaging evidence

- Final technical report
- Design-evolution and transparency-log section
- End-to-end architecture diagram
- LangGraph orchestration flowchart for report and presentation
- Retrieval pipeline diagram
- One Claim Journey diagram and detailed walkthrough
- Executive presentation
- Clean-copy reproducibility proof
- Secrets, paths, links, notebooks, and artifact QA
- Final submission checklist
- Final proposal and rubric review
- Final merge and release tag

---

## 14. Final Project Position

The project has completed its technical implementation, systematic evaluation, README, and final reviewer-walkthrough phases.

The system:

- exceeded the primary held-out accuracy target,
- preserved deterministic authority,
- maintained authorised human control,
- passed the held-out adversarial safety gate,
- provided controlled analyst guidance,
- produced reproducible committed evaluation evidence,
- and verified its frozen prediction fingerprint.

The system also demonstrated a material limitation:

- six held-out claims were incorrectly routed to `PROCEED`.

The final submission must therefore present the project as:

> A successful, evaluated capstone decision-support prototype that met the approved proposal criteria, while requiring fail-safe routing and stronger structured deterministic-rule coverage before production use.