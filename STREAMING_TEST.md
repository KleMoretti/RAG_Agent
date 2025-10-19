# 流式聊天功能测试指南

## ✅ 已完成的工作

### 后端
- ✅ 添加了 `/api/chat/stream` SSE 流式端点（main.py:686-836）
- ✅ 实现了 RAG 检索 + 流式响应
- ✅ 支持来源（sources）、推理步骤（reasoning）、内容（content）分段发送
- ✅ 支持超时降级（RAG_TIMEOUT_SECONDS）

### 前端
- ✅ 创建了 `ChatMessage` 组件（展示消息、来源、推理步骤）
- ✅ 创建了 `StreamingMessage` 组件（实时显示生成中的内容）
- ✅ 创建了 `FileUploadProgress` 组件（上传进度）
- ✅ 创建了 `useStreamingChat` Hook（处理 SSE 流）
- ✅ 创建了 `Progress` UI 组件
- ✅ 更新了 `dashboard/page.tsx` 以使用流式聊天

## 🧪 测试步骤

### 1. 启动后端

```bash
cd /Users/rinki/Documents/RAG_Agent

# 方式 A：使用 manage.py
python manage.py start backend

# 方式 B：直接使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端启动成功：**
```bash
# 检查健康端点
curl http://localhost:8000/health

# 检查路由（应该看到 /api/chat/stream）
curl http://localhost:8000/docs
```

### 2. 启动前端

```bash
cd /Users/rinki/Documents/RAG_Agent/frontend

# 安装依赖（如果还没安装）
npm install

# 启动开发服务器
npm run dev
```

前端应该运行在 http://localhost:3000

### 3. 测试流式聊天

1. **打开浏览器** → http://localhost:3000
2. **登录系统**（使用已有账户或注册）
3. **进入 Dashboard**
4. **发送测试消息**，例如：
   - "你好，请介绍一下你自己"
   - "钢铁生产的主要流程是什么？"
   - "什么是 RAG？"

### 4. 预期行为

#### ✅ 正常流式响应流程
1. **发送消息后**：
   - 消息立即显示在聊天区域
   - 显示"AI 正在生成回答..."加载指示器

2. **如果有 RAG 检索结果**：
   - 显示可折叠的"来源"部分
   - 点击展开可以看到文件名、内容预览、相关度分数

3. **推理步骤**：
   - 显示可折叠的"推理步骤"
   - 展开可以看到 AI 的思考过程

4. **流式内容**：
   - 文字逐字或逐句出现（打字机效果）
   - 有闪烁光标 `▊` 表示正在生成

5. **完成后**：
   - 光标消失
   - 消息保存到历史记录

#### ⚠️ 降级模式（超时）
如果 RAG 检索超过 25 秒（默认 `RAG_TIMEOUT_SECONDS=25`）：
- 自动跳过 RAG，直接使用 LLM 回答
- **不会**显示降级提示（后端有标志，但前端暂未使用）

#### ❌ 错误处理
- 网络错误：显示错误提示
- 取消生成：点击"取消"按钮停止流式响应

### 5. 调试工具

#### 后端日志
启动后端时，控制台会输出：
```
✅ RAG completed in 2.31s          # 正常完成
⚠️ RAG timeout after 25s           # 超时降级
⚠️ Retrieval error: ...            # 检索错误
❌ Stream error: ...                # 流式错误
```

#### 前端开发者工具
打开浏览器控制台（F12）：
- **Network** 标签 → 查看 `/api/chat/stream` 请求
  - 应该看到 `EventStream` 类型
  - Status 应该是 `200 OK`（如果是 404，说明后端路由未加载）
- **Console** 标签 → 查看 JavaScript 错误

#### 测试 SSE 端点（curl）
```bash
# 测试流式端点是否存在
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "test-123"}' \
  --no-buffer

# 预期输出（流式）：
# data: {"type": "sources", "sources": [...]}
# 
# data: {"type": "reasoning", "steps": [...]}
# 
# data: {"type": "content", "delta": "你"}
# 
# data: {"type": "content", "delta": "好"}
# ...
# data: {"type": "done", "fallback_mode": false}
# 
# data: [DONE]
```

## 🐛 常见问题排查

### 问题 1: 404 Not Found on /api/chat/stream

**症状**：
```
INFO: 127.0.0.1:54575 - "POST /api/chat/stream HTTP/1.1" 404 Not Found
```

**原因**：
- 后端代码未正确加载
- Python 环境问题

**解决方案**：
```bash
# 1. 检查 main.py 是否有语法错误
python -m py_compile main.py

# 2. 重启后端（确保代码重新加载）
# 先停止旧进程（Ctrl+C）
# 再重新启动
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. 验证路由
curl http://localhost:8000/docs  # 打开 Swagger UI，搜索 /api/chat/stream
```

### 问题 2: 前端显示 "Cannot find module" 错误

**症状**：
```
Cannot find module '@/components/chat/ChatMessage'
```

**原因**：
- TypeScript 语言服务器缓存问题

**解决方案**：
```bash
# 方式 A：重启编辑器（VS Code / Cursor / Zed）

# 方式 B：清除 Next.js 缓存
cd frontend
rm -rf .next
npm run dev

# 方式 C：重新安装依赖
rm -rf node_modules package-lock.json
npm install
```

### 问题 3: 流式响应卡住不动

**症状**：
- 发送消息后，一直显示"正在生成..."
- 没有任何内容出现

**可能原因 & 解决方案**：

#### 原因 A：后端 Agent 未初始化
```bash
# 检查后端日志，看是否有错误
# 确保 .env 中有 LLM API Key
cat .env | grep DASHSCOPE_API_KEY
cat src/llm/.env | grep DASHSCOPE_API_KEY
```

#### 原因 B：CORS 问题
```python
# 检查 main.py 中的 CORS 配置（main.py:277-285）
cors_origins = [
    "http://localhost:3000",  # 确保包含前端地址
    # ...
]
```

#### 原因 C：SSE 被代理缓冲
如果使用 Nginx 反向代理：
```nginx
location /api/chat/stream {
    proxy_pass http://localhost:8000;
    proxy_buffering off;  # 关键！
    proxy_cache off;
    proxy_set_header X-Accel-Buffering no;
}
```

### 问题 4: Google Fonts 加载失败（构建时）

**症状**：
```
Failed to fetch `IBM Plex Sans` from Google Fonts.
```

**解决方案**：
```bash
# 方式 A：配置网络代理
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# 方式 B：临时注释字体（测试用）
# 编辑 frontend/app/layout.tsx，注释掉字体导入

# 方式 C：使用开发模式（不构建）
npm run dev  # 而不是 npm run build
```

## 📊 性能参数调整

### 调整 RAG 超时时间

编辑 `.env` 文件：
```bash
# 默认 25 秒
RAG_TIMEOUT_SECONDS=25

# 如果网络较慢，可以增加
RAG_TIMEOUT_SECONDS=40
```

### 调整流式响应速度

编辑 `main.py:815`：
```python
# 当前每次发送 20 个字符
chunk_size = 20  # 增大 → 更快但不流畅；减小 → 更流畅但更慢

# 当前每 50ms 发送一次
await asyncio.sleep(0.05)  # 减小 → 更快；增大 → 更慢（打字机效果更明显）
```

### 调整检索数量

编辑 `main.py:717`：
```python
hits = store.search(vec, top_k=5, include_metadata=True)
#                           ↑ 修改这里（默认 5）
# 增大 → 更多上下文，但响应变慢
# 减小 → 更少上下文，但响应更快
```

## 🎯 下一步建议

### 功能增强
1. ✅ **已完成**：基础流式聊天
2. 🔄 **建议实现**：
   - [ ] 消息点赞/点踩反馈
   - [ ] 复制消息内容
   - [ ] 导出对话记录
   - [ ] 代码块语法高亮（使用 Prism.js）
   - [ ] 消息搜索

### 性能优化
- [ ] 使用虚拟滚动（long conversation）
- [ ] 消息懒加载
- [ ] WebSocket 替代 SSE（双向通信）

### 测试覆盖
- [ ] 编写前端组件测试（Jest + React Testing Library）
- [ ] 编写后端 SSE 端点测试（pytest + httpx）
- [ ] E2E 测试（Playwright）

## 📝 检查清单

在提交前，确保：
- [ ] 后端启动无错误
- [ ] 前端启动无错误
- [ ] 可以发送消息并收到流式响应
- [ ] 来源和推理步骤可以正常展开/折叠
- [ ] 可以取消正在生成的响应
- [ ] 没有 TypeScript 编译错误
- [ ] 没有 ESLint 警告（运行 `npm run lint`）

## 🆘 需要帮助？

如果遇到问题：
1. 检查后端日志（控制台输出）
2. 检查前端控制台（浏览器 F12）
3. 使用 curl 测试 API 端点
4. 查看 `AGENTS.md` 的 "RAG Timeout & Fallback" 部分

---

**最后更新**: 2025-01-XX  
**状态**: ✅ 流式端点已实现，等待测试验证