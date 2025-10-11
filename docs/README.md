# RAG Agent 项目文档中心

> 本文档中心提供RAG Agent系统的完整文档,包括快速开始、系统架构、功能指南等。

---

## 📚 文档导航

### 🚀 快速开始

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [quick_start.md](./quick_start.md) | 项目快速开始指南 | 新用户 |
| [usage_examples.md](./usage_examples.md) | 使用示例和场景 | 所有用户 |

### 🏗️ 系统架构

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) | 完整系统架构设计 | 开发者、架构师 |
| [NETWORK_SETUP_GUIDE.md](./NETWORK_SETUP_GUIDE.md) | 网络配置指南 | 运维人员 |

### ⚡ 核心功能指南

#### 1. RAG检索优化

| 文档 | 描述 | 内容 |
|------|------|------|
| **[RAG_OPTIMIZATION_GUIDE.md](./RAG_OPTIMIZATION_GUIDE.md)** | RAG检索性能优化完整指南 | 快速开始、详细实施、配置调优、故障排查、进阶优化 |

**包含内容**:
- ⚡ 5分钟快速开始
- 📊 优化概览(IVF+PQ索引、两级缓存)
- 📋 详细实施步骤
- 🔧 配置调优指南
- 📈 性能监控
- 🐛 故障排查
- 💡 进阶优化(GPU加速、分布式等)
- 📊 性能基准参考

**适合**: 需要优化RAG检索性能的开发者

---

#### 2. Prompt管理系统

| 文档 | 描述 | 内容 |
|------|------|------|
| **[PROMPT_MANAGEMENT_GUIDE.md](./PROMPT_MANAGEMENT_GUIDE.md)** | Prompt管理系统完整指南 | 系统概述、API文档、核心组件、最佳实践 |

**包含内容**:
- ✨ 系统概述和核心特性
- 🏗️ 系统架构
- 🚀 快速开始
- 📖 完整API文档
  - 智能体管理
  - 提示词管理
  - 版本管理
  - 使用统计
  - 分析功能
  - 缓存管理
- 🔧 核心组件
- 💡 最佳实践
- 🧪 测试与部署

**适合**: 需要管理智能体和提示词的开发者、管理员

---

#### 3. 钢铁领域AI系统

| 文档 | 描述 | 内容 |
|------|------|------|
| **[STEEL_DOMAIN_GUIDE.md](./STEEL_DOMAIN_GUIDE.md)** | 钢铁领域AI系统完整指南 | 专业工具集、词汇管理、知识图谱 |

**包含内容**:
- 🏭 系统概述
- 🔧 专业工具集(7种工具)
  - SteelGradeQueryTool - 钢种查询
  - ProcessParameterTool - 工艺计算
  - EquipmentDiagnosisTool - 设备诊断
  - MaterialCostCalculatorTool - 成本计算
  - StandardQueryTool - 标准查询
  - KnowledgeGraphQueryTool - 知识图谱查询
  - QualityAnalysisTool - 质量分析
- 📚 钢铁词汇管理(218个专业术语)
- 🕸️ 知识图谱系统
- 💡 使用场景
- 🔧 扩展开发

**适合**: 钢铁行业应用开发者、领域专家

---

## 📖 文档版本历史

### v2.0.0 (2025-01-11)

**文档重组**:
- ✅ 整合RAG优化相关文档(4个→1个)
- ✅ 整合Prompt管理文档(2个→1个)
- ✅ 整合钢铁领域文档(3个→1个)
- ✅ 创建文档导航中心

**改进**:
- 📝 统一文档结构和格式
- 🔍 增强可读性和查找性
- 📊 添加完整目录和导航
- ✅ 减少文档冗余

### v1.0.0 (之前)

原始文档结构:
- RAG相关: 4个独立文档
- Prompt管理: 2个独立文档
- 钢铁领域: 3个独立文档
- 其他: 4个独立文档

---

## 🗺️ 文档地图

```
docs/
├── README.md (本文件)                    # 📍 你在这里
│
├── 🚀 快速开始
│   ├── quick_start.md                   # 项目快速开始
│   └── usage_examples.md                # 使用示例
│
├── 🏗️ 系统架构
│   ├── SYSTEM_ARCHITECTURE.md           # 完整系统架构
│   └── NETWORK_SETUP_GUIDE.md           # 网络配置
│
└── ⚡ 核心功能指南
    ├── RAG_OPTIMIZATION_GUIDE.md        # RAG优化完整指南
    ├── PROMPT_MANAGEMENT_GUIDE.md       # Prompt管理完整指南
    └── STEEL_DOMAIN_GUIDE.md            # 钢铁领域完整指南
```

---

## 🎯 使用建议

### 新用户入门路径

1. **第1天**: 阅读 [quick_start.md](./quick_start.md)
2. **第2-3天**: 阅读 [usage_examples.md](./usage_examples.md)
3. **第4天+**: 根据需求阅读相关专题文档

### 开发者学习路径

1. **系统架构**: [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
2. **RAG优化**: [RAG_OPTIMIZATION_GUIDE.md](./RAG_OPTIMIZATION_GUIDE.md)
3. **Prompt管理**: [PROMPT_MANAGEMENT_GUIDE.md](./PROMPT_MANAGEMENT_GUIDE.md)
4. **领域定制**: [STEEL_DOMAIN_GUIDE.md](./STEEL_DOMAIN_GUIDE.md)

### 运维人员路径

1. **网络配置**: [NETWORK_SETUP_GUIDE.md](./NETWORK_SETUP_GUIDE.md)
2. **性能优化**: [RAG_OPTIMIZATION_GUIDE.md](./RAG_OPTIMIZATION_GUIDE.md) - 性能监控章节
3. **系统监控**: [PROMPT_MANAGEMENT_GUIDE.md](./PROMPT_MANAGEMENT_GUIDE.md) - 性能章节

---

## 📊 文档统计

| 类别 | 文档数量 | 总字数 | 说明 |
|------|---------|-------|------|
| 快速开始 | 2个 | ~15k | 入门必读 |
| 系统架构 | 2个 | ~160k | 深入理解 |
| 核心功能 | 3个 | ~35k | 专题指南 |
| **总计** | **7个** | **~210k** | 完整文档库 |

---

## 🔄 文档更新

### 如何贡献文档

1. **发现问题**: 提交Issue说明问题
2. **提出改进**: Fork项目并修改文档
3. **提交PR**: 创建Pull Request
4. **代码审查**: 等待审查和合并

### 文档规范

- ✅ 使用Markdown格式
- ✅ 添加清晰的标题层级
- ✅ 包含代码示例
- ✅ 提供截图或图表(如适用)
- ✅ 更新文档版本信息

---

## 💡 常见问题

### Q: 文档太多,从哪里开始?

**A**: 
- 如果你是新用户,从 [quick_start.md](./quick_start.md) 开始
- 如果你是开发者,从 [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) 开始
- 如果你有特定需求,直接查看对应的专题指南

### Q: 文档会定期更新吗?

**A**: 是的,文档会随着系统更新而更新。每次重大更新都会在文档版本历史中记录。

### Q: 发现文档错误怎么办?

**A**: 请提交Issue或直接提交PR修正。

### Q: 需要更详细的某个主题说明?

**A**: 请提交Issue说明需求,我们会考虑增加相关内容。

---

## 📞 联系我们

- 📧 邮箱: support@example.com
- 💬 讨论: [GitHub Discussions](https://github.com/example/rag-agent/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/example/rag-agent/issues)
- 📖 在线文档: [docs.example.com](https://docs.example.com)

---

## 📄 相关文档

- [主项目README](../README.md)
- [项目规则](../AGENTS.md)
- [开发指南](../DEVELOPING.md)

---

<div align="center">
  <strong>📚 让每个人都能快速上手RAG Agent系统</strong>
</div>

---

**最后更新**: 2025-01-11  
**文档版本**: 2.0.0  
**维护者**: RAG Agent Team

