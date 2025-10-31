"""ML 系统综合测试脚本

此脚本整合了以下测试功能：
1. 训练数据查询工具测试 (TrainingDataQueryTool)
2. 模型训练流程测试 (FaultDetector)
3. 预测功能测试（单条和批量）
4. Agent 集成测试（可选）
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ml.training_data_tool import TrainingDataQueryTool
from src.ml.fault_detector import FaultDetector


def print_section(title: str, char: str = "="):
    """打印分隔线"""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def test_training_data_tool():
    """测试训练数据查询工具的各种功能"""
    print_section("📊 测试 1: 训练数据查询工具", "=")
    
    tool = TrainingDataQueryTool()
    
    # 测试 1.1: 整体统计
    print("【1.1】整体统计信息")
    print("-" * 80)
    result = tool.execute(query_type="statistics")
    print(result)
    
    # 测试 1.2: 特定设备统计
    print("\n【1.2】Turbine 设备统计")
    print("-" * 80)
    result = tool.execute(query_type="equipment_stats", equipment_type="Turbine")
    print(result)
    
    # 测试 1.3: 故障分析
    print("\n【1.3】故障样本分析")
    print("-" * 80)
    result = tool.execute(query_type="fault_analysis")
    print(result)
    
    # 测试 1.4: 参数范围查询
    print("\n【1.4】故障样本的温度参数")
    print("-" * 80)
    result = tool.execute(
        query_type="parameter_range",
        parameter="temperature",
        condition="faulty"
    )
    print(result)
    
    # 测试 1.5: 对比分析
    print("\n【1.5】正常 vs 故障样本对比")
    print("-" * 80)
    result = tool.execute(query_type="compare")
    print(result)
    
    print("\n✅ 训练数据查询工具测试完成！")


def test_model_training():
    """测试模型训练流程"""
    print_section("🤖 测试 2: 模型训练流程", "=")
    
    # 2.1: 检查训练数据
    data_path = project_root / "data" / "ml" / "training_data" / "equipment_anomaly_data.csv"
    
    if not data_path.exists():
        print(f"❌ 训练数据不存在: {data_path}")
        print(f"\n请先生成训练数据:")
        print(f"  python scripts/generate_test_data.py --n-samples 1000 --output {data_path}")
        return False
    
    print(f"✅ 训练数据存在: {data_path}")
    
    # 2.2: 训练小模型（快速测试）
    print("\n【2.1】开始训练小模型（快速测试）...")
    print("-" * 80)
    detector = FaultDetector()
    
    try:
        result = detector.train(
            data_path=data_path,
            test_size=0.2,
            n_estimators=50,  # 小模型，快速训练
            max_depth=5,
            random_state=42,
        )
        
        print(f"\n✅ 训练成功!")
        print(f"   准确率: {result['metrics']['accuracy']:.4f}")
        print(f"   F1分数: {result['metrics']['f1_score']:.4f}")
        print(f"   模型路径: {result['model_path']}")
        
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2.3: 测试单条预测
    print("\n【2.2】测试单条预测功能...")
    print("-" * 80)
    
    test_cases = [
        {
            "name": "正常设备",
            "data": {
                "temperature": 70.5,
                "pressure": 40.2,
                "vibration": 1.45,
                "humidity": 50.3,
                "equipment": "Turbine",
                "location": "Atlanta",
            },
            "expected_faulty": False,
        },
        {
            "name": "故障设备",
            "data": {
                "temperature": 150.0,  # 过高温度
                "pressure": 80.0,       # 过高压力
                "vibration": 5.0,       # 过高振动
                "humidity": 20.0,
                "equipment": "Compressor",
                "location": "Chicago",
            },
            "expected_faulty": True,
        },
    ]
    
    for test_case in test_cases:
        prediction = detector.predict(test_case["data"])
        print(f"\n📊 {test_case['name']}:")
        print(f"   故障概率: {prediction['fault_probability']:.2%}")
        print(f"   预测结果: {'故障' if prediction['is_faulty'] else '正常'}")
        print(f"   置信度: {prediction['confidence']:.2%}")
        
        is_correct = prediction['is_faulty'] == test_case['expected_faulty']
        print(f"   验证: {'✅ 正确' if is_correct else '❌ 错误'}")
    
    # 2.4: 测试批量预测
    print("\n【2.3】测试批量预测...")
    print("-" * 80)
    batch_data = [tc["data"] for tc in test_cases]
    batch_predictions = detector.batch_predict(batch_data)
    
    print(f"✅ 批量预测成功: {len(batch_predictions)} 条记录")
    for i, pred in enumerate(batch_predictions):
        print(f"   样本{i+1}: 故障概率={pred['fault_probability']:.2%}, "
              f"结果={'故障' if pred['is_faulty'] else '正常'}")
    
    print("\n✅ 模型训练流程测试完成！")
    return True


def test_agent_integration():
    """测试工具与 Agent 集成"""
    print_section("🤝 测试 3: Agent 集成（可选）", "=")
    
    import os
    from src.agent.base_agent import BaseAgent
    from src.llm.client import OpenAIClient
    from src.llm.model_config import OpenAIConfig
    from config.settings import get_settings
    
    cfg = get_settings()
    
    # 获取 API Key
    api_key = os.environ.get("QWEN_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = cfg.openai_api_key
    
    if not api_key:
        print("⚠️  未设置 API Key，跳过 Agent 集成测试")
        print("请设置环境变量: QWEN_API_KEY 或 OPENAI_API_KEY")
        return False
    
    # 创建 OpenAI Config
    llm_config = OpenAIConfig(
        model_name=cfg.llm_model,
        api_key=api_key,
        max_tokens=2000,
        temperature=0.7,
    )
    
    # 创建 Agent
    llm = OpenAIClient(llm_config)
    agent = BaseAgent(llm_client=llm, system_prompt="你是一个设备故障诊断专家")
    
    # 添加训练数据工具
    tool = TrainingDataQueryTool()
    agent.add_tool(tool)
    
    print(f"✅ Agent 已加载工具: {[t.name for t in agent.tools]}")
    
    # 测试查询
    test_queries = [
        {
            "description": "查询 Compressor 设备的历史数据",
            "tool_call": {
                "query_type": "equipment_stats",
                "equipment_type": "Compressor"
            }
        },
        {
            "description": "分析故障样本的振动参数范围",
            "tool_call": {
                "query_type": "parameter_range",
                "parameter": "vibration",
                "condition": "faulty"
            }
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n【Agent 测试 {i}】{query['description']}")
        print("-" * 80)
        result = tool.execute(**query['tool_call'])
        print(result)
    
    print("\n✅ Agent 集成测试完成！")
    return True


def main():
    """主测试流程"""
    print_section("🧪 ML 系统综合测试", "=")
    print("此脚本将依次测试：")
    print("1. 训练数据查询工具")
    print("2. 模型训练与预测")
    print("3. Agent 集成（可选）")
    print("=" * 80)
    
    # 测试 1: 训练数据查询工具
    try:
        test_training_data_tool()
    except Exception as e:
        print(f"\n❌ 训练数据查询工具测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试 2: 模型训练流程
    try:
        training_success = test_model_training()
        if not training_success:
            print("\n⚠️  模型训练测试跳过（训练数据不存在）")
    except Exception as e:
        print(f"\n❌ 模型训练测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试 3: Agent 集成（可选）
    try:
        test_agent_integration()
    except Exception as e:
        print(f"\n⚠️  Agent 集成测试跳过: {e}")
    
    # 总结
    print_section("✅ 所有测试完成！", "=")
    print("如果所有测试都通过，说明 ML 系统运行正常。")
    print("如果有测试失败，请检查上面的错误信息。")
    print("=" * 80)


if __name__ == "__main__":
    main()

