# Final Submission Rubric Evidence Matrix

## Purpose

This document controls the remaining final-submission work for:

**Device Protection Claims Triage: A Rule-Grounded Agentic AI Decision-Support System**

It maps each university rubric area to:

- current repository evidence,
- remaining evidence gaps,
- required final artifact,
- completion criteria,
- estimated remaining effort.

The matrix is intended to prevent scope creep. New work should be undertaken only when it closes an approved proposal commitment, rubric requirement, reproducibility gap, or confirmed implementation defect.

---

## Governing Scope Boundaries

The project remains a human-controlled decision-support system.

The following boundaries are fixed:

- Deterministic policy and eligibility rules remain authoritative.
- The LLM must not override triage outcomes or triggering rules.
- Risk indicators may route a case only to `MANUAL_REVIEW`.
- Follow-up questions must come from the approved catalogue.
- RAG provides non-authoritative analyst guidance only.
- The system does not approve claims, authorise payments, confirm fraud, or issue final customer denials.
- The accepted domain and synthetic dataset remain unchanged.
- The remaining work must stay within the approved 30–40 hour total project scope.

---

## Baseline Control Record

| Item | Verified value |
|---|---|
| Active branch | `final-submission-dev` |
| Frozen baseline branch | `main` |
| Frozen submission tag | `mid-submission-v1` |
| Baseline commit | `f42b60e83a7f6925e2e6ec751f763a28c1d98f4d` |
| Working tree at baseline | Clean |
| Regression tests | 136 passed |
| Python | 3.11.15 |
| FAISS | 1.14.3 |
| OpenAI SDK | 2.44.0 |
| LangGraph | 1.2.6 |
| Sentence Transformers | 5.6.0 |

---

## Rubric Evidence Matrix

| ID | Rubric area | Max marks | Current status | Existing repository evidence | Remaining action | Required final artifact | Completion criterion | Est. hours |
|---:|---|---:|---|---|---|---|---|---:|
| 1 | Business problem and GenAI suitability | 7 | Complete | Accepted proposal, `README.md`, `docs/mid_submission_summary.md`, `docs/architecture_decisions.md` | Preserve a clear explanation of why deterministic rules alone are insufficient for narrative understanding, explanation and SOP retrieval | Final report and presentation | Business problem, GenAI role and deterministic boundaries are clearly separated | 0.5 |
| 2 | Stakeholders, user experience and guardrails | 5 | Complete | Accepted proposal, decision taxonomy, controlled follow-up, analyst guidance formatter, content and response guardrails | Summarise stakeholder value and human-control boundaries | Final report and presentation | Analyst workflow and prohibited autonomous actions are explicitly documented | 0.5 |
| 3 | Data sourcing, provenance and legal usability | 4 | Complete | Synthetic dataset documentation, data dictionaries, licence files, data validation, proposal PII/IP declaration | Consolidate provenance and limitations into final README and report | README and final report | Source, synthetic-generation rationale, legal status, PII/IP position and limitations are stated | 0.5 |
| 4 | Data parsing, preparation and cleansing | 5 | Mostly complete | `src/data_loader.py`, `src/data_validation.py`, corpus builder, inventory notebook, data dictionaries and validation artifacts | Make the preprocessing and validation flow easy for a reviewer to locate | Final report and reviewer walkthrough | Parsing, validation, exclusions and structured preparation are evidenced | 0.5 |
| 5 | Chunking and embeddings | 5 | Mostly complete | `src/rag/corpus_builder.py`, semantic retriever, approved KB registry, chunk metadata and corpus fingerprint | Describe the implemented section-aware chunking accurately and avoid overstating generic semantic splitting | Final report and architecture documentation | Chunk boundaries, overlap/structure decisions, embedding model and trade-offs are documented | 0.5 |
| 6 | Vector storage and indexing | 7 | Complete | Persisted FAISS index, `semantic_index.faiss`, manifest, vector dimension, corpus and chunk-order fingerprints | Add exact index build, validation and load instructions | README and final reviewer walkthrough | Reviewer can reproduce or validate the persisted index | 0.5 |
| 7 | Retrieval and cross-encoder reranking | 11 | Complete | Lexical, semantic and hybrid retrievers; cross-encoder reranker; before/after metrics; retrieval manifests | Explain why the selected retrieval path is retained despite metric trade-offs | Final evaluation summary, report and slides | Top-K retrieval and reranking are quantitatively compared and honestly interpreted | 0.5 |
| 8 | Generation, orchestration, prompts and guardrails | 10 | Complete | LangGraph orchestrator, deterministic tools, OpenAI explainer, analyst guidance formatter, content guardrail, response guardrail | Add one concise end-to-end architecture and execution trace | Final report, slides and walkthrough | Reviewer can trace input, tools, retrieval, generation, guardrails and final output | 1.0 |
| 9 | Reproducibility | 7 | Mostly complete | Modular repository, `requirements.txt`, environment notebook, manifests, tests and relative paths | Perform clean-clone or fresh-folder validation and record commands/results | Final submission checklist and README | Setup, tests and reviewer workflow succeed from a clean copy | 1.0 |
| 10 | Architecture, modularity and index freshness | 7 | Mostly complete | Separated modules, architecture decisions, corpus fingerprinting, stale-index rejection, index manifest tests | Document the controlled rebuild procedure and embedding-rot handling | Architecture decisions and README | Changed corpus cannot silently use a stale index; rebuild path is documented | 0.5 |
| 11 | Automated evaluation framework | 12 | Partial | Retrieval metrics, development workflow metrics, safety metrics and reproducible manifests | Add bounded generation-quality evaluation for context relevance, groundedness, answer relevance and unsupported claims | Evaluation module/notebook, CSV results, manifest and summary | Quantitative generation-quality results exist on a frozen development subset | 3.0–4.0 |
| 12 | LLM-as-judge and documented human baseline | 10 | Not yet evidenced | No explicit judge-calibration artifact in the frozen baseline | Create a small human-reviewed subset, fixed scoring rubric, LLM judge and agreement analysis | Human review CSV, judge results CSV, calibration summary and manifest | Human and judge scores are compared; disagreements and limitations are documented | 3.0–4.0 |
| 13 | Technical report | 4 | Not started | Mid-submission documentation provides source material | Produce a dense 10–15 page technical report using the required six-section structure | Final technical report | Report meets template, references repository evidence and reports held-out results honestly | 4.0–5.0 |
| 14 | Executive presentation | 3 | Not started | Existing architecture and metrics can be reused | Produce an 8–12 slide boardroom narrative | Final presentation | Slides cover problem, architecture, demo, results, trade-offs, impact and limitations | 2.5–3.5 |
| 15 | GitHub repository and README | 3 | Mostly complete | Strong modular repository and mid-submission README | Add final status, held-out metrics, run sequence, artifact index, limitations and final reviewer path | Updated `README.md` | README functions as standalone reviewer onboarding | 1.0–1.5 |
| 16 | Final held-out evaluation and approved proposal success criteria | Proposal commitment | Not started | Held-out protocol and frozen 55-claim dataset exist | Freeze workflow, generate locked predictions, then reveal labels and evaluate | Held-out result CSVs, manifest, mismatch analysis and summary | At least 80% disposition agreement is assessed; zero critical safety failures is verified and honestly reported | 3.0–4.0 |

---

## Evidence Status Summary

### Complete or substantially complete

- Business framing and GenAI suitability.
- Stakeholder and human-control framing.
- Synthetic-data provenance and privacy safeguards.
- Deterministic triage engine.
- LangGraph orchestration.
- Controlled follow-up selection.
- Controlled RAG.
- FAISS persistence and fingerprint validation.
- Cross-encoder reranking.
- Response authority and content safety guardrails.
- Development workflow evaluation.
- Safety/adversarial evaluation.
- Regression-test baseline.

### Evidence strengthening required

- Data preparation narrative.
- Chunking rationale and terminology.
- Index rebuild and freshness procedure.
- Clean-clone reproducibility proof.
- Reviewer-facing architecture trace.
- Prompt evolution, failed iterations and safeguard reflections.

### Genuine remaining implementation or evaluation work

- Generation-quality evaluation.
- LLM-as-judge evaluation.
- Human-reviewed calibration subset.
- Development mismatch review and justified corrections.
- Locked held-out evaluation.
- Final reviewer walkthrough.
- Final report.
- Final presentation.
- Final repository packaging.

---

## Recommended Execution Order

1. Finalise this rubric evidence matrix.
2. Design the bounded generation-quality evaluation.
3. Create the human-reviewed calibration subset.
4. Implement and test the LLM judge.
5. Run development-only generation evaluation.
6. Review development workflow mismatches.
7. Apply only justified deterministic corrections.
8. Re-run regression, development and safety evaluations.
9. Freeze the final workflow and commit hash.
10. Run the locked 55-claim held-out evaluation.
11. Complete held-out mismatch analysis.
12. Build the final reviewer walkthrough.
13. Complete the technical report.
14. Complete the executive presentation.
15. Perform clean-clone verification.
16. Update README and final checklist.
17. Merge `final-submission-dev` into `main`.
18. Create the `final-submission-v1` tag.

---

## Stop Rules

Do not add a new feature when any of the following applies:

- It is not required by the accepted proposal or rubric.
- It introduces a new agent, UI, API, deployment platform or external dataset.
- It replaces deterministic authority with LLM judgement.
- It is intended only to chase a perfect development score.
- It requires tuning against held-out labels.
- It materially risks exceeding the approved effort limit.
- The same rubric evidence can be produced through documentation or a smaller evaluation addition.

---

## Remaining-Hours Control

| Work area | Planned hours |
|---|---:|
| Rubric and evidence control | 1 |
| Generation-quality evaluation | 3–4 |
| Human calibration and LLM judge | 3–4 |
| Development mismatch review and corrections | 4–6 |
| Workflow freeze and held-out evaluation | 4–5 |
| Safety and retrieval revalidation | 1–2 |
| Reviewer walkthrough | 2–3 |
| Technical report | 4–5 |
| Executive presentation | 2.5–3.5 |
| README, reproducibility and final packaging | 2–3 |
| **Estimated remaining total** | **26.5–36.5** |

Any increase beyond this range requires removal or reduction of a lower-priority task.

---

## Final Acceptance Checks

The final submission is ready only when:

- All tests pass.
- The final workflow commit is recorded.
- Development and held-out results are clearly separated.
- Held-out predictions were generated before label comparison.
- Critical safety failures are zero or transparently reported if not.
- Deterministic authority is preserved in every final output.
- Human and LLM-judge calibration evidence is available.
- Retrieval and generation evaluation artifacts are reproducible.
- The report is 10–15 pages.
- The presentation is 8–12 slides.
- The README supports a clean reviewer setup.
- The reviewer walkthrough runs end to end.
- `main` is updated only after final validation.
- The final release tag is created without modifying `mid-submission-v1`.
