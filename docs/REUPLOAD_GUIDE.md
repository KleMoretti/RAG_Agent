# PDF重新上传指南 - 无需完整重建

## 方案概述

**优势**：
- ✅ 不需要运行 `rag_cli.py build --rebuild`（避免7分钟等待）
- ✅ 只清理索引数据，保留或删除原始PDF
- ✅ 通过前端上传接口重新上传，自动生成正确索引
- ✅ 可以选择性上传部分文件

**原理**：
- `POST /api/upload` 接口使用 `process_and_index_file()` 函数
- 该函数会正确生成包含 `file_id` 和 `file_name` 的metadata
- 新上传的文件会自动索引到向量库

---

## 操作步骤

### 第1步：预览将要删除的内容

```bash
# 预览模式（不实际删除）
python scripts/clear_rag_data.py --dry-run
```

**输出示例**：
```
[1] 清理向量库索引...
   [DRY RUN] 将删除: index.faiss (12714.0 KB)
   [DRY RUN] 将删除: index.meta.jsonl (2474.0 KB)

[2] 清理processed目录...
   [DRY RUN] 将删除 93 个文件，总计 3500.0 KB

[DRY RUN] 将删除 95 个文件，总计 18688.0 KB (18.2 MB)
```

### 第2步：清理数据

#### 方案A：保留原始PDF（推荐）

```bash
# 只清理向量库和processed目录，保留raw目录的PDF
python scripts/clear_rag_data.py
```

**优点**：
- 原始PDF文件保留在 `data/raw/` 目录
- 可以选择性重新上传部分文件
- 节省重新下载/准备文件的时间

**注意**：清理后，前端上传相同文件名的PDF会覆盖旧文件

#### 方案B：完全清空（适合重新整理）

```bash
# 删除所有数据（包括原始PDF）
python scripts/clear_rag_data.py --all
```

**适用场景**：
- 想要重新整理文档
- 删除不需要的旧文件
- 完全重置系统

#### 可选：先备份再清理

```bash
# 自动备份到 data_backup_YYYYMMDD_HHMMSS 目录
python scripts/clear_rag_data.py --backup
```

### 第3步：启动后端

```bash
python manage.py start backend
```

**验证后端启动成功**：
- 访问 http://localhost:8000/docs 查看API文档
- 检查终端输出是否有错误

### 第4步：重新上传PDF

#### 方法1：通过前端界面上传（推荐）

1. 访问前端：http://localhost:3000
2. 登录系统
3. 进入聊天页面
4. 点击"上传文件"按钮（📎）
5. 选择PDF文件并上传

**上传成功标志**：
- 显示 "文件上传成功，已处理为 N 个块"
- 可以看到文件预览

#### 方法2：通过API批量上传

```bash
# 单个文件上传
curl -X POST http://localhost:8000/api/upload \
  -F "file=@path/to/your.pdf"

# 批量上传脚本（PowerShell）
Get-ChildItem D:\PDFs\*.pdf | ForEach-Object {
    curl.exe -X POST http://localhost:8000/api/upload `
      -F "file=@$($_.FullName)"
    Start-Sleep -Seconds 2  # 避免并发过多
}
```

#### 方法3：从raw目录批量重新索引

如果你使用了**方案A**（保留原始PDF），可以创建批量重新索引脚本：

```python
# scripts/reindex_raw_files.py
import requests
from pathlib import Path

data_dir = Path("data/raw")
pdf_files = list(data_dir.glob("*.pdf"))

print(f"发现 {len(pdf_files)} 个PDF文件")

for i, pdf_file in enumerate(pdf_files, 1):
    print(f"[{i}/{len(pdf_files)}] 上传: {pdf_file.name}")
    
    with open(pdf_file, 'rb') as f:
        files = {'file': (pdf_file.name, f, 'application/pdf')}
        response = requests.post('http://localhost:8000/api/upload', files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ 成功: {result.get('chunks', 0)} 个块")
    else:
        print(f"  ❌ 失败: {response.status_code}")

print("\n完成！")
```

**运行**：
```bash
python scripts/reindex_raw_files.py
```

### 第5步：验证修复成功

#### 检查向量库

```bash
python scripts/diagnose_rag.py
```

**预期输出**：
```
总条目数: 1234
包含file_id字段: 1234 (100%) ✅
包含file_name字段: 1234 (100%) ✅
```

#### 测试查询

```bash
# 使用rag_cli.py测试搜索
python scripts/rag_cli.py search "你的测试查询" --top-k 3
```

#### 前端测试

1. 在聊天界面输入问题："请总结XXX.pdf的主要内容"
2. 检查回答是否包含具体内容（不是通用知识）
3. 查看"检索来源"是否显示正确的文件名和内容

---

## 常见问题

### Q1: 清理后数据能恢复吗？

**A**: 
- **向量库和processed**：无法恢复，但可以通过重新上传PDF重新生成
- **raw原始文件**：如果使用 `--all` 参数删除，则无法恢复。建议使用 `--backup` 备份

### Q2: 我有100个PDF，全部重新上传太麻烦？

**A**: 使用方法3的批量重新索引脚本，自动处理 `data/raw/` 目录下的所有PDF

### Q3: 上传失败怎么办？

**A**: 检查以下几点：
- 后端是否正常运行
- PDF文件是否损坏
- 文件大小是否超过限制
- 查看后端日志 `logs/app.log`

### Q4: 部分旧文件想保留，只重新上传部分文件？

**A**: 
1. 使用 `--dry-run` 查看将要删除的文件
2. 清理前备份 `data/raw/` 目录
3. 清理后只上传需要更新的PDF
4. 旧的有问题的文件会从索引中删除，新文件会正确索引

### Q5: 清理会影响正在运行的系统吗？

**A**: 建议停止后端再清理：
1. 停止后端：`Ctrl+C`
2. 运行清理脚本
3. 重新启动后端

### Q6: 如何确认新上传的PDF有正确的file_id？

**A**: 查看上传响应：
```json
{
  "success": true,
  "message": "文件上传成功，已处理为 22 个块",
  "file_id": "6a3b0602a6faee0892ee0917615a5dc9_终轧温度.pdf",
  "chunks": [...]
}
```

确认 `file_id` 字段存在且包含文件hash和名称。

---

## 脚本参数说明

### clear_rag_data.py 参数

```bash
python scripts/clear_rag_data.py [OPTIONS]
```

| 参数 | 说明 |
|------|------|
| `--dry-run`, `-n` | 预览模式，不实际删除 |
| `--all`, `-a` | 删除所有数据（包括raw） |
| `--backup`, `-b` | 清理前先备份 |
| `--force`, `-f` | 强制执行，不询问确认 |
| `--data-dir PATH` | 指定数据目录（默认：data） |

**示例**：
```bash
# 预览
python scripts/clear_rag_data.py --dry-run

# 清理并备份
python scripts/clear_rag_data.py --backup

# 完全清空（包括raw），强制执行
python scripts/clear_rag_data.py --all --force
```

---

## 对比：重新上传 vs 重建索引

| 特性 | 重新上传 | 重建索引 |
|------|----------|----------|
| **耗时** | 取决于上传速度 | ~7分钟（87个文件） |
| **灵活性** | 可选择性上传 | 处理所有文件 |
| **适用场景** | 部分文件更新 | 完整重建系统 |
| **操作复杂度** | 需要手动/脚本上传 | 一条命令 |
| **结果** | 只索引上传的文件 | 所有raw文件被索引 |

**建议**：
- **少量文件**：使用重新上传
- **全量更新**：使用 `rag_cli.py build --rebuild`
- **生产环境**：使用重新上传，避免影响服务

---

## 相关文件

- `scripts/clear_rag_data.py` - 清理脚本
- `scripts/diagnose_rag.py` - 诊断工具
- `scripts/rag_cli.py` - RAG系统管理CLI
- `main.py` - 上传接口（process_and_index_file函数）

---

## 完整流程示例

```bash
# 1. 预览
python scripts/clear_rag_data.py --dry-run

# 2. 备份并清理（保留raw）
python scripts/clear_rag_data.py --backup

# 3. 启动后端
python manage.py start backend

# 4. 批量重新索引
python scripts/reindex_raw_files.py

# 5. 验证
python scripts/diagnose_rag.py

# 6. 测试搜索
python scripts/rag_cli.py search "测试查询" --top-k 3
```

---

## 注意事项

⚠️ **清理前务必确认**：
- [ ] 已备份重要数据（或使用 `--backup`）
- [ ] 了解哪些数据会被删除
- [ ] 后端已停止运行
- [ ] 有原始PDF文件的来源（如需重新上传）

✅ **清理后检查**：
- [ ] 向量库文件已删除
- [ ] processed目录已清空
- [ ] raw目录状态符合预期（保留或清空）
- [ ] 备份目录存在（如果使用了 `--backup`）

