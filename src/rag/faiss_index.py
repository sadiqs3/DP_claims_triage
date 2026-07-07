from __future__ import annotations

# Persists approved KB embeddings only; it is not a claims-triage component.
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import faiss
import numpy as np
import pandas as pd

from src.rag.corpus_builder import compute_corpus_fingerprint
from src.rag.lexical_retriever import _validate_corpus

from src.rag.semantic_retriever import (
    DEFAULT_EMBEDDING_MODEL,
    embed_approved_corpus_chunks,
)


INDEX_ARTIFACT_VERSION = "faiss_semantic_index_v1"
INDEX_TYPE = "IndexFlatIP"

INDEX_FILENAME = "semantic_index.faiss"
MANIFEST_FILENAME = "semantic_index_manifest.json"


@dataclass(frozen=True)
class FAISSIndexManifest:
    """Metadata required to validate a persisted FAISS index before use."""

    artifact_version: str
    index_type: str
    embedding_model: str
    embedding_dimension: int
    corpus_size: int
    corpus_fingerprint: str
    chunk_order_fingerprint: str
    faiss_version: str
    created_at_utc: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serialisable representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: object) -> "FAISSIndexManifest":
        """Create a validated manifest from persisted JSON content."""
        if not isinstance(payload, dict):
            raise ValueError("Persisted index manifest must be a JSON object.")

        required_fields = {
            "artifact_version",
            "index_type",
            "embedding_model",
            "embedding_dimension",
            "corpus_size",
            "corpus_fingerprint",
            "chunk_order_fingerprint",
            "faiss_version",
            "created_at_utc",
        }

        missing_fields = required_fields.difference(payload)

        if missing_fields:
            raise ValueError(
                "Persisted index manifest is missing required fields: "
                f"{sorted(missing_fields)}."
            )

        try:
            return cls(
                artifact_version=str(payload["artifact_version"]),
                index_type=str(payload["index_type"]),
                embedding_model=str(payload["embedding_model"]),
                embedding_dimension=int(payload["embedding_dimension"]),
                corpus_size=int(payload["corpus_size"]),
                corpus_fingerprint=str(payload["corpus_fingerprint"]),
                chunk_order_fingerprint=str(
                    payload["chunk_order_fingerprint"]
                ),
                faiss_version=str(payload["faiss_version"]),
                created_at_utc=str(payload["created_at_utc"]),
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Persisted index manifest contains invalid field values."
            ) from error


@dataclass(frozen=True)
class LoadedFAISSIndex:
    """A validated FAISS index paired with the ordered approved corpus."""

    index: Any
    corpus: pd.DataFrame
    manifest: FAISSIndexManifest


def _prepare_corpus(corpus: pd.DataFrame) -> pd.DataFrame:
    """Validate and deterministically order the approved retrieval corpus."""
    _validate_corpus(corpus)

    return (
        corpus.copy()
        .sort_values(
            by=["registry_priority", "document_id", "section_index"],
            kind="stable",
        )
        .reset_index(drop=True)
    )


def _validate_embedding_model(model: object) -> str:
    """Validate the embedding-model identifier."""
    if not isinstance(model, str) or not model.strip():
        raise ValueError("embedding_model must be a non-empty string.")

    return model.strip()


def _normalise_document_embeddings(
    document_embeddings: object,
    expected_rows: int,
) -> np.ndarray:
    """Validate and L2-normalise document vectors for cosine-equivalent IP."""
    try:
        matrix = np.asarray(
            document_embeddings,
            dtype=np.float32,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(
            "document_embeddings must contain numeric vector values."
        ) from error

    if matrix.ndim != 2:
        raise ValueError(
            "document_embeddings must be a two-dimensional matrix."
        )

    if matrix.shape[0] != expected_rows:
        raise ValueError(
            "document_embeddings row count must match corpus size."
        )

    if matrix.shape[1] == 0:
        raise ValueError(
            "document_embeddings must contain at least one dimension."
        )

    if not np.isfinite(matrix).all():
        raise ValueError(
            "document_embeddings contains non-finite values."
        )

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)

    if np.any(norms == 0):
        raise ValueError(
            "document_embeddings must have non-zero L2 norms."
        )

    return np.ascontiguousarray(
        matrix / norms,
        dtype=np.float32,
    )


def _compute_chunk_order_fingerprint(corpus: pd.DataFrame) -> str:
    """Fingerprint ordered chunk IDs to protect FAISS row-to-chunk mapping."""
    ordered_chunk_ids = corpus["chunk_id"].astype(str).tolist()

    payload = json.dumps(
        ordered_chunk_ids,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return sha256(payload.encode("utf-8")).hexdigest()


def _resolve_artifact_directory(output_dir: str | Path) -> Path:
    """Create and return a directory for index and manifest artifacts."""
    artifact_dir = Path(output_dir)

    if artifact_dir.exists() and not artifact_dir.is_dir():
        raise ValueError("output_dir must be a directory path.")

    artifact_dir.mkdir(parents=True, exist_ok=True)

    return artifact_dir


def _write_json_atomically(path: Path, payload: dict[str, object]) -> None:
    """Write JSON through a temporary file to avoid partial manifest writes."""
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")

    temporary_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    temporary_path.replace(path)


def persist_faiss_semantic_index(
    corpus: pd.DataFrame,
    document_embeddings: object,
    output_dir: str | Path,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> FAISSIndexManifest:
    """
    Build and persist a FAISS exact inner-product index.

    Inputs must originate from the approved corpus only. The index stores
    embeddings; the runtime corpus remains the source of chunk text/metadata.
    """
    prepared_corpus = _prepare_corpus(corpus)
    validated_model = _validate_embedding_model(embedding_model)

    embedding_matrix = _normalise_document_embeddings(
        document_embeddings=document_embeddings,
        expected_rows=len(prepared_corpus),
    )

    index = faiss.IndexFlatIP(embedding_matrix.shape[1])
    index.add(embedding_matrix)

    artifact_dir = _resolve_artifact_directory(output_dir)
    index_path = artifact_dir / INDEX_FILENAME
    manifest_path = artifact_dir / MANIFEST_FILENAME
    temporary_index_path = index_path.with_suffix(".faiss.tmp")

    if temporary_index_path.exists():
        temporary_index_path.unlink()

    faiss.write_index(index, str(temporary_index_path))
    temporary_index_path.replace(index_path)

    manifest = FAISSIndexManifest(
        artifact_version=INDEX_ARTIFACT_VERSION,
        index_type=INDEX_TYPE,
        embedding_model=validated_model,
        embedding_dimension=int(embedding_matrix.shape[1]),
        corpus_size=len(prepared_corpus),
        corpus_fingerprint=compute_corpus_fingerprint(prepared_corpus),
        chunk_order_fingerprint=_compute_chunk_order_fingerprint(
            prepared_corpus
        ),
        faiss_version=str(getattr(faiss, "__version__", "unknown")),
        created_at_utc=datetime.now(timezone.utc).isoformat(),
    )

    _write_json_atomically(
        path=manifest_path,
        payload=manifest.to_dict(),
    )

    return manifest

def build_persisted_faiss_index_from_openai(
    corpus: pd.DataFrame,
    output_dir: str | Path,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    client: object | None = None,
) -> FAISSIndexManifest:
    """
    Build a persisted FAISS index from approved KB chunks only.

    The input must be the allow-listed RAG corpus. It must not contain claim
    records, customer narratives, identifiers, follow-up wording, or workflow
    outputs.
    """
    prepared_corpus, document_embeddings = (
        embed_approved_corpus_chunks(
            corpus=corpus,
            embedding_model=embedding_model,
            client=client,
        )
    )

    return persist_faiss_semantic_index(
        corpus=prepared_corpus,
        document_embeddings=document_embeddings,
        output_dir=output_dir,
        embedding_model=embedding_model,
    )

def load_validated_faiss_semantic_index(
    corpus: pd.DataFrame,
    output_dir: str | Path,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> LoadedFAISSIndex:
    """
    Load an index only when its corpus and embedding configuration match.

    A mismatch blocks loading rather than risking incorrect chunk mapping.
    """
    prepared_corpus = _prepare_corpus(corpus)
    validated_model = _validate_embedding_model(embedding_model)

    artifact_dir = Path(output_dir)
    index_path = artifact_dir / INDEX_FILENAME
    manifest_path = artifact_dir / MANIFEST_FILENAME

    if not index_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError(
            "Persisted FAISS index and manifest must both exist."
        )

    try:
        manifest_payload = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Persisted index manifest is not valid JSON."
        ) from error

    manifest = FAISSIndexManifest.from_dict(manifest_payload)

    if manifest.artifact_version != INDEX_ARTIFACT_VERSION:
        raise ValueError(
            "Persisted index artifact version is not supported."
        )

    if manifest.index_type != INDEX_TYPE:
        raise ValueError(
            "Persisted index type does not match the expected index type."
        )

    if manifest.embedding_model != validated_model:
        raise ValueError(
            "Persisted index embedding model does not match the "
            "requested embedding model."
        )

    expected_corpus_fingerprint = compute_corpus_fingerprint(
        prepared_corpus
    )

    if manifest.corpus_fingerprint != expected_corpus_fingerprint:
        raise ValueError(
            "Persisted index corpus fingerprint does not match the "
            "current approved corpus. Rebuild the index."
        )

    expected_chunk_order_fingerprint = _compute_chunk_order_fingerprint(
        prepared_corpus
    )

    if (
        manifest.chunk_order_fingerprint
        != expected_chunk_order_fingerprint
    ):
        raise ValueError(
            "Persisted index chunk order does not match the approved "
            "corpus. Rebuild the index."
        )

    index = faiss.read_index(str(index_path))

    if not isinstance(index, faiss.IndexFlatIP):
        raise ValueError(
            "Persisted index is not the expected FAISS IndexFlatIP type."
        )

    if int(index.ntotal) != manifest.corpus_size:
        raise ValueError(
            "Persisted index vector count does not match manifest."
        )

    if int(index.ntotal) != len(prepared_corpus):
        raise ValueError(
            "Persisted index vector count does not match corpus size."
        )

    if int(index.d) != manifest.embedding_dimension:
        raise ValueError(
            "Persisted index dimension does not match manifest."
        )

    return LoadedFAISSIndex(
        index=index,
        corpus=prepared_corpus,
        manifest=manifest,
    )