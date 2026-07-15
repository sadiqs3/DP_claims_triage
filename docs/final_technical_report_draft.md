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

Device-protection claim triage requires analysts to reconcile policy status, device eligibility, incident coverage, prior-claim limits, evidence sufficiency, and operational exceptions before recommending the next action. Although deterministic rules are suitable for authoritative eligibility checks, manual workflows may become inconsistent when analysts must combine multiple structured records with supporting operational guidance under time pressure. Conversely, an unrestricted large language model may produce plausible but unsupported interpretations, particularly when policy facts are incomplete or conflicting. This capstone therefore investigates a hybrid approach in which deterministic rules retain decision authority while agentic and generative AI components support orchestration, information retrieval, explanation, and analyst review.

The implemented solution is a rule-grounded Agentic AI decision-support system with four triage outcomes: `PROCEED`, `INFO_REQUIRED`, `MANUAL_REVIEW`, and `NOT_ELIGIBLE`. Modular deterministic tools evaluate policy, plan, device, coverage, claim-history, evidence, and risk facts. LangGraph coordinates these tools with controlled follow-up-question selection, retrieval-augmented generation, analyst-facing explanation, and two protective guardrails. The retrieval layer uses an approved 21-chunk operational knowledge base, OpenAI semantic embeddings, a persisted FAISS index, and an optional cross-encoder reranker. Retrieved content and LLM-generated explanations are explicitly non-authoritative: they cannot change the deterministic outcome or triggering rule. Final approval, denial, payment, fraud assessment, and customer communication remain under authorised human control.

The project used a purpose-built, domain-representative synthetic claims ecosystem containing 220 new claims, of which 165 were reserved for development and 55 for final held-out evaluation. No real customer information, production claims, proprietary policy documents, or confidential organisational data were used. The technical implementation was validated through 149 regression tests, a 14-query retrieval benchmark, 12 frozen generation-quality cases, automated Ragas evaluation, human review, LLM-as-judge calibration, and a separate eight-case held-out adversarial safety assessment.

On the frozen 55-claim held-out set, the system achieved 49 correct triage outcomes, corresponding to an accuracy of **89.1%**, exceeding the approved target of 80%. Follow-up requirement accuracy was **100.0%**, exact follow-up selection was **93.3%**, policy-rule adherence was **89.1%**, and manual-review precision was **100.0%**. All eight held-out safety cases passed, with zero critical safety failures, 100% preservation of deterministic authority, and 100% preservation of the human-control boundary.

The evaluation also identified a material limitation. Six ordinary held-out claims were incorrectly routed to `PROCEED`, producing an unsafe-decision diagnostic of **10.9%**. Error analysis showed that these failures arose from gaps in structured authoritative data and deterministic rule coverage, including unresolved conflicts, exclusions, and eligibility-date conditions. They were not caused by RAG or LLM overrides. The prototype therefore requires fail-safe `MANUAL_REVIEW` routing, explicit `UNABLE_TO_EVALUATE` states, and stronger structured rule coverage before production use.

Overall, the project demonstrates that deterministic decision authority can be combined with controlled Agentic AI and RAG to improve the consistency, traceability, and explainability of claims-triage support without delegating final decision-making to an LLM. The approved proposal criteria were met, but the correct final assessment is **`MET_WITH_DOCUMENTED_LIMITATION`**, rather than production readiness.

---

## 1. Business Problem and Objectives

### 1.1 Business Context

Device-protection claims are typically evaluated against several interconnected sources of information, including policy status, plan configuration, registered device details, incident coverage, prior-claim history, evidence requirements, and risk or anomaly indicators. An analyst may need to establish whether the policy was active on the incident date, whether the claimed device matches the protected device, whether the incident type is covered by the plan, whether claim limits have been reached, and whether the submitted evidence is sufficient and internally consistent.

These checks are individually understandable, but the overall triage process becomes complex when multiple conditions must be evaluated in a defined order. A claim may appear eligible at one stage but require additional evidence, manual review, or a non-eligibility recommendation because of a higher-precedence condition identified later. Operational guidance may also be distributed across procedures and knowledge documents rather than presented alongside the authoritative policy facts.

The resulting challenge is not simply to classify a claim. The system must combine structured rule evaluation, evidence assessment, operational guidance, traceability, and safety controls while preserving the distinction between an internal triage recommendation and a legally or operationally binding claim decision.

This project addresses that need through a hybrid decision-support architecture. Deterministic tools evaluate authoritative business facts, while Agentic AI coordinates the workflow and provides controlled retrieval and explanation support. The design aims to improve consistency and traceability without transferring final decision authority to a large language model.

### 1.2 Problem Statement

A purely manual workflow may be affected by variation in analyst experience, fragmented information, repeated lookups, and inconsistent application of operational guidance. A purely generative solution introduces a different risk: an LLM may produce a plausible interpretation even when the relevant policy fact is missing, contradictory, unsupported, or outside the model's authority.

The central technical problem is therefore:

> How can deterministic policy and eligibility rules be combined with controlled Agentic AI, retrieval-augmented generation, and guardrails to support device-protection claim triage while preserving authoritative rule execution, traceability, safety, and authorised human control?

The project treats this as a decision-support problem rather than an autonomous adjudication problem. The system must determine a recommended next-step disposition, identify the triggering rule, retrieve relevant operational guidance, and communicate the reasoning to an analyst. It must not independently approve a claim, issue a final denial, authorise payment, determine fraud, or communicate a binding decision to a customer.

### 1.3 Stakeholders and User Experience

The primary user is a claims analyst who requires a concise, traceable recommendation supported by authoritative facts and relevant operational guidance. Additional stakeholders include claims operations managers, policy and product teams, risk and compliance functions, technology teams, and customers indirectly affected by the consistency and quality of the triage process.

| Stakeholder | Primary need | Relevant system control |
|---|---|---|
| Claims analyst | Clear next-step recommendation, supporting facts, required evidence, and applicable guidance | Structured triage result, rule trace, approved follow-up question, analyst explanation |
| Claims operations manager | Consistent handling and measurable workflow quality | Deterministic rule precedence, evaluation metrics, regression tests |
| Policy and product teams | Correct application of plan configuration and coverage rules | Authoritative policy, plan, device, and coverage tools |
| Risk and compliance teams | Prevention of unsupported automation and unsafe decisions | Manual-review routing, content-safety guardrail, authority guardrail |
| Technology teams | Maintainable, reproducible, and auditable implementation | Modular tools, LangGraph orchestration, manifests, fingerprints, automated tests |
| Customers | Fair and consistent handling with human accountability | Human-controlled final decision and restricted customer-facing authority |

The intended user experience is an analyst-facing workflow in which:

1. a claim is validated and linked to available authoritative records;
2. deterministic tools evaluate policy, eligibility, coverage, evidence, history, and risk facts;
3. rule precedence produces a recommended disposition and triggering rule;
4. an approved follow-up question is selected when more information is required;
5. relevant operational guidance is retrieved from an approved knowledge base;
6. an LLM produces a controlled analyst-facing explanation;
7. guardrails verify content safety and preserve the deterministic outcome;
8. an authorised human determines the final operational action.

This sequence supports the analyst without obscuring the source of authority or allowing generated content to replace business rules.

### 1.4 Project Objectives

The project has six principal objectives.

#### Objective 1: Implement authoritative deterministic triage

Develop modular tools that evaluate the core structured facts required for claim triage, including:

- policy and customer lookup;
- plan configuration and product scope;
- policy status on the incident date;
- protected-device match;
- incident coverage;
- prior-claim usage and limits;
- evidence sufficiency;
- risk, anomaly, and conflict indicators.

These tools must produce traceable results and remain authoritative over the final triage recommendation.

#### Objective 2: Implement controlled Agentic AI orchestration

Use LangGraph to coordinate deterministic tools, rule precedence, follow-up selection, retrieval, explanation, and guardrails as an explicit stateful workflow. The orchestration layer must improve modularity and traceability without acquiring decision authority.

#### Objective 3: Provide controlled operational guidance through RAG

Construct an approved operational knowledge base and evaluate lexical, semantic, hybrid, and reranked retrieval methods. Retrieval must use controlled queries derived from authoritative facts and must not modify the deterministic outcome.

#### Objective 4: Generate safe and grounded analyst explanations

Use an LLM to present the evaluated facts, applicable guidance, and recommended next step in a form useful to an analyst. The explanation must remain bounded by the authoritative context and pass both content-safety and response-authority controls.

#### Objective 5: Preserve human accountability

Ensure that claim approval, final denial, payment authorisation, fraud determination, and customer-facing communication remain outside the autonomous system boundary. The system output must be clearly positioned as decision support.

#### Objective 6: Evaluate the complete workflow systematically

Evaluate the solution through:

- automated regression tests;
- retrieval benchmarking;
- human generation review;
- LLM-as-judge evaluation and calibration;
- automated Ragas metrics;
- frozen held-out claim evaluation;
- held-out adversarial safety testing;
- documented error and limitation analysis.

### 1.5 Success Criteria

The approved proposal defined the primary success criterion as agreement with ground-truth triage outcomes on at least 80% of a 55-claim held-out evaluation set.

The final assessment also reports supporting measures to provide a more complete view of performance and safety.

| Criterion | Intended measure |
|---|---|
| Primary disposition accuracy | Percentage of held-out claims assigned the correct triage outcome |
| Policy-rule adherence | Agreement between the workflow result and expected business-rule application |
| Exact primary-rule agreement | Correct identification of the principal triggering rule |
| Follow-up requirement accuracy | Correct identification of whether additional information is required |
| Exact follow-up selection | Correct selection of the approved follow-up question |
| Manual-review recall | Proportion of required manual-review cases correctly identified |
| Manual-review precision | Proportion of predicted manual-review cases that genuinely require review |
| Unsafe-decision diagnostic | Cases incorrectly routed to `PROCEED` when a safer outcome was expected |
| Adversarial safety performance | Preservation of deterministic outcomes and blocking of unsafe overrides |
| Human-control preservation | Confirmation that final operational authority remains with an authorised person |

The approved safety gate required zero critical failures in the held-out adversarial safety evaluation. A critical failure would include an unsafe LLM override, fabricated authority, autonomous approval or denial, fraud determination, payment authorisation, or loss of the human-control boundary.

### 1.6 Scope and Human-Control Boundary

The system produces one of four internal triage recommendations:

| Outcome | Operational meaning |
|---|---|
| `PROCEED` | Available authoritative facts support continuation to standard processing; this is not a claim approval |
| `INFO_REQUIRED` | A defined item of evidence or information is missing and an approved follow-up is required |
| `MANUAL_REVIEW` | A conflict, anomaly, unsupported condition, risk trigger, or evaluation uncertainty requires authorised review |
| `NOT_ELIGIBLE` | Deterministic rules support a non-eligibility recommendation; this is not a final customer-facing denial |

The following functions are within scope:

- synthetic claims-data preparation and validation;
- deterministic policy and eligibility evaluation;
- evidence, history, and risk assessment;
- LangGraph workflow orchestration;
- approved follow-up-question selection;
- controlled RAG over an allow-listed knowledge base;
- FAISS semantic retrieval;
- optional cross-encoder reranking;
- LLM-based analyst explanation support;
- content-safety and response-authority guardrails;
- systematic development and held-out evaluation.

The following functions are intentionally outside scope:

- autonomous claim approval;
- final customer-facing denial;
- payment or settlement authorisation;
- fraud determination;
- unrestricted customer communication;
- use of customer narrative as verified policy evidence;
- live enterprise-system integration;
- production deployment and user-interface development;
- external web search;
- additional autonomous agents;
- model fine-tuning;
- long-term conversational memory.

The governing design principle is:

> Deterministic rules evaluate authoritative claim facts; Agentic AI coordinates the workflow; RAG retrieves non-authoritative operational guidance; the LLM explains the result; and an authorised human remains accountable for the final action.

This boundary is central to both the technical architecture and the ethical position of the project.

---

## 2. Data and Knowledge Preparation

### 2.1 Synthetic Data Strategy

Access to real device-protection claims is restricted by privacy, commercial sensitivity, and intellectual-property considerations. Production claims may contain personal identifiers, device details, incident descriptions, financial information, policy records, and operational decisions that cannot be used safely in an academic repository. Proprietary policy rules and internal operating procedures may also be unsuitable for public disclosure.

The project therefore used a purpose-built, domain-representative synthetic data ecosystem. The objective was not to reproduce any specific organisation's production data, but to create a legally usable and internally consistent test environment that represented the principal entities and decision conditions involved in device-protection claim triage.

The synthetic ecosystem models relationships among:

- policy and customer records;
- protected devices;
- plan configuration and product scope;
- coverage by incident type;
- policy status on the incident date;
- historical claims and usage limits;
- submitted evidence;
- risk and anomaly indicators;
- operational knowledge documents;
- approved follow-up questions;
- expected triage outcomes and triggering rules.

This relational design was necessary because the triage outcome depends on interactions among multiple authoritative sources rather than on a single claim description. For example, an incident may be covered by a plan but still require additional evidence, exceed a claim limit, contain conflicting identifiers, or fall outside the active policy period.

The synthetic records were designed to represent both routine and boundary conditions across the four target outcomes:

- `PROCEED`;
- `INFO_REQUIRED`;
- `MANUAL_REVIEW`;
- `NOT_ELIGIBLE`.

The dataset also contains adversarial and edge cases intended to test whether generated explanations or malicious instructions could override deterministic authority. Synthetic data therefore supported both functional evaluation and safety evaluation without exposing real customer or organisational information.

### 2.2 Dataset Structure and Volumes

The final project dataset contains structured claim, policy, evidence, history, guidance, and evaluation records.

**Table 2.1 — Final dataset volumes**

| Dataset component | Record count | Role in the solution |
|---|---:|---|
| Policy-device records | 120 | Authoritative policy, customer, plan, and protected-device relationships |
| Historical claims | 112 | Prior-claim usage and claim-limit evaluation |
| New claims | 220 | Claims evaluated by the developed workflow |
| Development claims | 165 | Implementation, debugging, and development evaluation |
| Held-out claims | 55 | Final frozen evaluation only |
| Evidence bundles | 220 | Claim-level evidence availability and completeness |
| Evidence document records | 283 | Individual evidence items linked to evidence bundles |
| Knowledge-base documents | 7 | Approved synthetic operational guidance |
| Approved knowledge-base chunks | 21 | Retrieval units used by lexical, semantic, hybrid, and reranked retrieval |
| Approved follow-up questions | 14 | Controlled questions available to the workflow |
| Ground-truth labels | 220 | Expected outcomes, rules, and evaluation attributes |
| Safety and adversarial cases | 24 | Development and final guardrail testing |
| Held-out safety cases | 8 | Frozen final adversarial safety gate |

The 220 new claims were divided into 165 development claims and 55 held-out claims. Claim identifiers in the two partitions were verified as disjoint. The development partition was used for implementation, workflow inspection, retrieval evaluation, generation-quality evaluation, and debugging. The held-out partition was reserved for final evaluation and was not used to modify the frozen workflow after its labels were revealed.

The ground-truth data records the expected triage outcome and associated evaluation attributes. These labels were generated from the intended synthetic scenario definitions and rule conditions. They were stored separately from the runtime claims so that the workflow could operate only on the information available to the simulated analyst process.

The final held-out protocol strengthened this separation by:

1. running all 55 held-out claims without consulting their labels;
2. exporting the prediction-only artifact;
3. calculating a SHA-256 fingerprint for that artifact;
4. joining the labels only after predictions were frozen;
5. calculating performance metrics without subsequent tuning.

This procedure reduces the risk of adapting the workflow to the final evaluation cases and preserves the integrity of the reported result.

### 2.3 Data Validation and Preparation

The source data consists primarily of controlled CSV and JSON records together with Markdown knowledge documents. Consequently, optical character recognition and complex PDF-layout extraction were not required. Data preparation focused instead on structural validity, referential integrity, metadata quality, and separation of authoritative and non-authoritative information.

The validation process covered the following areas.

#### Schema and mandatory-field validation

Each dataset was checked for its expected columns, required identifiers, supported categorical values, and mandatory fields. This ensured that downstream tools received predictable input structures and that missing critical fields could be detected explicitly rather than causing silent processing errors.

#### Identifier and relationship validation

The project models linked entities such as claims, policies, devices, evidence bundles, evidence documents, and historical claims. Validation therefore checked that referenced identifiers existed in the relevant authoritative source and that links were logically consistent.

Examples include:

- claim-to-policy relationships;
- policy-to-device relationships;
- evidence-bundle-to-claim relationships;
- evidence-document-to-bundle relationships;
- historical-claim-to-policy relationships;
- ground-truth-label-to-claim relationships.

#### Date and status preparation

Date fields required for policy eligibility and incident-date checks were normalised into consistent machine-readable representations. Policy status, incident date, policy start and end dates, and related eligibility attributes were prepared for deterministic comparison.

The held-out evaluation later showed that date-related rule coverage still requires strengthening for production use. Nevertheless, the preparation layer ensured that available structured dates were consistently represented and could be consumed by the deterministic tools.

#### Categorical and logical validation

Controlled values were used for attributes such as:

- policy and plan status;
- product scope;
- incident type;
- coverage status;
- evidence state;
- risk indicators;
- triage outcome;
- triggering rule;
- follow-up requirement.

This reduced uncontrolled variation and supported deterministic rule execution.

#### Partition and leakage controls

Development and held-out claim identifiers were verified as non-overlapping. Held-out labels were not supplied to the runtime workflow and were not used during development. Evaluation manifests record the relevant artifacts, configurations, and partition boundaries.

#### Data profiling and review

Notebook 01 documents the inventory, shapes, key relationships, and validation results for the prepared datasets. The supporting validation modules provide reusable checks rather than relying solely on visual notebook inspection.

The principal implementation evidence is contained in:

- `src/data_loader.py`;
- `src/data_validation.py`;
- `notebooks/01_data_inventory.ipynb`;
- the prepared files under `data/runtime/`;
- the supporting records under `data/internal/`.

This preparation strategy prioritised reproducibility and rule reliability over unnecessary transformation of already controlled synthetic sources.

### 2.4 Knowledge-Base Preparation

The retrieval component uses seven approved synthetic knowledge documents containing operational guidance relevant to claim triage. These documents are non-authoritative: they explain procedures, evidence handling, escalation expectations, and analyst guidance, but they do not determine policy eligibility or the final triage outcome.

A source allow-list controls which documents may enter the retrieval corpus. This prevents arbitrary files, customer narrative, or unapproved text from being treated as operational guidance.

The corpus-building process performs the following steps:

1. loads only documents registered in the approved knowledge-base configuration;
2. validates source metadata and document identity;
3. divides documents using meaningful section boundaries;
4. creates retrieval metadata for each section;
5. preserves stable chunk ordering;
6. generates corpus and chunk-order fingerprints;
7. produces the final 21-chunk retrieval corpus.

Section-aware chunking was selected because the source documents are short and structurally organised. Each chunk corresponds to a coherent guidance section rather than an arbitrary fixed-length window. The resulting chunks preserve the subject and procedural meaning of their source sections.

Overlapping chunks were not used. In this corpus, overlap would have duplicated substantial portions of short guidance sections and could have produced multiple near-identical results in the top-ranked set. The frozen retrieval benchmark also did not provide evidence that a chunking change was necessary. Chunking was therefore retained as a deliberate design decision rather than modified solely to satisfy a generic document-processing pattern.

Each chunk contains metadata that supports traceability, including its source document and section identity. The persisted FAISS index also records information required to validate whether the index remains aligned with the current corpus. Corpus fingerprints and stable chunk order help detect stale or mismatched indexes before retrieval is performed.

The knowledge base is used only after deterministic triage. A controlled query is generated from allow-listed authoritative facts such as:

- the deterministic outcome;
- triggering rule;
- evidence state;
- coverage result;
- manual-review requirement;
- relevant structured decision context.

Arbitrary customer narrative is excluded from the controlled retrieval query because it has not been independently verified. This separation prevents untrusted narrative from acquiring policy authority through the retrieval process.

The principal implementation evidence is contained in:

- `src/rag/corpus_builder.py`;
- the approved documents under `data/knowledge_base/`;
- the persisted corpus and index artifacts under `data/artifacts/rag/`;
- `notebooks/05_sop_rag_retrieval.ipynb`.

### 2.5 Data Governance, Privacy, and Limitations

The project applies the following data-governance controls:

- all claim and policy data is synthetic and project-generated;
- no real customer PII is used;
- no production claims are included;
- no proprietary enterprise policy or operational documents are reproduced;
- source documents entering the knowledge base are explicitly allow-listed;
- customer narrative is not treated as verified policy evidence;
- development and held-out partitions are separated;
- held-out predictions are fingerprinted before label comparison;
- held-out results are not used for subsequent tuning;
- generated explanations remain subordinate to deterministic facts.

These controls make the repository suitable for academic review and public version control while preserving the intended business-domain structure.

The synthetic-data strategy also introduces limitations. Synthetic records may reflect the assumptions of their creator and cannot fully represent the variety, ambiguity, missingness, behavioural patterns, or operational complexity found in production claims. The controlled source formats are cleaner than real-world data, which may include scanned documents, inconsistent formats, duplicate records, unstructured communications, and incomplete system integration.

The reported evaluation results should therefore be interpreted as evidence about the implemented prototype under the defined synthetic conditions. They do not establish production performance or generalisation to a real claims portfolio.

A production implementation would require:

- approved access to representative historical data;
- formal privacy and retention controls;
- role-based access;
- data-quality monitoring;
- validated mappings to authoritative enterprise systems;
- controlled policy and rule ownership;
- audit logging;
- ongoing drift and exception analysis;
- additional evaluation across products, markets, incident types, and operational teams.

Within the approved capstone boundary, the synthetic ecosystem provides a sufficiently structured and traceable basis for implementing and evaluating the hybrid deterministic and Agentic AI design. Its limitations are explicitly retained as part of the final production-readiness assessment.

---

## 3. Solution Architecture and Design Rationale

### 3.1 End-to-End Architecture

The solution uses a hybrid architecture that separates authoritative claim evaluation from non-authoritative AI assistance. Structured policy and claim facts are first processed through deterministic tools. LangGraph then coordinates follow-up selection, knowledge retrieval, explanation generation, and guardrail validation around the authoritative result.

The architecture consists of seven logical layers:

1. claim and reference data;
2. deterministic triage tools;
3. rule precedence and authoritative disposition;
4. controlled follow-up selection;
5. retrieval-augmented analyst guidance;
6. LLM explanation and protective guardrails;
7. authorised human review.

**Figure 3.1 — End-to-End System Architecture**

*Insert the final end-to-end architecture diagram here.*

The overall processing flow is:

1. Claim intake and input validation
2. Deterministic policy, coverage, evidence, history, and risk checks
3. Rule precedence and authoritative triage outcome
4. Controlled follow-up-question selection
5. Controlled retrieval-query construction
6. FAISS semantic retrieval
7. Optional cross-encoder reranking
8. LLM-generated analyst explanation
9. Content-safety validation
10. Response-authority validation
11. Authorised human review

The central architectural principle is:

> Deterministic rules determine the claim-triage recommendation; Agentic AI coordinates supporting processes; RAG retrieves approved operational guidance; the LLM explains the result; and an authorised human remains accountable for final action.

This design avoids two unsuitable extremes. A rules-only implementation would provide consistency and traceability but limited retrieval and explanation support. An unrestricted LLM workflow could provide fluent responses but would introduce unacceptable uncertainty around policy interpretation, evidence handling, and decision authority.

The hybrid architecture retains deterministic control over business decisions while using generative AI only where semantic retrieval, explanation, and workflow assistance provide clear value.

### 3.2 Deterministic Decision Authority

The deterministic layer is the authoritative decision component. It evaluates structured claim facts through modular tools covering:

- policy and customer lookup;
- plan configuration;
- product eligibility;
- policy status on the incident date;
- protected-device match;
- incident coverage;
- prior-claim usage and limits;
- evidence availability and sufficiency;
- risk and anomaly indicators;
- data conflicts and unsupported conditions.

Each tool returns a structured result rather than free-form prose. These outputs are consolidated into an authoritative claim context and then evaluated through a defined rule-precedence sequence.

Rule precedence is necessary because more than one condition may apply to the same claim. For example, an incident may be covered by the plan but still require additional evidence, exceed a claim limit, contain conflicting identifiers, or fall outside the active policy period. The workflow must apply the highest-priority relevant rule rather than selecting an outcome based only on evaluation order.

The deterministic layer produces:

- the recommended disposition;
- the triggering rule;
- the precedence stage;
- the decision reason;
- the supporting structured facts;
- the traceable rule path.

The four supported dispositions are:

- `PROCEED`;
- `INFO_REQUIRED`;
- `MANUAL_REVIEW`;
- `NOT_ELIGIBLE`.

These are internal decision-support recommendations. They are not equivalent to claim approval, final denial, payment authorisation, or fraud determination.

The LLM does not participate in rule selection. Even when an explanation is generated, the deterministic disposition and triggering rule remain protected values that are validated again by the response-authority guardrail.

### 3.3 LangGraph Agentic Orchestration

LangGraph was selected to represent the workflow as an explicit stateful graph rather than as a loosely connected sequence of function calls. The compiled workflow used in the final implementation is identified as `langgraph_v6`.

The implemented node sequence is:

1. `START`
2. `deterministic_triage`
3. `controlled_follow_up_selection`
4. `controlled_rag_retrieval`
5. `explanation_proposal`
6. `agent_content_safety_guardrail`
7. `response_guardrail`
8. `END`

**Figure 3.2 — LangGraph Orchestration Flow**

*Insert the detailed LangGraph node-level diagram here.*

The graph state carries the original claim input and progressively adds:

- deterministic tool outputs;
- authoritative triage facts;
- disposition and triggering rule;
- approved follow-up selection;
- controlled retrieval query;
- retrieved knowledge chunks;
- proposed analyst explanation;
- content-safety status;
- guarded final response.

LangGraph contributes three important capabilities.

#### Explicit workflow state

Each node reads from and writes to a defined state. This reduces hidden dependencies and makes the origin of each output easier to inspect.

#### Controlled execution order

Deterministic triage is completed before retrieval and generation. AI-support components therefore operate on an established authoritative result rather than influencing its creation.

#### Guarded conditional behaviour

Retrieval and explanation can be enabled, disabled, or replaced by a controlled fallback without changing the deterministic outcome. Guardrail nodes may reject unsafe generated content while preserving the underlying triage result.

The graph is agentic because it coordinates specialised tools and conditional stages towards a defined claim-triage objective. It is not an autonomous adjudication agent. Its authority is intentionally restricted to orchestration.

### 3.4 Controlled RAG and FAISS Retrieval

Retrieval-Augmented Generation is used to provide operational guidance relevant to the deterministic outcome. It is not used to determine policy eligibility, coverage, or claim disposition.

The retrieval pipeline consists of:

1. an approved seven-document synthetic knowledge base;
2. section-aware corpus construction;
3. 21 traceable knowledge chunks;
4. semantic embedding generation;
5. FAISS vector indexing;
6. controlled Top-K retrieval;
7. optional cross-encoder reranking;
8. analyst-guidance formatting.

**Figure 3.3 — Controlled Retrieval Pipeline**

*Insert the retrieval pipeline diagram here.*

The controlled retrieval query is built from selected authoritative facts, including:

- deterministic disposition;
- triggering rule;
- evidence state;
- coverage result;
- manual-review requirement;
- relevant structured decision context.

Customer narrative is excluded from the controlled query because it has not been independently verified. This prevents untrusted text from influencing retrieval as though it were authoritative policy information.

The semantic retrieval configuration uses:

| Component | Configuration |
|---|---|
| Embedding model | `text-embedding-3-small` |
| Embedding dimension | 1536 |
| Vector index | FAISS `IndexFlatIP` |
| Approved knowledge-base chunks | 21 |

FAISS `IndexFlatIP` was selected because the corpus is small and exact similarity search is appropriate. With only 21 chunks, an approximate-nearest-neighbour index would introduce additional complexity without providing a meaningful performance advantage.

The persisted index includes controls for:

- expected vector dimension;
- corpus fingerprint;
- stable chunk-order fingerprint;
- index-to-corpus consistency;
- stale-index detection.

These controls reduce the risk of retrieving against an index that no longer matches the approved knowledge corpus.

RAG remains explicitly non-authoritative. Retrieved guidance may explain the next operational step, but it cannot:

- change coverage;
- create policy eligibility;
- alter evidence requirements;
- override a claim limit;
- independently apply an exclusion;
- replace the triggering rule;
- approve or deny a claim.

### 3.5 Cross-Encoder Reranking

A cross-encoder reranker was evaluated as a second-stage retrieval mechanism using `cross-encoder/ms-marco-MiniLM-L-6-v2`.

The semantic retriever first selects a candidate set. The cross-encoder then jointly evaluates each query-and-chunk pair and reorders the candidates according to predicted relevance.

This approach can provide finer-grained comparison than independent embedding similarity because the query and document text are processed together. However, it also introduces additional computation, model dependency, latency, and possible ranking instability.

The frozen retrieval benchmark produced mixed results:

- two queries improved;
- two queries regressed;
- nine retained the same top-ranked chunk;
- one remained a persistent Top-3 miss;
- aggregate MRR@3 decreased from 0.857 to 0.845.

The reranker therefore remains available as a controlled optional stage, but it is not the default retrieval method.

This decision follows an evidence-based engineering principle:

> Additional model complexity should be adopted only when it produces a consistent and measurable improvement in the target workflow.

Semantic embedding retrieval remains the default because it achieved the strongest aggregate result on the frozen benchmark.

### 3.6 LLM Explanation Support and Guardrails

The LLM transforms structured triage facts and retrieved operational guidance into a concise analyst-facing explanation. Its role is communicative rather than adjudicative.

The explanation context contains:

- the deterministic disposition;
- the triggering rule;
- structured policy and claim facts;
- evidence assessment;
- approved follow-up selection;
- retrieved operational guidance;
- explicit authority and safety constraints.

The generated response is expected to explain:

- why the claim received the recommended disposition;
- which authoritative conditions were relevant;
- what evidence or review is required;
- how the analyst should interpret the recommendation;
- the limitations of the system output.

Two guardrails protect the generated result.

#### Agent Content-Safety Guardrail

The content-safety guardrail checks for prohibited or unsafe generated behaviour, including:

- autonomous approval or denial;
- payment authorisation;
- fraud confirmation;
- unsupported policy statements;
- fabricated evidence;
- instructions to bypass human review;
- responses influenced by malicious or adversarial instructions.

When unsafe content is detected, the proposed explanation is replaced by a controlled fallback response.

#### Response-Authority Guardrail

The response-authority guardrail verifies that protected fields remain aligned with the deterministic result.

It preserves:

- the final disposition;
- the triggering rule;
- the follow-up requirement;
- the approved follow-up question;
- decision-support wording;
- the human-control notice.

When generated content attempts to modify these values, the deterministic values are restored and the attempted override is recorded as blocked.

This design recognises that prompt instructions alone are insufficient as a safety mechanism. The final response is mechanically compared with the authoritative workflow state rather than relying only on the LLM to follow instructions.

### 3.7 Human-Control Boundary

The final system output is intended for an authorised claims analyst. It provides structured decision support but does not complete the claim decision.

The system may:

- recommend a triage outcome;
- identify the triggering rule;
- present authoritative supporting facts;
- select an approved follow-up question;
- retrieve relevant operational guidance;
- generate a guarded analyst explanation.

The system may not:

- approve a claim;
- issue a final customer-facing denial;
- authorise settlement or payment;
- confirm or determine fraud;
- create unapproved customer questions;
- treat unverified narrative as authoritative policy evidence;
- bypass required human review.

The human analyst remains responsible for:

- reviewing the available records;
- resolving data conflicts;
- assessing unsupported or unusual conditions;
- obtaining additional evidence;
- making the final operational decision;
- ensuring that customer communication follows approved procedures.

Human control is not treated merely as a disclaimer added after generation. It is implemented through:

- deterministic decision authority;
- manual-review routing;
- approved follow-up selection;
- restricted LLM prompts;
- content-safety validation;
- response-authority validation;
- explicit decision-support notices.

The architecture therefore applies a defence-in-depth approach to human accountability.

### 3.8 Technologies Considered but Not Adopted

Several technologies and architectural extensions were considered but intentionally excluded from the final capstone.

| Technology or approach | Reason not adopted |
|---|---|
| Fully autonomous LLM decision-making | Incompatible with policy authority, safety, auditability, and human-accountability requirements |
| Multi-agent debate or voting | Added complexity without a demonstrated benefit for a deterministic-rule-governed workflow |
| Model fine-tuning | The problem required rule grounding and controlled retrieval rather than behavioural adaptation of a model |
| Knowledge graph | Potentially useful for larger policy ecosystems, but unnecessary for the limited synthetic corpus and project scope |
| External web search | Operational guidance had to remain within an approved and reproducible knowledge boundary |
| Long-term conversational memory | Not required for single-claim triage and could introduce privacy and state-management risks |
| Autonomous follow-up generation | Replaced by selection from an approved catalogue to preserve wording control |
| Customer narrative as authoritative evidence | Narrative may be incomplete, contradictory, or unverified |
| Approximate FAISS indexing | The 21-chunk corpus is sufficiently small for exact similarity search |
| Default cross-encoder reranking | Frozen evaluation did not show a consistent aggregate improvement |
| User-interface development | Outside the approved technical and effort scope |
| Production deployment | Requires enterprise integration, security, monitoring, and governance beyond the capstone |
| Live enterprise-data integration | Real systems and production data were unavailable and inappropriate for an academic prototype |

The final architecture was selected to maximise:

- rule correctness;
- traceability;
- reproducibility;
- controlled use of generative AI;
- safety;
- human accountability;
- alignment with the approved 30–40 hour capstone boundary.

The result is a bounded Agentic AI architecture in which each component has a clearly defined responsibility and authority level.

---

## 4. Implementation

### 4.1 Modular Repository Structure

_Content to be added._

### 4.2 Deterministic Triage Tools

_Content to be added._

### 4.3 Rule Precedence and Triage Outcomes

_Content to be added._

### 4.4 Controlled Follow-Up Selection

_Content to be added._

### 4.5 Corpus, Embeddings, and FAISS Index

_Content to be added._

### 4.6 Controlled Query and Explanation Workflow

_Content to be added._

### 4.7 Content-Safety and Authority Guardrails

_Content to be added._

### 4.8 Testing and Reproducibility

_Content to be added._

---

## 5. Design Evolution and Transparency Log

### 5.1 Controlled Follow-Up Selection

_Content to be added._

### 5.2 Treatment of Customer Narrative

_Content to be added._

### 5.3 Retrieval Technology Decisions

_Content to be added._

### 5.4 Reranker Evaluation and Final Decision

_Content to be added._

### 5.5 Hybrid Ragas Evaluation Design

_Content to be added._

### 5.6 LLM-Judge Calibration

_Content to be added._

### 5.7 Frozen Held-Out Evaluation Protocol

_Content to be added._

---

## 6. Evaluation Methodology

### 6.1 Regression Testing

_Content to be added._

### 6.2 Retrieval Evaluation

_Content to be added._

### 6.3 Human Generation Review

_Content to be added._

### 6.4 LLM-as-Judge Evaluation

_Content to be added._

### 6.5 Automated Ragas Evaluation

_Content to be added._

### 6.6 Final Held-Out Claim Evaluation

_Content to be added._

### 6.7 Held-Out Adversarial Safety Evaluation

_Content to be added._

---

## 7. Results

### 7.1 Regression-Test Results

_Content to be added._

### 7.2 Retrieval and Reranking Results

_Content to be added._

### 7.3 Human Review and LLM-Judge Results

_Content to be added._

### 7.4 Ragas Results

_Content to be added._

### 7.5 Final Held-Out Results

_Content to be added._

### 7.6 Safety and Governance Results

_Content to be added._

### 7.7 Proposal Commitment versus Final Outcome

_Content to be added._

---

## 8. One Claim Journey

_Content and diagram to be added._

---

## 9. Limitations and Production Readiness

### 9.1 Material Held-Out Limitation

_Content to be added._

### 9.2 Root-Cause Analysis

_Content to be added._

### 9.3 Required Production Improvements

_Content to be added._

### 9.4 Remaining Operational and Governance Requirements

_Content to be added._

---

## 10. Business Impact and Conclusion

### 10.1 Expected Business Value

_Content to be added._

### 10.2 Final Project Assessment

_Content to be added._

### 10.3 Conclusion

_Content to be added._

---

## References

_Content to be added._

---

## Appendix A — Key Evaluation Artifacts

_Content to be added._