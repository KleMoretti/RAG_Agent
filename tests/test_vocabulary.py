"""
专业词汇功能测试
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.vocabulary.service import VocabularyService
from src.vocabulary.query_enhancer import QueryEnhancer
from src.api.models import Vocabulary


@pytest.fixture
def mock_db():
    """创建模拟数据库会话"""
    return Mock()


@pytest.fixture
def sample_vocabulary():
    """创建示例词汇数据"""
    return [
        Vocabulary(
            id=1,
            term="Q235",
            definition="碳素结构钢，屈服强度≥235MPa",
            category="steel_grade",
            synonyms=["碳素钢", "结构钢"],
            related_terms=["Q345", "抗拉强度", "屈服强度"],
        ),
        Vocabulary(
            id=2,
            term="转炉",
            definition="炼钢的主要设备，用于将生铁转化为钢",
            category="equipment",
            synonyms=["炼钢炉"],
            related_terms=["电炉", "炼钢", "钢水"],
        ),
        Vocabulary(
            id=3,
            term="抗拉强度",
            definition="材料在拉伸试验中所能承受的最大拉应力",
            category="material_property",
            synonyms=["拉伸强度"],
            related_terms=["屈服强度", "延伸率"],
        ),
    ]


@pytest.fixture
def vocab_service(mock_db, sample_vocabulary):
    """创建专业词汇服务实例"""
    service = VocabularyService(mock_db)
    
    # 模拟数据库查询
    mock_db.query.return_value.all.return_value = sample_vocabulary
    
    service.initialize()
    return service


@pytest.fixture
def query_enhancer(vocab_service):
    """创建查询增强器实例"""
    return QueryEnhancer(vocab_service)


class TestVocabularyService:
    """测试专业词汇服务"""

    def test_initialize(self, vocab_service):
        """测试初始化"""
        assert vocab_service._initialized is True
        assert len(vocab_service._cache) > 0
        assert len(vocab_service._term_index) > 0

    def test_get_by_term(self, vocab_service):
        """测试按术语获取"""
        vocab = vocab_service.get_by_term("Q235")
        assert vocab is not None
        assert vocab.term == "Q235"
        assert vocab.category == "steel_grade"

    def test_get_by_term_synonym(self, vocab_service):
        """测试通过同义词获取"""
        vocab = vocab_service.get_by_term("碳素钢")
        assert vocab is not None
        assert vocab.term == "Q235"

    def test_get_by_term_case_insensitive(self, vocab_service):
        """测试大小写不敏感"""
        vocab1 = vocab_service.get_by_term("Q235")
        vocab2 = vocab_service.get_by_term("q235")
        assert vocab1 is not None
        assert vocab2 is not None
        assert vocab1.id == vocab2.id

    def test_get_by_category(self, vocab_service):
        """测试按分类获取"""
        vocabs = vocab_service.get_by_category("steel_grade")
        assert len(vocabs) == 1
        assert vocabs[0].term == "Q235"

    def test_search_terms(self, vocab_service):
        """测试搜索词汇"""
        results = vocab_service.search_terms("Q2")
        assert len(results) > 0
        assert any(v.term == "Q235" for v in results)

    def test_find_terms_in_text(self, vocab_service):
        """测试在文本中识别词汇"""
        text = "Q235钢板的抗拉强度是多少？"
        found = vocab_service.find_terms_in_text(text)
        
        assert len(found) == 2
        terms = [t["term"].lower() for t in found]
        assert "q235" in terms
        assert "抗拉强度" in terms

    def test_find_terms_word_boundary(self, vocab_service):
        """测试单词边界检测"""
        # "Q2" 不应该匹配 "Q235"
        text = "Q2是什么材料？"
        found = vocab_service.find_terms_in_text(text)
        
        # 不应该误识别为 Q235
        assert not any(t["vocabulary"].term == "Q235" for t in found)

    def test_get_related_terms(self, vocab_service):
        """测试获取相关术语"""
        related = vocab_service.get_related_terms("Q235")
        assert len(related) > 0
        assert "Q345" in related or "抗拉强度" in related

    def test_get_statistics(self, vocab_service):
        """测试统计信息"""
        stats = vocab_service.get_statistics()
        assert stats["total_terms"] == 3
        assert "steel_grade" in stats["category_distribution"]


class TestQueryEnhancer:
    """测试查询增强器"""

    def test_enhance_no_terms(self, query_enhancer):
        """测试不包含专业词汇的查询"""
        result = query_enhancer.enhance("今天天气怎么样？")
        
        assert result.original_query == "今天天气怎么样？"
        assert result.enhanced_query == "今天天气怎么样？"
        assert len(result.identified_terms) == 0
        assert result.vocabulary_context == ""

    def test_enhance_with_terms(self, query_enhancer):
        """测试包含专业词汇的查询"""
        result = query_enhancer.enhance("Q235钢板的抗拉强度是多少？")
        
        assert result.original_query == "Q235钢板的抗拉强度是多少？"
        assert len(result.identified_terms) == 2
        assert len(result.related_terms) > 0
        assert result.vocabulary_context != ""
        assert "Q235" in result.vocabulary_context

    def test_enhance_with_synonyms(self, query_enhancer):
        """测试添加同义词"""
        result = query_enhancer.enhance(
            "Q235的性能如何？",
            add_synonyms=True,
            add_related=False
        )
        
        # 应该识别到 Q235
        assert len(result.identified_terms) > 0
        # 同义词应该在相关术语中
        assert any(term in ["碳素钢", "结构钢"] for term in result.related_terms)

    def test_enhance_with_related(self, query_enhancer):
        """测试添加相关术语"""
        result = query_enhancer.enhance(
            "Q235的性能如何？",
            add_synonyms=False,
            add_related=True
        )
        
        # 应该识别到 Q235
        assert len(result.identified_terms) > 0
        # 相关术语应该在列表中
        assert len(result.related_terms) > 0

    def test_enhance_max_related_terms(self, query_enhancer):
        """测试限制相关术语数量"""
        result = query_enhancer.enhance(
            "Q235的性能如何？",
            add_related=True,
            max_related_terms=2
        )
        
        # 相关术语数量应该不超过2
        assert len(result.related_terms) <= 2

    def test_vocabulary_context_format(self, query_enhancer):
        """测试专业词汇上下文格式"""
        result = query_enhancer.enhance("Q235钢板的抗拉强度")
        
        assert "=== 查询中的专业词汇 ===" in result.vocabulary_context
        assert "【Q235】" in result.vocabulary_context
        assert "定义:" in result.vocabulary_context
        assert "分类:" in result.vocabulary_context

    def test_get_vocabulary_definitions(self, query_enhancer):
        """测试批量获取词汇定义"""
        definitions = query_enhancer.get_vocabulary_definitions(["Q235", "转炉"])
        
        assert len(definitions) == 2
        assert "Q235" in definitions
        assert "转炉" in definitions
        assert "碳素结构钢" in definitions["Q235"]

    def test_suggest_related_questions(self, query_enhancer):
        """测试推荐相关问题"""
        suggestions = query_enhancer.suggest_related_questions("Q235的性能如何？")
        
        assert len(suggestions) > 0
        # 应该包含与Q235相关的问题
        assert any("Q235" in s for s in suggestions)


def test_integration_flow(vocab_service, query_enhancer):
    """测试完整集成流程"""
    # 1. 用户查询
    user_query = "Q235钢板和Q345钢板有什么区别？"
    
    # 2. 查询增强
    enhanced = query_enhancer.enhance(user_query, add_synonyms=True, add_related=True)
    
    # 3. 验证识别结果
    assert len(enhanced.identified_terms) >= 1  # 至少识别到Q235
    assert enhanced.vocabulary_context != ""
    
    # 4. 验证增强查询
    assert enhanced.enhanced_query != user_query  # 应该有扩展
    
    # 5. 验证上下文包含关键信息
    assert "碳素结构钢" in enhanced.vocabulary_context or "Q235" in enhanced.vocabulary_context
    
    print(f"✅ 集成测试通过:")
    print(f"   原始查询: {enhanced.original_query}")
    print(f"   增强查询: {enhanced.enhanced_query}")
    print(f"   识别词汇: {[t['term'] for t in enhanced.identified_terms]}")
    print(f"   相关术语: {enhanced.related_terms}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

