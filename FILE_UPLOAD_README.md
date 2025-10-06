# 文件传输功能说明

## 功能概述

为 RAG Agent 系统添加了完整的文件传输功能，支持：

- 📁 **文件上传**：支持多种文本文件格式
- 🔍 **内容识别**：自动识别文件类型和内容
- ✂️ **智能分块**：将大文件分割成可处理的块
- 💬 **对话集成**：上传的文件内容可参与对话

## 支持的文件类型

- 文本文件：`.txt`, `.md`
- 代码文件：`.py`, `.js`, `.ts`
- 数据文件：`.json`
- 其他：`.pdf`, `.doc`, `.docx`（基本信息显示）

## 技术实现

### 后端 (FastAPI)

**新增接口：**
- `POST /api/upload` - 文件上传接口

**核心功能：**
```python
# 文件内容处理
def _process_text_file(content: bytes, file_name: str) -> list[dict]:
    """处理文本文件，进行分块"""
    # 按段落分割，每块最多1000字符
    # 返回分块结果

def _process_file_content(file: UploadFile, content: bytes) -> list[dict]:
    """根据文件类型处理内容"""
    # 支持文本文件内容提取
    # 非文本文件显示基本信息
```

**响应格式：**
```json
{
  "success": true,
  "message": "文件上传成功，已处理为 3 个块",
  "file_id": "hash_filename",
  "file_name": "test.txt",
  "file_size": 1024,
  "content_type": "text/plain",
  "chunks": [
    {
      "content": "文件内容...",
      "type": "text",
      "length": 500
    }
  ]
}
```

### 前端 (Next.js + TypeScript)

**新增组件：**
- `FileUpload` (`components/shared/FileUpload.tsx`) - 文件上传组件
  - 拖拽上传支持
  - 实时上传状态显示
  - 分块结果预览
  - 文件类型和大小验证
- Upload API Client (`lib/api/upload.ts`) - 文件上传API客户端

**集成功能：**
- 聊天界面集成文件上传按钮（📎 图标）
- 上传结果自动添加到对话历史
- 文件上下文自动关联到当前会话
- 响应式设计，支持移动端
- 使用 Dialog 组件弹窗展示上传界面

**状态管理：**
- `chatStore.addFileContext()` - 添加文件到会话上下文
- `chatStore.fileContext` - 存储每个会话的文件列表
- 上传成功后自动在聊天中添加文件信息消息

## 使用方法

### 1. 启动系统

```bash
# 安装后端依赖
pip install fastapi uvicorn python-multipart

# 安装前端依赖
cd frontend
npm install

# 启动系统（推荐）
python start_system.py

# 或手动启动
# 后端
uvicorn main:app --reload --port 8000

# 前端
cd frontend
npm run dev
```

### 2. 使用文件上传

1. 打开前端页面：http://localhost:3000
2. 登录后进入聊天界面
3. 在聊天输入框左下角点击 **📎** (回形针) 按钮
4. 在弹出的对话框中：
   - 点击"选择文件"按钮，或
   - 直接拖拽文件到上传区域
5. 查看文件处理结果和分块信息
6. 上传的文件信息会自动添加到对话中
7. 文件内容已被索引，可以在后续对话中引用

**快捷操作：**
- 支持的文件类型会在上传区域显示
- 文件大小限制：10MB
- 上传成功后会显示文件名、大小、类型和分块数量
- 可预览前3个分块的内容

### 3. 测试文件

系统已创建 `test_file.txt` 测试文件，包含：
- 多段文本内容
- 中文和英文混合
- 不同长度的段落

## 分块策略

### 文本文件分块规则：
- 按段落（`\n\n`）分割
- 每块最多 1000 字符
- 保持段落完整性
- 自动处理编码问题

### 分块示例：
```
原始文件：
段落1内容...
段落2内容...
段落3内容...

分块结果：
块1: 段落1内容 (500字符)
块2: 段落2内容 (800字符)  
块3: 段落3内容 (300字符)
```

## API 接口

### 文件上传接口

**请求：**
```http
POST /api/upload
Content-Type: multipart/form-data

file: [文件数据]
```

**响应：**
```json
{
  "success": true,
  "message": "文件上传成功，已处理为 3 个块",
  "file_id": "abc123_test.txt",
  "file_name": "test.txt", 
  "file_size": 1024,
  "content_type": "text/plain",
  "chunks": [
    {
      "content": "第一段内容...",
      "type": "text",
      "length": 500
    },
    {
      "content": "第二段内容...",
      "type": "text", 
      "length": 300
    }
  ]
}
```

## 错误处理

### 常见错误：
- 文件过大：限制文件大小
- 编码错误：自动忽略无法解码的字符
- 网络错误：显示友好错误信息
- 类型不支持：显示文件基本信息

### 错误响应：
```json
{
  "success": false,
  "message": "文件处理失败: 编码错误"
}
```

## 扩展功能

### 未来可扩展：
1. **向量化存储**：将分块内容向量化存储
2. **语义搜索**：基于文件内容的语义搜索
3. **更多格式**：支持更多文件格式解析
4. **批量上传**：支持多文件同时上传
5. **文件管理**：文件列表和管理功能

## 技术栈

- **后端**：FastAPI + Python
- **前端**：Next.js + TypeScript + Tailwind CSS
- **文件处理**：Python 标准库
- **UI 组件**：Radix UI + Lucide React

## 注意事项

1. **文件大小限制**：建议单个文件不超过 10MB
2. **编码支持**：主要支持 UTF-8 编码
3. **安全考虑**：文件内容在内存中处理，不持久化存储
4. **性能优化**：大文件分块处理，避免内存溢出

## 故障排除

### 常见问题：

1. **上传失败**
   - 检查文件大小
   - 确认文件格式支持
   - 查看浏览器控制台错误

2. **分块显示异常**
   - 检查文件编码
   - 确认文件内容格式

3. **服务启动失败**
   - 检查端口占用
   - 确认依赖安装完整
   - 查看错误日志

### 调试方法：

1. 查看后端日志：`uvicorn main:app --reload --log-level debug`
2. 查看前端控制台：F12 开发者工具
3. 检查网络请求：Network 标签页
4. 测试 API 接口：http://localhost:8000/docs
