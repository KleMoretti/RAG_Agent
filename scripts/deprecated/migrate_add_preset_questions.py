#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 此脚本已废弃，请使用新的统一 CLI 工具

推荐使用: python scripts/db_migrate.py add-presets

数据库迁移脚本：添加Agent预设问题表
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config.settings import get_settings
from src.api.db import Base
from src.api.models import Agent, AgentPresetQuestion
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_preset_questions_table():
    """创建Agent预设问题表"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    try:
        # 创建表
        logger.info("创建Agent预设问题表...")
        Base.metadata.create_all(engine, tables=[AgentPresetQuestion.__table__])
        logger.info("✅ Agent预设问题表创建成功")
        
        return True
    except Exception as e:
        logger.error(f"❌ 创建表失败: {e}")
        return False


def insert_default_preset_questions():
    """插入默认的预设问题数据"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    # 优化后的差异化预设问题
    default_questions = {
        "general": [
            {
                "title": "行业发展现状",
                "question": "请分析当前中国钢铁行业的发展现状、主要挑战和未来机遇",
                "category": "industry_overview",
                "order_index": 1,
                "difficulty_level": "basic",
                "tags": ["行业分析", "发展趋势", "市场概况"]
            },
            {
                "title": "数字化转型策略",
                "question": "钢铁企业如何制定和实施数字化转型战略，提升智能制造水平？",
                "category": "digital_transformation",
                "order_index": 2,
                "difficulty_level": "intermediate",
                "tags": ["数字化", "智能制造", "转型升级"]
            },
            {
                "title": "政策法规影响",
                "question": "近期国家出台的钢铁行业相关政策对企业经营有哪些具体影响？",
                "category": "policy_analysis",
                "order_index": 3,
                "difficulty_level": "intermediate",
                "tags": ["政策解读", "法规分析", "合规管理"]
            },
            {
                "title": "国际竞争格局",
                "question": "在全球钢铁贸易格局变化下，中国钢企如何提升国际竞争力？",
                "category": "global_competition",
                "order_index": 4,
                "difficulty_level": "advanced",
                "tags": ["国际贸易", "竞争策略", "全球化"]
            }
        ],
        "process": [
            {
                "title": "转炉炼钢优化",
                "question": "转炉炼钢过程中如何精确控制脱碳速率和终点温度，提高钢水纯净度？",
                "category": "steelmaking",
                "order_index": 1,
                "difficulty_level": "advanced",
                "tags": ["转炉炼钢", "工艺控制", "质量提升"]
            },
            {
                "title": "连铸工艺改进",
                "question": "连铸过程中如何通过优化拉速和二冷配水减少铸坯内部缺陷？",
                "category": "continuous_casting",
                "order_index": 2,
                "difficulty_level": "advanced",
                "tags": ["连铸技术", "缺陷控制", "工艺优化"]
            },
            {
                "title": "轧制参数设计",
                "question": "热轧带钢生产中如何设计轧制规程，平衡产品性能与生产效率？",
                "category": "rolling",
                "order_index": 3,
                "difficulty_level": "intermediate",
                "tags": ["热轧工艺", "参数设计", "性能控制"]
            },
            {
                "title": "合金化技术",
                "question": "微合金化钢生产中，Nb、Ti、V等元素的最佳添加时机和配比如何确定？",
                "category": "alloying",
                "order_index": 4,
                "difficulty_level": "advanced",
                "tags": ["微合金化", "成分设计", "性能调控"]
            }
        ],
        "equipment": [
            {
                "title": "高炉炉况诊断",
                "question": "高炉出现炉缸侵蚀加剧和炉温分布不均时，如何进行系统性诊断和处理？",
                "category": "blast_furnace",
                "order_index": 1,
                "difficulty_level": "advanced",
                "tags": ["高炉诊断", "炉况分析", "设备维护"]
            },
            {
                "title": "轧机振动分析",
                "question": "四辊轧机出现异常振动和轧制力波动，如何通过频谱分析定位故障源？",
                "category": "rolling_mill",
                "order_index": 2,
                "difficulty_level": "advanced",
                "tags": ["振动诊断", "故障分析", "精密设备"]
            },
            {
                "title": "预测性维护",
                "question": "如何建立关键设备的预测性维护体系，实现从计划维修向状态维修转变？",
                "category": "predictive_maintenance",
                "order_index": 3,
                "difficulty_level": "intermediate",
                "tags": ["预测维护", "状态监测", "维修策略"]
            },
            {
                "title": "设备数字化改造",
                "question": "老旧烧结机如何进行数字化改造，集成IoT传感器和智能控制系统？",
                "category": "digitalization",
                "order_index": 4,
                "difficulty_level": "intermediate",
                "tags": ["数字化改造", "智能控制", "设备升级"]
            }
        ],
        "market": [
            {
                "title": "原料价格预测",
                "question": "基于全球供需格局和地缘政治因素，如何预测未来6个月铁矿石价格走势？",
                "category": "raw_materials",
                "order_index": 1,
                "difficulty_level": "advanced",
                "tags": ["价格预测", "供需分析", "风险评估"]
            },
            {
                "title": "产品定价策略",
                "question": "在原料成本波动和市场竞争加剧背景下，如何制定差异化产品定价策略？",
                "category": "pricing_strategy",
                "order_index": 2,
                "difficulty_level": "intermediate",
                "tags": ["定价策略", "成本分析", "竞争策略"]
            },
            {
                "title": "供应链风险管理",
                "question": "如何构建多元化供应链体系，降低原料供应中断和价格暴涨风险？",
                "category": "supply_chain",
                "order_index": 3,
                "difficulty_level": "intermediate",
                "tags": ["供应链", "风险管理", "采购策略"]
            },
            {
                "title": "期货套期保值",
                "question": "钢铁企业如何运用铁矿石和螺纹钢期货进行套期保值，锁定生产利润？",
                "category": "hedging",
                "order_index": 4,
                "difficulty_level": "advanced",
                "tags": ["期货交易", "套期保值", "风险对冲"]
            }
        ],
        "quality": [
            {
                "title": "成分精确控制",
                "question": "汽车用钢生产中如何实现C、Mn、Si等元素的±0.01%精确控制？",
                "category": "composition_control",
                "order_index": 1,
                "difficulty_level": "advanced",
                "tags": ["成分控制", "精密制造", "汽车钢"]
            },
            {
                "title": "表面质量提升",
                "question": "冷轧薄板表面出现氧化色差和微细划痕，如何通过工艺调整改善表面质量？",
                "category": "surface_quality",
                "order_index": 2,
                "difficulty_level": "intermediate",
                "tags": ["表面质量", "冷轧工艺", "缺陷控制"]
            },
            {
                "title": "力学性能优化",
                "question": "高强钢生产中如何平衡强度、塑性和韧性，实现综合性能最优化？",
                "category": "mechanical_properties",
                "order_index": 3,
                "difficulty_level": "advanced",
                "tags": ["力学性能", "性能平衡", "高强钢"]
            },
            {
                "title": "在线检测技术",
                "question": "如何应用激光测厚、涡流探伤等在线检测技术提高质量控制精度？",
                "category": "online_testing",
                "order_index": 4,
                "difficulty_level": "intermediate",
                "tags": ["在线检测", "质量控制", "检测技术"]
            }
        ],
        "environment": [
            {
                "title": "超低排放改造",
                "question": "钢铁企业如何实施超低排放改造，确保颗粒物、SO₂、NOₓ稳定达标？",
                "category": "ultra_low_emission",
                "order_index": 1,
                "difficulty_level": "advanced",
                "tags": ["超低排放", "环保改造", "达标治理"]
            },
            {
                "title": "碳减排路径",
                "question": "钢铁企业实现碳中和目标的技术路径和时间节点如何规划？",
                "category": "carbon_reduction",
                "order_index": 2,
                "difficulty_level": "advanced",
                "tags": ["碳中和", "减排技术", "绿色发展"]
            },
            {
                "title": "固废资源化",
                "question": "钢渣、除尘灰等固体废物如何实现高值化利用和资源化处理？",
                "category": "waste_utilization",
                "order_index": 3,
                "difficulty_level": "intermediate",
                "tags": ["固废处理", "资源化利用", "循环经济"]
            },
            {
                "title": "氢能炼钢技术",
                "question": "氢基直接还原技术在中国钢铁工业的应用前景和技术挑战是什么？",
                "category": "hydrogen_metallurgy",
                "order_index": 4,
                "difficulty_level": "advanced",
                "tags": ["氢能冶金", "清洁技术", "技术创新"]
            }
        ]
    }
    
    try:
        with engine.connect() as conn:
            # 首先获取所有Agent的ID
            result = conn.execute(text("SELECT name, id FROM agent"))
            agent_map = {row[0]: row[1] for row in result}
            
            logger.info(f"找到 {len(agent_map)} 个Agent: {list(agent_map.keys())}")
            
            # 清空现有的预设问题
            conn.execute(text("DELETE FROM agent_preset_question"))
            conn.commit()
            logger.info("清空现有预设问题数据")
            
            # 插入新的预设问题
            total_inserted = 0
            for agent_name, questions in default_questions.items():
                if agent_name not in agent_map:
                    logger.warning(f"Agent '{agent_name}' 不存在，跳过")
                    continue
                
                agent_id = agent_map[agent_name]
                for question_data in questions:
                    import json
                    conn.execute(text("""
                        INSERT INTO agent_preset_question 
                        (agent_id, title, question, category, order_index, difficulty_level, tags, is_active, usage_count, created_at, updated_at)
                        VALUES (:agent_id, :title, :question, :category, :order_index, :difficulty_level, :tags, true, 0, NOW(), NOW())
                    """), {
                        "agent_id": agent_id,
                        "title": question_data["title"],
                        "question": question_data["question"],
                        "category": question_data["category"],
                        "order_index": question_data["order_index"],
                        "difficulty_level": question_data["difficulty_level"],
                        "tags": json.dumps(question_data["tags"], ensure_ascii=False)  # 正确的JSON格式
                    })
                    total_inserted += 1
                
                logger.info(f"为Agent '{agent_name}' 插入了 {len(questions)} 个预设问题")
            
            conn.commit()
            logger.info(f"✅ 成功插入 {total_inserted} 个预设问题")
            return True
            
    except Exception as e:
        logger.error(f"❌ 插入预设问题失败: {e}")
        return False


def main():
    """主函数"""
    logger.info("开始Agent预设问题表迁移...")
    
    # 创建表
    if not create_preset_questions_table():
        logger.error("表创建失败，退出")
        return False
    
    # 插入默认数据
    if not insert_default_preset_questions():
        logger.error("数据插入失败，退出")
        return False
    
    logger.info("🎉 Agent预设问题表迁移完成！")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)