# 钢铁领域知识图谱系统

## 概述

本系统实现了专门针对钢铁行业的知识图谱，能够从文档中自动抽取钢铁相关的实体和关系，并提供丰富的查询接口。系统包含后端API和前端界面，支持实体搜索、关系查询、钢种分析等功能。

## 系统架构

```
钢铁领域知识图谱系统
├── 后端 (Python/FastAPI)
│   ├── 数据模型 (models.py)
│   ├── 实体抽取器 (steel_extractor.py)
│   ├── 知识图谱构建器 (builder.py)
│   ├── 查询引擎 (query.py)
│   ├── API接口 (api.py)
│   └── 管理器 (manager.py)
├── 前端 (React/TypeScript)
│   ├── 类型定义 (types/knowledge-graph.ts)
│   ├── API客户端 (lib/knowledge-graph-api.ts)
│   └── 组件
│       ├── 实体搜索 (steel-search.tsx)
│       ├── 实体详情 (steel-entity-detail.tsx)
│       ├── 统计面板 (steel-stats-panel.tsx)
│       └── 主界面 (steel-knowledge-graph.tsx)
└── 工具脚本
    ├── 初始化脚本 (init_steel_knowledge_graph.py)
    └── 演示脚本 (steel_knowledge_graph_demo.py)
```

## 核心功能

### 1. 实体识别
- **钢种**: Q235, Q345, 304, 316L, SUS304等
- **钢材类型**: 碳素钢, 合金钢, 不锈钢, 工具钢等
- **合金元素**: 碳, 硅, 锰, 铬, 镍, 钼等
- **材料性能**: 抗拉强度, 屈服强度, 延伸率, 硬度等
- **工艺**: 炼钢, 连铸, 热轧, 冷轧, 退火等
- **设备**: 转炉, 电炉, 连铸机, 热轧机等
- **应用领域**: 建筑结构, 汽车制造, 船舶建造等
- **标准**: GB/T, ASTM, JIS, DIN等

### 2. 关系抽取
- **包含关系**: 钢种包含合金元素
- **性能关系**: 钢种具有特定性能
- **生产工艺**: 钢种通过特定工艺生产
- **使用设备**: 工艺使用特定设备
- **应用关系**: 钢种用于特定应用
- **标准关系**: 钢种符合特定标准

### 3. 查询功能
- 实体搜索和过滤
- 相关实体发现
- 实体间路径查找
- 钢种成分分析
- 钢种应用领域查询
- 钢种生产工艺查询
- 钢种相关标准查询

## API接口

### 基础查询
- `POST /api/knowledge-graph/search/entities` - 搜索实体
- `GET /api/knowledge-graph/entities/{id}` - 获取实体详情
- `GET /api/knowledge-graph/entities/name/{name}` - 根据名称获取实体
- `GET /api/knowledge-graph/entities/type/{type}` - 根据类型获取实体

### 关系查询
- `POST /api/knowledge-graph/entities/{id}/related` - 获取相关实体
- `POST /api/knowledge-graph/path` - 查找实体间路径

### 钢种专用查询
- `POST /api/knowledge-graph/steel-grades/by-properties` - 根据性能查找钢种
- `POST /api/knowledge-graph/steel-grades/composition` - 获取钢种成分
- `POST /api/knowledge-graph/steel-grades/applications` - 获取钢种应用
- `POST /api/knowledge-graph/steel-grades/processes` - 获取钢种工艺
- `POST /api/knowledge-graph/steel-grades/standards` - 获取钢种标准

### 统计信息
- `GET /api/knowledge-graph/statistics` - 获取统计信息
- `GET /api/knowledge-graph/entity-types` - 获取实体类型
- `GET /api/knowledge-graph/relation-types` - 获取关系类型

## 使用方法

### 1. 初始化知识图谱
```bash
# 从已处理的文档构建知识图谱
python scripts/init_steel_knowledge_graph.py
```

### 2. 运行演示
```bash
# 运行知识图谱演示
python examples/steel_knowledge_graph_demo.py
```

### 3. 启动API服务
```bash
# 启动FastAPI服务
uvicorn main:app --reload
```

### 4. 前端使用
```typescript
import { knowledgeGraphAPI } from '@/lib/knowledge-graph-api';

// 搜索实体
const results = await knowledgeGraphAPI.searchEntities({
  query: 'Q235',
  entity_types: ['steel_grade'],
  min_confidence: 0.5
});

// 获取钢种成分
const composition = await knowledgeGraphAPI.getSteelComposition({
  steel_grade: 'Q235'
});
```

## 数据存储

知识图谱数据存储在 `data/knowledge_graph.json` 文件中，包含：
- 实体信息（ID、名称、类型、属性、置信度等）
- 关系信息（源实体、目标实体、关系类型、置信度等）
- 索引信息（实体类型索引、关系类型索引）

## 配置说明

### 实体抽取配置
- 支持正则表达式模式匹配
- 内置钢铁领域术语词典
- 可配置置信度阈值
- 支持停用词过滤

### 关系抽取配置
- 基于模式匹配的关系识别
- 支持上下文分析
- 可配置关系类型
- 支持置信度计算

## 扩展性

### 添加新实体类型
1. 在 `SteelEntityType` 枚举中添加新类型
2. 在 `SteelEntityExtractor` 中添加识别模式
3. 更新术语词典

### 添加新关系类型
1. 在 `SteelRelationType` 枚举中添加新类型
2. 在 `SteelRelationExtractor` 中添加抽取模式
3. 更新查询接口

### 添加新查询功能
1. 在 `SteelKnowledgeGraphQuery` 中添加查询方法
2. 在 `SteelKnowledgeGraphAPI` 中添加API接口
3. 更新前端组件

## 性能优化

- 使用FAISS进行向量相似度搜索
- 实现实体和关系的索引
- 支持批量操作
- 缓存频繁查询结果

## 注意事项

1. 所有API接口都需要用户认证
2. 知识图谱构建需要已处理的文档
3. 实体和关系的置信度基于抽取算法的准确性
4. 建议定期重建知识图谱以保持数据新鲜度
5. 前端组件需要相应的UI库支持

## 未来改进

1. 集成机器学习模型提高抽取准确性
2. 支持多语言实体识别
3. 添加知识图谱可视化功能
4. 实现增量更新机制
5. 添加数据质量评估功能
