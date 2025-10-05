# Prompt Management 快速开始指南

## 概述

Prompt Management 是一个强大的智能体和提示词管理系统，提供版本控制、性能监控、缓存优化等企业级功能。

## 系统要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+ (可选，用于缓存)
- FastAPI 0.100+

## 安装和配置

### 1. 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd RAG_Agent

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置

```bash
# 创建数据库
createdb prompt_management

# 运行迁移
alembic upgrade head
```

### 3. 环境变量配置

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost/prompt_management

# Redis配置（可选）
REDIS_URL=redis://localhost:6379/0

# API配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# 安全配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. 启动服务

```bash
# 启动API服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 5分钟快速体验

### 步骤1：创建第一个智能体

```python
import asyncio
import httpx

async def create_agent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/prompt-management/agents",
            json={
                "name": "我的第一个智能体",
                "description": "用于快速体验的智能体",
                "agent_type": "chat",
                "capabilities": ["对话", "问答"]
            },
            headers={"Authorization": "Bearer your-token"}
        )
        
        agent = response.json()
        print(f"✅ 创建智能体成功: {agent['name']} (ID: {agent['id']})")
        return agent

# 运行
agent = asyncio.run(create_agent())
```

### 步骤2：创建提示词

```python
async def create_prompt(agent_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/prompt-management/prompts",
            json={
                "agent_id": agent_id,
                "name": "友好对话提示词",
                "content": "你是一个友好的AI助手。用户姓名：{user_name}，请礼貌地回答问题。",
                "language": "zh-CN",
                "variables": ["user_name"],
                "tags": ["友好", "对话"]
            },
            headers={"Authorization": "Bearer your-token"}
        )
        
        prompt = response.json()
        print(f"✅ 创建提示词成功: {prompt['name']} (ID: {prompt['id']})")
        return prompt

# 运行
prompt = asyncio.run(create_prompt(agent['id']))
```

### 步骤3：激活提示词

```python
async def activate_prompt(prompt_id):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:8000/api/v1/prompt-management/prompts/{prompt_id}/activate",
            headers={"Authorization": "Bearer your-token"}
        )
        
        result = response.json()
        print(f"✅ 激活提示词成功: {result['is_active']}")
        return result

# 运行
asyncio.run(activate_prompt(prompt['id']))
```

### 步骤4：获取当前提示词

```python
async def get_current_prompt(agent_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/api/v1/prompt-management/agents/{agent_id}/prompt",
            headers={"Authorization": "Bearer your-token"}
        )
        
        current_prompt = response.json()
        print(f"✅ 当前提示词: {current_prompt['name']}")
        print(f"   内容: {current_prompt['content']}")
        return current_prompt

# 运行
current_prompt = asyncio.run(get_current_prompt(agent['id']))
```

## 使用Python SDK

### 安装SDK

```bash
pip install prompt-management-sdk
```

### 基础使用

```python
from prompt_management_sdk import PromptManagementClient

# 初始化客户端
client = PromptManagementClient(
    base_url="http://localhost:8000/api/v1/prompt-management",
    token="your-access-token"
)

# 创建智能体
agent = client.agents.create({
    "name": "SDK测试智能体",
    "description": "使用SDK创建的智能体",
    "agent_type": "chat"
})

# 创建提示词
prompt = client.prompts.create({
    "agent_id": agent.id,
    "name": "SDK测试提示词",
    "content": "你是一个AI助手，用户：{user_name}",
    "language": "zh-CN",
    "variables": ["user_name"]
})

# 激活提示词
client.prompts.activate(prompt.id)

# 获取当前提示词
current_prompt = client.agents.get_current_prompt(agent.id)
print(f"当前提示词: {current_prompt.name}")
```

## 常见使用模式

### 模式1：简单对话智能体

```python
# 1. 创建对话智能体
agent = client.agents.create({
    "name": "客服助手",
    "agent_type": "chat",
    "capabilities": ["对话", "问答", "帮助"]
})

# 2. 创建基础提示词
prompt = client.prompts.create({
    "agent_id": agent.id,
    "name": "客服对话模板",
    "content": """你是一个专业的客服代表。

用户信息：
- 姓名：{user_name}
- 问题：{user_question}

请礼貌地回答用户的问题。""",
    "language": "zh-CN",
    "variables": ["user_name", "user_question"]
})

# 3. 激活提示词
client.prompts.activate(prompt.id)
```

### 模式2：多版本管理

```python
# 1. 创建初始版本
initial_prompt = client.prompts.create({
    "agent_id": agent.id,
    "name": "基础版本",
    "content": "你是一个AI助手。",
    "language": "zh-CN"
})

# 2. 创建改进版本
improved_version = client.prompts.create_version(initial_prompt.id, {
    "content": "你是一个专业且友善的AI助手。",
    "change_description": "改进语气，更加友善"
})

# 3. A/B测试后决定使用哪个版本
if ab_test_results["improved"] > ab_test_results["initial"]:
    client.prompts.activate_version(improved_version.id)
else:
    client.prompts.rollback(initial_prompt.id, improved_version.id)
```

### 模式3：性能监控

```python
from prompt_management_sdk import PerformanceMonitor

# 初始化性能监控
monitor = PerformanceMonitor(client)

# 记录使用统计
monitor.record_usage(
    prompt_id=prompt.id,
    response_time=1.2,
    success=True,
    user_feedback=4.5
)

# 获取性能报告
report = monitor.get_performance_report(agent.id, days=7)
print(f"7天性能报告:")
print(f"- 总使用次数: {report.total_usage}")
print(f"- 平均响应时间: {report.avg_response_time:.2f}秒")
print(f"- 成功率: {report.success_rate:.2%}")
```

## 高级功能

### 缓存管理

```python
# 清除特定类型的缓存
client.cache.clear(cache_type="agent")

# 获取缓存统计
cache_stats = client.cache.get_stats()
print(f"缓存命中率: {cache_stats.hit_rate:.2%}")

# 预热缓存
client.cache.preload(agent_id=agent.id)
```

### 分析和报告

```python
# 生成使用报告
usage_report = client.analytics.generate_usage_report(
    agent_id=agent.id,
    days=30
)

# 获取趋势分析
trends = client.analytics.get_trends(
    agent_id=agent.id,
    metric="usage",
    days=90
)

# 效果分析
effectiveness = client.analytics.analyze_effectiveness(
    prompt_id=prompt.id,
    days=30
)
```

## 故障排除

### 常见问题

#### 1. 连接数据库失败

```bash
# 检查数据库连接
psql -h localhost -U username -d prompt_management

# 检查环境变量
echo $DATABASE_URL
```

#### 2. API认证失败

```python
# 检查token是否有效
response = client.auth.verify_token()
if not response.valid:
    # 重新获取token
    token = client.auth.login(username, password)
```

#### 3. 性能问题

```python
# 检查系统资源
system_stats = client.performance.get_system_stats()
if system_stats.memory_usage > 0.8:
    print("内存使用率过高，建议清理缓存")
    client.cache.clear()
```

### 调试模式

```python
# 启用调试日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用调试客户端
client = PromptManagementClient(
    base_url="http://localhost:8000/api/v1/prompt-management",
    token="your-token",
    debug=True  # 启用调试模式
)
```

## 生产环境部署

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/prompt_management
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=prompt_management
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 环境配置

```bash
# 生产环境变量
export DATABASE_URL="postgresql://user:pass@prod-db:5432/prompt_management"
export REDIS_URL="redis://prod-redis:6379/0"
export DEBUG=False
export SECRET_KEY="your-production-secret-key"
```

## 下一步

现在你已经成功设置了Prompt Management系统！接下来可以：

1. 📖 阅读 [API文档](./prompt_management_api.md) 了解所有可用功能
2. 💡 查看 [使用示例](./usage_examples.md) 学习高级用法
3. 🧪 运行测试确保系统正常工作：
   ```bash
   python tests/test_prompt_management/run_tests.py --type all
   ```
4. 🚀 开始构建你的第一个AI应用！

## 获取帮助

- 📚 [完整文档](./prompt_management_api.md)
- 💬 [社区讨论](https://github.com/example/prompt-management/discussions)
- 🐛 [问题反馈](https://github.com/example/prompt-management/issues)
- 📧 技术支持: support@example.com