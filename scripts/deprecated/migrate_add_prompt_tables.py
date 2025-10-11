#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 此脚本已废弃，请使用新的统一 CLI 工具

推荐使用: python scripts/db_migrate.py add-prompts

添加prompt管理表的数据库迁移脚本
使用方法: python scripts/migrate_add_prompt_tables.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from src.api.db import SessionLocal, engine, Base
from src.api.models import User, UserRole
import src.prompt_management  # 导入prompt管理模型
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_add_prompt_tables():
    """添加prompt管理相关表"""
    try:
        # 检查是否需要迁移
        tables_to_check = ['agent', 'system_prompt', 'prompt_version', 'prompt_usage_stats']
        existing_tables = [table for table in tables_to_check if check_table_exists(table)]
        
        if len(existing_tables) == len(tables_to_check):
            logger.info("✅ 所有prompt管理表已存在，无需迁移")
            return
        
        logger.info("🔄 开始添加prompt管理表...")
        
        # 创建新表（只会创建不存在的表）
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Prompt管理表创建成功")
        
        # 验证表是否创建成功
        missing_tables = [table for table in tables_to_check if not check_table_exists(table)]
        if missing_tables:
            logger.error(f"❌ 以下表创建失败: {missing_tables}")
            return False
        
        # 创建一些示例Agent（如果agents表为空）
        db = SessionLocal()
        try:
            from src.api.models import Agent, AgentType
            
            # 检查是否已有Agent
            existing_agents = db.query(Agent).count()
            if existing_agents == 0:
                logger.info("📝 创建示例Agent...")
                
                # 创建示例Agent
                sample_agents = [
                    Agent(
                        name="RAG智能问答助手",
                        agent_type=AgentType.RAG_AGENT,
                        description="基于知识库的智能问答系统，能够检索相关文档并生成准确回答",
                        capabilities=["文档检索", "智能问答", "上下文理解", "多轮对话"],
                        is_active=True
                    ),
                    Agent(
                        name="钢铁生产分析师",
                        agent_type=AgentType.ANALYSIS_AGENT,
                        description="专业的钢铁生产数据分析助手，提供生产效率和质量分析",
                        capabilities=["生产数据分析", "效率优化建议", "质量控制", "趋势预测"],
                        is_active=True
                    ),
                    Agent(
                        name="设备维护专家",
                        agent_type=AgentType.MAINTENANCE_AGENT,
                        description="设备故障诊断和维护建议专家系统",
                        capabilities=["故障诊断", "维护计划", "设备监控", "预防性维护"],
                        is_active=True
                    ),
                    Agent(
                        name="市场情报分析师",
                        agent_type=AgentType.MARKET_AGENT,
                        description="钢铁市场价格分析和趋势预测专家",
                        capabilities=["价格分析", "市场趋势", "供需预测", "竞争分析"],
                        is_active=True
                    )
                ]
                
                for agent in sample_agents:
                    db.add(agent)
                
                db.commit()
                logger.info(f"✅ 创建了 {len(sample_agents)} 个示例Agent")
                
                # 为每个Agent创建默认prompt（这将由PromptService自动处理）
                from src.prompt_management.service import PromptService
                prompt_service = PromptService(db)
                
                for agent in sample_agents:
                    db.refresh(agent)  # 获取ID
                    logger.info(f"   - {agent.name} (ID: {agent.id})")
                
            else:
                logger.info(f"✅ 已存在 {existing_agents} 个Agent，跳过示例数据创建")
                
        except Exception as e:
            logger.error(f"❌ 创建示例数据失败: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("🎉 Prompt管理表迁移完成！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        raise

def main():
    """主函数"""
    logger.info("🚀 开始prompt管理表迁移...")
    success = migrate_add_prompt_tables()
    
    if success:
        logger.info("=" * 50)
        logger.info("✅ 迁移成功完成！")
        logger.info("")
        logger.info("新增的表:")
        logger.info("  - agents: AI Agent定义")
        logger.info("  - system_prompts: 系统提示词")
        logger.info("  - prompt_versions: 提示词版本历史")
        logger.info("  - prompt_usage_stats: 使用统计")
        logger.info("")
        logger.info("API接口已可用:")
        logger.info("  - GET /api/v1/prompts/agents - 获取Agent列表")
        logger.info("  - GET /api/v1/prompts/agents/{agent_id}/active - 获取Agent的激活prompt")
        logger.info("  - POST /api/v1/prompts/ - 创建新prompt")
        logger.info("  - 更多接口请查看 /docs")
    else:
        logger.error("❌ 迁移失败")
        sys.exit(1)

if __name__ == "__main__":
    main()