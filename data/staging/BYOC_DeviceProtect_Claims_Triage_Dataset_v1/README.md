# DeviceProtect Synthetic Claims-Triage Dataset v1

## Purpose

A self-created, fictional data package for an academic agentic-AI proof of concept that triages device-protection claims. It does not contain real customer data, production policy wording, proprietary company rules or actual insurance decisions.

## Contents

- Reference data: triage taxonomy, plans, coverage, deterministic policy rules, lookup and question catalogues.
- Operational data: policy/device records, historical claims, current claims, evidence metadata and risk results.
- RAG corpus: seven SOP and glossary Markdown documents.
- Internal/evaluation data: ground-truth labels and safety/adversarial cases, which must not be exposed to the agent at runtime.

## Data profile

- Policy eligibility records: 120
- Historical claims: 112
- New claims - development: 165
- New claims - held-out evaluation: 55
- Evidence bundles: 220
- Evidence document metadata: 283
- Knowledge-base documents: 7
- Follow-up questions: 14
- Risk-trigger results: 6
- Ground-truth labels: 220
- Safety/adversarial tests: 24

## Licence and provenance

Original synthetic data created by the learner for the BYOC capstone. See `LICENSE.md`.

## Validation

The active package uses Policy Rules v1.2, not the earlier v1.1 catalogue. See `validation/final_data_validation_summary_v1_1.csv`.
