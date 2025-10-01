from __future__ import annotations

from typing import Annotated, List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from src.api.db import get_db
from src.api.models import User, UserRole
from src.api.auth import _get_current_user
from src.api.security import hash_password

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])

# 权限检查装饰器
def require_admin(user: User = Depends(_get_current_user)) -> User:
    """要求管理员权限"""
    if user.role != UserRole.ADMIN:
        logger.warning(f"Non-admin user {user.username} attempted admin access")
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user

# 请求/响应模型
class UserCreateRequest(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=64)
    role: str = UserRole.USER
    can_upload: bool = True
    can_download: bool = True
    can_chat: bool = True
    notes: str | None = None

class UserUpdateRequest(BaseModel):
    username: constr(min_length=3, max_length=64) | None = None
    role: str | None = None
    is_active: bool | None = None
    can_upload: bool | None = None
    can_download: bool | None = None
    can_chat: bool | None = None
    notes: str | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    can_upload: bool
    can_download: bool
    can_chat: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None
    created_by: int | None
    notes: str | None

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    page_size: int

class FileInfo(BaseModel):
    file_name: str
    file_size: int
    upload_time: datetime
    uploader: str | None
    file_path: str

class FileListResponse(BaseModel):
    files: List[FileInfo]
    total: int
    page: int
    page_size: int

# 用户管理API
@router.post("/users", response_model=UserResponse)
def create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """创建新用户"""
    try:
        logger.info(f"Admin {admin.username} creating user: {req.username}")
        
        # 检查用户名是否已存在
        existing = db.query(User).filter(User.username == req.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 创建用户
        user = User(
            username=req.username,
            password_hash=hash_password(req.password),
            role=req.role,
            can_upload=req.can_upload,
            can_download=req.can_download,
            can_chat=req.can_chat,
            created_by=admin.id,
            notes=req.notes
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created successfully: {req.username}")
        return UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            can_upload=user.can_upload,
            can_download=user.can_download,
            can_chat=user.can_chat,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            created_by=user.created_by,
            notes=user.notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="创建用户失败")

@router.get("/users", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """获取用户列表"""
    try:
        query = db.query(User)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    User.username.contains(search),
                    User.notes.contains(search)
                )
            )
        
        # 角色过滤
        if role:
            query = query.filter(User.role == role)
        
        # 状态过滤
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # 总数
        total = query.count()
        
        # 分页
        users = query.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size).all()
        
        user_responses = [
            UserResponse(
                id=user.id,
                username=user.username,
                role=user.role,
                is_active=user.is_active,
                can_upload=user.can_upload,
                can_download=user.can_download,
                can_chat=user.can_chat,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
                created_by=user.created_by,
                notes=user.notes
            )
            for user in users
        ]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="获取用户列表失败")

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """获取用户详情"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            can_upload=user.can_upload,
            can_download=user.can_download,
            can_chat=user.can_chat,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            created_by=user.created_by,
            notes=user.notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="获取用户信息失败")

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    req: UserUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """更新用户信息"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 防止修改自己的角色
        if user_id == admin.id and req.role and req.role != admin.role:
            raise HTTPException(status_code=400, detail="不能修改自己的角色")
        
        # 更新字段
        if req.username is not None:
            # 检查用户名是否已被其他用户使用
            existing = db.query(User).filter(User.username == req.username, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="用户名已被使用")
            user.username = req.username
        
        if req.role is not None:
            user.role = req.role
        if req.is_active is not None:
            user.is_active = req.is_active
        if req.can_upload is not None:
            user.can_upload = req.can_upload
        if req.can_download is not None:
            user.can_download = req.can_download
        if req.can_chat is not None:
            user.can_chat = req.can_chat
        if req.notes is not None:
            user.notes = req.notes
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user_id} updated by admin {admin.username}")
        
        return UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            can_upload=user.can_upload,
            can_download=user.can_download,
            can_chat=user.can_chat,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            created_by=user.created_by,
            notes=user.notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="更新用户失败")

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除用户"""
    try:
        # 防止删除自己
        if user_id == admin.id:
            raise HTTPException(status_code=400, detail="不能删除自己")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        db.delete(user)
        db.commit()
        
        logger.info(f"User {user_id} deleted by admin {admin.username}")
        return {"message": "用户删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="删除用户失败")

# 文件管理API
@router.get("/files", response_model=FileListResponse)
def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """获取文件列表"""
    try:
        from pathlib import Path
        import os
        
        # 获取文件目录
        files_dir = Path("data/processed")
        if not files_dir.exists():
            return FileListResponse(files=[], total=0, page=page, page_size=page_size)
        
        # 获取所有文件
        all_files = []
        for file_path in files_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                all_files.append({
                    "file_name": file_path.name,
                    "file_size": stat.st_size,
                    "upload_time": datetime.fromtimestamp(stat.st_mtime),
                    "uploader": None,  # 暂时无法获取上传者信息
                    "file_path": str(file_path)
                })
        
        # 搜索过滤
        if search:
            all_files = [f for f in all_files if search.lower() in f["file_name"].lower()]
        
        # 按上传时间排序
        all_files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        # 分页
        total = len(all_files)
        start = (page - 1) * page_size
        end = start + page_size
        files = all_files[start:end]
        
        return FileListResponse(
            files=[FileInfo(**f) for f in files],
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail="获取文件列表失败")

@router.delete("/files/{file_name}")
def delete_file(
    file_name: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除文件"""
    try:
        from pathlib import Path
        import os
        
        # 安全验证文件名
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            raise HTTPException(status_code=400, detail="无效的文件名")
        
        file_path = Path("data/processed") / file_name
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 删除文件
        file_path.unlink()
        
        logger.info(f"File {file_name} deleted by admin {admin.username}")
        return {"message": "文件删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_name}: {e}")
        raise HTTPException(status_code=500, detail="删除文件失败")

# 系统统计API
@router.get("/stats")
def get_system_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """获取系统统计信息"""
    try:
        from pathlib import Path
        
        # 用户统计
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
        
        # 文件统计
        files_dir = Path("data/processed")
        file_count = 0
        total_size = 0
        if files_dir.exists():
            for file_path in files_dir.glob("*"):
                if file_path.is_file():
                    file_count += 1
                    total_size += file_path.stat().st_size
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "admins": admin_users,
                "regular": total_users - admin_users
            },
            "files": {
                "count": file_count,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="获取系统统计失败")
