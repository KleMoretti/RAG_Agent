#!/bin/bash

# 聊天记录用户隔离测试指南
# 用于验证不同用户登录时聊天记录的隔离性

echo "======================================================================"
echo "聊天记录用户隔离测试指南"
echo "======================================================================"
echo ""

echo "📋 测试目标："
echo "   验证不同用户的聊天记录完全隔离，退出登录后切换用户时看不到其他用户的聊天记录"
echo ""

echo "======================================================================"
echo "前提条件检查"
echo "======================================================================"
echo ""

# 检查系统是否运行
echo "1. 检查系统运行状态..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ 后端运行正常 (http://localhost:8000)"
else
    echo "   ❌ 后端未运行，请先启动: python manage.py start backend"
    exit 1
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ 前端运行正常 (http://localhost:3000)"
else
    echo "   ❌ 前端未运行，请先启动: python manage.py start frontend"
    exit 1
fi

echo ""
echo "2. 检查测试用户是否存在..."
python3 -c "
from src.api.db import get_db
from src.api.models import User

db = next(get_db())
users = db.query(User).filter(User.username.in_(['admin', 'manager', 'technician'])).all()

if len(users) == 3:
    print('   ✅ 测试用户已创建 (admin, manager, technician)')
    exit(0)
else:
    print('   ❌ 测试用户不完整，请运行: python scripts/init_test_users.py')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "   ❌ 测试用户不完整，请运行: python scripts/init_test_users.py"
    exit 1
fi

echo ""
echo "======================================================================"
echo "测试步骤（手动操作）"
echo "======================================================================"
echo ""

echo "第一步：以 admin 用户身份测试"
echo "--------------------------------------------------------------------"
echo "1. 打开浏览器访问: http://localhost:3000/login"
echo "2. 使用以下凭据登录："
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "3. 登录后执行以下操作："
echo "   ✅ 创建几条聊天记录（发送 2-3 条消息）"
echo "   ✅ 观察消息内容和 Agent 选择"
echo "   ✅ 注意侧边栏显示的会话标题"
echo ""
echo "4. 记录你创建的聊天内容（用于后续验证）："
echo "   例如: '你好，我是管理员用户'"
echo ""
read -p "✅ 完成上述操作后按 Enter 继续..."
echo ""

echo "第二步：退出登录"
echo "--------------------------------------------------------------------"
echo "1. 点击侧边栏底部用户菜单"
echo "2. 选择'退出登录'"
echo "3. 确认已返回登录页面"
echo ""
read -p "✅ 完成退出登录后按 Enter 继续..."
echo ""

echo "第三步：以 manager 用户身份测试"
echo "--------------------------------------------------------------------"
echo "1. 使用以下凭据登录："
echo "   用户名: manager"
echo "   密码: manager123"
echo ""
echo "2. 登录后检查以下内容："
echo "   ❌ 应该看不到 admin 用户的聊天记录"
echo "   ✅ 侧边栏应该显示'新对话'会话"
echo "   ✅ 聊天记录应该为空（没有历史消息）"
echo "   ✅ 用户角色显示为'技术经理'"
echo ""
echo "3. 创建新的聊天记录："
echo "   ✅ 发送几条消息（例如: '你好，我是技术经理'）"
echo "   ✅ 切换到不同的 Agent（例如: 市场分析师）"
echo ""
read -p "✅ 完成上述操作后按 Enter 继续..."
echo ""

echo "第四步：验证数据隔离"
echo "--------------------------------------------------------------------"
echo "1. 再次退出登录"
echo ""
echo "2. 重新以 admin 身份登录："
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "3. 验证聊天记录恢复："
echo "   ✅ 应该能看到之前创建的 admin 聊天记录"
echo "   ✅ 消息内容应该完整保留"
echo "   ❌ 看不到 manager 用户的聊天记录"
echo ""
read -p "✅ 完成验证后按 Enter 继续..."
echo ""

echo "第五步：以 technician 用户身份测试"
echo "--------------------------------------------------------------------"
echo "1. 退出登录，使用以下凭据登录："
echo "   用户名: technician"
echo "   密码: tech123"
echo ""
echo "2. 验证隔离性："
echo "   ❌ 应该看不到 admin 或 manager 的聊天记录"
echo "   ✅ 侧边栏显示'新对话'会话"
echo "   ✅ 用户角色显示为'技术员'"
echo "   ✅ Agent 列表仅显示 3 个（设备诊断、工艺专家、通用助手）"
echo ""
read -p "✅ 完成验证后按 Enter 继续..."
echo ""

echo "======================================================================"
echo "技术验证（浏览器开发者工具）"
echo "======================================================================"
echo ""

echo "1. 打开浏览器开发者工具（F12）"
echo "2. 切换到 'Application' 或 'Storage' 标签"
echo "3. 查看 'Local Storage' → http://localhost:3000"
echo ""
echo "预期结果："
echo "   ✅ 应该看到 'user-id' 键，值为当前用户的 ID"
echo "   ✅ 应该看到 'chat-store-user-{ID}' 键，存储当前用户的聊天记录"
echo "   ✅ 不同用户登录时，'user-id' 值会变化"
echo "   ✅ 不同用户的聊天记录使用不同的存储键"
echo ""

echo "示例："
echo "   admin 用户登录时:"
echo "     - user-id: 1"
echo "     - chat-store-user-1: {...聊天记录...}"
echo ""
echo "   manager 用户登录时:"
echo "     - user-id: 2"
echo "     - chat-store-user-2: {...聊天记录...}"
echo ""
read -p "✅ 完成技术验证后按 Enter 继续..."
echo ""

echo "======================================================================"
echo "常见问题排查"
echo "======================================================================"
echo ""

echo "问题 1：退出登录后仍能看到旧用户的聊天记录"
echo "原因："
echo "   - localStorage 未正确清除"
echo "   - user-id 未更新"
echo ""
echo "解决方案："
echo "   1. 打开开发者工具 → Console"
echo "   2. 执行: localStorage.clear()"
echo "   3. 刷新页面重新登录"
echo ""

echo "问题 2：登录后聊天记录为空（预期应恢复）"
echo "原因："
echo "   - 存储键名不匹配"
echo "   - 数据被意外清除"
echo ""
echo "解决方案："
echo "   1. 检查 localStorage 中是否存在 chat-store-user-{ID} 键"
echo "   2. 如果不存在，说明数据已丢失，需要重新创建"
echo ""

echo "问题 3：切换用户后 Agent 列表不正确"
echo "原因："
echo "   - 角色权限未正确应用"
echo "   - 前端缓存问题"
echo ""
echo "解决方案："
echo "   1. 强制刷新页面（Ctrl+Shift+R 或 Cmd+Shift+R）"
echo "   2. 清除浏览器缓存重新登录"
echo ""

echo "======================================================================"
echo "测试完成"
echo "======================================================================"
echo ""

echo "✅ 如果所有验证通过，说明聊天记录隔离功能正常"
echo ""
echo "测试报告："
echo "   - admin 用户的聊天记录独立存储"
echo "   - manager 用户的聊天记录独立存储"
echo "   - technician 用户的聊天记录独立存储"
echo "   - 退出登录时自动清除聊天数据"
echo "   - 重新登录时自动恢复用户的聊天记录"
echo ""

echo "技术实现细节："
echo "   - 存储方式: localStorage 动态键名"
echo "   - 键名格式: chat-store-user-{userId}"
echo "   - 登录时: 设置 user-id → 加载对应聊天记录"
echo "   - 退出时: 清除 user-id → 清除聊天数据"
echo ""

echo "======================================================================"
echo "后续改进建议"
echo "======================================================================"
echo ""

echo "当前实现（前端隔离）："
echo "   ✅ 已实现：用户聊天记录按 ID 隔离存储"
echo "   ⚠️  限制：数据仅在本地浏览器，不支持跨设备同步"
echo ""

echo "未来改进方向（后端存储）："
echo "   1. 创建 chat_session 和 chat_message 数据库表"
echo "   2. 每条消息关联到 user_id"
echo "   3. 前端从后端 API 加载聊天记录"
echo "   4. 支持跨设备同步、云端备份、聊天记录导出"
echo ""

echo "参考文档："
echo "   - AGENTS.md → 用户聊天记录隔离部分"
echo "   - frontend/store/chatStore.ts → 动态存储实现"
echo "   - frontend/store/authStore.ts → 登录/退出逻辑"
echo ""

echo "======================================================================"
echo "测试脚本结束"
echo "======================================================================"
