from __future__ import annotations

# Connects deterministic triage facts to controlled persisted-KB retrieval.
# This tool is read-only and cannot change claim routing or follow-up wording.

from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from src.claim_context import assemble_claim_context
from src.rag.controlled_query_builder import ControlledRAGQueryBuilder
from src.rag.corpus_builder import build_rag_corpus, get_project_root
from src.rag.faiss_retriever import ControlledPersistedFAISSRetriever
from src.rag.semantic_retriever import DEFAULT_MIN_RELEVANCE_SCORE
from src.rag.triage_facts_projection import (
    PROJECTION_NAME,
    PROJECTION_VERSION,
    project_authoritative_rag_facts,
)


TOOL_NAME = "controlled_rag_retrieval"
TOOL_VERSION = "projection_faiss_v1"


def _as_dict(value: object) -> dict[str, Any]:
    """Return a plain dictionary for a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return dict(value)

    return {}


def _default_artifact_dir() -> Path:
    """Return the standard persisted FAISS artifact directory."""
    return (
        get_project_root()
        / "data"
        / "artifacts"
        / "rag"
        / "faiss_semantic_index_v1"
    )


def _validate_claim_id(claim_id: object) -> str:
    """Validate and normalise the claim identifier used for lookup only."""
    if not isinstance(claim_id, str) or not claim_id.strip():
        raise ValueError("claim_id must be a non-empty string.")

    return claim_id.strip()


def _extract_deterministic_decision(
    deterministic_tool_result: Mapping[str, Any],
    claim_id: str,
) -> dict[str, Any]:
    """Validate deterministic-triage provenance and claim alignment."""
    tool_result = _as_dict(deterministic_tool_result)

    if tool_result.get("tool_name") != "deterministic_triage":
        raise ValueError(
            "deterministic_tool_result must originate from "
            "deterministic_triage."
        )

    decision = _as_dict(tool_result.get("deterministic_decision"))

    if not decision:
        raise ValueError(
            "deterministic_tool_result must contain deterministic_decision."
        )

    decision_claim_id = str(decision.get("claim_id", "")).strip()

    if decision_claim_id != claim_id:
        raise ValueError(
            "claim_id does not match deterministic_decision claim_id."
        )

    return decision


def _build_approved_corpus(data: Mapping[str, Any]) -> pd.DataFrame:
    """Build the approved retrieval corpus from the runtime registry."""
    registry = data.get("rag_document_registry")

    if not isinstance(registry, pd.DataFrame):
        raise ValueError(
            "Runtime data is missing rag_document_registry."
        )

    return build_rag_corpus(registry.copy())


def run_controlled_rag_retrieval(
    data: Mapping[str, Any],
    claim_id: str,
    deterministic_tool_result: Mapping[str, Any],
    artifact_dir: str | Path | None = None,
    top_k: int = 3,
    min_relevance_score: float = DEFAULT_MIN_RELEVANCE_SCORE,
    client: object | None = None,
) -> dict[str, Any]:
    """
    Retrieve approved analyst guidance for a deterministic triage result.

    The retrieval query is built only from allow-listed structured facts
    projected from deterministic context. It excludes customer narrative,
    identifiers, document text, decision reasons, and arbitrary rule traces.

    Retrieved content is non-authoritative and cannot alter deterministic
    triage, eligibility routing, evidence requirements, or follow-up wording.
    """
    if not isinstance(data, Mapping):
        raise ValueError("data must be a mapping of runtime datasets.")

    normalised_claim_id = _validate_claim_id(claim_id)

    decision = _extract_deterministic_decision(
        deterministic_tool_result=deterministic_tool_result,
        claim_id=normalised_claim_id,
    )

    context = assemble_claim_context(
        data=dict(data),
        claim_id=normalised_claim_id,
    )

    facts = project_authoritative_rag_facts(
        context=context,
        deterministic_decision=decision,
    )

    controlled_query = ControlledRAGQueryBuilder().build(facts)

    approved_corpus = _build_approved_corpus(data)

    retriever = ControlledPersistedFAISSRetriever.from_artifacts(
        corpus=approved_corpus,
        artifact_dir=(
            Path(artifact_dir)
            if artifact_dir is not None
            else _default_artifact_dir()
        ),
    )

    retrieval_result = retriever.retrieve(
        query=controlled_query,
        top_k=top_k,
        min_relevance_score=min_relevance_score,
        client=client,
    )

    tool_result = _as_dict(deterministic_tool_result)

    return {
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "claim_id": normalised_claim_id,
        "decision_source": (
            f"{tool_result.get('tool_name', 'unknown')}:"
            f"{tool_result.get('tool_version', 'unknown')}"
        ),
        "projection_source": f"{PROJECTION_NAME}:{PROJECTION_VERSION}",
        "retrieval_source": (
            f"{retrieval_result['tool_name']}:"
            f"{retrieval_result['tool_version']}"
        ),
        "authority": "non_authoritative_guidance",
        "authority_notice": (
            "Controlled RAG retrieval provides analyst-facing guidance only. "
            "It cannot override deterministic triage, policy eligibility, "
            "evidence requirements, or controlled customer follow-up wording."
        ),
        "projected_facts": asdict(facts),
        "controlled_query": {
            "query_text": controlled_query.query_text,
            "query_fingerprint": controlled_query.query_fingerprint,
            "source": controlled_query.source,
            "audience": controlled_query.audience,
            "authority": controlled_query.authority,
        },
        "retrieval_status": retrieval_result["retrieval_status"],
        "retrieved_guidance_count": retrieval_result["result_count"],
        "retrieved_guidance": retrieval_result["results"],
        "retrieval_result": retrieval_result,
    }