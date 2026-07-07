from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from src.rag.lexical_retriever import _validate_top_k


REQUIRED_EVALUATION_COLUMNS = {
    "query_id",
    "query_family",
    "query_text",
    "relevant_chunk_ids_json",
    "rationale",
}


def _normalise_text(value: object) -> str:
    """Return stripped text, treating missing values as empty strings."""
    if value is None or pd.isna(value):
        return ""

    return str(value).strip()


def _parse_relevant_chunk_ids(
    value: object,
    query_id: str,
) -> list[str]:
    """Parse and validate a query's JSON relevance targets."""
    raw_value = _normalise_text(value)

    if not raw_value:
        raise ValueError(
            f"{query_id} has an empty relevant_chunk_ids_json value."
        )

    try:
        parsed_value = json.loads(raw_value)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{query_id} has invalid relevant_chunk_ids_json."
        ) from error

    if not isinstance(parsed_value, list) or not parsed_value:
        raise ValueError(
            f"{query_id} must define a non-empty list of relevant chunk IDs."
        )

    relevant_chunk_ids: list[str] = []

    for chunk_id in parsed_value:
        normalised_chunk_id = _normalise_text(chunk_id)

        if not normalised_chunk_id:
            raise ValueError(
                f"{query_id} contains an empty relevant chunk ID."
            )

        relevant_chunk_ids.append(normalised_chunk_id)

    if len(relevant_chunk_ids) != len(set(relevant_chunk_ids)):
        raise ValueError(
            f"{query_id} contains duplicate relevant chunk IDs."
        )

    return relevant_chunk_ids


def validate_retrieval_evaluation_set(
    evaluation_set: pd.DataFrame,
    known_chunk_ids: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Validate a frozen retrieval-evaluation set.

    The returned DataFrame adds a parsed `relevant_chunk_ids` column for
    evaluation only. This helper does not load or alter runtime RAG data.
    """
    if not isinstance(evaluation_set, pd.DataFrame):
        raise ValueError(
            "Retrieval evaluation set must be a pandas DataFrame."
        )

    missing_columns = REQUIRED_EVALUATION_COLUMNS.difference(
        evaluation_set.columns
    )

    if missing_columns:
        raise ValueError(
            "Retrieval evaluation set is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if evaluation_set.empty:
        raise ValueError(
            "Retrieval evaluation set must not be empty."
        )

    validated_set = evaluation_set.copy()

    required_text_columns = [
        "query_id",
        "query_family",
        "query_text",
        "rationale",
    ]

    for column_name in required_text_columns:
        if (
            validated_set[column_name]
            .map(_normalise_text)
            .eq("")
            .any()
        ):
            raise ValueError(
                "Retrieval evaluation set contains an empty "
                f"{column_name} value."
            )

        validated_set[column_name] = validated_set[
            column_name
        ].map(_normalise_text)

    if validated_set["query_id"].duplicated().any():
        raise ValueError(
            "Retrieval evaluation set contains duplicate query_id values."
        )

    parsed_relevance_targets = []

    for row in validated_set.itertuples(index=False):
        parsed_relevance_targets.append(
            _parse_relevant_chunk_ids(
                value=row.relevant_chunk_ids_json,
                query_id=row.query_id,
            )
        )

    validated_set["relevant_chunk_ids"] = parsed_relevance_targets

    if known_chunk_ids is not None:
        known_chunk_id_set = {
            _normalise_text(chunk_id)
            for chunk_id in known_chunk_ids
            if _normalise_text(chunk_id)
        }

        if not known_chunk_id_set:
            raise ValueError(
                "known_chunk_ids must contain at least one chunk ID."
            )

        for row in validated_set.itertuples(index=False):
            unknown_chunk_ids = set(row.relevant_chunk_ids).difference(
                known_chunk_id_set
            )

            if unknown_chunk_ids:
                raise ValueError(
                    f"{row.query_id} references unknown corpus chunk IDs: "
                    + ", ".join(sorted(unknown_chunk_ids))
                )

    return validated_set


def load_retrieval_evaluation_set(
    evaluation_path: str | Path,
    known_chunk_ids: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Load and validate a retrieval evaluation CSV.

    This is an offline-evaluation utility. It is intentionally separate from
    runtime data loading and retrieval-index construction.
    """
    resolved_path = Path(evaluation_path)

    if not resolved_path.is_file():
        raise FileNotFoundError(
            "Retrieval evaluation file was not found: "
            f"{resolved_path}"
        )

    evaluation_set = pd.read_csv(
        resolved_path,
        dtype=str,
    )

    return validate_retrieval_evaluation_set(
        evaluation_set=evaluation_set,
        known_chunk_ids=known_chunk_ids,
    )


def _validate_retrieval_result(
    retrieval_result: object,
    known_chunk_ids: set[str],
    top_k: int,
) -> list[str]:
    """Validate a retriever response and return its ranked chunk IDs."""
    if not isinstance(retrieval_result, Mapping):
        raise ValueError(
            "Retriever callback must return a mapping."
        )

    raw_results = retrieval_result.get("results")

    if not isinstance(raw_results, list):
        raise ValueError(
            "Retriever result must contain a list named results."
        )

    if len(raw_results) > top_k:
        raise ValueError(
            "Retriever returned more results than the requested top_k."
        )

    retrieved_chunk_ids: list[str] = []

    for item in raw_results:
        if not isinstance(item, Mapping):
            raise ValueError(
                "Each retriever result item must be a mapping."
            )

        chunk_id = _normalise_text(item.get("chunk_id"))

        if not chunk_id:
            raise ValueError(
                "Each retriever result item must contain chunk_id."
            )

        if chunk_id not in known_chunk_ids:
            raise ValueError(
                "Retriever returned a chunk outside the approved corpus: "
                f"{chunk_id}"
            )

        retrieved_chunk_ids.append(chunk_id)

    if len(retrieved_chunk_ids) != len(set(retrieved_chunk_ids)):
        raise ValueError(
            "Retriever returned duplicate chunk IDs for one query."
        )

    return retrieved_chunk_ids


def evaluate_retrieval_method(
    evaluation_set: pd.DataFrame,
    known_chunk_ids: Iterable[str],
    method_name: str,
    retrieve_query: Callable[[str, int], Mapping[str, Any]],
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Evaluate one retrieval method against the frozen query-to-chunk targets.

    `retrieve_query` receives `(query_text, top_k)` and must return a
    provenance-preserving retriever response with a ranked `results` list.
    """
    validated_top_k = _validate_top_k(top_k)

    normalised_method_name = _normalise_text(method_name)

    if not normalised_method_name:
        raise ValueError("method_name must be a non-empty string.")

    if not callable(retrieve_query):
        raise ValueError("retrieve_query must be callable.")

    known_chunk_id_set = {
        _normalise_text(chunk_id)
        for chunk_id in known_chunk_ids
        if _normalise_text(chunk_id)
    }

    validated_evaluation_set = validate_retrieval_evaluation_set(
        evaluation_set=evaluation_set,
        known_chunk_ids=known_chunk_id_set,
    )

    per_query_rows: list[dict[str, Any]] = []

    for row in validated_evaluation_set.itertuples(index=False):
        retrieval_result = retrieve_query(
            row.query_text,
            validated_top_k,
        )

        retrieved_chunk_ids = _validate_retrieval_result(
            retrieval_result=retrieval_result,
            known_chunk_ids=known_chunk_id_set,
            top_k=validated_top_k,
        )

        relevant_chunk_ids = set(row.relevant_chunk_ids)

        first_relevant_rank = next(
            (
                rank
                for rank, chunk_id in enumerate(
                    retrieved_chunk_ids,
                    start=1,
                )
                if chunk_id in relevant_chunk_ids
            ),
            None,
        )

        hit_at_1 = int(first_relevant_rank == 1)
        hit_at_k = int(first_relevant_rank is not None)

        reciprocal_rank = (
            round(1 / first_relevant_rank, 6)
            if first_relevant_rank is not None
            else 0.0
        )

        per_query_rows.append(
            {
                "method_name": normalised_method_name,
                "query_id": row.query_id,
                "query_family": row.query_family,
                "query_text": row.query_text,
                "relevant_chunk_ids": row.relevant_chunk_ids,
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "retrieval_status": _normalise_text(
                    retrieval_result.get(
                        "retrieval_status",
                        "UNKNOWN",
                    )
                ),
                "returned_result_count": len(retrieved_chunk_ids),
                "first_relevant_rank": first_relevant_rank,
                "hit_at_1": hit_at_1,
                f"hit_at_{validated_top_k}": hit_at_k,
                f"mrr_at_{validated_top_k}": reciprocal_rank,
            }
        )

    per_query_results = pd.DataFrame(per_query_rows)

    hit_at_k_column = f"hit_at_{validated_top_k}"
    mrr_at_k_column = f"mrr_at_{validated_top_k}"

    summary_metrics = {
        "method_name": normalised_method_name,
        "query_count": int(len(per_query_results)),
        "top_k": validated_top_k,
        "hit_at_1": float(per_query_results["hit_at_1"].mean()),
        hit_at_k_column: float(
            per_query_results[hit_at_k_column].mean()
        ),
        mrr_at_k_column: float(
            per_query_results[mrr_at_k_column].mean()
        ),
        "no_result_rate": float(
            per_query_results["returned_result_count"]
            .eq(0)
            .mean()
        ),
    }

    family_metrics = (
        per_query_results.groupby(
            "query_family",
            as_index=False,
        )
        .agg(
            query_count=("query_id", "count"),
            hit_at_1=("hit_at_1", "mean"),
            **{
                hit_at_k_column: (
                    hit_at_k_column,
                    "mean",
                ),
                mrr_at_k_column: (
                    mrr_at_k_column,
                    "mean",
                ),
            },
        )
        .sort_values(
            by="query_family",
            kind="stable",
        )
        .reset_index(drop=True)
    )

    return {
        "method_name": normalised_method_name,
        "top_k": validated_top_k,
        "query_results": per_query_results,
        "summary_metrics": summary_metrics,
        "family_metrics": family_metrics,
    }