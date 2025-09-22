from __future__ import annotations
from typing import Any, List, Callable
from pathlib import Path

import numpy as np

from .vector_store import VectorStore

class Indexer:
    """
    批量文本分块、嵌入并写入向量库，适配 dataprocessing 的 Embedder/Preprocessor/DataLoader。
    """

    def __init__(
        self,
        embedder: Any,  # 需有 encode(List[str]) -> np.ndarray
        store: VectorStore,
        chunker: Callable[[str], List[str]],
        preprocessor: Callable[[str], str] | None = None,
    ):
        self.embedder = embedder
        self.store = store
        self.chunker = chunker
        self.preprocessor = preprocessor

    def index_file(self, file_path: str | Path, file_id: str | None = None) -> List[int]:
        """
        索引单个文件，返回新加向量的 id 列表。
        读取原始文本，预处理、分块、嵌入、写入向量库。
        """
        file_path = Path(file_path)
        with file_path.open("r", encoding="utf-8") as f:
            text = f.read()
        if self.preprocessor:
            text = self.preprocessor(text)
        chunks = self.chunker(text)
        if not chunks:
            return []
        vectors = self.embedder.encode(chunks, normalize=True)
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadatas.append({
                "file": str(file_path),
                "chunk_id": i,
                "hash": hash(chunk),
                "preview": chunk[:50],
            })
        return self.store.add(vectors, metadatas)

    def index_files(self, files: List[str | Path]) -> None:
        """批量索引多个文件"""
        for file in files:
            self.index_file(file)

    def index_dataset(self, dataset: List[dict[str, Any]]) -> None:
        """
        索引结构化数据集（如 [{'text': ..., ...}, ...]）
        """
        for item in dataset:
            text = item.get("text", "")
            if self.preprocessor:
                text = self.preprocessor(text)
            chunks = self.chunker(text)
            if not chunks:
                continue
            vectors = self.embedder.encode(chunks, normalize=True)
            metadatas = []
            for i, chunk in enumerate(chunks):
                meta = dict(item)
                meta.update({
                    "chunk_id": i,
                    "hash": hash(chunk),
                    "preview": chunk[:50],
                })
                metadatas.append(meta)
            self.store.add(vectors, metadatas)
