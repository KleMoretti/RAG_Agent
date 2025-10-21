"""
专业词汇服务

提供专业词汇的查询、缓存和管理功能。
"""

import logging
from typing import List, Dict, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.api.models import Vocabulary

logger = logging.getLogger(__name__)


class VocabularyService:
    """专业词汇服务类"""

    def __init__(self, db: Session):
        """
        初始化专业词汇服务

        Args:
            db: 数据库会话
        """
        self.db = db
        self._cache: Dict[str, List[Vocabulary]] = {}
        self._term_index: Dict[str, Vocabulary] = {}
        self._initialized = False

    def initialize(self) -> None:
        """
        初始化词汇缓存
        从数据库加载所有专业词汇到内存，提升查询性能
        """
        if self._initialized:
            return

        try:
            logger.info("正在加载专业词汇库...")
            all_vocab = self.db.query(Vocabulary).all()

            # 按分类缓存
            for vocab in all_vocab:
                category = vocab.category
                if category not in self._cache:
                    self._cache[category] = []
                self._cache[category].append(vocab)

                # 建立术语索引（用于快速查找）
                self._term_index[vocab.term.lower()] = vocab

                # 索引同义词
                if vocab.synonyms:
                    for synonym in vocab.synonyms:
                        self._term_index[synonym.lower()] = vocab

            logger.info(
                f"✅ 专业词汇库加载完成: {len(all_vocab)} 个词汇, "
                f"{len(self._cache)} 个分类, {len(self._term_index)} 个索引"
            )
            self._initialized = True

        except Exception as e:
            logger.error(f"加载专业词汇库失败: {e}")
            self._initialized = False

    def get_by_term(self, term: str) -> Optional[Vocabulary]:
        """
        根据术语获取词汇条目（支持同义词查询）

        Args:
            term: 术语名称

        Returns:
            词汇条目，如果不存在返回 None
        """
        if not self._initialized:
            self.initialize()

        return self._term_index.get(term.lower())

    def get_by_category(self, category: str) -> List[Vocabulary]:
        """
        根据分类获取词汇列表

        Args:
            category: 分类名称

        Returns:
            词汇列表
        """
        if not self._initialized:
            self.initialize()

        return self._cache.get(category, [])

    def search_terms(self, query: str, limit: int = 10) -> List[Vocabulary]:
        """
        模糊搜索专业词汇

        Args:
            query: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的词汇列表
        """
        if not self._initialized:
            self.initialize()

        query_lower = query.lower()
        results = []

        # 优先精确匹配
        if query_lower in self._term_index:
            results.append(self._term_index[query_lower])

        # 模糊匹配
        for term, vocab in self._term_index.items():
            if query_lower in term and vocab not in results:
                results.append(vocab)
                if len(results) >= limit:
                    break

        return results

    def find_terms_in_text(self, text: str) -> List[Dict[str, any]]:
        """
        在文本中识别专业词汇

        Args:
            text: 待识别的文本

        Returns:
            识别到的词汇列表，包含位置信息
            [
                {
                    "term": "Q235",
                    "position": (0, 4),
                    "vocabulary": Vocabulary对象,
                    "matched_by": "term"  # or "synonym"
                }
            ]
        """
        if not self._initialized:
            self.initialize()

        text_lower = text.lower()
        found_terms = []

        # 按术语长度倒序排列，优先匹配长词汇（避免子串干扰）
        sorted_terms = sorted(
            self._term_index.items(), key=lambda x: len(x[0]), reverse=True
        )

        for term, vocab in sorted_terms:
            start = 0
            while True:
                pos = text_lower.find(term, start)
                if pos == -1:
                    break

                # 检查边界（避免匹配单词的一部分）
                if self._is_word_boundary(text_lower, pos, pos + len(term)):
                    matched_by = "term" if term == vocab.term.lower() else "synonym"
                    found_terms.append(
                        {
                            "term": term,
                            "position": (pos, pos + len(term)),
                            "vocabulary": vocab,
                            "matched_by": matched_by,
                        }
                    )

                start = pos + 1

        # 去重并按位置排序
        unique_terms = self._deduplicate_terms(found_terms)
        return sorted(unique_terms, key=lambda x: x["position"][0])

    def get_related_terms(self, term: str, max_depth: int = 2) -> Set[str]:
        """
        获取相关术语（包括同义词和关联词汇）

        Args:
            term: 原始术语
            max_depth: 关联深度（1=直接关联, 2=二级关联）

        Returns:
            相关术语集合
        """
        if not self._initialized:
            self.initialize()

        vocab = self.get_by_term(term)
        if not vocab:
            return set()

        related = set()
        visited = set()

        def collect_related(v: Vocabulary, depth: int):
            if depth > max_depth or v.term in visited:
                return
            visited.add(v.term)

            # 添加同义词
            if v.synonyms:
                related.update(v.synonyms)

            # 添加相关词汇
            if v.related_terms:
                related.update(v.related_terms)
                # 递归查找相关词汇
                if depth < max_depth:
                    for related_term in v.related_terms:
                        related_vocab = self.get_by_term(related_term)
                        if related_vocab:
                            collect_related(related_vocab, depth + 1)

        collect_related(vocab, 1)
        return related

    def get_all_categories(self) -> List[str]:
        """
        获取所有词汇分类

        Returns:
            分类列表
        """
        if not self._initialized:
            self.initialize()

        return list(self._cache.keys())

    def get_statistics(self) -> Dict[str, any]:
        """
        获取词汇库统计信息

        Returns:
            统计数据
        """
        if not self._initialized:
            self.initialize()

        return {
            "total_terms": len(set(v.term for v in self._term_index.values())),
            "total_indexed_terms": len(self._term_index),
            "categories": len(self._cache),
            "category_distribution": {
                cat: len(vocabs) for cat, vocabs in self._cache.items()
            },
        }

    @staticmethod
    def _is_word_boundary(text: str, start: int, end: int) -> bool:
        """
        检查是否是单词边界
        
        支持中英文混合文本的边界检测：
        - 英文/数字术语（如 Q235）前后不能是英文/数字/下划线
        - 中文术语（如 抗拉强度）前后不能是中文字符
        - 英文和中文之间算边界

        Args:
            text: 文本
            start: 起始位置
            end: 结束位置

        Returns:
            是否是完整单词
        """
        # 检查前一个字符
        if start > 0:
            prev_char = text[start - 1]
            # 如果前一个字符是英文字母、数字或下划线，则不是边界
            if prev_char.isascii() and (prev_char.isalnum() or prev_char == '_'):
                return False
        
        # 检查后一个字符
        if end < len(text):
            next_char = text[end]
            # 如果后一个字符是英文字母、数字或下划线，则不是边界
            if next_char.isascii() and (next_char.isalnum() or next_char == '_'):
                return False
        
        return True

    @staticmethod
    def _deduplicate_terms(terms: List[Dict]) -> List[Dict]:
        """
        去除重叠的术语识别结果

        Args:
            terms: 识别到的术语列表

        Returns:
            去重后的列表
        """
        if not terms:
            return []

        # 按位置排序
        sorted_terms = sorted(terms, key=lambda x: (x["position"][0], -len(x["term"])))

        result = []
        last_end = -1

        for term in sorted_terms:
            start, end = term["position"]
            # 如果不重叠，则保留
            if start >= last_end:
                result.append(term)
                last_end = end

        return result

    def refresh_cache(self) -> None:
        """
        刷新缓存（重新从数据库加载）
        """
        self._cache.clear()
        self._term_index.clear()
        self._initialized = False
        self.initialize()

