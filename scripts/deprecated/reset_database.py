#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 此脚本已废弃，请使用新的统一 CLI 工具

推荐使用: python scripts/db_migrate.py reset

重置数据库的脚本
删除所有表并重新创建
使用方法: python scripts/reset_database.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.api.db import SessionLocal, engine, Base
from src.api.models import User, UserRole
from src.api.security import hash_password
# 导入prompt管理模型，确保新表被包含在重置中
import src.prompt_management
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """重置数据库"""
    try:
        # 删除所有表
        logger.info("🗑️ 删除所有表...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 所有表已删除")
        
        # 重新创建所有表
        logger.info("🏗️ 创建新表...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建成功")
        
        # 创建默认管理员用户
        db = SessionLocal()
        try:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                can_upload=True,
                can_download=True,
                can_chat=True,
                can_access_admin=True,  # 管理员可以访问管理面板
                notes="默认管理员账户",
                created_by=None,  # 系统创建，无创建者
                last_login=None  # 初始登录时间
            )
            
            db.add(admin_user)
            db.commit()
            logger.info("✅ 默认管理员用户创建成功")
            logger.info("   用户名: admin")
            logger.info("   密码: admin123")
            logger.info("   角色: admin")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ 数据库重置失败: {e}")
        raise

def main():
    """主函数"""
    reset_database()

if __name__ == "__main__":
    main()
