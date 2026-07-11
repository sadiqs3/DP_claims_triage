from __future__ import annotations

import os
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from src.evaluation.generation_judge import (
    DEFAULT_JUDGE_MODEL,
    JUDGE_PROMPT_VERSION,
    GenerationJudgeResult,
    build_generation_judge_input,
    build_generation_judge_instructions,
    run_generation_judge,
)


def build_valid_case() -> dict[str, object]:
    """Return a complete frozen-case record for judge testing."""
    return {
        "evaluation_case_id": "GEN-001",
        "claim_id": "CLM-000001",
        "deterministic_outcome": "PROCEED",
        "triggering_rule_id": "OUT-001",
        "deterministic_reason": (
            "All applicable deterministic checks passed."
        ),
        "decision_support_only": True,
        "precedence_stage": 6,
        "system_limitations": (
            '["Decision support only.", '
            '"Authorised reviewers retain responsibility."]'
        ),
        "rule_trace": (
            '[{"rule_id": "OUT-001", '
            '"status": "TRIGGERED"}]'
        ),
        "projected_triage_outcome": "PROCEED",
        "projected_triggering_rule_id": "OUT-001",
        "projected_precedence_stage": 6,
        "claim_category": "SCREEN_DAMAGE",
        "requested_service_type": "REPAIR",
        "plan_configuration_status": (
            "ACTIVE_CONFIGURATION_AVAILABLE"
        ),
        "product_scope_status": "IN_SCOPE",
        "coverage_lookup_status": "UNIQUE_COVERAGE_RECORD",
        "covered_flag": True,
        "evidence_profile_id": "EVD-SCREEN-01",
        "evidence_assessment_status": "SUFFICIENT",
        "missing_required_evidence_codes": "[]",
        "unreadable_required_evidence_codes": "[]",
        "device_match_status": "DEVICE_MATCH",
        "risk_indicator_ids": "[]",
        "manual_review_reason_codes": "[]",
        "follow_up_required": False,
        "follow_up_selection_status": "NOT_REQUIRED",
        "follow_up_question_ids": "[]",
        "controlled_query_text": (
            "SCREEN_DAMAGE evidence handling and analyst next steps"
        ),
        "retrieved_chunk_ids": '["KB-002::S03"]',
        "retrieved_document_ids": '["KB-002"]',
        "retrieved_context": (
            "[KB-002 / KB-002::S03] "
            "Screen-damage claims require a damage photo."
        ),
        "analyst_guidance_summary": (
            "Evidence handling guidance for screen damage."
        ),
        "analyst_guidance_usage_boundary": (
            "Guidance is non-authoritative and must not override "
            "deterministic policy facts."
        ),
        "analyst_guidance_text": (
            "Review the damage photo and follow the documented "
            "evidence-handling steps."
        ),
        "generated_explanation": (
            "The claim can proceed for standard processing. "
            "This is not approval or a payout decision."
        ),
        "final_explanation": (
            "The claim can proceed for standard processing. "
            "Authorised reviewers retain responsibility."
        ),
        "content_safety_status": "SAFE",
        "authority_guardrail_status": "ALIGNED",
    }


class TestGenerationJudgeModels(unittest.TestCase):
    """Tests for structured judge result validation."""

    def test_valid_result_model_accepts_scores(self):
        result = GenerationJudgeResult(
            context_relevance=4,
            groundedness=4,
            answer_relevance=3,
            hallucination_control=4,
            critical_safety_failure=False,
            evaluation_notes={
                "context_relevance": "Relevant context.",
                "groundedness": "Statements are supported.",
                "answer_relevance": "Useful next step.",
                "hallucination_control": "No unsupported claim.",
                "critical_safety_failure": "No critical failure.",
            },
        )

        self.assertEqual(result.context_relevance, 4)
        self.assertFalse(result.critical_safety_failure)

    def test_result_model_rejects_score_above_four(self):
        with self.assertRaises(ValidationError):
            GenerationJudgeResult(
                context_relevance=5,
                groundedness=4,
                answer_relevance=4,
                hallucination_control=4,
                critical_safety_failure=False,
                evaluation_notes={
                    "context_relevance": "Invalid score.",
                    "groundedness": "Supported.",
                    "answer_relevance": "Relevant.",
                    "hallucination_control": "Controlled.",
                    "critical_safety_failure": "No failure.",
                },
            )

    def test_result_model_rejects_empty_note(self):
        with self.assertRaises(ValidationError):
            GenerationJudgeResult(
                context_relevance=4,
                groundedness=4,
                answer_relevance=4,
                hallucination_control=4,
                critical_safety_failure=False,
                evaluation_notes={
                    "context_relevance": "",
                    "groundedness": "Supported.",
                    "answer_relevance": "Relevant.",
                    "hallucination_control": "Controlled.",
                    "critical_safety_failure": "No failure.",
                },
            )


class TestGenerationJudgeInput(unittest.TestCase):
    """Tests for bounded judge-input construction."""

    def test_build_input_keeps_required_evidence(self):
        judge_input = build_generation_judge_input(
            build_valid_case()
        )

        self.assertEqual(
            judge_input["evaluation_case_id"],
            "GEN-001",
        )
        self.assertEqual(
            judge_input[
                "authoritative_deterministic_decision"
            ]["triage_outcome"],
            "PROCEED",
        )
        self.assertIn(
            "retrieved_context",
            judge_input["retrieval_evidence"],
        )
        self.assertIn(
            "guidance_text",
            judge_input["analyst_only_rag_guidance"],
        )

    def test_build_input_excludes_human_scores(self):
        case = build_valid_case()
        case["context_relevance_human"] = 3
        case["human_notes"] = "Human baseline."

        judge_input = build_generation_judge_input(case)
        serialized = str(judge_input)

        self.assertNotIn(
            "context_relevance_human",
            serialized,
        )
        self.assertNotIn(
            "Human baseline",
            serialized,
        )

    def test_build_input_rejects_missing_required_field(self):
        case = build_valid_case()
        del case["retrieved_context"]

        with self.assertRaisesRegex(
            ValueError,
            "retrieved_context",
        ):
            build_generation_judge_input(case)

    def test_build_input_rejects_empty_required_field(self):
        case = build_valid_case()
        case["final_explanation"] = "   "

        with self.assertRaisesRegex(
            ValueError,
            "final_explanation",
        ):
            build_generation_judge_input(case)

    def test_prompt_preserves_deterministic_authority(self):
        instructions = build_generation_judge_instructions()

        self.assertIn(
            "authoritative",
            instructions.lower(),
        )
        self.assertIn(
            "must not reconsider",
            instructions.lower(),
        )
        self.assertIn(
            "critical safety failure",
            instructions.lower(),
        )
    def test_build_input_includes_complete_authoritative_evidence(self):
        judge_input = build_generation_judge_input(
            build_valid_case()
        )

        authoritative_decision = judge_input[
            "authoritative_deterministic_decision"
        ]

        self.assertEqual(
            authoritative_decision["precedence_stage"],
            "6",
        )
        self.assertIn(
            "Decision support only",
            authoritative_decision["system_limitations"],
        )
        self.assertIn(
            "OUT-001",
            authoritative_decision["rule_trace"],
        )

    def test_v2_prompt_prioritises_triggering_reason(self):
        instructions = build_generation_judge_instructions()

        self.assertIn(
            "primary routing reason",
            instructions.lower(),
        )
        self.assertIn(
            "missing device identifier",
            instructions.lower(),
        )
        self.assertIn(
            "annual-limit exhaustion",
            instructions.lower(),
        )
        self.assertIn(
            "rule trace",
            instructions.lower(),
        )


class TestGenerationJudgeExecution(unittest.TestCase):
    """Tests for OpenAI structured judge execution."""

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key"},
        clear=False,
    )
    def test_run_judge_returns_structured_result(self):
        parsed_result = GenerationJudgeResult(
            context_relevance=3,
            groundedness=4,
            answer_relevance=4,
            hallucination_control=4,
            critical_safety_failure=False,
            evaluation_notes={
                "context_relevance": "Mostly relevant.",
                "groundedness": "Fully supported.",
                "answer_relevance": "Clear and useful.",
                "hallucination_control": "No unsupported claim.",
                "critical_safety_failure": "No critical failure.",
            },
        )

        mock_response = Mock()
        mock_response.output_parsed = parsed_result

        mock_client = Mock()
        mock_client.responses.parse.return_value = mock_response

        result = run_generation_judge(
            build_valid_case(),
            client=mock_client,
        )

        self.assertEqual(result["context_relevance"], 3)
        self.assertEqual(result["groundedness"], 4)
        self.assertEqual(
            result["judge_model"],
            DEFAULT_JUDGE_MODEL,
        )
        self.assertEqual(
            result["judge_prompt_version"],
            JUDGE_PROMPT_VERSION,
        )

        mock_client.responses.parse.assert_called_once()

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key"},
        clear=False,
    )
    def test_run_judge_rejects_missing_parsed_output(self):
        mock_response = Mock()
        mock_response.output_parsed = None

        mock_client = Mock()
        mock_client.responses.parse.return_value = mock_response

        with self.assertRaisesRegex(
            ValueError,
            "no structured generation-judge output",
        ):
            run_generation_judge(
                build_valid_case(),
                client=mock_client,
            )

    @patch.dict(
        os.environ,
        {},
        clear=True,
    )
    def test_run_judge_requires_api_key(self):
        with self.assertRaisesRegex(
            EnvironmentError,
            "OPENAI_API_KEY",
        ):
            run_generation_judge(
                build_valid_case(),
                client=Mock(),
            )


if __name__ == "__main__":
    unittest.main()