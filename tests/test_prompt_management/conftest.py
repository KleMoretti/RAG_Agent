"""
Pytest配置文件，提供测试fixtures
"""
import pytest
import asyncio
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.database import Base, get_db
from src.main import app
from src.api.models import Agent, SystemPrompt, PromptVersion, PromptUsageStats
from src.prompt_management.service import PromptService
from src.prompt_management.cache_manager import AdvancedCacheManager
from src.prompt_management.performance import PerformanceMonitor
from src.api.models import User


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def prompt_service(db_session):
    """创建PromptService实例"""
    return PromptService(db_session)


@pytest.fixture
def cache_manager():
    """创建缓存管理器实例"""
    return AdvancedCacheManager()


@pytest.fixture
def performance_monitor():
    """创建性能监控器实例"""
    return PerformanceMonitor()


@pytest.fixture
def sample_user(db_session):
    """创建测试用户"""
    user = User(
        id=1,
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_agent(db_session):
    """创建测试Agent"""
    agent = Agent(
        name="测试智能体",
        description="用于测试的智能体",
        agent_type="chat",
        capabilities=["对话", "问答"],
        is_active=True,
        created_by=1
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)
    return agent


@pytest.fixture
def sample_prompt(db_session, sample_agent):
    """创建测试SystemPrompt"""
    prompt = SystemPrompt(
        agent_id=sample_agent.id,
        name="测试提示词",
        content="你是一个测试助手，请回答用户的问题。",
        language="zh-CN",
        variables=["user_name", "context"],
        is_active=True,
        created_by=1
    )
    db_session.add(prompt)
    db_session.commit()
    db_session.refresh(prompt)
    return prompt


@pytest.fixture
def sample_prompt_version(db_session, sample_prompt):
    """创建测试PromptVersion"""
    version = PromptVersion(
        prompt_id=sample_prompt.id,
        version="1.0.0",
        content="你是一个测试助手，请回答用户的问题。",
        variables=["user_name", "context"],
        change_description="初始版本",
        created_by=1
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(version)
    return version


@pytest.fixture
def sample_usage_stats(db_session, sample_prompt):
    """创建测试PromptUsageStats"""
    stats = PromptUsageStats(
        prompt_id=sample_prompt.id,
        usage_count=10,
        avg_response_time=1.5,
        success_rate=0.95,
        user_feedback_score=4.2,
        last_used=datetime.utcnow()
    )
    db_session.add(stats)
    db_session.commit()
    db_session.refresh(stats)
    return stats