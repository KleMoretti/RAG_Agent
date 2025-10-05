"""
测试Prompt Management服务层
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.prompt_management.service import PromptService
from src.prompt_management.schemas import AgentCreate, AgentUpdate, SystemPromptCreate, SystemPromptUpdate
from src.api.models import Agent, SystemPrompt, PromptVersion


class TestPromptService:
    """测试PromptService"""
    
    @pytest.mark.asyncio
    async def test_create_agent(self, prompt_service):
        """测试创建Agent"""
        agent_data = AgentCreate(
            name="测试智能体",
            description="用于测试的智能体",
            agent_type="chat",
            capabilities=["对话", "问答"]
        )
        
        agent = await prompt_service.create_agent(agent_data, created_by=1)
        
        assert agent.name == "测试智能体"
        assert agent.agent_type == "chat"
        assert agent.capabilities == ["对话", "问答"]
        assert agent.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_agent(self, prompt_service, sample_agent):
        """测试获取Agent"""
        agent = await prompt_service.get_agent(sample_agent.id)
        
        assert agent is not None
        assert agent.id == sample_agent.id
        assert agent.name == sample_agent.name
    
    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, prompt_service):
        """测试获取不存在的Agent"""
        agent = await prompt_service.get_agent(999)
        assert agent is None
    
    @pytest.mark.asyncio
    async def test_update_agent(self, prompt_service, sample_agent):
        """测试更新Agent"""
        update_data = AgentUpdate(
            name="更新后的智能体",
            description="更新后的描述"
        )
        
        updated_agent = await prompt_service.update_agent(
            sample_agent.id, update_data, updated_by=1
        )
        
        assert updated_agent.name == "更新后的智能体"
        assert updated_agent.description == "更新后的描述"
        assert updated_agent.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_delete_agent(self, prompt_service, sample_agent):
        """测试删除Agent"""
        result = await prompt_service.delete_agent(sample_agent.id)
        assert result is True
        
        # 验证Agent已被删除
        deleted_agent = await prompt_service.get_agent(sample_agent.id)
        assert deleted_agent is None
    
    @pytest.mark.asyncio
    async def test_list_agents(self, prompt_service, sample_agent):
        """测试列出Agents"""
        agents = await prompt_service.list_agents()
        
        assert len(agents) >= 1
        assert any(agent.id == sample_agent.id for agent in agents)
    
    @pytest.mark.asyncio
    async def test_create_prompt(self, prompt_service, sample_agent):
        """测试创建SystemPrompt"""
        prompt_data = SystemPromptCreate(
            agent_id=sample_agent.id,
            name="测试提示词",
            content="你是一个测试助手，请回答用户的问题。",
            language="zh-CN",
            variables=["user_name", "context"]
        )
        
        prompt = await prompt_service.create_prompt(prompt_data, created_by=1)
        
        assert prompt.name == "测试提示词"
        assert prompt.agent_id == sample_agent.id
        assert prompt.language == "zh-CN"
        assert prompt.variables == ["user_name", "context"]
    
    @pytest.mark.asyncio
    async def test_get_prompt(self, prompt_service, sample_prompt):
        """测试获取SystemPrompt"""
        prompt = await prompt_service.get_prompt(sample_prompt.id)
        
        assert prompt is not None
        assert prompt.id == sample_prompt.id
        assert prompt.name == sample_prompt.name
    
    @pytest.mark.asyncio
    async def test_update_prompt(self, prompt_service, sample_prompt):
        """测试更新SystemPrompt"""
        update_data = SystemPromptUpdate(
            name="更新后的提示词",
            content="更新后的内容"
        )
        
        updated_prompt = await prompt_service.update_prompt(
            sample_prompt.id, update_data, updated_by=1
        )
        
        assert updated_prompt.name == "更新后的提示词"
        assert updated_prompt.content == "更新后的内容"
        assert updated_prompt.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_activate_prompt(self, prompt_service, sample_prompt):
        """测试激活提示词"""
        # 先将提示词设为非激活状态
        sample_prompt.is_active = False
        prompt_service.db.commit()
        
        activated_prompt = await prompt_service.activate_prompt(
            sample_prompt.id, activated_by=1
        )
        
        assert activated_prompt.is_active is True
        assert activated_prompt.activated_at is not None
        assert activated_prompt.activated_by == 1
    
    @pytest.mark.asyncio
    async def test_get_agent_prompt(self, prompt_service, sample_agent, sample_prompt):
        """测试获取Agent的活跃提示词"""
        prompt = await prompt_service.get_agent_prompt(
            sample_agent.id, language="zh-CN"
        )
        
        assert prompt is not None
        assert prompt.agent_id == sample_agent.id
        assert prompt.language == "zh-CN"
        assert prompt.is_active is True
    
    @pytest.mark.asyncio
    async def test_search_prompts(self, prompt_service, sample_prompt):
        """测试搜索提示词"""
        results = await prompt_service.search_prompts(
            query="测试", language="zh-CN"
        )
        
        assert len(results) >= 1
        assert any(prompt.id == sample_prompt.id for prompt in results)
    
    @pytest.mark.asyncio
    async def test_record_usage(self, prompt_service, sample_prompt):
        """测试记录使用统计"""
        await prompt_service.record_usage(
            prompt_id=sample_prompt.id,
            response_time=1.5,
            success=True,
            user_feedback=4.5
        )
        
        # 验证统计数据已更新
        stats = prompt_service.db.query(
            prompt_service.db.query(sample_prompt).first().usage_stats
        ).first()
        
        if stats:
            assert stats.usage_count > 0
            assert stats.avg_response_time > 0
    
    @pytest.mark.asyncio
    async def test_get_usage_analytics(self, prompt_service, sample_usage_stats):
        """测试获取使用分析"""
        analytics = await prompt_service.get_usage_analytics(
            agent_id=sample_usage_stats.prompt.agent_id,
            days=30
        )
        
        assert analytics is not None
        assert "total_usage" in analytics
        assert "avg_response_time" in analytics
        assert "success_rate" in analytics
    
    @pytest.mark.asyncio
    async def test_create_version(self, prompt_service, sample_prompt):
        """测试创建提示词版本"""
        version = await prompt_service.create_version(
            prompt_id=sample_prompt.id,
            content="新版本内容",
            variables=["new_var"],
            change_description="测试版本更新",
            created_by=1
        )
        
        assert version.prompt_id == sample_prompt.id
        assert version.content == "新版本内容"
        assert version.variables == ["new_var"]
        assert version.change_description == "测试版本更新"
    
    @pytest.mark.asyncio
    async def test_get_version_history(self, prompt_service, sample_prompt_version):
        """测试获取版本历史"""
        history = await prompt_service.get_version_history(
            sample_prompt_version.prompt_id
        )
        
        assert len(history) >= 1
        assert any(v.id == sample_prompt_version.id for v in history)
    
    @pytest.mark.asyncio
    async def test_rollback_version(self, prompt_service, sample_prompt, sample_prompt_version):
        """测试版本回滚"""
        rolled_back = await prompt_service.rollback_version(
            sample_prompt.id,
            sample_prompt_version.id,
            rolled_back_by=1
        )
        
        assert rolled_back.content == sample_prompt_version.content
        assert rolled_back.variables == sample_prompt_version.variables
    
    @pytest.mark.asyncio
    async def test_cache_integration(self, prompt_service, sample_agent):
        """测试缓存集成"""
        # 第一次获取（从数据库）
        agent1 = await prompt_service.get_agent(sample_agent.id)
        
        # 第二次获取（从缓存）
        agent2 = await prompt_service.get_agent(sample_agent.id)
        
        assert agent1.id == agent2.id
        assert agent1.name == agent2.name
    
    @pytest.mark.asyncio
    async def test_error_handling(self, prompt_service):
        """测试错误处理"""
        # 测试获取不存在的资源
        agent = await prompt_service.get_agent(999)
        assert agent is None
        
        prompt = await prompt_service.get_prompt(999)
        assert prompt is None
        
        # 测试删除不存在的资源
        result = await prompt_service.delete_agent(999)
        assert result is False