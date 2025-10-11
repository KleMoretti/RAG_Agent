"""
优化的FAISS向量存储，使用IVF+PQ索引加速检索。

性能对比：
- IndexFlatIP: O(n) 暴力检索，适合<10万向量
- IndexIVFPQ: O(log n) 近似检索，适合>10万向量，速度提升5-10倍

设计：
- 自动根据向量数量选择索引类型
- 小数据集(<10000)使用Flat精确检索
- 大数据集使用IVF+PQ近似检索
- 保持与原VectorStore API兼容
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import faiss  # type: ignore


class VectorStoreFast:
    """优化的FAISS向量库，自动选择最优索引类型。
    
    自动策略：
    - < 10k 向量：IndexFlatIP (精确检索)
    - >= 10k 向量：IndexIVFPQ (近似检索，5-10倍加速)
    """

    # 切换阈值
    IVF_THRESHOLD = 10000
    
    def __init__(
        self,
        dim: int,
        index_path: str | Path,
        metadata_path: str | Path | None = None,
        normalize: bool = False,
        use_ivf: bool | None = None,  # None=自动，True=强制IVF，False=强制Flat
        nlist: int = 100,  # IVF聚类中心数
        m: int = 8,  # PQ子向量数
        nbits: int = 8,  # PQ每个子向量的比特数
    ) -> None:
        self.dim = dim
        self.index_path = Path(index_path)
        self.metadata_path = (
            Path(metadata_path) if metadata_path else self.index_path.with_suffix(".meta.jsonl")
        )
        self.normalize = normalize
        self.use_ivf = use_ivf
        self.nlist = nlist
        self.m = m
        self.nbits = nbits
        
        # 初始化为Flat索引（后续可能升级）
        self._index = faiss.IndexFlatIP(dim)
        self._is_ivf = False
        self._metadatas: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        
        # 如果已有索引，加载
        if self.index_path.exists() and self.metadata_path.exists():
            self.load()

    def _should_use_ivf(self) -> bool:
        """判断是否应该使用IVF索引"""
        if self.use_ivf is not None:
            return self.use_ivf
        return self._index.ntotal >= self.IVF_THRESHOLD

    def _upgrade_to_ivf(self) -> None:
        """将Flat索引升级为IVF索引（当数据量足够大时）"""
        if self._is_ivf or self._index.ntotal < self.IVF_THRESHOLD:
            return
            
        print(f"🚀 向量数量达到 {self._index.ntotal}，升级为IVF+PQ索引以加速检索...")
        
        # 1. 提取现有向量
        vectors = faiss.rev_swig_ptr(self._index.get_xb(), self._index.ntotal * self.dim)
        vectors = vectors.reshape(self._index.ntotal, self.dim)
        
        # 2. 创建IVF+PQ索引
        quantizer = faiss.IndexFlatIP(self.dim)
        # 使用PQ压缩：将向量压缩到m个子向量，每个nbits位
        index = faiss.IndexIVFPQ(quantizer, self.dim, self.nlist, self.m, self.nbits)
        
        # 3. 训练索引（IVF需要训练聚类中心）
        if self._index.ntotal >= self.nlist:
            print(f"   训练IVF索引（{self.nlist}个聚类中心）...")
            index.train(vectors)
            
            # 4. 添加向量
            print(f"   添加 {vectors.shape[0]} 个向量...")
            index.add(vectors)
            
            # 5. 替换索引
            self._index = index
            self._is_ivf = True
            print(f"✅ 升级完成！预计检索速度提升5-10倍")
        else:
            print(f"   向量数不足以训练IVF（需要>={self.nlist}），保持Flat索引")

    # --------------------------- Persistence --------------------------- #
    def save(self) -> None:
        """持久化 index 与 metadata (原子写)."""
        with self._lock:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存索引类型信息
            config_path = self.index_path.with_suffix(".config.json")
            config = {
                "is_ivf": self._is_ivf,
                "dim": self.dim,
                "normalize": self.normalize,
                "nlist": self.nlist,
                "m": self.m,
                "nbits": self.nbits,
            }
            
            tmp_index = self.index_path.with_suffix(".tmp.index")
            tmp_meta = self.metadata_path.with_suffix(".tmp.jsonl")
            tmp_config = config_path.with_suffix(".tmp.json")
            
            faiss.write_index(self._index, str(tmp_index))
            
            with tmp_meta.open("w", encoding="utf-8") as f:
                for m in self._metadatas:
                    f.write(json.dumps(m, ensure_ascii=False) + "\n")
            
            with tmp_config.open("w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 原子替换
            tmp_index.replace(self.index_path)
            tmp_meta.replace(self.metadata_path)
            tmp_config.replace(config_path)

    def load(self) -> None:
        """从磁盘加载 index + metadata."""
        with self._lock:
            # 加载配置
            config_path = self.index_path.with_suffix(".config.json")
            if config_path.exists():
                with config_path.open("r", encoding="utf-8") as f:
                    config = json.load(f)
                self._is_ivf = config.get("is_ivf", False)
            
            self._index = faiss.read_index(str(self.index_path))
            self._metadatas.clear()
            with self.metadata_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._metadatas.append(json.loads(line))
            if len(self._metadatas) != self._index.ntotal:
                raise ValueError(
                    f"Metadata count ({len(self._metadatas)}) and index size ({self._index.ntotal}) mismatch"
                )
            
            print(f"📥 加载向量库: {self._index.ntotal} 个向量, 索引类型: {'IVF+PQ' if self._is_ivf else 'Flat'}")

    # ----------------------------- Mutations --------------------------- #
    def add(self, vectors: np.ndarray, metadatas: list[dict[str, Any]]) -> list[int]:
        """添加向量与元数据，自动触发索引升级。"""
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
            
            # 如果是IVF索引且已训练，直接添加
            if self._is_ivf:
                self._index.add(vectors)  # type: ignore[arg-type]
            else:
                # Flat索引直接添加
                self._index.add(vectors)  # type: ignore[arg-type]
                
                # 检查是否需要升级
                if self._should_use_ivf() and not self._is_ivf:
                    self._upgrade_to_ivf()
            
            self._metadatas.extend(metadatas)
            return list(range(start_id, start_id + vectors.shape[0]))

    # ------------------------------ Search ----------------------------- #
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        include_metadata: bool = True,
        nprobe: int = 10,  # IVF搜索时探测的聚类数
    ) -> list[dict[str, Any]]:
        """向量检索（自动优化）。
        
        Args:
            query_vector: shape=(D,) or (1,D) float32 已归一化向量
            top_k: 返回条数
            include_metadata: 是否附带元数据
            nprobe: IVF索引探测的聚类数（越大越准确但越慢，建议10-100）
        """
        if query_vector.dtype != np.float32:
            raise ValueError("query_vector must be float32")
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        if query_vector.shape != (1, self.dim):
            raise ValueError(f"query_vector must have shape (D,) or (1,D) with D={self.dim}")
        
        if self.normalize:
            norm = np.linalg.norm(query_vector, axis=1, keepdims=True) + 1e-12
            query_vector = query_vector / norm
        
        if self._index.ntotal == 0:
            return []
        
        k = min(top_k, self._index.ntotal)
        
        # 如果是IVF索引，设置nprobe
        if self._is_ivf:
            self._index.nprobe = nprobe
        
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
    
    @property
    def index_type(self) -> str:
        """返回当前索引类型"""
        return "IVF+PQ" if self._is_ivf else "Flat"

