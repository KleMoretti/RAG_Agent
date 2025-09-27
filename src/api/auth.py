from __future__ import annotations

from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

from src.api.db import get_db, engine, Base
from src.api.models import User
from src.api.security import verify_password, hash_password, create_access_token, decode_token

# 设置日志
logger = logging.getLogger(__name__)

# Ensure tables are created (for demo/dev); in prod use migrations
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=64)
    role: constr(min_length=2, max_length=32) | None = None

class LoginRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=64)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: int
    username: str
    role: str

@router.post("/register", response_model=MeResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Registration attempt for username: {req.username}")
        
        existing = db.query(User).filter(User.username == req.username).first()
        if existing is not None:
            logger.warning(f"Username already exists: {req.username}")
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建用户
        user = User(
            username=req.username,
            password_hash=hash_password(req.password),
            role=(req.role or "user"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User registered successfully: {req.username}")
        return MeResponse(id=user.id, username=user.username, role=user.role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Login attempt for username: {req.username}")
        
        user = db.query(User).filter(User.username == req.username).first()
        if user is None:
            logger.warning(f"User not found: {req.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        
        if not verify_password(req.password, user.password_hash):
            logger.warning(f"Invalid password for user: {req.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        
        token = create_access_token(subject=str(user.id), extra_claims={"username": user.username, "role": user.role})
        logger.info(f"Login successful for user: {req.username}")
        return TokenResponse(access_token=token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="登录失败，请稍后重试")

def _get_current_user(authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        logger.warning("Missing or invalid authorization header")
        raise HTTPException(status_code=401, detail="缺少凭证")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        logger.info(f"Token decoded successfully for user_id: {payload.get('sub')}")
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        raise HTTPException(status_code=401, detail="无效或过期的凭证")
    user_id = int(payload.get("sub", 0))
    if user_id == 0:
        logger.error("Invalid user_id in token")
        raise HTTPException(status_code=401, detail="无效的用户ID")
    user = db.query(User).get(user_id)
    if user is None:
        logger.error(f"User not found for user_id: {user_id}")
        raise HTTPException(status_code=401, detail="用户不存在")
    logger.info(f"User authenticated successfully: {user.username}")
    return user

@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(_get_current_user)):
    return MeResponse(id=user.id, username=user.username, role=user.role)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(user: User = Depends(_get_current_user)):
    """刷新访问令牌，无需重新输入密码"""
    token = create_access_token(subject=str(user.id), extra_claims={"username": user.username, "role": user.role})
    return TokenResponse(access_token=token)


