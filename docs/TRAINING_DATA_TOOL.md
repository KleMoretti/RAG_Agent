# 训练数据查询工具使用指南

## 概述

训练数据查询工具 (`TrainingDataQueryTool`) 允许 AI Agent 查询设备故障训练数据，为工艺问题和故障诊断提供数据支持。

## 数据说明

### 数据位置
- 文件路径：`data/ml_models/equipment_anomaly_data.csv`
- 样本数量：7,654 条记录

### 数据字段
| 字段 | 说明 | 数据类型 | 示例 |
|-----|------|---------|-----|
| `temperature` | 设备温度 (°C) | float | 58.18, 148.92 |
| `pressure` | 设备压力 (psi) | float | 25.03, 76.43 |
| `vibration` | 设备振动 (mm/s) | float | 0.61, 4.81 |
| `humidity` | 环境湿度 (%) | float | 45.69, 86.39 |
| `equipment` | 设备类型 | string | Turbine, Compressor, Pump |
| `location` | 设备位置 | string | Atlanta, Chicago, San Francisco, New York, Houston |
| `faulty` | 是否故障 | float | 0.0 (正常), 1.0 (故障) |

## 功能特性

### 1. 整体统计 (statistics)
查询所有训练数据的统计信息。

**使用示例**：
```python
result = tool.execute(query_type="statistics")
```

**返回信息**：
- 总样本数
- 故障样本数和故障率
- 设备类型列表
- 位置分布
- 各参数的最小值、最大值、均值

### 2. 设备类型统计 (equipment_stats)
查询特定设备类型的统计信息。

**使用示例**：
```python
result = tool.execute(
    query_type="equipment_stats",
    equipment_type="Turbine"  # 或 Compressor, Pump
)
```

**返回信息**：
- 该设备类型的样本数
- 故障样本数和故障率
- 参数统计（温度、压力、振动、湿度）

### 3. 故障分析 (fault_analysis)
分析故障样本的特征，对比正常样本。

**使用示例**：
```python
result = tool.execute(query_type="fault_analysis")
```

**返回信息**：
- 故障样本数和占比
- 故障样本的平均参数（温度、压力、振动、湿度）
- 与正常样本的对比
- 各设备类型的故障分布

### 4. 参数范围查询 (parameter_range)
查询特定参数在不同条件下的分布。

**使用示例**：
```python
# 查询故障样本的温度参数
result = tool.execute(
    query_type="parameter_range",
    parameter="temperature",  # 或 pressure, vibration, humidity
    condition="faulty"        # 或 normal, all
)
```

**返回信息**：
- 样本数
- 最小值、最大值
- 均值、中位数
- 标准差
- 25%、75% 分位数

### 5. 对比分析 (compare)
对比正常样本和故障样本的参数差异。

**使用示例**：
```python
result = tool.execute(query_type="compare")
```

**返回信息**：
- 正常样本数和故障样本数
- 各参数在正常/故障状态下的均值
- 差异百分比（↑ 上升，↓ 下降）

## Agent 集成使用

### 工艺专家 Agent 示例

```python
from src.agent.base import BaseAgent
from src.ml.training_data_tool import TrainingDataQueryTool
from src.llm.client import OpenAIClient
from config.settings import get_settings

cfg = get_settings()

# 创建工艺专家 Agent
llm = OpenAIClient(cfg.openai)
agent = BaseAgent(
    llm_client=llm,
    system_prompt="""你是钢铁生产工艺专家。
    当用户询问设备参数、故障模式、历史数据时，优先使用训练数据查询工具。
    示例问题：
    - Turbine 设备的正常温度范围是多少？
    - 故障样本的振动值通常是多少？
    - Compressor 设备的故障率有多高？
    """
)

# 添加训练数据工具
tool = TrainingDataQueryTool()
agent.add_tool(tool)

# 用户查询
response = agent.chat("Turbine 设备的正常温度范围是多少？")
```

**Agent 推理流程**：
1. 识别查询涉及 Turbine 设备的温度参数
2. 调用工具：`training_data_query(query_type="parameter_range", parameter="temperature", condition="normal")`
3. 获取数据：温度范围 50-85°C，均值 67.5°C
4. 生成回答："根据历史训练数据，Turbine 设备的正常温度范围是 50-85°C，平均温度约为 67.5°C。"

### 自动注册（推荐）

系统已将训练数据工具集成到 `register_steel_tools()` 函数中，自动注册给所有 Agent。

```python
from src.agent.steel_tools import register_steel_tools

# Agent 会自动拥有训练数据查询能力
agent = create_agent(llm, system_prompt="...")
register_steel_tools(agent)
```

## 典型查询场景

### 场景 1：工艺参数咨询
**用户问题**：  
"Compressor 设备的正常压力是多少？"

**Agent 执行**：
```python
tool.execute(
    query_type="parameter_range",
    parameter="pressure",
    condition="normal"
)
```

**返回示例**：
```
📊 正常样本的pressure参数
============================================================
样本数: 6432
最小值: 20.15
最大值: 79.98
均值: 45.32
中位数: 44.87
标准差: 12.45
25%分位: 35.21
75%分位: 55.67
```

### 场景 2：故障诊断
**用户问题**：  
"设备温度达到 145°C，这正常吗？"

**Agent 执行**：
```python
# 1. 查询正常温度范围
tool.execute(
    query_type="parameter_range",
    parameter="temperature",
    condition="normal"
)

# 2. 查询故障温度范围
tool.execute(
    query_type="parameter_range",
    parameter="temperature",
    condition="faulty"
)
```

**Agent 推理**：  
"根据训练数据，正常温度范围是 50-85°C，而故障样本的温度通常在 120-150°C。您的设备温度 145°C **明显超出正常范围**，属于故障模式。建议立即停机检查。"

### 场景 3：故障模式分析
**用户问题**：  
"为什么设备故障了？"

**Agent 执行**：
```python
tool.execute(query_type="fault_analysis")
tool.execute(query_type="compare")
```

**返回示例**：
```
⚖️  正常 vs 故障样本对比
============================================================
参数对比 (均值):
  temperature: 正常=67.45, 故障=125.78 (↑86.5%)
  pressure: 正常=45.32, 故障=52.89 (↑16.7%)
  vibration: 正常=1.35, 故障=3.67 (↑171.9%)
  humidity: 正常=48.21, 故障=43.12 (↓10.6%)
```

**Agent 分析**：  
"故障样本的特征是：**温度升高 86.5%**，**振动增加 171.9%**，压力略微升高。这表明故障通常由过热和异常振动引起。建议优先检查冷却系统和轴承状态。"

### 场景 4：设备对比
**用户问题**：  
"Turbine 和 Pump 哪个更容易故障？"

**Agent 执行**：
```python
# 查询 Turbine
tool.execute(query_type="equipment_stats", equipment_type="Turbine")

# 查询 Pump
tool.execute(query_type="equipment_stats", equipment_type="Pump")
```

**Agent 对比**：  
"根据历史数据：
- **Turbine**：故障率 15.3% (52/339)
- **Pump**：故障率 15.3% (50/327)

两种设备的故障率接近，但 Turbine 样本更多。建议根据具体工况和维护记录进一步分析。"

## 最佳实践

### ✅ 推荐用法
1. **工艺参数咨询**：查询正常参数范围，为操作人员提供参考
2. **故障预警**：对比实时参数与训练数据，判断是否异常
3. **故障诊断辅助**：结合训练数据和知识库文档，提供综合诊断
4. **设备对比**：比较不同设备类型的故障率和参数分布

### ❌ 避免误用
1. ❌ 不要将训练数据作为唯一依据（应结合知识库和专家经验）
2. ❌ 不要用于实时监控（训练数据是历史数据，不反映当前状态）
3. ❌ 不要过度依赖平均值（应关注分布和异常值）

### 📋 Agent Prompt 建议

在工艺专家或设备诊断 Agent 的 system_prompt 中添加：

```
当用户询问以下问题时，优先使用训练数据查询工具：
1. 设备的正常参数范围（温度、压力、振动、湿度）
2. 故障样本的特征和模式
3. 不同设备类型的故障率对比
4. 参数异常时的故障判断

使用工具后，结合知识库文档提供全面的分析和建议。
```

## 测试验证

运行测试脚本验证功能：

```bash
# 测试工具功能
python scripts/test_training_data_tool.py

# 示例输出：
# 🧪 测试训练数据查询工具
# ================================================================================
# 【测试 1】整体统计信息
# --------------------------------------------------------------------------------
# 📊 训练数据整体统计
# ============================================================
# 总样本数: 7654
# 故障样本: 1153 (15.1%)
# ...
```

## 故障排查

### 问题 1：文件未找到
**错误**：`FileNotFoundError: 训练数据文件不存在`

**解决方案**：
1. 确认文件位置：`data/ml_models/equipment_anomaly_data.csv`
2. 如果文件在根目录，运行：
   ```bash
   mkdir -p data/ml_models
   move equipment_anomaly_data.csv data/ml_models/
   ```

### 问题 2：工具未注册
**错误**：Agent 无法调用训练数据工具

**解决方案**：
1. 检查是否调用了 `register_steel_tools(agent)`
2. 查看后端日志确认工具加载：
   ```
   ✅ 已加载训练数据: 7654 条记录
   ```

### 问题 3：查询返回空结果
**原因**：参数名称或设备类型拼写错误

**解决方案**：
- 参数名称：`temperature`, `pressure`, `vibration`, `humidity`（小写）
- 设备类型：`Turbine`, `Compressor`, `Pump`（首字母大写）

## 扩展建议

### 未来功能方向
1. **时间序列分析**：如果添加时间戳，可以分析趋势
2. **异常检测**：基于训练数据自动识别异常参数
3. **预测功能**：使用训练模型预测故障概率
4. **多维度筛选**：支持 `location` 和 `equipment` 组合查询

### 与 ML 模型集成
训练数据工具提供数据查询，ML 模型提供预测：

```python
# 查询训练数据（历史统计）
data_result = tool.execute(query_type="compare")

# 预测故障概率（实时预测）
from src.ml.fault_detector import FaultDetector
detector = FaultDetector()
detector.load_model("data/ml_models/fault_detector_latest.pkl")

prediction = detector.predict({
    "temperature": 145.0,
    "pressure": 55.2,
    "vibration": 3.8,
    "humidity": 42.5,
    "equipment_type": "Turbine",
    "location": "Chicago"
})

# 结合两者提供综合诊断
```

## 总结

训练数据查询工具为 AI Agent 提供了**数据驱动的决策支持**能力，使其能够：
- ✅ 基于历史数据回答工艺参数问题
- ✅ 提供故障诊断的数据依据
- ✅ 对比分析不同设备和条件
- ✅ 辅助判断当前参数是否异常

配合知识库检索和专业工具，Agent 可以为用户提供更精准、更可靠的回答。

