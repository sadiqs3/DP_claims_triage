# Architecture Decisions

## ADR-001 — Persisted semantic vector index

**Status:** Accepted  
**Date:** 2026-07-07

### Context

The project already contains a tested in-memory semantic retriever using
OpenAI `text-embedding-3-small` embeddings, L2 normalisation, and
cosine-similarity ranking.

The mid-submission baseline requires a reproducible vector storage and
indexing capability without changing deterministic triage authority or
silently changing the currently evaluated semantic retrieval behaviour.

### Options considered

1. **FAISS `IndexFlatIP`**
2. ChromaDB persistent collection
3. Continue with in-memory NumPy retrieval only

### Decision

Use **FAISS `IndexFlatIP`** as the persisted semantic index.

The index will use L2-normalised vectors and inner-product search, which
preserves cosine-similarity ranking semantics used by the current in-memory
semantic baseline.

A separate manifest will store corpus fingerprint, embedding model, vector
dimension, chunk ordering fingerprint, index type, and build metadata.

### Rationale

- Preserves the current tested semantic retrieval behaviour with minimal change.
- Suitable for the approved 21-chunk corpus and local execution.
- Supports deterministic persistence, loading, integrity validation, and rebuild.
- Keeps metadata, authority boundaries, and source lineage explicit.
- Leaves the future cross-encoder reranker independent of the vector store.

### Consequences

- The current `ControlledSemanticRetriever` remains the evaluated in-memory baseline.
- A separate persisted FAISS component will be added rather than replacing it.
- Corpus or embedding-configuration mismatches must block index loading and
  require a controlled rebuild.
- RAG retrieval remains analyst-facing and non-authoritative.
