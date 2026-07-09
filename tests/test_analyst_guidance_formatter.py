from __future__ import annotations

import unittest

from src.rag.analyst_guidance_formatter import (
    FORMATTER_NAME,
    FORMATTER_VERSION,
    format_analyst_guidance,
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
            "This query contains CLM-TEST-001 and should not be copied."
        ),
        "query_fingerprint": "abc123",
        "source": "authoritative_deterministic_triage_facts",
        "audience": "analyst",
        "authority": "non_authoritative_guidance",
    },
    "projected_facts": {
        "claim_id": "CLM-TEST-001",
        "customer_statement": "This should not be copied.",
    },
    "retrieval_status": "RESULTS_FOUND",
    "retrieved_guidance_count": 2,
    "retrieved_guidance": [
        {
            "rank": 1,
            "chunk_id": "KB-002::S03",
            "document_id": "KB-002",
            "section_title": "Evidence profiles",
            "relevance_score": 0.81234567,
            "chunk_text": (
                "Screen damage claims require the applicable evidence "
                "profile. Missing evidence should be requested through "
                "the approved case-management workflow."
            ),
            "source_reference": {
                "source_relative_path": (
                    "data/knowledge_base/"
                    "KB-002_evidence_review_guide_v1.md"
                ),
            },
        },
        {
            "rank": 2,
            "chunk_id": "KB-002::S02",
            "document_id": "KB-002",
            "section_title": "Evidence-review principles",
            "relevance_score": 0.742,
            "chunk_text": (
                "Evidence validates a potentially eligible claim; it does "
                "not create coverage or override deterministic triage."
            ),
            "source_reference": {
                "source_relative_path": (
                    "data/knowledge_base/"
                    "KB-002_evidence_review_guide_v1.md"
                ),
            },
        },
    ],
}


class TestAnalystGuidanceFormatter(unittest.TestCase):
    """Tests deterministic formatting of analyst-only RAG guidance."""

    def test_formats_retrieved_sources_with_reference_ids(self):
        result = format_analyst_guidance(SAMPLE_RAG_TOOL_RESULT)

        self.assertEqual(result["formatter_name"], FORMATTER_NAME)
        self.assertEqual(result["formatter_version"], FORMATTER_VERSION)
        self.assertEqual(
            result["authority"],
            "non_authoritative_guidance",
        )
        self.assertEqual(result["retrieved_guidance_count"], 2)
        self.assertEqual(
            result["controlled_query_fingerprint"],
            "abc123",
        )

        self.assertEqual(
            result["source_references"][0]["reference_id"],
            "S1",
        )
        self.assertEqual(
            result["source_references"][0]["chunk_id"],
            "KB-002::S03",
        )
        self.assertEqual(
            result["source_references"][0]["relevance_score"],
            0.812346,
        )
        self.assertEqual(
            result["guidance_items"][0]["source_label"],
            "S1: KB-002 / Evidence profiles",
        )

    def test_does_not_copy_query_text_projected_facts_or_identifiers(self):
        result = format_analyst_guidance(SAMPLE_RAG_TOOL_RESULT)

        formatted_text = str(result)

        self.assertNotIn("This query contains", formatted_text)
        self.assertNotIn("CLM-TEST-001", formatted_text)
        self.assertNotIn("This should not be copied", formatted_text)
        self.assertNotIn("projected_facts", formatted_text)

    def test_handles_no_retrieved_guidance_without_inventing_content(self):
        rag_result = dict(SAMPLE_RAG_TOOL_RESULT)
        rag_result["retrieval_status"] = "NO_RESULTS"
        rag_result["retrieved_guidance"] = []

        result = format_analyst_guidance(rag_result)

        self.assertEqual(result["retrieved_guidance_count"], 0)
        self.assertEqual(result["source_references"], [])
        self.assertEqual(result["guidance_items"], [])
        self.assertIn(
            "Do not invent guidance",
            result["guidance_summary"],
        )

    def test_rejects_non_rag_authority(self):
        rag_result = dict(SAMPLE_RAG_TOOL_RESULT)
        rag_result["authority"] = "authoritative_decision"

        with self.assertRaisesRegex(
            ValueError,
            "non-authoritative guidance",
        ):
            format_analyst_guidance(rag_result)

    def test_truncates_long_guidance_preview(self):
        rag_result = dict(SAMPLE_RAG_TOOL_RESULT)
        rag_result["retrieved_guidance"] = [
            dict(SAMPLE_RAG_TOOL_RESULT["retrieved_guidance"][0])
        ]
        rag_result["retrieved_guidance"][0]["chunk_text"] = "A" * 300

        result = format_analyst_guidance(
            rag_result,
            max_preview_chars=120,
        )

        preview = result["guidance_items"][0]["guidance_preview"]

        self.assertEqual(len(preview), 120)
        self.assertTrue(preview.endswith("..."))

    def test_rejects_preview_limit_below_minimum(self):
        with self.assertRaisesRegex(
            ValueError,
            "at least 80",
        ):
            format_analyst_guidance(
                SAMPLE_RAG_TOOL_RESULT,
                max_preview_chars=40,
            )


if __name__ == "__main__":
    unittest.main()