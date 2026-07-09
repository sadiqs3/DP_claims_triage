from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from src.agent.langgraph_orchestrator import (
    WORKFLOW_NAME,
    WORKFLOW_VERSION,
    run_langgraph_guarded_claim_triage,
)


SAMPLE_TOOL_RESULT = {
    "tool_name": "deterministic_triage",
    "tool_version": "rules_baseline_v1",
    "authority": "authoritative_deterministic_triage",
    "authority_notice": (
        "Deterministic triage is authoritative for routing. "
        "Agent-generated content is decision-support only."
    ),
    "deterministic_decision": {
        "claim_id": "CLM-TEST-001",
        "triage_outcome": "PROCEED",
        "triggering_rule_id": "OUT-001",
        "precedence_stage": "OUTCOME_ROUTING",
        "decision_reason": (
            "The claim passed policy, device, coverage, evidence, "
            "and risk checks."
        ),
        "rule_trace": [
            {
                "rule_id": "OUT-001",
                "precedence_stage": "OUTCOME_ROUTING",
                "evaluation": "TRIGGERED",
                "observed_value": "Standard processing criteria met.",
            }
        ],
        "system_limitations": [
            "This is a decision-support recommendation only."
        ],
        "decision_support_only": True,
    },
}


SAMPLE_NO_FOLLOW_UP_RESULT = {
    "tool_name": "controlled_follow_up_selection",
    "tool_version": "controlled_follow_up_v1",
    "claim_id": "CLM-TEST-001",
    "authority": "controlled_follow_up_catalogue",
    "authority_notice": (
        "Follow-up wording is selected only from the approved catalogue."
    ),
    "follow_up_selection": {
        "follow_up_required": False,
        "selection_status": "NOT_REQUIRED",
        "question_ids": [],
        "questions": [],
    },
}


SAMPLE_FOLLOW_UP_REQUIRED_RESULT = {
    "tool_name": "controlled_follow_up_selection",
    "tool_version": "controlled_follow_up_v1",
    "claim_id": "CLM-TEST-001",
    "authority": "controlled_follow_up_catalogue",
    "authority_notice": (
        "Follow-up wording is selected only from the approved catalogue."
    ),
    "follow_up_selection": {
        "follow_up_required": True,
        "selection_status": "SELECTED",
        "question_ids": ["FU-EVD-001"],
        "questions": [
            {
                "question_id": "FU-EVD-001",
                "question_text": (
                    "Please upload a clear photo of the damaged screen."
                ),
                "evidence_code": "EVD-SCREEN-01",
            }
        ],
    },
}


SAMPLE_RAG_TOOL_RESULT = {
    "tool_name": "controlled_rag_retrieval",
    "tool_version": "projection_faiss_v1",
    "claim_id": "CLM-TEST-001",
    "decision_source": "deterministic_triage:rules_baseline_v1",
    "projection_source": "authoritative_rag_facts_projection:v1",
    "retrieval_source": (
        "persisted_semantic_sop_retrieval:faiss_embedding_v1"
    ),
    "authority": "non_authoritative_guidance",
    "authority_notice": (
        "Controlled RAG retrieval provides analyst-facing guidance only."
    ),
    "controlled_query": {
        "query_text": "controlled retrieval query",
        "query_fingerprint": "abc123",
        "source": "authoritative_deterministic_triage_facts",
        "audience": "analyst",
        "authority": "non_authoritative_guidance",
    },
    "retrieval_status": "RESULTS_FOUND",
    "retrieved_guidance_count": 2,
    "retrieved_guidance": [
        {
            "rank": 1,
            "chunk_id": "KB-002::S03",
            "document_id": "KB-002",
            "section_title": "Evidence profiles",
            "relevance_score": 0.81,
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
            "relevance_score": 0.74,
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


class TestLangGraphGuardedClaimTriage(unittest.TestCase):
    """Tests the protected LangGraph claim-triage workflow."""

    def test_workflow_metadata(self):
        self.assertEqual(
            WORKFLOW_NAME,
            "langgraph_guarded_claim_triage",
        )
        self.assertEqual(WORKFLOW_VERSION, "langgraph_v6")

    def test_runs_default_guarded_workflow_without_rag(self):
        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_NO_FOLLOW_UP_RESULT),
        ) as mock_follow_up:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
            )

        self.assertEqual(result["workflow_name"], WORKFLOW_NAME)
        self.assertEqual(result["workflow_version"], WORKFLOW_VERSION)
        self.assertEqual(result["workflow_status"], "COMPLETED")

        self.assertEqual(
            [item["node"] for item in result["workflow_trace"]],
            [
                "deterministic_triage",
                "controlled_follow_up_selection",
                "explanation_proposal",
                "agent_content_safety_guardrail",
                "response_guardrail",
            ],
        )

        self.assertEqual(result["rag_tool_result"], {})
        self.assertEqual(result["analyst_guidance"], {})

        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
        )
        self.assertEqual(
            result["final_response"]["triggering_rule_id"],
            "OUT-001",
        )
        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )

        mock_triage.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
        )
        mock_follow_up.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
            deterministic_tool_result=SAMPLE_TOOL_RESULT,
            questions_already_asked=None,
        )

    def test_custom_proposal_builder_is_used(self):
        def custom_builder(tool_result):
            return {
                "case_summary": (
                    "Custom analyst summary based on deterministic triage."
                ),
                "reviewer_note": (
                    "Decision support only; human review remains available."
                ),
                "next_step_message": (
                    "Continue with the controlled operational workflow."
                ),
            }

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ), patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_NO_FOLLOW_UP_RESULT),
        ):
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                proposal_builder=custom_builder,
            )

        self.assertEqual(result["proposal_source"], "CUSTOM")
        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )

    def test_unsafe_custom_proposal_uses_safety_fallback(self):
        def unsafe_builder(tool_result):
            return {
                "case_summary": (
                    "This claim is finally approved with no restrictions."
                ),
                "reviewer_note": (
                    "No human review is required for this decision."
                ),
                "next_step_message": (
                    "Tell the customer the claim outcome is final."
                ),
            }

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ), patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_NO_FOLLOW_UP_RESULT),
        ):
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                proposal_builder=unsafe_builder,
            )

        self.assertEqual(result["proposal_source"], "CUSTOM")
        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["content_safety"]["fallback_used"])
        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
        )
        self.assertEqual(
            result["final_response"]["triggering_rule_id"],
            "OUT-001",
        )

    def test_controlled_follow_up_is_attached_to_final_response(self):
        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ), patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_FOLLOW_UP_REQUIRED_RESULT),
        ):
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                questions_already_asked=[],
            )

        controlled_follow_up = result["final_response"][
            "controlled_follow_up"
        ]

        self.assertTrue(controlled_follow_up["follow_up_required"])
        self.assertEqual(
            controlled_follow_up["selection_status"],
            "SELECTED",
        )
        self.assertEqual(
            controlled_follow_up["question_ids"],
            ["FU-EVD-001"],
        )
        self.assertEqual(
            result["final_response"]["controlled_follow_up_source"],
            "controlled_follow_up_selection:controlled_follow_up_v1",
        )

    def test_controlled_rag_branch_is_read_only_when_enabled(self):
        rag_client = object()

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_NO_FOLLOW_UP_RESULT),
        ) as mock_follow_up, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_rag_retrieval",
            return_value=copy.deepcopy(SAMPLE_RAG_TOOL_RESULT),
        ) as mock_rag:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                enable_controlled_rag=True,
                rag_artifact_dir="/tmp/fake-faiss-artifact",
                rag_retrieval_client=rag_client,
                rag_top_k=2,
                rag_min_relevance_score=0.0,
            )

        self.assertEqual(
            [item["node"] for item in result["workflow_trace"]],
            [
                "deterministic_triage",
                "controlled_follow_up_selection",
                "controlled_rag_retrieval",
                "explanation_proposal",
                "agent_content_safety_guardrail",
                "response_guardrail",
            ],
        )

        self.assertEqual(
            result["analyst_guidance"]["formatter_name"],
            "analyst_guidance_formatter",
        )
        self.assertEqual(
            result["analyst_guidance"]["formatter_version"],
            "v1",
        )
        self.assertEqual(
            result["analyst_guidance"]["authority"],
            "non_authoritative_guidance",
        )
        self.assertEqual(
            result["analyst_guidance"]["retrieval_status"],
            "RESULTS_FOUND",
        )
        self.assertEqual(
            result["analyst_guidance"]["retrieved_guidance_count"],
            2,
        )
        self.assertEqual(
            result["analyst_guidance"]["controlled_query_fingerprint"],
            "abc123",
        )
        self.assertEqual(
            result["analyst_guidance"]["source_references"][0][
                "reference_id"
            ],
            "S1",
        )
        self.assertEqual(
            result["analyst_guidance"]["source_references"][0][
                "chunk_id"
            ],
            "KB-002::S03",
        )
        self.assertEqual(
            result["analyst_guidance"]["guidance_items"][0][
                "source_label"
            ],
            "S1: KB-002 / Evidence profiles",
        )

        self.assertEqual(
            result["rag_tool_result"]["tool_name"],
            "controlled_rag_retrieval",
        )

        self.assertNotIn("analyst_guidance", result["final_response"])
        self.assertNotIn("retrieved_guidance", result["final_response"])

        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
        )
        self.assertEqual(
            result["final_response"]["triggering_rule_id"],
            "OUT-001",
        )
        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )

        mock_triage.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
        )
        mock_follow_up.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
            deterministic_tool_result=SAMPLE_TOOL_RESULT,
            questions_already_asked=None,
        )
        mock_rag.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
            deterministic_tool_result=SAMPLE_TOOL_RESULT,
            artifact_dir="/tmp/fake-faiss-artifact",
            top_k=2,
            min_relevance_score=0.0,
            client=rag_client,
            reranker_scorer=None,
            rerank_top_n=None,
            reranker_model_name=None,
        )

    def test_controlled_rag_branch_passes_reranking_options_when_enabled(self):
        rag_client = object()
        fake_reranker = object()

        reranked_rag_result = copy.deepcopy(SAMPLE_RAG_TOOL_RESULT)
        reranked_rag_result["reranking"] = {
            "reranker_name": "cross_encoder_reranker",
            "reranker_version": "v1",
            "reranker_model_name": "fake-cross-encoder",
            "reranking_status": "RERANKED",
            "candidate_count": 2,
            "reranked_count": 2,
            "controlled_query_fingerprint": "abc123",
        }

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ), patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_NO_FOLLOW_UP_RESULT),
        ), patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_rag_retrieval",
            return_value=reranked_rag_result,
        ) as mock_rag:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                enable_controlled_rag=True,
                rag_artifact_dir="/tmp/fake-faiss-artifact",
                rag_retrieval_client=rag_client,
                rag_top_k=3,
                rag_min_relevance_score=0.0,
                enable_reranking=True,
                rag_reranker_scorer=fake_reranker,
                rag_rerank_top_n=2,
                rag_reranker_model_name="fake-cross-encoder",
            )

        rag_trace = [
            item
            for item in result["workflow_trace"]
            if item["node"] == "controlled_rag_retrieval"
        ][0]

        self.assertEqual(rag_trace["reranking_status"], "RERANKED")
        self.assertEqual(
            rag_trace["reranker_model_name"],
            "fake-cross-encoder",
        )

        self.assertEqual(
            result["rag_tool_result"]["reranking"]["reranking_status"],
            "RERANKED",
        )

        self.assertEqual(
            result["analyst_guidance"]["formatter_name"],
            "analyst_guidance_formatter",
        )
        self.assertEqual(
            result["analyst_guidance"]["authority"],
            "non_authoritative_guidance",
        )

        self.assertNotIn("analyst_guidance", result["final_response"])
        self.assertNotIn("retrieved_guidance", result["final_response"])

        mock_rag.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
            deterministic_tool_result=SAMPLE_TOOL_RESULT,
            artifact_dir="/tmp/fake-faiss-artifact",
            top_k=3,
            min_relevance_score=0.0,
            client=rag_client,
            reranker_scorer=fake_reranker,
            rerank_top_n=2,
            reranker_model_name="fake-cross-encoder",
        )


if __name__ == "__main__":
    unittest.main()