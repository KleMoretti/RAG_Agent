from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config.settings import get_settings


class Base(DeclarativeBase):
    pass


def _create_engine_url() -> str:
    settings = get_settings()
    return settings.database_url


engine = create_engine(
    _create_engine_url(), 
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,   # 1小时后回收连接
    echo=False,
    # 连接池配置
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接数
    pool_timeout=30,     # 获取连接的超时时间
    # 连接参数
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        # 连接超时设置
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


