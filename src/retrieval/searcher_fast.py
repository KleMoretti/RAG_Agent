"""
优化的语义搜索引擎，整合快速索引和缓存机制。

性能优化：
1. 使用IVF+PQ快速索引（5-10倍加速）
2. 两级缓存（embedding缓存 + 结果缓存）
3. 批量查询优化
4. 性能监控和统计
"""
from __future__ import annotations

import time
from typing import Any, List, Protocol, runtime_checkable

import numpy as np

from .vector_store_fast import VectorStoreFast
from .cache import QueryCache, CachedEmbedder


@runtime_checkable
class SupportsEmbed(Protocol):
    def embed(self, texts: List[str]) -> np.ndarray:  # pragma: no cover - structural
        ...


class SearcherFast:
    """高性能语义搜索引擎（带缓存和快速索引）。
    
    特性：
    - 自动选择最优FAISS索引（Flat vs IVF+PQ）
    - 两级缓存机制（embedding + 结果）
    - 性能监控和统计
    """

    def __init__(
        self,
        embedder: SupportsEmbed,
        store: VectorStoreFast,
        enable_cache: bool = True,
        cache_size: int = 1000,
        cache_ttl: float = 3600.0,
    ) -> None:
        """
        Args:
            embedder: 向量化模型
            store: 快速向量存储
            enable_cache: 是否启用缓存
            cache_size: 缓存最大条目数
            cache_ttl: 缓存过期时间（秒）
        """
        self._store = store
        
        # 如果启用缓存，包装embedder
        if enable_cache:
            cache = QueryCache(max_size=cache_size, ttl=cache_ttl)
            self._embedder = CachedEmbedder(embedder, cache)
            self._result_cache = cache
            self._cache_enabled = True
        else:
            self._embedder = embedder
            self._result_cache = None
            self._cache_enabled = False
        
        # 性能统计
        self._stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "total_time_ms": 0.0,
        }

    @property
    def store(self) -> VectorStoreFast:
        return self._store

    def search(
        self,
        query: str,
        top_k: int = 5,
        use_cache: bool = True,
        nprobe: int = 10,
    ) -> List[dict[str, Any]]:
        """语义搜索（优化版）。

        Args:
            query: 查询文本
            top_k: 返回结果数
            use_cache: 是否使用缓存
            nprobe: IVF索引探测聚类数（10-100，越大越准确但越慢）

        Returns:
            排序的检索结果列表
        """
        start_time = time.perf_counter()
        
        query = (query or '').strip()
        if not query:
            return []
        
        # 尝试从结果缓存获取
        if use_cache and self._cache_enabled and self._result_cache:
            cached = self._result_cache.get_results(query, top_k)
            if cached is not None:
                self._stats["cache_hits"] += 1
                self._stats["total_queries"] += 1
                elapsed = (time.perf_counter() - start_time) * 1000
                self._stats["total_time_ms"] += elapsed
                return cached
        
        # Embedding（自动使用embedding缓存）
        vecs = self._embedder.embed([query])
        query_vec = vecs[0]
        
        # FAISS检索（使用快速索引）
        results = self._store.search(
            query_vec,
            top_k=top_k,
            include_metadata=True,
            nprobe=nprobe,
        )
        
        # 缓存结果
        if use_cache and self._cache_enabled and self._result_cache:
            self._result_cache.set_results(query, top_k, results)
        
        # 更新统计
        self._stats["total_queries"] += 1
        elapsed = (time.perf_counter() - start_time) * 1000
        self._stats["total_time_ms"] += elapsed
        
        return results

    def batch_search(
        self,
        queries: List[str],
        top_k: int = 5,
        use_cache: bool = True,
        nprobe: int = 10,
    ) -> List[List[dict[str, Any]]]:
        """批量搜索优化。"""
        results: List[List[dict[str, Any]]] = []
        
        # 先检查哪些可以从缓存获取
        uncached_queries = []
        uncached_indices = []
        
        for i, q in enumerate(queries):
            q = q.strip()
            if not q:
                results.append([])
                continue
            
            if use_cache and self._cache_enabled and self._result_cache:
                cached = self._result_cache.get_results(q, top_k)
                if cached is not None:
                    results.append(cached)
                    self._stats["cache_hits"] += 1
                    continue
            
            uncached_queries.append(q)
            uncached_indices.append(i)
            results.append([])  # 占位
        
        # 批量处理未缓存的查询
        if uncached_queries:
            vecs = self._embedder.embed(uncached_queries)
            for i, (q, vec) in enumerate(zip(uncached_queries, vecs)):
                res = self._store.search(vec, top_k=top_k, include_metadata=True, nprobe=nprobe)
                
                # 缓存结果
                if use_cache and self._cache_enabled and self._result_cache:
                    self._result_cache.set_results(q, top_k, res)
                
                # 填充结果
                original_idx = uncached_indices[i]
                results[original_idx] = res
        
        self._stats["total_queries"] += len(queries)
        return results

    def get_stats(self) -> dict[str, Any]:
        """获取性能统计。"""
        stats = self._stats.copy()
        
        if stats["total_queries"] > 0:
            stats["avg_time_ms"] = stats["total_time_ms"] / stats["total_queries"]
            stats["cache_hit_rate"] = f"{stats['cache_hits'] / stats['total_queries']:.2%}"
        else:
            stats["avg_time_ms"] = 0.0
            stats["cache_hit_rate"] = "0.00%"
        
        stats["index_type"] = self._store.index_type
        stats["index_size"] = self._store.size
        
        if self._cache_enabled and isinstance(self._embedder, CachedEmbedder):
            stats["embedder_cache"] = self._embedder.get_stats()
        
        return stats
    
    def clear_cache(self) -> None:
        """清空所有缓存。"""
        if self._cache_enabled:
            if isinstance(self._embedder, CachedEmbedder):
                self._embedder.clear_cache()
            if self._result_cache:
                self._result_cache.clear()
        
        # 重置统计
        self._stats = {
            "total_queries": 0,
            "cache_hits": 0,
            "total_time_ms": 0.0,
        }

