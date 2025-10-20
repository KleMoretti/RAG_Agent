# 知识图谱功能使用指南

## 概述

知识图谱系统自动从上传的钢铁行业文档中提取实体（钢种、工艺、设备、合金元素等）和关系，构建结构化的知识网络。Agent 可以通过知识图谱提供更精准的领域知识回答。

## 数据统计

- **数据文件**: `data/knowledge_graph.json` (~6MB)
- **实体数量**: 6669+ 个
- **实体类型**: 钢种、工艺、设备、合金元素、材料性能、应用领域、标准、公司、产品等
- **关系类型**: 包含成分、用于生产、符合标准、具有性能等

## Agent 工具使用

### KnowledgeGraphQueryTool 支持的查询类型

#### 1. **statistics** - 获取知识图谱统计信息
```python
# 用户问题示例：
# - "知识图谱中有多少个实体？"
# - "统计一下知识图谱的数据"
# - "知识图谱包含哪些信息？"

# Agent 调用：
tool.run(query_type='statistics', entity_name='')

# 返回示例：
{
    "success": True,
    "statistics": {
        "total_entities": 6669,
        "total_relations": 8234,
        "entity_type_counts": {
            "steel_grade": 234,
            "process": 156,
            "equipment": 89,
            ...
        }
    }
}
```

#### 2. **search** - 搜索实体（模糊匹配）
```python
# 用户问题示例：
# - "搜索硅钢相关信息"
# - "找一下关于热轧的实体"
# - "有哪些不锈钢？"

# Agent 调用：
tool.run(query_type='search', entity_name='硅钢', limit=10)

# 返回示例：
{
    "success": True,
    "query": "硅钢",
    "total_count": 15,
    "entities": [
        {
            "name": "无取向硅钢",
            "entity_type": "steel_grade",
            "description": "钢种 无取向硅钢",
            "confidence": 0.95
        },
        ...
    ]
}
```

#### 3. **properties** - 查询实体属性
```python
# 用户问题示例：
# - "Q235 钢的属性是什么？"
# - "告诉我热轧工艺的详细信息"
# - "转炉设备有哪些属性？"

# Agent 调用：
tool.run(query_type='properties', entity_name='Q235')

# 返回示例：
{
    "success": True,
    "entity": "Q235",
    "entity_type": "steel_grade",
    "description": "钢种 Q235",
    "properties": {
        "confidence": 0.95,
        "context": "...",
        "source": "document.pdf"
    },
    "confidence": 0.95
}
```

#### 4. **relationships** - 查询实体关系
```python
# 用户问题示例：
# - "Q235 钢和哪些实体有关系？"
# - "硅钢的生产工艺是什么？"
# - "转炉设备用于哪些工艺？"

# Agent 调用：
tool.run(query_type='relationships', entity_name='Q235', max_depth=1)

# 返回示例：
{
    "success": True,
    "entity": "Q235",
    "relationship_count": 12,
    "relationships": [
        {
            "relation_type": "contains",
            "direction": "outgoing",
            "target": "碳",
            "target_type": "alloy_element",
            "confidence": 0.9
        },
        ...
    ]
}
```

#### 5. **similar** - 查询相似实体
```python
# 用户问题示例：
# - "有哪些钢种和 Q235 相似？"
# - "找一些和热轧类似的工艺"
# - "304 不锈钢的替代品有哪些？"

# Agent 调用：
tool.run(query_type='similar', entity_name='Q235', limit=10)

# 返回示例：
{
    "success": True,
    "entity": "Q235",
    "entity_type": "steel_grade",
    "similar_count": 5,
    "similar_entities": [
        {
            "entity": "Q215",
            "entity_type": "steel_grade",
            "confidence": 0.92,
            "description": "钢种 Q215"
        },
        ...
    ]
}
```

#### 6. **steel_composition** - 查询钢种成分
```python
# 用户问题示例：
# - "Q235 钢的化学成分是什么？"
# - "316L 不锈钢含有哪些合金元素？"
# - "硅钢的成分分析"

# Agent 调用：
tool.run(query_type='steel_composition', entity_name='Q235')

# 返回示例：
{
    "success": True,
    "steel_grade": "Q235",
    "composition": {
        "碳": {
            "confidence": 0.9,
            "context": "C含量≤0.22%"
        },
        "硅": {
            "confidence": 0.9,
            "context": "Si含量≤0.35%"
        },
        ...
    }
}
```

## 为什么 Agent 给出的是文字描述而非可视化图谱？

### 问题
用户问 "生成知识图谱" 或 "让agent生成知识图谱"，Agent 返回了文字描述。

### 原因
1. **Agent 的职责是回答问题**，不是渲染 UI 界面
2. **知识图谱可视化需要前端页面**（使用 D3.js、Cytoscape.js 等图形库）
3. 当前的 `KnowledgeGraphQueryTool` 返回 JSON 数据，Agent 基于这些数据生成易读的文字回答
4. 如果用户上传了文档，Agent 会结合 RAG 检索到的文档内容（关于知识图谱的定义、应用等）来生成回答

### 工作流程
```
用户提问 "生成知识图谱"
    ↓
Agent 理解意图（可能是想看知识图谱统计或结构）
    ↓
Agent 调用 KnowledgeGraphQueryTool.run('statistics', '')
    ↓
工具返回 JSON 数据（6669 个实体，8234 个关系等）
    ↓
Agent 同时使用 RAG 检索相关文档（如果有）
    ↓
Agent 生成文字描述："基于您提供的检索内容，我目前掌握的钢铁行业知识主要集中在..."
```

### 解决方案

#### ✅ 已实现（后端部分）
1. **知识图谱 API**: 
   - `GET /api/knowledge-graph/statistics` - 获取统计信息
   - `POST /api/knowledge-graph/search/entities` - 搜索实体
   - `GET /api/knowledge-graph/entities/{id}` - 获取实体详情
   - `POST /api/knowledge-graph/entities/{id}/related` - 获取相关实体

2. **Agent 工具**: 
   - `KnowledgeGraphQueryTool` 支持 6 种查询类型
   - 自动加载 `data/knowledge_graph.json` 文件
   - 延迟初始化（避免启动时加载大文件）

3. **数据文件**: 
   - `data/knowledge_graph.json` 包含 6669+ 实体
   - 实体类型包括钢种、工艺、设备、合金元素等
   - 关系类型包括成分、生产、标准、性能等

#### ⏳ 待开发（前端可视化）
如果需要交互式知识图谱可视化界面，需要：

1. **创建前端页面**: `frontend/app/dashboard/knowledge-graph/page.tsx`
2. **使用图形库**: 
   - Cytoscape.js（推荐）- 适合大规模网络图
   - D3.js Force Layout - 灵活但性能较低
   - React Flow - 轻量级流程图
3. **功能设计**:
   - 显示实体节点和关系边
   - 点击节点显示详情面板
   - 搜索框过滤实体
   - 按类型筛选（钢种、工艺、设备等）
   - 调整布局（力导向、层次、网格）
   - 导出图片/数据

## 测试知识图谱功能

### 命令行测试
```bash
# 测试统计功能
python -c "from src.agent.steel_tools import KnowledgeGraphQueryTool; tool = KnowledgeGraphQueryTool(); result = tool.run('statistics', ''); print('Total entities:', result['statistics']['total_entities'])"

# 测试搜索功能
python -c "from src.agent.steel_tools import KnowledgeGraphQueryTool; tool = KnowledgeGraphQueryTool(); result = tool.run('search', '硅钢', limit=5); print('Found:', result['total_count'], 'entities')"

# 测试实体属性查询
python -c "from src.agent.steel_tools import KnowledgeGraphQueryTool; tool = KnowledgeGraphQueryTool(); result = tool.run('properties', '硅钢'); print(result)"
```

### 通过聊天界面测试
在 Chat 界面中提问：
- ✅ "知识图谱中有多少个实体？" → Agent 调用 `statistics`
- ✅ "搜索硅钢相关的信息" → Agent 调用 `search`
- ✅ "Q235 钢的成分是什么？" → Agent 调用 `steel_composition`
- ✅ "有哪些不锈钢？" → Agent 调用 `search` 搜索不锈钢

### API 测试
```bash
# 需要先启动后端
python manage.py start backend

# 测试统计接口（需要登录 token）
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/knowledge-graph/statistics

# 测试搜索接口
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" \
  -d '{"query":"硅钢","limit":5}' \
  http://localhost:8000/api/knowledge-graph/search/entities
```

## 重建知识图谱

如果需要从头重建知识图谱（例如上传了新文档）：

```bash
# 运行知识图谱构建脚本
python scripts/init_steel_knowledge_graph.py

# 脚本会：
# 1. 读取 data/raw/ 中的所有文档
# 2. 提取实体和关系
# 3. 保存到 data/knowledge_graph.json
# 4. 输出统计信息
```

## 常见问题

### Q: 为什么 Agent 没有使用知识图谱？
A: 检查以下几点：
1. `data/knowledge_graph.json` 文件是否存在
2. 后端是否成功加载知识图谱（查看启动日志）
3. Agent 是否注册了 `KnowledgeGraphQueryTool`（在 `main.py` 中检查）

### Q: 如何查看知识图谱的原始数据？
A: 直接打开 `data/knowledge_graph.json` 文件（注意文件较大，6MB+）

### Q: 知识图谱数据从哪里来？
A: 
1. 运行 `scripts/init_steel_knowledge_graph.py` 从上传的文档中自动提取
2. 使用 NLP 技术识别实体（如钢种名称、工艺术语等）
3. 通过规则和模式匹配提取关系

### Q: 可以手动编辑知识图谱吗？
A: 可以，但不推荐。`knowledge_graph.json` 是 JSON 格式，可以手动编辑，但：
- 需要遵循数据结构规范
- 手动修改后重新运行脚本会被覆盖
- 建议通过 API 接口进行增删改操作

## 扩展功能建议

### 短期（后端）
- [ ] 知识图谱增量更新（不重建整个图谱）
- [ ] 实体合并和去重算法优化
- [ ] 关系置信度评分机制
- [ ] 知识图谱版本管理

### 中期（前端）
- [ ] 知识图谱可视化页面
- [ ] 交互式实体探索
- [ ] 图谱编辑功能（添加/删除节点和边）
- [ ] 导出为多种格式（PNG、SVG、GraphML）

### 长期（AI 增强）
- [ ] 基于大模型的实体关系抽取
- [ ] 知识图谱推理和补全
- [ ] 多模态知识图谱（支持图片、表格）
- [ ] 知识图谱问答增强

