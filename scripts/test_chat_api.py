#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试聊天 API 和不同 agent_type 的 Prompt 加载
验证后端是否正确根据 agent_type 加载对应的 system_prompt
"""

import requests
import json
from typing import Dict, Any


# API 配置
BASE_URL = "http://localhost:8000"
API_CHAT_URL = f"{BASE_URL}/api/chat"


def test_chat_with_agent_type(
    message: str, agent_type: str, session_id: str = "test_session"
) -> Dict[str, Any]:
    """
    测试带 agent_type 的聊天请求

    Args:
        message: 用户消息
        agent_type: Agent 类型（general, process, equipment, market, quality, environment）
        session_id: 会话ID

    Returns:
        API 响应
    """
    payload = {
        "message": message,
        "session_id": session_id,
        "agent_type": agent_type,
        "user_role": None,
    }

    print(f"\n{'=' * 80}")
    print(f"测试 Agent 类型: {agent_type}")
    print(f"{'=' * 80}")
    print(f"📤 发送消息: {message}")
    print(f"🔑 会话ID: {session_id}")
    print(f"🤖 Agent类型: {agent_type}")

    try:
        response = requests.post(
            API_CHAT_URL, json=payload, headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 响应成功 (状态码: {response.status_code})")
            print(f"📥 响应内容:")
            print(f"   {result.get('response', '')[:300]}...")
            print(f"   (总长度: {len(result.get('response', ''))} 字符)")

            if result.get("fallback_mode"):
                print(f"⚠️  注意: 使用了降级模式（RAG超时）")

            reasoning_steps = result.get("reasoning_steps", [])
            if reasoning_steps:
                print(f"🧠 推理步骤: {len(reasoning_steps)} 步")
            else:
                print(f"🧠 推理步骤: 无")

            return result
        else:
            print(f"\n❌ 请求失败 (状态码: {response.status_code})")
            print(f"错误信息: {response.text}")
            return {"error": response.text, "status_code": response.status_code}

    except requests.exceptions.ConnectionError:
        print(f"\n❌ 连接失败: 无法连接到 {BASE_URL}")
        print(f"请确保后端服务已启动: python manage.py start backend")
        return {"error": "Connection failed"}
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        return {"error": str(e)}


def run_comprehensive_test():
    """运行综合测试，测试所有 Agent 类型"""
    print("=" * 80)
    print("聊天 API 综合测试 - 验证不同 agent_type 的 Prompt 加载")
    print("=" * 80)

    # 测试用例：每个 Agent 类型对应一个专业问题
    test_cases = [
        {
            "agent_type": "general",
            "message": "你是谁？你能做什么？",
            "expected_keywords": ["AI助手", "知识", "问答"],
        },
        {
            "agent_type": "process",
            "message": "炼钢过程中如何控制温度？",
            "expected_keywords": ["工艺", "炼钢", "温度"],
        },
        {
            "agent_type": "equipment",
            "message": "轧机出现异常振动，应该如何排查？",
            "expected_keywords": ["设备", "故障", "诊断", "维护"],
        },
        {
            "agent_type": "market",
            "message": "目前钢材市场的价格趋势如何？",
            "expected_keywords": ["市场", "价格", "趋势", "分析"],
        },
        {
            "agent_type": "quality",
            "message": "如何提高钢材的表面质量？",
            "expected_keywords": ["质量", "控制"],
        },
        {
            "agent_type": "environment",
            "message": "钢铁生产如何降低能耗？",
            "expected_keywords": ["环保", "节能", "能耗"],
        },
    ]

    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}")
        result = test_chat_with_agent_type(
            message=test_case["message"],
            agent_type=test_case["agent_type"],
            session_id=f"test_session_{test_case['agent_type']}",
        )

        # 简单的响应质量检查
        if "response" in result:
            response_text = result["response"]
            keywords_found = [
                kw for kw in test_case["expected_keywords"] if kw in response_text
            ]
            print(
                f"\n✅ 关键词检查: 找到 {len(keywords_found)}/{len(test_case['expected_keywords'])} 个"
            )
            if keywords_found:
                print(f"   匹配的关键词: {', '.join(keywords_found)}")

        results.append(
            {
                "agent_type": test_case["agent_type"],
                "message": test_case["message"],
                "success": "response" in result,
                "result": result,
            }
        )

        # 避免请求过快
        import time

        time.sleep(1)

    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)

    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)

    print(f"总测试数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    print(f"成功率: {success_count / total_count * 100:.1f}%")

    print("\n各 Agent 类型测试结果:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['agent_type']:15s} - {r['message'][:40]}...")

    if success_count == total_count:
        print("\n🎉 所有测试通过！每个 Agent 类型都能正确加载专属 Prompt。")
    else:
        print("\n⚠️  部分测试失败，请检查后端日志。")


def test_same_message_different_agents():
    """测试相同消息在不同 Agent 下的响应差异"""
    print("\n" + "=" * 80)
    print("对比测试 - 相同问题在不同 Agent 下的响应")
    print("=" * 80)

    message = "钢铁生产中最重要的是什么？"
    agent_types = ["general", "process", "equipment", "quality"]

    responses = {}
    for agent_type in agent_types:
        result = test_chat_with_agent_type(
            message=message,
            agent_type=agent_type,
            session_id=f"compare_{agent_type}",
        )
        if "response" in result:
            responses[agent_type] = result["response"]

    # 对比分析
    print("\n" + "=" * 80)
    print("响应对比分析")
    print("=" * 80)

    for agent_type, response in responses.items():
        print(f"\n【{agent_type} Agent】")
        print(f"响应长度: {len(response)} 字符")
        print(f"前150字: {response[:150]}...")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试聊天 API 和 Agent 类型功能")
    parser.add_argument(
        "--comprehensive", action="store_true", help="运行综合测试（所有 Agent 类型）"
    )
    parser.add_argument(
        "--compare", action="store_true", help="对比测试（相同问题不同 Agent）"
    )
    parser.add_argument("--agent-type", type=str, help="指定 Agent 类型进行单次测试")
    parser.add_argument("--message", type=str, help="自定义消息内容")

    args = parser.parse_args()

    if args.comprehensive:
        run_comprehensive_test()
    elif args.compare:
        test_same_message_different_agents()
    elif args.agent_type and args.message:
        test_chat_with_agent_type(
            message=args.message, agent_type=args.agent_type, session_id="custom_test"
        )
    else:
        # 默认运行综合测试
        print("提示: 使用 --help 查看所有选项\n")
        run_comprehensive_test()
