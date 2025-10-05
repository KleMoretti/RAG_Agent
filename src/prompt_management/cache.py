"""
Prompt缓存管理模块
实现高性能的prompt缓存机制，确保低延迟响应
"""
from __future__ import annotations

import json
import time
from typing import Optional, Dict, Any, List
from functools import lru_cache
from datetime import datetime, timedelta

from config.logging_config import setup_logging

logger = setup_logging()


class PromptCache:
    """
    Prompt缓存管理器
    使用内存缓存提供高性能的prompt检索
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存生存时间(秒)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._creation_times: Dict[str, float] = {}
        
    def _generate_key(self, agent_id: int, language: str = "zh-CN", 
                     status: str = "active") -> str:
        """生成缓存键"""
        return f"prompt:{agent_id}:{language}:{status}"
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存项是否过期"""
        if key not in self._creation_times:
            return True
        
        creation_time = self._creation_times[key]
        return time.time() - creation_time > self.ttl_seconds
    
    def _evict_expired(self) -> None:
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = [
            key for key, creation_time in self._creation_times.items()
            if current_time - creation_time > self.ttl_seconds
        ]
        
        for key in expired_keys:
            self._remove_key(key)
    
    def _evict_lru(self) -> None:
        """使用LRU策略清理缓存"""
        if len(self._cache) <= self.max_size:
            return
        
        # 按访问时间排序，移除最久未使用的项
        sorted_keys = sorted(
            self._access_times.items(), 
            key=lambda x: x[1]
        )
        
        # 移除最旧的项，直到缓存大小符合限制
        while len(self._cache) > self.max_size:
            oldest_key = sorted_keys.pop(0)[0]
            self._remove_key(oldest_key)
    
    def _remove_key(self, key: str) -> None:
        """移除缓存键"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._creation_times.pop(key, None)
    
    def get(self, agent_id: int, language: str = "zh-CN", 
            status: str = "active") -> Optional[Dict[str, Any]]:
        """
        获取缓存的prompt
        
        Args:
            agent_id: Agent ID
            language: 语言
            status: 状态
            
        Returns:
            缓存的prompt数据或None
        """
        key = self._generate_key(agent_id, language, status)
        
        # 检查是否过期
        if self._is_expired(key):
            self._remove_key(key)
            return None
        
        if key in self._cache:
            # 更新访问时间
            self._access_times[key] = time.time()
            logger.debug(f"Cache hit for key: {key}")
            return self._cache[key].copy()
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, agent_id: int, prompt_data: Dict[str, Any], 
            language: str = "zh-CN", status: str = "active") -> None:
        """
        设置缓存的prompt
        
        Args:
            agent_id: Agent ID
            prompt_data: Prompt数据
            language: 语言
            status: 状态
        """
        key = self._generate_key(agent_id, language, status)
        current_time = time.time()
        
        # 清理过期项
        self._evict_expired()
        
        # 设置缓存
        self._cache[key] = prompt_data.copy()
        self._access_times[key] = current_time
        self._creation_times[key] = current_time
        
        # LRU清理
        self._evict_lru()
        
        logger.debug(f"Cache set for key: {key}")
    
    def invalidate(self, agent_id: int, language: Optional[str] = None) -> None:
        """
        使指定Agent的缓存失效
        
        Args:
            agent_id: Agent ID
            language: 语言，如果为None则清理所有语言的缓存
        """
        if language:
            # 清理特定语言的缓存
            keys_to_remove = [
                key for key in self._cache.keys()
                if key.startswith(f"prompt:{agent_id}:{language}:")
            ]
        else:
            # 清理所有语言的缓存
            keys_to_remove = [
                key for key in self._cache.keys()
                if key.startswith(f"prompt:{agent_id}:")
            ]
        
        for key in keys_to_remove:
            self._remove_key(key)
        
        logger.info(f"Invalidated cache for agent_id: {agent_id}, language: {language}")
    
    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._access_times.clear()
        self._creation_times.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        current_time = time.time()
        expired_count = sum(
            1 for creation_time in self._creation_times.values()
            if current_time - creation_time > self.ttl_seconds
        )
        
        return {
            "total_items": len(self._cache),
            "expired_items": expired_count,
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "memory_usage_estimate": len(json.dumps(self._cache))
        }


# 全局缓存实例
_prompt_cache: Optional[PromptCache] = None


def get_prompt_cache() -> PromptCache:
    """获取全局prompt缓存实例"""
    global _prompt_cache
    if _prompt_cache is None:
        _prompt_cache = PromptCache()
    return _prompt_cache


@lru_cache(maxsize=128)
def get_default_prompt_template(agent_type: str, language: str = "zh-CN") -> str:
    """
    获取默认的prompt模板
    使用LRU缓存提高性能
    
    Args:
        agent_type: Agent类型
        language: 语言
        
    Returns:
        默认prompt模板
    """
    templates = {
        "zh-CN": {
            "general": """你是一个专业的AI助手，具备广泛的知识基础和问题解决能力。
请根据用户的问题提供准确、有用的回答。

核心能力：
- 多领域知识问答
- 文档分析与总结
- 数据解读与建议
- 工作流程优化

请保持回答的专业性和准确性。""",
            
            "process": """你是钢铁生产工艺专家，深度了解炼钢、轧钢等各个生产环节。
请基于专业知识为用户提供工艺优化和技术改进建议。

专业领域：
- 工艺流程分析
- 生产参数优化
- 技术改进建议
- 工艺故障诊断

请确保建议的可操作性和安全性。""",
            
            "equipment": """你是设备维护和故障诊断专家，具备丰富的设备管理经验。
请帮助用户快速定位问题并提供解决方案。

专业能力：
- 故障快速诊断
- 预防性维护建议
- 设备性能分析
- 维修方案制定

请优先考虑安全因素，提供详细的操作指导。""",
            
            "market": """你是市场分析专家，专注于钢铁行业的市场情报和趋势分析。
请为用户提供专业的市场洞察和决策支持。

分析领域：
- 价格趋势分析
- 供需关系评估
- 竞争情报分析
- 投资决策建议

请基于数据提供客观、准确的分析结论。""",
        },
        "en-US": {
            "general": """You are a professional AI assistant with broad knowledge and problem-solving capabilities.
Please provide accurate and helpful responses based on user questions.

Core Capabilities:
- Multi-domain Q&A
- Document analysis and summarization
- Data interpretation and recommendations
- Workflow optimization

Please maintain professionalism and accuracy in your responses.""",
            
            "process": """You are a steel production process expert with deep understanding of steelmaking, rolling, and other production processes.
Please provide process optimization and technical improvement suggestions based on professional knowledge.

Expertise Areas:
- Process flow analysis
- Production parameter optimization
- Technical improvement recommendations
- Process fault diagnosis

Please ensure suggestions are actionable and safe.""",
            
            "equipment": """You are an equipment maintenance and fault diagnosis expert with extensive equipment management experience.
Please help users quickly identify problems and provide solutions.

Professional Capabilities:
- Rapid fault diagnosis
- Preventive maintenance recommendations
- Equipment performance analysis
- Repair plan development

Please prioritize safety factors and provide detailed operational guidance.""",
            
            "market": """You are a market analysis expert focused on steel industry market intelligence and trend analysis.
Please provide professional market insights and decision support for users.

Analysis Areas:
- Price trend analysis
- Supply and demand assessment
- Competitive intelligence analysis
- Investment decision recommendations

Please provide objective and accurate analytical conclusions based on data.""",
        }
    }
    
    return templates.get(language, templates["zh-CN"]).get(
        agent_type, templates[language]["general"]
    )