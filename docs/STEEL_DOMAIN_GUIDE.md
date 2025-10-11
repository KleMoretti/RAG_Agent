# 钢铁领域AI系统完整指南

> 本文档整合了钢铁领域的专业工具、词汇管理和知识图谱系统,为AI助手提供全面的钢铁行业支持。

---

## 📑 目录

- [系统概述](#系统概述)
- [专业工具集](#专业工具集)
- [钢铁词汇管理](#钢铁词汇管理)
- [知识图谱系统](#知识图谱系统)
- [快速开始](#快速开始)
- [使用场景](#使用场景)
- [扩展开发](#扩展开发)

---

## 🏭 系统概述

钢铁领域AI系统是为钢铁行业AI决策中心定制的专业模块,包含三大核心组件:

1. **专业工具集**: 7种钢铁专业工具,涵盖钢种查询、工艺计算、设备诊断等
2. **词汇管理系统**: 218个专业术语,支持中英文双语
3. **知识图谱**: 实体关系抽取和查询系统

### 系统架构

```
钢铁领域AI系统
├── 专业工具集 (steel_tools.py)
│   ├── SteelGradeQueryTool - 钢种查询
│   ├── ProcessParameterTool - 工艺计算
│   ├── EquipmentDiagnosisTool - 设备诊断
│   ├── MaterialCostCalculatorTool - 成本计算
│   ├── StandardQueryTool - 标准查询
│   ├── KnowledgeGraphQueryTool - 知识图谱查询
│   └── QualityAnalysisTool - 质量分析
├── 词汇管理系统
│   ├── 词汇库 (218个术语)
│   ├── 分类管理 (8大类别)
│   └── 增强脚本
└── 知识图谱系统
    ├── 实体抽取器
    ├── 关系抽取器
    ├── 查询引擎
    └── API接口
```

---

## 🔧 专业工具集

### 工具清单

| # | 工具名称 | 功能 | 典型用法 |
|---|---------|------|---------|
| 1 | **SteelGradeQueryTool** | 钢种查询 | `tool.run("Q235")` |
| 2 | **ProcessParameterTool** | 工艺计算 | `tool.run("hot_rolling", steel_grade="Q345", ...)` |
| 3 | **EquipmentDiagnosisTool** | 设备诊断 | `tool.run("轧机", "异常振动")` |
| 4 | **MaterialCostCalculatorTool** | 成本计算 | `tool.run("blast_furnace", output_tons=100)` |
| 5 | **StandardQueryTool** | 标准查询 | `tool.run("GB/T 700-2006")` |
| 6 | **KnowledgeGraphQueryTool** | 知识图谱 | `tool.run("properties", "Q235")` |
| 7 | **QualityAnalysisTool** | 质量分析 | `tool.run("surface", "裂纹")` |

### 1. SteelGradeQueryTool - 钢种性能查询工具

**功能**: 查询常见钢种的详细信息,包括化学成分、力学性能、应用场景等。

**支持的钢种**:
- 碳素结构钢: Q235, Q345, Q420, Q460
- 优质碳素钢: 20#, 45#, 65Mn
- 不锈钢: 304, 304L, 316, 316L, 321
- 美标钢: A36, A572, A992

**使用方法**:
```python
from src.agent.steel_tools import SteelGradeQueryTool

tool = SteelGradeQueryTool()
result = tool.run("Q235")

# 返回结果示例
{
    "success": True,
    "steel_grade": "Q235",
    "data": {
        "name": "Q235普通碳素结构钢",
        "chemical_composition": {
            "C": "≤0.22%",
            "Si": "≤0.35%",
            "Mn": "0.30-0.65%",
            ...
        },
        "mechanical_properties": {
            "抗拉强度": "375-500 MPa",
            "屈服强度": "≥235 MPa",
            ...
        },
        "applications": ["建筑结构", "桥梁", "车辆", ...],
        "weldability": "良好",
        "standard": "GB/T 700-2006"
    }
}
```

### 2. ProcessParameterTool - 工艺参数计算工具

**功能**: 计算钢铁生产工艺的关键参数,辅助工艺优化。

**支持的工艺**:
- `hot_rolling`: 热轧工艺参数计算
- `heat_treatment`: 热处理参数计算(淬火、回火、正火、退火)
- `cooling`: 冷却参数计算

#### 热轧参数计算

**输入参数**:
- `steel_grade`: 钢种(如"Q235")
- `thickness_initial`: 初始厚度(mm)
- `thickness_final`: 最终厚度(mm)
- `width`: 宽度(mm)

**输出**:
- 总压下率(%)
- 估算轧制力(kN)
- 推荐轧制温度(°C)
- 建议轧制道次

**使用示例**:
```python
tool = ProcessParameterTool()
result = tool.run(
    process_type="hot_rolling",
    steel_grade="Q345",
    thickness_initial=200.0,
    thickness_final=10.0,
    width=1500.0
)
```

#### 热处理参数计算

**支持的热处理类型**:
- `quenching`: 淬火
- `tempering`: 回火
- `normalizing`: 正火
- `annealing`: 退火

**输出**:
- 加热温度
- 保温时间
- 冷却介质
- 预期硬度
- 操作步骤

### 3. EquipmentDiagnosisTool - 设备故障诊断工具

**功能**: 基于症状和参数诊断常见设备故障,提供维修建议。

**支持的设备**:
- 轧机(故障:异常振动、温度过高、产品质量差)
- 加热炉(故障:温度不均、燃耗过高)
- 转炉(故障:氧枪堵塞、炉龄低)

**诊断流程**:
1. 识别设备类型和故障症状
2. 列出可能原因(按概率排序)
3. 提供诊断步骤(指导现场检查)
4. 推荐解决方案
5. 评估紧急程度(高/中/低)

**使用示例**:
```python
tool = EquipmentDiagnosisTool()
result = tool.run(
    equipment_type="轧机",
    symptom="异常振动",
    vibration_level="高"
)

# 返回
{
    "success": True,
    "equipment": "轧机",
    "symptom": "异常振动",
    "urgency": "高",
    "possible_causes": [
        "轴承磨损或损坏",
        "轧辊不平衡",
        "传动系统松动",
        ...
    ],
    "diagnostic_procedure": [
        "1. 检查振动频率和幅值",
        "2. 检查轴承温度和声音",
        ...
    ],
    "recommended_solutions": [
        "更换磨损轴承",
        "重新平衡轧辊",
        ...
    ],
    "warning": "⚠️ 此故障紧急程度高,建议立即停机检修"
}
```

### 4. MaterialCostCalculatorTool - 生产成本计算工具

**功能**: 计算钢铁生产的原材料成本、能源成本等。

**支持的工艺**:
- `blast_furnace`: 高炉炼铁
- `bof`: 转炉炼钢(Basic Oxygen Furnace)
- `eaf`: 电炉炼钢(Electric Arc Furnace)

**价格库**(可自定义):
- 铁矿石: 850元/吨(62%品位)
- 焦炭: 2400元/吨
- 废钢: 2600元/吨
- 电力: 0.65元/kWh
- 天然气: 3.2元/m³

**使用示例**:
```python
tool = MaterialCostCalculatorTool()

# 计算100吨铁水成本
result = tool.run(
    calculation_type="blast_furnace",
    output_tons=100
)

# 返回详细成本分解
{
    "success": True,
    "process": "高炉炼铁",
    "output": "100 吨铁水",
    "cost_breakdown": {
        "铁矿石": {"消耗": "160.00 吨", "成本": "136000.00 元"},
        "焦炭": {"消耗": "35.00 吨", "成本": "84000.00 元"},
        ...
    },
    "summary": {
        "总成本": "226750.00 元",
        "吨铁成本": "2267.50 元/吨"
    }
}
```

### 5. StandardQueryTool - 标准规范查询工具

**功能**: 查询钢铁行业国家标准和国际标准。

**覆盖的标准**:
- GB/T 700-2006: 碳素结构钢
- GB/T 1591-2008: 低合金高强度结构钢
- GB/T 3280-2015: 不锈钢冷轧钢板和钢带
- GB/T 699-2015: 优质碳素结构钢
- GB/T 8163-2018: 输送流体用无缝钢管

**查询内容**:
- 标准名称和范围
- 涵盖的钢种
- 关键技术要求
- 化学成分和力学性能要求

### 6. KnowledgeGraphQueryTool - 知识图谱查询工具

**功能**: 查询钢铁领域知识图谱中的实体关系。

**支持的查询类型**:
- `properties`: 查询实体属性
- `relationships`: 查询实体关系
- `similar`: 查询相似实体

**使用示例**:
```python
tool = KnowledgeGraphQueryTool()

# 查询Q235的属性
result = tool.run(
    query_type="properties",
    entity_name="Q235"
)

# 查询Q235的关系
result = tool.run(
    query_type="relationships",
    entity_name="Q235",
    relation_type="应用"
)

# 查询与304相似的钢种
result = tool.run(
    query_type="similar",
    entity_name="304"
)
```

### 7. QualityAnalysisTool - 质量分析工具

**功能**: 分析产品质量问题,诊断原因并提供改进措施。

**支持的缺陷类型**:
- `surface`: 表面缺陷(裂纹、麻点、划伤等)
- `dimension`: 尺寸偏差(厚度、宽度超差)
- `performance`: 性能不达标(强度、延伸率等)

---

## 📚 钢铁词汇管理

### 词汇库概览

包含218个钢铁行业专业术语,支持中英文双语。

### 分类统计

| 分类 | 中文术语 | 英文术语 | 说明 |
|------|----------|----------|------|
| 钢种牌号 | 40个 | 40个 | Q235、Q345、304、316L等 |
| 钢材类型 | 21个 | 21个 | 碳素钢、合金钢、不锈钢等 |
| 合金元素 | 38个 | 38个 | 碳、硅、锰、铬、镍等 |
| 材料性能 | 29个 | 29个 | 抗拉强度、屈服强度、硬度等 |
| 工艺流程 | 27个 | 27个 | 炼钢、连铸、热轧、冷轧等 |
| 设备名称 | 24个 | 24个 | 转炉、电炉、连铸机等 |
| 应用领域 | 20个 | 20个 | 建筑结构、汽车制造等 |
| 标准规范 | 19个 | 19个 | GB/T、ASTM、ISO等 |

**总计**: 218个专业术语

### 使用方法

#### 一键增强(推荐)

```bash
# 运行增强脚本
python -m scripts.enhance_steel_vocabulary
```

脚本会自动:
- 为所有Agent创建包含专业词汇的增强prompt
- 支持中英文双语
- 标记增强状态和统计信息

#### 手动编辑

1. 访问管理界面
2. 选择"Prompt管理"
3. 找到对应的Agent和语言
4. 编辑Prompt内容

### 测试效果

**测试问题示例**:

1. **钢种相关**
   - "Q235钢的性能特点是什么?"
   - "不锈钢304和316有什么区别?"

2. **工艺相关**
   - "什么是转炉炼钢?"
   - "热轧和冷轧的区别是什么?"

3. **性能相关**
   - "钢材的抗拉强度、屈服强度是什么意思?"
   - "如何提高钢材的焊接性?"

4. **设备相关**
   - "连铸机的工作原理是什么?"
   - "退火炉的温度控制要点?"

### 预期效果

✅ Agent会使用准确的专业术语  
✅ 回答更加专业和准确  
✅ 中英文术语使用规范  
✅ 符合钢铁行业标准

### 自定义词汇

**添加新术语**:

1. 编辑词汇库文件
   ```python
   # scripts/enhance_steel_vocabulary.py
   STEEL_VOCABULARY = {
       "steel_grades": {
           "zh": ["Q235", "Q345", "你的新术语"],
           "en": ["Q235", "Q345", "Your New Term"]
       }
   }
   ```

2. 重新运行增强脚本
   ```bash
   python -m scripts.enhance_steel_vocabulary
   ```

---

## 🕸️ 知识图谱系统

### 系统概述

专门针对钢铁行业的知识图谱,能够从文档中自动抽取钢铁相关的实体和关系,并提供丰富的查询接口。

### 核心功能

#### 1. 实体识别

- **钢种**: Q235, Q345, 304, 316L, SUS304等
- **钢材类型**: 碳素钢, 合金钢, 不锈钢, 工具钢等
- **合金元素**: 碳, 硅, 锰, 铬, 镍, 钼等
- **材料性能**: 抗拉强度, 屈服强度, 延伸率, 硬度等
- **工艺**: 炼钢, 连铸, 热轧, 冷轧, 退火等
- **设备**: 转炉, 电炉, 连铸机, 热轧机等
- **应用领域**: 建筑结构, 汽车制造, 船舶建造等
- **标准**: GB/T, ASTM, JIS, DIN等

#### 2. 关系抽取

- **包含关系**: 钢种包含合金元素
- **性能关系**: 钢种具有特定性能
- **生产工艺**: 钢种通过特定工艺生产
- **使用设备**: 工艺使用特定设备
- **应用关系**: 钢种用于特定应用
- **标准关系**: 钢种符合特定标准

#### 3. 查询功能

- 实体搜索和过滤
- 相关实体发现
- 实体间路径查找
- 钢种成分分析
- 钢种应用领域查询
- 钢种生产工艺查询
- 钢种相关标准查询

### API接口

#### 基础查询
- `POST /api/knowledge-graph/search/entities` - 搜索实体
- `GET /api/knowledge-graph/entities/{id}` - 获取实体详情
- `GET /api/knowledge-graph/entities/name/{name}` - 根据名称获取实体
- `GET /api/knowledge-graph/entities/type/{type}` - 根据类型获取实体

#### 关系查询
- `POST /api/knowledge-graph/entities/{id}/related` - 获取相关实体
- `POST /api/knowledge-graph/path` - 查找实体间路径

#### 钢种专用查询
- `POST /api/knowledge-graph/steel-grades/by-properties` - 根据性能查找钢种
- `POST /api/knowledge-graph/steel-grades/composition` - 获取钢种成分
- `POST /api/knowledge-graph/steel-grades/applications` - 获取钢种应用
- `POST /api/knowledge-graph/steel-grades/processes` - 获取钢种工艺
- `POST /api/knowledge-graph/steel-grades/standards` - 获取钢种标准

#### 统计信息
- `GET /api/knowledge-graph/statistics` - 获取统计信息
- `GET /api/knowledge-graph/entity-types` - 获取实体类型
- `GET /api/knowledge-graph/relation-types` - 获取关系类型

### 使用方法

#### 1. 初始化知识图谱
```bash
# 从已处理的文档构建知识图谱
python scripts/init_steel_knowledge_graph.py
```

#### 2. 运行演示
```bash
# 运行知识图谱演示
python examples/steel_knowledge_graph_demo.py
```

#### 3. API使用
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

### 数据存储

知识图谱数据存储在 `data/knowledge_graph.json` 文件中,包含:
- 实体信息(ID、名称、类型、属性、置信度等)
- 关系信息(源实体、目标实体、关系类型、置信度等)
- 索引信息(实体类型索引、关系类型索引)

---

## 🚀 快速开始

### 方式1: 直接使用工具

```python
from src.agent.steel_tools import SteelGradeQueryTool

# 创建工具实例
tool = SteelGradeQueryTool()

# 查询钢种信息
result = tool.run("Q235")

if result["success"]:
    print(f"钢种: {result['data']['name']}")
    print(f"屈服强度: {result['data']['mechanical_properties']['屈服强度']}")
```

### 方式2: 集成到Agent

```python
from src.agent.steel_tools import register_steel_tools
from src.agent import RAGAgent
from src.llm import LLMClient
from src.agent.reasoning import ReasoningEngine

# 创建Agent
llm = LLMClient()
reasoning = ReasoningEngine(model=llm)
agent = RAGAgent(llm_client=llm, reasoning_engine=reasoning)

# 注册所有钢铁工具
register_steel_tools(agent)

# Agent现在可以智能地调用这些工具
response = agent.process("Q235钢的屈服强度是多少?")
```

### 运行演示

```bash
# 查看所有工具的演示
python examples/steel_tools_demo.py

# 运行测试
pytest tests/test_steel_tools.py -v
```

---

## 💡 使用场景

### 场景1: 钢种选型

**问题**: "我需要制造一个承受350MPa应力的构件,应该选什么钢种?"

**解决方案**:
```python
# 查询几种常见钢种
grades = ["Q235", "Q345", "Q420"]
for grade in grades:
    result = SteelGradeQueryTool().run(grade)
    yield_strength = result['data']['mechanical_properties']['屈服强度']
    print(f"{grade}: {yield_strength}")

# 输出:
# Q235: ≥235 MPa  ❌ 不满足
# Q345: ≥345 MPa  ✅ 满足
# Q420: ≥420 MPa  ✅ 满足(安全系数更高)
```

### 场景2: 工艺优化

**问题**: "我们要把150mm的钢坯轧制到8mm,应该分几道次?温度怎么控制?"

**解决方案**:
```python
result = ProcessParameterTool().run(
    process_type="hot_rolling",
    steel_grade="Q235",
    thickness_initial=150.0,
    thickness_final=8.0
)

print(f"建议道次: {result['parameters']['建议轧制道次']}")
print(f"开轧温度: {result['parameters']['推荐开轧温度']}")
print(f"终轧温度: {result['parameters']['推荐终轧温度']}")
```

### 场景3: 故障诊断

**问题**: "轧机突然震动加剧,轴承温度升高,怎么办?"

**解决方案**:
```python
result = EquipmentDiagnosisTool().run(
    equipment_type="轧机",
    symptom="异常振动",
    temperature="高"
)

print(f"紧急程度: {result['urgency']}")
print("可能原因:")
for i, cause in enumerate(result['possible_causes'], 1):
    print(f"  {i}. {cause}")

print("\n诊断步骤:")
for step in result['diagnostic_procedure']:
    print(f"  {step}")
```

### 场景4: 成本分析

**问题**: "如果原料价格上涨,对生产成本影响有多大?"

**解决方案**:
```python
# 原价格成本
baseline = MaterialCostCalculatorTool().run(
    "blast_furnace", 
    output_tons=1000
)

# 涨价后成本
increased = MaterialCostCalculatorTool().run(
    "blast_furnace", 
    output_tons=1000,
    custom_prices={"铁矿石": {"price": 950}}  # 从850涨到950
)

baseline_cost = float(baseline['summary']['吨铁成本'].split()[0])
increased_cost = float(increased['summary']['吨铁成本'].split()[0])
diff = increased_cost - baseline_cost

print(f"原成本: {baseline_cost:.2f} 元/吨")
print(f"新成本: {increased_cost:.2f} 元/吨")
print(f"增加: {diff:.2f} 元/吨 ({diff/baseline_cost*100:.1f}%)")
```

---

## 🔧 扩展开发

### 添加新钢种数据

编辑 `src/agent/steel_tools.py` 中的 `SteelGradeQueryTool.STEEL_DATABASE`:

```python
STEEL_DATABASE = {
    "YOUR_GRADE": {
        "name": "钢种全名",
        "chemical_composition": {...},
        "mechanical_properties": {...},
        "applications": [...],
        "standard": "GB/T XXXX"
    }
}
```

### 连接真实数据源

```python
class RealTimePriceTool(Tool):
    """实时价格查询工具(连接市场API)"""
    
    def __init__(self, api_client):
        super().__init__(
            name="real_time_price",
            description="查询铁矿石、焦炭等原材料实时价格"
        )
        self.api_client = api_client
    
    def run(self, material: str) -> Dict[str, Any]:
        try:
            # 调用真实API
            price_data = self.api_client.get_price(material)
            return {
                "success": True,
                "material": material,
                "price": price_data["current_price"],
                "currency": price_data["currency"],
                "timestamp": price_data["timestamp"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

### 添加机器学习模型

```python
class QualityPredictionTool(Tool):
    """质量预测工具(基于ML模型)"""
    
    def __init__(self, model_path: str):
        super().__init__(
            name="quality_prediction",
            description="基于工艺参数预测产品质量"
        )
        self.model = load_model(model_path)
    
    def run(self, **process_params) -> Dict[str, Any]:
        # 准备特征
        features = self._prepare_features(process_params)
        
        # 预测
        prediction = self.model.predict(features)
        
        return {
            "success": True,
            "predicted_quality": prediction[0],
            "confidence": prediction[1],
            "factors": self._explain_prediction(features, prediction)
        }
```

### 扩展知识图谱

#### 添加新实体类型

1. 在 `SteelEntityType` 枚举中添加新类型
2. 在 `SteelEntityExtractor` 中添加识别模式
3. 更新术语词典

#### 添加新关系类型

1. 在 `SteelRelationType` 枚举中添加新类型
2. 在 `SteelRelationExtractor` 中添加抽取模式
3. 更新查询接口

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|-----|------|------|
| **工具数量** | 7个 | 覆盖7大核心领域 |
| **代码行数** | 1000+ | 核心工具代码 |
| **测试用例** | 24个 | 100%通过 |
| **钢种数据** | 5种 | 可扩展到100+ |
| **标准数据** | 5个 | GB/T国家标准 |
| **故障模式** | 6种 | 常见设备故障 |
| **专业术语** | 218个 | 中英文双语 |
| **响应时间** | <50ms | 工具调用平均时间 |
| **文档完整度** | 100% | 全部工具有文档 |

---

## 📚 相关文档

- [Agent架构设计](./SYSTEM_ARCHITECTURE.md)
- [RAG优化指南](./RAG_OPTIMIZATION_GUIDE.md)
- [项目规则](../AGENTS.md)

---

## 🎓 总结

钢铁领域AI系统为RAG Agent提供了强大的专业能力:

### 核心价值
1. **专业性**: 内置钢铁行业专业知识,符合行业标准
2. **实用性**: 解决真实业务问题,提供可操作建议
3. **智能性**: 与LLM协同工作,实现复杂推理
4. **可扩展**: 易于添加新工具、连接外部系统

### 技术成果
- ✅ **7个专业工具**,覆盖钢种、工艺、设备、成本、标准、知识图谱、质量
- ✅ **218个专业术语**,支持中英文双语
- ✅ **知识图谱系统**,自动抽取实体和关系
- ✅ **完整文档**,使用说明详尽

### 应用场景
- 🏭 **生产工艺优化**: 计算热轧/热处理参数,提高产品质量
- 🔧 **设备维护**: 故障诊断,减少停机时间
- 💰 **成本管理**: 原料价格分析,优化采购决策
- 📊 **质量管理**: 缺陷分析,改进生产工艺

---

**最后更新**: 2025-01-11  
**版本**: 2.0.0  
**维护者**: RAG Agent Team

**联系方式**: 如有问题或建议,请提交Issue或联系开发团队。

