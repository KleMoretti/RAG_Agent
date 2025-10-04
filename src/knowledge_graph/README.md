# 钢铁领域知识图谱

本模块实现了专门针对钢铁行业的知识图谱系统，包括实体识别、关系抽取、知识图谱构建和查询功能。

## 功能特性

### 1. 实体类型
- **钢种** (steel_grade): Q235, Q345, 304, 316L等
- **钢材类型** (steel_type): 碳素钢, 合金钢, 不锈钢等
- **合金元素** (alloy_element): 碳, 硅, 锰, 铬, 镍等
- **材料性能** (material_property): 抗拉强度, 屈服强度, 延伸率等
- **工艺** (process): 炼钢, 连铸, 热轧, 冷轧等
- **设备** (equipment): 转炉, 电炉, 连铸机等
- **应用领域** (application): 建筑结构, 汽车制造, 船舶建造等
- **标准** (standard): GB/T, ASTM, JIS等
- **公司** (company): 钢铁企业
- **产品** (product): 钢板, 钢管, 钢棒等

### 2. 关系类型
- **包含关系** (contains): 钢种包含合金元素
- **性能关系** (has_property): 钢种具有特定性能
- **生产工艺** (produced_by): 钢种通过特定工艺生产
- **使用设备** (uses_equipment): 工艺使用特定设备
- **应用关系** (used_in): 钢种用于特定应用
- **标准关系** (complies_with): 钢种符合特定标准
- **改善关系** (improves): 元素改善性能
- **降低关系** (reduces): 元素降低性能

## API接口

### 实体搜索
```http
POST /api/knowledge-graph/search/entities
{
    "query": "Q235",
    "entity_types": ["steel_grade"],
    "min_confidence": 0.5,
    "limit": 100
}
```

### 获取实体详情
```http
GET /api/knowledge-graph/entities/{entity_id}
```

### 根据名称获取实体
```http
GET /api/knowledge-graph/entities/name/{name}
```

### 根据类型获取实体
```http
GET /api/knowledge-graph/entities/type/{entity_type}
```

### 获取相关实体
```http
POST /api/knowledge-graph/entities/{entity_id}/related
{
    "relation_types": ["has_property", "used_in"],
    "max_depth": 2
}
```

### 查找实体间路径
```http
POST /api/knowledge-graph/path
{
    "source_id": "entity_id_1",
    "target_id": "entity_id_2",
    "max_depth": 5
}
```

### 钢种相关查询

#### 根据性能查找钢种
```http
POST /api/knowledge-graph/steel-grades/by-properties
{
    "properties": ["抗拉强度", "屈服强度"],
    "min_confidence": 0.5
}
```

#### 获取钢种成分
```http
POST /api/knowledge-graph/steel-grades/composition
{
    "steel_grade": "Q235"
}
```

#### 获取钢种应用领域
```http
POST /api/knowledge-graph/steel-grades/applications
{
    "steel_grade": "Q235"
}
```

#### 获取钢种生产工艺
```http
POST /api/knowledge-graph/steel-grades/processes
{
    "steel_grade": "Q235"
}
```

#### 获取钢种相关标准
```http
POST /api/knowledge-graph/steel-grades/standards
{
    "steel_grade": "Q235"
}
```

### 统计信息
```http
GET /api/knowledge-graph/statistics
```

### 获取实体类型列表
```http
GET /api/knowledge-graph/entity-types
```

### 获取关系类型列表
```http
GET /api/knowledge-graph/relation-types
```

## 使用方法

### 1. 初始化知识图谱
```python
from src.knowledge_graph.manager import SteelKnowledgeGraphManager

# 创建管理器
kg_manager = SteelKnowledgeGraphManager()

# 从已处理的文件中构建知识图谱
kg = kg_manager.build_from_processed_files()
```

### 2. 搜索实体
```python
# 搜索钢种
steel_grades = kg_manager.search_entities(
    query="Q235",
    entity_types=["steel_grade"],
    min_confidence=0.5
)

# 搜索性能
properties = kg_manager.search_entities(
    query="抗拉强度",
    entity_types=["material_property"]
)
```

### 3. 钢种相关查询
```python
# 根据性能查找钢种
grades = kg_manager.get_steel_grades_by_properties(
    properties=["抗拉强度", "屈服强度"]
)

# 获取钢种成分
composition = kg_manager.get_steel_composition("Q235")

# 获取钢种应用
applications = kg_manager.get_steel_applications("Q235")

# 获取钢种工艺
processes = kg_manager.get_steel_processes("Q235")

# 获取钢种标准
standards = kg_manager.get_steel_standards("Q235")
```

### 4. 获取统计信息
```python
stats = kg_manager.get_statistics()
print(f"总实体数: {stats['total_entities']}")
print(f"总关系数: {stats['total_relations']}")
```

## 初始化脚本

使用提供的初始化脚本来构建知识图谱：

```bash
python scripts/init_steel_knowledge_graph.py
```

## 数据存储

知识图谱数据存储在 `data/knowledge_graph.json` 文件中，包含：
- 实体信息
- 关系信息
- 索引信息
- 元数据

## 扩展性

系统设计为可扩展的，可以轻松添加：
- 新的实体类型
- 新的关系类型
- 新的抽取模式
- 新的查询功能

## 注意事项

1. 所有API接口都需要用户认证
2. 知识图谱构建需要已处理的文档
3. 实体和关系的置信度基于抽取算法的准确性
4. 建议定期重建知识图谱以保持数据新鲜度
