#!/usr/bin/env python3
"""
测试领域分类器和Agent转发机制
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent.domain_classifier import get_domain_classifier, DomainClassifier


# 测试用例
TEST_CASES = [
    # 工艺专家领域
    {
        "query": "炼钢过程中如何控制温度？",
        "expected": "process",
        "description": "工艺参数控制问题"
    },
    {
        "query": "Q235钢的化学成分是什么？",
        "expected": "process",
        "description": "钢种成分问题"
    },
    {
        "query": "如何提高轧钢产能？",
        "expected": "process",
        "description": "工艺优化问题"
    },
    
    # 设备诊断领域
    {
        "query": "加热炉温度传感器故障怎么办？",
        "expected": "equipment",
        "description": "设备故障诊断"
    },
    {
        "query": "轧机振动异常如何排查？",
        "expected": "equipment",
        "description": "设备异常诊断"
    },
    {
        "query": "设备预防性维护计划如何制定？",
        "expected": "equipment",
        "description": "设备维护问题"
    },
    
    # 市场分析师领域
    {
        "query": "铁矿石最近的价格走势如何？",
        "expected": "market",
        "description": "市场价格问题"
    },
    {
        "query": "钢材市场供需情况分析",
        "expected": "market",
        "description": "供需分析问题"
    },
    {
        "query": "现在适合采购废钢吗？",
        "expected": "market",
        "description": "采购决策问题"
    },
    
    # 质量顾问领域
    {
        "query": "钢板表面裂纹是什么原因？",
        "expected": "quality",
        "description": "质量问题分析"
    },
    {
        "query": "如何检测钢材的抗拉强度？",
        "expected": "quality",
        "description": "质量检测方法"
    },
    {
        "query": "产品质量不合格如何改进？",
        "expected": "quality",
        "description": "质量改进问题"
    },
    
    # 节能专家领域
    {
        "query": "如何降低炼钢过程的能耗？",
        "expected": "environment",
        "description": "节能优化问题"
    },
    {
        "query": "废气排放超标怎么处理？",
        "expected": "environment",
        "description": "环保合规问题"
    },
    {
        "query": "余热回收系统如何设计？",
        "expected": "environment",
        "description": "能源回收问题"
    },
    
    # 通用助手领域
    {
        "query": "你好，请介绍一下自己",
        "expected": "general",
        "description": "问候和介绍"
    },
    {
        "query": "钢铁行业有哪些常见岗位？",
        "expected": "general",
        "description": "通用咨询问题"
    },
]


def test_domain_classification():
    """测试领域分类准确性"""
    classifier = get_domain_classifier()
    
    print("=" * 80)
    print("🧪 测试Agent领域分类器")
    print("=" * 80)
    print()
    
    correct = 0
    total = len(TEST_CASES)
    
    for i, case in enumerate(TEST_CASES, 1):
        query = case["query"]
        expected = case["expected"]
        description = case["description"]
        
        # 分类
        primary_domain, confidence, all_scores = classifier.classify(query)
        
        # 判断是否正确
        is_correct = primary_domain == expected
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        print(f"{status} 测试 {i}/{total}: {description}")
        print(f"   查询: {query}")
        print(f"   预期: {expected} | 实际: {primary_domain} | 置信度: {confidence:.2%}")
        
        # 显示所有得分
        if len(all_scores) > 1:
            print(f"   其他候选: {', '.join([f'{d}({s:.2%})' for d, s in all_scores[1:3]])}")
        
        print()
    
    # 统计结果
    accuracy = correct / total
    print("=" * 80)
    print(f"📊 测试结果统计")
    print("=" * 80)
    print(f"总测试用例: {total}")
    print(f"正确分类: {correct}")
    print(f"错误分类: {total - correct}")
    print(f"准确率: {accuracy:.2%}")
    print()
    
    if accuracy >= 0.9:
        print("🎉 优秀！分类器准确率 ≥ 90%")
    elif accuracy >= 0.8:
        print("👍 良好！分类器准确率 ≥ 80%")
    else:
        print("⚠️  需要改进！分类器准确率 < 80%")
    
    print()


def test_domain_boundary_check():
    """测试领域边界检查"""
    classifier = get_domain_classifier()
    
    print("=" * 80)
    print("🔍 测试Agent领域边界检查")
    print("=" * 80)
    print()
    
    # 测试场景：工艺专家收到市场问题
    test_scenarios = [
        {
            "agent": "process",
            "query": "铁矿石价格走势如何？",
            "should_redirect": True,
            "expected_target": "market"
        },
        {
            "agent": "process",
            "query": "炼钢温度如何控制？",
            "should_redirect": False,
            "expected_target": None
        },
        {
            "agent": "equipment",
            "query": "设备振动异常怎么办？",
            "should_redirect": False,
            "expected_target": None
        },
        {
            "agent": "equipment",
            "query": "如何降低能耗？",
            "should_redirect": True,
            "expected_target": "environment"
        },
        {
            "agent": "market",
            "query": "钢材质量如何检测？",
            "should_redirect": True,
            "expected_target": "quality"
        },
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        agent = scenario["agent"]
        query = scenario["query"]
        should_redirect = scenario["should_redirect"]
        expected_target = scenario["expected_target"]
        
        # 检查领域边界
        is_match, suggested_agent, reason = classifier.check_domain_match(
            query=query,
            current_agent=agent,
            threshold=0.5
        )
        
        # 判断结果
        is_correct = (not is_match) == should_redirect
        if should_redirect:
            is_correct = is_correct and (suggested_agent == expected_target)
        
        status = "✅" if is_correct else "❌"
        
        agent_info = classifier.get_domain_info(agent)
        print(f"{status} 场景 {i}: {agent_info['name']} 收到查询")
        print(f"   查询: {query}")
        print(f"   是否匹配: {'是' if is_match else '否'}")
        
        if not is_match and suggested_agent:
            target_info = classifier.get_domain_info(suggested_agent)
            print(f"   建议转发: {target_info['name']}")
            print(f"   理由: {reason}")
        else:
            print(f"   判断: {reason}")
        
        print()
    
    print("=" * 80)


def test_cross_domain_questions():
    """测试跨领域问题"""
    classifier = get_domain_classifier()
    
    print("=" * 80)
    print("🔀 测试跨领域问题")
    print("=" * 80)
    print()
    
    cross_domain_queries = [
        "工艺改进如何降低能耗？",  # 工艺 + 节能
        "设备故障导致的质量问题如何解决？",  # 设备 + 质量
        "市场需求变化对生产工艺的影响",  # 市场 + 工艺
    ]
    
    for query in cross_domain_queries:
        print(f"📝 查询: {query}")
        
        # 分类
        primary_domain, confidence, all_scores = classifier.classify(query)
        
        print(f"   主要领域: {primary_domain} (置信度: {confidence:.2%})")
        print(f"   涉及领域:")
        for domain, score in all_scores[:3]:
            if score > 0.1:
                domain_info = classifier.get_domain_info(domain)
                print(f"      - {domain_info['name']}: {score:.2%}")
        
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    # 运行所有测试
    test_domain_classification()
    print()
    
    test_domain_boundary_check()
    print()
    
    test_cross_domain_questions()

