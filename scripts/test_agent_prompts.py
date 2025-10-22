#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Agent 类型和 Prompt 加载功能
验证不同 agent_type 是否能正确加载对应的 system_prompt
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.db import SessionLocal
from src.prompt_management.service import PromptService
from src.api.models import AgentType, PromptStatus


def test_agent_prompts():
    """测试 Agent 和 Prompt 加载"""
    print("=" * 80)
    print("测试 Agent 类型和 Prompt 加载功能")
    print("=" * 80)

    db = SessionLocal()
    try:
        prompt_service = PromptService(db)

        # 1. 测试所有 Agent 类型
        print("\n【1】列出所有活跃的 Agent:")
        print("-" * 80)
        agents = prompt_service.list_agents(is_active=True)
        if not agents:
            print("⚠️  数据库中没有活跃的 Agent")
            print("\n建议操作:")
            print(
                "1. 运行 'python scripts/db_migrate.py add-prompts' 创建默认 Prompt 表"
            )
            print(
                "2. 运行 'python scripts/enhance_steel_vocabulary.py' 创建钢铁专业 Agents"
            )
            return

        for agent in agents:
            print(
                f"  • {agent.agent_type:15s} | {agent.name:30s} | {agent.display_name}"
            )

        # 2. 测试每个 Agent 类型的 Prompt
        print("\n【2】测试每个 Agent 类型的 Prompt 加载:")
        print("-" * 80)

        agent_types = [
            "general",
            "process",
            "equipment",
            "market",
            "quality",
            "environment",
        ]

        for agent_type in agent_types:
            print(f"\n测试 {agent_type} Agent:")

            # 查找该类型的 Agent
            agents = prompt_service.list_agents(
                agent_type=agent_type, is_active=True, limit=1
            )

            if not agents:
                print(f"  ❌ 未找到 {agent_type} 类型的 Agent")
                continue

            agent = agents[0]
            print(f"  ✅ 找到 Agent: {agent.name} (ID: {agent.id})")

            # 获取该 Agent 的活跃 Prompt
            prompt = prompt_service.get_agent_prompt(
                agent_id=agent.id,
                language="zh-CN",
                use_cache=False,  # 测试时不使用缓存
            )

            if not prompt:
                print(f"  ⚠️  该 Agent 没有活跃的 Prompt")

                # 尝试查找所有 Prompt
                from src.prompt_management.schemas import PromptSearchRequest

                search_req = PromptSearchRequest(
                    agent_id=agent.id, page=1, page_size=10
                )
                search_result = prompt_service.search_prompts(search_req)

                if search_result.items:
                    print(
                        f"  ℹ️  该 Agent 有 {len(search_result.items)} 个 Prompt，但都未激活:"
                    )
                    for p in search_result.items:
                        print(
                            f"      - {p.name} (状态: {p.status}, 是否默认: {p.is_default})"
                        )
                else:
                    print(f"  ⚠️  该 Agent 完全没有 Prompt")
                continue

            print(f"  ✅ 找到活跃 Prompt:")
            print(f"      ID: {prompt.id}")
            print(f"      名称: {prompt.name}")
            print(f"      版本: {prompt.version}")
            print(f"      状态: {prompt.status}")
            print(f"      语言: {prompt.language}")
            print(f"      是否默认: {prompt.is_default}")
            print(f"      内容长度: {len(prompt.content)} 字符")
            print(f"      内容预览 (前200字符):")
            print(f"      {prompt.content[:200]}...")

        # 3. 测试 Prompt 统计
        print("\n【3】Prompt 统计信息:")
        print("-" * 80)

        from src.prompt_management.schemas import PromptSearchRequest

        search_req = PromptSearchRequest(page=1, page_size=100)
        all_prompts = prompt_service.search_prompts(search_req)

        print(f"  总 Prompt 数量: {all_prompts.total}")

        # 按状态统计
        status_count = {}
        for p in all_prompts.items:
            status_count[p.status] = status_count.get(p.status, 0) + 1

        print(f"  按状态统计:")
        for status, count in status_count.items():
            print(f"    - {status}: {count}")

        # 按语言统计
        lang_count = {}
        for p in all_prompts.items:
            lang_count[p.language] = lang_count.get(p.language, 0) + 1

        print(f"  按语言统计:")
        for lang, count in lang_count.items():
            print(f"    - {lang}: {count}")

        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


def create_test_agents():
    """创建测试用的 Agent 和 Prompt"""
    print("=" * 80)
    print("创建测试 Agent 和 Prompt")
    print("=" * 80)

    db = SessionLocal()
    try:
        prompt_service = PromptService(db)

        # 定义测试 Agent 配置
        test_agents = [
            {
                "name": "general_assistant_test",
                "agent_type": "general",
                "display_name": "通用助手（测试）",
                "description": "通用 AI 助手，可以回答各种问题",
                "prompt_content": """你是一个专业的AI助手，具备广泛的知识基础。

核心能力：
- 多领域知识问答
- 逻辑推理与分析
- 信息整理与总结

请用清晰、准确的语言回答用户的问题。""",
            },
            {
                "name": "process_expert_test",
                "agent_type": "process",
                "display_name": "工艺专家（测试）",
                "description": "钢铁生产工艺专家，专注于生产流程优化",
                "prompt_content": """你是钢铁生产工艺专家，专注于钢铁生产流程的优化和问题解决。

专业领域：
- 炼钢工艺流程
- 连铸工艺参数
- 轧制工艺控制
- 生产效率优化

回答时请：
1. 使用专业术语，但确保清晰易懂
2. 提供具体的工艺参数建议
3. 考虑实际生产环境的约束条件""",
            },
            {
                "name": "equipment_maintenance_test",
                "agent_type": "equipment",
                "display_name": "设备维护专家（测试）",
                "description": "设备维护专家，专注于设备故障诊断和维护",
                "prompt_content": """你是设备维护专家，专注于钢铁设备的故障诊断和维护保养。

专业领域：
- 设备故障诊断
- 维护保养计划
- 备件管理建议
- 设备改造升级

回答时请：
1. 提供系统化的故障排查步骤
2. 强调安全注意事项
3. 给出预防性维护建议""",
            },
        ]

        created_count = 0
        for agent_config in test_agents:
            # 检查 Agent 是否已存在
            existing = prompt_service.get_agent_by_name(agent_config["name"])
            if existing:
                print(f"⚠️  Agent '{agent_config['name']}' 已存在，跳过")
                continue

            # 创建 Agent
            from src.prompt_management.schemas import AgentCreate

            agent_data = AgentCreate(
                name=agent_config["name"],
                agent_type=agent_config["agent_type"],
                display_name=agent_config["display_name"],
                description=agent_config["description"],
                is_active=True,
            )

            agent = prompt_service.create_agent(agent_data)
            print(f"✅ 创建 Agent: {agent.name} (ID: {agent.id})")

            # 创建对应的 Prompt
            from src.prompt_management.schemas import SystemPromptCreate

            prompt_data = SystemPromptCreate(
                agent_id=agent.id,
                name=f"{agent.name}_default_prompt",
                content=agent_config["prompt_content"],
                version="1.0.0",
                is_default=True,
                language="zh-CN",
            )

            prompt = prompt_service.create_prompt(prompt_data)
            print(f"  ✅ 创建 Prompt: {prompt.name} (ID: {prompt.id})")

            # 激活 Prompt
            prompt_service.activate_prompt(prompt.id)
            print(f"  ✅ 激活 Prompt")

            created_count += 1

        print(f"\n总计创建 {created_count} 个 Agent 和 Prompt")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 创建失败: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试 Agent 类型和 Prompt 加载功能")
    parser.add_argument(
        "--create", action="store_true", help="创建测试用的 Agent 和 Prompt"
    )

    args = parser.parse_args()

    if args.create:
        create_test_agents()
    else:
        test_agent_prompts()
