import copy
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.agent.openai_explainer import (
    StructuredExplanation,
    _build_explanation_input,
    build_openai_explanation_proposal,
)


SAMPLE_TOOL_RESULT = {
    "tool_name": "deterministic_triage",
    "tool_version": "rules_baseline_v1",
    "deterministic_decision": {
        "claim_id": "CLM-TEST-001",
        "triage_outcome": "NOT_ELIGIBLE",
        "triggering_rule_id": "LIM-001",
        "precedence_stage": 2,
        "decision_reason": "The annual claim allowance is exhausted.",
        "rule_trace": [],
        "system_limitations": [
            (
                "DEV-003 is not evaluated because the runtime context does "
                "not provide a verified NOT_ENROLLED device decision."
            ),
            (
                "EXC-001 and EXC-002 are not evaluated because no structured "
                "exclusion-status dataset is available."
            ),
            (
                "Claim-history source completeness cannot be independently "
                "verified from the current runtime package."
            ),
        ],
        "decision_support_only": True,
    },
}


class FakeResponses:
    def __init__(self, parsed_output):
        self.parsed_output = parsed_output
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed_output)


class FakeOpenAIClient:
    def __init__(self, parsed_output):
        self.responses = FakeResponses(parsed_output)


class TestOpenAIExplainer(unittest.TestCase):

    def test_builds_minimized_input_with_compact_limitations(self):
        explanation_input = _build_explanation_input(
            SAMPLE_TOOL_RESULT
        )

        self.assertIn(
            "system_limitations_summary",
            explanation_input,
        )
        self.assertNotIn(
            "system_limitations",
            explanation_input,
        )

        self.assertEqual(
            explanation_input["system_limitations_summary"],
            [
                (
                    "DEV-003: verified NOT_ENROLLED device status is "
                    "unavailable."
                ),
                (
                    "EXC-001/EXC-002: structured exclusion status is "
                    "unavailable."
                ),
                (
                    "Claim history: source completeness cannot be "
                    "independently verified."
                ),
            ],
        )

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
            "OPENAI_EXPLANATION_MODEL": "test-model",
        },
        clear=False,
    )
    def test_returns_only_permitted_structured_fields(self):
        parsed_output = StructuredExplanation(
            case_summary=(
                "System triage recommendation: NOT_ELIGIBLE under LIM-001."
            ),
            reviewer_note=(
                "This is decision support only. An authorised reviewer may "
                "apply approved review or escalation procedures."
            ),
            next_step_message=(
                "Follow the approved analyst review process."
            ),
        )

        fake_client = FakeOpenAIClient(parsed_output)

        result = build_openai_explanation_proposal(
            tool_result=SAMPLE_TOOL_RESULT,
            model="test-model",
            client=fake_client,
        )

        self.assertEqual(
            set(result),
            {
                "case_summary",
                "reviewer_note",
                "next_step_message",
            },
        )

        self.assertEqual(
            result["case_summary"],
            parsed_output.case_summary,
        )

        parse_call = fake_client.responses.calls[0]

        self.assertEqual(parse_call["model"], "test-model")
        self.assertIs(
            parse_call["text_format"],
            StructuredExplanation,
        )

        input_payload = json.loads(parse_call["input"])

        self.assertIn(
            "system_limitations_summary",
            input_payload,
        )
        self.assertNotIn(
            "system_limitations",
            input_payload,
        )

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key"},
        clear=False,
    )
    def test_missing_required_decision_field_raises_error(self):
        invalid_tool_result = copy.deepcopy(SAMPLE_TOOL_RESULT)

        del invalid_tool_result["deterministic_decision"][
            "triage_outcome"
        ]

        fake_client = FakeOpenAIClient(
            StructuredExplanation(
                case_summary="Placeholder.",
                reviewer_note="Placeholder.",
                next_step_message="Placeholder.",
            )
        )

        with self.assertRaisesRegex(
            ValueError,
            "deterministic_decision is missing required fields",
        ):
            build_openai_explanation_proposal(
                tool_result=invalid_tool_result,
                client=fake_client,
            )

    @patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "test-key"},
        clear=False,
    )
    def test_missing_structured_output_raises_error(self):
        fake_client = FakeOpenAIClient(parsed_output=None)

        with self.assertRaisesRegex(
            ValueError,
            "OpenAI returned no structured explanation output",
        ):
            build_openai_explanation_proposal(
                tool_result=SAMPLE_TOOL_RESULT,
                client=fake_client,
            )


if __name__ == "__main__":
    unittest.main()