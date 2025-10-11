# Prompt Management System - 完整指南

> 企业级智能体和提示词管理系统,提供版本控制、性能监控、缓存优化等功能

---

## 📑 目录

- [系统概述](#系统概述)
- [核心特性](#核心特性)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [API文档](#api文档)
- [核心组件](#核心组件)
- [最佳实践](#最佳实践)
- [测试与部署](#测试与部署)

---

## ✨ 系统概述

Prompt Management System 是一个完整的智能体和提示词管理平台,为AI应用提供:

- 🤖 智能体生命周期管理
- 📝 提示词版本控制
- 📊 性能监控和分析
- ⚡ 多级缓存优化
- 🔍 智能搜索和推荐

---

## 🌟 核心特性

### 🤖 智能体管理
- **多类型支持**: 对话、分析、翻译等多种智能体类型
- **能力配置**: 灵活的能力定义和配置管理
- **状态管理**: 智能体激活/停用状态控制

### 📝 提示词管理
- **版本控制**: 完整的版本历史和回滚功能
- **多语言支持**: 中文、英文等多语言提示词
- **变量系统**: 动态变量替换和验证
- **分类标签**: 灵活的分类和标签系统

### 🔄 版本管理
- **语义化版本**: 自动版本号生成(主版本.次版本.修订版本)
- **变更追踪**: 详细的变更记录和描述
- **版本比较**: 版本间差异对比功能
- **一键回滚**: 安全的版本回滚机制

### 📊 分析和监控
- **使用统计**: 详细的使用数据收集和分析
- **性能指标**: 响应时间、成功率等关键指标
- **趋势分析**: 长期趋势和模式识别
- **智能洞察**: AI驱动的性能优化建议

### ⚡ 性能优化
- **多级缓存**: L1内存缓存 + L2持久化缓存
- **智能预加载**: 基于使用模式的缓存预热
- **自动优化**: 缓存策略自动调整
- **性能监控**: 实时性能指标收集

### 🔍 搜索和发现
- **全文搜索**: 基于内容的智能搜索
- **多维过滤**: 按类型、语言、标签等过滤
- **相关推荐**: 基于使用模式的智能推荐

---

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   REST API      │    │   Database      │
│                 │◄──►│                 │◄──►│                 │
│ - 管理界面      │    │ - FastAPI       │    │ - PostgreSQL    │
│ - 监控面板      │    │ - 认证授权      │    │ - 数据持久化    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Core Services │
                       │                 │
                       │ - PromptService │
                       │ - CacheManager  │
                       │ - Analytics     │
                       │ - Performance   │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Cache Layer   │
                       │                 │
                       │ - Redis/Memory  │
                       │ - 多级缓存      │
                       └─────────────────┘
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
git clone <repository-url>
cd RAG_Agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

### 3. 初始化数据库

```bash
# 创建数据库
createdb prompt_management

# 运行迁移
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 验证安装

```bash
curl http://localhost:8000/api/v1/prompt-management/health
```

---

## 📖 API文档

### 基础信息

- **基础URL**: `http://localhost:8000/api/v1/prompt-management`
- **认证方式**: Bearer Token
- **内容类型**: `application/json`

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

#### 1.3 获取智能体详情

```http
GET /agents/{agent_id}
```

#### 1.4 更新智能体

```http
PUT /agents/{agent_id}
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
  "content": "你是一个专业的客服代表,请礼貌地回答用户的问题。用户信息:{user_name},问题类型:{question_type}",
  "language": "zh-CN",
  "variables": ["user_name", "question_type"],
  "tags": ["客服", "对话"],
  "category": "customer_service"
}
```

#### 2.2 激活提示词

```http
POST /prompts/{prompt_id}/activate
```

#### 2.3 获取智能体的当前提示词

```http
GET /agents/{agent_id}/prompt
```

#### 2.4 搜索提示词

```http
GET /prompts/search?query=客服&language=zh-CN&category=customer_service&page=1&size=10
```

### 3. 版本管理 (Versions)

#### 3.1 创建新版本

```http
POST /prompts/{prompt_id}/versions
```

**请求体**:
```json
{
  "content": "你是一个专业且友善的客服代表,请耐心地回答用户的问题。用户信息:{user_name},问题类型:{question_type},紧急程度:{urgency}",
  "variables": ["user_name", "question_type", "urgency"],
  "change_description": "添加紧急程度变量,优化语气表达"
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

#### 6.3 预热缓存

```http
POST /cache/preload?agent_id=1
```

### 7. 健康检查 (Health)

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

---

## 🔧 核心组件

### 数据模型

```python
# 智能体模型
class Agent:
    id: int
    name: str
    description: str
    agent_type: str
    capabilities: List[str]
    config: Dict
    is_active: bool

# 提示词模型
class SystemPrompt:
    id: int
    agent_id: int
    name: str
    content: str
    language: str
    variables: List[str]
    is_active: bool

# 版本模型
class PromptVersion:
    id: int
    prompt_id: int
    version: str
    content: str
    change_description: str
```

### 服务层

```python
# 核心服务
class PromptService:
    async def create_agent(self, data: AgentCreate) -> Agent
    async def create_prompt(self, data: SystemPromptCreate) -> SystemPrompt
    async def activate_prompt(self, prompt_id: int) -> SystemPrompt
    async def create_version(self, prompt_id: int, data: VersionCreate) -> PromptVersion

# 缓存管理
class AdvancedCacheManager:
    def get_agent(self, agent_id: int) -> Optional[Agent]
    def set_agent(self, agent_id: int, agent: Agent) -> None
    def invalidate_agent(self, agent_id: int) -> None

# 性能监控
class PerformanceMonitor:
    def record_response_time(self, endpoint: str, duration: float) -> None
    def get_performance_summary(self) -> Dict
```

---

## 💡 最佳实践

### 1. 提示词设计

- ✅ 使用清晰的变量命名
- ✅ 提供详细的上下文信息
- ✅ 定期测试和优化提示词效果

### 2. 版本管理

- ✅ 为每次重要更改创建新版本
- ✅ 提供详细的变更描述
- ✅ 在生产环境中谨慎进行版本回滚

### 3. 性能优化

- ✅ 利用缓存机制减少数据库查询
- ✅ 监控API响应时间
- ✅ 定期清理过期的性能数据

### 4. 安全考虑

- ✅ 定期轮换访问令牌
- ✅ 验证所有输入参数
- ✅ 记录敏感操作的审计日志

---

## 🧪 测试与部署

### 运行所有测试

```bash
# 使用测试脚本
python tests/test_prompt_management/run_tests.py --type all --coverage

# 或使用pytest
pytest tests/test_prompt_management/ -v --cov=src.prompt_management
```

### 测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=src.prompt_management --cov-report=html
open htmlcov/index.html
```

### 性能测试

```bash
# 运行性能测试
python tests/test_prompt_management/run_tests.py --type performance
```

### Docker部署

```bash
# 构建镜像
docker build -t prompt-management .

# 运行容器
docker-compose up -d
```

### Kubernetes部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prompt-management
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prompt-management
  template:
    metadata:
      labels:
        app: prompt-management
    spec:
      containers:
      - name: app
        image: prompt-management:latest
        ports:
        - containerPort: 8000
```

---

## 🔒 安全

### 认证和授权

- **JWT Token**: 基于JWT的无状态认证
- **角色权限**: 细粒度的权限控制
- **API限流**: 防止API滥用

### 数据安全

- **输入验证**: 严格的输入参数验证
- **SQL注入防护**: 使用ORM防止SQL注入
- **敏感数据**: 敏感信息加密存储

### Bearer Token 认证

在请求头中包含认证令牌:

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

---

## 📈 性能

### 基准测试结果

| 操作 | 平均响应时间 | QPS | 内存使用 |
|------|-------------|-----|----------|
| 创建智能体 | 50ms | 200 | 10MB |
| 获取提示词 | 5ms | 2000 | 5MB |
| 搜索提示词 | 100ms | 100 | 20MB |
| 版本创建 | 80ms | 125 | 15MB |

### 优化建议

1. **缓存策略**: 启用Redis缓存提升性能
2. **数据库优化**: 添加适当的索引
3. **连接池**: 配置数据库连接池
4. **异步处理**: 使用异步I/O提升并发

---

## 📊 API端点概览

### 智能体管理
- `POST /agents` - 创建智能体
- `GET /agents` - 获取智能体列表
- `GET /agents/{id}` - 获取智能体详情
- `PUT /agents/{id}` - 更新智能体
- `DELETE /agents/{id}` - 删除智能体

### 提示词管理
- `POST /prompts` - 创建提示词
- `POST /prompts/{id}/activate` - 激活提示词
- `GET /agents/{id}/prompt` - 获取当前提示词
- `GET /prompts/search` - 搜索提示词

### 版本管理
- `POST /prompts/{id}/versions` - 创建版本
- `GET /prompts/{id}/versions` - 获取版本列表
- `POST /prompts/{id}/versions/{version_id}/rollback` - 版本回滚

### 分析功能
- `GET /analytics/usage` - 使用分析
- `GET /analytics/performance` - 性能分析
- `GET /analytics/trends` - 趋势分析

---

## ❓ 错误处理

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

---

## 🔍 限流

API 实施了速率限制:

- **标准用户**: 每分钟 100 请求
- **高级用户**: 每分钟 1000 请求
- **企业用户**: 无限制

超出限制时返回 `429 Too Many Requests`。

---

## 📖 分页

支持分页的端点使用以下参数:

- `page`: 页码(从1开始)
- `size`: 每页大小(默认10,最大100)

分页响应格式:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

---

## 🔌 WebSocket 支持

### 实时通知

连接到 WebSocket 端点接收实时通知:

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

---

## 📋 路线图

### v1.1.0 (计划中)
- [ ] 智能体模板市场
- [ ] 提示词效果A/B测试
- [ ] 多租户支持
- [ ] 审计日志

### v1.2.0 (计划中)
- [ ] 图形化提示词编辑器
- [ ] 智能提示词优化建议
- [ ] 实时协作编辑
- [ ] 插件系统

### v2.0.0 (远期)
- [ ] 分布式部署支持
- [ ] 机器学习驱动的优化
- [ ] 多模态提示词支持
- [ ] 企业级SSO集成

---

## 🤝 贡献

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 代码风格
- 添加类型注解
- 编写单元测试
- 更新文档

### 提交规范

```bash
# 功能添加
git commit -m "feat: 添加智能体批量导入功能"

# 问题修复
git commit -m "fix: 修复缓存失效问题"

# 文档更新
git commit -m "docs: 更新API文档"
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

感谢所有贡献者和开源社区的支持！

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库
- [Redis](https://redis.io/) - 内存数据结构存储

---

## 📞 联系我们

- 📧 邮箱: support@example.com
- 💬 讨论: [GitHub Discussions](https://github.com/example/prompt-management/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/example/prompt-management/issues)
- 📖 文档: [在线文档](https://docs.example.com)

---

<div align="center">
  <strong>让AI提示词管理变得简单高效</strong>
</div>

---

**最后更新**: 2025-01-11  
**版本**: 1.0.0  
**维护者**: RAG Agent Team

