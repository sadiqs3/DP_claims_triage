import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.rag.evaluation import (
    evaluate_retrieval_method,
    load_retrieval_evaluation_set,
    validate_retrieval_evaluation_set,
)


KNOWN_CHUNK_IDS = {
    "KB-001::S01",
    "KB-001::S02",
    "KB-002::S01",
    "KB-002::S02",
}


def build_evaluation_set() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "query_id": "EVAL-001",
                "query_family": "FAMILY_A",
                "query_text": "first guidance question",
                "relevant_chunk_ids_json": '["KB-001::S01"]',
                "rationale": "First target.",
            },
            {
                "query_id": "EVAL-002",
                "query_family": "FAMILY_A",
                "query_text": "second guidance question",
                "relevant_chunk_ids_json": '["KB-001::S02"]',
                "rationale": "Second target.",
            },
            {
                "query_id": "EVAL-003",
                "query_family": "FAMILY_B",
                "query_text": "third guidance question",
                "relevant_chunk_ids_json": '["KB-002::S01"]',
                "rationale": "Third target.",
            },
        ]
    )


def build_result(chunk_ids: list[str]) -> dict:
    return {
        "retrieval_status": (
            "RESULTS_FOUND"
            if chunk_ids
            else "NO_MATCH"
        ),
        "results": [
            {"rank": rank, "chunk_id": chunk_id}
            for rank, chunk_id in enumerate(
                chunk_ids,
                start=1,
            )
        ],
    }


class TestRagEvaluation(unittest.TestCase):

    def setUp(self):
        self.evaluation_set = build_evaluation_set()

    def test_loads_and_validates_evaluation_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            evaluation_path = (
                Path(temp_dir)
                / "retrieval_eval.csv"
            )

            self.evaluation_set.to_csv(
                evaluation_path,
                index=False,
            )

            loaded_set = load_retrieval_evaluation_set(
                evaluation_path=evaluation_path,
                known_chunk_ids=KNOWN_CHUNK_IDS,
            )

        self.assertEqual(len(loaded_set), 3)
        self.assertIn(
            "relevant_chunk_ids",
            loaded_set.columns,
        )
        self.assertEqual(
            loaded_set.loc[0, "relevant_chunk_ids"],
            ["KB-001::S01"],
        )

    def test_calculates_hit_and_mrr_metrics(self):
        results_by_query = {
            "first guidance question": build_result(
                ["KB-001::S01"]
            ),
            "second guidance question": build_result(
                ["KB-002::S02", "KB-001::S02"]
            ),
            "third guidance question": build_result([]),
        }

        def retrieve_query(query_text, top_k):
            return results_by_query[query_text]

        result = evaluate_retrieval_method(
            evaluation_set=self.evaluation_set,
            known_chunk_ids=KNOWN_CHUNK_IDS,
            method_name="test_method",
            retrieve_query=retrieve_query,
            top_k=3,
        )

        summary = result["summary_metrics"]
        per_query = result["query_results"]

        self.assertEqual(summary["query_count"], 3)
        self.assertAlmostEqual(summary["hit_at_1"], 1 / 3)
        self.assertAlmostEqual(summary["hit_at_3"], 2 / 3)
        self.assertAlmostEqual(summary["mrr_at_3"], 0.5)
        self.assertAlmostEqual(summary["no_result_rate"], 1 / 3)

        self.assertEqual(
            per_query.loc[
                per_query["query_id"].eq("EVAL-002"),
                "first_relevant_rank",
            ].iloc[0],
            2,
        )

    def test_no_results_counts_as_miss(self):
        def retrieve_query(query_text, top_k):
            return build_result([])

        result = evaluate_retrieval_method(
            evaluation_set=self.evaluation_set,
            known_chunk_ids=KNOWN_CHUNK_IDS,
            method_name="empty_method",
            retrieve_query=retrieve_query,
            top_k=3,
        )

        summary = result["summary_metrics"]

        self.assertEqual(summary["hit_at_1"], 0.0)
        self.assertEqual(summary["hit_at_3"], 0.0)
        self.assertEqual(summary["mrr_at_3"], 0.0)
        self.assertEqual(summary["no_result_rate"], 1.0)

    def test_rejects_unknown_relevance_target(self):
        invalid_evaluation_set = self.evaluation_set.copy()

        invalid_evaluation_set.loc[
            0,
            "relevant_chunk_ids_json",
        ] = '["KB-999::S99"]'

        with self.assertRaisesRegex(
            ValueError,
            "references unknown corpus chunk IDs",
        ):
            validate_retrieval_evaluation_set(
                evaluation_set=invalid_evaluation_set,
                known_chunk_ids=KNOWN_CHUNK_IDS,
            )

    def test_rejects_invalid_json_targets(self):
        invalid_evaluation_set = self.evaluation_set.copy()

        invalid_evaluation_set.loc[
            0,
            "relevant_chunk_ids_json",
        ] = "[not valid json]"

        with self.assertRaisesRegex(
            ValueError,
            "invalid relevant_chunk_ids_json",
        ):
            validate_retrieval_evaluation_set(
                evaluation_set=invalid_evaluation_set,
                known_chunk_ids=KNOWN_CHUNK_IDS,
            )

    def test_rejects_result_with_chunk_outside_approved_corpus(self):
        def retrieve_query(query_text, top_k):
            return build_result(["KB-999::S99"])

        with self.assertRaisesRegex(
            ValueError,
            "outside the approved corpus",
        ):
            evaluate_retrieval_method(
                evaluation_set=self.evaluation_set,
                known_chunk_ids=KNOWN_CHUNK_IDS,
                method_name="unsafe_method",
                retrieve_query=retrieve_query,
                top_k=3,
            )

    def test_rejects_duplicate_retrieved_chunk_ids(self):
        def retrieve_query(query_text, top_k):
            return build_result(
                [
                    "KB-001::S01",
                    "KB-001::S01",
                ]
            )

        with self.assertRaisesRegex(
            ValueError,
            "duplicate chunk IDs",
        ):
            evaluate_retrieval_method(
                evaluation_set=self.evaluation_set,
                known_chunk_ids=KNOWN_CHUNK_IDS,
                method_name="duplicate_method",
                retrieve_query=retrieve_query,
                top_k=3,
            )

    def test_rejects_non_mapping_retriever_response(self):
        def retrieve_query(query_text, top_k):
            return ["not", "a", "mapping"]

        with self.assertRaisesRegex(
            ValueError,
            "Retriever callback must return a mapping",
        ):
            evaluate_retrieval_method(
                evaluation_set=self.evaluation_set,
                known_chunk_ids=KNOWN_CHUNK_IDS,
                method_name="invalid_response_method",
                retrieve_query=retrieve_query,
                top_k=3,
            )


if __name__ == "__main__":
    unittest.main()