import copy
import unittest
from unittest.mock import patch

from src.agent.langgraph_orchestrator import (
    WORKFLOW_VERSION,
    run_langgraph_guarded_claim_triage,
)


SAMPLE_TOOL_RESULT = {
    "tool_name": "deterministic_triage",
    "tool_version": "rules_baseline_v1",
    "claim_id": "CLM-TEST-001",
    "authority_notice": (
        "The deterministic decision is authoritative for triage routing."
    ),
    "deterministic_decision": {
        "claim_id": "CLM-TEST-001",
        "triage_outcome": "PROCEED",
        "triggering_rule_id": "OUT-001",
        "precedence_stage": 6,
        "decision_reason": (
            "No deterministic rule requiring a different triage route "
            "was triggered."
        ),
        "rule_trace": [],
        "system_limitations": [
            "Claim-history source completeness cannot be independently verified."
        ],
        "decision_support_only": True,
    },
}


SAMPLE_NO_FOLLOW_UP_RESULT = {
    "tool_name": "controlled_follow_up_selection",
    "tool_version": "v1",
    "claim_id": "CLM-TEST-001",
    "authority_notice": (
        "Follow-up selection is deterministic and uses only approved "
        "catalogue questions."
    ),
    "follow_up_selection": {
        "claim_id": "CLM-TEST-001",
        "follow_up_required": False,
        "selection_status": "NOT_REQUIRED",
        "question_ids": [],
        "selected_questions": [],
        "customer_message": "",
        "deferred_requirements": [],
        "selection_notes": [
            "No follow-up is required for PROCEED."
        ],
    },
}


SAMPLE_INFO_REQUIRED_TOOL_RESULT = {
    **SAMPLE_TOOL_RESULT,
    "deterministic_decision": {
        **SAMPLE_TOOL_RESULT["deterministic_decision"],
        "triage_outcome": "INFO_REQUIRED",
        "triggering_rule_id": "ELG-001",
        "precedence_stage": 3,
        "decision_reason": (
            "A valid incident date is required before eligibility can be "
            "assessed."
        ),
    },
}


SAMPLE_INFO_REQUIRED_FOLLOW_UP_RESULT = {
    "tool_name": "controlled_follow_up_selection",
    "tool_version": "v1",
    "claim_id": "CLM-TEST-001",
    "authority_notice": (
        "Follow-up selection is deterministic and uses only approved "
        "catalogue questions."
    ),
    "follow_up_selection": {
        "claim_id": "CLM-TEST-001",
        "follow_up_required": True,
        "selection_status": "QUESTIONS_SELECTED",
        "question_ids": ["FUP-002"],
        "selected_questions": [
            {
                "question_id": "FUP-002",
                "source_rule_id": "ELG-001",
                "response_field": "reported_incident_date",
                "response_format": "DATE_YYYY_MM_DD",
                "customer_facing_question": (
                    "Please confirm the date on which the incident occurred."
                ),
            }
        ],
        "customer_message": (
            "Thanks for submitting your claim. Please confirm the date on "
            "which the incident occurred."
        ),
        "deferred_requirements": [],
        "selection_notes": [
            "Question selected from the approved catalogue."
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
        },
        {
            "rank": 2,
            "chunk_id": "KB-002::S02",
            "document_id": "KB-002",
            "section_title": "Evidence-review principles",
            "relevance_score": 0.74,
        },
    ],
}

class TestLangGraphGuardedClaimTriage(unittest.TestCase):

    def test_template_workflow_is_safe_and_has_five_nodes(self):
        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=SAMPLE_TOOL_RESULT,
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=SAMPLE_NO_FOLLOW_UP_RESULT,
        ) as mock_follow_up:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
            )

        self.assertEqual(WORKFLOW_VERSION, "langgraph_v4")
        self.assertEqual(result["workflow_status"], "COMPLETED")
        self.assertEqual(result["proposal_source"], "TEMPLATE")

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

        self.assertFalse(
            result["final_response"]["controlled_follow_up"][
                "follow_up_required"
            ]
        )
        self.assertEqual(
            result["final_response"]["controlled_follow_up"][
                "question_ids"
            ],
            [],
        )

        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "SAFE",
        )
        self.assertFalse(result["content_safety"]["fallback_used"])

        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )
        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
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

    def test_info_required_carries_controlled_follow_up_output(self):
        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=SAMPLE_INFO_REQUIRED_TOOL_RESULT,
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=SAMPLE_INFO_REQUIRED_FOLLOW_UP_RESULT,
        ) as mock_follow_up:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                questions_already_asked=["FUP-001"],
            )

        controlled_follow_up = result["final_response"][
            "controlled_follow_up"
        ]

        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "INFO_REQUIRED",
        )
        self.assertEqual(
            result["final_response"]["triggering_rule_id"],
            "ELG-001",
        )
        self.assertTrue(controlled_follow_up["follow_up_required"])
        self.assertEqual(
            controlled_follow_up["question_ids"],
            ["FUP-002"],
        )
        self.assertEqual(
            controlled_follow_up["selection_status"],
            "QUESTIONS_SELECTED",
        )
        self.assertEqual(
            result["final_response"]["controlled_follow_up_source"],
            "controlled_follow_up_selection:v1",
        )

        mock_triage.assert_called_once()

        mock_follow_up.assert_called_once_with(
            data={},
            claim_id="CLM-TEST-001",
            deterministic_tool_result=SAMPLE_INFO_REQUIRED_TOOL_RESULT,
            questions_already_asked=["FUP-001"],
        )

    def test_unsafe_content_and_authority_override_are_blocked(self):
        def unsafe_proposal_builder(tool_result):
            return {
                "case_summary": (
                    "The claim is approved for standard processing."
                ),
                "reviewer_note": (
                    "Do not override or reinterpret the outcome."
                ),
                "next_step_message": (
                    "Proceed with standard processing."
                ),
                "triage_outcome": "NOT_ELIGIBLE",
                "triggering_rule_id": "LIM-001",
            }

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=SAMPLE_TOOL_RESULT,
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=SAMPLE_NO_FOLLOW_UP_RESULT,
        ) as mock_follow_up:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                proposal_builder=unsafe_proposal_builder,
            )

        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["content_safety"]["fallback_used"])
        self.assertIn(
            "RESTRICTS_HUMAN_REVIEW",
            result["content_safety"]["content_safety_violations"],
        )

        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "OVERRIDE_BLOCKED",
        )
        self.assertEqual(
            result["final_response"]["triage_outcome"],
            "PROCEED",
        )
        self.assertEqual(
            result["final_response"]["triggering_rule_id"],
            "OUT-001",
        )

        mock_triage.assert_called_once()
        mock_follow_up.assert_called_once()

    def test_none_custom_proposal_uses_safe_fallback(self):
        def empty_proposal_builder(tool_result):
            return None

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=SAMPLE_TOOL_RESULT,
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=SAMPLE_NO_FOLLOW_UP_RESULT,
        ) as mock_follow_up:
            result = run_langgraph_guarded_claim_triage(
                data={},
                claim_id="CLM-TEST-001",
                proposal_builder=empty_proposal_builder,
            )

        self.assertEqual(result["proposal_source"], "CUSTOM")
        self.assertEqual(result["agent_proposal"], {})
        self.assertEqual(
            result["content_safety"]["content_safety_status"],
            "FALLBACK_APPLIED",
        )
        self.assertTrue(result["content_safety"]["fallback_used"])
        self.assertEqual(
            result["final_response"]["authority_guardrail"]["status"],
            "ALIGNED",
        )

        mock_triage.assert_called_once()
        mock_follow_up.assert_called_once()

    def test_invalid_custom_proposal_type_raises_error(self):
        def invalid_proposal_builder(tool_result):
            return ["not", "a", "mapping"]

        with patch(
            "src.agent.langgraph_orchestrator.run_deterministic_triage",
            return_value=copy.deepcopy(SAMPLE_TOOL_RESULT),
        ) as mock_triage, patch(
            "src.agent.langgraph_orchestrator."
            "run_controlled_follow_up_selection",
            return_value=copy.deepcopy(SAMPLE_NO_FOLLOW_UP_RESULT),
        ) as mock_follow_up:
            with self.assertRaisesRegex(
                ValueError,
                "proposal_builder must return a mapping or None.",
            ):
                run_langgraph_guarded_claim_triage(
                    data={},
                    claim_id="CLM-TEST-001",
                    proposal_builder=invalid_proposal_builder,
                )

        mock_triage.assert_called_once()
        mock_follow_up.assert_called_once()

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
        )

if __name__ == "__main__":
    unittest.main()