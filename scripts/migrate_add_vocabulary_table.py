#!/usr/bin/env python3
"""
添加专业词汇表的数据库迁移脚本
使用方法: python scripts/migrate_add_vocabulary_table.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from src.api.db import SessionLocal, engine, Base
from src.api.models import User, UserRole, Vocabulary
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_add_vocabulary_table():
    """添加专业词汇表"""
    try:
        # 检查是否需要迁移
        if check_table_exists('vocabulary'):
            logger.info("✅ vocabulary表已存在，无需迁移")
            return True
        
        logger.info("🔄 开始添加vocabulary表...")
        
        # 创建新表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ vocabulary表创建成功")
        
        # 验证表是否创建成功
        if not check_table_exists('vocabulary'):
            logger.error("❌ vocabulary表创建失败")
            return False
        
        # 创建一些示例词汇数据（如果表为空）
        db = SessionLocal()
        try:
            # 检查是否已有词汇
            existing_count = db.query(Vocabulary).count()
            if existing_count == 0:
                logger.info("📝 创建示例词汇数据...")
                
                # 创建示例词汇
                sample_vocabulary = [
                    Vocabulary(
                        term="高炉",
                        definition="用于炼铁的大型冶金设备，通过还原反应将铁矿石转化为生铁",
                        category="设备",
                        synonyms=["炼铁炉", "鼓风炉"],
                        related_terms=["铁矿石", "焦炭", "生铁"]
                    ),
                    Vocabulary(
                        term="转炉",
                        definition="用于炼钢的设备，通过吹氧将生铁中的碳和其他杂质氧化去除",
                        category="设备",
                        synonyms=["炼钢炉", "氧气转炉"],
                        related_terms=["生铁", "钢水", "氧气"]
                    ),
                    Vocabulary(
                        term="连铸",
                        definition="将钢水连续浇铸成钢坯的工艺过程",
                        category="工艺",
                        synonyms=["连续铸造"],
                        related_terms=["钢水", "钢坯", "浇铸"]
                    ),
                    Vocabulary(
                        term="热轧",
                        definition="在高温下对钢坯进行轧制加工的工艺",
                        category="工艺",
                        synonyms=["热加工"],
                        related_terms=["钢坯", "钢板", "轧制"]
                    ),
                    Vocabulary(
                        term="冷轧",
                        definition="在常温下对钢板进行轧制加工的工艺",
                        category="工艺",
                        synonyms=["冷加工"],
                        related_terms=["钢板", "薄板", "轧制"]
                    )
                ]
                
                for vocab in sample_vocabulary:
                    db.add(vocab)
                
                db.commit()
                logger.info(f"✅ 创建了 {len(sample_vocabulary)} 个示例词汇")
                
            else:
                logger.info(f"✅ 已存在 {existing_count} 个词汇，跳过示例数据创建")
                
        except Exception as e:
            logger.error(f"❌ 创建示例数据失败: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("🎉 vocabulary表迁移完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        raise

def main():
    """主函数"""
    logger.info("🚀 开始vocabulary表迁移...")
    success = migrate_add_vocabulary_table()
    
    if success:
        logger.info("=" * 50)
        logger.info("✅ 迁移成功完成！")
        logger.info("")
        logger.info("新增的表:")
        logger.info("  - vocabulary: 专业词汇表")
        logger.info("")
        logger.info("API接口已可用:")
        logger.info("  - GET /api/admin/vocabulary - 获取词汇列表")
        logger.info("  - POST /api/admin/vocabulary - 创建新词汇")
        logger.info("  - PUT /api/admin/vocabulary/{id} - 更新词汇")
        logger.info("  - DELETE /api/admin/vocabulary/{id} - 删除词汇")
        logger.info("  - GET /api/admin/vocabulary/search - 搜索词汇")
    else:
        logger.error("❌ 迁移失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
