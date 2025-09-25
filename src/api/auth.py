from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

from src.api.db import get_db, engine, Base
from src.api.models import User
from src.api.security import verify_password, hash_password, create_access_token, decode_token


# Ensure tables are created (for demo/dev); in prod use migrations
Base.metadata.create_all(bind=engine)

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
    existing = db.query(User).filter(User.username == req.username).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role=(req.role or "user"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return MeResponse(id=user.id, username=user.username, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token(subject=str(user.id), extra_claims={"username": user.username, "role": user.role})
    return TokenResponse(access_token=token)


def _get_current_user(authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="缺少凭证")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="无效或过期的凭证")
    user_id = int(payload.get("sub", 0))
    user = db.query(User).get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(_get_current_user)):
    return MeResponse(id=user.id, username=user.username, role=user.role)


