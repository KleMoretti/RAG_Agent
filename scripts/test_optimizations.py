"""
测试系统优化效果：
1. 意图识别（智能判断是否需要 RAG）
2. Agent 差异化回答
"""

import asyncio
import httpx
import time
from typing import Any

# 测试用例
TEST_CASES = [
    # 简单问候（不应使用 RAG）
    {"query": "你好", "expected_rag": False, "category": "问候"},
    {"query": "早上好", "expected_rag": False, "category": "问候"},
    {"query": "谢谢", "expected_rag": False, "category": "问候"},
    
    # 闲聊（不应使用 RAG）
    {"query": "今天天气怎么样", "expected_rag": False, "category": "闲聊"},
    {"query": "你叫什么名字", "expected_rag": False, "category": "闲聊"},
    
    # 专业问题（应使用 RAG）
    {"query": "Q235的抗拉强度是多少？", "expected_rag": True, "category": "专业查询"},
    {"query": "如何控制炼钢过程中的温度？", "expected_rag": True, "category": "专业查询"},
    {"query": "转炉和电炉有什么区别？", "expected_rag": True, "category": "专业查询"},
]

# 不同 Agent 对比测试
COMPARE_QUERIES = [
    "炼钢过程中温度控制有什么注意事项？",
    "设备出现异响怎么办？",
    "铁矿石价格走势如何？",
]


async def test_single_query(client: httpx.AsyncClient, query: str, agent_type: str = "general") -> dict[str, Any]:
    """测试单个查询"""
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": query,
        "agent_type": agent_type,
        "session_id": f"test_{agent_type}_{int(time.time())}"
    }
    
    try:
        start = time.time()
        response = await client.post(url, json=payload, timeout=30.0)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", ""),
                "fallback_mode": data.get("fallback_mode", False),
                "intent_skip_rag": data.get("intent_skip_rag", False),
                "intent_reason": data.get("intent_reason"),
                "elapsed": elapsed,
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "elapsed": elapsed,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "elapsed": 0,
        }


async def test_intent_classification():
    """测试意图识别功能"""
    print("=" * 80)
    print("【测试 1】意图识别 - 智能判断是否需要 RAG")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient() as client:
        results = []
        
        for test_case in TEST_CASES:
            query = test_case["query"]
            expected_rag = test_case["expected_rag"]
            category = test_case["category"]
            
            print(f"📝 测试查询: {query} ({category})")
            result = await test_single_query(client, query)
            
            if result["success"]:
                intent_skip = result.get("intent_skip_rag", False)
                used_rag = not intent_skip and not result.get("fallback_mode", False)
                
                # 判断是否符合预期
                correct = (used_rag == expected_rag)
                status = "✅ 正确" if correct else "❌ 错误"
                
                print(f"   预期: {'使用RAG' if expected_rag else '跳过RAG'}")
                print(f"   实际: {'使用RAG' if used_rag else '跳过RAG'} ({result.get('intent_reason', 'N/A')})")
                print(f"   结果: {status}")
                print(f"   耗时: {result['elapsed']:.2f}s")
                
                results.append({
                    "query": query,
                    "expected": expected_rag,
                    "actual": used_rag,
                    "correct": correct,
                })
            else:
                print(f"   ❌ 请求失败: {result.get('error')}")
            
            print()
        
        # 统计准确率
        if results:
            correct_count = sum(1 for r in results if r["correct"])
            accuracy = correct_count / len(results) * 100
            
            print("=" * 80)
            print(f"意图识别准确率: {correct_count}/{len(results)} = {accuracy:.1f}%")
            print("=" * 80)
            print()


async def test_agent_differences():
    """测试不同 Agent 的回答差异"""
    print("=" * 80)
    print("【测试 2】Agent 差异化 - 相同问题不同 Agent 的回答对比")
    print("=" * 80)
    print()
    
    agent_types = ["general", "process", "equipment", "market"]
    
    async with httpx.AsyncClient() as client:
        for query in COMPARE_QUERIES:
            print(f"🔍 测试问题: {query}")
            print("-" * 80)
            
            responses = {}
            
            for agent_type in agent_types:
                result = await test_single_query(client, query, agent_type)
                
                if result["success"]:
                    response_text = result["response"][:200]  # 只显示前200字符
                    responses[agent_type] = {
                        "text": response_text,
                        "length": len(result["response"]),
                        "elapsed": result["elapsed"],
                    }
                    
                    print(f"\n【{agent_type} Agent】")
                    print(f"回答长度: {responses[agent_type]['length']} 字符")
                    print(f"耗时: {responses[agent_type]['elapsed']:.2f}s")
                    print(f"前200字: {response_text}...")
                else:
                    print(f"\n【{agent_type} Agent】")
                    print(f"❌ 失败: {result.get('error')}")
            
            # 分析差异
            if len(responses) >= 2:
                lengths = [r["length"] for r in responses.values()]
                avg_length = sum(lengths) / len(lengths)
                max_diff = max(lengths) - min(lengths)
                
                print(f"\n📊 差异分析:")
                print(f"   平均长度: {avg_length:.0f} 字符")
                print(f"   最大差异: {max_diff} 字符")
                print(f"   长度变异系数: {(max_diff / avg_length * 100):.1f}%")
            
            print("\n" + "=" * 80 + "\n")


async def main():
    """主测试函数"""
    print("\n")
    print("🚀 系统优化效果测试")
    print("=" * 80)
    print("测试内容:")
    print("1. 意图识别 - 智能判断是否需要 RAG")
    print("2. Agent 差异化 - 不同 Agent 回答的差异性")
    print()
    print("⚠️  请确保后端服务已启动: python manage.py start backend")
    print("=" * 80)
    print()
    
    input("按 Enter 键开始测试...")
    print()
    
    try:
        # 测试 1: 意图识别
        await test_intent_classification()
        
        # 测试 2: Agent 差异化
        await test_agent_differences()
        
        print("✅ 所有测试完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

