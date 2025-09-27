from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import logging

import jwt
from passlib.context import CryptContext

from config.settings import get_settings

# 设置日志
logger = logging.getLogger(__name__)

# 使用更兼容的配置
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12
)

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)

def create_access_token(subject: str, extra_claims: Optional[dict[str, Any]] = None) -> str:
    settings = get_settings()
    expire_minutes = settings.jwt_access_token_expires_minutes
    # Use timezone-aware datetime to avoid system clock issues
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
    if extra_claims:
        payload.update(extra_claims)
    
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token

def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError as e:
        logger.error(f"Token has expired: {e}")
        raise
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        raise


