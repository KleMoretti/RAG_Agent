import sys, pathlib
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.retrieval.vector_store import VectorStore
from src.retrieval.searcher import Searcher


class DummyEmbedder:
    def __init__(self, base_vec):
        self._base = base_vec.astype(np.float32)

    def embed(self, texts):
        # Deterministic embedding: base + hash length noise
        arr = []
        for t in texts:
            v = self._base.copy()
            v[0] += (len(t) % 10) * 0.01
            arr.append(v)
        return np.vstack(arr).astype(np.float32)


def test_searcher_pipeline(tmp_path):
    dim = 6
    index_path = tmp_path / 'store.index'
    store = VectorStore(dim=dim, index_path=index_path, normalize=True)
    base = np.random.rand(dim).astype(np.float32)
    emb = DummyEmbedder(base)
    # Add documents
    docs = ["alpha", "beta text", "gamma longer", "delta", "epsilon"]
    vecs = emb.embed(docs)
    metas = [
        {"file": f"doc{i}", "chunk_id": i, "hash": f"h{i}", "preview": d}
        for i, d in enumerate(docs)
    ]
    store.add(vecs, metas)

    searcher = Searcher(embedder=emb, store=store)
    results = searcher.search("beta query", top_k=3)
    assert results
    assert all('score' in r and 'rank' in r for r in results)
    assert len(results) <= 3

    batch = searcher.batch_search(["alpha", "", "epsilon"], top_k=2)
    assert len(batch) == 3
    assert batch[1] == []
