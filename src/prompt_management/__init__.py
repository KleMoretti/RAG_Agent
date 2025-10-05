"""
Prompt管理模块
提供AI Agent与System Prompt的映射管理、版本控制、缓存、分析等功能
"""

from .service import PromptService
from .cache import PromptCache, get_prompt_cache, get_default_prompt_template
from .cache_manager import AdvancedCacheManager, get_cache_manager, MultiLevelCache, CacheStats, CacheEntry
from .performance import PerformanceMonitor, get_performance_monitor, monitor_performance, PerformanceMetric, ResponseTimeStats, SystemResourceStats
from .version_manager import VersionManager, VersionComparison, VersionMetrics
from .analytics import PromptAnalytics, UsageReport, PerformanceMetrics, EffectAnalysis, TrendData
from .schemas import (
    # Agent相关
    AgentCreate, AgentUpdate, AgentResponse,
    
    # SystemPrompt相关
    SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse,
    
    # 版本相关
    PromptVersionResponse,
    
    # 使用统计相关
    PromptUsageStatsResponse, PromptUsageCreate,
    
    # 分析相关
    PromptAnalytics, AgentAnalytics,
    
    # 搜索相关
    PromptSearchRequest, PromptSearchResponse
)

__all__ = [
    # 服务类
    "PromptService",
    
    # 缓存相关
    "PromptCache", "get_prompt_cache", "get_default_prompt_template",
    "AdvancedCacheManager", "get_cache_manager", "MultiLevelCache", "CacheStats", "CacheEntry",
    
    # 性能监控
    "PerformanceMonitor", "get_performance_monitor", "monitor_performance", "PerformanceMetric", "ResponseTimeStats", "SystemResourceStats",
    
    # 版本管理
    "VersionManager", "VersionComparison", "VersionMetrics",
    
    # 分析相关
    "PromptAnalytics", "UsageReport", "PerformanceMetrics", "EffectAnalysis", "TrendData",
    
    # Schema类
    "AgentCreate", "AgentUpdate", "AgentResponse",
    "SystemPromptCreate", "SystemPromptUpdate", "SystemPromptResponse",
    "PromptVersionResponse",
    "PromptUsageStatsResponse", "PromptUsageCreate",
    "PromptAnalytics", "AgentAnalytics",
    "PromptSearchRequest", "PromptSearchResponse"
]