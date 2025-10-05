"""
Prompt管理核心业务逻辑服务
"""
from __future__ import annotations

import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from src.api.models import Agent, SystemPrompt, PromptVersion, PromptUsageStats, PromptStatus, AgentType
from .schemas import (
    AgentCreate, AgentUpdate, AgentResponse,
    SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse,
    PromptVersionResponse, PromptUsageStatsResponse, PromptUsageCreate,
    PromptAnalytics, AgentAnalytics, PromptSearchRequest, PromptSearchResponse
)
from .cache import get_prompt_cache, get_default_prompt_template
from .cache_manager import get_cache_manager, AdvancedCacheManager
from config.logging_config import setup_logging

logger = setup_logging()


class PromptService:
    """Prompt管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = get_prompt_cache()
        self.cache_manager = get_cache_manager(lambda: db)
    
    # ==================== Agent管理 ====================
    
    def create_agent(self, agent_data: AgentCreate, created_by: Optional[int] = None) -> AgentResponse:
        """
        创建新的AI Agent
        
        Args:
            agent_data: Agent创建数据
            created_by: 创建者ID
            
        Returns:
            创建的Agent信息
            
        Raises:
            ValueError: 当Agent名称已存在时
        """
        # 检查名称是否已存在
        existing = self.db.query(Agent).filter(Agent.name == agent_data.name).first()
        if existing:
            raise ValueError(f"Agent with name '{agent_data.name}' already exists")
        
        # 验证agent_type
        if agent_data.agent_type not in [e.value for e in AgentType]:
            raise ValueError(f"Invalid agent_type: {agent_data.agent_type}")
        
        # 创建Agent
        agent = Agent(
            **agent_data.model_dump(),
            created_by=created_by
        )
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        # 创建默认prompt
        self._create_default_prompt(agent.id, agent.agent_type, created_by)
        
        logger.info(f"Created agent: {agent.name} (ID: {agent.id})")
        return AgentResponse.model_validate(agent)
    
    def get_agent(self, agent_id: int) -> Optional[AgentResponse]:
        """获取单个Agent（带缓存）"""
        # 先从缓存获取
        cached_agent = self.cache_manager.get_agent(agent_id)
        if cached_agent:
            return AgentResponse(**cached_agent)
        
        # 缓存未命中，从数据库获取
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            return AgentResponse.model_validate(agent)
        return None
    
    def get_agent_by_name(self, name: str) -> Optional[AgentResponse]:
        """根据名称获取Agent信息"""
        agent = self.db.query(Agent).filter(Agent.name == name).first()
        if agent:
            return AgentResponse.model_validate(agent)
        return None
    
    def list_agents(self, is_active: Optional[bool] = None, 
                   agent_type: Optional[str] = None,
                   skip: int = 0, limit: int = 100) -> List[AgentResponse]:
        """获取Agent列表"""
        query = self.db.query(Agent)
        
        if is_active is not None:
            query = query.filter(Agent.is_active == is_active)
        
        if agent_type:
            query = query.filter(Agent.agent_type == agent_type)
        
        agents = query.order_by(Agent.created_at.desc()).offset(skip).limit(limit).all()
        return [AgentResponse.model_validate(agent) for agent in agents]
    
    def update_agent(self, agent_id: int, agent_data: AgentUpdate, 
                    updated_by: Optional[int] = None) -> Optional[AgentResponse]:
        """更新Agent信息"""
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None
        
        # 更新字段
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(agent)
        
        # 使缓存失效
        self.cache_manager.invalidate_agent(agent_id)
        
        logger.info(f"Updated agent: {agent.name} (ID: {agent.id})")
        return AgentResponse.model_validate(agent)
    
    def delete_agent(self, agent_id: int) -> bool:
        """删除Agent（软删除，设置为非激活状态）"""
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return False
        
        agent.is_active = False
        agent.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # 使缓存失效
        self.cache_manager.invalidate_agent(agent_id)
        
        logger.info(f"Deactivated agent: {agent.name} (ID: {agent.id})")
        return True
    
    # ==================== SystemPrompt管理 ====================
    
    def create_prompt(self, prompt_data: SystemPromptCreate, 
                     created_by: Optional[int] = None) -> SystemPromptResponse:
        """
        创建新的系统提示词
        
        Args:
            prompt_data: Prompt创建数据
            created_by: 创建者ID
            
        Returns:
            创建的Prompt信息
        """
        # 验证Agent是否存在
        agent = self.db.query(Agent).filter(Agent.id == prompt_data.agent_id).first()
        if not agent:
            raise ValueError(f"Agent with ID {prompt_data.agent_id} not found")
        
        # 如果设置为默认，先取消其他默认prompt
        if prompt_data.is_default:
            self._unset_default_prompts(prompt_data.agent_id, prompt_data.language)
        
        # 创建Prompt
        prompt = SystemPrompt(
            **prompt_data.model_dump(),
            status=PromptStatus.DRAFT,
            created_by=created_by
        )
        
        self.db.add(prompt)
        self.db.commit()
        self.db.refresh(prompt)
        
        # 创建版本记录
        self._create_version_record(prompt, "Initial version", created_by)
        
        logger.info(f"Created prompt: {prompt.name} (ID: {prompt.id}) for agent {prompt_data.agent_id}")
        return SystemPromptResponse.model_validate(prompt)
    
    def get_prompt(self, prompt_id: int) -> Optional[SystemPromptResponse]:
        """获取Prompt信息"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if prompt:
            return SystemPromptResponse.model_validate(prompt)
        return None
    
    def get_agent_prompt(self, agent_id: int, language: str = "zh-CN", 
                        use_cache: bool = True) -> Optional[SystemPromptResponse]:
        """
        获取Agent的激活状态的默认Prompt
        
        Args:
            agent_id: Agent ID
            language: 语言
            use_cache: 是否使用缓存
            
        Returns:
            Prompt信息或None
        """
        # 尝试从缓存获取
        if use_cache:
            cached_data = self.cache.get(agent_id, language, "active")
            if cached_data:
                return SystemPromptResponse.model_validate(cached_data)
        
        # 从数据库查询
        prompt = self.db.query(SystemPrompt).filter(
            and_(
                SystemPrompt.agent_id == agent_id,
                SystemPrompt.language == language,
                SystemPrompt.status == PromptStatus.ACTIVE,
                SystemPrompt.is_default == True
            )
        ).first()
        
        if prompt:
            prompt_data = SystemPromptResponse.model_validate(prompt)
            
            # 更新缓存
            if use_cache:
                self.cache.set(agent_id, prompt_data.model_dump(), language, "active")
            
            return prompt_data
        
        return None
    
    def search_prompts(self, search_request: PromptSearchRequest) -> PromptSearchResponse:
        """搜索Prompt"""
        query = self.db.query(SystemPrompt)
        
        # 应用过滤条件
        if search_request.agent_id:
            query = query.filter(SystemPrompt.agent_id == search_request.agent_id)
        
        if search_request.status:
            query = query.filter(SystemPrompt.status == search_request.status)
        
        if search_request.language:
            query = query.filter(SystemPrompt.language == search_request.language)
        
        if search_request.keyword:
            keyword = f"%{search_request.keyword}%"
            query = query.filter(
                or_(
                    SystemPrompt.name.like(keyword),
                    SystemPrompt.content.like(keyword)
                )
            )
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (search_request.page - 1) * search_request.page_size
        prompts = query.order_by(desc(SystemPrompt.updated_at)).offset(offset).limit(search_request.page_size).all()
        
        # 计算总页数
        total_pages = (total + search_request.page_size - 1) // search_request.page_size
        
        return PromptSearchResponse(
            items=[SystemPromptResponse.model_validate(p) for p in prompts],
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )
    
    def update_prompt(self, prompt_id: int, prompt_data: SystemPromptUpdate, 
                     updated_by: Optional[int] = None) -> Optional[SystemPromptResponse]:
        """更新Prompt"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return None
        
        # 保存旧版本
        old_content = prompt.content
        old_variables = prompt.variables
        old_metadata = prompt.meta_data
        
        # 更新字段
        update_data = prompt_data.model_dump(exclude_unset=True, exclude={"change_log"})
        
        # 如果设置为默认，先取消其他默认prompt
        if update_data.get("is_default"):
            self._unset_default_prompts(prompt.agent_id, prompt.language)
        
        for field, value in update_data.items():
            setattr(prompt, field, value)
        
        # 更新版本号
        prompt.version = self._increment_version(prompt.version)
        prompt.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(prompt)
        
        # 创建版本记录
        if old_content != prompt.content or old_variables != prompt.variables or old_metadata != prompt.meta_data:
            self._create_version_record(
                prompt, 
                prompt_data.change_log or "Updated prompt", 
                updated_by,
                old_content,
                old_variables,
                old_metadata
            )
        
        # 清理缓存
        self.cache.invalidate(prompt.agent_id, prompt.language)
        # 使相关缓存失效
        self.cache_manager.invalidate_prompt(prompt.agent_id, prompt.language)
        
        logger.info(f"Updated prompt: {prompt.name} (ID: {prompt.id})")
        return SystemPromptResponse.model_validate(prompt)
    
    def activate_prompt(self, prompt_id: int, activated_by: Optional[int] = None) -> bool:
        """激活Prompt"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return False
        
        prompt.status = PromptStatus.ACTIVE
        prompt.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # 清理缓存
        self.cache.invalidate(prompt.agent_id, prompt.language)
        # 使相关缓存失效
        self.cache_manager.invalidate_prompt(prompt.agent_id, prompt.language)
        
        logger.info(f"Activated prompt: {prompt.name} (ID: {prompt.id})")
        return True
    
    def deactivate_prompt(self, prompt_id: int, deactivated_by: Optional[int] = None) -> bool:
        """停用Prompt"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return False
        
        prompt.status = PromptStatus.DEPRECATED
        prompt.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        # 清理缓存
        self.cache.invalidate(prompt.agent_id, prompt.language)
        
        logger.info(f"Deactivated prompt: {prompt.name} (ID: {prompt.id})")
        return True
    
    # ==================== 版本管理 ====================
    
    def get_prompt_versions(self, prompt_id: int) -> List[PromptVersionResponse]:
        """获取Prompt版本历史"""
        versions = self.db.query(PromptVersion).filter(
            PromptVersion.prompt_id == prompt_id
        ).order_by(desc(PromptVersion.created_at)).all()
        
        return [PromptVersionResponse.model_validate(v) for v in versions]
    
    def rollback_prompt(self, prompt_id: int, version: str, 
                       rollback_by: Optional[int] = None) -> Optional[SystemPromptResponse]:
        """回滚Prompt到指定版本"""
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return None
        
        version_record = self.db.query(PromptVersion).filter(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version == version
            )
        ).first()
        
        if not version_record:
            raise ValueError(f"Version {version} not found for prompt {prompt_id}")
        
        # 保存当前版本
        self._create_version_record(prompt, f"Rollback to version {version}", rollback_by)
        
        # 回滚内容
        prompt.content = version_record.content
        prompt.variables = version_record.variables
        prompt.meta_data = version_record.meta_data
        prompt.version = self._increment_version(prompt.version)
        prompt.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(prompt)
        
        # 清理缓存
        self.cache.invalidate(prompt.agent_id, prompt.language)
        
        logger.info(f"Rolled back prompt {prompt_id} to version {version}")
        return SystemPromptResponse.model_validate(prompt)
    
    # ==================== 使用统计 ====================
    
    def record_usage(self, usage_data: PromptUsageCreate) -> PromptUsageStatsResponse:
        """记录Prompt使用情况"""
        usage = PromptUsageStats(**usage_data.model_dump())
        
        self.db.add(usage)
        
        # 更新prompt使用计数
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == usage_data.prompt_id).first()
        if prompt:
            prompt.usage_count += 1
        
        self.db.commit()
        self.db.refresh(usage)
        
        return PromptUsageStatsResponse.model_validate(usage)
    
    def get_prompt_analytics(self, prompt_id: int, days: int = 30) -> PromptAnalytics:
        """获取Prompt分析数据"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计
        stats = self.db.query(
            func.count(PromptUsageStats.id).label("total_usage"),
            func.avg(PromptUsageStats.response_time_ms).label("avg_response_time"),
            func.avg(PromptUsageStats.user_feedback).label("avg_feedback"),
            func.sum(func.case([(PromptUsageStats.error_occurred == True, 1)], else_=0)).label("error_count")
        ).filter(
            and_(
                PromptUsageStats.prompt_id == prompt_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).first()
        
        total_usage = stats.total_usage or 0
        error_rate = (stats.error_count or 0) / total_usage if total_usage > 0 else 0
        
        # 性能趋势（按天统计）
        trends = self.db.query(
            func.date(PromptUsageStats.usage_date).label("date"),
            func.count(PromptUsageStats.id).label("usage_count"),
            func.avg(PromptUsageStats.response_time_ms).label("avg_response_time")
        ).filter(
            and_(
                PromptUsageStats.prompt_id == prompt_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(func.date(PromptUsageStats.usage_date)).all()
        
        return PromptAnalytics(
            total_usage=total_usage,
            avg_response_time=stats.avg_response_time,
            avg_user_feedback=stats.avg_feedback,
            error_rate=error_rate,
            most_used_prompts=[],  # 这里可以扩展为相关prompt推荐
            performance_trends=[
                {
                    "date": str(trend.date),
                    "usage_count": trend.usage_count,
                    "avg_response_time": trend.avg_response_time
                }
                for trend in trends
            ]
        )
    
    def get_agent_analytics(self, agent_id: int, days: int = 30) -> AgentAnalytics:
        """获取Agent分析数据"""
        from datetime import timedelta
        
        agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 基础统计
        total_usage = self.db.query(func.count(PromptUsageStats.id)).filter(
            and_(
                PromptUsageStats.agent_id == agent_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).scalar() or 0
        
        active_prompts = self.db.query(func.count(SystemPrompt.id)).filter(
            and_(
                SystemPrompt.agent_id == agent_id,
                SystemPrompt.status == PromptStatus.ACTIVE
            )
        ).scalar() or 0
        
        avg_performance = self.db.query(func.avg(SystemPrompt.performance_score)).filter(
            SystemPrompt.agent_id == agent_id
        ).scalar()
        
        # 使用趋势
        usage_trends = self.db.query(
            func.date(PromptUsageStats.usage_date).label("date"),
            func.count(PromptUsageStats.id).label("usage_count")
        ).filter(
            and_(
                PromptUsageStats.agent_id == agent_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(func.date(PromptUsageStats.usage_date)).all()
        
        # 热门prompt
        top_prompts = self.db.query(
            SystemPrompt.id,
            SystemPrompt.name,
            func.count(PromptUsageStats.id).label("usage_count")
        ).join(PromptUsageStats).filter(
            and_(
                SystemPrompt.agent_id == agent_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).group_by(SystemPrompt.id, SystemPrompt.name).order_by(
            desc("usage_count")
        ).limit(5).all()
        
        return AgentAnalytics(
            agent_id=agent_id,
            agent_name=agent.name,
            total_usage=total_usage,
            active_prompts=active_prompts,
            avg_performance_score=avg_performance,
            usage_trend=[
                {"date": str(trend.date), "usage_count": trend.usage_count}
                for trend in usage_trends
            ],
            top_prompts=[
                {"id": p.id, "name": p.name, "usage_count": p.usage_count}
                for p in top_prompts
            ]
        )
    
    # ==================== 私有方法 ====================
    
    def _create_default_prompt(self, agent_id: int, agent_type: str, 
                              created_by: Optional[int] = None) -> None:
        """为新Agent创建默认prompt"""
        # 中文默认prompt
        zh_content = get_default_prompt_template(agent_type, "zh-CN")
        zh_prompt = SystemPrompt(
            agent_id=agent_id,
            name=f"默认{agent_type}提示词",
            content=zh_content,
            language="zh-CN",
            status=PromptStatus.ACTIVE,
            is_default=True,
            created_by=created_by
        )
        
        # 英文默认prompt
        en_content = get_default_prompt_template(agent_type, "en-US")
        en_prompt = SystemPrompt(
            agent_id=agent_id,
            name=f"Default {agent_type} Prompt",
            content=en_content,
            language="en-US",
            status=PromptStatus.ACTIVE,
            is_default=True,
            created_by=created_by
        )
        
        self.db.add_all([zh_prompt, en_prompt])
        self.db.commit()
        
        # 创建版本记录
        self.db.refresh(zh_prompt)
        self.db.refresh(en_prompt)
        self._create_version_record(zh_prompt, "Initial default prompt", created_by)
        self._create_version_record(en_prompt, "Initial default prompt", created_by)
    
    def _unset_default_prompts(self, agent_id: int, language: str) -> None:
        """取消指定Agent和语言的所有默认prompt"""
        self.db.query(SystemPrompt).filter(
            and_(
                SystemPrompt.agent_id == agent_id,
                SystemPrompt.language == language,
                SystemPrompt.is_default == True
            )
        ).update({"is_default": False})
    
    def _create_version_record(self, prompt: SystemPrompt, change_log: str, 
                              created_by: Optional[int] = None,
                              old_content: Optional[str] = None,
                              old_variables: Optional[Dict[str, Any]] = None,
                              old_metadata: Optional[Dict[str, Any]] = None) -> None:
        """创建版本记录"""
        version = PromptVersion(
            prompt_id=prompt.id,
            version=prompt.version,
            content=old_content or prompt.content,
            change_log=change_log,
            variables=old_variables or prompt.variables,
            metadata=old_metadata or prompt.meta_data,
            created_by=created_by
        )
        
        self.db.add(version)
        self.db.commit()
    
    def _increment_version(self, current_version: str) -> str:
        """递增版本号"""
        try:
            # 解析语义化版本号 (major.minor.patch)
            parts = current_version.split(".")
            if len(parts) == 3:
                major, minor, patch = map(int, parts)
                return f"{major}.{minor}.{patch + 1}"
            else:
                # 简单递增
                match = re.search(r'(\d+)$', current_version)
                if match:
                    num = int(match.group(1))
                    return current_version.replace(str(num), str(num + 1))
                else:
                    return f"{current_version}.1"
        except Exception:
            # 如果解析失败，添加时间戳
            return f"{current_version}.{int(datetime.utcnow().timestamp())}"