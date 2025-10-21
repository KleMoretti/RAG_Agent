"""
查询增强器

在用户查询中识别专业词汇，并扩展查询以提高检索准确性。
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from src.vocabulary.service import VocabularyService

logger = logging.getLogger(__name__)


@dataclass
class EnhancedQuery:
    """增强后的查询"""

    original_query: str  # 原始查询
    enhanced_query: str  # 增强后的查询
    identified_terms: List[Dict]  # 识别到的专业词汇
    related_terms: List[str]  # 相关术语
    vocabulary_context: str  # 专业词汇上下文（用于Prompt）


class QueryEnhancer:
    """
    查询增强器

    功能：
    1. 识别查询中的专业词汇
    2. 扩展查询（添加同义词、相关术语）
    3. 生成专业词汇上下文（注入到Prompt）
    """

    def __init__(self, vocabulary_service: VocabularyService):
        """
        初始化查询增强器

        Args:
            vocabulary_service: 专业词汇服务
        """
        self.vocabulary_service = vocabulary_service

    def enhance(
        self,
        query: str,
        add_synonyms: bool = True,
        add_related: bool = True,
        max_related_terms: int = 5,
    ) -> EnhancedQuery:
        """
        增强查询

        Args:
            query: 原始查询
            add_synonyms: 是否添加同义词
            add_related: 是否添加相关术语
            max_related_terms: 最多添加的相关术语数量

        Returns:
            增强后的查询对象
        """
        # 1. 识别专业词汇
        identified_terms = self.vocabulary_service.find_terms_in_text(query)

        if not identified_terms:
            logger.debug(f"查询中未识别到专业词汇: {query}")
            return EnhancedQuery(
                original_query=query,
                enhanced_query=query,
                identified_terms=[],
                related_terms=[],
                vocabulary_context="",
            )

        logger.info(
            f"识别到 {len(identified_terms)} 个专业词汇: "
            f"{[t['term'] for t in identified_terms]}"
        )

        # 2. 收集相关术语
        all_related_terms = set()
        if add_synonyms or add_related:
            for term_info in identified_terms:
                vocab = term_info["vocabulary"]

                if add_synonyms and vocab.synonyms:
                    all_related_terms.update(vocab.synonyms)

                if add_related and vocab.related_terms:
                    all_related_terms.update(vocab.related_terms[:max_related_terms])

        related_terms_list = list(all_related_terms)[:max_related_terms]

        # 3. 构建增强查询
        enhanced_query = self._build_enhanced_query(
            query, identified_terms, related_terms_list
        )

        # 4. 生成专业词汇上下文
        vocabulary_context = self._build_vocabulary_context(identified_terms)

        return EnhancedQuery(
            original_query=query,
            enhanced_query=enhanced_query,
            identified_terms=identified_terms,
            related_terms=related_terms_list,
            vocabulary_context=vocabulary_context,
        )

    def _build_enhanced_query(
        self, original_query: str, identified_terms: List[Dict], related_terms: List[str]
    ) -> str:
        """
        构建增强查询（原始查询 + 相关术语）

        Args:
            original_query: 原始查询
            identified_terms: 识别到的专业词汇
            related_terms: 相关术语

        Returns:
            增强后的查询字符串
        """
        # 简单策略：在原始查询后追加相关术语
        if not related_terms:
            return original_query

        # 去重（避免重复添加）
        unique_related = [
            term for term in related_terms if term.lower() not in original_query.lower()
        ]

        if not unique_related:
            return original_query

        # 构建增强查询
        enhanced = f"{original_query} {' '.join(unique_related[:3])}"  # 最多添加3个相关词
        logger.debug(f"增强查询: {original_query} -> {enhanced}")
        return enhanced

    def _build_vocabulary_context(self, identified_terms: List[Dict]) -> str:
        """
        构建专业词汇上下文（用于注入到Prompt）

        Args:
            identified_terms: 识别到的专业词汇

        Returns:
            格式化的专业词汇上下文
        """
        if not identified_terms:
            return ""

        context_lines = ["=== 查询中的专业词汇 ==="]

        for term_info in identified_terms:
            vocab = term_info["vocabulary"]
            term = vocab.term

            # 词汇条目
            entry = [
                f"\n【{term}】",
                f"定义: {vocab.definition}",
                f"分类: {vocab.category}",
            ]

            # 同义词
            if vocab.synonyms:
                entry.append(f"同义词: {', '.join(vocab.synonyms)}")

            # 相关词汇
            if vocab.related_terms:
                entry.append(f"相关术语: {', '.join(vocab.related_terms[:5])}")

            context_lines.append("\n".join(entry))

        context_lines.append("\n=== 请基于以上专业词汇理解提供专业回答 ===\n")
        return "\n".join(context_lines)

    def get_vocabulary_definitions(self, terms: List[str]) -> Dict[str, str]:
        """
        批量获取专业词汇定义

        Args:
            terms: 术语列表

        Returns:
            术语 -> 定义的映射
        """
        definitions = {}
        for term in terms:
            vocab = self.vocabulary_service.get_by_term(term)
            if vocab:
                definitions[term] = vocab.definition
        return definitions

    def suggest_related_questions(
        self, query: str, max_suggestions: int = 3
    ) -> List[str]:
        """
        根据识别到的专业词汇推荐相关问题

        Args:
            query: 原始查询
            max_suggestions: 最多推荐数量

        Returns:
            推荐问题列表
        """
        identified_terms = self.vocabulary_service.find_terms_in_text(query)

        if not identified_terms:
            return []

        suggestions = []

        for term_info in identified_terms[:max_suggestions]:
            vocab = term_info["vocabulary"]

            # 基于相关术语生成推荐问题
            if vocab.related_terms:
                related = vocab.related_terms[0]
                suggestions.append(f"{vocab.term}与{related}的区别是什么？")

            # 基于分类生成推荐问题
            if vocab.category == "equipment":
                suggestions.append(f"{vocab.term}的维护保养要点有哪些？")
            elif vocab.category == "process":
                suggestions.append(f"{vocab.term}工艺的关键参数是什么？")
            elif vocab.category == "steel_grade":
                suggestions.append(f"{vocab.term}的化学成分和应用场景是什么？")

        return suggestions[:max_suggestions]

