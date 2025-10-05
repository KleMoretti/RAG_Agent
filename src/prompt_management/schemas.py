"""
Pydantic schemas for prompt management API
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict


class AgentBase(BaseModel):
    """Agent基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="Agent唯一标识")
    agent_type: str = Field(..., description="Agent类型")
    display_name: str = Field(..., min_length=1, max_length=128, description="显示名称")
    description: Optional[str] = Field(None, description="Agent描述")
    icon: Optional[str] = Field(None, max_length=64, description="图标名称")
    color: Optional[str] = Field(None, max_length=16, description="主题色")
    is_active: bool = Field(True, description="是否激活")
    capabilities: Optional[Dict[str, Any]] = Field(None, description="Agent能力描述")
    use_cases: Optional[Dict[str, Any]] = Field(None, description="使用场景")
    tags: Optional[Dict[str, Any]] = Field(None, description="标签")


class AgentCreate(AgentBase):
    """创建Agent的请求模型"""
    pass


class AgentUpdate(BaseModel):
    """更新Agent的请求模型"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=64)
    color: Optional[str] = Field(None, max_length=16)
    is_active: Optional[bool] = None
    capabilities: Optional[Dict[str, Any]] = None
    use_cases: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    """Agent响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None


class SystemPromptBase(BaseModel):
    """SystemPrompt基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="Prompt名称")
    content: str = Field(..., min_length=1, description="Prompt内容")
    language: str = Field("zh-CN", description="语言")
    variables: Optional[Dict[str, Any]] = Field(None, description="变量定义")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="元数据")


class SystemPromptCreate(SystemPromptBase):
    """创建SystemPrompt的请求模型"""
    agent_id: int = Field(..., description="关联的Agent ID")
    is_default: bool = Field(False, description="是否为默认Prompt")


class SystemPromptUpdate(BaseModel):
    """更新SystemPrompt的请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    content: Optional[str] = Field(None, min_length=1)
    language: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    change_log: Optional[str] = Field(None, description="变更日志")


class SystemPromptResponse(SystemPromptBase):
    """SystemPrompt响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    agent_id: int
    version: str
    status: str
    is_default: bool
    performance_score: Optional[float] = None
    usage_count: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None


class PromptVersionResponse(BaseModel):
    """Prompt版本响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    prompt_id: int
    version: str
    content: str
    change_log: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    created_by: Optional[int] = None


class PromptUsageStatsResponse(BaseModel):
    """Prompt使用统计响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    agent_id: int
    prompt_id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    usage_date: datetime
    response_time_ms: Optional[int] = None
    token_count: Optional[int] = None
    user_feedback: Optional[int] = None
    error_occurred: bool
    error_message: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class PromptUsageCreate(BaseModel):
    """创建使用统计的请求模型"""
    agent_id: int
    prompt_id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    response_time_ms: Optional[int] = None
    token_count: Optional[int] = None
    user_feedback: Optional[int] = Field(None, ge=1, le=5, description="用户反馈评分(1-5)")
    error_occurred: bool = False
    error_message: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None


class PromptAnalytics(BaseModel):
    """Prompt分析数据模型"""
    total_usage: int
    avg_response_time: Optional[float] = None
    avg_user_feedback: Optional[float] = None
    error_rate: float
    most_used_prompts: List[Dict[str, Any]]
    performance_trends: List[Dict[str, Any]]


class AgentAnalytics(BaseModel):
    """Agent分析数据模型"""
    agent_id: int
    agent_name: str
    total_usage: int
    active_prompts: int
    avg_performance_score: Optional[float] = None
    usage_trend: List[Dict[str, Any]]
    top_prompts: List[Dict[str, Any]]


class PromptSearchRequest(BaseModel):
    """Prompt搜索请求模型"""
    agent_id: Optional[int] = None
    status: Optional[str] = None
    language: Optional[str] = None
    keyword: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PromptSearchResponse(BaseModel):
    """Prompt搜索响应模型"""
    items: List[SystemPromptResponse]
    total: int
    page: int
    page_size: int
    total_pages: int