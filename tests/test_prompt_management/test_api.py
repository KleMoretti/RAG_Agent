"""
测试Prompt Management API端点
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from src.prompt_management.schemas import AgentCreate, SystemPromptCreate


class TestAgentAPI:
    """测试Agent API端点"""
    
    def test_create_agent(self, client):
        """测试创建Agent API"""
        agent_data = {
            "name": "测试智能体",
            "description": "用于测试的智能体",
            "agent_type": "chat",
            "capabilities": ["对话", "问答"]
        }
        
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post("/api/prompt-management/agents", json=agent_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试智能体"
        assert data["agent_type"] == "chat"
        assert data["is_active"] is True
    
    def test_get_agent(self, client, sample_agent):
        """测试获取Agent API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get(f"/api/prompt-management/agents/{sample_agent.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_agent.id
        assert data["name"] == sample_agent.name
    
    def test_get_agent_not_found(self, client):
        """测试获取不存在的Agent"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get("/api/prompt-management/agents/999")
        
        assert response.status_code == 404
    
    def test_list_agents(self, client, sample_agent):
        """测试列出Agents API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get("/api/prompt-management/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_update_agent(self, client, sample_agent):
        """测试更新Agent API"""
        update_data = {
            "name": "更新后的智能体",
            "description": "更新后的描述"
        }
        
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.put(
                f"/api/prompt-management/agents/{sample_agent.id}",
                json=update_data
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的智能体"
        assert data["description"] == "更新后的描述"
    
    def test_delete_agent(self, client, sample_agent):
        """测试删除Agent API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.delete(f"/api/prompt-management/agents/{sample_agent.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Agent deleted successfully"


class TestPromptAPI:
    """测试Prompt API端点"""
    
    def test_create_prompt(self, client, sample_agent):
        """测试创建Prompt API"""
        prompt_data = {
            "agent_id": sample_agent.id,
            "name": "测试提示词",
            "content": "你是一个测试助手，请回答用户的问题。",
            "language": "zh-CN",
            "variables": ["user_name", "context"]
        }
        
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post("/api/prompt-management/prompts", json=prompt_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试提示词"
        assert data["agent_id"] == sample_agent.id
        assert data["language"] == "zh-CN"
    
    def test_get_prompt(self, client, sample_prompt):
        """测试获取Prompt API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get(f"/api/prompt-management/prompts/{sample_prompt.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_prompt.id
        assert data["name"] == sample_prompt.name
    
    def test_get_agent_prompt(self, client, sample_agent, sample_prompt):
        """测试获取Agent提示词API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get(
                f"/api/prompt-management/agents/{sample_agent.id}/prompt",
                params={"language": "zh-CN"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == sample_agent.id
        assert data["language"] == "zh-CN"
    
    def test_activate_prompt(self, client, sample_prompt):
        """测试激活提示词API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post(
                f"/api/prompt-management/prompts/{sample_prompt.id}/activate"
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
    
    def test_search_prompts(self, client, sample_prompt):
        """测试搜索提示词API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get(
                "/api/prompt-management/prompts/search",
                params={"query": "测试", "language": "zh-CN"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestVersionAPI:
    """测试版本管理API端点"""
    
    def test_create_version(self, client, sample_prompt):
        """测试创建版本API"""
        version_data = {
            "content": "新版本内容",
            "variables": ["new_var"],
            "change_description": "测试版本更新"
        }
        
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post(
                f"/api/prompt-management/prompts/{sample_prompt.id}/versions",
                json=version_data
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "新版本内容"
        assert data["change_description"] == "测试版本更新"
    
    def test_get_version_history(self, client, sample_prompt_version):
        """测试获取版本历史API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get(
                f"/api/prompt-management/prompts/{sample_prompt_version.prompt_id}/versions"
            )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestAnalyticsAPI:
    """测试分析API端点"""
    
    def test_get_usage_analytics(self, client, sample_agent):
        """测试获取使用分析API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get(
                f"/api/prompt-management/analytics/usage/{sample_agent.id}",
                params={"days": 30}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "agent_id" in data
        assert "timeframe_days" in data
    
    def test_record_usage(self, client, sample_prompt):
        """测试记录使用统计API"""
        usage_data = {
            "response_time": 1.5,
            "success": True,
            "user_feedback": 4.5
        }
        
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post(
                f"/api/prompt-management/prompts/{sample_prompt.id}/usage",
                json=usage_data
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Usage recorded successfully"


class TestCacheAPI:
    """测试缓存管理API端点"""
    
    def test_clear_cache(self, client):
        """测试清空缓存API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post(
                "/api/prompt-management/cache/clear",
                params={"cache_type": "all"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_get_cache_stats(self, client):
        """测试获取缓存统计API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get("/api/prompt-management/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_size" in data


class TestPerformanceAPI:
    """测试性能监控API端点"""
    
    def test_get_performance_summary(self, client):
        """测试获取性能摘要API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get("/api/prompt-management/performance/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_endpoints" in data
        assert "total_metrics" in data
    
    def test_get_response_times(self, client):
        """测试获取响应时间API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.get("/api/prompt-management/performance/response-times")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
    
    def test_start_performance_monitoring(self, client):
        """测试启动性能监控API"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post(
                "/api/prompt-management/performance/start-monitoring",
                params={"interval": 30}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Performance monitoring started"


class TestHealthAPI:
    """测试健康检查API端点"""
    
    def test_health_check(self, client):
        """测试健康检查API"""
        response = client.get("/api/prompt-management/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "prompt_management"
        assert "timestamp" in data


class TestAuthenticationAPI:
    """测试API认证"""
    
    def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = client.get("/api/prompt-management/agents")
        
        # 应该返回401未授权状态码
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """测试无效token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/prompt-management/agents", headers=headers)
        
        # 应该返回401未授权状态码
        assert response.status_code == 401


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_json(self, client):
        """测试无效JSON"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post(
                "/api/prompt-management/agents",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """测试缺少必填字段"""
        agent_data = {
            "description": "缺少名称的智能体"
            # 缺少必填的name字段
        }
        
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            response = client.post("/api/prompt-management/agents", json=agent_data)
        
        assert response.status_code == 422
    
    def test_database_error_handling(self, client):
        """测试数据库错误处理"""
        with patch('src.auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = Mock(id=1, username="test_user")
            
            with patch('src.prompt_management.service.PromptService.create_agent') as mock_create:
                mock_create.side_effect = Exception("Database error")
                
                agent_data = {
                    "name": "测试智能体",
                    "description": "用于测试的智能体",
                    "agent_type": "chat"
                }
                
                response = client.post("/api/prompt-management/agents", json=agent_data)
        
        assert response.status_code == 500