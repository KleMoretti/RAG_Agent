"""
测试Prompt Management模型
"""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.api.models import Agent, SystemPrompt, PromptVersion, PromptUsageStats


class TestAgent:
    """测试Agent模型"""
    
    def test_create_agent(self, db_session):
        """测试创建Agent"""
        agent = Agent(
            name="测试智能体",
            description="用于测试的智能体",
            agent_type="chat",
            capabilities=["对话", "问答"],
            is_active=True,
            created_by=1
        )
        db_session.add(agent)
        db_session.commit()
        
        assert agent.id is not None
        assert agent.name == "测试智能体"
        assert agent.agent_type == "chat"
        assert agent.is_active is True
        assert agent.created_at is not None
    
    def test_agent_name_required(self, db_session):
        """测试Agent名称必填"""
        agent = Agent(
            description="用于测试的智能体",
            agent_type="chat",
            created_by=1
        )
        db_session.add(agent)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_agent_relationships(self, db_session, sample_agent):
        """测试Agent关联关系"""
        # 创建关联的SystemPrompt
        prompt = SystemPrompt(
            agent_id=sample_agent.id,
            name="测试提示词",
            content="测试内容",
            language="zh-CN",
            created_by=1
        )
        db_session.add(prompt)
        db_session.commit()
        
        # 验证关联关系
        db_session.refresh(sample_agent)
        assert len(sample_agent.prompts) == 1
        assert sample_agent.prompts[0].name == "测试提示词"


class TestSystemPrompt:
    """测试SystemPrompt模型"""
    
    def test_create_system_prompt(self, db_session, sample_agent):
        """测试创建SystemPrompt"""
        prompt = SystemPrompt(
            agent_id=sample_agent.id,
            name="测试提示词",
            content="你是一个测试助手，请回答用户的问题。",
            language="zh-CN",
            variables=["user_name", "context"],
            is_active=True,
            created_by=1
        )
        db_session.add(prompt)
        db_session.commit()
        
        assert prompt.id is not None
        assert prompt.name == "测试提示词"
        assert prompt.language == "zh-CN"
        assert prompt.variables == ["user_name", "context"]
        assert prompt.is_active is True
    
    def test_prompt_agent_required(self, db_session):
        """测试SystemPrompt必须关联Agent"""
        prompt = SystemPrompt(
            name="测试提示词",
            content="测试内容",
            language="zh-CN",
            created_by=1
        )
        db_session.add(prompt)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_prompt_versions_relationship(self, db_session, sample_prompt):
        """测试SystemPrompt版本关联关系"""
        # 创建版本
        version = PromptVersion(
            prompt_id=sample_prompt.id,
            version="1.0.0",
            content=sample_prompt.content,
            variables=sample_prompt.variables,
            change_description="初始版本",
            created_by=1
        )
        db_session.add(version)
        db_session.commit()
        
        # 验证关联关系
        db_session.refresh(sample_prompt)
        assert len(sample_prompt.versions) == 1
        assert sample_prompt.versions[0].version == "1.0.0"


class TestPromptVersion:
    """测试PromptVersion模型"""
    
    def test_create_prompt_version(self, db_session, sample_prompt):
        """测试创建PromptVersion"""
        version = PromptVersion(
            prompt_id=sample_prompt.id,
            version="1.0.0",
            content="你是一个测试助手，请回答用户的问题。",
            variables=["user_name", "context"],
            change_description="初始版本",
            created_by=1
        )
        db_session.add(version)
        db_session.commit()
        
        assert version.id is not None
        assert version.version == "1.0.0"
        assert version.change_description == "初始版本"
        assert version.created_at is not None
    
    def test_version_prompt_required(self, db_session):
        """测试PromptVersion必须关联SystemPrompt"""
        version = PromptVersion(
            version="1.0.0",
            content="测试内容",
            change_description="测试版本",
            created_by=1
        )
        db_session.add(version)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestPromptUsageStats:
    """测试PromptUsageStats模型"""
    
    def test_create_usage_stats(self, db_session, sample_prompt):
        """测试创建PromptUsageStats"""
        stats = PromptUsageStats(
            prompt_id=sample_prompt.id,
            usage_count=10,
            avg_response_time=1.5,
            success_rate=0.95,
            user_feedback_score=4.2,
            last_used=datetime.utcnow()
        )
        db_session.add(stats)
        db_session.commit()
        
        assert stats.id is not None
        assert stats.usage_count == 10
        assert stats.avg_response_time == 1.5
        assert stats.success_rate == 0.95
        assert stats.user_feedback_score == 4.2
    
    def test_stats_prompt_required(self, db_session):
        """测试PromptUsageStats必须关联SystemPrompt"""
        stats = PromptUsageStats(
            usage_count=10,
            avg_response_time=1.5,
            success_rate=0.95
        )
        db_session.add(stats)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_stats_relationship(self, db_session, sample_prompt):
        """测试PromptUsageStats关联关系"""
        stats = PromptUsageStats(
            prompt_id=sample_prompt.id,
            usage_count=10,
            avg_response_time=1.5,
            success_rate=0.95
        )
        db_session.add(stats)
        db_session.commit()
        
        # 验证关联关系
        db_session.refresh(sample_prompt)
        assert sample_prompt.usage_stats is not None
        assert sample_prompt.usage_stats.usage_count == 10