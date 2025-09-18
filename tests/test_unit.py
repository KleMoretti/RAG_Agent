import sys, pathlib
import numpy as np
# Ensure project root is on sys.path so 'src' is importable when running via tooling
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import pytest

from src.retrieval.vector_store import VectorStore


def test_vector_store_add_and_search():
    dim = 8
    store = VectorStore(dim=dim, index_path='tmp.index', normalize=True)
    vectors = np.random.rand(5, dim).astype(np.float32)
    metas = [
        {"file": f"f{i}", "chunk_id": i, "hash": f"h{i}", "preview": f"text {i}"}
        for i in range(5)
    ]
    ids = store.add(vectors, metas)
    assert len(ids) == 5
    assert store.size == 5
    q = vectors[0]
    results = store.search(q, top_k=3)
    assert results
    assert results[0]['id'] == 0  # nearest should be itself after normalization
    assert 'score' in results[0]


def test_vector_store_save_load(tmp_path):
    dim = 4
    path = tmp_path / 'vs.index'
    store = VectorStore(dim=dim, index_path=path, normalize=True)
    vecs = np.random.rand(3, dim).astype(np.float32)
    metas = [
        {"file": "a", "chunk_id": 0, "hash": "ha", "preview": "A"},
        {"file": "b", "chunk_id": 1, "hash": "hb", "preview": "B"},
        {"file": "c", "chunk_id": 2, "hash": "hc", "preview": "C"},
    ]
    store.add(vecs, metas)
    store.save()

    # Load another instance
    store2 = VectorStore(dim=dim, index_path=path, normalize=True)
    assert store2.size == 3
    r = store2.search(vecs[1], top_k=2)
    assert r
    assert any(x['file'] == 'b' for x in r)


@pytest.mark.parametrize('bad_shape', [np.random.rand(4).astype(np.float32), np.random.rand(2, 5).astype(np.float32)])
def test_vector_store_add_shape_errors(bad_shape):
    store = VectorStore(dim=6, index_path='tmp2.index')
    metas = [{"file": "f", "chunk_id": 0, "hash": "h", "preview": "p"}]
    if bad_shape.ndim == 1:
        with pytest.raises(ValueError):
            store.add(bad_shape, metas)  # type: ignore[arg-type]
    else:
        with pytest.raises(ValueError):
            store.add(bad_shape, metas)
