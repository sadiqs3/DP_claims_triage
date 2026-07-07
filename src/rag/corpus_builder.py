from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import pandas as pd


RETRIEVAL_STATUS_INCLUDED = "INCLUDED"

REQUIRED_REGISTRY_COLUMNS = {
    "document_id",
    "relative_path",
    "document_type",
    "retrieval_status",
    "retrieval_scope",
    "authority_role",
    "priority",
    "reason",
}

EXCLUDED_SECTION_TITLES = {
    "references",
    "examples of targeted requests",
}

CORPUS_COLUMNS = [
    "chunk_id",
    "document_id",
    "document_title",
    "document_version",
    "effective_date",
    "document_type",
    "retrieval_scope",
    "authority_role",
    "registry_priority",
    "source_relative_path",
    "source_document_sha256",
    "section_index",
    "section_title",
    "chunk_text",
    "chunk_char_count",
    "chunk_sha256",
]


def get_project_root() -> Path:
    """Return the project root from this module's location."""
    return Path(__file__).resolve().parents[2]


def _normalise_text(value: object) -> str:
    """Return stripped text, treating missing values as empty strings."""
    if value is None or pd.isna(value):
        return ""

    return str(value).strip()

def compute_corpus_fingerprint(corpus: pd.DataFrame) -> str:
    """
    Create a stable identity hash from corpus chunk IDs and content hashes.

    The fingerprint is independent of DataFrame row order and is used to
    verify that multiple retrievers operate over the same approved corpus.
    """
    required_columns = {"chunk_id", "chunk_sha256"}

    if not isinstance(corpus, pd.DataFrame):
        raise ValueError("Corpus must be a pandas DataFrame.")

    missing_columns = required_columns.difference(corpus.columns)

    if missing_columns:
        raise ValueError(
            "Corpus is missing fingerprint columns: "
            + ", ".join(sorted(missing_columns))
        )

    if corpus["chunk_id"].duplicated().any():
        raise ValueError(
            "Corpus contains duplicate chunk_id values."
        )

    fingerprint_rows = (
        corpus[["chunk_id", "chunk_sha256"]]
        .astype(str)
        .sort_values(by="chunk_id", kind="stable")
    )

    fingerprint_text = "\n".join(
        f"{row.chunk_id}|{row.chunk_sha256}"
        for row in fingerprint_rows.itertuples(index=False)
    )

    return hashlib.sha256(
        fingerprint_text.encode("utf-8")
    ).hexdigest()

def _validate_registry(registry: pd.DataFrame) -> None:
    """Validate the minimum schema required for controlled retrieval."""
    if not isinstance(registry, pd.DataFrame):
        raise ValueError("rag document registry must be a pandas DataFrame.")

    missing_columns = REQUIRED_REGISTRY_COLUMNS.difference(
        registry.columns
    )

    if missing_columns:
        raise ValueError(
            "rag document registry is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    if registry.empty:
        raise ValueError("rag document registry must not be empty.")


def _safe_document_path(
    relative_path: str,
    project_root: Path,
) -> Path:
    """
    Resolve a registered source document only within data/knowledge_base.

    This prevents accidental indexing of staging, evaluation, or arbitrary
    project files when registry contents are changed.
    """
    knowledge_base_root = (
        project_root / "data" / "knowledge_base"
    ).resolve()

    candidate_path = (project_root / relative_path).resolve()

    try:
        candidate_path.relative_to(knowledge_base_root)
    except ValueError as error:
        raise ValueError(
            "Included document path must remain inside "
            f"data/knowledge_base: {relative_path}"
        ) from error

    if not candidate_path.is_file():
        raise FileNotFoundError(
            f"Registered RAG document was not found: {relative_path}"
        )

    return candidate_path


def _extract_document_metadata(content: str) -> dict[str, str]:
    """Extract document title, version, and effective date from Markdown."""
    title_match = re.search(
        r"^#\s+(.+?)\s*$",
        content,
        flags=re.MULTILINE,
    )

    version_match = re.search(
        r"\*\*Version:\*\*\s*([^\n]+)",
        content,
    )

    effective_date_match = re.search(
        r"\*\*Effective date:\*\*\s*([^\n]+)",
        content,
    )

    return {
        "document_title": (
            title_match.group(1).strip()
            if title_match
            else "Untitled knowledge-base document"
        ),
        "document_version": (
            version_match.group(1).strip()
            if version_match
            else "Not specified"
        ),
        "effective_date": (
            effective_date_match.group(1).strip()
            if effective_date_match
            else "Not specified"
        ),
    }


def _clean_section_title(raw_title: str) -> str:
    """Remove numbering from a Markdown section title."""
    cleaned_title = re.sub(
        r"^\d+(\.\d+)*\.?\s*",
        "",
        raw_title.strip(),
    )

    return cleaned_title.strip()


def _normalise_chunk_text(text: str) -> str:
    """Preserve Markdown structure while removing excess blank lines."""
    return re.sub(
        r"\n{3,}",
        "\n\n",
        text.strip(),
    )


def _parse_markdown_sections(
    content: str,
) -> list[dict[str, Any]]:
    """
    Parse document preamble and level-two Markdown sections.

    Level-three headings remain within their parent section so examples and
    sub-guidance retain local context.
    """
    sections: list[dict[str, Any]] = []

    preamble_lines: list[str] = []
    current_title: str | None = None
    current_lines: list[str] = []

    def append_section(
        title: str,
        lines: list[str],
    ) -> None:
        section_text = _normalise_chunk_text("\n".join(lines))

        if not section_text:
            return

        clean_title = _clean_section_title(title)

        if clean_title.casefold() in EXCLUDED_SECTION_TITLES:
            return

        sections.append(
            {
                "section_title": clean_title,
                "section_body": section_text,
            }
        )

    for line in content.splitlines():
        if line.startswith("# "):
            continue

        if line.startswith("## "):
            if current_title is None:
                preamble_text = _normalise_chunk_text(
                    "\n".join(preamble_lines)
                )

                if preamble_text:
                    sections.append(
                        {
                            "section_title": "Document Overview",
                            "section_body": preamble_text,
                        }
                    )
            else:
                append_section(
                    title=current_title,
                    lines=current_lines,
                )

            current_title = line.removeprefix("## ").strip()
            current_lines = []
            continue

        if current_title is None:
            preamble_lines.append(line)
        else:
            current_lines.append(line)

    if current_title is None:
        preamble_text = _normalise_chunk_text(
            "\n".join(preamble_lines)
        )

        if preamble_text:
            sections.append(
                {
                    "section_title": "Document Overview",
                    "section_body": preamble_text,
                }
            )
    else:
        append_section(
            title=current_title,
            lines=current_lines,
        )

    return sections


def build_rag_corpus(
    registry: pd.DataFrame,
    project_root: Path | None = None,
) -> pd.DataFrame:
    """
    Build a provenance-preserving corpus from registry-approved documents only.

    Retrieved content is operational guidance only. This function does not
    create eligibility rules, alter triage outcomes, or load staging/evaluation
    assets.
    """
    _validate_registry(registry)

    resolved_project_root = (
        project_root.resolve()
        if project_root is not None
        else get_project_root()
    )

    included_documents = registry.loc[
        registry["retrieval_status"]
        .astype(str)
        .str.strip()
        .eq(RETRIEVAL_STATUS_INCLUDED)
    ].copy()

    if included_documents.empty:
        raise ValueError(
            "rag document registry contains no INCLUDED documents."
        )

    included_documents = included_documents.sort_values(
        by=["priority", "document_id"],
        kind="stable",
    )

    corpus_rows: list[dict[str, Any]] = []

    for _, registry_row in included_documents.iterrows():
        document_id = _normalise_text(registry_row["document_id"])
        relative_path = _normalise_text(
            registry_row["relative_path"]
        )

        if not document_id:
            raise ValueError(
                "Included registry document has an empty document_id."
            )

        if not relative_path:
            raise ValueError(
                f"Included registry document {document_id} has no path."
            )

        source_path = _safe_document_path(
            relative_path=relative_path,
            project_root=resolved_project_root,
        )

        content = source_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        metadata = _extract_document_metadata(content)
        source_document_sha256 = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        sections = _parse_markdown_sections(content)

        if not sections:
            raise ValueError(
                f"Registered RAG document has no usable sections: "
                f"{relative_path}"
            )

        for section_index, section in enumerate(sections, start=1):
            section_title = section["section_title"]
            section_body = section["section_body"]

            chunk_text = _normalise_chunk_text(
                f"Document: {metadata['document_title']}\n"
                f"Section: {section_title}\n\n"
                f"{section_body}"
            )

            chunk_id = (
                f"{document_id}::S{section_index:02d}"
            )

            corpus_rows.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "document_title": metadata["document_title"],
                    "document_version": metadata[
                        "document_version"
                    ],
                    "effective_date": metadata["effective_date"],
                    "document_type": _normalise_text(
                        registry_row["document_type"]
                    ),
                    "retrieval_scope": _normalise_text(
                        registry_row["retrieval_scope"]
                    ),
                    "authority_role": _normalise_text(
                        registry_row["authority_role"]
                    ),
                    "registry_priority": int(
                        registry_row["priority"]
                    ),
                    "source_relative_path": relative_path,
                    "source_document_sha256": source_document_sha256,
                    "section_index": section_index,
                    "section_title": section_title,
                    "chunk_text": chunk_text,
                    "chunk_char_count": len(chunk_text),
                    "chunk_sha256": hashlib.sha256(
                        chunk_text.encode("utf-8")
                    ).hexdigest(),
                }
            )

    corpus = pd.DataFrame(
        corpus_rows,
        columns=CORPUS_COLUMNS,
    )

    if corpus.empty:
        raise ValueError(
            "No retrieval chunks were created from INCLUDED documents."
        )

    if corpus["chunk_id"].duplicated().any():
        duplicate_ids = corpus.loc[
            corpus["chunk_id"].duplicated(),
            "chunk_id",
        ].tolist()

        raise ValueError(
            "Duplicate RAG chunk IDs detected: "
            + ", ".join(duplicate_ids)
        )

    return corpus