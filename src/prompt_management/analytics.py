"""
Prompt使用情况分析和效果追踪模块
提供详细的使用统计、性能分析和效果评估功能
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, text
from collections import defaultdict

from src.api.models import (
    Agent, SystemPrompt, PromptUsageStats, PromptVersion, 
    User, AgentType, PromptStatus
)
from config.logging_config import setup_logging

logger = setup_logging()


@dataclass
class UsageReport:
    """使用情况报告"""
    total_usage: int
    unique_users: int
    avg_response_time: float
    success_rate: float
    peak_usage_hour: int
    most_active_agent: str
    trend_direction: str  # "increasing", "decreasing", "stable"


@dataclass
class PerformanceMetrics:
    """性能指标"""
    response_time_p50: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    timeout_rate: float
    user_satisfaction: float


@dataclass
class EffectAnalysis:
    """效果分析"""
    prompt_id: int
    prompt_name: str
    effectiveness_score: float
    user_feedback_avg: float
    improvement_suggestions: List[str]
    comparison_with_previous: Dict[str, float]


@dataclass
class TrendData:
    """趋势数据"""
    date: str
    usage_count: int
    avg_response_time: float
    error_rate: float
    user_feedback: float


class PromptAnalytics:
    """Prompt分析引擎"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_usage_report(self, days: int = 30, agent_id: Optional[int] = None) -> UsageReport:
        """
        生成使用情况报告
        
        Args:
            days: 统计天数
            agent_id: 特定Agent ID（可选）
            
        Returns:
            使用情况报告
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础查询
        query = self.db.query(PromptUsageStats).filter(
            PromptUsageStats.usage_date >= start_date
        )
        
        if agent_id:
            query = query.filter(PromptUsageStats.agent_id == agent_id)
        
        usage_stats = query.all()
        
        if not usage_stats:
            return UsageReport(
                total_usage=0, unique_users=0, avg_response_time=0,
                success_rate=0, peak_usage_hour=0, most_active_agent="",
                trend_direction="stable"
            )
        
        # 计算基础指标
        total_usage = len(usage_stats)
        unique_users = len(set(stat.user_id for stat in usage_stats if stat.user_id))
        avg_response_time = sum(stat.response_time_ms for stat in usage_stats) / total_usage
        success_rate = (1 - sum(1 for stat in usage_stats if stat.error_occurred) / total_usage) * 100
        
        # 计算峰值使用时间
        hour_usage = defaultdict(int)
        for stat in usage_stats:
            if stat.usage_date:
                hour_usage[stat.usage_date.hour] += 1
        peak_usage_hour = max(hour_usage.items(), key=lambda x: x[1])[0] if hour_usage else 0
        
        # 找出最活跃的Agent
        agent_usage = defaultdict(int)
        for stat in usage_stats:
            if stat.agent_id:
                agent_usage[stat.agent_id] += 1
        
        most_active_agent = ""
        if agent_usage:
            most_active_agent_id = max(agent_usage.items(), key=lambda x: x[1])[0]
            agent = self.db.query(Agent).filter(Agent.id == most_active_agent_id).first()
            most_active_agent = agent.name if agent else f"Agent-{most_active_agent_id}"
        
        # 计算趋势方向
        trend_direction = self._calculate_trend_direction(usage_stats, days)
        
        return UsageReport(
            total_usage=total_usage,
            unique_users=unique_users,
            avg_response_time=round(avg_response_time, 2),
            success_rate=round(success_rate, 2),
            peak_usage_hour=peak_usage_hour,
            most_active_agent=most_active_agent,
            trend_direction=trend_direction
        )
    
    def get_performance_metrics(self, prompt_id: int, days: int = 30) -> PerformanceMetrics:
        """
        获取性能指标
        
        Args:
            prompt_id: Prompt ID
            days: 统计天数
            
        Returns:
            性能指标
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        usage_stats = self.db.query(PromptUsageStats).filter(
            and_(
                PromptUsageStats.prompt_id == prompt_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).all()
        
        if not usage_stats:
            return PerformanceMetrics(
                response_time_p50=0, response_time_p95=0, response_time_p99=0,
                error_rate=0, timeout_rate=0, user_satisfaction=0
            )
        
        # 响应时间分位数
        response_times = sorted([stat.response_time_ms for stat in usage_stats])
        total_count = len(response_times)
        
        p50_idx = int(total_count * 0.5)
        p95_idx = int(total_count * 0.95)
        p99_idx = int(total_count * 0.99)
        
        response_time_p50 = response_times[p50_idx] if p50_idx < total_count else 0
        response_time_p95 = response_times[p95_idx] if p95_idx < total_count else 0
        response_time_p99 = response_times[p99_idx] if p99_idx < total_count else 0
        
        # 错误率
        error_count = sum(1 for stat in usage_stats if stat.error_occurred)
        error_rate = (error_count / total_count) * 100
        
        # 超时率（假设超过5秒为超时）
        timeout_count = sum(1 for stat in usage_stats if stat.response_time_ms > 5000)
        timeout_rate = (timeout_count / total_count) * 100
        
        # 用户满意度
        feedback_scores = [stat.user_feedback for stat in usage_stats if stat.user_feedback is not None]
        user_satisfaction = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0
        
        return PerformanceMetrics(
            response_time_p50=round(response_time_p50, 2),
            response_time_p95=round(response_time_p95, 2),
            response_time_p99=round(response_time_p99, 2),
            error_rate=round(error_rate, 2),
            timeout_rate=round(timeout_rate, 2),
            user_satisfaction=round(user_satisfaction, 2)
        )
    
    def analyze_prompt_effectiveness(self, prompt_id: int, days: int = 30) -> EffectAnalysis:
        """
        分析Prompt效果
        
        Args:
            prompt_id: Prompt ID
            days: 统计天数
            
        Returns:
            效果分析结果
        """
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取当前期间的统计数据
        current_stats = self.db.query(PromptUsageStats).filter(
            and_(
                PromptUsageStats.prompt_id == prompt_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).all()
        
        # 获取前一个期间的统计数据用于对比
        previous_start = start_date - timedelta(days=days)
        previous_stats = self.db.query(PromptUsageStats).filter(
            and_(
                PromptUsageStats.prompt_id == prompt_id,
                PromptUsageStats.usage_date >= previous_start,
                PromptUsageStats.usage_date < start_date
            )
        ).all()
        
        # 计算当前期间指标
        current_metrics = self._calculate_period_metrics(current_stats)
        previous_metrics = self._calculate_period_metrics(previous_stats)
        
        # 计算效果分数 (0-100)
        effectiveness_score = self._calculate_effectiveness_score(current_metrics)
        
        # 用户反馈平均分
        feedback_scores = [stat.user_feedback for stat in current_stats if stat.user_feedback is not None]
        user_feedback_avg = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(current_metrics)
        
        # 与前期对比
        comparison_with_previous = {
            "response_time_change": ((current_metrics["avg_response_time"] - previous_metrics["avg_response_time"]) 
                                   / previous_metrics["avg_response_time"] * 100) if previous_metrics["avg_response_time"] > 0 else 0,
            "error_rate_change": current_metrics["error_rate"] - previous_metrics["error_rate"],
            "usage_change": ((current_metrics["usage_count"] - previous_metrics["usage_count"]) 
                           / previous_metrics["usage_count"] * 100) if previous_metrics["usage_count"] > 0 else 0,
            "satisfaction_change": current_metrics["user_satisfaction"] - previous_metrics["user_satisfaction"]
        }
        
        return EffectAnalysis(
            prompt_id=prompt_id,
            prompt_name=prompt.name,
            effectiveness_score=round(effectiveness_score, 2),
            user_feedback_avg=round(user_feedback_avg, 2),
            improvement_suggestions=improvement_suggestions,
            comparison_with_previous={k: round(v, 2) for k, v in comparison_with_previous.items()}
        )
    
    def get_usage_trends(self, prompt_id: Optional[int] = None, 
                        agent_id: Optional[int] = None, days: int = 30) -> List[TrendData]:
        """
        获取使用趋势数据
        
        Args:
            prompt_id: Prompt ID（可选）
            agent_id: Agent ID（可选）
            days: 统计天数
            
        Returns:
            趋势数据列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 构建查询
        query = self.db.query(
            func.date(PromptUsageStats.usage_date).label("date"),
            func.count(PromptUsageStats.id).label("usage_count"),
            func.avg(PromptUsageStats.response_time_ms).label("avg_response_time"),
            func.avg(func.case([(PromptUsageStats.error_occurred == True, 1)], else_=0)).label("error_rate"),
            func.avg(PromptUsageStats.user_feedback).label("user_feedback")
        ).filter(
            PromptUsageStats.usage_date >= start_date
        )
        
        if prompt_id:
            query = query.filter(PromptUsageStats.prompt_id == prompt_id)
        if agent_id:
            query = query.filter(PromptUsageStats.agent_id == agent_id)
        
        results = query.group_by(func.date(PromptUsageStats.usage_date)).order_by("date").all()
        
        trends = []
        for result in results:
            trends.append(TrendData(
                date=result.date.strftime("%Y-%m-%d") if result.date else "",
                usage_count=result.usage_count or 0,
                avg_response_time=round(result.avg_response_time or 0, 2),
                error_rate=round((result.error_rate or 0) * 100, 2),
                user_feedback=round(result.user_feedback or 0, 2)
            ))
        
        return trends
    
    def get_agent_comparison(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取Agent对比分析
        
        Args:
            days: 统计天数
            
        Returns:
            Agent对比数据
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取所有Agent的统计数据
        agent_stats = self.db.query(
            Agent.id,
            Agent.name,
            Agent.type,
            func.count(PromptUsageStats.id).label("usage_count"),
            func.avg(PromptUsageStats.response_time_ms).label("avg_response_time"),
            func.avg(func.case([(PromptUsageStats.error_occurred == True, 1)], else_=0)).label("error_rate"),
            func.avg(PromptUsageStats.user_feedback).label("user_feedback")
        ).outerjoin(
            PromptUsageStats,
            and_(
                PromptUsageStats.agent_id == Agent.id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(Agent.id, Agent.name, Agent.type).all()
        
        comparison_data = []
        for stat in agent_stats:
            comparison_data.append({
                "agent_id": stat.id,
                "agent_name": stat.name,
                "agent_type": stat.type.value if stat.type else "unknown",
                "usage_count": stat.usage_count or 0,
                "avg_response_time": round(stat.avg_response_time or 0, 2),
                "error_rate": round((stat.error_rate or 0) * 100, 2),
                "user_feedback": round(stat.user_feedback or 0, 2),
                "performance_score": self._calculate_agent_performance_score(
                    stat.avg_response_time or 0,
                    stat.error_rate or 0,
                    stat.user_feedback or 0,
                    stat.usage_count or 0
                )
            })
        
        # 按性能分数排序
        return sorted(comparison_data, key=lambda x: x["performance_score"], reverse=True)
    
    def generate_insights(self, days: int = 30) -> Dict[str, Any]:
        """
        生成智能洞察
        
        Args:
            days: 统计天数
            
        Returns:
            洞察报告
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取基础统计
        total_usage = self.db.query(PromptUsageStats).filter(
            PromptUsageStats.usage_date >= start_date
        ).count()
        
        if total_usage == 0:
            return {"message": "No usage data available for the specified period"}
        
        # 获取各种洞察
        insights = {
            "summary": {
                "total_usage": total_usage,
                "analysis_period": f"{days} days",
                "generated_at": datetime.utcnow().isoformat()
            },
            "top_performers": self._get_top_performing_prompts(days),
            "problem_areas": self._identify_problem_areas(days),
            "usage_patterns": self._analyze_usage_patterns(days),
            "recommendations": self._generate_recommendations(days)
        }
        
        return insights
    
    # ==================== 私有方法 ====================
    
    def _calculate_trend_direction(self, usage_stats: List[PromptUsageStats], days: int) -> str:
        """计算趋势方向"""
        if len(usage_stats) < 7:  # 数据不足
            return "stable"
        
        # 按日期分组
        daily_usage = defaultdict(int)
        for stat in usage_stats:
            if stat.usage_date:
                date_key = stat.usage_date.date()
                daily_usage[date_key] += 1
        
        # 计算前半期和后半期的平均使用量
        sorted_dates = sorted(daily_usage.keys())
        mid_point = len(sorted_dates) // 2
        
        first_half_avg = sum(daily_usage[date] for date in sorted_dates[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(daily_usage[date] for date in sorted_dates[mid_point:]) / (len(sorted_dates) - mid_point) if len(sorted_dates) > mid_point else 0
        
        if second_half_avg > first_half_avg * 1.1:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_period_metrics(self, stats: List[PromptUsageStats]) -> Dict[str, float]:
        """计算期间指标"""
        if not stats:
            return {
                "usage_count": 0,
                "avg_response_time": 0,
                "error_rate": 0,
                "user_satisfaction": 0
            }
        
        usage_count = len(stats)
        avg_response_time = sum(stat.response_time_ms for stat in stats) / usage_count
        error_rate = sum(1 for stat in stats if stat.error_occurred) / usage_count * 100
        
        feedback_scores = [stat.user_feedback for stat in stats if stat.user_feedback is not None]
        user_satisfaction = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0
        
        return {
            "usage_count": usage_count,
            "avg_response_time": avg_response_time,
            "error_rate": error_rate,
            "user_satisfaction": user_satisfaction
        }
    
    def _calculate_effectiveness_score(self, metrics: Dict[str, float]) -> float:
        """计算效果分数 (0-100)"""
        # 响应时间分数 (0-30分)
        time_score = max(0, 30 - (metrics["avg_response_time"] - 100) / 900 * 30)
        time_score = min(30, max(0, time_score))
        
        # 错误率分数 (0-30分)
        error_score = max(0, 30 - metrics["error_rate"])
        error_score = min(30, max(0, error_score))
        
        # 用户满意度分数 (0-40分)
        satisfaction_score = (metrics["user_satisfaction"] - 1) / 4 * 40 if metrics["user_satisfaction"] > 0 else 0
        satisfaction_score = min(40, max(0, satisfaction_score))
        
        return time_score + error_score + satisfaction_score
    
    def _generate_improvement_suggestions(self, metrics: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if metrics["avg_response_time"] > 1000:
            suggestions.append("响应时间较长，建议优化prompt内容或模型配置")
        
        if metrics["error_rate"] > 5:
            suggestions.append("错误率偏高，建议检查prompt格式和输入验证")
        
        if metrics["user_satisfaction"] < 3:
            suggestions.append("用户满意度较低，建议收集用户反馈并优化prompt内容")
        
        if metrics["usage_count"] < 10:
            suggestions.append("使用频率较低，建议推广或改进prompt可用性")
        
        if not suggestions:
            suggestions.append("当前表现良好，建议继续监控和优化")
        
        return suggestions
    
    def _calculate_agent_performance_score(self, avg_response_time: float, error_rate: float, 
                                         user_feedback: float, usage_count: int) -> float:
        """计算Agent性能分数"""
        # 响应时间分数
        time_score = max(0, 30 - (avg_response_time - 100) / 900 * 30)
        time_score = min(30, max(0, time_score))
        
        # 错误率分数
        error_score = max(0, 30 - error_rate * 30)
        error_score = min(30, max(0, error_score))
        
        # 用户反馈分数
        feedback_score = (user_feedback - 1) / 4 * 40 if user_feedback > 0 else 0
        feedback_score = min(40, max(0, feedback_score))
        
        # 使用量权重
        usage_weight = min(1.0, usage_count / 100)
        
        return (time_score + error_score + feedback_score) * usage_weight
    
    def _get_top_performing_prompts(self, days: int) -> List[Dict[str, Any]]:
        """获取表现最佳的Prompt"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        prompt_stats = self.db.query(
            SystemPrompt.id,
            SystemPrompt.name,
            func.count(PromptUsageStats.id).label("usage_count"),
            func.avg(PromptUsageStats.response_time_ms).label("avg_response_time"),
            func.avg(PromptUsageStats.user_feedback).label("user_feedback")
        ).join(
            PromptUsageStats,
            and_(
                PromptUsageStats.prompt_id == SystemPrompt.id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(SystemPrompt.id, SystemPrompt.name).having(
            func.count(PromptUsageStats.id) >= 5  # 至少5次使用
        ).all()
        
        top_prompts = []
        for stat in prompt_stats:
            score = self._calculate_effectiveness_score({
                "avg_response_time": stat.avg_response_time or 0,
                "error_rate": 0,  # 简化计算
                "user_satisfaction": stat.user_feedback or 0
            })
            
            top_prompts.append({
                "prompt_id": stat.id,
                "prompt_name": stat.name,
                "usage_count": stat.usage_count,
                "performance_score": round(score, 2)
            })
        
        return sorted(top_prompts, key=lambda x: x["performance_score"], reverse=True)[:5]
    
    def _identify_problem_areas(self, days: int) -> List[Dict[str, Any]]:
        """识别问题区域"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 查找高错误率的Prompt
        problem_prompts = self.db.query(
            SystemPrompt.id,
            SystemPrompt.name,
            func.count(PromptUsageStats.id).label("usage_count"),
            func.avg(func.case([(PromptUsageStats.error_occurred == True, 1)], else_=0)).label("error_rate")
        ).join(
            PromptUsageStats,
            and_(
                PromptUsageStats.prompt_id == SystemPrompt.id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(SystemPrompt.id, SystemPrompt.name).having(
            func.avg(func.case([(PromptUsageStats.error_occurred == True, 1)], else_=0)) > 0.1  # 错误率>10%
        ).all()
        
        problems = []
        for prompt in problem_prompts:
            problems.append({
                "prompt_id": prompt.id,
                "prompt_name": prompt.name,
                "error_rate": round((prompt.error_rate or 0) * 100, 2),
                "usage_count": prompt.usage_count,
                "issue_type": "high_error_rate"
            })
        
        return problems
    
    def _analyze_usage_patterns(self, days: int) -> Dict[str, Any]:
        """分析使用模式"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按小时统计使用量
        hourly_usage = self.db.query(
            func.extract('hour', PromptUsageStats.usage_date).label("hour"),
            func.count(PromptUsageStats.id).label("usage_count")
        ).filter(
            PromptUsageStats.usage_date >= start_date
        ).group_by(func.extract('hour', PromptUsageStats.usage_date)).all()
        
        # 按Agent类型统计
        agent_type_usage = self.db.query(
            Agent.type,
            func.count(PromptUsageStats.id).label("usage_count")
        ).join(
            PromptUsageStats,
            and_(
                PromptUsageStats.agent_id == Agent.id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(Agent.type).all()
        
        return {
            "peak_hours": [{"hour": h.hour, "usage": h.usage_count} for h in hourly_usage],
            "agent_type_distribution": [
                {"type": t.type.value if t.type else "unknown", "usage": t.usage_count} 
                for t in agent_type_usage
            ]
        }
    
    def _generate_recommendations(self, days: int) -> List[str]:
        """生成推荐建议"""
        recommendations = [
            "定期监控高频使用的Prompt性能",
            "对错误率高的Prompt进行优化",
            "收集更多用户反馈以改进Prompt质量",
            "考虑为热门Agent类型增加更多Prompt模板",
            "建立Prompt性能基准和告警机制"
        ]
        
        return recommendations