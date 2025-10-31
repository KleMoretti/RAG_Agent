# 知识图谱系统

## 概述

知识图谱系统从上传的钢铁行业文档中自动提取实体和关系，构建知识网络，支持可视化探索和智能查询。

**核心特性**：
- ✅ 自动识别 15+ 种实体类型（钢种、工艺、设备、性能等）
- ✅ 支持 15+ 种关系类型（包含成分、用于生产、符合标准等）
- ✅ 交互式可视化（React Flow，支持缩放、拖拽、搜索）
- ✅ 三种智能布局算法（力导向、层次、圆形）
- ✅ 实体详情面板（属性、关系、置信度）

**数据规模**：
- 数据文件：`data/knowledge_graph.json` (~6MB)
- 实体数量：6669+ 个
- 关系数量：12000+ 条

---

## 快速开始

### 1. 构建知识图谱

**Web 界面**（推荐）：
1. 访问 `http://localhost:3000/dashboard/knowledge-graph`
2. 点击"重新构建图谱"按钮
3. 等待构建完成（10-60 秒）

**命令行**：
```bash
python scripts/init_steel_knowledge_graph.py
```

### 2. 搜索实体

在搜索框输入关键词（如 "Q235"、"热轧"、"抗拉强度"）：
- **直接匹配节点**：实心填充 + 发光效果
- **一跳关系节点**：空心节点（与匹配节点有直接关系）
- **自动居中**：搜索结果自动居中显示

### 3. 查看节点详情

**操作**：点击任意节点
**显示**：右侧滑出详情面板
**内容**：
- 基本信息（名称、类型、描述）
- 置信度（0-100%）
- 属性（来源、上下文、首次提及时间）

---

## 实体与关系类型

### 实体类型

| 类型 | 说明 | 示例 | 颜色 |
|-----|------|------|-----|
| `steel_grade` | 钢种牌号 | Q235, 304, 316L | 🔵 蓝色 |
| `steel_type` | 钢材类型 | 碳素钢、不锈钢 | 🟣 紫色 |
| `alloy_element` | 合金元素 | 碳、硅、铬 | 🟢 绿色 |
| `material_property` | 材料性能 | 抗拉强度、硬度 | 🟢 深绿 |
| `process` | 工艺流程 | 炼钢、热轧、退火 | 🟠 橙色 |
| `equipment` | 设备 | 转炉、轧机 | 🟣 紫罗兰 |
| `application` | 应用领域 | 建筑结构、汽车 | 🔵 天蓝 |
| `standard` | 标准规范 | GB/T 700, ASTM | 🟡 黄色 |

### 关系类型

| 关系 | 说明 | 示例 |
|-----|------|------|
| `contains` | 包含成分 | Q235 含有 碳 |
| `has_property` | 具有性能 | Q235 具有 抗拉强度 |
| `produced_by` | 由...生产 | 钢板 由 热轧 生产 |
| `used_in` | 用于 | Q235 用于 建筑结构 |
| `complies_with` | 符合标准 | Q235 符合 GB/T 700 |
| `improves` | 改善 | 添加铬 改善 耐腐蚀性 |

---

## 可视化与布局

### 布局算法

#### 1. 力导向布局 ⭐ 推荐
**特点**：连接度高的节点靠近中心，适合探索关系网络
**适用**：查看节点关系密度、识别核心节点

#### 2. 层次布局
**特点**：按实体类型分层排列，同类型成一行
**适用**：查看类型分布、对比不同类型数量

#### 3. 圆形布局
**特点**：节点均匀分布在圆周上
**适用**：小规模图谱（< 30 节点）、美观展示

### 节点数量

**默认**：50 个节点
**可选**：30 / 50 / 100
**说明**：节点越少加载越快，建议根据需要调整

### 节点样式

- **实心节点**：搜索匹配结果（带发光效果）
- **空心节点**：普通节点
- **边的粗细**：反映关系置信度
- **动画边**：置信度 > 80% 的关系显示流动动画

---

## API 使用

### 前端 API

```typescript
import {
    getGraphVisualizationData,
    searchGraphVisualizationData,
    getKnowledgeGraphStats,
    buildKnowledgeGraph,
} from '@/lib/api/knowledge-graph';

// 获取图谱数据
const data = await getGraphVisualizationData(['steel_grade'], 100);

// 搜索
const searchData = await searchGraphVisualizationData({
    query: 'Q235',
    limit: 50
});

// 统计信息
const stats = await getKnowledgeGraphStats();

// 构建图谱
const result = await buildKnowledgeGraph();
```

### REST API

```bash
# 获取图谱数据
GET /api/knowledge-graph/graph-data?entity_types=steel_grade&limit=100

# 搜索
POST /api/knowledge-graph/search/graph-data
{"query": "Q235", "limit": 50}

# 统计信息
GET /api/knowledge-graph/statistics

# 构建图谱（管理员）
POST /api/knowledge-graph/build
```

### Agent 工具

```python
from src.agent.steel_tools import KnowledgeGraphQueryTool

tool = KnowledgeGraphQueryTool()

# 统计信息
result = tool.run('statistics', '')

# 搜索实体
result = tool.run('search', '硅钢', limit=10)

# 查询属性
result = tool.run('properties', 'Q235')

# 查询关系
result = tool.run('relationships', 'Q235', max_depth=1)

# 查询相似实体
result = tool.run('similar', 'Q235', limit=10)

# 查询钢种成分
result = tool.run('steel_composition', 'Q235')
```

---

## 故障排查

### 问题：知识图谱为空

**解决**：
1. 确认已上传文档到知识库
2. 点击"重新构建图谱"
3. 检查后端日志：`tail -f backend.log | grep knowledge_graph`
4. 手动构建：`python scripts/init_steel_knowledge_graph.py`

### 问题：搜索无结果

**解决**：
1. 检查关键词拼写
2. 使用更通用的词汇
3. 移除实体类型过滤
4. 检查数据：`grep -i "Q235" data/knowledge_graph.json`

### 问题：图谱加载慢

**解决**：
1. 减少显示节点数量（设置为 30 或 50）
2. 使用实体类型过滤
3. 清除浏览器缓存
4. 升级浏览器到最新版本

### 问题：构建失败

**解决**：
1. 检查磁盘空间（需要 > 1GB）
2. 验证文档格式（支持 PDF、DOCX、TXT）
3. 检查数据库连接：`python manage.py check --verbose`
4. 重置数据：`rm data/knowledge_graph.json`

---

## 最佳实践

### 文档上传
✅ 上传高质量技术文档（规格书、工艺说明、标准文本）
✅ 确保文档包含明确的实体名称和关系描述
✅ 避免上传图片扫描件（识别准确率低）
✅ 定期更新文档库

### 知识图谱构建
✅ 在文档上传后立即构建
✅ 大批量上传后分批构建
✅ 定期备份 `data/knowledge_graph.json`
❌ 避免频繁构建（每次 30-60 秒）

### 搜索与探索
✅ 使用简短明确的关键词
✅ 先查看统计信息了解规模
✅ 利用实体类型过滤缩小范围
✅ 点击节点查看详情
❌ 避免一次显示过多节点

### 使用场景推荐

**场景 1：探索大型图谱**
- 布局：力导向
- 节点数：50
- 操作：搜索缩小范围

**场景 2：查看类型分布**
- 布局：层次布局
- 节点数：100
- 操作：观察各层分布

**场景 3：精确查询**
- 布局：圆形布局
- 节点数：30
- 操作：搜索特定实体

---

## 权限控制

| 操作 | ADMIN | MANAGER | TECHNICIAN |
|-----|-------|---------|------------|
| 查看知识图谱 | ✅ | ✅ | ✅ |
| 搜索实体 | ✅ | ✅ | ✅ |
| 查看详情 | ✅ | ✅ | ✅ |
| 构建图谱 | ✅ | ✅ | ❌ |

---

**版本**: v2.1 (2025-10-30)  
**维护**: RAG_Agent 开发团队

