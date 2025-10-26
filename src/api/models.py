from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    String,
    BigInteger,
    DateTime,
    Boolean,
    Text,
    Integer,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.db import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIAN = "technician"
    USER = "user"


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(
        String(32), default=UserRole.USER, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_upload: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_download: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_chat: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_access_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )  # 创建者ID
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
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    agent_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)  # 显示名称
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # Agent描述
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 图标名称
    color: Mapped[str | None] = mapped_column(String(16), nullable=True)  # 主题色
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    capabilities: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Agent能力描述
    use_cases: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 使用场景
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 标签
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    prompts: Mapped[list["SystemPrompt"]] = relationship(
        "SystemPrompt", back_populates="agent"
    )
    usage_stats: Mapped[list["PromptUsageStats"]] = relationship(
        "PromptUsageStats", back_populates="agent"
    )
    preset_questions: Mapped[list["AgentPresetQuestion"]] = relationship(
        "AgentPresetQuestion", back_populates="agent"
    )


class SystemPrompt(Base):
    """系统提示词模型"""

    __tablename__ = "system_prompt"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("agent.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)  # Prompt名称
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Prompt内容
    version: Mapped[str] = mapped_column(
        String(32), nullable=False, default="1.0.0"
    )  # 版本号
    status: Mapped[str] = mapped_column(
        String(32), default=PromptStatus.DRAFT, nullable=False, index=True
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # 是否为默认Prompt
    language: Mapped[str] = mapped_column(
        String(8), default="zh-CN", nullable=False
    )  # 语言
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 变量定义
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 元数据
    performance_score: Mapped[float | None] = mapped_column(nullable=True)  # 性能评分
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # 使用次数
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="prompts")
    usage_stats: Mapped[list["PromptUsageStats"]] = relationship(
        "PromptUsageStats", back_populates="prompt"
    )
    versions: Mapped[list["PromptVersion"]] = relationship(
        "PromptVersion", back_populates="prompt"
    )

    # 索引
    __table_args__ = (
        Index("idx_agent_status", "agent_id", "status"),
        Index("idx_agent_default", "agent_id", "is_default"),
        {"extend_existing": True},
    )


class PromptVersion(Base):
    """Prompt版本历史表"""

    __tablename__ = "prompt_version"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    prompt_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("system_prompt.id"), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)  # 版本号
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 历史内容
    change_log: Mapped[str | None] = mapped_column(Text, nullable=True)  # 变更日志
    variables: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 历史变量定义
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 历史元数据
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    prompt: Mapped["SystemPrompt"] = relationship(
        "SystemPrompt", back_populates="versions"
    )

    # 索引
    __table_args__ = (
        Index("idx_prompt_version", "prompt_id", "version"),
        {"extend_existing": True},
    )


class PromptUsageStats(Base):
    """Prompt使用统计表"""

    __tablename__ = "prompt_usage_stats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("agent.id"), nullable=False, index=True
    )
    prompt_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("system_prompt.id"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True, index=True
    )
    session_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True
    )  # 会话ID
    usage_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    response_time_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 响应时间(毫秒)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Token数量
    user_feedback: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 用户反馈评分(1-5)
    error_occurred: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # 是否发生错误
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)  # 错误信息
    context_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 上下文数据

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="usage_stats")
    prompt: Mapped["SystemPrompt"] = relationship(
        "SystemPrompt", back_populates="usage_stats"
    )

    # 索引
    __table_args__ = (
        Index("idx_usage_date", "usage_date"),
        Index("idx_agent_date", "agent_id", "usage_date"),
        Index("idx_prompt_date", "prompt_id", "usage_date"),
        {"extend_existing": True},
    )


class AgentPresetQuestion(Base):
    """Agent预设问题模型"""

    __tablename__ = "agent_preset_question"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("agent.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)  # 问题标题
    question: Mapped[str] = mapped_column(Text, nullable=False)  # 问题内容
    category: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )  # 问题分类
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )  # 显示顺序
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )  # 是否激活
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # 使用次数
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # 标签
    difficulty_level: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )  # 难度级别: basic, intermediate, advanced
    expected_response_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # 期望响应类型
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 元数据
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="preset_questions")

    # 索引
    __table_args__ = (
        Index("idx_agent_order", "agent_id", "order_index"),
        Index("idx_agent_active", "agent_id", "is_active"),
        Index("idx_category", "category"),
        {"extend_existing": True},
    )


class Vocabulary(Base):
    """专业词汇表"""

    __tablename__ = "vocabulary"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    term: Mapped[str] = mapped_column(
        String(128), nullable=False, index=True
    )  # 词汇术语
    definition: Mapped[str] = mapped_column(Text, nullable=False)  # 定义
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # 分类
    synonyms: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # 同义词
    related_terms: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )  # 相关词汇
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 索引
    __table_args__ = (
        Index("idx_term_category", "term", "category"),
        {"extend_existing": True},
    )


class MaterialCategory(str, Enum):
    """原料分类枚举"""
    
    IRON_ORE = "iron_ore"  # 铁矿石
    COAL = "coal"  # 煤炭
    COKE = "coke"  # 焦炭
    SCRAP = "scrap"  # 废钢
    ALLOY = "alloy"  # 合金
    OTHER = "other"  # 其他


class ProductCategory(str, Enum):
    """产品分类枚举"""
    
    REBAR = "rebar"  # 螺纹钢
    HOT_ROLLED = "hot_rolled"  # 热轧卷板
    COLD_ROLLED = "cold_rolled"  # 冷轧卷板
    PLATE = "plate"  # 中厚板
    WIRE = "wire"  # 线材
    OTHER = "other"  # 其他


class MarketPriceData(Base):
    """市场价格数据表"""

    __tablename__ = "market_price_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    material_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # 材料类型（铁矿石、螺纹钢等）
    category: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # 分类（raw_material/product）
    price: Mapped[float] = mapped_column(nullable=False)  # 价格（元/吨）
    unit: Mapped[str] = mapped_column(String(16), default="元/吨", nullable=False)  # 单位
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 地区
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)  # 数据来源
    price_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )  # 价格日期
    change_rate: Mapped[float | None] = mapped_column(nullable=True)  # 涨跌幅（%）
    change_amount: Mapped[float | None] = mapped_column(nullable=True)  # 涨跌金额
    volume: Mapped[float | None] = mapped_column(nullable=True)  # 成交量（吨）
    high_price: Mapped[float | None] = mapped_column(nullable=True)  # 最高价
    low_price: Mapped[float | None] = mapped_column(nullable=True)  # 最低价
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他元数据
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 索引
    __table_args__ = (
        Index("idx_material_date", "material_type", "price_date"),
        Index("idx_category_date", "category", "price_date"),
        Index("idx_date", "price_date"),
        {"extend_existing": True},
    )


class MarketNews(Base):
    """市场新闻资讯表"""

    __tablename__ = "market_news"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)  # 新闻标题
    content: Mapped[str | None] = mapped_column(Text, nullable=True)  # 新闻内容
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)  # 摘要
    source: Mapped[str] = mapped_column(String(128), nullable=False)  # 来源
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # 分类（供应/需求/政策等）
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)  # 原文链接
    publish_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )  # 发布时间
    sentiment: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )  # 情绪（positive/negative/neutral）
    keywords: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # 关键词
    related_materials: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )  # 相关材料
    is_important: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # 是否重要
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他元数据
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 索引
    __table_args__ = (
        Index("idx_category_time", "category", "publish_time"),
        Index("idx_publish_time", "publish_time"),
        {"extend_existing": True},
    )


class MarketDataSource(Base):
    """市场数据源配置表"""

    __tablename__ = "market_data_source"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False
    )  # 数据源名称
    source_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # 类型（api/upload/manual）
    api_url: Mapped[str | None] = mapped_column(String(512), nullable=True)  # API地址
    api_key: Mapped[str | None] = mapped_column(String(256), nullable=True)  # API密钥
    headers: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 请求头
    params: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 请求参数
    data_format: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # 数据格式（json/xml/csv）
    update_frequency: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 更新频率（分钟）
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_update: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )  # 最后更新时间
    error_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )  # 错误次数
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 描述
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他配置
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 索引
    __table_args__ = (
        Index("idx_source_type", "source_type"),
        Index("idx_is_active", "is_active"),
        {"extend_existing": True},
    )


class Equipment(Base):
    """设备信息表"""

    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    equipment_type: Mapped[str] = mapped_column(String(64), nullable=False)  # 设备类型
    location: Mapped[str] = mapped_column(String(128), nullable=False)  # 位置
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 描述
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # 是否激活
    installation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 安装日期
    last_maintenance: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 上次维护日期
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他元数据
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    sensor_data: Mapped[list["SensorData"]] = relationship("SensorData", back_populates="equipment")
    fault_predictions: Mapped[list["FaultPrediction"]] = relationship("FaultPrediction", back_populates="equipment")

    # 索引
    __table_args__ = (
        Index("idx_equipment_type", "equipment_type"),
        Index("idx_location", "location"),
        Index("idx_is_active", "is_active"),
        {"extend_existing": True},
    )


class SensorData(Base):
    """传感器数据表"""

    __tablename__ = "sensor_data"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("equipment.id"), nullable=False, index=True
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=False)  # 温度
    pressure: Mapped[float] = mapped_column(Float, nullable=False)  # 压力
    vibration: Mapped[float] = mapped_column(Float, nullable=False)  # 振动
    humidity: Mapped[float] = mapped_column(Float, nullable=False)  # 湿度
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)  # 记录时间
    is_faulty: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # 是否故障
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他元数据
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="sensor_data")

    # 索引
    __table_args__ = (
        Index("idx_equipment_recorded", "equipment_id", "recorded_at"),
        {"extend_existing": True},
    )


class FaultPrediction(Base):
    """故障预测表"""

    __tablename__ = "fault_prediction"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("equipment.id"), nullable=False, index=True
    )
    fault_probability: Mapped[float] = mapped_column(Float, nullable=False)  # 故障概率
    predicted_fault_type: Mapped[str | None] = mapped_column(String(128), nullable=True)  # 预测故障类型
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)  # 模型版本
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 置信度
    predicted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)  # 预测时间
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否确认
    actual_fault_type: Mapped[str | None] = mapped_column(String(128), nullable=True)  # 实际故障类型
    meta_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他元数据
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 关系
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="fault_predictions")

    # 索引
    __table_args__ = (
        Index("idx_equipment_predicted", "equipment_id", "predicted_at"),
        Index("idx_model_version", "model_version"),
        {"extend_existing": True},
    )


class MLModel(Base):
    """机器学习模型表"""

    __tablename__ = "ml_model"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)  # 模型名称
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)  # 模型版本
    model_type: Mapped[str] = mapped_column(String(32), nullable=False)  # 模型类型
    model_path: Mapped[str] = mapped_column(String(512), nullable=False)  # 模型路径
    training_samples: Mapped[int] = mapped_column(Integer, nullable=False)  # 训练样本数
    test_samples: Mapped[int] = mapped_column(Integer, nullable=False)  # 测试样本数
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)  # 准确率
    precision: Mapped[float] = mapped_column(Float, nullable=False)  # 精确率
    recall: Mapped[float] = mapped_column(Float, nullable=False)  # 召回率
    f1_score: Mapped[float] = mapped_column(Float, nullable=False)  # F1分数
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 其他指标
    feature_importance: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 特征重要性
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否激活
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 描述
    trained_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)  # 训练时间
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("user.id"), nullable=True
    )

    # 索引
    __table_args__ = (
        Index("idx_model_type_version", "model_type", "model_version"),
        Index("idx_is_active", "is_active"),
        {"extend_existing": True},
    )