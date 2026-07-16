# Device Protection Claims Triage

## A Rule-Grounded Agentic AI Decision-Support System

**Final Technical Report**

**Programme:** Executive Diploma in Machine Learning and Artificial Intelligence  
**Specialisation:** Generative AI  
**Project Type:** Bring Your Own Capstone  
**Author:** Sadiq Sulaiman Sheik  
**Repository:** https://github.com/sadiqs3/DP_claims_triage  

---

## Executive Summary

Device-protection claims require analysts to evaluate multiple interconnected factors, including policy validity, protected-device identity, incident coverage, prior-claim limits, evidence sufficiency, exclusions, and risk indicators. While deterministic rules are appropriate for authoritative eligibility checks, analysts may still need to navigate fragmented information and operational guidance. An unrestricted large language model, however, could produce plausible but unsupported interpretations when claim facts are incomplete, contradictory, or outside its authority.

This capstone developed a rule-grounded Agentic AI decision-support system that combines deterministic business-rule execution with controlled retrieval and generative AI assistance. The system produces one of four internal triage recommendations: `PROCEED`, `INFO_REQUIRED`, `MANUAL_REVIEW`, or `NOT_ELIGIBLE`. These outcomes support an analyst’s next action; they do not constitute claim approval, final denial, payment authorisation, or fraud determination.

The implementation uses modular deterministic tools to evaluate policy, plan, device, coverage, claim history, evidence, and risk facts. LangGraph coordinates the workflow through deterministic triage, approved follow-up-question selection, controlled retrieval, explanation generation, and safety validation. The Retrieval-Augmented Generation layer uses seven approved synthetic knowledge documents divided into 21 section-aware chunks, `text-embedding-3-small` embeddings, and a persisted FAISS `IndexFlatIP` index. A cross-encoder reranker was evaluated as an optional second-stage retrieval component. Retrieved guidance and LLM-generated explanations remain non-authoritative and cannot change the deterministic outcome or triggering rule.

The project used a purpose-built, domain-representative synthetic dataset to avoid the privacy, intellectual-property, and legal-use risks associated with real customer claims and proprietary policy documents. The dataset contained 220 new claims, divided into 165 development cases and 55 held-out cases. Development and held-out claim identifiers were verified as disjoint. Final predictions were frozen and assigned a SHA-256 fingerprint before the held-out labels were joined, and the revealed results were not used for subsequent tuning.

Evaluation included 149 regression tests, a 14-query retrieval benchmark, 12 frozen generation-quality cases, documented human review, LLM-as-judge calibration, automated Ragas evaluation, and eight held-out adversarial safety cases. Semantic retrieval achieved the strongest aggregate retrieval result, with Hit@1 of 78.6%, Hit@3 of 92.9%, and MRR@3 of 0.857. The cross-encoder improved two queries but regressed two others, so it was retained as a controlled optional stage rather than the default.

On the frozen 55-claim held-out set, the system correctly classified 49 claims, achieving 89.1% disposition accuracy against the approved target of at least 80%. Policy-rule adherence was 89.1%, exact primary-rule agreement was 87.3%, follow-up requirement accuracy was 100%, and exact follow-up selection was 93.3%. All eight held-out safety cases passed with zero critical safety failures, while deterministic authority and the authorised human-control boundary were preserved in every evaluated case.

A material limitation was also identified. Six ordinary held-out claims were incorrectly routed to `PROCEED`, producing an unsafe-decision diagnostic of 10.9%. Error analysis showed that these failures arose from gaps in structured authoritative data and deterministic rule coverage, including unresolved conflicts, exclusions, and eligibility-date conditions. They were not caused by RAG, LLM generation, or guardrail override.

The project demonstrates that deterministic decision authority can be combined with controlled Agentic AI and RAG to improve the consistency, traceability, and explainability of claims-triage support. However, fail-safe routing, explicit `UNABLE_TO_EVALUATE` states, and stronger structured rule coverage are required before production use. The final project assessment is therefore **`MET_WITH_DOCUMENTED_LIMITATION`**.

---

## 1. Introduction & Business Context

### 1.1 Operational Problem

Device-protection claim triage requires analysts to combine information from several authoritative sources before determining the appropriate next action. Relevant factors may include policy status, registered device details, plan configuration, incident coverage, previous claim usage, evidence sufficiency, exclusions, and risk or anomaly indicators.

Although each check can be expressed individually, the overall process is complex because the conditions must be evaluated in a defined order. A claim may involve a covered incident but still require additional evidence, exceed a claim limit, contain conflicting identifiers, fall outside the active policy period, or require specialist review. Applying only one condition in isolation could therefore produce an unsafe or operationally incorrect recommendation.

Manual claim triage may also be affected by fragmented information, variation in analyst experience, repeated searches across procedures, and inconsistent interpretation of supporting guidance. These conditions can reduce traceability and make it difficult to explain why a particular claim was allowed to continue, paused for evidence, escalated, or considered ineligible.

A conventional rule engine can provide consistent policy and eligibility checks, but it does not by itself address every analyst-support need. Analysts may still require:

- relevant procedural guidance;
- a concise explanation of the evaluated facts;
- visibility of missing evidence;
- standard follow-up wording;
- a traceable summary of the rule that triggered the recommendation.

Conversely, allowing a large language model to independently interpret policy and select a claim outcome would introduce significant risk. An LLM may generate fluent but unsupported conclusions, particularly where information is incomplete, contradictory, or expressed only in unverified narrative text.

The project therefore addresses the following central question:

> How can deterministic policy and eligibility rules be combined with controlled Agentic AI, Retrieval-Augmented Generation, and guardrails to support device-protection claim triage while preserving traceability, safety, and authorised human control?

The solution is designed as an internal decision-support prototype rather than an autonomous claim-adjudication system.

### 1.2 Stakeholders and Business Stakes

The primary user is a claims analyst who requires a clear recommendation supported by authoritative facts and relevant operational guidance. Other stakeholders include operations managers, policy and product teams, risk and compliance functions, technology teams, and customers indirectly affected by claim-handling consistency.

| Stakeholder | Primary requirement |
|---|---|
| Claims analysts | Clear recommendation, triggering rule, missing evidence, and relevant guidance |
| Claims operations managers | Consistent triage, measurable performance, and operational traceability |
| Policy and product teams | Correct application of plan configuration, coverage, and eligibility rules |
| Risk and compliance teams | Prevention of unsupported automation and preservation of human accountability |
| Technology teams | Modular, testable, reproducible, and maintainable implementation |
| Customers | Fair and consistent handling with an authorised human retaining final responsibility |

The principal business risks addressed by the project are:

- inconsistent application of policy and evidence rules;
- excessive analyst effort spent locating relevant guidance;
- insufficient visibility of the reason behind a recommendation;
- uncontrolled generation of customer follow-up questions;
- unsupported LLM interpretation of policy conditions;
- unsafe continuation of claims that require review or should not proceed;
- weak auditability of automated recommendations.

The project does not claim measured financial savings, reduced handling time, or production-level operational improvement because these outcomes were not evaluated in a live environment. Instead, it demonstrates the technical feasibility of improving consistency, explainability, and control within a bounded synthetic setting.

### 1.3 Project Objectives and Success Criteria

The project had six principal objectives:

1. implement modular deterministic tools for policy, eligibility, coverage, evidence, history, and risk evaluation;
2. apply explicit rule precedence to produce a traceable triage recommendation;
3. use LangGraph to orchestrate deterministic tools, retrieval, generation, and guardrails;
4. retrieve approved operational guidance through controlled RAG and FAISS;
5. generate safe analyst-facing explanations without transferring decision authority to the LLM;
6. evaluate the complete workflow using retrieval metrics, human review, LLM judging, Ragas, regression tests, and a frozen held-out dataset.

The approved primary success criterion was:

> Achieve at least 80% agreement with ground-truth triage outcomes across 55 held-out claims.

Supporting evaluation measures were included to provide a more complete view of system performance:

- policy-rule adherence;
- exact triggering-rule agreement;
- follow-up requirement accuracy;
- exact follow-up-question selection;
- manual-review precision and recall;
- unsafe-decision rate;
- adversarial safety performance;
- preservation of deterministic authority;
- preservation of authorised human control.

The approved safety gate required zero critical failures in the final held-out adversarial evaluation. A critical failure would include behaviour such as:

- autonomous approval or denial;
- payment or settlement authorisation;
- fraud determination;
- fabrication of policy or evidence;
- successful override of the deterministic outcome;
- removal of the human-control boundary.

### 1.4 Scope and Human-Control Boundary

The system produces one of four internal triage recommendations.

| Outcome | Operational interpretation |
|---|---|
| `PROCEED` | Available authoritative facts support continuation to standard processing; this is not a claim approval |
| `INFO_REQUIRED` | Defined evidence or information is missing and an approved follow-up is required |
| `MANUAL_REVIEW` | A conflict, anomaly, risk indicator, unsupported condition, or evaluation uncertainty requires authorised review |
| `NOT_ELIGIBLE` | Deterministic rules support a non-eligibility recommendation; this is not a final customer-facing denial |

The implemented scope includes:

- synthetic claim and policy data preparation;
- deterministic policy and eligibility evaluation;
- evidence, history, limit, and risk checks;
- rule-precedence-based triage;
- controlled follow-up-question selection;
- LangGraph workflow orchestration;
- controlled RAG over an approved knowledge base;
- FAISS semantic retrieval;
- optional cross-encoder reranking;
- LLM-based analyst explanation;
- content-safety and response-authority guardrails;
- systematic development and held-out evaluation.

The following actions remain explicitly outside the autonomous system boundary:

- claim approval;
- final claim denial;
- payment or settlement authorisation;
- fraud determination;
- unrestricted customer communication;
- use of unverified narrative as authoritative policy evidence;
- live enterprise-system integration;
- production deployment;
- user-interface development.

The governing design principle is:

> Deterministic rules evaluate authoritative claim facts; LangGraph coordinates the workflow; RAG retrieves non-authoritative operational guidance; the LLM explains the result; and an authorised human remains accountable for the final action.

This separation of responsibilities is central to the project’s technical, ethical, and operational design.

---

## 2. Data Architecture & Methodology

### 2.1 Synthetic Data and Governance

Real device-protection claims may contain personally identifiable information, device identifiers, financial details, policy records, incident narratives, and internal operational decisions. Production policy rules and claims procedures may also contain proprietary organisational information. These constraints made real enterprise data unsuitable for a public academic repository.

The project therefore used a purpose-built, domain-representative synthetic data ecosystem. The objective was not to reproduce any specific organisation’s data, but to model the principal entities and relationships required for device-protection claim triage.

The synthetic ecosystem includes:

- policy and protected-device records;
- plan configuration and product eligibility;
- coverage by incident type;
- policy status and incident dates;
- prior-claim history and usage limits;
- evidence bundles and document records;
- risk and anomaly indicators;
- approved operational knowledge documents;
- controlled follow-up questions;
- expected triage outcomes and triggering rules.

The dataset was designed to represent routine, incomplete, conflicting, and boundary scenarios across the four target outcomes: `PROCEED`, `INFO_REQUIRED`, `MANUAL_REVIEW`, and `NOT_ELIGIBLE`.

**Table 2.1 — Final dataset and evaluation volumes**

| Dataset component | Records |
|---|---:|
| Policy-device records | 120 |
| Historical claims | 112 |
| New claims | 220 |
| Development claims | 165 |
| Held-out claims | 55 |
| Evidence bundles | 220 |
| Evidence document records | 283 |
| Knowledge-base documents | 7 |
| Knowledge-base chunks | 21 |
| Approved follow-up questions | 14 |
| Ground-truth labels | 220 |
| Safety and adversarial cases | 24 |
| Held-out safety cases | 8 |

The following governance controls were applied:

- all claim and policy records are synthetic;
- no real customer PII is included;
- no production claims or proprietary enterprise documents are reproduced;
- knowledge sources are explicitly allow-listed;
- development and held-out claim identifiers are disjoint;
- customer narrative is not treated as verified policy evidence;
- held-out predictions were frozen before label comparison;
- held-out results were not used for subsequent tuning.

The synthetic design supports legal usability, reproducibility, and public academic review. However, it cannot reproduce the full variability, ambiguity, missingness, behavioural patterns, or operational complexity of a production claims portfolio. Results must therefore be interpreted as prototype evidence under controlled synthetic conditions.

### 2.2 Data Preparation and Held-Out Design

The project used controlled CSV and JSON records together with Markdown knowledge documents. Optical Character Recognition and complex PDF-layout extraction were not required because the selected sources did not contain scanned or layout-dependent documents.

Data preparation focused on structural quality and referential integrity.

The principal validation activities included:

- confirmation of expected schemas and mandatory fields;
- validation of supported categorical values;
- claim-to-policy and policy-to-device relationship checks;
- evidence-bundle and evidence-document linkage checks;
- historical-claim relationship checks;
- date normalisation for policy and incident evaluation;
- validation of ground-truth claim identifiers;
- verification that development and held-out partitions were disjoint;
- confirmation that runtime inputs excluded held-out labels.

The 220 new claims were divided into:

- 165 development claims;
- 55 held-out claims.

The development partition was used for implementation, debugging, retrieval benchmarking, generation-quality evaluation, and safety testing. The held-out partition was reserved for final evaluation.

The final held-out protocol followed these steps:

1. freeze the workflow and evaluation configuration;
2. execute all 55 held-out claims without consulting labels;
3. export the prediction-only artifact;
4. calculate a SHA-256 fingerprint;
5. join the ground-truth labels only after predictions were frozen;
6. calculate the approved metrics;
7. document errors without retuning the workflow.

The frozen prediction fingerprint is:

`0a20deead9d8fdcf75b740d39d11f8ff3934cb173da55c02ec61c860c92e2a1f`

This process reduced the risk of post-hoc optimisation and preserved the integrity of the reported held-out result.

### 2.3 Architecture and Authority Boundaries

The solution uses a hybrid architecture that separates authoritative business-rule execution from non-authoritative AI support.

The principal components are:

1. structured claim and reference data;
2. deterministic policy, eligibility, evidence, history, and risk tools;
3. rule precedence and authoritative triage outcome;
4. controlled follow-up-question selection;
5. controlled RAG over an approved knowledge base;
6. LLM-based analyst explanation;
7. content-safety and response-authority guardrails;
8. authorised human review.

**Figure 1 — End-to-End System Architecture**

![End-to-end architecture of the rule-grounded claims-triage system](figures/figure_1_end_to_end_architecture.svg)

*The architecture separates authoritative deterministic decision-making from non-authoritative retrieval and LLM explanation. LangGraph coordinates the workflow, guardrails protect the deterministic result, and an authorised human retains final accountability.*

The architecture follows a strict responsibility model.

| Component | Responsibility | Authority |
|---|---|---|
| Deterministic tools | Evaluate policy, plan, device, coverage, evidence, limits, conflicts, and risk | Authoritative |
| Rule-precedence engine | Select the triage outcome and triggering rule | Authoritative |
| LangGraph | Coordinate tools, retrieval, generation, and guardrails | Orchestration only |
| Follow-up selector | Select an approved catalogue question | Catalogue-controlled |
| RAG and FAISS | Retrieve relevant operational guidance | Non-authoritative |
| Cross-encoder | Optionally reorder approved retrieved chunks | Non-authoritative |
| LLM explanation | Produce analyst-facing explanation support | Non-authoritative |
| Content-safety guardrail | Block prohibited generated behaviour | Protective control |
| Response-authority guardrail | Preserve deterministic outcome and rule | Protective control |
| Authorised human | Determine final operational action | Final accountability |

The governing principle is:

> Deterministic rules determine the recommendation; Agentic AI coordinates the workflow; RAG retrieves approved guidance; the LLM explains the result; and an authorised human remains accountable for final action.

This architecture prevents retrieval or generation components from independently changing policy eligibility, coverage, evidence requirements, claim limits, exclusions, or final triage outcomes.

### 2.4 Knowledge Base, Embeddings, and Retrieval

The RAG component uses seven allow-listed synthetic operational knowledge documents. These documents provide guidance on evidence handling, escalation, review expectations, and analyst procedures. They do not determine claim eligibility.

The corpus builder divides the documents into 21 section-aware chunks. Each chunk represents a coherent procedural section and retains metadata identifying its source document and section.

Overlapping chunks were not used because the source documents were short and structurally organised. Overlap would have introduced duplicate guidance and near-identical retrieval results. The frozen retrieval benchmark did not provide evidence that a different chunking strategy was required.

The controlled retrieval pipeline is:

1. load allow-listed knowledge documents;
2. create section-aware chunks;
3. generate semantic embeddings;
4. build or load the persisted FAISS index;
5. construct a query from authoritative triage facts;
6. retrieve the highest-ranked chunks;
7. optionally apply cross-encoder reranking;
8. format the retrieved content as analyst guidance.

**Figure 2 — Controlled Retrieval Pipeline**

![Controlled retrieval pipeline showing knowledge-base preparation, query construction, FAISS retrieval, optional reranking, and index validation](figures/figure_2_controlled_retrieval_pipeline.svg)

*The retrieval pipeline uses only allow-listed knowledge documents and authoritative structured triage facts. Customer narrative and identifiers are excluded from the controlled query. Corpus and chunk-order fingerprints protect the persisted FAISS index from stale or mismatched use, while retrieved content remains non-authoritative analyst guidance.*

The semantic configuration is shown in Table 2.2.

**Table 2.2 — Semantic retrieval configuration**

| Component | Configuration |
|---|---|
| Embedding model | `text-embedding-3-small` |
| Embedding dimension | 1536 |
| Vector index | FAISS `IndexFlatIP` |
| Search type | Exact inner-product search |
| Approved corpus size | 21 chunks |
| Cross-encoder | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Reranker status | Controlled optional stage |

FAISS `IndexFlatIP` was appropriate because the corpus was small and exact search avoided the complexity of approximate indexing.

The persisted index includes controls for:

- vector dimension;
- embedding model;
- expected chunk count;
- corpus fingerprint;
- stable chunk-order fingerprint;
- index-to-corpus consistency;
- stale-index detection.

A mismatch between the current corpus and the persisted index blocks normal loading and requires a controlled rebuild.

The retrieval query is not created from unrestricted customer narrative. It is built from an allow-listed projection of authoritative facts, such as:

- deterministic outcome;
- triggering rule;
- claim category;
- coverage status;
- evidence status;
- missing evidence codes;
- manual-review requirement.

This reduces prompt-injection exposure and prevents unverified narrative from influencing operational guidance as though it were an established policy fact.

### 2.5 Design Evolution and Methodological Choices

The final implementation was refined through evaluation and safety analysis rather than following every initial assumption unchanged.

**Table 2.3 — Principal design refinements**

| Initial assumption | Final implementation | Rationale |
|---|---|---|
| LLM-generated follow-up questions | Selection from an approved 14-question catalogue | Improved consistency, auditability, safety, and exact evaluation |
| Use of customer narrative in retrieval | Controlled query from authoritative structured facts | Prevented unverified or adversarial narrative from influencing guidance |
| Lexical retrieval based on planned BM25-style approach | TF-IDF lexical baseline | Transparent and sufficient for comparison on the small corpus |
| Semantic retrieval plus default reranking | Semantic retrieval default; reranker optional | Reranker produced mixed improvements and regressions |
| Faithfulness evaluated only against KB chunks | Evaluated against structured facts plus retrieved guidance | Reflected the actual hybrid generation context |
| LLM judge used independently | Judge calibrated against human review | Avoided treating an automated evaluator as ground truth |
| Final evaluation against visible labels | Predictions frozen before label reveal | Reduced leakage and post-hoc tuning risk |

The reranker was retained because second-stage scoring was a required and technically valid component. However, the frozen benchmark showed no aggregate improvement over semantic retrieval. It therefore remained available as a controlled optional stage rather than being enabled by default.

The Ragas methodology also required adaptation. A standard document-only faithfulness assessment penalised statements that were correctly grounded in deterministic structured facts but absent from retrieved KB chunks. The final approach evaluated response faithfulness against the complete legitimate generation context: authoritative structured facts plus retrieved guidance.

Similarly, the LLM-as-judge evaluation was compared with a documented human baseline. The judge broadly aligned with human scores for groundedness, answer relevance, and hallucination control, but was more generous when scoring context relevance. Automated judging was therefore retained as supplementary evidence rather than a replacement for human assessment.

These methodological choices narrowed generative authority, improved reproducibility, and aligned the evaluation with the actual hybrid architecture.

---

## 3. Implementation & Results

### 3.1 Implementation Pipeline

The solution was implemented as a modular Python project rather than as a notebook-only prototype. Reusable logic is separated across deterministic tools, orchestration, retrieval, generation, guardrails, evaluation utilities, and tests. Notebooks are used to demonstrate the implementation stages and preserve evaluation evidence.

The principal processing sequence is summarised in Table 3.1.

**Table 3.1 — Implemented workflow stages**

| Stage | Implementation responsibility |
|---|---|
| Claim intake | Load and validate the claim and linked runtime records |
| Deterministic tools | Evaluate policy, plan, device, coverage, history, evidence, and risk facts |
| Rule precedence | Select the authoritative disposition and triggering rule |
| Controlled follow-up | Select an approved catalogue question where information is missing |
| Controlled query | Project allow-listed authoritative facts into a retrieval query |
| FAISS retrieval | Retrieve approved operational guidance |
| Cross-encoder | Optionally rerank the bounded candidate set |
| LLM explanation | Produce non-authoritative analyst-facing guidance |
| Content-safety guardrail | Detect prohibited or unsafe generated behaviour |
| Response-authority guardrail | Preserve the deterministic outcome, rule, and controlled fields |
| Human review | Determine the final operational or customer-facing action |

LangGraph represents this process as an explicit stateful workflow. The compiled implementation, identified as `langgraph_v6`, uses the following node sequence:

1. `deterministic_triage`
2. `controlled_follow_up_selection`
3. `controlled_rag_retrieval`
4. `explanation_proposal`
5. `agent_content_safety_guardrail`
6. `response_guardrail`

The workflow state progressively records the deterministic result, approved follow-up selection, retrieval context, generated explanation, safety status, and final protected response. Deterministic triage is completed before retrieval or generation, preventing AI-support components from influencing the creation of the authoritative outcome.

**Figure 3 — LangGraph Orchestration Flow**

![LangGraph orchestration flow showing deterministic triage, controlled retrieval, explanation generation, guardrails, and authorised human review](figures/figure_3_langgraph_orchestration_flow.svg)

*The workflow completes deterministic triage before retrieval or generation. Controlled RAG may be enabled or bypassed without changing the authoritative result. The content-safety guardrail replaces prohibited generated content, while the response-authority guardrail restores protected deterministic values when an override is detected. Final operational responsibility remains with an authorised human reviewer.*

The deterministic layer is composed of specialised tools for policy lookup, plan configuration, policy eligibility, device match, incident coverage, claims history, evidence lookup, evidence assessment, and risk indicators. Their structured outputs are consolidated into an authoritative claim context and evaluated through explicit rule precedence.

The retrieval query is built from an allow-listed `AuthoritativeTriageFacts` projection rather than from unrestricted customer narrative. This projection may contain the disposition, triggering rule, claim category, service type, coverage status, evidence state, missing evidence codes, and manual-review requirement. Customer statements, arbitrary free text, identifiers, and generated reasons are excluded.

The resulting architecture preserves three distinct evidence categories:

- authoritative structured facts produced by deterministic tools;
- non-authoritative guidance retrieved from the approved knowledge base;
- non-authoritative explanatory text produced by the LLM.

This separation is retained in the final response and evaluation artifacts.

### 3.2 One Claim Journey

A representative frozen development case, `GEN-001`, demonstrates how one claim passes through the complete workflow. The associated claim is `CLM-000001`, a screen-damage repair case.

**Figure 4 — One Claim Journey**

![Journey of claim CLM-000001 through deterministic evaluation, controlled retrieval, explanation, guardrails, and human review](figures/figure_4_one_claim_journey.svg)

*The representative development claim `CLM-000001` was matched to an active `DP-ESSENTIAL` policy, confirmed as in scope and covered, and assessed as having sufficient evidence with no risk indicators. Rule precedence produced `OUT-001 → PROCEED`. Controlled retrieval supplied evidence-handling guidance, while the LLM explanation remained non-authoritative. The final response passed the content-safety and authority guardrails before being presented for authorised human review.*

**Table 3.2 — Representative journey for claim `CLM-000001`**

| Journey stage | Actual project output | Authority role |
|---|---|---|
| Policy lookup | `UNIQUE_MATCH`; plan `DP-ESSENTIAL` | Authoritative |
| Plan configuration | `ACTIVE_CONFIGURATION_AVAILABLE`; product `IN_SCOPE` | Authoritative |
| Policy and device | `ACTIVE_ON_INCIDENT_DATE`; `DEVICE_MATCH` | Authoritative |
| Coverage | `UNIQUE_COVERAGE_RECORD`; `covered_flag = True` | Authoritative |
| Claims history | Annual claims used: 0 of 1; theft limit not applicable | Authoritative |
| Evidence assessment | Profile `EVD-SCREEN-01`; status `SUFFICIENT`; no missing or unreadable required evidence | Authoritative |
| Risk assessment | No triggered risk indicators or manual-review reasons | Authoritative |
| Rule precedence | Earlier rules not triggered; `OUT-001` triggered at stage 6 | Authoritative |
| Deterministic outcome | `PROCEED` | Authoritative recommendation |
| Follow-up selection | `NOT_REQUIRED`; no question selected | Catalogue-controlled |
| Controlled query | Constructed from outcome, rule, claim category, service type, coverage, evidence, and device-match status | Deterministic projection |
| Retrieved guidance | `KB-002::S03`, `KB-001::S01`, and `KB-002::S01` | Non-authoritative |
| Highest-ranked guidance | Evidence Review Guide, “Evidence profiles”; confirms `EVD-SCREEN-01` requires a damage photo | Non-authoritative |
| Reranking | Candidate set reranked using `cross-encoder/ms-marco-MiniLM-L-6-v2` | Non-authoritative |
| Explanation | States that no earlier applicable rule triggered and that `PROCEED` means standard-processing routing only | Non-authoritative |
| Content-safety guardrail | `SAFE`; no fallback required | Protective control |
| Authority guardrail | `ALIGNED`; no conflicting protected fields | Protective control |
| Final response | Outcome `PROCEED`; rule `OUT-001`; authorised analyst retains final control | Protected decision support |

The controlled query for this claim described the authoritative outcome, rule, screen-damage category, repair service, active configuration, in-scope product, confirmed coverage, sufficient evidence, and device match. It explicitly requested approved internal guidance for evidence handling and analyst next steps.

The highest-ranked retrieved chunk was the “Evidence profiles” section of the Evidence Review Guide. It linked screen-damage claims to evidence profile `EVD-SCREEN-01` and identified a damage photo as the primary required evidence. The retrieved material was useful for analyst interpretation but did not create the evidence requirement or determine the outcome.

The generated explanation preserved the deterministic result and clarified that `PROCEED` was not an approval, payout, fraud determination, or final denial. It also retained known system limitations, including rule families that could not be fully evaluated from the available structured sources.

This journey demonstrates the intended separation of responsibilities: deterministic tools establish the result, retrieval provides supporting guidance, the LLM explains the result, guardrails protect it, and the analyst remains accountable for final action.

### 3.3 Testing and Reproducibility

The final regression suite contains 149 passing tests. Coverage includes:

- deterministic triage and rule precedence;
- plan configuration and policy checks;
- controlled follow-up validation and selection;
- lexical, semantic, hybrid, and FAISS retrieval;
- index persistence and stale-index validation;
- cross-encoder reranking;
- controlled query construction;
- LangGraph orchestration;
- analyst-guidance formatting;
- LLM explanation handling;
- content-safety and response-authority guardrails;
- Ragas and LLM-judge evaluation utilities.

The project separates locally reproducible validation from external-model execution. Deterministic tools, guardrails, committed-artifact inspection, fingerprint verification, and regression tests do not require an OpenAI API key. Live embedding generation, explanation generation, and LLM-judge reruns require separately configured model access.

Reproducibility controls include:

- Python and dependency records;
- relative repository paths;
- modular source files;
- committed evaluation cases and results;
- configuration manifests;
- corpus and chunk-order fingerprints;
- persisted FAISS artifacts;
- disjoint development and held-out partitions;
- a frozen held-out prediction artifact;
- SHA-256 verification;
- a final reviewer walkthrough.

The reviewer walkthrough loads the committed evidence, displays the actual compiled LangGraph, verifies expected artifact counts, recalculates the held-out prediction fingerprint, and runs the 149-test suite. It does not regenerate embeddings, call the LLM, rerun Ragas, recreate held-out predictions, or tune the workflow.

### 3.4 Retrieval and Reranking Results

Four retrieval configurations were evaluated on 14 frozen, manually grounded queries at `Top K = 3`.

**Table 3.3 — Retrieval benchmark**

| Retrieval method | Hit@1 | Hit@3 | MRR@3 | No-result rate |
|---|---:|---:|---:|---:|
| Lexical TF-IDF | 57.1% | 85.7% | 0.702 | 0.0% |
| Semantic Embedding | **78.6%** | **92.9%** | **0.857** | 0.0% |
| Hybrid RRF | 71.4% | 92.9% | 0.798 | 0.0% |
| Semantic plus Cross-Encoder | 78.6% | 92.9% | 0.845 | 0.0% |

Semantic retrieval produced the strongest aggregate result. Relative to TF-IDF, it improved Hit@1 by 21.5 percentage points and Hit@3 by 7.2 percentage points. Hybrid RRF matched semantic retrieval at Hit@3 but did not improve its Hit@1 or MRR@3.

The cross-encoder produced mixed case-level behaviour:

- two queries improved;
- two queries regressed;
- nine retained the same Top-1 result;
- one remained a Top-3 miss.

Although Hit@1 and Hit@3 remained unchanged, MRR@3 decreased from 0.857 to 0.845. The reranker was therefore retained as a technically valid second-stage component but classified as a `CONTROLLED_OPTIONAL_STAGE`.

The final retrieval decision was:

- Semantic Embedding as the default method;
- cross-encoder reranking available but not enabled by default;
- no change to section-aware chunking.

The analysis shows that additional model complexity did not automatically improve a small, specialised knowledge corpus. Case-level regression review was therefore necessary in addition to aggregate metrics.

### 3.5 Generation, Human Review, LLM Judge, and Ragas

Generation quality was evaluated using 12 frozen development cases covering all four dispositions. In every case:

- the deterministic outcome matched the final outcome;
- the triggering rule matched the final triggering rule;
- content-safety status was `SAFE`;
- authority-guardrail status was `ALIGNED`;
- no critical human-identified safety failure occurred.

**Table 3.4 — Human generation review**

| Human-review dimension | Mean score |
|---|---:|
| Context relevance | 2.75 / 4 |
| Groundedness | 3.75 / 4 |
| Answer relevance | 3.67 / 4 |
| Hallucination control | 3.75 / 4 |
| Critical safety failures | 0 |

Groundedness, answer relevance, and hallucination control were strong. The lower context-relevance score reflected cases where retrieval returned broad evidence guidance or document-overview sections rather than guidance tightly aligned to the triggering rule.

An LLM-as-judge evaluated the same cases and was calibrated against the documented human review. It broadly aligned with the human reviewer for groundedness, answer relevance, and hallucination control. The largest disagreement concerned context relevance, where the judge frequently rated semantically related passages more highly than the human reviewer rated their practical operational usefulness.

The LLM judge was therefore treated as a repeatable supplementary evaluator, not as an independent ground truth or replacement for human assessment.

Ragas was applied to the same 12 frozen cases.

**Table 3.5 — Automated Ragas evaluation**

| Ragas metric | Mean |
|---|---:|
| Context Precision | 0.576 |
| Context Recall | 0.417 |
| Faithfulness | 0.627 |
| Answer Relevancy | 0.533 |

Context Precision and Context Recall evaluated retrieved knowledge-base chunks against rule-level guidance references. Faithfulness used the complete legitimate generation context: authoritative structured facts plus retrieved KB guidance. This adaptation was required because the architecture is not a document-only RAG system.

Diagnostic review found:

- exact preferred chunk retrieval in 3 of 12 cases;
- semantically adequate context in 6 of 12 cases;
- semantic coverage without the exact preferred chunk in 3 of 12 cases.

The main Ragas finding was therefore a retrieval-alignment weakness rather than a decision-authority failure. The appropriate improvement is more rule-aware retrieval, not additional authority for RAG or the LLM.

### 3.6 Final Held-Out and Safety Results

The frozen workflow was evaluated on 55 held-out claims after predictions had been exported and fingerprinted. No tuning was performed after the labels were joined.

The primary proposal criterion was exceeded:

**Table 3.6 — Final proposal result**

| Metric | Target | Result | Status |
|---|---:|---:|---|
| Held-out disposition accuracy | At least 80% | **49/55, 89.1%** | **PASS** |

Supporting results were:

| Supporting metric | Result |
|---|---:|
| Policy-rule adherence | 89.1% |
| Exact primary-rule agreement | 87.3% |
| Follow-up requirement accuracy | 100.0% |
| Exact follow-up selection | 93.3% |
| Manual-review recall | 78.6% |
| Manual-review precision | 100.0% |
| Authority alignment | 100.0% |
| Human-control preservation | 100.0% |
| Unsafe-decision diagnostic | 10.9% |

**Table 3.7 — Held-out confusion matrix**

| Gold \ Predicted | `PROCEED` | `INFO_REQUIRED` | `MANUAL_REVIEW` | `NOT_ELIGIBLE` |
|---|---:|---:|---:|---:|
| `PROCEED` | 17 | 0 | 0 | 0 |
| `INFO_REQUIRED` | 0 | 15 | 0 | 0 |
| `MANUAL_REVIEW` | 3 | 0 | 11 | 0 |
| `NOT_ELIGIBLE` | 3 | 0 | 0 | 6 |

**Table 3.8 — Per-disposition performance**

| Disposition | Precision | Recall | F1 |
|---|---:|---:|---:|
| `PROCEED` | 0.739 | 1.000 | 0.850 |
| `INFO_REQUIRED` | 1.000 | 1.000 | 1.000 |
| `MANUAL_REVIEW` | 1.000 | 0.786 | 0.880 |
| `NOT_ELIGIBLE` | 1.000 | 0.667 | 0.800 |

All genuine `PROCEED` and `INFO_REQUIRED` cases were classified correctly. The principal weakness was over-routing to `PROCEED`: three `MANUAL_REVIEW` cases and three `NOT_ELIGIBLE` cases were incorrectly allowed to continue. This pattern is more operationally significant than the overall accuracy alone and is examined in Section 5.

Eight separate adversarial and edge cases were used for the final safety gate.

**Table 3.9 — Held-out safety results**

| Safety control | Result |
|---|---:|
| Safety cases passed | 8/8 |
| Deterministic outcome preserved | 8/8 |
| Applicable triggering rule preserved | 6/6 |
| No fabricated rule where none was expected | 2/2 |
| Unsafe override blocked | 8/8 |
| Controlled fallback used | 8/8 |
| Critical safety failures | **0** |

The hard safety gate passed. The LLM and guardrails did not alter the authoritative decision in any held-out safety case, and the authorised human-control boundary was preserved.

However, successful guardrail performance did not correct errors already present in the deterministic result. The six incorrect `PROCEED` outcomes therefore demonstrate that AI-authority controls and deterministic business-rule completeness are separate safety requirements.

---

## 4. Strategic Deductions & Business Impact

### 4.1 Operational Implications

The project demonstrates how deterministic business rules and controlled generative AI can support different parts of the same claims-triage process without sharing decision authority.

The deterministic layer provides consistency in evaluating policy, device, coverage, evidence, claim-history, and risk conditions. LangGraph coordinates the processing sequence, while RAG and the LLM support the analyst by retrieving relevant guidance and presenting the evaluated facts in a concise form.

Within the evaluated prototype, the architecture provides five potential operational benefits.

#### More consistent preliminary triage

The same structured inputs are processed through the same tool and rule-precedence sequence. This reduces dependence on individual interpretation during the initial triage stage and provides a consistent basis for analyst review.

#### Improved traceability

Each recommendation includes a triggering rule, precedence stage, supporting facts, and rule trace. Retrieved guidance and generated explanations remain separately identifiable from authoritative business facts. This enables reviewers to distinguish between:

- facts established by deterministic tools;
- guidance retrieved from the approved knowledge base;
- explanatory text generated by the LLM.

#### Faster access to relevant guidance

The controlled RAG layer retrieves operational guidance using the deterministic outcome, triggering rule, evidence state, coverage result, and review requirement. This can reduce the need for analysts to manually search multiple procedure documents.

The project did not measure production handling time, and no claim is made that the system has already reduced operational cycle time. The evaluation instead demonstrates the technical feasibility of bringing relevant guidance into the triage workflow.

#### Standardised follow-up handling

Selecting from an approved 14-question catalogue ensures that equivalent evidence gaps receive consistent wording. The approach also prevents the LLM from requesting unsupported information or creating uncontrolled customer-facing questions.

#### Reduced risk of unsupported generative decisions

The LLM cannot independently select the disposition or triggering rule. The content-safety and response-authority guardrails also prevent generated text from overriding protected deterministic values.

These controls reduce the risk associated with unrestricted LLM use. However, they do not compensate for missing structured facts or incomplete deterministic rules, as demonstrated by the six held-out routing errors.

### 4.2 Architecture Trade-Offs and Lessons

The implementation and evaluation produced several broader technical deductions.

#### Deterministic rules and generative AI should have distinct responsibilities

Policy eligibility, coverage, evidence requirements, limits, and exclusions require predictable and auditable execution. These responsibilities are therefore assigned to deterministic tools.

Generative AI is more suitable for:

- semantic retrieval;
- explanation;
- summarisation;
- analyst guidance;
- coordination of supporting workflow stages.

The project shows that GenAI can add value without becoming the source of policy authority.

#### Semantic retrieval improved guidance access without becoming authoritative

Semantic Embedding achieved the strongest retrieval performance, with Hit@1 of 78.6%, Hit@3 of 92.9%, and MRR@3 of 0.857. This exceeded the lexical TF-IDF baseline.

The result supports the use of semantic retrieval for specialised operational guidance. It does not imply that semantic similarity should be used to determine policy eligibility or final claim outcomes.

#### Additional model complexity did not guarantee better results

The cross-encoder reranker improved two queries but regressed two others. Aggregate MRR@3 decreased from 0.857 to 0.845.

The decision to retain reranking as an optional stage illustrates that architectural sophistication should not be treated as evidence of improved performance. Component adoption should be based on measured workflow value.

#### Automated RAG metrics must reflect the actual generation context

A standard document-only faithfulness evaluation was not fully appropriate because the explanation was generated from both deterministic structured facts and retrieved guidance.

The final Ragas methodology therefore separated:

- retrieval quality against preferred KB guidance;
- explanation faithfulness against the complete legitimate generation context.

This distinction is important for systems that combine rule engines, databases, tools, and RAG rather than generating responses solely from retrieved documents.

#### LLM judges require human calibration

The LLM judge broadly agreed with human review for groundedness, answer relevance, and hallucination control. It was more generous when assessing context relevance.

The result demonstrates that an automated judge can improve scalability and consistency, but it should not be treated as independent ground truth. Human review remains necessary for dimensions involving operational usefulness, nuance, and domain judgement.

#### Aggregate accuracy can conceal operationally unsafe errors

The held-out accuracy of 89.1% exceeded the approved target. However, all six errors were incorrect `PROCEED` recommendations.

This shows that overall accuracy alone is insufficient for evaluating a claims-triage system. Class-specific recall, confusion patterns, manual-review routing, and unsafe-decision diagnostics are necessary to assess operational risk.

#### Guardrail safety and business-rule completeness are separate controls

The safety guardrails successfully blocked prohibited LLM behaviour and preserved deterministic outcomes. Nevertheless, the guardrails also preserved six incorrect deterministic `PROCEED` outcomes.

A safe production architecture therefore requires both:

1. strong controls preventing AI override;
2. complete and fail-safe deterministic business-rule coverage.

### 4.3 Proposal Commitment versus Final Outcome

Table 4.1 compares the principal proposal commitments with the final implementation and evaluation evidence.

**Table 4.1 — Proposal commitment versus final outcome**

| Proposal commitment | Final outcome | Status |
|---|---|---|
| Implement four triage outcomes | `PROCEED`, `INFO_REQUIRED`, `MANUAL_REVIEW`, and `NOT_ELIGIBLE` implemented | Met |
| Use deterministic policy and eligibility rules | Modular authoritative tools and rule precedence implemented | Met |
| Use Agentic AI orchestration | LangGraph workflow implemented and validated | Met |
| Provide RAG-based operational guidance | Allow-listed KB, semantic retrieval, FAISS, and controlled query implemented | Met |
| Include cross-encoder reranking | Reranker implemented and evaluated as an optional stage | Met |
| Support follow-up questions | Approved catalogue selection implemented instead of unrestricted generation | Met with controlled refinement |
| Generate analyst-facing explanations | Guarded LLM explanation workflow implemented | Met |
| Preserve authorised human control | Human-control boundary preserved in all final evaluation cases | Met |
| Achieve at least 80% accuracy on 55 held-out claims | 49 of 55 claims correct, or 89.1% | Passed |
| Report supporting rule and follow-up metrics | Rule, follow-up, manual-review, and unsafe-decision metrics reported | Met |
| Achieve zero critical held-out safety failures | Zero critical failures across 8 held-out safety cases | Passed |
| Avoid use of real customer or proprietary data | Purpose-built synthetic ecosystem used | Met |
| Deliver reproducible technical evidence | 149 tests, manifests, frozen outputs, SHA-256, and reviewer walkthrough provided | Substantially met; final clean-copy QA pending |
| Demonstrate production readiness | Six unsafe `PROCEED` errors require further deterministic controls | Not claimed |

The project also introduced controlled refinements to the proposal:

- unrestricted follow-up generation was replaced by approved-catalogue selection;
- unverified customer narrative was excluded from authoritative decision-making and controlled retrieval queries;
- TF-IDF was used as the lexical baseline;
- semantic retrieval became the default after comparative evaluation;
- reranking remained optional because it did not improve aggregate performance;
- automated evaluation was adapted to the hybrid structured-fact and document context.

These refinements preserved the approved business problem while strengthening safety, auditability, and methodological validity.

### 4.4 Business Impact Position

The evaluated prototype indicates potential value in three areas:

1. **Operational consistency:** deterministic rule execution can provide a repeatable initial recommendation and standard follow-up selection.
2. **Analyst effectiveness:** retrieval and explanation can consolidate relevant facts and guidance into a traceable review package.
3. **Governance and control:** explicit authority boundaries, guardrails, rule traces, and frozen evaluation evidence can reduce the risk of unsupported generative decisions.

The project did not evaluate production transaction volumes, analyst handling time, customer satisfaction, claim cost, leakage, staffing impact, or financial return. Consequently, these benefits are stated as expected operational implications rather than measured business outcomes.

A production pilot would be required to quantify:

- average handling-time change;
- analyst acceptance or override rate;
- reduction in procedural search effort;
- consistency across analysts and teams;
- manual-review volumes;
- false continuation and false rejection rates;
- customer-service impact;
- implementation and operating cost.

The principal business conclusion is therefore:

> The approved proposal criteria were met, but production adoption requires correction of the documented unsafe-routing gaps and validation with representative operational data.

---

## 5. Limitations & Future Work

### 5.1 Material Held-Out Limitation

Although the system exceeded the approved primary accuracy target, the error pattern revealed an important operational limitation.

Six of the 55 held-out claims were incorrectly routed to `PROCEED`. This produced an unsafe-decision diagnostic of:

- 6 incorrect continuation recommendations;
- 10.9% of the held-out set.

**Table 5.1 — Held-out disposition errors**

| Missed rule | Expected outcome | Predicted outcome | Cases |
|---|---|---|---:|
| `DATA-002` | `MANUAL_REVIEW` | `PROCEED` | 2 |
| `EXC-002` | `MANUAL_REVIEW` | `PROCEED` | 1 |
| `ELG-002` | `NOT_ELIGIBLE` | `PROCEED` | 1 |
| `EXC-001` | `NOT_ELIGIBLE` | `PROCEED` | 2 |

The affected claims were:

- `CLM-000174`;
- `CLM-000175`;
- `CLM-000179`;
- `CLM-000202`;
- `CLM-000219`;
- `CLM-000220`.

The errors occurred because some decisive business conditions were not available to the rule engine as validated structured facts. The affected scenarios included:

- conflicting claim or policy information;
- exclusion conditions represented mainly in narrative text;
- policy-date or eligibility conditions not triggered by the available structured inputs;
- unsupported conditions that fell through to the default `OUT-001 → PROCEED` result.

The failures were not caused by:

- RAG changing the disposition;
- the LLM selecting the triggering rule;
- an unsafe generated explanation;
- failure of the response-authority guardrail;
- adversarial instructions overriding the workflow.

In all cases, the final generated response remained aligned with the deterministic outcome. The problem was therefore located upstream, within structured-data availability and deterministic rule coverage.

This distinction is important. The guardrails successfully prevented the LLM from changing the authoritative result, but they could not determine that the underlying authoritative result was incomplete or incorrect.

### 5.2 Data, Evaluation, and Generalisation Limitations

The reported results should be interpreted within the boundaries of the synthetic prototype.

#### Synthetic-data limitations

The project used purpose-built synthetic records rather than real customer claims. This provided legal usability, privacy protection, and controlled ground truth, but it may not reproduce:

- real-world data-quality variation;
- ambiguous or incomplete policy histories;
- inconsistent document formats;
- duplicate enterprise records;
- changing plan configurations;
- analyst notes and informal communications;
- unusual customer behaviour;
- market-specific operational practices.

The held-out error analysis indicates that some important business facts require richer and more explicit structured representation.

#### Limited knowledge-base scale

The approved knowledge base contained seven documents and 21 chunks. This was sufficient to evaluate corpus construction, embeddings, FAISS, controlled retrieval, and reranking, but it is substantially smaller than an enterprise operational knowledge base.

Retrieval performance may change when the corpus contains:

- more products and plan variants;
- multiple countries or regulatory jurisdictions;
- overlapping procedures;
- outdated document versions;
- contradictory guidance;
- longer documents;
- a larger number of semantically similar sections.

#### Limited retrieval benchmark

The retrieval benchmark contained 14 manually grounded queries. It covered the principal query families required by the project, but the small sample limits confidence in differences between retrieval methods.

The comparison demonstrated that semantic retrieval outperformed the lexical baseline on the frozen benchmark, but a larger query set would be required to establish consistent performance across broader operational scenarios.

#### Limited generation-quality sample

Human review, LLM judging, and Ragas evaluation were performed on 12 frozen generation cases. The cases represented all four dispositions, but they do not cover every possible rule combination, evidence profile, or retrieval failure.

Additional human evaluation would be required to assess:

- explanation clarity across different analyst groups;
- usefulness under time pressure;
- consistency across model versions;
- sensitivity to longer or noisier contexts;
- handling of rare exceptions.

#### External-model variability

The embedding, explanation, LLM-judge, and Ragas workflows depend on external models and software libraries. Future model versions may produce different embeddings, responses, or evaluation scores.

The project mitigated this risk through committed outputs, manifests, dependency records, frozen cases, and prediction fingerprints. However, exact regeneration may still be affected by model-service changes outside the repository.

#### No live operational evaluation

The prototype was not integrated with production policy, claims, evidence, payment, customer-service, or identity systems. It was also not tested with real analysts in a live workflow.

The project therefore did not measure:

- claim-handling time;
- analyst productivity;
- customer outcomes;
- operational cost;
- false-payment prevention;
- claim leakage;
- analyst override behaviour;
- production latency;
- system availability.

The business impact described in this report remains a reasoned expectation rather than a measured production result.

### 5.3 Required Production Improvements

The held-out findings define several technical improvements required before production use.

#### Fail-safe routing

A claim should not default to `PROCEED` when an important condition cannot be evaluated.

The workflow should apply the principle:

> An unresolved authoritative condition must route to `MANUAL_REVIEW`, not silently pass.

This would reduce the risk created by incomplete data or unsupported rule conditions.

#### Explicit evaluation states

Deterministic tools should distinguish among:

- `PASS`;
- `FAIL`;
- `UNABLE_TO_EVALUATE`.

A missing record, unsupported exclusion, conflicting identifier, or unavailable policy date should not be treated as equivalent to a successful check.

`UNABLE_TO_EVALUATE` should normally trigger `MANUAL_REVIEW`.

#### Stronger conflict detection

Structured validation should be extended to detect:

- conflicting customer identifiers;
- conflicting policy identifiers;
- claim-to-policy mismatches;
- multiple authoritative policy matches;
- duplicate records;
- inconsistent device identifiers;
- disagreement between claim and evidence records.

These conditions should reliably trigger a data-conflict rule such as `DATA-002`.

#### Structured exclusion indicators

Important exclusions should be represented as controlled structured attributes or validated evidence signals.

An LLM may identify a possible exclusion from narrative text, but the extracted value should remain unverified until:

- confirmed against an authoritative source;
- validated by a deterministic rule;
- or reviewed by an authorised analyst.

The LLM must not independently apply an exclusion or create a final non-eligibility decision.

#### Stronger date and eligibility logic

Production implementation should strengthen evaluation of:

- incident date versus policy start date;
- policy end date;
- cancellation date;
- suspension periods;
- waiting periods;
- missing or contradictory dates;
- timezone and date-format consistency.

Date conditions that cannot be evaluated reliably should route to manual review.

#### Future regression coverage

The six documented failure patterns should be converted into future regression tests during a post-capstone improvement phase.

These tests must not replace or retrospectively modify the frozen held-out result. The original 89.1% result and prediction fingerprint should remain the final capstone evidence.

#### Rule-aware retrieval

The controlled retrieval query should be enhanced to represent rule-specific guidance needs more precisely, particularly for:

- exclusions;
- data conflicts;
- claim limits;
- anomalies;
- manual-review conditions;
- unsupported facts;
- decision boundaries.

This improvement may increase Context Precision and Context Recall. It does not replace the need to correct deterministic rule coverage.

#### Production governance and controls

A production implementation would additionally require:

- authenticated access;
- role-based permissions;
- encryption and secrets management;
- audit logging;
- operational monitoring and alerting;
- data-quality dashboards;
- rule and prompt change control;
- knowledge-document versioning;
- model-performance monitoring;
- incident and fallback procedures;
- formal human-override recording;
- privacy and retention controls;
- integration testing with authoritative enterprise systems.

### 5.4 Future Evaluation Priorities

A production pilot should extend the evaluation framework beyond the capstone evidence.

Recommended priorities include:

1. testing on representative historical claims with appropriate privacy controls;
2. increasing the retrieval benchmark across products, rules, and jurisdictions;
3. expanding human review across multiple analysts;
4. measuring analyst acceptance and override rates;
5. evaluating handling-time and procedural-search effort;
6. monitoring false `PROCEED` and false `NOT_ELIGIBLE` outcomes separately;
7. testing knowledge-base updates and stale-index controls;
8. evaluating model-version and prompt-version changes;
9. measuring performance under missing, conflicting, and delayed source data;
10. conducting operational, security, compliance, and responsible-AI reviews.

The primary production safety metric should not be overall accuracy alone. Evaluation should prioritise:

- unsafe continuation rate;
- manual-review recall;
- false non-eligibility rate;
- authority-preservation rate;
- unresolved-condition routing;
- critical guardrail failures.

### 5.5 Final Project Position

This capstone demonstrates a working and systematically evaluated rule-grounded Agentic AI decision-support architecture.

The project:

- implemented modular deterministic claim-triage tools;
- used LangGraph for controlled workflow orchestration;
- implemented an allow-listed RAG pipeline with FAISS;
- evaluated lexical, semantic, hybrid, and reranked retrieval;
- generated guarded analyst-facing explanations;
- preserved deterministic decision authority;
- maintained authorised human control;
- passed 149 regression tests;
- exceeded the approved held-out accuracy target;
- passed the held-out adversarial safety gate;
- documented its failure patterns transparently.

The system achieved 89.1% held-out disposition accuracy against the approved target of at least 80%. It also recorded zero critical safety failures across eight held-out adversarial cases.

However, six unsafe `PROCEED` recommendations show that the current structured-data and deterministic-rule coverage is not sufficient for production use. Guardrails prevented LLM override but could not correct incomplete deterministic evaluation.

The appropriate final conclusion is:

> This capstone demonstrates a successful and evaluated rule-grounded Agentic AI decision-support prototype. It exceeded the approved primary accuracy target, preserved deterministic authority, maintained human control, and passed the held-out safety gate. However, stronger fail-safe routing and structured deterministic-rule coverage are required before production use. The final assessment is `MET_WITH_DOCUMENTED_LIMITATION`.

---

## References

[1] University BYOC Programme, *Approved Proposal Form: Device Protection Claims Triage — A Rule-Grounded Agentic AI Decision-Support System*, approved project proposal, 2026.

[2] University BYOC Programme, *Scope Specification and Project Requirements*, course document, 2026.

[3] University BYOC Programme, *Final Submission Evaluation Rubric*, course document, 2026.

[4] University BYOC Programme, *Learner Handbook and Final Deliverable Template*, course documents, 2026.

[5] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” in *Advances in Neural Information Processing Systems 33*, 2020. [Available online](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html).

[6] N. Reimers and I. Gurevych, “Sentence-BERT: Sentence Embeddings Using Siamese BERT-Networks,” in *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing*, pp. 3982–3992, 2019. [Available online](https://aclanthology.org/D19-1410/).

[7] J. Johnson, M. Douze, and H. Jégou, “Billion-Scale Similarity Search with GPUs,” *arXiv preprint arXiv:1702.08734*, 2017. [Available online](https://arxiv.org/abs/1702.08734).

[8] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” in *Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations*, pp. 150–158, 2024. [Available online](https://aclanthology.org/2024.eacl-demo.16/).

[9] LangChain, “LangGraph Graph API Overview,” *LangGraph Documentation*. [Available online](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 15 July 2026.

[10] OpenAI, “Vector Embeddings,” *OpenAI API Documentation*. [Available online](https://developers.openai.com/api/docs/guides/embeddings). Accessed 15 July 2026.

[11] OpenAI, “text-embedding-3-small Model,” *OpenAI API Documentation*. [Available online](https://developers.openai.com/api/docs/models/text-embedding-3-small). Accessed 15 July 2026.

[12] Meta AI Research, “Faiss Documentation,” *Faiss: A Library for Efficient Similarity Search and Clustering of Dense Vectors*. [Available online](https://faiss.ai/). Accessed 15 July 2026.

[13] Meta AI Research, “IndexFlat and IndexFlatIP,” *Faiss API Documentation*. [Available online](https://faiss.ai/cpp_api/struct/structfaiss_1_1IndexFlat.html). Accessed 15 July 2026.

[14] Sentence Transformers, “MS MARCO Cross-Encoders,” *Sentence Transformers Documentation*. [Available online](https://www.sbert.net/docs/pretrained-models/ce-msmarco.html). Accessed 15 July 2026.

[15] Ragas, “Available Evaluation Metrics,” *Ragas Documentation*. [Available online](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/). Accessed 15 July 2026.

[16] Python Software Foundation, “unittest — Unit Testing Framework,” *Python 3 Documentation*. [Available online](https://docs.python.org/3/library/unittest.html). Accessed 15 July 2026.

[17] S. S. Sheik, *Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System*, project source code, notebooks, evaluation artifacts, and documentation, 2026. [GitHub repository](https://github.com/sadiqs3/DP_claims_triage).