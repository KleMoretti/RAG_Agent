# 文件上传与管理

## 概述

系统支持文件上传和智能检索，具备**知识库与用户上传隔离**、**权限分级管理**、**优先检索策略**等特性。

**核心功能**：
- ✅ 多种文件格式支持（PDF、DOCX、TXT、Markdown、CSV、JSON、XML）
- ✅ 双存储架构（知识库 + 用户临时上传，物理隔离）
- ✅ 权限分级（管理员/经理可上传到知识库，所有用户可上传到临时目录）
- ✅ 智能检索优先级（用户上传文件优先，知识库补充）
- ✅ 快速重新索引（无需完整重建）

---

## 系统架构

### 存储结构

```
data/
├── knowledge_base/              # 知识库（管理员维护，持久化）
│   ├── raw/                    # 原始文件
│   └── processed/              # 分块文件（.chunks.jsonl）
├── user_uploads/               # 用户上传（临时文件）
│   ├── raw/                    # 原始文件
│   └── processed/              # 分块文件
└── embeddings/
    ├── knowledge_base.faiss    # 知识库向量索引
    └── user_uploads.faiss      # 用户上传向量索引
```

### 检索策略

```
用户提问
   ↓
1. 先搜索用户上传文件（user_uploads）
   ├── 相似度 > 70%：直接返回
   └── 相似度 < 70%：继续下一步
   ↓
2. 搜索知识库（knowledge_base）
   ↓
3. 合并结果（用户上传结果排在前面）
   ↓
4. 返回 Top-K 结果
```

---

## 快速开始

### 1. 上传文件

#### 方式一：通过前端上传（推荐）

1. 访问 `http://localhost:3000/dashboard/knowledge`
2. 点击"上传文档"按钮
3. **管理员/经理**：选择上传位置（知识库 或 临时上传）
4. **技术员**：自动上传到临时目录
5. 拖拽或选择文件上传

**支持格式**：`.pdf`, `.doc`, `.docx`, `.txt`, `.md`, `.csv`, `.json`, `.xml`

**文件大小**：建议不超过 50MB

#### 方式二：通过 API 上传

```bash
# 上传到用户临时目录（所有用户）
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "upload_type=user_upload"

# 上传到知识库（仅管理员/经理）
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "upload_type=knowledge_base"
```

### 2. 重新索引文件（无需完整重建）

如果需要清理旧索引并重新上传：

#### 步骤 1：清理旧数据

```bash
# 预览将要删除的内容
python scripts/clear_rag_data.py --dry-run

# 清理向量库和processed，保留raw文件（推荐）
python scripts/clear_rag_data.py

# 清理所有数据（包括raw文件）
python scripts/clear_rag_data.py --all

# 清理前先备份
python scripts/clear_rag_data.py --backup
```

#### 步骤 2：批量重新索引

如果保留了 `data/raw/` 中的原始文件：

```bash
# 批量重新索引
python scripts/reindex_raw_files.py
```

**脚本说明**：自动读取 `data/raw/` 中的所有文件并通过 `/api/upload` 接口重新上传。

---

## 权限控制

### 角色权限

| 操作 | ADMIN | MANAGER | TECHNICIAN |
|-----|-------|---------|------------|
| 上传到知识库 | ✅ | ✅ | ❌ |
| 上传到临时目录 | ✅ | ✅ | ✅ |
| 查看知识库文件 | ✅ | ✅ | ✅ (只读) |
| 删除知识库文件 | ✅ | ✅ | ❌ |

### UI 差异

**管理员/经理**：
- 上传对话框显示"上传位置"选择器（知识库 / 临时上传）
- 默认选中"知识库"

**技术员**：
- 不显示上传位置选择器
- 显示蓝色提示："上传到个人临时目录"
- 自动上传到 `user_uploads`

---

## 配置选项

### 配置文件（`config/settings.py`）

```python
class Settings(BaseSettings):
    # 检索优先级配置
    user_upload_score_threshold: float = 0.7  # 用户上传相似度阈值
    enable_priority_search: bool = True       # 启用优先检索
    
    # 存储路径
    knowledge_base_raw_dir: str = "./data/knowledge_base/raw"
    user_uploads_raw_dir: str = "./data/user_uploads/raw"
    knowledge_base_index_path: str = "./data/embeddings/knowledge_base.faiss"
    user_uploads_index_path: str = "./data/embeddings/user_uploads.faiss"
```

### 环境变量（`.env`）

```bash
# 用户上传文件相似度阈值
USER_UPLOAD_SCORE_THRESHOLD=0.7

# 是否启用优先检索
ENABLE_PRIORITY_SEARCH=true
```

---

## API 参考

### 文件上传 API

**端点**：`POST /api/upload`

**参数**：
- `file`：文件对象（multipart/form-data）
- `upload_type`：上传类型
  - `"user_upload"`：上传到临时目录（默认，所有用户）
  - `"knowledge_base"`：上传到知识库（仅管理员/经理）

**响应**：
```json
{
  "success": true,
  "message": "文件上传成功（知识库），已处理为 5 个块",
  "file_id": "abc123_document.pdf",
  "file_name": "document.pdf",
  "file_size": 1048576,
  "content_type": "application/pdf",
  "chunks": [
    {
      "content": "文件内容...",
      "type": "text",
      "length": 500
    }
  ]
}
```

**错误响应**：
```json
{
  "success": false,
  "message": "只有管理员和经理可以上传文件到知识库"
}
```

---

## 数据管理

### 查看索引状态

```bash
# 查看双向量存储统计
python -c "
from main import get_dual_vector_store
store = get_dual_vector_store()
print(f'知识库: {store.kb_size} 个向量')
print(f'用户上传: {store.user_size} 个向量')
print(f'总计: {store.total_size} 个向量')
"
```

### 清空索引

```bash
# 清空用户上传索引（保留知识库）
python -c "
from main import get_dual_vector_store
store = get_dual_vector_store()
store.clear(store_type='user_upload')
store.save(store_type='user_upload')
print('✅ 已清空用户上传索引')
"

# 清空知识库索引（保留用户上传）
python -c "
from main import get_dual_vector_store
store = get_dual_vector_store()
store.clear(store_type='knowledge_base')
store.save(store_type='knowledge_base')
print('✅ 已清空知识库索引')
"

# 清空所有索引
python -c "
from main import get_dual_vector_store
store = get_dual_vector_store()
store.clear(store_type='both')
store.save(store_type='both')
print('✅ 已清空所有索引')
"
```

### 数据迁移

如果从旧版本升级，需要迁移旧文件：

```bash
# 查看帮助
python scripts/migrate_files_to_kb.py --help

# 预览迁移（不实际执行）
python scripts/migrate_files_to_kb.py --dry-run

# 迁移到知识库（默认）
python scripts/migrate_files_to_kb.py --target knowledge_base

# 迁移到用户上传目录
python scripts/migrate_files_to_kb.py --target user_upload

# 跳过确认
python scripts/migrate_files_to_kb.py --yes
```

---

## 故障排查

### 问题 1：上传文件后无法检索

**症状**：文件上传成功，但聊天时无法检索到内容

**解决**：
1. 检查索引状态：
   ```bash
   python -c "from main import get_dual_vector_store; \
              store = get_dual_vector_store(); \
              print(f'知识库: {store.kb_size}, 用户上传: {store.user_size}')"
   ```
2. 检查处理后的文件：
   ```bash
   ls data/user_uploads/processed/*.chunks.jsonl
   ls data/knowledge_base/processed/*.chunks.jsonl
   ```
3. 重新上传文件

### 问题 2：权限错误（403 Forbidden）

**症状**：技术员上传到知识库时返回 403 错误

**原因**：只有管理员和经理可以上传到知识库

**解决**：
- 技术员应使用 `upload_type=user_upload`
- 或联系管理员上传到知识库

### 问题 3：检索未优先使用用户上传文件

**症状**：用户上传了文件，但聊天时仍返回知识库内容

**原因**：
1. 用户上传文件相似度 < 70%
2. 优先检索被禁用

**解决**：
1. 降低相似度阈值：
   ```python
   # config/settings.py
   user_upload_score_threshold: float = 0.5  # 从 0.7 降到 0.5
   ```
2. 确认优先检索已启用：
   ```python
   enable_priority_search: bool = True
   ```
3. 查看后端日志：
   ```bash
   tail -f backend.log | grep "🎯\|🔍"
   ```

### 问题 4：上传失败

**常见原因**：
- 文件过大（> 50MB）
- 文件格式不支持
- 后端服务未启动
- 磁盘空间不足

**解决**：
1. 检查文件大小：`ls -lh your_file.pdf`
2. 验证文件格式是否在支持列表中
3. 确认后端运行：`curl http://localhost:8000/docs`
4. 检查磁盘空间：`df -h`

### 问题 5：清理数据后恢复

**症状**：误删除数据需要恢复

**解决**：
1. 如果使用了 `--backup`，从备份恢复：
   ```bash
   cp -r data_backup_YYYYMMDD_HHMMSS/* data/
   ```
2. 如果保留了 `data/raw/`，重新索引：
   ```bash
   python scripts/reindex_raw_files.py
   ```
3. 如果完全删除，从原始来源重新上传文件

---

## 最佳实践

### 知识库管理

✅ **推荐**：
- 知识库只存放经过审核的高质量文档
- 定期清理过期或错误的文档
- 使用统一的命名规范
- 分类组织文档

❌ **避免**：
- 将临时文件上传到知识库
- 上传重复内容的文档
- 上传未经审核的内容

### 用户上传文件

✅ **推荐**：
- 用于临时、个性化的文档查询
- 上传与当前对话相关的文件
- 定期清理不再需要的临时文件

❌ **避免**：
- 将长期使用的文档上传到临时目录
- 上传敏感或机密文件

### 重新索引

✅ **推荐**：
- 少量文件：使用重新上传
- 全量更新：使用 `rag_cli.py build --rebuild`
- 生产环境：使用重新上传（避免影响服务）

❌ **避免**：
- 频繁执行完整重建（耗时 7+ 分钟）
- 在高峰期清理数据

---

## 技术细节

### 分块策略

**文本文件分块规则**：
- 按段落（`\n\n`）分割
- 每块最多 1000 字符
- 保持段落完整性
- 自动处理编码问题

**分块示例**：
```
原始文件：
段落1内容（500字符）
段落2内容（800字符）
段落3内容（300字符）

分块结果：
块1: 段落1（500字符）
块2: 段落2（800字符）
块3: 段落3（300字符）
```

### 双向量存储管理器

```python
from src.retrieval.dual_vector_store import DualVectorStoreManager

# 初始化
dual_store = DualVectorStoreManager(
    kb_index_path="data/embeddings/knowledge_base.faiss",
    user_index_path="data/embeddings/user_uploads.faiss",
    dim=384,
    user_upload_score_threshold=0.7,
    enable_priority_search=True,
)

# 添加向量
dual_store.add(vectors, metadatas, store_type="knowledge_base")
dual_store.add(vectors, metadatas, store_type="user_upload")

# 智能检索
results = dual_store.search(query_vector, top_k=5)
```

---

## 相关脚本

- `scripts/clear_rag_data.py` - 清理索引和文件
- `scripts/reindex_raw_files.py` - 批量重新索引
- `scripts/migrate_files_to_kb.py` - 数据迁移
- `scripts/rag_cli.py` - RAG 系统管理 CLI

---

**版本**: v2.0 (2025-10-31)  
**维护**: RAG_Agent 开发团队

