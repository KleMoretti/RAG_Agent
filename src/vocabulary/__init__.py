"""
专业词汇模块

提供专业词汇管理、查询增强和智能识别功能。
"""

from src.vocabulary.service import VocabularyService
from src.vocabulary.query_enhancer import QueryEnhancer, EnhancedQuery

__all__ = ["VocabularyService", "QueryEnhancer", "EnhancedQuery"]

