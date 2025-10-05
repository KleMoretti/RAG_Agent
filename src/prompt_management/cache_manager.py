"""
高级缓存管理器
提供多层缓存、预热、失效策略等功能
"""
from __future__ import annotations

import json
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import OrderedDict
from threading import Lock
from sqlalchemy.orm import Session

from src.api.models import Agent, SystemPrompt, PromptUsageStats, AgentType
from .cache import PromptCache, get_prompt_cache
from config.logging_config import setup_logging

logger = setup_logging()


@dataclass
class CacheStats:
    """缓存统计信息"""
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_requests: int = 0
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        return self.hit_count / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """缓存未命中率"""
        return self.miss_count / self.total_requests if self.total_requests > 0 else 0.0


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        if self.ttl_seconds is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> float:
        """缓存年龄（秒）"""
        return (datetime.utcnow() - self.created_at).total_seconds()


class MultiLevelCache:
    """多层缓存系统"""
    
    def __init__(self, l1_size: int = 100, l2_size: int = 500, default_ttl: int = 3600):
        self.l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # L1: 热点数据
        self.l2_cache: OrderedDict[str, CacheEntry] = OrderedDict()  # L2: 温数据
        self.l1_size = l1_size
        self.l2_size = l2_size
        self.default_ttl = default_ttl
        self.stats = CacheStats()
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            self.stats.total_requests += 1
            
            # 先检查L1缓存
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if not entry.is_expired:
                    entry.last_accessed = datetime.utcnow()
                    entry.access_count += 1
                    self.l1_cache.move_to_end(key)  # 移到末尾（最近使用）
                    self.stats.hit_count += 1
                    return entry.value
                else:
                    del self.l1_cache[key]
            
            # 检查L2缓存
            if key in self.l2_cache:
                entry = self.l2_cache[key]
                if not entry.is_expired:
                    entry.last_accessed = datetime.utcnow()
                    entry.access_count += 1
                    # 从L2提升到L1
                    del self.l2_cache[key]
                    self._put_l1(key, entry)
                    self.stats.hit_count += 1
                    return entry.value
                else:
                    del self.l2_cache[key]
            
            self.stats.miss_count += 1
            return None
    
    def put(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """存储缓存值"""
        with self.lock:
            ttl = ttl_seconds or self.default_ttl
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                ttl_seconds=ttl
            )
            self._put_l1(key, entry)
    
    def _put_l1(self, key: str, entry: CacheEntry) -> None:
        """存储到L1缓存"""
        if key in self.l1_cache:
            del self.l1_cache[key]
        elif len(self.l1_cache) >= self.l1_size:
            # L1满了，移除最旧的到L2
            old_key, old_entry = self.l1_cache.popitem(last=False)
            self._put_l2(old_key, old_entry)
        
        self.l1_cache[key] = entry
    
    def _put_l2(self, key: str, entry: CacheEntry) -> None:
        """存储到L2缓存"""
        if key in self.l2_cache:
            del self.l2_cache[key]
        elif len(self.l2_cache) >= self.l2_size:
            # L2满了，直接删除最旧的
            self.l2_cache.popitem(last=False)
            self.stats.eviction_count += 1
        
        self.l2_cache[key] = entry
    
    def invalidate(self, key: str) -> bool:
        """使缓存失效"""
        with self.lock:
            removed = False
            if key in self.l1_cache:
                del self.l1_cache[key]
                removed = True
            if key in self.l2_cache:
                del self.l2_cache[key]
                removed = True
            return removed
    
    def invalidate_pattern(self, pattern: str) -> int:
        """按模式使缓存失效"""
        with self.lock:
            removed_count = 0
            
            # 从L1删除匹配的键
            keys_to_remove = [k for k in self.l1_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.l1_cache[key]
                removed_count += 1
            
            # 从L2删除匹配的键
            keys_to_remove = [k for k in self.l2_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.l2_cache[key]
                removed_count += 1
            
            return removed_count
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self.lock:
            self.l1_cache.clear()
            self.l2_cache.clear()
            self.stats = CacheStats()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                "l1_size": len(self.l1_cache),
                "l2_size": len(self.l2_cache),
                "l1_capacity": self.l1_size,
                "l2_capacity": self.l2_size,
                "hit_count": self.stats.hit_count,
                "miss_count": self.stats.miss_count,
                "hit_rate": round(self.stats.hit_rate * 100, 2),
                "miss_rate": round(self.stats.miss_rate * 100, 2),
                "eviction_count": self.stats.eviction_count,
                "total_requests": self.stats.total_requests
            }


class AdvancedCacheManager:
    """高级缓存管理器"""
    
    def __init__(self, db_session_factory: Callable[[], Session]):
        self.db_session_factory = db_session_factory
        self.prompt_cache = MultiLevelCache(l1_size=50, l2_size=200, default_ttl=1800)  # 30分钟
        self.agent_cache = MultiLevelCache(l1_size=20, l2_size=100, default_ttl=3600)   # 1小时
        self.analytics_cache = MultiLevelCache(l1_size=30, l2_size=150, default_ttl=600)  # 10分钟
        self.preload_lock = Lock()
        self._preloaded = False
    
    def get_prompt(self, agent_id: int, language: str = "zh-CN") -> Optional[Dict[str, Any]]:
        """获取Prompt（带缓存）"""
        cache_key = f"prompt:{agent_id}:{language}"
        
        # 先从缓存获取
        cached_prompt = self.prompt_cache.get(cache_key)
        if cached_prompt:
            logger.debug(f"Cache hit for prompt {cache_key}")
            return cached_prompt
        
        # 缓存未命中，从数据库获取
        logger.debug(f"Cache miss for prompt {cache_key}, fetching from database")
        with self.db_session_factory() as db:
            prompt = db.query(SystemPrompt).filter(
                SystemPrompt.agent_id == agent_id,
                SystemPrompt.language == language,
                SystemPrompt.is_default == True,
                SystemPrompt.status == "active"
            ).first()
            
            if prompt:
                prompt_data = {
                    "id": prompt.id,
                    "name": prompt.name,
                    "content": prompt.content,
                    "variables": prompt.variables,
                    "version": prompt.version,
                    "metadata": prompt.meta_data
                }
                
                # 存入缓存
                self.prompt_cache.put(cache_key, prompt_data)
                return prompt_data
        
        return None
    
    def get_agent(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """获取Agent信息（带缓存）"""
        cache_key = f"agent:{agent_id}"
        
        cached_agent = self.agent_cache.get(cache_key)
        if cached_agent:
            return cached_agent
        
        with self.db_session_factory() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if agent:
                agent_data = {
                    "id": agent.id,
                    "name": agent.name,
                    "agent_type": agent.agent_type,
                    "display_name": agent.display_name,
                    "description": agent.description,
                    "icon": agent.icon,
                    "color": agent.color,
                    "capabilities": agent.capabilities,
                    "use_cases": agent.use_cases,
                    "tags": agent.tags,
                    "is_active": agent.is_active,
                    "created_at": agent.created_at,
                    "updated_at": agent.updated_at,
                    "created_by": agent.created_by
                }
                
                self.agent_cache.put(cache_key, agent_data)
                return agent_data
        
        return None
    
    def get_analytics_data(self, cache_key: str, compute_func: Callable[[], Any], 
                          ttl_seconds: int = 600) -> Any:
        """获取分析数据（带缓存）"""
        cached_data = self.analytics_cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 计算数据
        data = compute_func()
        if data is not None:
            self.analytics_cache.put(cache_key, data, ttl_seconds)
        
        return data
    
    def invalidate_prompt(self, agent_id: int, language: str = None) -> None:
        """使Prompt缓存失效"""
        if language:
            cache_key = f"prompt:{agent_id}:{language}"
            self.prompt_cache.invalidate(cache_key)
        else:
            # 删除该Agent的所有语言版本
            pattern = f"prompt:{agent_id}:"
            self.prompt_cache.invalidate_pattern(pattern)
        
        logger.info(f"Invalidated prompt cache for agent {agent_id}")
    
    def invalidate_agent(self, agent_id: int) -> None:
        """使Agent缓存失效"""
        cache_key = f"agent:{agent_id}"
        self.agent_cache.invalidate(cache_key)
        
        # 同时使相关的Prompt缓存失效
        self.invalidate_prompt(agent_id)
        
        logger.info(f"Invalidated agent cache for agent {agent_id}")
    
    def invalidate_analytics(self, pattern: str = None) -> None:
        """使分析数据缓存失效"""
        if pattern:
            self.analytics_cache.invalidate_pattern(pattern)
        else:
            self.analytics_cache.clear()
        
        logger.info("Invalidated analytics cache")
    
    def preload_hot_data(self) -> None:
        """预加载热点数据"""
        if self._preloaded:
            return
        
        with self.preload_lock:
            if self._preloaded:
                return
            
            logger.info("Starting cache preload...")
            
            with self.db_session_factory() as db:
                # 预加载活跃的Agent
                active_agents = db.query(Agent).filter(Agent.is_active == True).all()
                for agent in active_agents:
                    agent_data = {
                        "id": agent.id,
                        "name": agent.name,
                        "type": agent.type.value if agent.type else None,
                        "description": agent.description,
                        "capabilities": agent.capabilities,
                        "is_active": agent.is_active
                    }
                    self.agent_cache.put(f"agent:{agent.id}", agent_data)
                
                # 预加载默认Prompt
                default_prompts = db.query(SystemPrompt).filter(
                    SystemPrompt.is_default == True,
                    SystemPrompt.status == "active"
                ).all()
                
                for prompt in default_prompts:
                    prompt_data = {
                        "id": prompt.id,
                        "name": prompt.name,
                        "content": prompt.content,
                        "variables": prompt.variables,
                        "version": prompt.version,
                        "metadata": prompt.meta_data
                    }
                    cache_key = f"prompt:{prompt.agent_id}:{prompt.language}"
                    self.prompt_cache.put(cache_key, prompt_data)
            
            self._preloaded = True
            logger.info(f"Cache preload completed. Loaded {len(active_agents)} agents and {len(default_prompts)} prompts")
    
    async def preload_hot_data_async(self) -> None:
        """异步预加载热点数据"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.preload_hot_data)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取所有缓存统计信息"""
        return {
            "prompt_cache": self.prompt_cache.get_stats(),
            "agent_cache": self.agent_cache.get_stats(),
            "analytics_cache": self.analytics_cache.get_stats(),
            "preloaded": self._preloaded,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """优化缓存性能"""
        optimization_results = {
            "actions_taken": [],
            "before_stats": self.get_cache_stats(),
            "after_stats": None
        }
        
        # 清理过期条目
        expired_count = 0
        
        # 清理Prompt缓存中的过期条目
        with self.prompt_cache.lock:
            expired_keys = []
            for key, entry in self.prompt_cache.l1_cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            for key in expired_keys:
                del self.prompt_cache.l1_cache[key]
                expired_count += 1
            
            expired_keys = []
            for key, entry in self.prompt_cache.l2_cache.items():
                if entry.is_expired:
                    expired_keys.append(key)
            for key in expired_keys:
                del self.prompt_cache.l2_cache[key]
                expired_count += 1
        
        if expired_count > 0:
            optimization_results["actions_taken"].append(f"Removed {expired_count} expired entries")
        
        # 检查缓存命中率，如果太低则预加载热点数据
        prompt_hit_rate = self.prompt_cache.stats.hit_rate
        if prompt_hit_rate < 0.7 and not self._preloaded:
            self.preload_hot_data()
            optimization_results["actions_taken"].append("Preloaded hot data due to low hit rate")
        
        optimization_results["after_stats"] = self.get_cache_stats()
        
        logger.info(f"Cache optimization completed: {optimization_results['actions_taken']}")
        return optimization_results


# 全局缓存管理器实例
_cache_manager: Optional[AdvancedCacheManager] = None


def get_cache_manager(db_session_factory: Callable[[], Session]) -> AdvancedCacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = AdvancedCacheManager(db_session_factory)
    return _cache_manager


def init_cache_manager(db_session_factory: Callable[[], Session]) -> AdvancedCacheManager:
    """初始化缓存管理器"""
    global _cache_manager
    _cache_manager = AdvancedCacheManager(db_session_factory)
    return _cache_manager