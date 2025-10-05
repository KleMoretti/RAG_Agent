#!/bin/bash
# 启动 RAG Agent 系统的脚本

echo "🚀 正在启动 RAG Agent 系统..."
echo ""

# 1. 检查 MySQL
echo "📊 检查 MySQL 状态..."
if ! mysql -u root -p123456 -e "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ MySQL 未运行或密码不正确"
    echo "   请运行: brew services start mysql"
    exit 1
fi
echo "✅ MySQL 运行正常"
echo ""

# 2. 确保数据库存在
echo "🗄️  检查数据库..."
mysql -u root -p123456 -e "CREATE DATABASE IF NOT EXISTS rag_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
echo "✅ 数据库已就绪"
echo ""

# 3. 初始化数据库表
echo "📋 初始化数据库表..."
cd "$(dirname "$0")"
PYTHONPATH=$(pwd) python3 scripts/__init__db.py
echo ""

# 4. 创建管理员用户（如果不存在）
echo "👤 创建管理员用户..."
PYTHONPATH=$(pwd) python3 create_admin_user.py 2>/dev/null || echo "用户可能已存在"
echo ""

# 5. 启动后端
echo "🔧 启动后端服务器 (端口 8000)..."
echo "   日志文件: backend.log"
nohup python3 -m uvicorn main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   后端进程 PID: $BACKEND_PID"
sleep 3
echo ""

# 6. 检查后端是否启动成功
echo "✅ 检查后端状态..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ 后端启动成功！"
else
    echo "❌ 后端启动失败，请查看 backend.log"
    exit 1
fi
echo ""

echo "=" "==" 50
echo "🎉 系统启动完成！"
echo ""
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:8000"
echo "📄 API 文档: http://localhost:8000/docs"
echo ""
echo "👤 测试账号:"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📝 查看后端日志: tail -f backend.log"
echo "🛑 停止后端: kill $BACKEND_PID"
echo "=" "==" 50
