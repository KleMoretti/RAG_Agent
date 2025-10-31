# ML目录结构重构 - 更新日志

**更新日期**: 2025-10-31  
**版本**: v2.0  
**影响模块**: ML设备故障检测系统

## 📋 更新摘要

将ML相关数据和模型从分散的 `data/ml_models/` 目录迁移到更加结构化的 `data/ml/` 目录，分离训练数据、原始数据和模型文件。

## 🎯 更新目标

1. **解决训练文件不存在问题** - 明确训练数据的存放位置
2. **解决模型导入错误问题** - 统一模型文件路径
3. **提高数据管理清晰度** - 分离不同类型的数据

## 📂 新的目录结构

```
data/ml/
├── training_data/      # 训练数据（已处理的CSV格式数据）
│   ├── equipment_anomaly_data.csv
│   └── README.md      # 数据格式说明
├── raw_data/           # 原始数据（传感器采集的原始数据）
│   └── README.md      # 原始数据处理指南
└── models/             # 训练好的模型文件
    ├── fault_detector_YYYYMMDD_HHMMSS.pkl
    ├── fault_detector_YYYYMMDD_HHMMSS.pkl.metadata.json
    └── README.md      # 模型使用说明
```

### vs 旧的目录结构

```
data/ml_models/         # ❌ 旧结构（已废弃）
├── equipment_anomaly_data.csv    # 训练数据
├── fault_detector_*.pkl          # 模型文件
└── fault_detector_*.pkl.metadata.json
```

## 🔧 代码更改

### 1. `src/ml/fault_detector.py`

**更改**：模型保存路径

```python
# ❌ 旧代码
self.model_dir = model_dir or Path(cfg.data_dir) / "ml_models"

# ✅ 新代码
project_root = Path(cfg.data_dir).parent  # data/raw -> data
self.model_dir = model_dir or project_root / "ml" / "models"
```

**影响**：
- 所有新训练的模型保存到 `data/ml/models/`
- `load_model()` 从新路径加载模型

### 2. `src/ml/training_data_tool.py`

**更改**：训练数据加载路径

```python
# ❌ 旧代码
self.data_path = Path(cfg.data_dir) / "ml_models" / "equipment_anomaly_data.csv"

# ✅ 新代码
project_root = Path(cfg.data_dir).parent  # data/raw -> data
self.data_path = project_root / "ml" / "training_data" / "equipment_anomaly_data.csv"
```

**影响**：
- TrainingDataQueryTool 从新路径加载训练数据
- Agent 查询训练数据时使用新路径

### 3. `scripts/migrate_ml_data.py` (新增)

**功能**：自动迁移脚本

- 创建新的目录结构
- 迁移现有的CSV训练数据文件
- 迁移现有的模型文件（.pkl和.metadata.json）
- 自动生成各目录的README说明文件

**使用方法**：
```bash
python scripts/migrate_ml_data.py
```

## 📝 更新后的命令行示例

### 生成训练数据

```bash
# ❌ 旧命令
python scripts/generate_test_data.py --n-samples 1000 --output equipment_fault_data.csv

# ✅ 新命令
python scripts/generate_test_data.py --n-samples 1000 --output data/ml/training_data/equipment_anomaly_data.csv
```

### 训练模型

```bash
# ❌ 旧命令
python scripts/train_fault_detector.py --data equipment_fault_data.csv

# ✅ 新命令
python scripts/train_fault_detector.py --data data/ml/training_data/equipment_anomaly_data.csv
```

### 测试工具

```bash
# ✅ 无需更改（工具自动使用新路径）
python scripts/test_training_data_tool.py
```

## 🚀 迁移步骤（用户操作）

### 首次使用或升级用户

1. **运行迁移脚本**：
   ```bash
   python scripts/migrate_ml_data.py
   ```

2. **验证迁移结果**：
   ```bash
   # 检查目录结构
   ls -R data/ml/
   
   # 测试训练数据工具
   python scripts/test_training_data_tool.py
   ```

3. **（可选）删除旧目录**：
   ```bash
   # 确认迁移成功后，可以删除旧目录
   rm -rf data/ml_models/
   ```

### 新用户

直接运行迁移脚本创建目录结构：
```bash
python scripts/migrate_ml_data.py
```

然后按照正常流程生成数据和训练模型。

## ✅ 验证测试

### 测试1：检查目录结构

```bash
python -c "from pathlib import Path; \
           ml = Path('data/ml'); \
           print('训练数据:', (ml/'training_data').exists()); \
           print('原始数据:', (ml/'raw_data').exists()); \
           print('模型目录:', (ml/'models').exists())"
```

**预期输出**：
```
训练数据: True
原始数据: True
模型目录: True
```

### 测试2：测试训练数据工具

```bash
python -c "from src.ml.training_data_tool import TrainingDataQueryTool; \
           tool = TrainingDataQueryTool(); \
           print('工具路径:', tool.data_path); \
           result = tool.execute(query_type='statistics'); \
           print('查询成功!' if '总样本数' in result else '查询失败')"
```

**预期输出**：
```
工具路径: data\ml\training_data\equipment_anomaly_data.csv
✅ 已加载训练数据: 7672 条记录
查询成功!
```

### 测试3：测试故障检测器

```bash
python -c "from src.ml.fault_detector import FaultDetector; \
           detector = FaultDetector(); \
           print('模型目录:', detector.model_dir); \
           print('目录存在:', detector.model_dir.exists())"
```

**预期输出**：
```
模型目录: data\ml\models
目录存在: True
```

## 📚 相关文档更新

以下文档已更新以反映新的目录结构：

1. **AGENTS.md** - 主文档
   - ✅ 钢铁设备监控系统章节
   - ✅ 快速开始章节
   - ✅ 使用场景示例
   - ✅ 故障排查章节
   - ✅ 新增ML目录迁移说明

2. **data/ml/README.md** - ML根目录说明（自动生成）
3. **data/ml/training_data/README.md** - 训练数据说明（自动生成）
4. **data/ml/raw_data/README.md** - 原始数据说明（自动生成）
5. **data/ml/models/README.md** - 模型文件说明（自动生成）

## 🐛 已知问题和解决方案

### 问题1：FileNotFoundError - 训练数据文件不存在

**症状**：
```
FileNotFoundError: 训练数据文件不存在: data\ml\training_data\equipment_anomaly_data.csv
```

**解决方案**：
```bash
# 生成训练数据
python scripts/generate_test_data.py --n-samples 1000 --output data/ml/training_data/equipment_anomaly_data.csv
```

### 问题2：旧路径仍然被引用

**症状**：代码中仍然引用 `data/ml_models/`

**解决方案**：
1. 检查 `cfg.data_dir` 配置（应为 `data/raw`）
2. 确保使用了正确的路径计算：`Path(cfg.data_dir).parent / "ml"`
3. 重启Python解释器清除缓存的模块

### 问题3：模型加载失败

**症状**：
```
ValueError: 模型未加载，请先调用 load_model() 或 train()
```

**解决方案**：
```bash
# 重新训练模型
python scripts/train_fault_detector.py --data data/ml/training_data/equipment_anomaly_data.csv
```

## 💡 最佳实践

### 数据管理

1. **训练数据** (`training_data/`):
   - 存放已经清洗和预处理的CSV格式数据
   - 定期更新以包含最新的故障样本
   - 保留历史版本（使用日期后缀命名）

2. **原始数据** (`raw_data/`):
   - 存放传感器采集的原始数据
   - 可以是CSV、JSON、Excel等格式
   - 用于数据分析和处理流程开发

3. **模型文件** (`models/`):
   - 自动命名（包含时间戳）
   - 保留最近3-5个版本
   - 定期清理旧模型以节省空间

### 版本控制

建议将以下文件添加到 `.gitignore`：
```gitignore
data/ml/training_data/*.csv
data/ml/raw_data/*
data/ml/models/*.pkl
data/ml/models/*.metadata.json
```

但保留README文件：
```gitignore
!data/ml/*/README.md
```

## 🔄 回滚方案

如果需要回滚到旧的目录结构：

1. **恢复代码**：
   ```bash
   git checkout HEAD~1 src/ml/fault_detector.py
   git checkout HEAD~1 src/ml/training_data_tool.py
   ```

2. **复制数据回旧目录**：
   ```bash
   mkdir -p data/ml_models
   cp data/ml/training_data/*.csv data/ml_models/
   cp data/ml/models/fault_detector_*.pkl* data/ml_models/
   ```

3. **重启服务**：
   ```bash
   python manage.py start backend
   ```

## 📞 技术支持

如果遇到问题，请：
1. 检查本文档的"已知问题和解决方案"章节
2. 运行验证测试确认问题
3. 查看 `data/ml/*/README.md` 文件了解详细说明
4. 查看 AGENTS.md 中的"故障排查"章节

## 📊 更新统计

- **新增文件**: 1个脚本 + 4个README
- **修改文件**: 2个源代码文件 + 1个文档
- **受影响的命令**: 2个（generate_test_data.py, train_fault_detector.py）
- **向后兼容性**: ✅ 通过迁移脚本保证数据迁移

## 🎉 更新完成

所有ML相关的问题已解决：
- ✅ 训练文件路径清晰明确
- ✅ 模型导入路径统一规范
- ✅ 目录结构逻辑清晰
- ✅ 数据管理更加便捷

---

**文档版本**: 1.0  
**最后更新**: 2025-10-31  
**维护者**: AI Assistant





