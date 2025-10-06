#!/usr/bin/env python3
"""
创建 AI 助手角色到数据库
"""

import asyncio
from datetime import datetime
from src.api.db import get_db
from src.prompt_management.service import PromptService
from src.prompt_management.schemas import AgentCreate

# 定义 AI 助手角色配置
AGENTS_CONFIG = [
    {
        "name": "general",
        "display_name": "通用助手",
        "agent_type": "general",
        "description": "通用 AI 助手，可以帮助解答各类问题",
        "icon": "Bot",
        "color": "bg-primary",
        "capabilities": {
            "primary": ["问答", "对话", "信息查询", "通用咨询"],
            "greeting": "您好！我是通用AI助手，可以帮您解答各类问题。"
        },
        "use_cases": {
            "scenarios": ["日常问答", "信息查询", "通用咨询"],
            "examples": ["基础知识查询", "信息检索", "通用咨询"]
        },
        "tags": {
            "category": ["通用", "助手", "问答"],
            "level": "basic"
        }
    },
    {
        "name": "process",
        "display_name": "工艺专家",
        "agent_type": "process",
        "description": "钢铁工艺专家，专注于生产工艺咨询和优化建议",
        "icon": "FlaskConical",
        "color": "bg-secondary",
        "capabilities": {
            "primary": ["工艺分析", "生产优化", "技术咨询", "工艺改进"],
            "greeting": "您好！我是钢铁工艺专家，专注于生产工艺咨询和优化建议。"
        },
        "use_cases": {
            "scenarios": ["生产工艺咨询", "工艺参数优化", "技术问题解答"],
            "examples": ["炼钢工艺优化", "轧钢参数调整", "工艺流程改进"]
        },
        "tags": {
            "category": ["工艺", "生产", "技术", "优化"],
            "level": "expert"
        }
    },
    {
        "name": "equipment",
        "display_name": "设备诊断",
        "agent_type": "equipment",
        "description": "设备诊断专家，可以帮助诊断设备故障并提供维护建议",
        "icon": "Wrench",
        "color": "bg-primary",
        "capabilities": {
            "primary": ["故障诊断", "设备维护", "预防性维护", "维修指导"],
            "greeting": "您好！我是设备诊断专家，可以帮您诊断设备故障并提供维护建议。"
        },
        "use_cases": {
            "scenarios": ["设备故障诊断", "维护计划制定", "维修指导"],
            "examples": ["设备故障排查", "维护计划制定", "维修方案建议"]
        },
        "tags": {
            "category": ["设备", "诊断", "维护", "故障"],
            "level": "specialist"
        }
    },
    {
        "name": "market",
        "display_name": "市场分析师",
        "agent_type": "market",
        "description": "市场分析师，为您提供市场行情和趋势分析",
        "icon": "TrendingUp",
        "color": "bg-accent",
        "capabilities": {
            "primary": ["市场分析", "价格预测", "趋势分析", "行业洞察"],
            "greeting": "您好！我是市场分析师，为您提供市场行情和趋势分析。"
        },
        "use_cases": {
            "scenarios": ["市场行情分析", "价格趋势预测", "投资决策支持"],
            "examples": ["钢材价格分析", "市场趋势预测", "投资建议"]
        },
        "tags": {
            "category": ["市场", "分析", "趋势", "价格"],
            "level": "analyst"
        }
    },
    {
        "name": "quality",
        "display_name": "质量顾问",
        "agent_type": "quality",
        "description": "质量顾问，专注于质量控制和参数优化",
        "icon": "ShieldCheck",
        "color": "bg-muted",
        "capabilities": {
            "primary": ["质量控制", "参数优化", "质量检测", "标准制定"],
            "greeting": "您好！我是质量顾问，专注于质量控制和参数优化。"
        },
        "use_cases": {
            "scenarios": ["质量问题分析", "参数优化建议", "质量标准制定"],
            "examples": ["产品质量检测", "质量标准制定", "质量改进方案"]
        },
        "tags": {
            "category": ["质量", "控制", "优化", "标准"],
            "level": "consultant"
        }
    },
    {
        "name": "environment",
        "display_name": "节能专家",
        "agent_type": "environment",
        "description": "节能专家，帮助您优化能源使用和降低成本",
        "icon": "Zap",
        "color": "bg-secondary",
        "capabilities": {
            "primary": ["能源分析", "节能优化", "成本控制", "环保建议"],
            "greeting": "您好！我是节能专家，帮助您优化能源使用和降低成本。"
        },
        "use_cases": {
            "scenarios": ["能源使用优化", "节能方案制定", "成本降低建议"],
            "examples": ["能耗数据分析", "节能技术推荐", "成本效益分析"]
        },
        "tags": {
            "category": ["节能", "环保", "成本", "优化"],
            "level": "expert"
        }
    }
]

def create_agents():
    """创建所有 AI 助手角色"""
    # 获取数据库连接
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 创建服务实例
        service = PromptService(db)
        
        created_agents = []
        
        for agent_config in AGENTS_CONFIG:
            print(f"创建 Agent: {agent_config['display_name']}")
            
            try:
                # 创建 Agent 数据
                agent_data = AgentCreate(
                    name=agent_config["name"],
                    agent_type=agent_config["agent_type"],
                    display_name=agent_config["display_name"],
                    description=agent_config["description"],
                    icon=agent_config["icon"],
                    color=agent_config["color"],
                    capabilities=agent_config["capabilities"],
                    use_cases=agent_config["use_cases"],
                    tags=agent_config["tags"],
                    is_active=True
                )
                
                # 创建 Agent
                agent = service.create_agent(agent_data, created_by=1)  # 使用管理员用户 ID
                created_agents.append(agent)
                
                print(f"✅ 成功创建 Agent: {agent.display_name} (ID: {agent.id})")
                
            except ValueError as e:
                if "already exists" in str(e):
                    print(f"⚠️  Agent 已存在，跳过: {agent_config['display_name']}")
                    continue
                else:
                    print(f"❌ 创建 Agent 时出错: {e}")
                    raise
            except Exception as e:
                print(f"❌ 创建 Agent 时出错: {e}")
                raise
        
        print(f"\n🎉 总共创建了 {len(created_agents)} 个 AI 助手角色")
        
        # 验证创建结果
        all_agents = service.list_agents()
        print(f"数据库中现有 Agent 数量: {len(all_agents)}")
        
        return created_agents
        
    except Exception as e:
        print(f"❌ 创建 Agent 时出错: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_agents()