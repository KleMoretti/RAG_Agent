from __future__ import annotations

from typing import Annotated
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

from src.api.db import get_db, engine, Base
from src.api.models import User, UserRole
from src.api.security import verify_password, hash_password, create_access_token, decode_token

# 设置日志
logger = logging.getLogger(__name__)

# Database tables are created by start_system.py

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=64)
    role: constr(min_length=2, max_length=32) | None = None

class LoginRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=64)

class ChangePasswordRequest(BaseModel):
    old_password: constr(min_length=6, max_length=64)
    new_password: constr(min_length=6, max_length=64)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    can_upload: bool
    can_download: bool
    can_chat: bool

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
            hashed_password=hash_password(req.password),
            role=(req.role or UserRole.USER),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User registered successfully: {req.username}")
        return MeResponse(
            id=user.id, 
            username=user.username, 
            role=user.role,
            is_active=user.is_active,
            can_upload=user.can_upload,
            can_download=user.can_download,
            can_chat=user.can_chat
        )
        
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
        
        if not verify_password(req.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {req.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        
        # 检查用户是否被禁用
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {req.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账户已被禁用")
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.commit()
        
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
    return MeResponse(
        id=user.id, 
        username=user.username, 
        role=user.role,
        is_active=user.is_active,
        can_upload=user.can_upload,
        can_download=user.can_download,
        can_chat=user.can_chat
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(user: User = Depends(_get_current_user)):
    """刷新访问令牌，无需重新输入密码"""
    token = create_access_token(subject=str(user.id), extra_claims={"username": user.username, "role": user.role})
    return TokenResponse(access_token=token)

@router.post("/change-password")
def change_password(req: ChangePasswordRequest, user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    """用户更改密码"""
    try:
        logger.info(f"Password change attempt for user: {user.username}")
        
        # 验证旧密码
        if not verify_password(req.old_password, user.hashed_password):
            logger.warning(f"Invalid old password for user: {user.username}")
            raise HTTPException(status_code=400, detail="当前密码不正确")
        
        # 检查新密码是否与旧密码相同
        if verify_password(req.new_password, user.hashed_password):
            logger.warning(f"New password same as old password for user: {user.username}")
            raise HTTPException(status_code=400, detail="新密码不能与当前密码相同")
        
        # 更新密码
        user.hashed_password = hash_password(req.new_password)
        db.commit()
        
        logger.info(f"Password changed successfully for user: {user.username}")
        return {"message": "密码修改成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error for user {user.username}: {e}")
        raise HTTPException(status_code=500, detail="密码修改失败，请稍后重试")

# 权限检查函数
def require_permission(permission: str):
    """权限检查装饰器工厂"""
    def permission_checker(user: User = Depends(_get_current_user)) -> User:
        if not user.is_active:
            raise HTTPException(status_code=403, detail="账户已被禁用")
        
        if permission == "upload" and not user.can_upload:
            raise HTTPException(status_code=403, detail="没有上传权限")
        elif permission == "download" and not user.can_download:
            raise HTTPException(status_code=403, detail="没有下载权限")
        elif permission == "chat" and not user.can_chat:
            raise HTTPException(status_code=403, detail="没有聊天权限")
        
        return user
    return permission_checker

def require_admin(user: User = Depends(_get_current_user)) -> User:
    """要求管理员权限"""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


