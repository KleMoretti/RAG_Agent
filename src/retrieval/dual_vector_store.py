"""双向量存储管理器：分离知识库和用户上传文件的向量索引"""

import logging
from pathlib import Path
from typing import Any, List, Literal

import numpy as np

from src.retrieval.vector_store_fast import VectorStoreFast

logger = logging.getLogger(__name__)


class DualVectorStoreManager:
    """双向量存储管理器
    
    特性：
    - 维护两个独立的 FAISS 索引（知识库 + 用户上传）
    - 支持优先检索策略（先搜索用户上传文件）
    - 自动路由文件到对应的索引
    """

    def __init__(
        self,
        kb_index_path: str | Path,
        user_index_path: str | Path,
        dim: int = 384,
        user_upload_score_threshold: float = 0.7,
        enable_priority_search: bool = True,
    ):
        """初始化双向量存储管理器
        
        Args:
            kb_index_path: 知识库索引路径
            user_index_path: 用户上传索引路径
            dim: 向量维度
            user_upload_score_threshold: 用户上传文件相似度阈值
            enable_priority_search: 是否启用优先检索
        """
        self.kb_index_path = Path(kb_index_path)
        self.user_index_path = Path(user_index_path)
        self.dim = dim
        self.user_upload_score_threshold = user_upload_score_threshold
        self.enable_priority_search = enable_priority_search

        # 创建两个独立的向量存储
        self.kb_store = VectorStoreFast(
            dim=dim,
            index_path=str(self.kb_index_path),
        )
        self.user_store = VectorStoreFast(
            dim=dim,
            index_path=str(self.user_index_path),
        )

        # 加载索引
        self._load_indexes()

    def _load_indexes(self):
        """加载向量索引"""
        # 加载知识库索引
        if self.kb_index_path.exists():
            try:
                self.kb_store.load()
                logger.info(f"✅ 已加载知识库索引: {self.kb_store.size} 个向量")
            except Exception as e:
                logger.warning(f"⚠️ 加载知识库索引失败: {e}")
        else:
            logger.info("📝 知识库索引不存在，将创建新索引")

        # 加载用户上传索引
        if self.user_index_path.exists():
            try:
                self.user_store.load()
                logger.info(f"✅ 已加载用户上传索引: {self.user_store.size} 个向量")
            except Exception as e:
                logger.warning(f"⚠️ 加载用户上传索引失败: {e}")
        else:
            logger.info("📝 用户上传索引不存在，将创建新索引")

    def add(
        self,
        vectors: np.ndarray,
        metadatas: List[dict[str, Any]],
        store_type: Literal["knowledge_base", "user_upload"] = "user_upload",
    ) -> List[int]:
        """添加向量到指定存储
        
        Args:
            vectors: 向量数组
            metadatas: 元数据列表
            store_type: 存储类型（knowledge_base 或 user_upload）
        
        Returns:
            添加的向量ID列表
        """
        # 在元数据中标记来源
        for meta in metadatas:
            meta["store_type"] = store_type

        if store_type == "knowledge_base":
            ids = self.kb_store.add(vectors, metadatas)
            logger.info(f"➕ 已添加 {len(ids)} 个向量到知识库索引")
        else:
            ids = self.user_store.add(vectors, metadatas)
            logger.info(f"➕ 已添加 {len(ids)} 个向量到用户上传索引")

        return ids

    def save(self, store_type: Literal["knowledge_base", "user_upload", "both"] = "both"):
        """保存索引到磁盘
        
        Args:
            store_type: 保存哪个索引（knowledge_base/user_upload/both）
        """
        if store_type in ("knowledge_base", "both"):
            self.kb_store.save()
            logger.info(f"💾 已保存知识库索引: {self.kb_index_path}")

        if store_type in ("user_upload", "both"):
            self.user_store.save()
            logger.info(f"💾 已保存用户上传索引: {self.user_index_path}")

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        include_metadata: bool = True,
        nprobe: int = 10,
    ) -> List[dict[str, Any]]:
        """智能检索：优先搜索用户上传文件，必要时结合知识库
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数
            include_metadata: 是否包含元数据
            nprobe: IVF索引探测聚类数
        
        Returns:
            排序的检索结果列表（用户上传结果优先）
        """
        if not self.enable_priority_search:
            # 禁用优先检索，合并搜索
            return self._combined_search(query_vector, top_k, include_metadata, nprobe)

        # 1. 先搜索用户上传文件
        user_results = []
        if self.user_store.size > 0:
            user_results = self.user_store.search(
                query_vector,
                top_k=top_k,
                include_metadata=include_metadata,
                nprobe=nprobe,
            )

        # 2. 判断用户上传结果是否足够好
        if user_results:
            best_score = user_results[0].get("score", 0.0)
            if best_score >= self.user_upload_score_threshold:
                logger.info(
                    f"🎯 用户上传文件高相关（相似度 {best_score:.2%}），"
                    f"返回 {len(user_results)} 个结果"
                )
                return user_results

        # 3. 搜索知识库
        kb_results = []
        if self.kb_store.size > 0:
            kb_results = self.kb_store.search(
                query_vector,
                top_k=top_k,
                include_metadata=include_metadata,
                nprobe=nprobe,
            )

        # 4. 合并结果（用户上传结果优先）
        combined = user_results + kb_results
        combined.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        result = combined[:top_k]

        user_count = sum(1 for r in result if r.get("store_type") == "user_upload")
        kb_count = len(result) - user_count
        logger.info(
            f"🔍 检索结果: {user_count} 个来自用户上传, {kb_count} 个来自知识库"
        )

        return result

    def _combined_search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        include_metadata: bool,
        nprobe: int,
    ) -> List[dict[str, Any]]:
        """合并搜索：同时搜索两个索引并合并结果"""
        all_results = []

        # 搜索用户上传索引
        if self.user_store.size > 0:
            user_results = self.user_store.search(
                query_vector,
                top_k=top_k * 2,  # 多取一些结果
                include_metadata=include_metadata,
                nprobe=nprobe,
            )
            all_results.extend(user_results)

        # 搜索知识库索引
        if self.kb_store.size > 0:
            kb_results = self.kb_store.search(
                query_vector,
                top_k=top_k * 2,
                include_metadata=include_metadata,
                nprobe=nprobe,
            )
            all_results.extend(kb_results)

        # 按相似度排序
        all_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return all_results[:top_k]

    def get_store(
        self, store_type: Literal["knowledge_base", "user_upload"]
    ) -> VectorStoreFast:
        """获取指定类型的向量存储
        
        Args:
            store_type: 存储类型
        
        Returns:
            VectorStoreFast 实例
        """
        if store_type == "knowledge_base":
            return self.kb_store
        else:
            return self.user_store

    @property
    def kb_size(self) -> int:
        """知识库索引大小"""
        return self.kb_store.size

    @property
    def user_size(self) -> int:
        """用户上传索引大小"""
        return self.user_store.size

    @property
    def total_size(self) -> int:
        """总索引大小"""
        return self.kb_size + self.user_size

    def clear(self, store_type: Literal["knowledge_base", "user_upload", "both"] = "both"):
        """清空索引
        
        Args:
            store_type: 清空哪个索引（knowledge_base/user_upload/both）
        """
        if store_type in ("knowledge_base", "both"):
            self.kb_store = VectorStoreFast(
                dim=self.dim,
                index_path=str(self.kb_index_path),
            )
            logger.info("🗑️ 已清空知识库索引")

        if store_type in ("user_upload", "both"):
            self.user_store = VectorStoreFast(
                dim=self.dim,
                index_path=str(self.user_index_path),
            )
            logger.info("🗑️ 已清空用户上传索引")

