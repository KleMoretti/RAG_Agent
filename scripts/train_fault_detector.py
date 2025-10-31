"""Train Fault Detection Machine Learning Model.

Usage:
    python scripts/train_fault_detector.py --data data/ml/training_data/equipment_anomaly_data.csv
    python scripts/train_fault_detector.py --data data.csv --n-estimators 200 --max-depth 15
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ml.fault_detector import FaultDetector


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="训练设备故障检测模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认参数训练
  python scripts/train_fault_detector.py --data data/ml/training_data/equipment_anomaly_data.csv
  
  # 自定义模型参数
  python scripts/train_fault_detector.py \\
      --data data/ml/training_data/equipment_anomaly_data.csv \\
      --n-estimators 200 \\
      --max-depth 15 \\
      --test-size 0.25
  
  # 快速训练（小模型，用于测试）
  python scripts/train_fault_detector.py \\
      --data data/ml/training_data/equipment_anomaly_data.csv \\
      --n-estimators 50 \\
      --max-depth 5
        """,
    )
    
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="训练数据CSV文件路径（必填）",
    )
    
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="随机森林树的数量（默认: 100）",
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=10,
        help="树的最大深度（默认: 10）",
    )
    
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="测试集比例（默认: 0.2）",
    )
    
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="随机种子（默认: 42）",
    )
    
    parser.add_argument(
        "--model-dir",
        type=str,
        default=None,
        help="模型保存目录（默认: data/ml/models/）",
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 验证数据文件存在
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ 错误: 数据文件不存在: {data_path}")
        print(f"   请先生成训练数据:")
        print(f"   python scripts/generate_test_data.py --n-samples 1000 --output {data_path}")
        sys.exit(1)
    
    print("🚀 开始训练设备故障检测模型")
    print("=" * 60)
    
    # 初始化检测器
    model_dir = Path(args.model_dir) if args.model_dir else None
    detector = FaultDetector(model_dir=model_dir)
    
    # 训练模型
    try:
        result = detector.train(
            data_path=data_path,
            test_size=args.test_size,
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.random_state,
        )
        
        print("\n" + "=" * 60)
        print("✅ 训练完成!")
        print("=" * 60)
        print(f"📊 模型版本: {result['model_version']}")
        print(f"📊 训练样本: {result['training_samples']}")
        print(f"📊 测试样本: {result['test_samples']}")
        print(f"📊 准确率: {result['metrics']['accuracy']:.4f}")
        print(f"📊 F1分数: {result['metrics']['f1_score']:.4f}")
        print(f"📂 模型路径: {result['model_path']}")
        
        if result.get('equipment_types'):
            print(f"🏷️  设备类型: {', '.join(result['equipment_types'])}")
        
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
