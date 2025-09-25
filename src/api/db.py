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
    _create_engine_url(), pool_pre_ping=True, pool_recycle=3600, echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


