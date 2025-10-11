# 废弃脚本说明

> ⚠️ **警告**: 此目录中的所有脚本已被废弃，不再维护。请使用新的统一 CLI 工具。

## 📢 重要通知

自 **v2.0.0 (2025-10-11)** 起，scripts 目录已经过重构。所有功能已整合到两个统一的 CLI 工具中：

- **`rag_cli.py`** - RAG 系统管理
- **`db_migrate.py`** - 数据库管理

## 🗑️ 废弃脚本列表

| 废弃脚本 | 替代方案 | 说明 |
|---------|---------|------|
| `build_rag_system.py` | `python scripts/rag_cli.py build` | RAG 系统构建 |
| `data_ingestion.py` | `python scripts/rag_cli.py build` | 数据摄入 |
| `example_rag_usage.py` | `python scripts/rag_cli.py search --interactive` | 交互式搜索 |
| `reset_database.py` | `python scripts/db_migrate.py reset` | 重置数据库 |
| `migrate_add_preset_questions.py` | `python scripts/db_migrate.py add-presets` | 添加预设问题表 |
| `migrate_add_vocabulary_table.py` | `python scripts/db_migrate.py add-vocabulary` | 添加词汇表 |
| `migrate_add_prompt_tables.py` | `python scripts/db_migrate.py add-prompts` | 添加 Prompt 表 |

## 🔄 迁移指南

### 快速迁移

**旧方式：**
```bash
# 构建 RAG
python scripts/build_rag_system.py --rebuild

# 搜索文档
python scripts/example_rag_usage.py --interactive

# 重置数据库
python scripts/reset_database.py
```

**新方式：**
```bash
# 构建 RAG
python scripts/rag_cli.py build --rebuild

# 搜索文档
python scripts/rag_cli.py search --interactive

# 重置数据库
python scripts/db_migrate.py reset
```

## ❓ 为什么废弃？

### 问题
- 脚本分散，难以管理
- 代码重复率高
- 用户体验不一致
- 缺乏统一标准

### 改进
- ✅ 统一的 CLI 接口
- ✅ 代码复用率提高
- ✅ 一致的用户体验
- ✅ 更好的错误处理
- ✅ 完善的帮助文档

## 📚 新工具文档

详细使用方法请参考：

- **快速开始**: [../README.md](../README.md)
- **RAG 技术**: [../RAG_README.md](../RAG_README.md)
- **项目规范**: [../../AGENTS.md](../../AGENTS.md)

## ⚠️ 使用建议

1. **不推荐继续使用这些脚本**
   - 不再维护和更新
   - 可能存在未修复的问题
   - 缺少新功能

2. **请尽快迁移到新工具**
   - 功能完全兼容
   - 更好的用户体验
   - 持续维护和支持

3. **遇到问题请使用新工具**
   - 报告问题时请使用新工具复现
   - Issue 中注明使用的工具版本

## 🗓️ 移除计划

- **立即（2025-10-11）**: 脚本移至 deprecated 目录 ✅
- **1个月后**: 在文档中移除所有旧脚本引用
- **3个月后**: 在新工具中移除对旧脚本的兼容
- **6个月后**: 完全删除 deprecated 目录

## 📞 获取帮助

如有疑问，请：

1. 查看新工具文档：`python scripts/rag_cli.py --help`
2. 阅读主文档：[../README.md](../README.md)
3. 提交 Issue：在项目中创建问题反馈
4. 查看项目规范：[../../AGENTS.md](../../AGENTS.md)

---

**最后更新**: 2025-10-11  
**状态**: ⚠️ 已废弃，不再维护  
**推荐**: 使用 `rag_cli.py` 和 `db_migrate.py`

