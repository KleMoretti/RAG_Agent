"""
Prompt管理API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.api.db import get_db
from src.api.auth import get_current_user
from src.api.models import User
from .service import PromptService
from .version_manager import VersionManager, VersionComparison, VersionMetrics
from .analytics import PromptAnalytics, UsageReport, PerformanceMetrics, EffectAnalysis, TrendData
from .cache_manager import get_cache_manager
from .performance import get_performance_monitor, monitor_performance
from .schemas import (
    AgentCreate, AgentUpdate, AgentResponse,
    SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse,
    PromptVersionResponse, PromptUsageCreate, PromptUsageStatsResponse,
    PromptAnalytics, AgentAnalytics, PromptSearchRequest, PromptSearchResponse
)

router = APIRouter(prefix="/api/prompt-management", tags=["prompt-management"])


def get_prompt_service(db: Session = Depends(get_db)) -> PromptService:
    """获取PromptService实例"""
    return PromptService(db)


# ==================== Agent管理接口 ====================

@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("create_agent")
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """
    创建新的AI Agent
    
    - **name**: Agent名称（唯一）
    - **agent_type**: Agent类型（rag_agent, chat_agent, analysis_agent等）
    - **description**: Agent描述
    - **capabilities**: Agent能力列表
    - **is_active**: 是否激活（默认True）
    """
    try:
        return service.create_agent(agent, created_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    is_active: Optional[bool] = Query(None, description="过滤激活状态"),
    agent_type: Optional[str] = Query(None, description="过滤Agent类型"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    service: PromptService = Depends(get_prompt_service)
):
    """
    获取Agent列表
    
    支持按激活状态和类型过滤
    注意: 此端点不需要认证,以便前端UI能够显示可用的Agent列表
    """
    # 不使用 current_user 依赖,允许未认证用户访问Agent列表
    return service.list_agents(is_active=is_active, agent_type=agent_type, skip=skip, limit=limit)


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """获取指定Agent信息"""
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.get("/agents/by-name/{agent_name}", response_model=AgentResponse)
async def get_agent_by_name(
    agent_name: str,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """根据名称获取Agent信息"""
    agent = service.get_agent_by_name(agent_name)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """更新Agent信息"""
    agent = service.update_agent(agent_id, agent_data, updated_by=current_user.id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """删除Agent（软删除）"""
    success = service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")


# ==================== SystemPrompt管理接口 ====================

@router.get("/prompts", response_model=List[SystemPromptResponse])
async def list_prompts(
    agent_id: Optional[int] = Query(None, description="过滤Agent ID"),
    is_active: Optional[bool] = Query(None, description="过滤激活状态"),
    language: Optional[str] = Query(None, description="过滤语言"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(100, ge=1, le=1000, description="每页大小"),
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """
    获取Prompt列表
    
    支持多条件过滤和分页
    """
    try:
        return service.list_prompts(
            agent_id=agent_id,
            is_active=is_active,
            language=language,
            page=page,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/prompts", response_model=SystemPromptResponse, status_code=status.HTTP_201_CREATED)
@monitor_performance("create_prompt")
async def create_prompt(
    prompt: SystemPromptCreate,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """
    创建新的系统提示词
    
    - **agent_id**: 关联的Agent ID
    - **name**: Prompt名称
    - **content**: Prompt内容
    - **language**: 语言（zh-CN, en-US等）
    - **variables**: 变量定义
    - **meta_data**: 元数据
    - **is_default**: 是否为默认Prompt
    """
    try:
        return service.create_prompt(prompt, created_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/search", response_model=PromptSearchResponse)
async def search_prompts(
    agent_id: Optional[int] = Query(None, description="Agent ID"),
    status: Optional[str] = Query(None, description="Prompt状态"),
    language: Optional[str] = Query(None, description="语言"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """
    搜索Prompt
    
    支持多条件过滤和分页
    """
    search_request = PromptSearchRequest(
        agent_id=agent_id,
        status=status,
        language=language,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return service.search_prompts(search_request)


@router.get("/{prompt_id}", response_model=SystemPromptResponse)
async def get_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """获取指定Prompt信息"""
    prompt = service.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return prompt


@router.get("/agents/{agent_id}/active", response_model=SystemPromptResponse)
@monitor_performance("get_agent_active_prompt")
async def get_agent_active_prompt(
    agent_id: int,
    language: str = Query("zh-CN", description="语言"),
    use_cache: bool = Query(True, description="是否使用缓存"),
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """
    获取Agent的激活状态默认Prompt
    
    这是最常用的接口，用于获取Agent当前使用的Prompt
    """
    prompt = service.get_agent_prompt(agent_id, language, use_cache)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No active prompt found for agent {agent_id} with language {language}"
        )
    return prompt


@router.put("/{prompt_id}", response_model=SystemPromptResponse)
async def update_prompt(
    prompt_id: int,
    prompt_data: SystemPromptUpdate,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """更新Prompt"""
    prompt = service.update_prompt(prompt_id, prompt_data, updated_by=current_user.id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return prompt


@router.post("/{prompt_id}/activate", status_code=status.HTTP_200_OK)
async def activate_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """激活Prompt"""
    success = service.activate_prompt(prompt_id, activated_by=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return {"message": "Prompt activated successfully"}


@router.post("/{prompt_id}/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_prompt(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """停用Prompt"""
    success = service.deactivate_prompt(prompt_id, deactivated_by=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return {"message": "Prompt deactivated successfully"}


# ==================== 版本管理接口 ====================

@router.get("/{prompt_id}/versions", response_model=List[PromptVersionResponse])
async def get_prompt_versions(
    prompt_id: int,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """获取Prompt版本历史"""
    return service.get_prompt_versions(prompt_id)


@router.post("/{prompt_id}/rollback", response_model=SystemPromptResponse)
async def rollback_prompt(
    prompt_id: int,
    version: str = Query(..., description="目标版本号"),
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """回滚Prompt到指定版本"""
    try:
        prompt = service.rollback_prompt(prompt_id, version, rollback_by=current_user.id)
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
        return prompt
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== 高级版本管理 ====================

@router.post("/prompts/{prompt_id}/versions/tag")
async def create_version_tag(
    prompt_id: int,
    tag_name: str,
    description: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """为当前版本创建标签"""
    version_manager = VersionManager(db)
    success = version_manager.create_version_tag(
        prompt_id, tag_name, description, current_user.id
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to create version tag")
    return {"message": f"Version tag '{tag_name}' created successfully"}


@router.get("/prompts/{prompt_id}/versions/tagged", response_model=List[PromptVersionResponse])
async def get_tagged_versions(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有带标签的版本"""
    version_manager = VersionManager(db)
    return version_manager.get_tagged_versions(prompt_id)


@router.get("/prompts/{prompt_id}/versions/compare")
async def compare_versions(
    prompt_id: int,
    version_a: str,
    version_b: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """比较两个版本的差异"""
    version_manager = VersionManager(db)
    try:
        comparison = version_manager.compare_versions(prompt_id, version_a, version_b)
        return {
            "version_a": comparison.version_a,
            "version_b": comparison.version_b,
            "content_diff": comparison.content_diff,
            "variables_diff": comparison.variables_diff,
            "meta_data_diff": comparison.meta_data_diff,
            "similarity_score": comparison.similarity_score
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/prompts/{prompt_id}/versions/metrics")
async def get_version_metrics(
    prompt_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取各版本的性能指标"""
    version_manager = VersionManager(db)
    metrics = version_manager.get_version_metrics(prompt_id, days)
    return [
        {
            "version": m.version,
            "usage_count": m.usage_count,
            "avg_response_time": m.avg_response_time,
            "avg_user_feedback": m.avg_user_feedback,
            "error_rate": m.error_rate,
            "performance_score": m.performance_score
        }
        for m in metrics
    ]


@router.get("/prompts/{prompt_id}/versions/recommend")
async def recommend_best_version(
    prompt_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """推荐最佳版本"""
    version_manager = VersionManager(db)
    best_version = version_manager.suggest_best_version(prompt_id, days)
    if not best_version:
        raise HTTPException(status_code=404, detail="No suitable version found")
    return {"recommended_version": best_version}


@router.post("/prompts/{prompt_id}/versions/cleanup")
async def cleanup_old_versions(
    prompt_id: int,
    keep_count: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清理旧版本"""
    version_manager = VersionManager(db)
    deleted_count = version_manager.auto_cleanup_old_versions(prompt_id, keep_count)
    return {"message": f"Cleaned up {deleted_count} old versions"}


@router.get("/prompts/{prompt_id}/versions/export")
async def export_version_history(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出版本历史"""
    version_manager = VersionManager(db)
    try:
        export_data = version_manager.export_version_history(prompt_id)
        return export_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ==================== 使用统计接口 ====================

@router.post("/usage", response_model=PromptUsageStatsResponse, status_code=status.HTTP_201_CREATED)
async def record_prompt_usage(
    usage_data: PromptUsageCreate,
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """
    记录Prompt使用情况
    
    通常由AI Agent系统自动调用
    """
    return service.record_usage(usage_data)


@router.get("/{prompt_id}/analytics", response_model=PromptAnalytics)
async def get_prompt_analytics(
    prompt_id: int,
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """获取Prompt分析数据"""
    return service.get_prompt_analytics(prompt_id, days)


@router.get("/agents/{agent_id}/analytics", response_model=AgentAnalytics)
async def get_agent_analytics(
    agent_id: int,
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_user),
    service: PromptService = Depends(get_prompt_service)
):
    """获取Agent分析数据"""
    try:
        return service.get_agent_analytics(agent_id, days)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== 高级分析功能 ====================

@router.get("/analytics/usage-report")
async def get_usage_report(
    days: int = 30,
    agent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取使用情况报告"""
    analytics = PromptAnalytics(db)
    report = analytics.generate_usage_report(days, agent_id)
    return {
        "total_usage": report.total_usage,
        "unique_users": report.unique_users,
        "avg_response_time": report.avg_response_time,
        "success_rate": report.success_rate,
        "peak_usage_hour": report.peak_usage_hour,
        "most_active_agent": report.most_active_agent,
        "trend_direction": report.trend_direction
    }


@router.get("/analytics/performance/{prompt_id}")
async def get_performance_metrics(
    prompt_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取Prompt性能指标"""
    analytics = PromptAnalytics(db)
    metrics = analytics.get_performance_metrics(prompt_id, days)
    return {
        "response_time_p50": metrics.response_time_p50,
        "response_time_p95": metrics.response_time_p95,
        "response_time_p99": metrics.response_time_p99,
        "error_rate": metrics.error_rate,
        "timeout_rate": metrics.timeout_rate,
        "user_satisfaction": metrics.user_satisfaction
    }


@router.get("/analytics/effectiveness/{prompt_id}")
async def analyze_prompt_effectiveness(
    prompt_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """分析Prompt效果"""
    analytics = PromptAnalytics(db)
    try:
        analysis = analytics.analyze_prompt_effectiveness(prompt_id, days)
        return {
            "prompt_id": analysis.prompt_id,
            "prompt_name": analysis.prompt_name,
            "effectiveness_score": analysis.effectiveness_score,
            "user_feedback_avg": analysis.user_feedback_avg,
            "improvement_suggestions": analysis.improvement_suggestions,
            "comparison_with_previous": analysis.comparison_with_previous
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analytics/trends")
async def get_usage_trends(
    prompt_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取使用趋势数据"""
    analytics = PromptAnalytics(db)
    trends = analytics.get_usage_trends(prompt_id, agent_id, days)
    return [
        {
            "date": trend.date,
            "usage_count": trend.usage_count,
            "avg_response_time": trend.avg_response_time,
            "error_rate": trend.error_rate,
            "user_feedback": trend.user_feedback
        }
        for trend in trends
    ]


@router.get("/analytics/agent-comparison")
async def get_agent_comparison(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取Agent对比分析"""
    analytics = PromptAnalytics(db)
    comparison = analytics.get_agent_comparison(days)
    return comparison


@router.get("/analytics/insights")
async def get_insights(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取智能洞察"""
    analytics = PromptAnalytics(db)
    insights = analytics.generate_insights(days)
    return insights


@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分析仪表板数据"""
    analytics = PromptAnalytics(db)
    
    # 获取综合数据
    usage_report = analytics.generate_usage_report(days)
    agent_comparison = analytics.get_agent_comparison(days)
    insights = analytics.generate_insights(days)
    
    return {
        "overview": {
            "total_usage": usage_report.total_usage,
            "unique_users": usage_report.unique_users,
            "avg_response_time": usage_report.avg_response_time,
            "success_rate": usage_report.success_rate,
            "trend_direction": usage_report.trend_direction
        },
        "top_agents": agent_comparison[:5],
        "insights": insights,
        "period": f"{days} days",
        "generated_at": datetime.utcnow().isoformat()
    }


# ==================== 缓存管理接口 ====================

@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = Query(None, description="缓存类型: prompt, agent, analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清理缓存"""
    cache_manager = get_cache_manager(lambda: db)
    
    if cache_type == "prompt":
        cache_manager.prompt_cache.clear()
        return {"message": "Prompt cache cleared successfully"}
    elif cache_type == "agent":
        cache_manager.agent_cache.clear()
        return {"message": "Agent cache cleared successfully"}
    elif cache_type == "analytics":
        cache_manager.analytics_cache.clear()
        return {"message": "Analytics cache cleared successfully"}
    else:
        cache_manager.prompt_cache.clear()
        cache_manager.agent_cache.clear()
        cache_manager.analytics_cache.clear()
        return {"message": "All caches cleared successfully"}


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取缓存统计信息"""
    cache_manager = get_cache_manager(lambda: db)
    stats = cache_manager.get_cache_stats()
    return stats


@router.post("/cache/preload")
async def preload_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """预加载热点数据到缓存"""
    cache_manager = get_cache_manager(lambda: db)
    cache_manager.preload_hot_data()
    return {"message": "Cache preloaded successfully"}


@router.post("/cache/optimize")
async def optimize_cache(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """优化缓存性能"""
    cache_manager = get_cache_manager(lambda: db)
    result = cache_manager.optimize_cache()
    return result


# ==================== 性能监控接口 ====================

@router.get("/performance/summary")
async def get_performance_summary(
    current_user: User = Depends(get_current_user)
):
    """获取性能摘要"""
    monitor = get_performance_monitor()
    summary = monitor.get_performance_summary()
    return summary


@router.get("/performance/response-times")
async def get_response_times(
    endpoint: Optional[str] = Query(None, description="特定端点名称"),
    current_user: User = Depends(get_current_user)
):
    """获取API响应时间统计"""
    monitor = get_performance_monitor()
    stats = monitor.get_response_time_stats(endpoint)
    return stats


@router.get("/performance/system-resources")
async def get_system_resources(
    minutes: int = Query(60, description="获取最近N分钟的数据"),
    current_user: User = Depends(get_current_user)
):
    """获取系统资源使用情况"""
    monitor = get_performance_monitor()
    stats = monitor.get_system_stats(minutes)
    return {
        "timeframe_minutes": minutes,
        "data_points": len(stats),
        "stats": stats
    }


@router.get("/performance/metrics")
async def get_performance_metrics(
    name: Optional[str] = Query(None, description="指标名称"),
    minutes: int = Query(60, description="获取最近N分钟的数据"),
    current_user: User = Depends(get_current_user)
):
    """获取性能指标"""
    monitor = get_performance_monitor()
    metrics = monitor.get_metrics(name, minutes)
    return {
        "timeframe_minutes": minutes,
        "metric_name": name,
        "data_points": len(metrics),
        "metrics": metrics
    }


@router.post("/performance/clear-metrics")
async def clear_old_metrics(
    older_than_hours: int = Query(24, description="清理N小时前的指标"),
    current_user: User = Depends(get_current_user)
):
    """清理旧的性能指标"""
    monitor = get_performance_monitor()
    removed_count = monitor.clear_metrics(older_than_hours)
    return {
        "message": f"Cleared {removed_count} old metrics",
        "older_than_hours": older_than_hours
    }


@router.post("/performance/start-monitoring")
async def start_performance_monitoring(
    interval: int = Query(30, description="监控间隔（秒）"),
    current_user: User = Depends(get_current_user)
):
    """开始性能监控"""
    monitor = get_performance_monitor()
    await monitor.start_monitoring(interval)
    return {
        "message": "Performance monitoring started",
        "interval_seconds": interval
    }


@router.post("/performance/stop-monitoring")
async def stop_performance_monitoring(
    current_user: User = Depends(get_current_user)
):
    """停止性能监控"""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()
    return {"message": "Performance monitoring stopped"}


# ==================== 健康检查接口 ====================

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "prompt_management"
    }