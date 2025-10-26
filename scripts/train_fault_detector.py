"""训练设备故障检测模型."""

import argparse
from pathlib import Path
from src.ml.fault_detector import FaultDetector


def main():
    parser = argparse.ArgumentParser(description="训练设备故障检测模型")
    parser.add_argument("--data", type=str, required=True, help="训练数据CSV文件路径")
    parser.add_argument("--n-estimators", type=int, default=100, help="随机森林树的数量")
    parser.add_argument("--max-depth", type=int, default=10, help="随机森林最大深度")
    parser.add_argument("--test-size", type=float, default=0.2, help="测试集比例")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"❌ 错误: 数据文件不存在: {data_path}")
        return

    print("=" * 60)
    print("🚀 开始训练设备故障检测模型")
    print("=" * 60)

    detector = FaultDetector()

    result = detector.train(
        data_path=data_path,
        test_size=args.test_size,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
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


if __name__ == "__main__":
    main()
