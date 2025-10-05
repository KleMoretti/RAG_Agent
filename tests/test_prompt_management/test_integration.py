"""
Prompt Management集成测试
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.prompt_management.service import PromptService
from src.prompt_management.cache_manager import AdvancedCacheManager
from src.prompt_management.performance import PerformanceMonitor
from src.prompt_management.analytics import PromptAnalytics
from src.prompt_management.version_manager import VersionManager
from src.prompt_management.schemas import AgentCreate, SystemPromptCreate


class TestPromptManagementIntegration:
    """测试Prompt Management系统集成"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, db_session):
        """测试完整的工作流程"""
        # 初始化服务
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        performance_monitor = PerformanceMonitor()
        
        # 1. 创建Agent
        agent_data = AgentCreate(
            name="集成测试智能体",
            description="用于集成测试的智能体",
            agent_type="chat",
            capabilities=["对话", "问答", "分析"]
        )
        
        agent = await service.create_agent(agent_data, created_by=1)
        assert agent.id is not None
        
        # 2. 创建Prompt
        prompt_data = SystemPromptCreate(
            agent_id=agent.id,
            name="集成测试提示词",
            content="你是一个集成测试助手，请回答用户的问题。变量：{user_name}, {context}",
            language="zh-CN",
            variables=["user_name", "context"]
        )
        
        prompt = await service.create_prompt(prompt_data, created_by=1)
        assert prompt.id is not None
        
        # 3. 激活Prompt
        activated_prompt = await service.activate_prompt(prompt.id, activated_by=1)
        assert activated_prompt.is_active is True
        
        # 4. 测试缓存
        cache_manager.set_agent(agent.id, agent)
        cached_agent = cache_manager.get_agent(agent.id)
        assert cached_agent.id == agent.id
        
        # 5. 记录使用统计
        for i in range(5):
            await service.record_usage(
                prompt_id=prompt.id,
                response_time=1.0 + i * 0.1,
                success=True,
                user_feedback=4.0 + i * 0.2
            )
        
        # 6. 创建版本
        version = await service.create_version(
            prompt_id=prompt.id,
            content="更新后的提示词内容",
            variables=["user_name", "context", "new_var"],
            change_description="添加新变量",
            created_by=1
        )
        assert version.version == "1.1.0"  # 自动版本递增
        
        # 7. 获取分析数据
        analytics = await service.get_usage_analytics(agent_id=agent.id, days=30)
        assert analytics["total_usage"] >= 5
        
        # 8. 性能监控
        performance_monitor.record_response_time("test_endpoint", 1.5)
        stats = performance_monitor.get_response_time_stats("test_endpoint")
        assert stats.count == 1
        
        # 9. 搜索功能
        search_results = await service.search_prompts(query="集成测试", language="zh-CN")
        assert len(search_results) >= 1
        assert any(p.id == prompt.id for p in search_results)
    
    @pytest.mark.asyncio
    async def test_cache_performance_integration(self, db_session):
        """测试缓存与性能监控集成"""
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        performance_monitor = PerformanceMonitor()
        
        # 创建测试数据
        agent_data = AgentCreate(
            name="缓存测试智能体",
            description="用于缓存测试",
            agent_type="chat"
        )
        agent = await service.create_agent(agent_data, created_by=1)
        
        # 测试缓存性能
        start_time = datetime.utcnow()
        
        # 第一次获取（从数据库）
        with performance_monitor.monitor("get_agent_db"):
            agent1 = await service.get_agent(agent.id)
        
        # 设置缓存
        cache_manager.set_agent(agent.id, agent1)
        
        # 第二次获取（从缓存）
        with performance_monitor.monitor("get_agent_cache"):
            agent2 = cache_manager.get_agent(agent.id)
        
        # 验证缓存效果
        assert agent1.id == agent2.id
        
        # 检查性能差异
        db_stats = performance_monitor.get_response_time_stats("get_agent_db")
        cache_stats = performance_monitor.get_response_time_stats("get_agent_cache")
        
        # 缓存应该更快
        assert cache_stats.avg < db_stats.avg
    
    @pytest.mark.asyncio
    async def test_version_analytics_integration(self, db_session):
        """测试版本管理与分析集成"""
        service = PromptService(db_session)
        version_manager = VersionManager(db_session)
        analytics = PromptAnalytics(db_session)
        
        # 创建测试数据
        agent_data = AgentCreate(name="版本测试智能体", agent_type="chat")
        agent = await service.create_agent(agent_data, created_by=1)
        
        prompt_data = SystemPromptCreate(
            agent_id=agent.id,
            name="版本测试提示词",
            content="原始版本",
            language="zh-CN"
        )
        prompt = await service.create_prompt(prompt_data, created_by=1)
        
        # 创建多个版本
        versions = []
        for i in range(3):
            version = await service.create_version(
                prompt_id=prompt.id,
                content=f"版本 {i+1} 内容",
                change_description=f"更新到版本 {i+1}",
                created_by=1
            )
            versions.append(version)
            
            # 为每个版本记录使用统计
            for j in range((i+1) * 2):  # 递增使用次数
                await service.record_usage(
                    prompt_id=prompt.id,
                    response_time=1.0 + i * 0.1,
                    success=True,
                    user_feedback=4.0 + i * 0.1
                )
        
        # 获取版本性能指标
        for version in versions:
            metrics = await version_manager.get_version_metrics(version.id)
            assert metrics.usage_count >= 0
            assert metrics.performance_score >= 0
        
        # 获取最佳版本推荐
        best_version = await version_manager.get_best_version(prompt.id)
        assert best_version is not None
        
        # 获取分析报告
        report = await analytics.generate_usage_report(agent.id, days=30)
        assert report.agent_id == agent.id
        assert report.total_requests >= 0
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, db_session):
        """测试错误恢复集成"""
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        
        # 创建测试数据
        agent_data = AgentCreate(name="错误测试智能体", agent_type="chat")
        agent = await service.create_agent(agent_data, created_by=1)
        
        # 设置缓存
        cache_manager.set_agent(agent.id, agent)
        
        # 模拟数据库错误
        with patch.object(service, 'get_agent') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            # 应该从缓存获取
            cached_agent = cache_manager.get_agent(agent.id)
            assert cached_agent is not None
            assert cached_agent.id == agent.id
        
        # 测试缓存失效后的恢复
        cache_manager.invalidate_agent(agent.id)
        
        # 数据库恢复后应该能正常获取
        recovered_agent = await service.get_agent(agent.id)
        assert recovered_agent.id == agent.id
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, db_session):
        """测试并发操作"""
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        
        # 创建测试Agent
        agent_data = AgentCreate(name="并发测试智能体", agent_type="chat")
        agent = await service.create_agent(agent_data, created_by=1)
        
        # 并发创建Prompts
        async def create_prompt(index):
            prompt_data = SystemPromptCreate(
                agent_id=agent.id,
                name=f"并发提示词 {index}",
                content=f"并发测试内容 {index}",
                language="zh-CN"
            )
            return await service.create_prompt(prompt_data, created_by=1)
        
        # 并发执行
        tasks = [create_prompt(i) for i in range(5)]
        prompts = await asyncio.gather(*tasks)
        
        # 验证所有Prompts都创建成功
        assert len(prompts) == 5
        assert all(p.agent_id == agent.id for p in prompts)
        
        # 并发缓存操作
        async def cache_operations(prompt):
            cache_manager.set_prompt(prompt.id, prompt)
            await asyncio.sleep(0.01)  # 模拟异步操作
            return cache_manager.get_prompt(prompt.id)
        
        cache_tasks = [cache_operations(p) for p in prompts]
        cached_prompts = await asyncio.gather(*cache_tasks)
        
        # 验证缓存操作成功
        assert len(cached_prompts) == 5
        assert all(cp is not None for cp in cached_prompts)
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, db_session):
        """测试数据一致性"""
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        
        # 创建测试数据
        agent_data = AgentCreate(name="一致性测试智能体", agent_type="chat")
        agent = await service.create_agent(agent_data, created_by=1)
        
        prompt_data = SystemPromptCreate(
            agent_id=agent.id,
            name="一致性测试提示词",
            content="原始内容",
            language="zh-CN"
        )
        prompt = await service.create_prompt(prompt_data, created_by=1)
        
        # 设置缓存
        cache_manager.set_agent(agent.id, agent)
        cache_manager.set_prompt(prompt.id, prompt)
        
        # 更新数据
        from src.prompt_management.schemas import AgentUpdate
        update_data = AgentUpdate(name="更新后的智能体")
        updated_agent = await service.update_agent(agent.id, update_data, updated_by=1)
        
        # 验证缓存已失效
        cached_agent = cache_manager.get_agent(agent.id)
        assert cached_agent is None  # 缓存应该被清除
        
        # 重新获取应该得到更新后的数据
        fresh_agent = await service.get_agent(agent.id)
        assert fresh_agent.name == "更新后的智能体"
        assert fresh_agent.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, db_session):
        """测试负载下的性能"""
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        performance_monitor = PerformanceMonitor()
        
        # 创建测试数据
        agent_data = AgentCreate(name="负载测试智能体", agent_type="chat")
        agent = await service.create_agent(agent_data, created_by=1)
        
        # 预热缓存
        cache_manager.set_agent(agent.id, agent)
        
        # 模拟高负载
        async def simulate_load():
            tasks = []
            for i in range(100):
                # 混合数据库和缓存操作
                if i % 2 == 0:
                    task = service.get_agent(agent.id)
                else:
                    task = asyncio.create_task(
                        asyncio.coroutine(lambda: cache_manager.get_agent(agent.id))()
                    )
                tasks.append(task)
            
            start_time = datetime.utcnow()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = datetime.utcnow()
            
            return results, (end_time - start_time).total_seconds()
        
        results, duration = await simulate_load()
        
        # 验证性能
        assert duration < 5.0  # 应该在5秒内完成
        assert len([r for r in results if not isinstance(r, Exception)]) >= 50
        
        # 记录性能指标
        performance_monitor.record_metric("load_test_duration", duration)
        performance_monitor.record_metric("load_test_success_rate", 
                                        len([r for r in results if not isinstance(r, Exception)]) / len(results))
    
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, db_session):
        """测试系统健康监控"""
        service = PromptService(db_session)
        cache_manager = AdvancedCacheManager()
        performance_monitor = PerformanceMonitor()
        
        # 启动监控
        await performance_monitor.start_monitoring(interval=0.1)
        
        # 执行一些操作
        agent_data = AgentCreate(name="健康监控测试智能体", agent_type="chat")
        agent = await service.create_agent(agent_data, created_by=1)
        
        # 等待监控收集数据
        await asyncio.sleep(0.5)
        
        # 停止监控
        performance_monitor.stop_monitoring()
        
        # 检查系统健康状况
        summary = performance_monitor.get_performance_summary()
        assert "system_health" in summary
        
        # 检查缓存状态
        cache_stats = cache_manager.get_cache_stats()
        assert cache_stats.total_size >= 0
        
        # 检查系统资源
        system_stats = performance_monitor.get_system_stats(minutes=1)
        assert len(system_stats) > 0
        
        # 验证系统健康
        latest_stats = system_stats[-1] if system_stats else None
        if latest_stats:
            assert latest_stats.cpu_percent >= 0
            assert latest_stats.memory_percent >= 0