from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import faiss  # type: ignore


class VectorStore:
    """FAISS 内存向量库 + 元数据持久化。

    设计取舍：
    - 使用 Inner Product（配合外部已归一化向量 => 等价 cosine）。
    - 使用 JSONL 保存元数据（追加/调试友好），与二进制 index 分离。
    - 原子保存：写入临时文件后 rename，避免进程被杀导致损坏。
    - 线程安全：轻量锁保护 add/save/load（足够当前单进程场景）。
    """

    def __init__(
        self,
        dim: int,
        index_path: str | Path,
        metadata_path: str | Path | None = None,
        normalize: bool = False,
    ) -> None:
        self.dim = dim
        self.index_path = Path(index_path)
        self.metadata_path = (
            Path(metadata_path) if metadata_path else self.index_path.with_suffix(".meta.jsonl")
        )
        self.normalize = normalize
        self._index = faiss.IndexFlatIP(dim)
        self._metadatas: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        if self.index_path.exists() and self.metadata_path.exists():
            self.load()

    # --------------------------- Persistence --------------------------- #
    def save(self) -> None:
        """持久化 index 与 metadata (原子写)."""
        with self._lock:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_index = self.index_path.with_suffix(".tmp.index")
            tmp_meta = self.metadata_path.with_suffix(".tmp.jsonl")
            faiss.write_index(self._index, str(tmp_index))
            with tmp_meta.open("w", encoding="utf-8") as f:
                for m in self._metadatas:
                    f.write(json.dumps(m, ensure_ascii=False) + "\n")
            tmp_index.rename(self.index_path)
            tmp_meta.rename(self.metadata_path)

    def load(self) -> None:
        """从磁盘加载 index + metadata 并校验条数一致。"""
        with self._lock:
            self._index = faiss.read_index(str(self.index_path))
            self._metadatas.clear()
            with self.metadata_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._metadatas.append(json.loads(line))
            if len(self._metadatas) != self._index.ntotal:
                raise ValueError("Metadata count and index size mismatch")

    # ----------------------------- Mutations --------------------------- #
    def add(self, vectors: np.ndarray, metadatas: list[dict[str, Any]]) -> list[int]:
        """添加向量与元数据。

        Args:
            vectors: shape=(N,D) float32
            metadatas: N 条元数据，包含 file, chunk_id, hash, preview
        Returns:
            新增向量的内部 id 列表
        """
        if vectors.dtype != np.float32:
            raise ValueError("vectors must be float32")
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(f"Expected shape (*,{self.dim}) got {vectors.shape}")
        if len(metadatas) != vectors.shape[0]:
            raise ValueError("metadatas length mismatch")
        required = {"file", "chunk_id", "hash", "preview"}
        for m in metadatas:
            missing = required - m.keys()
            if missing:
                raise ValueError(f"metadata missing keys: {missing}")
        with self._lock:
            if self.normalize:
                norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
                vectors = vectors / norms
            start_id = self._index.ntotal
            self._index.add(vectors)  # type: ignore[arg-type]
            self._metadatas.extend(metadatas)
            return list(range(start_id, start_id + vectors.shape[0]))

    # ------------------------------ Search ----------------------------- #
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        include_metadata: bool = True,
    ) -> list[dict[str, Any]]:
        """向量检索。

        Args:
            query_vector: shape=(D,) or (1,D) float32 已归一化向量
            top_k: 返回条数
            include_metadata: 是否附带元数据
        Returns:
            排序结果列表（含 score, rank, id + 元数据）
        """
        if query_vector.dtype != np.float32:
            raise ValueError("query_vector must be float32")
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        if query_vector.shape != (1, self.dim):
            raise ValueError(f"query_vector must have shape (D,) or (1,D) with D={self.dim}")
        if self.normalize:
            # Ensure query normalized to match index normalization strategy
            norm = np.linalg.norm(query_vector, axis=1, keepdims=True) + 1e-12
            query_vector = query_vector / norm
        if self._index.ntotal == 0:
            return []
        k = min(top_k, self._index.ntotal)
        scores, ids = self._index.search(query_vector, k)  # type: ignore[arg-type]
        results: list[dict[str, Any]] = []
        for rank, (idx, score) in enumerate(zip(ids[0], scores[0]), start=1):
            base: dict[str, Any] = {"id": int(idx), "score": float(score), "rank": rank}
            if include_metadata:
                meta = self._metadatas[idx].copy()
                meta.update(base)
                results.append(meta)
            else:
                results.append(base)
        return results

    # ------------------------------ Utility ---------------------------- #
    @property
    def size(self) -> int:
        return self._index.ntotal

    def iter_metadata(self) -> Iterable[dict[str, Any]]:
        return iter(self._metadatas)
