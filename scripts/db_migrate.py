#!/usr/bin/env python3
"""
数据库迁移管理工具

功能：
1. 重置数据库（reset）- 删除所有表并重新创建
2. 添加预设问题（add-presets）- 迁移添加预设问题表
3. 添加词汇表（add-vocabulary）- 迁移添加钢铁专业词汇表
4. 添加 Prompt 表（add-prompts）- 迁移添加 Prompt 管理表
5. 列出所有迁移（list）- 查看可用的迁移
6. 检查状态（status）- 检查数据库状态

使用方法:
    python scripts/db_migrate.py reset
    python scripts/db_migrate.py add-presets
    python scripts/db_migrate.py status
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from src.api.db import SessionLocal, engine, Base
from src.api.models import User, UserRole
from src.api.security import hash_password

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """重置数据库"""
    print("🗑️ 重置数据库...")
    print("=" * 60)
    
    try:
        # 删除所有表
        logger.info("删除所有表...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 所有表已删除")
        
        # 重新创建所有表
        logger.info("创建新表...")
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
                can_access_admin=True,
                notes="默认管理员账户",
                created_by=None,
                last_login=None
            )
            
            db.add(admin_user)
            db.commit()
            
            print("\n✅ 默认管理员用户创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   角色: ADMIN")
            
        finally:
            db.close()
        
        print("\n✅ 数据库重置完成！")
        
    except Exception as e:
        logger.error(f"❌ 数据库重置失败: {e}")
        raise


def add_preset_questions():
    """添加预设问题表"""
    print("📝 添加预设问题表...")
    print("=" * 60)
    
    try:
        from src.api.models import PresetQuestion
        
        # 创建预设问题表
        PresetQuestion.__table__.create(engine, checkfirst=True)
        
        # 添加默认预设问题
        db = SessionLocal()
        try:
            # 检查是否已有预设问题
            existing = db.query(PresetQuestion).first()
            if existing:
                print("⚠️  预设问题已存在，跳过...")
                return
            
            # 默认预设问题
            default_questions = [
                {
                    'question': '钢铁生产的主要流程是什么？',
                    'role': 'PRODUCTION',
                    'category': 'process',
                    'order': 1,
                    'is_active': True
                },
                {
                    'question': '高炉温度控制有哪些关键参数？',
                    'role': 'TECHNICIAN',
                    'category': 'equipment',
                    'order': 2,
                    'is_active': True
                },
                {
                    'question': '如何诊断设备故障？',
                    'role': 'TECHNICIAN',
                    'category': 'equipment',
                    'order': 3,
                    'is_active': True
                },
                {
                    'question': '当前铁矿石市场价格趋势如何？',
                    'role': 'PURCHASER',
                    'category': 'market',
                    'order': 4,
                    'is_active': True
                },
                {
                    'question': '环保排放标准有哪些要求？',
                    'role': 'ENV_EXPERT',
                    'category': 'environment',
                    'order': 5,
                    'is_active': True
                },
            ]
            
            for q_data in default_questions:
                question = PresetQuestion(**q_data)
                db.add(question)
            
            db.commit()
            print(f"✅ 成功添加 {len(default_questions)} 个预设问题")
            
        finally:
            db.close()
        
        print("✅ 预设问题表迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 添加预设问题表失败: {e}")
        raise


def add_vocabulary_table():
    """添加专业词汇表"""
    print("📖 添加专业词汇表...")
    print("=" * 60)
    
    try:
        from src.knowledge_graph.models import SteelVocabulary
        
        # 创建词汇表
        SteelVocabulary.__table__.create(engine, checkfirst=True)
        
        # 添加默认词汇
        db = SessionLocal()
        try:
            # 检查是否已有词汇
            existing = db.query(SteelVocabulary).first()
            if existing:
                print("⚠️  词汇表已存在，跳过...")
                return
            
            # 默认词汇
            default_vocab = [
                {
                    'term': '高炉',
                    'category': 'equipment',
                    'definition': '炼铁的主要设备，用于将铁矿石还原成生铁',
                    'english_term': 'Blast Furnace',
                    'synonyms': ['炼铁炉'],
                    'related_terms': ['炼铁', '生铁', '铁矿石'],
                    'domain_score': 0.95
                },
                {
                    'term': '转炉',
                    'category': 'equipment',
                    'definition': '炼钢的主要设备，用于将生铁转化为钢',
                    'english_term': 'Converter',
                    'synonyms': ['炼钢炉'],
                    'related_terms': ['炼钢', '生铁', '钢水'],
                    'domain_score': 0.95
                },
                {
                    'term': '轧钢',
                    'category': 'process',
                    'definition': '通过轧制将钢坯加工成各种钢材的工艺',
                    'english_term': 'Steel Rolling',
                    'synonyms': ['钢材轧制'],
                    'related_terms': ['钢坯', '钢材', '轧机'],
                    'domain_score': 0.90
                },
            ]
            
            for vocab_data in default_vocab:
                vocab = SteelVocabulary(**vocab_data)
                db.add(vocab)
            
            db.commit()
            print(f"✅ 成功添加 {len(default_vocab)} 个专业词汇")
            
        finally:
            db.close()
        
        print("✅ 专业词汇表迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 添加词汇表失败: {e}")
        raise


def add_prompt_tables():
    """添加 Prompt 管理表"""
    print("💬 添加 Prompt 管理表...")
    print("=" * 60)
    
    try:
        # 导入 prompt 模型
        import src.prompt_management
        from src.prompt_management.service import PromptService
        
        # 创建所有 prompt 表
        Base.metadata.create_all(bind=engine)
        
        # 初始化默认 prompt
        db = SessionLocal()
        try:
            service = PromptService(db)
            
            # 检查是否已有 prompt 模板
            templates = service.list_prompt_templates(limit=1)
            if templates:
                print("⚠️  Prompt 表已存在，跳过...")
                return
            
            # 创建默认系统 prompt
            default_prompt = """你是钢铁行业AI决策助手，专注于为钢铁生产、设备维护、市场分析提供专业支持。

你的职责:
1. 基于检索到的文档提供准确、专业的回答
2. 使用钢铁行业术语和最佳实践
3. 如果信息不足，明确说明并建议查询方向
4. 保持回答简洁、可操作

回答格式:
- 使用清晰的结构化格式
- 引用文档来源
- 提供具体的数据和建议"""
            
            template = service.create_prompt_template(
                name="default_system_prompt",
                content=default_prompt,
                description="默认系统 Prompt",
                agent_type="GENERAL",
                user_role="ADMIN",
                is_active=True,
                version="1.0.0"
            )
            
            print(f"✅ 成功创建默认 Prompt 模板 (ID: {template.id})")
            
        finally:
            db.close()
        
        print("✅ Prompt 管理表迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 添加 Prompt 表失败: {e}")
        raise


def check_database_status():
    """检查数据库状态"""
    print("🔍 数据库状态检查")
    print("=" * 60)
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 数据库表数量: {len(tables)}")
        print("\n表列表:")
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        # 检查关键表
        required_tables = ['users', 'preset_questions', 'steel_vocabulary', 'prompt_templates']
        print("\n关键表检查:")
        for table in required_tables:
            status = "✅" if table in tables else "❌"
            print(f"  {status} {table}")
        
        # 统计记录数
        print("\n记录统计:")
        db = SessionLocal()
        try:
            if 'users' in tables:
                from src.api.models import User
                user_count = db.query(User).count()
                print(f"  users: {user_count} 条")
            
            if 'preset_questions' in tables:
                from src.api.models import PresetQuestion
                preset_count = db.query(PresetQuestion).count()
                print(f"  preset_questions: {preset_count} 条")
            
            if 'steel_vocabulary' in tables:
                from src.knowledge_graph.models import SteelVocabulary
                vocab_count = db.query(SteelVocabulary).count()
                print(f"  steel_vocabulary: {vocab_count} 条")
        
        finally:
            db.close()
        
        print("\n✅ 数据库状态检查完成")
        
    except Exception as e:
        logger.error(f"❌ 检查数据库状态失败: {e}")
        raise


def list_migrations():
    """列出所有可用的迁移"""
    print("📋 可用的迁移操作")
    print("=" * 60)
    
    migrations = [
        ("reset", "重置数据库（删除所有表并重新创建）"),
        ("add-presets", "添加预设问题表"),
        ("add-vocabulary", "添加专业词汇表"),
        ("add-prompts", "添加 Prompt 管理表"),
        ("status", "检查数据库状态"),
    ]
    
    for cmd, desc in migrations:
        print(f"  {cmd:20s} - {desc}")
    
    print("\n使用方法:")
    print(f"  python scripts/db_migrate.py <command>")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="数据库迁移管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 重置数据库
  python scripts/db_migrate.py reset
  
  # 添加预设问题
  python scripts/db_migrate.py add-presets
  
  # 添加词汇表
  python scripts/db_migrate.py add-vocabulary
  
  # 添加 Prompt 表
  python scripts/db_migrate.py add-prompts
  
  # 检查状态
  python scripts/db_migrate.py status
  
  # 列出所有迁移
  python scripts/db_migrate.py list
        """
    )
    
    parser.add_argument('command', 
                       choices=['reset', 'add-presets', 'add-vocabulary', 
                               'add-prompts', 'status', 'list'],
                       help='迁移命令')
    parser.add_argument('--force', action='store_true',
                       help='强制执行（跳过确认）')
    
    args = parser.parse_args()
    
    # 危险操作需要确认
    if args.command == 'reset' and not args.force:
        print("⚠️  警告: 此操作将删除所有数据！")
        confirm = input("确认继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
    
    # 执行命令
    command_handlers = {
        'reset': reset_database,
        'add-presets': add_preset_questions,
        'add-vocabulary': add_vocabulary_table,
        'add-prompts': add_prompt_tables,
        'status': check_database_status,
        'list': list_migrations,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            handler()
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

