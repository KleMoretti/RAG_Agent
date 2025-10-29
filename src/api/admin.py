from __future__ import annotations

from typing import Annotated, List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from src.api.db import get_db
from src.api.models import User, UserRole, Vocabulary
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


def require_manager_or_admin(user: User = Depends(_get_current_user)) -> User:
    """要求管理员或经理权限"""
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        logger.warning(f"User {user.username} ({user.role}) attempted manager/admin access")
        raise HTTPException(status_code=403, detail="需要管理员或经理权限")
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


class ResetPasswordRequest(BaseModel):
    new_password: constr(min_length=6, max_length=64)


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    can_upload: bool
    can_download: bool
    can_chat: bool
    can_access_admin: bool
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
    id: str
    fileName: str
    fileSize: int
    uploadDate: str
    uploaderName: str | None
    filePath: str
    isProcessed: bool = True
    chunkCount: int | None = None


class FileListResponse(BaseModel):
    data: List[FileInfo]
    meta: dict


class BatchDeleteRequest(BaseModel):
    fileNames: List[str]


class BatchDeleteResponse(BaseModel):
    success: List[str]
    failed: List[dict]
    total: int


# 用户管理API
@router.post("/users", response_model=UserResponse)
def create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
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
            hashed_password=hash_password(req.password),
            role=req.role,
            can_upload=req.can_upload,
            can_download=req.can_download,
            can_chat=req.can_chat,
            created_by=admin.id,
            notes=req.notes,
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
            can_access_admin=user.can_access_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            created_by=user.created_by,
            notes=user.notes,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="创建用户失败")


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """获取用户列表"""
    try:
        query = db.query(User)

        # 搜索过滤
        if search:
            query = query.filter(
                or_(User.username.contains(search), User.notes.contains(search))
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
        users = (
            query.order_by(desc(User.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        user_responses = [
            UserResponse(
                id=user.id,
                username=user.username,
                role=user.role,
                is_active=user.is_active,
                can_upload=user.can_upload,
                can_download=user.can_download,
                can_chat=user.can_chat,
                can_access_admin=user.can_access_admin,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
                created_by=user.created_by,
                notes=user.notes,
            )
            for user in users
        ]

        total_pages = (total + page_size - 1) // page_size

        return {
            "data": user_responses,
            "meta": {
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages,
            },
        }

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="获取用户列表失败")


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
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
            can_access_admin=user.can_access_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            created_by=user.created_by,
            notes=user.notes,
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
    admin: User = Depends(require_admin),
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
            existing = (
                db.query(User)
                .filter(User.username == req.username, User.id != user_id)
                .first()
            )
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
            can_access_admin=user.can_access_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            created_by=user.created_by,
            notes=user.notes,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="更新用户失败")


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)
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


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    req: ResetPasswordRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """管理员重置用户密码"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 更新密码
        user.hashed_password = hash_password(req.new_password)
        user.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Password reset for user {user_id} by admin {admin.username}")
        return {"message": "密码重置成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="密码重置失败")


# 文件管理API
@router.get("/files")
def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_get_current_user),
):
    """获取文件列表（所有登录用户可查看）"""
    try:
        from pathlib import Path
        import os

        # 获取文件目录 - 从 data/raw 读取原始文件
        files_dir = Path("data/raw")
        if not files_dir.exists():
            return FileListResponse(
                data=[],
                meta={"total": 0, "page": page, "pageSize": page_size, "totalPages": 0},
            )

        # 获取所有文件
        all_files = []
        processed_dir = Path("data/processed")

        for file_path in files_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()

                # 检查是否已处理（存在对应的 .done 文件）
                file_id = file_path.name
                done_marker = processed_dir / f"{file_id}.done"
                is_processed = done_marker.exists()

                # 尝试获取原始文件名（从 file_id 中提取）
                # file_id 格式: {hash}_{original_name}
                display_name = file_id
                if "_" in file_id:
                    # 移除前缀哈希
                    parts = file_id.split("_", 1)
                    if len(parts) == 2:
                        display_name = parts[1]

                import uuid

                all_files.append(
                    FileInfo(
                        id=file_id,  # 使用实际文件名作为ID，便于后续操作
                        fileName=display_name,
                        fileSize=stat.st_size,
                        uploadDate=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        uploaderName="系统",  # 暂时无法获取上传者信息
                        filePath=str(file_path),
                        isProcessed=is_processed,
                        chunkCount=None,
                    )
                )

        # 搜索过滤
        if search:
            all_files = [f for f in all_files if search.lower() in f.fileName.lower()]

        # 按上传时间排序
        all_files.sort(key=lambda x: x.uploadDate, reverse=True)

        # 分页
        total = len(all_files)
        start = (page - 1) * page_size
        end = start + page_size
        files = all_files[start:end]

        total_pages = (total + page_size - 1) // page_size

        return FileListResponse(
            data=files,
            meta={
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages,
            },
        )

    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail="获取文件列表失败")


@router.delete("/files/{file_name}")
def delete_file(
    file_name: str, db: Session = Depends(get_db), admin: User = Depends(require_manager_or_admin)
):
    """删除文件（需要管理员或经理权限）"""
    try:
        from pathlib import Path
        import os

        # 安全验证文件名
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            raise HTTPException(status_code=400, detail="无效的文件名")

        # 删除 data/raw 中的原始文件
        raw_path = Path("data/raw") / file_name
        if not raw_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        raw_path.unlink()

        # 删除 data/processed 中的相关文件
        processed_dir = Path("data/processed")
        chunks_file = processed_dir / f"{file_name}.chunks.jsonl"
        done_file = processed_dir / f"{file_name}.done"

        if chunks_file.exists():
            chunks_file.unlink()
        if done_file.exists():
            done_file.unlink()

        logger.info(
            f"File {file_name} and its processed files deleted by {admin.username} ({admin.role})"
        )
        return {"message": "文件删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_name}: {e}")
        raise HTTPException(status_code=500, detail="删除文件失败")


@router.post("/files/batch-delete")
def batch_delete_files(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_manager_or_admin),
):
    """批量删除文件（需要管理员或经理权限）"""
    try:
        from pathlib import Path

        success = []
        failed = []

        for file_name in request.fileNames:
            try:
                # 安全验证文件名
                if ".." in file_name or "/" in file_name or "\\" in file_name:
                    failed.append({"fileName": file_name, "reason": "无效的文件名"})
                    continue

                # 删除 data/raw 中的原始文件
                raw_path = Path("data/raw") / file_name
                if not raw_path.exists():
                    failed.append({"fileName": file_name, "reason": "文件不存在"})
                    continue

                raw_path.unlink()

                # 删除 data/processed 中的相关文件
                processed_dir = Path("data/processed")
                chunks_file = processed_dir / f"{file_name}.chunks.jsonl"
                done_file = processed_dir / f"{file_name}.done"

                if chunks_file.exists():
                    chunks_file.unlink()
                if done_file.exists():
                    done_file.unlink()

                success.append(file_name)
                logger.info(
                    f"File {file_name} and its processed files deleted by {admin.username} ({admin.role})"
                )

            except Exception as e:
                logger.error(f"Error deleting file {file_name}: {e}")
                failed.append({"fileName": file_name, "reason": str(e)})

        return BatchDeleteResponse(
            success=success, failed=failed, total=len(request.fileNames)
        )

    except Exception as e:
        logger.error(f"Error in batch delete: {e}")
        raise HTTPException(status_code=500, detail="批量删除失败")


@router.get("/files/{file_name}/preview")
def preview_file(
    file_name: str, db: Session = Depends(get_db), current_user: User = Depends(_get_current_user)
):
    """预览文件内容（所有登录用户可查看）"""
    try:
        from pathlib import Path

        # 安全验证文件名
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            raise HTTPException(status_code=400, detail="无效的文件名")

        # 读取原始文件
        raw_path = Path("data/raw") / file_name
        if not raw_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # 尝试读取文件内容（限制大小）
        MAX_PREVIEW_SIZE = 1024 * 1024  # 1MB
        file_size = raw_path.stat().st_size

        if file_size > MAX_PREVIEW_SIZE:
            # 对于大文件，只读取前 1MB
            with raw_path.open("rb") as f:
                content = f.read(MAX_PREVIEW_SIZE)
            is_truncated = True
        else:
            with raw_path.open("rb") as f:
                content = f.read()
            is_truncated = False

        # 尝试解码为文本
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text_content = content.decode("gbk")
            except UnicodeDecodeError:
                text_content = (
                    f"[二进制文件，无法预览文本内容]\n文件大小: {file_size} 字节"
                )

        # 读取处理后的分块信息
        processed_dir = Path("data/processed")
        chunks_file = processed_dir / f"{file_name}.chunks.jsonl"
        chunks = []

        if chunks_file.exists():
            import json

            try:
                with chunks_file.open("r", encoding="utf-8") as f:
                    for line in f:
                        chunk_data = json.loads(line.strip())
                        chunks.append(
                            {
                                "content": chunk_data.get("content", "")[:100],
                                "type": "text",
                                "length": chunk_data.get("length", 0),
                            }
                        )
            except Exception:
                pass

        return {
            "content": text_content,
            "contentType": "text/plain",
            "chunks": chunks,
            "isTruncated": is_truncated,
            "fileSize": file_size,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing file {file_name}: {e}")
        raise HTTPException(status_code=500, detail="预览文件失败")


@router.get("/files/{file_name}/download")
def download_file(
    file_name: str, db: Session = Depends(get_db), current_user: User = Depends(_get_current_user)
):
    """下载文件（所有登录用户可下载）"""
    try:
        from pathlib import Path
        from fastapi.responses import FileResponse

        # 安全验证文件名
        if ".." in file_name or "/" in file_name or "\\" in file_name:
            raise HTTPException(status_code=400, detail="无效的文件名")

        # 读取原始文件
        raw_path = Path("data/raw") / file_name
        if not raw_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # 提取显示文件名（移除哈希前缀）
        display_name = file_name
        if "_" in file_name:
            parts = file_name.split("_", 1)
            if len(parts) == 2:
                display_name = parts[1]

        logger.info(f"File {file_name} downloaded by {current_user.username} ({current_user.role})")

        return FileResponse(
            path=str(raw_path),
            filename=display_name,
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_name}: {e}")
        raise HTTPException(status_code=500, detail="下载文件失败")


# 专业词汇管理API
class VocabularyEntry(BaseModel):
    id: str
    term: str
    definition: str
    category: str
    synonyms: List[str]
    relatedTerms: List[str]
    createdAt: str
    updatedAt: str
    createdBy: str


class VocabularyCreateRequest(BaseModel):
    term: str
    definition: str
    category: str = ""
    synonyms: List[str] = []
    relatedTerms: List[str] = []


class VocabularyUpdateRequest(BaseModel):
    term: str | None = None
    definition: str | None = None
    category: str | None = None
    synonyms: List[str] | None = None
    relatedTerms: List[str] | None = None


class VocabularyListResponse(BaseModel):
    data: List[VocabularyEntry]
    meta: dict


# 专业词汇管理API


@router.get("/vocabulary", response_model=VocabularyListResponse)
def get_vocabulary_entries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """获取专业词汇列表"""
    try:
        # 查询总数
        total = db.query(Vocabulary).count()

        # 分页查询
        start = (page - 1) * page_size
        vocabulary_entries = (
            db.query(Vocabulary)
            .order_by(desc(Vocabulary.created_at))
            .offset(start)
            .limit(page_size)
            .all()
        )

        # 转换为响应格式
        entries = [
            VocabularyEntry(
                id=str(entry.id),
                term=entry.term,
                definition=entry.definition,
                category=entry.category,
                synonyms=entry.synonyms or [],
                relatedTerms=entry.related_terms or [],
                createdAt=entry.created_at.isoformat(),
                updatedAt=entry.updated_at.isoformat(),
                createdBy="admin",  # 暂时设为admin
            )
            for entry in vocabulary_entries
        ]

        total_pages = (total + page_size - 1) // page_size

        return VocabularyListResponse(
            data=entries,
            meta={
                "total": total,
                "page": page,
                "pageSize": page_size,
                "totalPages": total_pages,
            },
        )

    except Exception as e:
        logger.error(f"Error getting vocabulary entries: {e}")
        raise HTTPException(status_code=500, detail="获取词汇列表失败")


@router.post("/vocabulary", response_model=VocabularyEntry)
def create_vocabulary_entry(
    req: VocabularyCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """创建专业词汇条目"""
    try:
        # 检查词汇是否已存在
        existing = db.query(Vocabulary).filter(Vocabulary.term == req.term).first()
        if existing:
            raise HTTPException(status_code=400, detail="词汇已存在")

        # 创建新词汇
        new_vocabulary = Vocabulary(
            term=req.term,
            definition=req.definition,
            category=req.category,
            synonyms=req.synonyms,
            related_terms=req.relatedTerms,
            created_by=admin.id,
        )

        db.add(new_vocabulary)
        db.commit()
        db.refresh(new_vocabulary)

        # 返回响应
        return VocabularyEntry(
            id=str(new_vocabulary.id),
            term=new_vocabulary.term,
            definition=new_vocabulary.definition,
            category=new_vocabulary.category,
            synonyms=new_vocabulary.synonyms or [],
            relatedTerms=new_vocabulary.related_terms or [],
            createdAt=new_vocabulary.created_at.isoformat(),
            updatedAt=new_vocabulary.updated_at.isoformat(),
            createdBy="admin",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vocabulary entry: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="创建词汇失败")


@router.put("/vocabulary/{entry_id}", response_model=VocabularyEntry)
def update_vocabulary_entry(
    entry_id: str,
    req: VocabularyUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """更新专业词汇条目"""
    try:
        # 查找条目
        entry = db.query(Vocabulary).filter(Vocabulary.id == int(entry_id)).first()
        if not entry:
            raise HTTPException(status_code=404, detail="词汇条目不存在")

        # 更新条目
        if req.term is not None:
            entry.term = req.term
        if req.definition is not None:
            entry.definition = req.definition
        if req.category is not None:
            entry.category = req.category
        if req.synonyms is not None:
            entry.synonyms = req.synonyms
        if req.relatedTerms is not None:
            entry.related_terms = req.relatedTerms

        db.commit()
        db.refresh(entry)

        # 返回响应
        return VocabularyEntry(
            id=str(entry.id),
            term=entry.term,
            definition=entry.definition,
            category=entry.category,
            synonyms=entry.synonyms or [],
            relatedTerms=entry.related_terms or [],
            createdAt=entry.created_at.isoformat(),
            updatedAt=entry.updated_at.isoformat(),
            createdBy="admin",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vocabulary entry {entry_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="更新词汇失败")


@router.delete("/vocabulary/{entry_id}")
def delete_vocabulary_entry(
    entry_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    """删除专业词汇条目"""
    try:
        # 查找条目
        entry = db.query(Vocabulary).filter(Vocabulary.id == int(entry_id)).first()
        if not entry:
            raise HTTPException(status_code=404, detail="词汇条目不存在")

        # 删除条目
        db.delete(entry)
        db.commit()

        logger.info(f"Vocabulary entry deleted: {entry_id} by {admin.username}")
        return {"message": "词汇条目删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vocabulary entry {entry_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="删除词汇失败")


@router.get("/vocabulary/search")
def search_vocabulary_entries(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """搜索专业词汇条目"""
    try:
        # 使用数据库查询进行搜索
        query_lower = f"%{q.lower()}%"

        # 搜索词汇术语、定义、分类
        results = (
            db.query(Vocabulary)
            .filter(
                or_(
                    Vocabulary.term.ilike(query_lower),
                    Vocabulary.definition.ilike(query_lower),
                    Vocabulary.category.ilike(query_lower),
                )
            )
            .all()
        )

        # 转换为响应格式
        entries = [
            VocabularyEntry(
                id=str(entry.id),
                term=entry.term,
                definition=entry.definition,
                category=entry.category,
                synonyms=entry.synonyms or [],
                relatedTerms=entry.related_terms or [],
                createdAt=entry.created_at.isoformat(),
                updatedAt=entry.updated_at.isoformat(),
                createdBy="admin",
            )
            for entry in results
        ]

        logger.info(f"Vocabulary search for '{q}' returned {len(entries)} results")
        return entries

    except Exception as e:
        logger.error(f"Error searching vocabulary entries: {e}")
        raise HTTPException(status_code=500, detail="搜索词汇失败")


# 系统统计API
@router.get("/stats")
def get_system_stats(
    db: Session = Depends(get_db), admin: User = Depends(require_admin)
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

        # 词汇统计
        vocabulary_count = db.query(Vocabulary).count()

        return {
            "totalUsers": total_users,
            "activeUsers": active_users,
            "totalFiles": file_count,
            "totalSessions": 0,  # 暂时设为0
            "systemHealth": "healthy",
            "diskUsage": {
                "total": 1000000000,  # 1GB
                "used": total_size,
                "free": 1000000000 - total_size,
            },
            "vocabularyCount": vocabulary_count,
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="获取系统统计失败")
