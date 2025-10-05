# Prompt Management API 文档

## 概述

Prompt Management API 提供了完整的智能体和提示词管理功能，包括版本控制、性能监控、缓存管理和分析功能。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1/prompt-management`
- **认证方式**: Bearer Token
- **内容类型**: `application/json`

## API 端点

### 1. 智能体管理 (Agents)

#### 1.1 创建智能体

```http
POST /agents
```

**请求体**:
```json
{
  "name": "客服智能体",
  "description": "专业的客服对话智能体",
  "agent_type": "chat",
  "capabilities": ["对话", "问答", "情感分析"],
  "config": {
    "max_tokens": 2048,
    "temperature": 0.7
  }
}
```

**响应**:
```json
{
  "id": 1,
  "name": "客服智能体",
  "description": "专业的客服对话智能体",
  "agent_type": "chat",
  "capabilities": ["对话", "问答", "情感分析"],
  "config": {
    "max_tokens": 2048,
    "temperature": 0.7
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": 1
}
```

#### 1.2 获取智能体列表

```http
GET /agents?page=1&size=10&agent_type=chat&is_active=true
```

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "客服智能体",
      "description": "专业的客服对话智能体",
      "agent_type": "chat",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

#### 1.3 获取智能体详情

```http
GET /agents/{agent_id}
```

**响应**:
```json
{
  "id": 1,
  "name": "客服智能体",
  "description": "专业的客服对话智能体",
  "agent_type": "chat",
  "capabilities": ["对话", "问答", "情感分析"],
  "config": {
    "max_tokens": 2048,
    "temperature": 0.7
  },
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "created_by": 1
}
```

#### 1.4 更新智能体

```http
PUT /agents/{agent_id}
```

**请求体**:
```json
{
  "name": "高级客服智能体",
  "description": "升级版的客服对话智能体",
  "capabilities": ["对话", "问答", "情感分析", "多轮对话"]
}
```

#### 1.5 删除智能体

```http
DELETE /agents/{agent_id}
```

### 2. 提示词管理 (Prompts)

#### 2.1 创建提示词

```http
POST /prompts
```

**请求体**:
```json
{
  "agent_id": 1,
  "name": "客服对话提示词",
  "content": "你是一个专业的客服代表，请礼貌地回答用户的问题。用户信息：{user_name}，问题类型：{question_type}",
  "language": "zh-CN",
  "variables": ["user_name", "question_type"],
  "tags": ["客服", "对话"],
  "category": "customer_service"
}
```

**响应**:
```json
{
  "id": 1,
  "agent_id": 1,
  "name": "客服对话提示词",
  "content": "你是一个专业的客服代表，请礼貌地回答用户的问题。用户信息：{user_name}，问题类型：{question_type}",
  "language": "zh-CN",
  "variables": ["user_name", "question_type"],
  "tags": ["客服", "对话"],
  "category": "customer_service",
  "is_active": false,
  "created_at": "2024-01-01T00:00:00Z",
  "created_by": 1
}
```

#### 2.2 激活提示词

```http
POST /prompts/{prompt_id}/activate
```

**响应**:
```json
{
  "id": 1,
  "is_active": true,
  "activated_at": "2024-01-01T00:00:00Z",
  "activated_by": 1
}
```

#### 2.3 获取智能体的当前提示词

```http
GET /agents/{agent_id}/prompt
```

**响应**:
```json
{
  "id": 1,
  "agent_id": 1,
  "name": "客服对话提示词",
  "content": "你是一个专业的客服代表，请礼貌地回答用户的问题。用户信息：{user_name}，问题类型：{question_type}",
  "language": "zh-CN",
  "variables": ["user_name", "question_type"],
  "is_active": true,
  "activated_at": "2024-01-01T00:00:00Z"
}
```

#### 2.4 搜索提示词

```http
GET /prompts/search?query=客服&language=zh-CN&category=customer_service&page=1&size=10
```

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "客服对话提示词",
      "content": "你是一个专业的客服代表...",
      "language": "zh-CN",
      "category": "customer_service",
      "tags": ["客服", "对话"],
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10
}
```

### 3. 版本管理 (Versions)

#### 3.1 创建新版本

```http
POST /prompts/{prompt_id}/versions
```

**请求体**:
```json
{
  "content": "你是一个专业且友善的客服代表，请耐心地回答用户的问题。用户信息：{user_name}，问题类型：{question_type}，紧急程度：{urgency}",
  "variables": ["user_name", "question_type", "urgency"],
  "change_description": "添加紧急程度变量，优化语气表达"
}
```

**响应**:
```json
{
  "id": 1,
  "prompt_id": 1,
  "version": "1.1.0",
  "content": "你是一个专业且友善的客服代表，请耐心地回答用户的问题。用户信息：{user_name}，问题类型：{question_type}，紧急程度：{urgency}",
  "variables": ["user_name", "question_type", "urgency"],
  "change_description": "添加紧急程度变量，优化语气表达",
  "created_at": "2024-01-01T00:00:00Z",
  "created_by": 1
}
```

#### 3.2 获取版本列表

```http
GET /prompts/{prompt_id}/versions?page=1&size=10
```

#### 3.3 版本回滚

```http
POST /prompts/{prompt_id}/versions/{version_id}/rollback
```

#### 3.4 版本比较

```http
GET /prompts/{prompt_id}/versions/compare?version1={version_id1}&version2={version_id2}
```

### 4. 使用统计 (Usage)

#### 4.1 记录使用统计

```http
POST /usage
```

**请求体**:
```json
{
  "prompt_id": 1,
  "response_time": 1.5,
  "success": true,
  "user_feedback": 4.5,
  "error_message": null
}
```

#### 4.2 获取使用分析

```http
GET /analytics/usage?agent_id=1&days=30
```

**响应**:
```json
{
  "agent_id": 1,
  "period_days": 30,
  "total_usage": 1250,
  "success_rate": 0.95,
  "avg_response_time": 1.2,
  "avg_user_feedback": 4.3,
  "daily_usage": [
    {
      "date": "2024-01-01",
      "count": 45,
      "success_rate": 0.96
    }
  ]
}
```

### 5. 分析功能 (Analytics)

#### 5.1 生成使用报告

```http
GET /analytics/reports/{agent_id}?days=30
```

#### 5.2 获取性能指标

```http
GET /analytics/performance/{agent_id}?days=7
```

#### 5.3 效果分析

```http
GET /analytics/effectiveness/{prompt_id}?days=30
```

#### 5.4 趋势分析

```http
GET /analytics/trends?agent_id=1&metric=usage&days=90
```

### 6. 缓存管理 (Cache)

#### 6.1 清除缓存

```http
DELETE /cache?type=agent
```

**参数**:
- `type`: 缓存类型 (`agent`, `prompt`, `analytics`, `all`)

#### 6.2 获取缓存统计

```http
GET /cache/stats
```

**响应**:
```json
{
  "total_size": 1024,
  "hit_rate": 0.85,
  "miss_rate": 0.15,
  "eviction_count": 5,
  "cache_types": {
    "agent": {
      "size": 512,
      "count": 10
    },
    "prompt": {
      "size": 256,
      "count": 5
    }
  }
}
```

#### 6.3 预热缓存

```http
POST /cache/preload?agent_id=1
```

### 7. 性能监控 (Performance)

#### 7.1 获取性能摘要

```http
GET /performance/summary
```

#### 7.2 获取响应时间统计

```http
GET /performance/response-times/{endpoint}
```

#### 7.3 获取系统资源使用

```http
GET /performance/system?minutes=60
```

### 8. 健康检查 (Health)

#### 8.1 系统健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "database": "connected",
  "cache": "operational",
  "performance": "optimal"
}
```

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "field": "name",
      "issue": "名称不能为空"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/v1/prompt-management/agents"
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `UNAUTHORIZED` | 401 | 未授权访问 |
| `FORBIDDEN` | 403 | 权限不足 |
| `CONFLICT` | 409 | 资源冲突 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

## 认证

### Bearer Token 认证

在请求头中包含认证令牌：

```http
Authorization: Bearer your_access_token_here
```

### 获取访问令牌

```http
POST /auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

## 限流

API 实施了速率限制：

- **标准用户**: 每分钟 100 请求
- **高级用户**: 每分钟 1000 请求
- **企业用户**: 无限制

超出限制时返回 `429 Too Many Requests`。

## 分页

支持分页的端点使用以下参数：

- `page`: 页码（从1开始）
- `size`: 每页大小（默认10，最大100）

分页响应格式：

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

## WebSocket 支持

### 实时通知

连接到 WebSocket 端点接收实时通知：

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/prompt-management');

ws.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log('收到通知:', notification);
};
```

### 通知类型

- `agent_created`: 智能体创建
- `prompt_activated`: 提示词激活
- `version_created`: 版本创建
- `usage_recorded`: 使用记录
- `performance_alert`: 性能警告

## SDK 示例

### Python SDK

```python
from prompt_management_client import PromptManagementClient

client = PromptManagementClient(
    base_url="http://localhost:8000/api/v1/prompt-management",
    token="your_access_token"
)

# 创建智能体
agent = client.agents.create({
    "name": "客服智能体",
    "description": "专业的客服对话智能体",
    "agent_type": "chat"
})

# 创建提示词
prompt = client.prompts.create({
    "agent_id": agent.id,
    "name": "客服对话提示词",
    "content": "你是一个专业的客服代表...",
    "language": "zh-CN"
})

# 激活提示词
client.prompts.activate(prompt.id)
```

### JavaScript SDK

```javascript
import { PromptManagementClient } from 'prompt-management-client';

const client = new PromptManagementClient({
  baseURL: 'http://localhost:8000/api/v1/prompt-management',
  token: 'your_access_token'
});

// 创建智能体
const agent = await client.agents.create({
  name: '客服智能体',
  description: '专业的客服对话智能体',
  agentType: 'chat'
});

// 获取智能体列表
const agents = await client.agents.list({
  page: 1,
  size: 10,
  agentType: 'chat'
});
```

## 最佳实践

### 1. 提示词设计

- 使用清晰的变量命名
- 提供详细的上下文信息
- 定期测试和优化提示词效果

### 2. 版本管理

- 为每次重要更改创建新版本
- 提供详细的变更描述
- 在生产环境中谨慎进行版本回滚

### 3. 性能优化

- 利用缓存机制减少数据库查询
- 监控API响应时间
- 定期清理过期的性能数据

### 4. 安全考虑

- 定期轮换访问令牌
- 验证所有输入参数
- 记录敏感操作的审计日志

## 支持

如有问题或建议，请联系：

- **技术支持**: support@example.com
- **文档反馈**: docs@example.com
- **GitHub**: https://github.com/example/prompt-management