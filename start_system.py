# python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动脚本：同时启动后端和前端服务，并打印关键路径与 API 前缀
"""

import subprocess
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        # 启动 FastAPI 服务
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"
        ], cwd=Path(__file__).parent)
        return backend_process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None


def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    try:
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print("❌ 前端目录不存在")
            return None

        # 启动 Next.js 服务
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir, shell=True)
        return frontend_process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None


def print_endpoints(frontend_port: int = 3000, backend_port: int = 8000):
    """打印关键路径与 API 前缀"""
    print()
    print("🔗 路径与 API 一览")
    print("=" * 50)

    fe = f"http://localhost:{frontend_port}"
    be = f"http://localhost:{backend_port}"

    # 前端路由
    print("🌐 前端（Next.js）")
    print(f"  • 站点首页: {fe}")
    print(f"  • 管理页面: {fe}/admin")
    print(f"  • 登录页面: {fe}/login")
    print(f"  • 登录直达管理页: {fe}/login?next=/admin")
    print(f"  • 聊天页面: {fe}/chat")
    print()

    # 后端 API
    print("🧩 后端（FastAPI）")
    print(f"  • 服务根地址: {be}")
    print(f"  • API 文档: {be}/docs")
    print(f"  • 管理 API 前缀: {be}/api/admin")
    print(f"  • 认证 API 前缀: {be}/api/auth")
    print()

    # 常见误用提示
    print("⚠️ 注意事项")
    print(f"  • 不要访问: {fe}/api/admin （这是前端路由，非后端 API）")
    print(f"  • 管理 API 请走: {be}/api/admin/*")
    print("=" * 50)
    print()


def main():
    """主函数"""
    print("🎯 RAG Agent 文件传输功能测试")
    print("=" * 50)

    # 检查依赖
    print("📋 检查依赖...")

    # 检查 Python 依赖
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        print("✅ FastAPI 依赖已安装")
    except ImportError:
        print("❌ 请安装 FastAPI: pip install fastapi uvicorn")
        return

    # 检查前端依赖
    frontend_dir = Path(__file__).parent / "frontend"
    if not (frontend_dir / "node_modules").exists():
        print("❌ 请先安装前端依赖: cd frontend && npm install")
        return

    print("✅ 依赖检查完成")
    print()

    # 启动服务
    backend_process = start_backend()
    if not backend_process:
        return

    time.sleep(3)  # 等待后端启动

    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return

    print()
    print("🎉 服务启动完成！")
    print("📱 前端地址: http://localhost:3000")
    print("🔧 后端地址: http://localhost:8000")
    print("📄 API 文档: http://localhost:8000/docs")
    print_endpoints(frontend_port=3000, backend_port=8000)

    print("📁 测试文件已创建: test_file.txt")
    print("💡 使用说明:")
    print("   1. 打开前端页面")
    print("   2. 点击 '📁 文件' 按钮")
    print("   3. 上传 test_file.txt 文件")
    print("   4. 查看文件分块结果")
    print()
    print("按 Ctrl+C 停止服务")

    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 服务已停止")


if __name__ == "__main__":
    main()