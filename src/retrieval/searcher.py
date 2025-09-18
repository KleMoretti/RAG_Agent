from __future__ import annotations

from typing import Any, List, Protocol, runtime_checkable

import numpy as np

from .vector_store import VectorStore


@runtime_checkable
class SupportsEmbed(Protocol):
    def embed(self, texts: List[str]) -> np.ndarray:  # pragma: no cover - structural
        ...


class Searcher:
    """High-level semantic search facade.

    Couples an `Embedder` with a `VectorStore` to provide
    text -> embedding -> vector search pipeline.
    """

    def __init__(self, embedder: SupportsEmbed, store: VectorStore) -> None:
        self._embedder = embedder
        self._store = store

    @property
    def store(self) -> VectorStore:
        return self._store

    def search(self, query: str, top_k: int = 5) -> List[dict[str, Any]]:
        """Search similar chunks for a query string.

        Args:
            query: user query text
            top_k: number of results
        Returns:
            Ranked list with metadata + score/rank
        """
        query = (query or '').strip()
        if not query:
            return []
        # Embed returns normalized float32 matrix shape (1,D) for single query
        vecs = self._embedder.embed([query])
        query_vec = vecs[0]
        return self._store.search(query_vec, top_k=top_k, include_metadata=True)

    def batch_search(self, queries: List[str], top_k: int = 5) -> List[List[dict[str, Any]]]:
        """Batch search for multiple queries to reuse embedding call."""
        cleaned = [q.strip() for q in queries]
        if not cleaned:
            return []
        vecs = self._embedder.embed(cleaned)
        results: List[List[dict[str, Any]]] = []
        for i, q in enumerate(cleaned):
            if not q:
                results.append([])
                continue
            results.append(self._store.search(vecs[i], top_k=top_k, include_metadata=True))
        return results
