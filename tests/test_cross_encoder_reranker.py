from __future__ import annotations

from copy import deepcopy
import unittest

from src.rag.cross_encoder_reranker import (
    RERANKER_NAME,
    RERANKER_VERSION,
    rerank_controlled_rag_result,
)


SAMPLE_RAG_TOOL_RESULT = {
    "tool_name": "controlled_rag_retrieval",
    "tool_version": "projection_faiss_v1",
    "claim_id": "CLM-TEST-001",
    "authority": "non_authoritative_guidance",
    "authority_notice": (
        "Controlled RAG retrieval provides analyst-facing guidance only."
    ),
    "projection_source": "authoritative_rag_facts_projection:v1",
    "retrieval_source": (
        "persisted_semantic_sop_retrieval:faiss_embedding_v1"
    ),
    "controlled_query": {
        "query_text": (
            "triage_outcome INFO_REQUIRED claim_category SCREEN_DAMAGE "
            "missing_required_evidence_codes EVD-SCREEN-01"
        ),
        "query_fingerprint": "fp-123",
        "source": "authoritative_deterministic_triage_facts",
        "audience": "analyst",
        "authority": "non_authoritative_guidance",
    },
    "retrieval_status": "RESULTS_FOUND",
    "retrieved_guidance_count": 3,
    "retrieved_guidance": [
        {
            "rank": 1,
            "chunk_id": "KB-001::S01",
            "document_id": "KB-001",
            "section_title": "Document Overview",
            "relevance_score": 0.91,
            "chunk_text": "Generic SOP overview text.",
            "source_reference": {
                "source_relative_path": "data/knowledge_base/KB-001.md"
            },
        },
        {
            "rank": 2,
            "chunk_id": "KB-002::S03",
            "document_id": "KB-002",
            "section_title": "Evidence profiles",
            "relevance_score": 0.82,
            "chunk_text": (
                "Evidence profile text for screen damage and missing "
                "damage photos."
            ),
            "source_reference": {
                "source_relative_path": "data/knowledge_base/KB-002.md"
            },
        },
        {
            "rank": 3,
            "chunk_id": "KB-001::S04",
            "document_id": "KB-001",
            "section_title": "Standard triage flow",
            "relevance_score": 0.77,
            "chunk_text": "Standard triage flow text.",
            "source_reference": {
                "source_relative_path": "data/knowledge_base/KB-001.md"
            },
        },
    ],
    "retrieval_result": {
        "tool_name": "persisted_semantic_sop_retrieval",
        "tool_version": "faiss_embedding_v1",
        "retrieval_status": "RESULTS_FOUND",
        "result_count": 3,
        "results": [],
    },
}


class FakeCrossEncoderScorer:
    """Deterministic fake scorer for unit tests."""

    model_name = "fake-cross-encoder"

    def __init__(self, scores):
        self.scores = scores
        self.pairs = []

    def predict(self, pairs):
        self.pairs = list(pairs)
        return list(self.scores)


class TestCrossEncoderReranker(unittest.TestCase):
    """Tests controlled cross-encoder reranking behavior."""

    def test_reranks_candidates_by_cross_encoder_score(self):
        scorer = FakeCrossEncoderScorer(
            scores=[0.10, 0.95, 0.40],
        )

        result = rerank_controlled_rag_result(
            rag_tool_result=SAMPLE_RAG_TOOL_RESULT,
            scorer=scorer,
            top_n=3,
        )

        self.assertEqual(
            result["reranking"]["reranker_name"],
            RERANKER_NAME,
        )
        self.assertEqual(
            result["reranking"]["reranker_version"],
            RERANKER_VERSION,
        )
        self.assertEqual(
            result["reranking"]["reranker_model_name"],
            "fake-cross-encoder",
        )
        self.assertEqual(
            result["reranking"]["reranking_status"],
            "RERANKED",
        )
        self.assertEqual(result["reranking"]["candidate_count"], 3)
        self.assertEqual(result["reranking"]["reranked_count"], 3)
        self.assertEqual(
            result["reranking"]["controlled_query_fingerprint"],
            "fp-123",
        )

        self.assertEqual(
            result["retrieved_guidance"][0]["chunk_id"],
            "KB-002::S03",
        )
        self.assertEqual(result["retrieved_guidance"][0]["rank"], 1)
        self.assertEqual(
            result["retrieved_guidance"][0]["original_rank"],
            2,
        )
        self.assertEqual(
            result["retrieved_guidance"][0]["rerank_score"],
            0.95,
        )

        self.assertEqual(len(scorer.pairs), 3)
        self.assertEqual(
            scorer.pairs[0][0],
            SAMPLE_RAG_TOOL_RESULT["controlled_query"]["query_text"],
        )

    def test_limits_output_to_top_n(self):
        scorer = FakeCrossEncoderScorer(
            scores=[0.10, 0.95, 0.40],
        )

        result = rerank_controlled_rag_result(
            rag_tool_result=SAMPLE_RAG_TOOL_RESULT,
            scorer=scorer,
            top_n=2,
        )

        self.assertEqual(result["retrieved_guidance_count"], 2)
        self.assertEqual(len(result["retrieved_guidance"]), 2)
        self.assertEqual(
            [
                item["chunk_id"]
                for item in result["retrieved_guidance"]
            ],
            ["KB-002::S03", "KB-001::S04"],
        )
        self.assertEqual(
            result["retrieval_result"]["result_count"],
            2,
        )

    def test_does_not_mutate_input_result(self):
        original = deepcopy(SAMPLE_RAG_TOOL_RESULT)
        scorer = FakeCrossEncoderScorer(
            scores=[0.10, 0.95, 0.40],
        )

        _ = rerank_controlled_rag_result(
            rag_tool_result=original,
            scorer=scorer,
            top_n=2,
        )

        self.assertEqual(original, SAMPLE_RAG_TOOL_RESULT)

    def test_handles_no_candidates_without_inventing_results(self):
        rag_result = deepcopy(SAMPLE_RAG_TOOL_RESULT)
        rag_result["retrieved_guidance"] = []
        rag_result["retrieved_guidance_count"] = 0

        scorer = FakeCrossEncoderScorer(scores=[])

        result = rerank_controlled_rag_result(
            rag_tool_result=rag_result,
            scorer=scorer,
        )

        self.assertEqual(result["retrieved_guidance"], [])
        self.assertEqual(result["retrieved_guidance_count"], 0)
        self.assertEqual(
            result["reranking"]["reranking_status"],
            "NO_CANDIDATES",
        )
        self.assertEqual(result["reranking"]["candidate_count"], 0)
        self.assertEqual(result["reranking"]["reranked_count"], 0)

    def test_rejects_authoritative_decision_input(self):
        rag_result = deepcopy(SAMPLE_RAG_TOOL_RESULT)
        rag_result["authority"] = "authoritative_decision"

        scorer = FakeCrossEncoderScorer(
            scores=[0.10, 0.95, 0.40],
        )

        with self.assertRaisesRegex(
            ValueError,
            "non-authoritative guidance",
        ):
            rerank_controlled_rag_result(
                rag_tool_result=rag_result,
                scorer=scorer,
            )

    def test_rejects_score_count_mismatch(self):
        scorer = FakeCrossEncoderScorer(scores=[0.10])

        with self.assertRaisesRegex(
            ValueError,
            "different number of scores",
        ):
            rerank_controlled_rag_result(
                rag_tool_result=SAMPLE_RAG_TOOL_RESULT,
                scorer=scorer,
            )


if __name__ == "__main__":
    unittest.main()