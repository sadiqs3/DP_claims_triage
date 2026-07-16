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

Device-protection claim triage requires analysts to reconcile policy validity, protected-device identity, incident coverage, prior-claim limits, evidence sufficiency, exclusions, and risk indicators. Deterministic rules are appropriate for authoritative eligibility checks, but analysts must still interpret fragmented information and locate relevant operational guidance. An unrestricted large language model introduces a different risk: it may generate plausible but unsupported conclusions when facts are incomplete, conflicting, or outside its authority.

This capstone developed a rule-grounded Agentic AI decision-support system that separates deterministic decision authority from generative assistance. The system recommends one of four internal outcomes: `PROCEED`, `INFO_REQUIRED`, `MANUAL_REVIEW`, or `NOT_ELIGIBLE`. These outcomes support an analyst’s next action; they do not constitute claim approval, final denial, payment authorisation, or fraud determination.

Modular deterministic tools evaluate policy, plan, device, coverage, claim history, evidence, and risk facts. LangGraph coordinates deterministic triage, approved follow-up-question selection, controlled retrieval, explanation generation, and protective guardrails. The Retrieval-Augmented Generation layer uses seven allow-listed synthetic knowledge documents, 21 section-aware chunks, `text-embedding-3-small` embeddings, and a persisted FAISS `IndexFlatIP` index. A cross-encoder reranker was evaluated as an optional second-stage component. Retrieved guidance and LLM-generated explanations remain non-authoritative and cannot modify the deterministic outcome or triggering rule.

The project used a purpose-built synthetic claims ecosystem containing 220 new claims, divided into 165 development cases and 55 held-out cases. No real customer data, production claims, or proprietary organisational policy documents were used. Development and held-out identifiers were verified as disjoint. Final held-out predictions were frozen and assigned a SHA-256 fingerprint before labels were joined, and the revealed results were not used for subsequent tuning.

Evaluation included 149 regression tests, a 14-query retrieval benchmark, 12 frozen generation-quality cases, human review, LLM-as-judge calibration, automated Ragas evaluation, and eight held-out adversarial safety cases. Semantic retrieval achieved the strongest aggregate retrieval performance, with Hit@1 of 78.6%, Hit@3 of 92.9%, and MRR@3 of 0.857. Cross-encoder reranking improved two queries but regressed two others; it was therefore retained as a controlled optional stage rather than the default.

On the frozen 55-claim held-out set, 49 claims were classified correctly, producing 89.1% disposition accuracy against the approved target of at least 80%. Policy-rule adherence was 89.1%, exact primary-rule agreement was 87.3%, follow-up requirement accuracy was 100%, and exact follow-up selection was 93.3%. All eight held-out safety cases passed with zero critical safety failures, while deterministic authority and the authorised human-control boundary were preserved throughout the final evaluation.

A material limitation remained. Six ordinary held-out claims were incorrectly routed to `PROCEED`, producing an unsafe-decision diagnostic of 10.9%. Error analysis attributed these failures to gaps in structured authoritative data and deterministic rule coverage, including unresolved conflicts, exclusions, and eligibility-date conditions. They were not caused by RAG, LLM generation, or guardrail override.

The project demonstrates that deterministic rules can be combined with controlled Agentic AI and RAG to improve the consistency, traceability, and explainability of claim-triage support without transferring final authority to an LLM. However, fail-safe routing, explicit `UNABLE_TO_EVALUATE` states, and stronger structured rule coverage are required before production use. The final assessment is **`MET_WITH_DOCUMENTED_LIMITATION`**.

---

## 1. Introduction & Business Context

### 1.1 Operational Problem

Device-protection claim triage requires information from several linked sources, including policy status, protected-device records, plan configuration, incident coverage, previous claims, evidence requirements, exclusions, and risk indicators. The applicable conditions must also be evaluated in a defined order. A covered incident may still require additional evidence, exceed a claim limit, contain conflicting identifiers, fall outside the active policy period, or require specialist review.

Manual processing may be affected by fragmented information, repeated procedural searches, variation in analyst experience, and inconsistent application of operational guidance. These conditions can reduce traceability and make it difficult to explain why a claim was allowed to continue, paused for information, escalated, or considered ineligible. The approved proposal identified improved consistency, traceability, operational productivity, and risk control as the principal business motivations for the project [1].

A conventional rule engine can provide repeatable policy and eligibility checks, but it offers limited support for semantic retrieval and concise explanation. Conversely, an unrestricted LLM may generate fluent but unsupported interpretations when information is incomplete, contradictory, or unverified.

The project therefore addresses the following question:

> How can deterministic policy and eligibility rules be combined with controlled Agentic AI, Retrieval-Augmented Generation, and guardrails to support device-protection claim triage while preserving traceability, safety, and authorised human control?

The solution is positioned as an internal decision-support prototype rather than an autonomous claim-adjudication system.

### 1.2 Stakeholders and Business Stakes

The primary user is a claims analyst who requires a clear recommendation supported by authoritative facts and relevant operational guidance. Other stakeholders include claims operations managers, policy and product teams, risk and compliance functions, technology teams, customer-service teams, and customers indirectly affected by the consistency of claim handling.

**Table 1.1 — Stakeholders and principal requirements**

| Stakeholder | Principal requirement |
|---|---|
| Claims analysts | Clear recommendation, triggering rule, missing evidence, and relevant guidance |
| Claims operations managers | Consistent triage, measurable performance, and traceability |
| Policy and product teams | Correct application of plan, coverage, eligibility, and limit rules |
| Risk and compliance teams | Prevention of unsupported automation and preservation of human accountability |
| Technology teams | Modular, testable, reproducible, and maintainable implementation |
| Customer-service teams | Controlled and consistent follow-up requests |
| Customers | Fair handling with an authorised human retaining final responsibility |

The main business risks considered were:

- inconsistent application of policy and evidence rules;
- unnecessary analyst effort spent locating procedures;
- weak visibility of the reason behind a recommendation;
- uncontrolled generation of follow-up questions;
- unsupported LLM interpretation of policy conditions;
- incorrect continuation of claims that require review or should not proceed;
- insufficient auditability of automated recommendations.

The project did not measure financial savings, handling-time reduction, customer satisfaction, or production-scale productivity. Its business conclusions are therefore limited to demonstrated technical feasibility and expected operational implications.

### 1.3 Project Objectives and Success Criteria

The project had six objectives:

1. implement deterministic tools for policy, eligibility, coverage, evidence, history, and risk evaluation;
2. apply explicit rule precedence to produce a traceable triage recommendation;
3. use LangGraph to coordinate deterministic tools, retrieval, generation, and guardrails;
4. retrieve approved operational guidance through controlled RAG and FAISS;
5. generate analyst-facing explanations without transferring decision authority to the LLM;
6. evaluate the complete workflow through regression testing, retrieval benchmarking, human review, LLM judging, Ragas, held-out claims, and adversarial safety cases.

The approved primary success criterion was at least **80% agreement with ground-truth outcomes across 55 held-out synthetic claims** [1].

Supporting measures included:

- policy-rule adherence;
- exact triggering-rule agreement;
- follow-up requirement accuracy;
- exact follow-up-question selection;
- manual-review precision and recall;
- unsafe-decision rate;
- retrieval quality before and after reranking;
- preservation of deterministic authority;
- preservation of authorised human control.

The approved safety gate required **zero critical failures** in the held-out adversarial safety evaluation [1]. Critical failures included autonomous approval or denial, payment authorisation, fraud determination, fabricated policy authority, successful override of the deterministic result, or removal of the human-control boundary.

### 1.4 Scope and Human-Control Boundary

The system produces four internal triage recommendations.

**Table 1.2 — Triage outcomes**

| Outcome | Operational interpretation |
|---|---|
| `PROCEED` | Available authoritative facts support continuation to standard processing; this is not a claim approval |
| `INFO_REQUIRED` | Defined evidence or information is missing and an approved follow-up is required |
| `MANUAL_REVIEW` | A conflict, anomaly, risk indicator, unsupported condition, or evaluation uncertainty requires authorised review |
| `NOT_ELIGIBLE` | Deterministic rules support a non-eligibility recommendation; this is not a final customer-facing denial |

The implemented scope includes deterministic rule evaluation, controlled follow-up selection, LangGraph orchestration, allow-listed RAG, FAISS semantic retrieval, optional cross-encoder reranking, LLM explanation support, protective guardrails, and systematic evaluation.

The following actions remain outside the autonomous system boundary:

- claim approval;
- final customer-facing denial;
- payment or settlement authorisation;
- fraud determination;
- unrestricted customer communication;
- use of unverified narrative as authoritative policy evidence;
- production deployment and live enterprise integration.

The approved proposal explicitly retained settlement, approval, rejection, and customer communication under authorised human control [1]. The final architecture implements this boundary through deterministic authority, manual-review routing, approved follow-up wording, restricted prompts, content-safety validation, response-authority validation, and explicit decision-support notices.

The governing design principle is:

> Deterministic rules evaluate authoritative claim facts; LangGraph coordinates the workflow; RAG retrieves non-authoritative operational guidance; the LLM explains the result; and an authorised human remains accountable for the final action.

---

## 2. Data Architecture & Methodology

### 2.1 Synthetic Data, Governance, and Evaluation Partitions

Real device-protection claims may contain personal identifiers, device details, financial information, incident narratives, and confidential policy decisions. Production rules and operating procedures may also contain proprietary organisational information. The project therefore used a purpose-built, domain-representative synthetic ecosystem, consistent with the approved proposal’s privacy and intellectual-property safeguards [1].

The synthetic data models the principal relationships required for claim triage:

- policies, customers, plans, and protected devices;
- policy status and incident dates;
- incident coverage and product eligibility;
- historical claims and usage limits;
- evidence bundles and document records;
- risk and anomaly indicators;
- approved operational guidance;
- controlled follow-up questions;
- expected outcomes and triggering rules.

**Table 2.1 — Final data and evaluation volumes**

| Component | Records |
|---|---:|
| Policy-device records | 120 |
| Historical claims | 112 |
| New claims | 220 |
| Development claims | 165 |
| Held-out claims | 55 |
| Evidence bundles | 220 |
| Evidence-document records | 283 |
| Knowledge-base documents | 7 |
| Knowledge-base chunks | 21 |
| Approved follow-up questions | 14 |
| Ground-truth labels | 220 |
| Safety and adversarial cases | 24 |
| Held-out safety cases | 8 |

The 220 new claims were divided into 165 development cases and 55 held-out cases. Claim identifiers were verified as disjoint. Development cases supported implementation, retrieval benchmarking, generation-quality review, and debugging; held-out cases were reserved for final evaluation.

Data preparation focused on structural quality rather than document extraction because the controlled sources consisted of CSV, JSON, and Markdown files. Optical Character Recognition and complex PDF-layout processing were therefore not required. Validation covered:

- expected schemas and mandatory fields;
- controlled categorical values;
- claim-to-policy and policy-to-device relationships;
- evidence-bundle and evidence-document links;
- historical-claim relationships;
- date normalisation;
- ground-truth identifier integrity;
- development and held-out partition separation.

The final held-out protocol was designed to reduce leakage:

1. freeze the workflow and configuration;
2. run all 55 claims without consulting their labels;
3. export the prediction-only artifact;
4. calculate its SHA-256 fingerprint;
5. join the labels only after predictions were frozen;
6. calculate the approved metrics;
7. document errors without retuning the workflow.

The frozen prediction fingerprint is:

`0a20deead9d8fdcf75b740d39d11f8ff3934cb173da55c02ec61c860c92e2a1f`

All claims, policies, evidence records, and knowledge documents are synthetic. No real customer data, production claims, or proprietary organisational records were included. The resulting evaluation is reproducible and legally usable, but it cannot represent the full ambiguity, missingness, behavioural variation, and system-integration complexity of production data.

### 2.2 Architecture and Authority Model

The solution uses a hybrid architecture that separates authoritative business-rule execution from non-authoritative AI assistance. LangGraph represents the workflow as a stateful graph in which nodes operate on shared workflow state and execute in a controlled sequence [5].

The principal layers are:

1. structured claim and reference data;
2. deterministic policy, eligibility, evidence, history, and risk tools;
3. rule precedence and authoritative triage outcome;
4. controlled follow-up-question selection;
5. controlled retrieval from an approved knowledge base;
6. LLM-based analyst explanation;
7. content-safety and response-authority guardrails;
8. authorised human review.

**Figure 1 — End-to-End System Architecture**

![End-to-end architecture of the rule-grounded claims-triage system](figures/figure_1_end_to_end_architecture.svg)

*The architecture separates authoritative deterministic decision-making from non-authoritative retrieval and LLM explanation. LangGraph coordinates the workflow, guardrails protect the deterministic result, and an authorised human retains final accountability.*

**Table 2.2 — Component responsibilities and authority**

| Component | Responsibility | Authority |
|---|---|---|
| Deterministic tools | Evaluate policy, plan, device, coverage, evidence, limits, conflicts, and risk | Authoritative |
| Rule-precedence engine | Select the outcome and triggering rule | Authoritative |
| LangGraph | Coordinate tools, retrieval, generation, and guardrails | Orchestration only |
| Follow-up selector | Select an approved catalogue question | Catalogue-controlled |
| RAG and FAISS | Retrieve operational guidance | Non-authoritative |
| Cross-encoder | Optionally reorder approved candidate chunks | Non-authoritative |
| LLM explanation | Produce analyst-facing explanation support | Non-authoritative |
| Content-safety guardrail | Block prohibited generated behaviour | Protective |
| Response-authority guardrail | Preserve protected deterministic values | Protective |
| Authorised human | Determine the final operational action | Final accountability |

The deterministic tools produce the recommended disposition, triggering rule, precedence stage, supporting facts, and rule trace. Retrieval and generation begin only after this result has been established. Consequently, neither the retrieved guidance nor the LLM explanation can create policy eligibility, alter coverage, change evidence requirements, apply exclusions, or replace the triggering rule.

This separation addresses the different strengths of rules and generative AI. Rules provide repeatable execution and auditability, while generative components support semantic retrieval and explanation. Human control is implemented through the architecture and guardrails rather than being treated only as a disclaimer.

### 2.3 Knowledge Base, Embeddings, and FAISS

Retrieval-Augmented Generation combines external retrieved information with language-model generation, allowing responses to use information outside the model’s internal parameters [2]. In this project, retrieval supplies approved operational guidance after deterministic triage; it does not determine the claim outcome.

The knowledge base contains seven allow-listed synthetic documents covering evidence handling, escalation, review expectations, and analyst procedures. A section-aware corpus builder divided these documents into 21 coherent chunks. Each chunk retains its source-document and section identity.

Chunk overlap was not used because the source documents were short and structurally organised. Overlap would have duplicated substantial portions of guidance and increased the likelihood of near-identical Top-K results. The frozen retrieval benchmark did not provide evidence that a different chunking strategy was required.

The semantic retriever uses `text-embedding-3-small`. Its default output is a 1536-dimensional vector, which matches the persisted project index configuration [4]. The vectors are L2-normalised and searched using FAISS `IndexFlatIP`. FAISS provides indexing and similarity-search methods for dense vectors [3].

**Table 2.3 — Retrieval configuration**

| Component | Configuration |
|---|---|
| Knowledge documents | 7 allow-listed documents |
| Retrieval chunks | 21 section-aware chunks |
| Embedding model | `text-embedding-3-small` |
| Embedding dimension | 1536 |
| Vector index | FAISS `IndexFlatIP` |
| Search method | Exact inner-product search |
| Cross-encoder | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Reranker status | Controlled optional stage |

Exact search was appropriate because the corpus contained only 21 chunks. Approximate indexing would have added configuration and validation complexity without a meaningful scale advantage.

The persisted index is accompanied by controls for:

- embedding model and vector dimension;
- expected chunk count;
- corpus fingerprint;
- stable chunk-order fingerprint;
- index-to-corpus consistency;
- stale-index detection.

A mismatch blocks normal index loading and requires a controlled rebuild.

**Figure 2 — Controlled Retrieval Pipeline**

![Controlled retrieval pipeline showing knowledge-base preparation, query construction, FAISS retrieval, optional reranking, and index validation](figures/figure_2_controlled_retrieval_pipeline.svg)

*The retrieval pipeline uses only allow-listed knowledge documents and authoritative structured triage facts. Customer narrative and identifiers are excluded from the controlled query. Corpus and chunk-order fingerprints protect the persisted FAISS index from stale or mismatched use, while retrieved content remains non-authoritative analyst guidance.*

The runtime retrieval query is built from an allow-listed projection of authoritative facts, such as:

- deterministic outcome and triggering rule;
- claim category and requested service type;
- coverage and evidence status;
- missing evidence codes;
- manual-review requirement.

Customer statements, arbitrary free text, identifiers, evidence-document text, and generated decision reasons are excluded. This restriction improves reproducibility and reduces the risk of unverified or adversarial narrative influencing retrieval as though it were an authoritative fact.

### 2.4 Comparative Retrieval Methodology

Four retrieval configurations were implemented:

1. lexical TF-IDF;
2. semantic embedding retrieval;
3. Hybrid Reciprocal Rank Fusion;
4. semantic retrieval followed by cross-encoder reranking.

TF-IDF provided a transparent term-based baseline. Semantic retrieval measured whether embeddings improved retrieval where the query and target guidance used different wording. Hybrid Reciprocal Rank Fusion combined lexical and semantic rankings without requiring their raw scores to be directly comparable [9]. The cross-encoder provided a second-stage relevance assessment of a bounded semantic candidate set.

All four methods were evaluated against the same frozen set of 14 manually grounded queries at `Top K = 3`. The target chunks and query families were defined before final comparison, reducing the risk of selecting examples based on favourable results.

The principal retrieval metrics were:

- **Hit@1:** whether a relevant chunk was ranked first;
- **Hit@3:** whether a relevant chunk appeared within the first three results;
- **MRR@3:** the reciprocal rank of the first relevant result, limited to three positions;
- **No-result rate:** the proportion of queries for which no result was returned.

Aggregate metrics were supplemented by case-level analysis so that improvements and regressions introduced by reranking remained visible.

### 2.5 Design Refinements

Several initial assumptions were narrowed during implementation to strengthen control and methodological validity.

**Table 2.4 — Principal design refinements**

| Initial assumption | Final implementation | Reason |
|---|---|---|
| LLM-generated follow-up questions | Selection from an approved 14-question catalogue | Improved consistency, auditability, and exact evaluation |
| Customer narrative used in AI processing | Excluded from authoritative decisions and controlled retrieval queries | Prevented unverified or adversarial text from acquiring policy influence |
| Planned BM25-style lexical retrieval | TF-IDF baseline | Transparent and sufficient for the small controlled corpus |
| Reranking enabled by default | Retained as an optional controlled stage | Mixed improvements and regressions on the frozen benchmark |
| Faithfulness assessed only against retrieved documents | Assessed against structured authoritative facts plus retrieved guidance | Reflected the actual hybrid generation context |
| LLM judge used without a baseline | Calibrated against documented human review | Avoided treating automated judgement as independent ground truth |
| Final evaluation performed with visible labels | Predictions frozen before label reveal | Reduced post-hoc optimisation and leakage |

The most important refinement concerned authority. Customer narrative and generated text were deliberately prevented from becoming authoritative inputs. A production system could use an LLM to identify possible facts from narrative text, but those facts should remain unverified until confirmed by an authoritative source or an authorised analyst.

The reranker was retained because second-stage scoring was a technically valid and rubric-relevant component. However, its use remained evidence-driven: it was not made the default when the frozen benchmark failed to show an aggregate improvement.

Similarly, the automated RAG methodology was adapted to the hybrid architecture. Retrieval quality was measured against preferred operational guidance, while response faithfulness was measured against all legitimate generation inputs: authoritative structured facts and retrieved guidance. This avoided penalising correct deterministic statements merely because they were not repeated in a knowledge-base chunk.
---

## 3. Implementation & Results

### 3.1 Modular Implementation and LangGraph Workflow

The solution was implemented as a modular Python project rather than as a notebook-only prototype. Reusable logic is separated across deterministic tools, agent orchestration, retrieval, explanation, guardrails, evaluation utilities, and tests. Notebooks preserve implementation walkthroughs and frozen evaluation evidence, while the source modules contain the executable workflow logic.

The principal implementation stages are summarised in Table 3.1.

**Table 3.1 — Implemented workflow stages**

| Stage | Responsibility |
|---|---|
| Claim intake | Load the claim and linked policy, device, evidence, history, and risk records |
| Deterministic tools | Evaluate authoritative policy, eligibility, coverage, evidence, history, and risk facts |
| Rule precedence | Select the disposition, triggering rule, and decision reason |
| Controlled follow-up | Select an approved catalogue question when information is missing |
| Controlled query | Project allow-listed authoritative facts into a retrieval query |
| FAISS retrieval | Retrieve approved operational guidance |
| Cross-encoder reranking | Optionally reorder a bounded candidate set |
| LLM explanation | Produce non-authoritative analyst-facing support |
| Content-safety guardrail | Detect prohibited generated behaviour |
| Response-authority guardrail | Preserve deterministic outcomes and protected fields |
| Human review | Determine the final operational or customer-facing action |

LangGraph was used to represent these stages as an explicit stateful workflow [5]. The compiled final implementation, identified as `langgraph_v6`, follows this sequence:

1. `deterministic_triage`;
2. `controlled_follow_up_selection`;
3. `controlled_rag_retrieval`;
4. `explanation_proposal`;
5. `agent_content_safety_guardrail`;
6. `response_guardrail`.

**Figure 3 — LangGraph Orchestration Flow**

![LangGraph orchestration flow showing deterministic triage, controlled retrieval, explanation generation, guardrails, and authorised human review](figures/figure_3_langgraph_orchestration_flow.svg)

*Deterministic triage is completed before retrieval or generation. Controlled RAG may be enabled or bypassed without changing the authoritative result. The content-safety guardrail replaces prohibited generated content, while the response-authority guardrail restores protected deterministic values when an override is detected. Final operational responsibility remains with an authorised human reviewer.*

The deterministic tools evaluate:

- policy and customer matching;
- applicable plan configuration;
- product scope;
- policy status on the incident date;
- protected-device match;
- incident coverage;
- prior-claim utilisation and limits;
- evidence availability and sufficiency;
- risk, anomaly, and conflict indicators.

Their outputs are consolidated into an authoritative claim context. Rule precedence then produces the triage outcome, triggering rule, precedence stage, decision reason, and rule trace. The LLM receives this result only after deterministic evaluation has completed.

Claims classified as `INFO_REQUIRED` use an approved catalogue containing 14 follow-up questions. The workflow selects an existing question identifier and wording rather than allowing unrestricted question generation. This provides consistent wording, auditability, and direct comparison with ground-truth labels.

The controlled RAG query is constructed from an allow-listed projection of authoritative facts. It may include the outcome, triggering rule, claim category, coverage status, evidence state, missing evidence codes, and manual-review requirement. Customer narrative, identifiers, evidence-document text, and generated reasoning are excluded.

The cross-encoder uses `cross-encoder/ms-marco-MiniLM-L-6-v2`. Cross-encoders jointly score query-document pairs and are commonly used as second-stage passage rerankers because they can model interactions that are not captured when query and document embeddings are generated independently [6]. In this project, reranking could change only the order of approved retrieved chunks; it could not introduce external information or change the claim outcome.

The LLM explanation is processed through two protective controls:

- the content-safety guardrail detects prohibited behaviour such as autonomous approval, denial, fraud determination, payment authorisation, fabricated facts, or attempts to bypass human review;
- the response-authority guardrail mechanically compares protected fields with the deterministic state and restores the authoritative outcome, rule, and approved follow-up values if a conflict is detected.

This separation ensures that safe-sounding generated text cannot silently alter the authoritative decision record.

### 3.2 One Claim Journey

The frozen development case `GEN-001`, linked to claim `CLM-000001`, illustrates the complete workflow for a screen-damage repair claim.

**Figure 4 — One Claim Journey**

![Journey of claim CLM-000001 through deterministic evaluation, controlled retrieval, explanation, guardrails, and human review](figures/figure_4_one_claim_journey.svg)

*The claim was matched to an active `DP-ESSENTIAL` policy, confirmed as in scope and covered, and assessed as having sufficient evidence with no risk indicators. Rule precedence produced `OUT-001 → PROCEED`. Controlled retrieval supplied evidence-handling guidance, while the explanation remained non-authoritative. The final response passed both guardrails before being presented for authorised human review.*

**Table 3.2 — Representative journey for `CLM-000001`**

| Stage | Actual project output | Role |
|---|---|---|
| Policy lookup | `UNIQUE_MATCH`; plan `DP-ESSENTIAL` | Authoritative |
| Plan and product scope | `ACTIVE_CONFIGURATION_AVAILABLE`; `IN_SCOPE` | Authoritative |
| Policy and device checks | `ACTIVE_ON_INCIDENT_DATE`; `DEVICE_MATCH` | Authoritative |
| Coverage | `UNIQUE_COVERAGE_RECORD`; covered | Authoritative |
| Claims history | Annual claims used: 0 of 1 | Authoritative |
| Evidence assessment | `EVD-SCREEN-01`; `SUFFICIENT` | Authoritative |
| Risk assessment | No triggered indicators | Authoritative |
| Rule precedence | `OUT-001` | Authoritative |
| Triage outcome | `PROCEED` | Authoritative recommendation |
| Follow-up | `NOT_REQUIRED` | Catalogue-controlled |
| Retrieved chunks | `KB-002::S03`, `KB-001::S01`, `KB-002::S01` | Non-authoritative |
| Highest-ranked guidance | Screen-damage evidence profile requires a damage photo | Non-authoritative |
| Content-safety status | `SAFE` | Protective |
| Authority status | `ALIGNED` | Protective |
| Final action | Presented to an authorised analyst | Human-controlled |

The controlled query described the established outcome, triggering rule, screen-damage category, repair service, active configuration, confirmed coverage, sufficient evidence, and device match. The highest-ranked chunk came from the Evidence Review Guide and confirmed the evidence profile applicable to screen damage.

The retrieved passage supported analyst interpretation but did not create the evidence requirement. The final explanation clarified that `PROCEED` meant continuation to standard processing rather than claim approval or payment authorisation.

The journey therefore demonstrates the separation of responsibilities: deterministic tools establish the recommendation, retrieval supplies guidance, the LLM explains the result, guardrails protect it, and the analyst determines the final action.

### 3.3 Testing and Reproducibility

The final regression suite contains **149 passing tests**. It covers:

- deterministic triage and rule precedence;
- plan, policy, device, and coverage checks;
- follow-up catalogue validation and selection;
- lexical, semantic, hybrid, and FAISS retrieval;
- index persistence and stale-index detection;
- cross-encoder reranking;
- controlled query construction;
- LangGraph orchestration;
- explanation and analyst-guidance formatting;
- content-safety and response-authority guardrails;
- Ragas and LLM-judge evaluation utilities.

The project separates locally reproducible validation from external-model execution. Deterministic tools, guardrails, committed-artifact review, fingerprint verification, and regression tests do not require an OpenAI API key. Live embedding generation, explanation generation, and LLM-judge reruns require separately configured model access.

Reproducibility controls include:

- documented environment and dependency versions;
- relative repository paths;
- modular source files;
- committed case-level evaluation outputs;
- evaluation manifests;
- corpus and chunk-order fingerprints;
- persisted FAISS artifacts;
- disjoint development and held-out partitions;
- frozen held-out predictions;
- SHA-256 verification;
- a final reviewer walkthrough.

The reviewer walkthrough displays the compiled LangGraph, validates expected artifact counts, recalculates the prediction fingerprint, and executes the 149-test suite. It does not regenerate embeddings, call the LLM, rerun Ragas, recreate held-out predictions, or tune the workflow.

### 3.4 Retrieval and Reranking Results

Four retrieval methods were evaluated on 14 frozen, manually grounded queries at `Top K = 3`.

**Table 3.3 — Retrieval benchmark**

| Retrieval method | Hit@1 | Hit@3 | MRR@3 |
|---|---:|---:|---:|
| Lexical TF-IDF | 57.1% | 85.7% | 0.702 |
| Semantic Embedding | **78.6%** | **92.9%** | **0.857** |
| Hybrid RRF | 71.4% | 92.9% | 0.798 |
| Semantic plus Cross-Encoder | 78.6% | 92.9% | 0.845 |

Semantic retrieval achieved the strongest aggregate result. Compared with TF-IDF, it improved Hit@1 by 21.5 percentage points and Hit@3 by 7.2 percentage points. Hybrid RRF matched semantic retrieval at Hit@3 but did not improve Hit@1 or MRR@3.

The cross-encoder produced mixed case-level behaviour:

- two queries improved;
- two queries regressed;
- nine retained the same Top-1 result;
- one remained a Top-3 miss.

Hit@1 and Hit@3 were unchanged, while MRR@3 decreased from 0.857 to 0.845. Semantic Embedding was therefore selected as the default, and reranking was retained as a `CONTROLLED_OPTIONAL_STAGE`.

The benchmark demonstrates that additional model complexity did not automatically improve retrieval for the small specialised corpus. Aggregate metrics were therefore interpreted together with query-level regressions rather than using only favourable examples.

### 3.5 Generation Quality, Human Review, and Automated Evaluation

Generation quality was evaluated on 12 frozen development cases covering all four dispositions. In every case:

- the final outcome matched the deterministic outcome;
- the final triggering rule matched the deterministic rule;
- content-safety status was `SAFE`;
- authority-guardrail status was `ALIGNED`;
- no critical human-identified safety failure occurred.

**Table 3.4 — Human generation review**

| Dimension | Mean score |
|---|---:|
| Context relevance | 2.75 / 4 |
| Groundedness | 3.75 / 4 |
| Answer relevance | 3.67 / 4 |
| Hallucination control | 3.75 / 4 |
| Critical safety failures | 0 |

Groundedness, answer relevance, and hallucination control were strong. Context relevance was lower because some retrieved passages were broadly related to evidence handling but did not directly address the triggering rule or immediate analyst action.

An LLM-as-judge evaluated the same cases and was calibrated against the human baseline. LLM judges can provide scalable comparative evaluation, but their reliability depends on the task, rubric, and evaluator model; human calibration remains necessary when the judged dimension involves domain-specific usefulness or nuance [8].

The largest disagreement concerned context relevance. The automated judge frequently rewarded semantic relatedness, while the human reviewer distinguished between generally relevant content and guidance that was directly useful for the particular rule.

The judge was therefore retained as supplementary evidence rather than as a replacement for human review.

Ragas was applied to the same 12 frozen cases. Ragas provides reference-based and reference-free metrics for evaluating retrieval and generated responses in RAG systems [7].

**Table 3.5 — Automated Ragas results**

| Metric | Mean |
|---|---:|
| Context Precision | 0.576 |
| Context Recall | 0.417 |
| Faithfulness | 0.627 |
| Answer Relevancy | 0.533 |

Context Precision and Context Recall compared retrieved chunks with preferred rule-level guidance. Faithfulness used the complete legitimate generation context: authoritative structured facts plus retrieved KB guidance.

This adaptation was required because the architecture is not a document-only RAG system. Statements such as the deterministic outcome, rule, evidence state, and precedence stage may be grounded in structured tool outputs rather than in the retrieved documents.

Diagnostic analysis found:

- the exact preferred chunk in 3 of 12 cases;
- semantically adequate context in 6 of 12 cases;
- partial semantic coverage without the exact preferred chunk in 3 of 12 cases.

The main weakness was therefore retrieval alignment rather than loss of decision authority. The relevant improvement is more rule-aware query construction and guidance retrieval, not additional authority for RAG or the LLM.

### 3.6 Final Held-Out and Safety Results

The frozen workflow was evaluated on 55 held-out claims after the prediction artifact had been exported and fingerprinted. No tuning was performed after labels were joined.

**Table 3.6 — Primary and supporting held-out results**

| Metric | Result |
|---|---:|
| Disposition accuracy | **49/55, 89.1%** |
| Approved accuracy target | At least 80% |
| Policy-rule adherence | 89.1% |
| Exact primary-rule agreement | 87.3% |
| Follow-up requirement accuracy | 100.0% |
| Exact follow-up selection | 93.3% |
| Manual-review recall | 78.6% |
| Manual-review precision | 100.0% |
| Authority alignment | 100.0% |
| Human-control preservation | 100.0% |
| Unsafe-decision diagnostic | 10.9% |

The primary proposal criterion was passed by 9.1 percentage points.

**Table 3.7 — Held-out confusion matrix**

| Gold \ Predicted | `PROCEED` | `INFO_REQUIRED` | `MANUAL_REVIEW` | `NOT_ELIGIBLE` |
|---|---:|---:|---:|---:|
| `PROCEED` | 17 | 0 | 0 | 0 |
| `INFO_REQUIRED` | 0 | 15 | 0 | 0 |
| `MANUAL_REVIEW` | 3 | 0 | 11 | 0 |
| `NOT_ELIGIBLE` | 3 | 0 | 0 | 6 |

All genuine `PROCEED` and `INFO_REQUIRED` cases were classified correctly. The weakness was over-routing to `PROCEED`: three `MANUAL_REVIEW` cases and three `NOT_ELIGIBLE` cases were incorrectly allowed to continue.

The class-level results reinforce this pattern:

- `PROCEED`: precision 0.739, recall 1.000, F1 0.850;
- `INFO_REQUIRED`: precision, recall, and F1 of 1.000;
- `MANUAL_REVIEW`: precision 1.000, recall 0.786, F1 0.880;
- `NOT_ELIGIBLE`: precision 1.000, recall 0.667, F1 0.800.

Eight separate adversarial and edge cases formed the final safety gate.

**Table 3.8 — Held-out safety results**

| Safety control | Result |
|---|---:|
| Safety cases passed | 8/8 |
| Deterministic outcome preserved | 8/8 |
| Applicable rule preserved | 6/6 |
| No fabricated rule where none was expected | 2/2 |
| Unsafe override blocked | 8/8 |
| Controlled fallback used | 8/8 |
| Critical safety failures | **0** |

The hard safety gate passed. Generated content did not change the authoritative result in any held-out safety case, and the authorised human-control boundary was preserved.

However, successful guardrail performance did not correct errors already present in the deterministic outcome. The six incorrect `PROCEED` recommendations demonstrate that AI-authority controls and complete deterministic business-rule coverage are separate safety requirements.
---

## 4. Strategic Deductions & Business Impact

### 4.1 Operational Implications

The project demonstrates that deterministic business rules and generative AI can support different parts of the claims-triage process without sharing decision authority.

The deterministic layer provides repeatable evaluation of policy, device, coverage, evidence, claim-history, and risk conditions. LangGraph coordinates the workflow, while RAG and the LLM support the analyst through guidance retrieval and concise explanation.

The evaluated architecture indicates four principal operational benefits.

#### Consistent preliminary triage

Equivalent structured inputs are processed through the same tools and rule-precedence sequence. This provides a repeatable starting point for analyst review and reduces reliance on individual interpretation during the initial triage stage.

#### Traceable recommendations

Each result contains a disposition, triggering rule, decision reason, supporting facts, and rule trace. The solution also preserves a clear distinction between:

- authoritative facts produced by deterministic tools;
- operational guidance retrieved from the knowledge base;
- explanatory text generated by the LLM.

This separation improves auditability and allows an analyst to identify the source and authority of each part of the response.

#### Controlled access to operational guidance

The retrieval layer uses the deterministic outcome, triggering rule, evidence state, and review requirement to locate relevant guidance. This demonstrates the feasibility of presenting procedural information alongside the claim recommendation rather than requiring analysts to search multiple documents manually.

The project did not measure handling-time reduction in a live environment. Faster processing is therefore an expected benefit requiring production validation rather than a measured project outcome.

#### Standardised follow-up handling

The approved 14-question catalogue provides consistent wording for recognised information gaps. Catalogue-based selection also prevents the LLM from requesting unsupported evidence or generating uncontrolled customer-facing questions.

These benefits support the proposal’s objectives of improving consistency, traceability, analyst productivity, and risk control [1]. However, the six held-out routing errors show that these benefits depend on complete and fail-safe deterministic rule coverage.

### 4.2 Technical and Methodological Deductions

The implementation and evaluation produced several broader conclusions.

#### Deterministic rules and GenAI require distinct responsibilities

Policy eligibility, coverage, exclusions, limits, and evidence requirements require predictable and auditable execution. These responsibilities are best handled through deterministic rules and authoritative structured data.

Generative AI is more appropriate for:

- semantic retrieval;
- explanation and summarisation;
- analyst guidance;
- orchestration of supporting workflow stages.

The project therefore shows that GenAI can add value without becoming the source of policy authority.

#### Semantic retrieval improved guidance access

Semantic Embedding achieved Hit@1 of 78.6%, Hit@3 of 92.9%, and MRR@3 of 0.857, outperforming the TF-IDF baseline. This supports semantic retrieval for specialised operational guidance where equivalent concepts may be expressed using different wording.

The result does not imply that semantic similarity should determine claim eligibility. Retrieval remains an analyst-support function.

#### Additional model complexity did not guarantee improvement

The cross-encoder improved two queries but regressed two others, while aggregate MRR@3 decreased from 0.857 to 0.845. Retaining it as an optional stage was therefore more appropriate than enabling it by default.

This finding reinforces an evidence-based engineering principle:

> A more complex model should be adopted only when it produces a consistent improvement in the target workflow.

#### Hybrid architectures require adapted evaluation

The explanation workflow uses both deterministic structured facts and retrieved guidance. A document-only faithfulness assessment would incorrectly penalise statements grounded in authoritative tool outputs but absent from retrieved chunks.

The final Ragas methodology therefore separated retrieval quality from response faithfulness. This distinction is relevant to other systems that combine databases, rule engines, tools, and RAG.

#### Automated judges require human calibration

The LLM judge broadly aligned with the human reviewer for groundedness, answer relevance, and hallucination control, but was more generous on context relevance. Semantically related content was not always considered operationally useful by the human reviewer.

Automated judging can improve scalability and consistency, but human review remains necessary for domain-specific usefulness and risk interpretation.

#### Aggregate accuracy can conceal unsafe error patterns

The overall held-out accuracy of 89.1% exceeded the approved target. However, all six errors were incorrect `PROCEED` recommendations.

This demonstrates that overall accuracy is insufficient for safety-sensitive triage. Evaluation must also examine:

- confusion patterns;
- class-specific recall;
- manual-review routing;
- false continuation rates;
- unsafe-decision diagnostics.

#### Guardrail safety and rule completeness are separate requirements

The guardrails successfully blocked unsafe LLM behaviour and preserved deterministic outcomes. They also preserved the six incorrect deterministic recommendations.

Production safety therefore requires both:

1. controls that prevent generated content from overriding authority;
2. complete and fail-safe deterministic business-rule coverage.

### 4.3 Proposal Commitment versus Final Outcome

**Table 4.1 — Proposal commitment versus final outcome**

| Proposal commitment | Final evidence | Status |
|---|---|---|
| Four triage outcomes | All four outcomes implemented | Met |
| Deterministic policy and eligibility rules | Modular tools and rule precedence implemented | Met |
| Agentic orchestration | LangGraph workflow implemented and validated | Met |
| RAG-based operational guidance | Allow-listed KB, embeddings, FAISS, and controlled query implemented | Met |
| Cross-encoder reranking | Implemented and evaluated as an optional stage | Met |
| Follow-up support | Approved catalogue selection replaced unrestricted generation | Met with controlled refinement |
| Analyst-facing explanations | Guarded LLM explanation workflow implemented | Met |
| Authorised human control | Preserved throughout final evaluation | Met |
| At least 80% accuracy on 55 held-out claims | 49 of 55 claims correct, or 89.1% | Passed |
| Supporting rule and follow-up metrics | Rule, follow-up, review-routing, and safety metrics reported | Met |
| Zero critical held-out safety failures | Zero failures across eight safety cases | Passed |
| Reproducible evidence | 149 tests, manifests, frozen outputs, fingerprint, and reviewer walkthrough | Substantially met; final clean-copy QA pending |
| Production readiness | Six unsafe `PROCEED` errors require correction | Not claimed |

The implementation also introduced controlled refinements:

- unrestricted follow-up generation became approved-catalogue selection;
- customer narrative was excluded from authoritative decisions and controlled retrieval queries;
- semantic retrieval became the default after comparative evaluation;
- reranking remained optional because it did not improve aggregate performance;
- Ragas evaluation was adapted to the hybrid structured-fact and document context;
- final predictions were frozen before held-out label comparison.

These refinements preserved the approved business problem while strengthening safety, auditability, and methodological validity.

### 4.4 Business Impact Position

The prototype indicates potential value in three areas:

1. **Operational consistency:** repeatable rule execution and standard follow-up selection can provide a more consistent starting point for analyst review.
2. **Analyst effectiveness:** consolidated facts, retrieved guidance, and guarded explanation can reduce information fragmentation.
3. **Governance:** explicit authority boundaries, rule traces, guardrails, manifests, and frozen evaluation evidence can reduce the risk of unsupported generative decisions.

The project did not evaluate production volumes, handling time, customer satisfaction, claim cost, leakage, staffing impact, or financial return. These benefits are therefore stated as expected implications rather than measured outcomes.

A production pilot should quantify:

- change in average handling time;
- analyst acceptance and override rates;
- reduction in procedural-search effort;
- manual-review volume;
- false `PROCEED` and false `NOT_ELIGIBLE` rates;
- customer-service impact;
- implementation and operating cost.

The principal business conclusion is:

> The approved proposal criteria were met, but production adoption requires correction of the documented unsafe-routing gaps and validation with representative operational data.
---

## 5. Limitations & Future Work

### 5.1 Material Held-Out Limitation

The system exceeded the approved primary accuracy target, but the error pattern revealed an important operational risk.

Six of the 55 held-out claims were incorrectly routed to `PROCEED`, producing an unsafe-decision diagnostic of **10.9%**.

**Table 5.1 — Held-out routing errors**

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

The failures occurred because some decisive conditions were not available to the deterministic workflow as validated structured facts. The affected scenarios included unresolved data conflicts, exclusions represented mainly in narrative text, and policy-date or eligibility conditions that were not triggered by the available runtime attributes.

The errors were not caused by:

- RAG changing the disposition;
- the LLM selecting the triggering rule;
- an unsafe explanation overriding the workflow;
- failure of the response-authority guardrail.

In every case, the generated response remained aligned with the deterministic result. The limitation was therefore located upstream, in structured-data availability and deterministic business-rule coverage.

This distinction is significant. Guardrails can prevent generative components from changing authority, but they cannot determine that the authoritative result itself is incomplete.

### 5.2 Data and Evaluation Limitations

The reported results should be interpreted within the boundaries of the controlled synthetic prototype.

#### Synthetic data

The purpose-built dataset provided privacy protection, legal usability, controlled ground truth, and reproducibility. However, it may not represent the full range of production conditions, including:

- inconsistent or duplicate enterprise records;
- incomplete policy histories;
- unstructured analyst notes;
- changing plan configurations;
- market-specific rules;
- unusual customer behaviour;
- real document-quality variation;
- delays or mismatches across source systems.

The held-out errors demonstrate that some business conditions require richer and more explicit structured representation.

#### Knowledge-base scale

The approved knowledge base contained seven documents and 21 chunks. This was sufficient to evaluate chunking, embeddings, FAISS, controlled retrieval, and reranking, but it is substantially smaller than an enterprise knowledge corpus.

Retrieval behaviour may change when the corpus includes more products, jurisdictions, document versions, overlapping procedures, contradictory guidance, and semantically similar sections.

#### Evaluation sample size

The retrieval benchmark contained 14 queries, while human review, LLM judging, and Ragas evaluation used 12 generation cases. These samples covered the intended query families and four dispositions, but they do not establish performance across every rule combination, evidence profile, exclusion, or rare exception.

#### External-model variability

Embedding, explanation, LLM-judge, and Ragas workflows depend on external models and software libraries. Future model or service versions may produce different outputs. The project mitigated this risk through frozen cases, manifests, committed results, dependency records, and fingerprints, but exact regeneration may still be affected by external change.

#### No live operational validation

The prototype was not integrated with production policy, claims, payment, identity, or customer-service systems. It was also not evaluated with claims analysts in a live workflow.

The project therefore did not measure:

- handling-time reduction;
- analyst productivity;
- analyst override behaviour;
- customer satisfaction;
- claim cost or leakage;
- production latency;
- system availability;
- financial return.

Business benefits remain expected implications rather than measured production outcomes.

### 5.3 Required Production Improvements

The held-out findings identify several priorities for future development.

**Table 5.2 — Required production improvements**

| Improvement | Purpose |
|---|---|
| Fail-safe `MANUAL_REVIEW` routing | Prevent unresolved conditions from falling through to `PROCEED` |
| Explicit `PASS`, `FAIL`, and `UNABLE_TO_EVALUATE` states | Distinguish a successful check from missing or unsupported evaluation |
| Stronger conflict detection | Identify duplicate, conflicting, or mismatched policy, customer, device, and evidence records |
| Structured exclusion indicators | Prevent exclusions described only in narrative from being missed |
| Stronger date and eligibility logic | Improve handling of policy start, end, cancellation, suspension, waiting periods, and conflicting dates |
| Future regression tests | Cover the six documented failure patterns without changing the frozen result |
| Rule-aware retrieval | Improve guidance alignment for exclusions, conflicts, limits, anomalies, and manual-review conditions |
| Production governance | Add access control, audit logging, monitoring, versioning, and change management |

#### Fail-safe routing

The workflow should apply the principle:

> An unresolved authoritative condition must route to `MANUAL_REVIEW`, not silently pass.

A missing record, unsupported exclusion, conflicting identifier, or unavailable policy date should produce `UNABLE_TO_EVALUATE` rather than being treated as an implicit pass.

#### Stronger structured rule coverage

Conflict detection should cover:

- conflicting customer or policy identifiers;
- claim-to-policy mismatches;
- multiple authoritative policy matches;
- duplicate records;
- inconsistent device identifiers;
- disagreement between claim and evidence records.

Important exclusions should also be represented as controlled structured attributes or validated evidence signals. An LLM may identify a possible exclusion from narrative text, but the extracted fact should remain unverified until confirmed by an authoritative source or an authorised analyst.

#### Date and eligibility controls

Production logic should strengthen evaluation of:

- incident date against policy start date;
- policy end and cancellation dates;
- suspension periods;
- waiting periods;
- missing or contradictory dates;
- timezone and date-format consistency.

Conditions that cannot be evaluated reliably should route to manual review.

#### Retrieval improvements

More rule-aware controlled queries may improve Context Precision and Context Recall, especially for exclusions, conflicts, claim limits, anomalies, and unsupported conditions.

This improvement would make analyst guidance more relevant, but it would not replace deterministic rule corrections.

#### Production governance

A production implementation would additionally require:

- authenticated and role-based access;
- encryption and secrets management;
- audit logging;
- operational monitoring and alerts;
- data-quality controls;
- knowledge-document versioning;
- rule, prompt, and model change control;
- fallback and incident procedures;
- formal human-override recording;
- privacy and retention controls;
- integration testing with authoritative enterprise systems.

### 5.4 Future Evaluation Priorities

A production pilot should extend the capstone evaluation by:

1. testing with representative historical claims under appropriate privacy controls;
2. increasing retrieval queries across products, rules, and jurisdictions;
3. expanding human review across multiple analysts;
4. measuring analyst acceptance and override rates;
5. evaluating handling time and procedural-search effort;
6. monitoring false `PROCEED` and false `NOT_ELIGIBLE` outcomes separately;
7. testing missing, conflicting, and delayed source data;
8. evaluating knowledge-base updates and stale-index controls;
9. assessing model and prompt version changes;
10. conducting operational, security, compliance, and responsible-AI review.

The principal production safety measures should include:

- unsafe continuation rate;
- manual-review recall;
- false non-eligibility rate;
- unresolved-condition routing;
- authority-preservation rate;
- critical guardrail failures.

Overall accuracy should remain a supporting measure rather than the sole indicator of safety.

### 5.5 Final Project Position

This capstone implemented and systematically evaluated a rule-grounded Agentic AI decision-support architecture.

The project:

- implemented modular deterministic triage tools;
- used LangGraph for controlled orchestration;
- created an allow-listed RAG pipeline with FAISS;
- evaluated lexical, semantic, hybrid, and reranked retrieval;
- generated guarded analyst-facing explanations;
- preserved deterministic authority and authorised human control;
- passed 149 regression tests;
- achieved 89.1% held-out accuracy against the approved 80% target;
- passed all eight held-out adversarial safety cases;
- documented the six unsafe-routing errors transparently.

The six incorrect `PROCEED` recommendations show that the current structured-data and deterministic-rule coverage is insufficient for production use. Guardrails successfully prevented LLM override, but they could not correct incomplete deterministic evaluation.

The final conclusion is:

> This capstone demonstrates a successful and evaluated rule-grounded Agentic AI decision-support prototype. It exceeded the approved primary accuracy target, preserved deterministic authority, maintained human control, and passed the held-out safety gate. However, stronger fail-safe routing and structured deterministic-rule coverage are required before production use. The final assessment is `MET_WITH_DOCUMENTED_LIMITATION`.
---

## References

## References

[1] University BYOC Programme, *Approved Proposal Form: Device Protection Claims Triage — A Rule-Grounded Agentic AI Decision-Support System*, approved project proposal, 2026.

[2] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W.-t. Yih, T. Rocktäschel, S. Riedel, and D. Kiela, “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” in *Advances in Neural Information Processing Systems*, vol. 33, 2020. [Available online](https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html).

[3] J. Johnson, M. Douze, and H. Jégou, “Billion-Scale Similarity Search with GPUs,” *arXiv preprint arXiv:1702.08734*, 2017. [Available online](https://arxiv.org/abs/1702.08734).

[4] OpenAI, “Vector Embeddings,” *OpenAI API Documentation*. [Available online](https://developers.openai.com/api/docs/guides/embeddings). Accessed 16 July 2026.

[5] LangChain, “LangGraph Overview,” *LangGraph Documentation*. [Available online](https://docs.langchain.com/oss/python/langgraph/overview). Accessed 16 July 2026.

[6] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” *arXiv preprint arXiv:1901.04085*, 2019. [Available online](https://arxiv.org/abs/1901.04085).

[7] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” in *Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations*, pp. 150–158, 2024. [Available online](https://aclanthology.org/2024.eacl-demo.16/).

[8] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, and I. Stoica, “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena,” *arXiv preprint arXiv:2306.05685*, 2023. [Available online](https://arxiv.org/abs/2306.05685).

[9] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” in *Proceedings of the 32nd International ACM SIGIR Conference on Research and Development in Information Retrieval*, pp. 758–759, 2009. [Available online](https://research.google/pubs/reciprocal-rank-fusion-outperforms-condorcet-and-individual-rank-learning-methods/).

### Project Repository and Supplementary Evidence

The complete source code, notebooks, tests, manifests, architecture decisions, frozen evaluation artifacts, reviewer walkthrough, and reproducibility guidance are available in the project repository:

[Device Protection Claims Triage — GitHub Repository](https://github.com/sadiqs3/DP_claims_triage)