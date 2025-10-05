from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import String, BigInteger, DateTime, Boolean, Text, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.db import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default=UserRole.USER, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_upload: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_download: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_chat: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)  # 创建者ID
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)  # 备注信息


class AgentType(str, Enum):
    """AI Agent类型枚举"""
    GENERAL = "general"  # 通用助手
    PROCESS = "process"  # 工艺专家
    EQUIPMENT = "equipment"  # 设备维护专家
    MARKET = "market"  # 市场分析师
    ENVIRONMENT = "environment"  # 环保专家
    QUALITY = "quality"  # 质量控制专家
    SAFETY = "safety"  # 安全专家
    CUSTOM = "custom"  # 自定义Agent


class PromptStatus(str, Enum):
    """Prompt状态枚举"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 激活
    DEPRECATED = "deprecated"  # 已弃用
    ARCHIVED = "archived"  # 已归档


class Agent(Base):
    """AI Agent定义表"""
    __tablename__ = "agent"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)  # 显示名称
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # Agent描述
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 图标名称
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)  # 主题色
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    capabilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Agent能力描述
    use_cases: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 使用场景
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 标签
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)

    # 关系
    prompts: Mapped[list["SystemPrompt"]] = relationship("SystemPrompt", back_populates="agent")
    usage_stats: Mapped[list["PromptUsageStats"]] = relationship("PromptUsageStats", back_populates="agent")


class SystemPrompt(Base):
    """系统提示词模型"""
    __tablename__ = "system_prompt"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("agent.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)  # Prompt名称
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Prompt内容
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")  # 版本号
    status: Mapped[str] = mapped_column(String(32), default=PromptStatus.DRAFT, nullable=False, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否为默认Prompt
    language: Mapped[str] = mapped_column(String(8), default="zh-CN", nullable=False)  # 语言
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 变量定义
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 元数据
    performance_score: Mapped[float | None] = mapped_column(nullable=True)  # 性能评分
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 使用次数
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="prompts")
    usage_stats: Mapped[list["PromptUsageStats"]] = relationship("PromptUsageStats", back_populates="prompt")
    versions: Mapped[list["PromptVersion"]] = relationship("PromptVersion", back_populates="prompt")

    # 索引
    __table_args__ = (
        Index("idx_agent_status", "agent_id", "status"),
        Index("idx_agent_default", "agent_id", "is_default"),
        {'extend_existing': True}
    )


class PromptVersion(Base):
    """Prompt版本历史表"""
    __tablename__ = "prompt_version"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prompt_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("system_prompt.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)  # 版本号
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 历史内容
    change_log: Mapped[str | None] = mapped_column(Text, nullable=True)  # 变更日志
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 历史变量定义
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 历史元数据
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)

    # 关系
    prompt: Mapped["SystemPrompt"] = relationship("SystemPrompt", back_populates="versions")

    # 索引
    __table_args__ = (
        Index("idx_prompt_version", "prompt_id", "version"),
        {'extend_existing': True}
    )


class PromptUsageStats(Base):
    """Prompt使用统计表"""
    __tablename__ = "prompt_usage_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("agent.id"), nullable=False, index=True)
    prompt_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("system_prompt.id"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True, index=True)
    session_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)  # 会话ID
    usage_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 响应时间(毫秒)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Token数量
    user_feedback: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 用户反馈评分(1-5)
    error_occurred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否发生错误
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)  # 错误信息
    context_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 上下文数据

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="usage_stats")
    prompt: Mapped["SystemPrompt"] = relationship("SystemPrompt", back_populates="usage_stats")

    # 索引
    __table_args__ = (
        Index("idx_usage_date", "usage_date"),
        Index("idx_agent_date", "agent_id", "usage_date"),
        Index("idx_prompt_date", "prompt_id", "usage_date"),
        {'extend_existing': True}
    )


