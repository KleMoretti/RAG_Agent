#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG Agent 系统统一管理脚本

功能：
1. start - 启动后端/前端服务
2. check - 检查数据库状态（Agent、用户、Prompt等）
3. init - 初始化数据库和创建管理员
4. status - 查看系统状态

使用方法:
    python manage.py start backend       # 启动后端
    python manage.py start frontend      # 启动前端
    python manage.py start all           # 同时启动前后端
    python manage.py check               # 检查数据库状态
    python manage.py check --verbose     # 检查详细信息
    python manage.py init                # 初始化系统
    python manage.py status              # 查看系统状态
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    try:
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--reload", "--port", "8000", "--host", "127.0.0.1"
        ], cwd=project_root)
        print("✅ 后端服务已启动 (PID: {})".format(backend_process.pid))
        print("📄 API 文档: http://localhost:8000/docs")
        return backend_process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        return None


def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    try:
        frontend_dir = project_root / "frontend"
        if not frontend_dir.exists():
            print("❌ 前端目录不存在")
            return None

        # 检查是否已安装依赖
        if not (frontend_dir / "node_modules").exists():
            print("⚠️  前端依赖未安装，正在安装...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, shell=True, check=True)

        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir, shell=True)
        print("✅ 前端服务已启动 (PID: {})".format(frontend_process.pid))
        print("🌐 前端地址: http://localhost:3000")
        return frontend_process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        return None


def check_database(verbose: bool = False):
    """检查数据库状态"""
    print("\n📊 数据库状态检查")
    print("=" * 60)
    
    try:
        from src.api.db import db_context
        from src.api.models import Agent, User, SystemPrompt
        
        with db_context() as db:
            agent_count = db.query(Agent).count()
            user_count = db.query(User).count()
            prompt_count = db.query(SystemPrompt).count()

            print(f"🧠 Agent 数量: {agent_count}")
            if verbose and agent_count:
                for agent in db.query(Agent).order_by(Agent.id):
                    print(f"  - ID: {agent.id}, 名称: {agent.name}, 展示名: {agent.display_name}, 类型: {agent.agent_type}")

            print(f"👤 用户数量: {user_count}")
            if verbose and user_count:
                for user in db.query(User).order_by(User.id):
                    print(f"  - ID: {user.id}, 用户名: {user.username}, 角色: {user.role}")

            print(f"🗂️  Prompt 数量: {prompt_count}")
            if verbose and prompt_count:
                for prompt in db.query(SystemPrompt).order_by(SystemPrompt.id).limit(10):
                    print(f"  - ID: {prompt.id}, 名称: {prompt.name}, 状态: {prompt.status}")
                if prompt_count > 10:
                    print(f"  ... 还有 {prompt_count - 10} 个 Prompt")

            print("=" * 60)
            print("✅ 数据库连接正常")
            
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        print("\n💡 提示:")
        print("  1. 检查 MySQL 是否运行")
        print("  2. 检查 .env 配置文件")
        print("  3. 运行 'python manage.py init' 初始化数据库")
        sys.exit(1)


def init_system():
    """初始化系统"""
    print("🎯 初始化 RAG Agent 系统")
    print("=" * 60)
    
    # 1. 初始化数据库表
    print("\n📋 步骤 1: 初始化数据库表...")
    try:
        subprocess.run([sys.executable, "scripts/__init__db.py"], check=True)
        print("✅ 数据库表初始化完成")
    except Exception as e:
        print(f"❌ 数据库表初始化失败: {e}")
        return
    
    # 2. 创建管理员用户
    print("\n👤 步骤 2: 创建管理员用户...")
    try:
        subprocess.run([sys.executable, "create_admin_user.py"], check=True)
        print("✅ 管理员用户创建完成")
    except Exception as e:
        print(f"⚠️  管理员用户可能已存在: {e}")
    
    # 3. 创建 Agent
    print("\n🤖 步骤 3: 创建默认 Agent...")
    try:
        subprocess.run([sys.executable, "create_agents.py"], check=True)
        print("✅ Agent 创建完成")
    except Exception as e:
        print(f"⚠️  Agent 可能已存在: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 系统初始化完成！")
    print("\n📱 默认管理员账号:")
    print("   用户名: admin")
    print("   密码: admin123")
    print("\n💡 下一步:")
    print("   1. 启动服务: python manage.py start all")
    print("   2. 访问前端: http://localhost:3000")
    print("   3. 查看 API: http://localhost:8000/docs")


def show_status():
    """显示系统状态"""
    print("\n📊 RAG Agent 系统状态")
    print("=" * 60)
    
    # 检查后端
    print("\n🔧 后端状态:")
    try:
        import requests
        response = requests.get("http://localhost:8000/docs", timeout=2)
        if response.status_code == 200:
            print("  ✅ 后端运行中 (http://localhost:8000)")
        else:
            print("  ⚠️  后端响应异常")
    except Exception:
        print("  ❌ 后端未运行")
    
    # 检查前端
    print("\n🌐 前端状态:")
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("  ✅ 前端运行中 (http://localhost:3000)")
        else:
            print("  ⚠️  前端响应异常")
    except Exception:
        print("  ❌ 前端未运行")
    
    # 检查数据库
    print("\n🗄️  数据库状态:")
    try:
        from src.api.db import db_context
        from src.api.models import Agent, User
        
        with db_context() as db:
            agent_count = db.query(Agent).count()
            user_count = db.query(User).count()
            print(f"  ✅ 数据库连接正常")
            print(f"  📊 Agent: {agent_count} 个")
            print(f"  👤 用户: {user_count} 个")
    except Exception as e:
        print(f"  ❌ 数据库连接失败: {e}")
    
    print("\n" + "=" * 60)


def cmd_start(args):
    """启动命令"""
    if args.service == "backend":
        backend = start_backend()
        if backend:
            try:
                print("\n按 Ctrl+C 停止服务")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 正在停止服务...")
                backend.terminate()
                print("✅ 服务已停止")
    
    elif args.service == "frontend":
        frontend = start_frontend()
        if frontend:
            try:
                print("\n按 Ctrl+C 停止服务")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 正在停止服务...")
                frontend.terminate()
                print("✅ 服务已停止")
    
    elif args.service == "all":
        backend = start_backend()
        if not backend:
            return
        
        time.sleep(3)  # 等待后端启动
        
        frontend = start_frontend()
        if not frontend:
            backend.terminate()
            return
        
        print("\n" + "=" * 60)
        print("🎉 服务启动完成！")
        print("\n📱 访问地址:")
        print("   前端: http://localhost:3000")
        print("   后端: http://localhost:8000")
        print("   API 文档: http://localhost:8000/docs")
        print("\n按 Ctrl+C 停止所有服务")
        print("=" * 60)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务...")
            backend.terminate()
            frontend.terminate()
            print("✅ 所有服务已停止")
    
    else:
        print(f"❌ 未知的服务类型: {args.service}")
        print("💡 可用的服务: backend, frontend, all")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RAG Agent 系统统一管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动服务
  python manage.py start backend       # 启动后端
  python manage.py start frontend      # 启动前端
  python manage.py start all           # 同时启动前后端
  
  # 检查状态
  python manage.py check               # 检查数据库
  python manage.py check --verbose     # 详细信息
  python manage.py status              # 查看系统状态
  
  # 初始化系统
  python manage.py init                # 首次运行需要初始化
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # start 子命令
    start_parser = subparsers.add_parser('start', help='启动服务')
    start_parser.add_argument('service', choices=['backend', 'frontend', 'all'],
                             help='要启动的服务')
    
    # check 子命令
    check_parser = subparsers.add_parser('check', help='检查数据库状态')
    check_parser.add_argument('--verbose', '-v', action='store_true',
                             help='显示详细信息')
    
    # init 子命令
    init_parser = subparsers.add_parser('init', help='初始化系统')
    
    # status 子命令
    status_parser = subparsers.add_parser('status', help='查看系统状态')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行对应的命令
    if args.command == 'start':
        cmd_start(args)
    elif args.command == 'check':
        check_database(args.verbose)
    elif args.command == 'init':
        init_system()
    elif args.command == 'status':
        show_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

