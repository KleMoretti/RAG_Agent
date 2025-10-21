# Markdown 渲染示例文档

本文档展示了聊天界面支持的各种 Markdown 格式。

## 基本格式

### 文本强调

这是 **粗体文本**，这是 *斜体文本*，这是 ~~删除线文本~~。

你也可以组合使用：***粗斜体文本***

### 标题层级

# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题

## 列表

### 无序列表

- 钢铁生产主要工艺流程
  - 炼铁工序
  - 炼钢工序
  - 轧钢工序
- 质量控制要点
  - 温度监控
  - 成分分析
  - 尺寸检测

### 有序列表

1. 高炉炼铁
2. 转炉炼钢
3. 连铸成型
4. 热轧加工
5. 冷轧精整

## 代码展示

### 行内代码

使用 `temperature > 1500°C` 进行温度判断，配置参数 `max_pressure = 150MPa`。

### 代码块

```python
# 钢铁生产参数计算
def calculate_steel_quality(temperature, carbon_content, cooling_rate):
    """
    计算钢材质量等级
    
    Args:
        temperature: 冶炼温度（摄氏度）
        carbon_content: 碳含量（百分比）
        cooling_rate: 冷却速率（度/分钟）
    
    Returns:
        质量等级：A/B/C
    """
    if temperature < 1400:
        return "C"
    
    if carbon_content > 0.8:
        quality_score = temperature * 0.6 + cooling_rate * 0.4
    else:
        quality_score = temperature * 0.7 + cooling_rate * 0.3
    
    if quality_score > 1000:
        return "A"
    elif quality_score > 800:
        return "B"
    else:
        return "C"

# 示例调用
result = calculate_steel_quality(1550, 0.45, 50)
print(f"钢材质量等级: {result}")
```

```javascript
// 设备监控数据处理
const processEquipmentData = (sensorData) => {
  const { temperature, pressure, vibration } = sensorData;
  
  // 异常检测
  const alerts = [];
  
  if (temperature > 1600) {
    alerts.push({ type: 'warning', message: '温度过高' });
  }
  
  if (pressure > 160) {
    alerts.push({ type: 'critical', message: '压力超限' });
  }
  
  if (vibration > 5.0) {
    alerts.push({ type: 'info', message: '振动异常' });
  }
  
  return { status: alerts.length === 0 ? 'normal' : 'alert', alerts };
};
```

```sql
-- 查询生产数据统计
SELECT 
    production_date,
    furnace_id,
    AVG(temperature) as avg_temp,
    SUM(output_tonnage) as total_output,
    COUNT(*) as batch_count
FROM steel_production
WHERE production_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY production_date, furnace_id
ORDER BY production_date DESC, total_output DESC;
```

## 引用块

> **重要提示：** 在高温作业环境下，必须严格遵守安全操作规程。
> 
> 所有进入炼钢车间的人员必须佩戴：
> - 防护头盔
> - 防护眼镜
> - 耐高温手套
> - 防护服

> 根据 GB/T 1591-2018 标准，低合金高强度结构钢的碳含量应控制在 0.20% 以下。

## 表格

### 钢材成分标准表

| 元素 | 符号 | 标准含量 (%) | 作用 |
|------|------|--------------|------|
| 碳 | C | 0.15-0.20 | 提高强度和硬度 |
| 硅 | Si | 0.20-0.35 | 脱氧剂，提高韧性 |
| 锰 | Mn | 1.20-1.60 | 脱硫，提高强度 |
| 磷 | P | ≤ 0.035 | 有害元素，需控制 |
| 硫 | S | ≤ 0.030 | 有害元素，降低韧性 |

### 设备运行参数

| 设备名称 | 额定温度 | 工作压力 | 日产能 | 维护周期 |
|----------|----------|----------|--------|----------|
| 高炉 #1 | 1500°C | 120 MPa | 2000吨 | 每月 |
| 转炉 #2 | 1650°C | 150 MPa | 1800吨 | 每月 |
| 轧机 #3 | 1100°C | 80 MPa | 3000吨 | 每季度 |

## 链接

- [钢铁行业标准文档](https://example.com/standards)
- [设备维护手册](https://example.com/maintenance)
- [生产安全规范](https://example.com/safety)

访问 [国家标准化管理委员会](https://www.sac.gov.cn/) 获取最新标准。

## 分割线

以下是不同类型的工艺流程：

---

### 炼铁工艺

高炉炼铁是将铁矿石还原成生铁的过程...

---

### 炼钢工艺

转炉炼钢通过氧气吹炼降低碳含量...

---

## 混合内容示例

### 问题诊断流程

当遇到 **设备温度异常** 时，按以下步骤排查：

1. **检查传感器状态**
   ```bash
   # 查询传感器读数
   sensor_query --device=furnace_01 --param=temperature
   ```

2. **分析历史数据**
   
   | 时间 | 温度 (°C) | 状态 |
   |------|-----------|------|
   | 10:00 | 1520 | 正常 |
   | 10:30 | 1680 | 偏高 |
   | 11:00 | 1850 | **异常** |

3. **检查冷却系统**
   > ⚠️ 警告：如果冷却水流量低于 50 L/min，需要立即停机检查。

4. **记录处理结果**
   - [ ] 确认故障原因
   - [ ] 实施纠正措施
   - [ ] 更新维护记录
   - [ ] 培训操作人员

### 钢材质量等级判定

根据不同的 `碳含量` 和 `抗拉强度`，钢材分为以下等级：

- **A级（优质钢）**：抗拉强度 ≥ 500 MPa，碳含量 0.15-0.20%
- **B级（普通钢）**：抗拉强度 400-500 MPa，碳含量 0.20-0.25%
- **C级（低碳钢）**：抗拉强度 < 400 MPa，碳含量 < 0.15%

---

## 特殊符号和公式

### 常用化学方程式

**炼铁反应：**
- Fe₂O₃ + 3CO → 2Fe + 3CO₂
- FeO + CO → Fe + CO₂

**炼钢反应：**
- C + ½O₂ → CO
- Si + O₂ → SiO₂
- Mn + ½O₂ → MnO

### 计算公式（文本表示）

钢材强度计算：
```
σ = F / A

其中：
σ - 应力 (MPa)
F - 作用力 (N)
A - 截面积 (mm²)
```

冷却速率：
```
v = ΔT / Δt

其中：
v - 冷却速率 (°C/min)
ΔT - 温度变化 (°C)
Δt - 时间间隔 (min)
```

---

## 使用建议

在 AI 对话中，你可以：

✅ **推荐做法：**
- 使用标题结构化回答
- 用代码块展示技术细节
- 用表格对比参数数据
- 用列表罗列要点
- 用引用块强调重要信息

❌ **避免做法：**
- 纯文本堆砌，缺乏层次
- 技术内容不用代码格式
- 数据对比不用表格
- 重要提示没有突出显示

---

## 效果预览

当 AI 返回以下内容时：

```
根据您的描述，设备可能存在以下问题：

**故障诊断结果：**

1. **主要问题**：冷却系统效率下降
   - 冷却水流量：35 L/min（正常值：50-60 L/min）
   - 管道压力：0.8 MPa（正常值：1.2-1.5 MPa）

2. **建议措施**：
   ```python
   # 系统自检程序
   def check_cooling_system():
       flow_rate = get_flow_rate()
       if flow_rate < 50:
           return "需要清理管道或更换泵"
       return "正常"
   ```

3. **维护计划**：

| 项目 | 周期 | 负责人 |
|------|------|--------|
| 清洗管道 | 立即 | 维修组 |
| 更换密封件 | 3天内 | 维修组 |
| 测试流量 | 5天内 | 质检组 |

> ⚠️ **安全提醒**：维护期间需停机操作，注意佩戴防护装备。
```

将会渲染成结构清晰、易于阅读的格式，提升用户体验。

---

**文档版本：** v1.0  
**更新时间：** 2024年  
**适用范围：** 钢铁行业 AI 决策中心聊天界面