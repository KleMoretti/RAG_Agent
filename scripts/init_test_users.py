#!/usr/bin/env python3
"""
测试用户初始化脚本
创建三种角色的测试账号：ADMIN、MANAGER、TECHNICIAN
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from src.api.db import get_db, engine
from src.api.models import User, UserRole
from src.api.security import hash_password
from datetime import datetime


def create_test_users(db: Session):
    """创建测试用户账号"""

    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "role": UserRole.ADMIN,
            "email": "admin@steel-ai.com",
            "notes": "系统管理员测试账号",
            "can_upload": True,
            "can_download": True,
            "can_chat": True,
            "can_access_admin": True,
        },
        {
            "username": "manager",
            "password": "manager123",
            "role": UserRole.MANAGER,
            "email": "manager@steel-ai.com",
            "notes": "技术经理测试账号 - 综合决策支持",
            "can_upload": True,
            "can_download": True,
            "can_chat": True,
            "can_access_admin": False,
        },
        {
            "username": "technician",
            "password": "tech123",
            "role": UserRole.TECHNICIAN,
            "email": "tech@steel-ai.com",
            "notes": "技术员测试账号 - 设备故障诊断",
            "can_upload": False,  # 技术员只能上传故障日志，不能删除
            "can_download": True,
            "can_chat": True,
            "can_access_admin": False,
        },
    ]

    created_count = 0
    updated_count = 0

    for user_data in test_users:
        username = user_data["username"]
        existing_user = db.query(User).filter(User.username == username).first()

        if existing_user:
            # 更新现有用户
            existing_user.role = user_data["role"]
            existing_user.email = user_data["email"]
            existing_user.notes = user_data["notes"]
            existing_user.can_upload = user_data["can_upload"]
            existing_user.can_download = user_data["can_download"]
            existing_user.can_chat = user_data["can_chat"]
            existing_user.can_access_admin = user_data["can_access_admin"]
            existing_user.is_active = True
            existing_user.updated_at = datetime.utcnow()
            # 重置密码
            existing_user.hashed_password = hash_password(user_data["password"])

            print(f"✅ 更新用户: {username} (角色: {user_data['role'].value})")
            updated_count += 1
        else:
            # 创建新用户
            new_user = User(
                username=username,
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                email=user_data["email"],
                notes=user_data["notes"],
                is_active=True,
                can_upload=user_data["can_upload"],
                can_download=user_data["can_download"],
                can_chat=user_data["can_chat"],
                can_access_admin=user_data["can_access_admin"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(new_user)
            print(f"✅ 创建用户: {username} (角色: {user_data['role'].value})")
            created_count += 1

    db.commit()

    return created_count, updated_count


def print_user_info(db: Session):
    """打印用户信息"""
    print("\n" + "=" * 80)
    print("测试账号列表")
    print("=" * 80)

    users = (
        db.query(User)
        .filter(User.username.in_(["admin", "manager", "technician"]))
        .all()
    )

    for user in users:
        print(f"\n👤 用户名: {user.username}")
        print(
            f"   密码: {'admin123' if user.role == 'admin' else 'manager123' if user.role == 'manager' else 'tech123'}"
        )
        print(f"   角色: {user.role}")
        print(f"   邮箱: {user.email}")
        print(f"   权限:")
        print(f"     - 聊天: {'✅' if user.can_chat else '❌'}")
        print(f"     - 上传: {'✅' if user.can_upload else '❌'}")
        print(f"     - 下载: {'✅' if user.can_download else '❌'}")
        print(f"     - 管理后台: {'✅' if user.can_access_admin else '❌'}")
        print(f"   备注: {user.notes}")

    print("\n" + "=" * 80)
    print("登录测试")
    print("=" * 80)
    print("\n1️⃣ 管理员登录:")
    print("   用户名: admin")
    print("   密码: admin123")
    print("   功能: 全部功能 + 系统管理")

    print("\n2️⃣ 技术经理登录:")
    print("   用户名: manager")
    print("   密码: manager123")
    print("   功能: 智能问答、知识库、市场分析、工艺流程")

    print("\n3️⃣ 技术员登录:")
    print("   用户名: technician")
    print("   密码: tech123")
    print("   功能: 设备诊断、设备管理、知识库查询")

    print("\n" + "=" * 80)
    print("前端访问地址: http://localhost:3000/login")
    print("后端 API 地址: http://localhost:8000/docs")
    print("=" * 80 + "\n")


def main():
    """主函数"""
    print("🚀 开始初始化测试用户...")

    try:
        # 获取数据库会话
        db = next(get_db())

        # 创建测试用户
        created, updated = create_test_users(db)

        print(f"\n📊 统计:")
        print(f"   - 新增用户: {created}")
        print(f"   - 更新用户: {updated}")
        print(f"   - 总计: {created + updated}")

        # 打印用户信息
        print_user_info(db)

        print("✅ 测试用户初始化完成！\n")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
