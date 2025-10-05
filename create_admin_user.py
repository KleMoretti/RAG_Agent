#!/usr/bin/env python3
"""创建管理员用户的简单脚本"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from src.api.db import SessionLocal
from src.api.models import User, UserRole
from src.api.security import hash_password

def create_admin():
    """创建管理员用户"""
    db: Session = SessionLocal()
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("❌ 用户 'admin' 已存在")
            return
        
        # 创建新用户
        hashed_password = hash_password("admin123")
        new_user = User(
            username="admin",
            email="admin@test.com",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
            can_upload=True,
            can_download=True,
            can_chat=True,
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ 管理员用户创建成功！")
        print(f"   用户名: {new_user.username}")
        print(f"   邮箱: {new_user.email}")
        print(f"   角色: {new_user.role}")
        print(f"   密码: admin123")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
