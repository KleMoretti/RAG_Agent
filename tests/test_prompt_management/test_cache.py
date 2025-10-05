"""
测试缓存管理功能
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.prompt_management.cache_manager import AdvancedCacheManager, MultiLevelCache, CacheEntry
from src.api.models import Agent, SystemPrompt


class TestMultiLevelCache:
    """测试多级缓存"""
    
    def test_cache_initialization(self):
        """测试缓存初始化"""
        cache = MultiLevelCache(l1_size=100, l2_size=1000)
        
        assert cache.l1_size == 100
        assert cache.l2_size == 1000
        assert len(cache.l1_cache) == 0
        assert len(cache.l2_cache) == 0
    
    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = MultiLevelCache()
        
        # 设置缓存
        cache.set("test_key", "test_value", ttl=3600)
        
        # 获取缓存
        value = cache.get("test_key")
        assert value == "test_value"
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        cache = MultiLevelCache()
        
        # 设置短期缓存
        cache.set("test_key", "test_value", ttl=1)
        
        # 立即获取应该成功
        value = cache.get("test_key")
        assert value == "test_value"
        
        # 等待过期后获取应该失败
        import time
        time.sleep(2)
        value = cache.get("test_key")
        assert value is None
    
    def test_cache_eviction(self):
        """测试缓存淘汰"""
        cache = MultiLevelCache(l1_size=2, l2_size=3)
        
        # 填满L1缓存
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # 添加第三个项目，应该触发L1淘汰
        cache.set("key3", "value3")
        
        # key1应该被移到L2
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_delete(self):
        """测试缓存删除"""
        cache = MultiLevelCache()
        
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        
        cache.delete("test_key")
        assert cache.get("test_key") is None
    
    def test_cache_clear(self):
        """测试缓存清空"""
        cache = MultiLevelCache()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert len(cache.l1_cache) == 0
        assert len(cache.l2_cache) == 0


class TestAdvancedCacheManager:
    """测试高级缓存管理器"""
    
    def test_cache_manager_initialization(self, cache_manager):
        """测试缓存管理器初始化"""
        assert cache_manager.prompt_cache is not None
        assert cache_manager.agent_cache is not None
        assert cache_manager.analytics_cache is not None
    
    @pytest.mark.asyncio
    async def test_agent_caching(self, cache_manager, sample_agent):
        """测试Agent缓存"""
        # 设置Agent缓存
        cache_manager.set_agent(sample_agent.id, sample_agent)
        
        # 获取Agent缓存
        cached_agent = cache_manager.get_agent(sample_agent.id)
        
        assert cached_agent is not None
        assert cached_agent.id == sample_agent.id
        assert cached_agent.name == sample_agent.name
    
    @pytest.mark.asyncio
    async def test_prompt_caching(self, cache_manager, sample_prompt):
        """测试Prompt缓存"""
        # 设置Prompt缓存
        cache_manager.set_prompt(sample_prompt.id, sample_prompt)
        
        # 获取Prompt缓存
        cached_prompt = cache_manager.get_prompt(sample_prompt.id)
        
        assert cached_prompt is not None
        assert cached_prompt.id == sample_prompt.id
        assert cached_prompt.name == sample_prompt.name
    
    @pytest.mark.asyncio
    async def test_analytics_caching(self, cache_manager):
        """测试Analytics缓存"""
        analytics_data = {
            "total_usage": 100,
            "avg_response_time": 1.5,
            "success_rate": 0.95
        }
        
        # 设置Analytics缓存
        cache_manager.set_analytics("test_key", analytics_data)
        
        # 获取Analytics缓存
        cached_analytics = cache_manager.get_analytics("test_key")
        
        assert cached_analytics is not None
        assert cached_analytics["total_usage"] == 100
        assert cached_analytics["success_rate"] == 0.95
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, cache_manager, sample_agent, sample_prompt):
        """测试缓存失效"""
        # 设置缓存
        cache_manager.set_agent(sample_agent.id, sample_agent)
        cache_manager.set_prompt(sample_prompt.id, sample_prompt)
        
        # 验证缓存存在
        assert cache_manager.get_agent(sample_agent.id) is not None
        assert cache_manager.get_prompt(sample_prompt.id) is not None
        
        # 失效Agent缓存
        cache_manager.invalidate_agent(sample_agent.id)
        assert cache_manager.get_agent(sample_agent.id) is None
        
        # 失效Prompt缓存
        cache_manager.invalidate_prompt(sample_prompt.id)
        assert cache_manager.get_prompt(sample_prompt.id) is None
    
    @pytest.mark.asyncio
    async def test_cache_preloading(self, cache_manager, db_session, sample_agent):
        """测试缓存预加载"""
        with patch.object(cache_manager, 'db', db_session):
            # 预加载Agent缓存
            await cache_manager.preload_agent_cache(sample_agent.id)
            
            # 验证缓存已加载
            cached_agent = cache_manager.get_agent(sample_agent.id)
            assert cached_agent is not None
            assert cached_agent.id == sample_agent.id
    
    @pytest.mark.asyncio
    async def test_cache_optimization(self, cache_manager):
        """测试缓存优化"""
        # 添加一些过期的缓存项
        cache_manager.prompt_cache.set("expired_key", "value", ttl=1)
        
        import time
        time.sleep(2)
        
        # 运行缓存优化
        await cache_manager.optimize_cache()
        
        # 验证过期项已被清理
        assert cache_manager.prompt_cache.get("expired_key") is None
    
    def test_cache_statistics(self, cache_manager):
        """测试缓存统计"""
        # 添加一些缓存项
        cache_manager.set_agent(1, Mock())
        cache_manager.set_prompt(1, Mock())
        cache_manager.set_analytics("key1", {})
        
        # 获取统计信息
        stats = cache_manager.get_cache_stats()
        
        assert stats.prompt_cache_size >= 1
        assert stats.agent_cache_size >= 1
        assert stats.analytics_cache_size >= 1
        assert stats.total_size >= 3
    
    @pytest.mark.asyncio
    async def test_cache_warming(self, cache_manager, db_session, sample_agent):
        """测试缓存预热"""
        with patch.object(cache_manager, 'db', db_session):
            # 预热所有活跃Agent的缓存
            await cache_manager.warm_all_active_agents()
            
            # 验证Agent缓存已预热
            cached_agent = cache_manager.get_agent(sample_agent.id)
            if sample_agent.is_active:
                assert cached_agent is not None
    
    def test_cache_clear_by_type(self, cache_manager):
        """测试按类型清空缓存"""
        # 添加各种类型的缓存
        cache_manager.set_agent(1, Mock())
        cache_manager.set_prompt(1, Mock())
        cache_manager.set_analytics("key1", {})
        
        # 清空Agent缓存
        cache_manager.clear_cache("agent")
        
        assert cache_manager.get_agent(1) is None
        assert cache_manager.get_prompt(1) is not None
        assert cache_manager.get_analytics("key1") is not None
        
        # 清空所有缓存
        cache_manager.clear_cache("all")
        
        assert cache_manager.get_prompt(1) is None
        assert cache_manager.get_analytics("key1") is None
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self, cache_manager):
        """测试并发缓存访问"""
        async def set_cache(key, value):
            cache_manager.set_agent(key, value)
            await asyncio.sleep(0.1)
            return cache_manager.get_agent(key)
        
        # 并发设置和获取缓存
        tasks = [
            set_cache(i, Mock(id=i, name=f"agent_{i}"))
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 验证所有操作都成功
        assert len(results) == 10
        assert all(result is not None for result in results)
    
    def test_cache_memory_management(self, cache_manager):
        """测试缓存内存管理"""
        # 添加大量缓存项
        for i in range(1000):
            cache_manager.set_agent(i, Mock(id=i, name=f"agent_{i}"))
        
        # 获取内存使用情况
        stats = cache_manager.get_cache_stats()
        
        # 验证缓存大小在合理范围内
        assert stats.agent_cache_size <= cache_manager.agent_cache.l1_size + cache_manager.agent_cache.l2_size