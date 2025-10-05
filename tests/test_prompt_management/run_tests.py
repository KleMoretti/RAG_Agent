#!/usr/bin/env python3
"""
Prompt Management测试运行脚本
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """运行测试"""
    base_cmd = ["python", "-m", "pytest"]
    
    if verbose:
        base_cmd.append("-v")
    
    if coverage:
        base_cmd.extend(["--cov=src.prompt_management", "--cov-report=html", "--cov-report=term"])
    
    test_dir = Path(__file__).parent
    
    if test_type == "all":
        cmd = base_cmd + [str(test_dir)]
    elif test_type == "unit":
        cmd = base_cmd + [
            str(test_dir / "test_models.py"),
            str(test_dir / "test_service.py"),
            str(test_dir / "test_cache.py"),
            str(test_dir / "test_performance.py")
        ]
    elif test_type == "integration":
        cmd = base_cmd + [str(test_dir / "test_integration.py")]
    elif test_type == "api":
        cmd = base_cmd + [str(test_dir / "test_api.py")]
    else:
        cmd = base_cmd + [str(test_dir / f"test_{test_type}.py")]
    
    print(f"运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=test_dir.parent.parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="运行Prompt Management测试")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "api", "models", "service", "cache", "performance"],
        default="all",
        help="测试类型"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    
    args = parser.parse_args()
    
    print(f"开始运行 {args.type} 测试...")
    exit_code = run_tests(args.type, args.verbose, args.coverage)
    
    if exit_code == 0:
        print("✅ 所有测试通过!")
    else:
        print("❌ 测试失败!")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()