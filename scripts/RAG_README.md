# 学术论文RAG系统构建指南

本指南详细说明如何使用本项目构建专为学术论文设计的RAG（检索增强生成）系统。

## 🎯 系统特点

- **智能分块**: 针对中文学术论文优化的分块策略
- **标准元数据**: 完全符合AGENTS.md规范的元数据结构
- **高效检索**: 基于FAISS的向量相似度搜索
- **批量处理**: 支持PDF、DOCX、TXT等多种格式
- **增量更新**: 支持增量添加新文档
- **可追溯性**: 每个检索结果都包含来源文件和块信息

## 📁 目录结构

```
data/
├── raw/                    # 原始论文文件（PDF、DOCX等）
├── processed/              # 清洗后的文本文件
└── embeddings/             # 向量索引和元数据
    ├── index.faiss         # FAISS向量索引
    └── index.meta.jsonl    # 元数据文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备论文文件

将你的论文文件放入 `data/raw/` 目录：

```bash
# 示例
data/raw/
├── paper1.pdf
├── paper2.pdf
├── paper3.docx
└── paper4.txt
```

### 3. 构建RAG系统

#### 方法一：使用完整构建脚本（推荐）

```bash
# 基本构建
python scripts/build_rag_system.py

# 自定义参数构建
python scripts/build_rag_system.py \
    --input data/raw \
    --output data/embeddings \
    --chunk-size 800 \
    --chunk-overlap 100 \
    --model all-MiniLM-L6-v2

# 重建索引（清空现有数据）
python scripts/build_rag_system.py --rebuild

# 构建后测试查询
python scripts/build_rag_system.py --test-query "机器学习算法"
```

#### 方法二：使用简化脚本

```bash
# 使用修复后的data_ingestion.py
python scripts/data_ingestion.py
```

### 4. 使用RAG系统

#### 基本使用

```python
from scripts.build_rag_system import AcademicRAGBuilder

# 加载RAG系统
builder = AcademicRAGBuilder(
    raw_data_dir="data/raw",
    processed_dir="data/processed",
    embeddings_dir="data/embeddings"
)

# 搜索相关文档
results = builder.search("深度学习", top_k=5)

# 查看结果
for result in results:
    print(f"文件: {result['file']}")
    print(f"相似度: {result['score']:.4f}")
    print(f"内容: {result['preview']}...")
```

#### 交互式搜索

```bash
# 启动交互式搜索
python scripts/example_rag_usage.py --interactive
```

## ⚙️ 配置参数

### 分块参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `chunk_size` | 600 | 分块大小（字符数） |
| `chunk_overlap` | 100 | 分块重叠大小 |
| `min_chunk_size` | 50 | 最小分块大小 |

### 嵌入模型

| 模型 | 维度 | 特点 |
|------|------|------|
| `all-MiniLM-L6-v2` | 384 | 轻量级，速度快 |
| `all-mpnet-base-v2` | 768 | 高质量，速度中等 |
| `moka-ai/m3e-base` | 768 | 中文优化 |

### 支持的文件格式

- PDF (`.pdf`)
- Word文档 (`.docx`, `.doc`)
- 纯文本 (`.txt`)
- Markdown (`.md`)

## 📊 元数据规范

每个文档块包含以下元数据（符合AGENTS.md规范）：

```json
{
    "file": "data/raw/paper1.pdf",      // 源文件路径
    "chunk_id": 0,                      // 块ID
    "hash": "abc123...",                // 内容哈希
    "preview": "这是文档的前50个字符...", // 内容预览
    "score": 0.85,                      // 相似度分数（检索时填充）
    "rank": 1                           // 排名（检索时填充）
}
```

## 🔍 搜索功能

### 基本搜索

```python
# 简单搜索
results = builder.search("机器学习", top_k=5)

# 带元数据的搜索
results = builder.search("深度学习", top_k=3, include_metadata=True)
```

### 高级搜索示例

```python
# 搜索特定文件类型
results = builder.search("算法", top_k=10)
pdf_results = [r for r in results if r['file'].endswith('.pdf')]

# 分析搜索结果
for result in results:
    file_name = Path(result['file']).name
    similarity = result['score']
    content = result['preview']
    print(f"{file_name}: {similarity:.3f} - {content}")
```

## 📈 性能优化

### 1. 分块策略优化

- **小文档**: 使用较小的chunk_size (400-600)
- **大文档**: 使用较大的chunk_size (800-1200)
- **重叠设置**: 10-20%的重叠比例

### 2. 嵌入模型选择

- **速度优先**: `all-MiniLM-L6-v2`
- **质量优先**: `all-mpnet-base-v2`
- **中文优化**: `moka-ai/m3e-base`

### 3. 批量处理

```python
# 批量处理多个文件
files = list(Path("data/raw").glob("*.pdf"))
for file in files:
    builder._process_single_file(file)
```

## 🛠️ 故障排除

### 常见问题

1. **文件加载失败**
   ```
   错误: 处理文件失败 data/raw/paper.pdf: Unsupported file type
   解决: 检查文件格式是否支持，确保文件未损坏
   ```

2. **内存不足**
   ```
   错误: 向量库加载失败
   解决: 减少chunk_size，或使用更小的嵌入模型
   ```

3. **搜索结果为空**
   ```
   问题: 搜索返回空结果
   解决: 检查向量库是否构建成功，尝试更通用的查询词
   ```

### 调试模式

```bash
# 启用详细日志
python scripts/build_rag_system.py --verbose

# 导出元数据进行分析
python scripts/build_rag_system.py --export-metadata
```

## 📚 与LLM集成

### 基本集成示例

```python
def rag_query(question: str, top_k: int = 3):
    """RAG查询函数"""
    # 1. 检索相关文档
    results = builder.search(question, top_k=top_k)
    
    # 2. 构建上下文
    context = ""
    for result in results:
        context += f"来源: {Path(result['file']).name}\n"
        context += f"内容: {result['preview']}...\n\n"
    
    # 3. 构建提示词
    prompt = f"""
    基于以下文档内容回答问题：
    
    {context}
    
    问题: {question}
    
    请基于上述文档内容给出详细回答，并注明信息来源。
    """
    
    return prompt

# 使用示例
question = "什么是深度学习？"
prompt = rag_query(question)
# 将prompt发送给LLM API
```

### 高级集成

```python
def advanced_rag_query(question: str, filters: dict = None):
    """高级RAG查询，支持过滤"""
    # 检索
    results = builder.search(question, top_k=5)
    
    # 应用过滤
    if filters:
        filtered_results = []
        for result in results:
            if filters.get('file_type') and not result['file'].endswith(filters['file_type']):
                continue
            if filters.get('min_score') and result['score'] < filters['min_score']:
                continue
            filtered_results.append(result)
        results = filtered_results
    
    # 重排序（可选）
    results = sorted(results, key=lambda x: x['score'], reverse=True)
    
    return results
```

## 🔄 增量更新

```python
# 添加新文档
new_file = Path("data/raw/new_paper.pdf")
builder._process_single_file(new_file)

# 保存更新
builder.store.save()
```

## 📊 监控和分析

### 系统状态检查

```python
info = builder.get_system_info()
print(f"向量库大小: {info['vector_store_size']}")
print(f"嵌入维度: {info['embedding_dimension']}")
print(f"处理统计: {info['stats']}")
```

### 元数据导出

```python
# 导出完整元数据
export_file = builder.export_metadata("metadata_export.json")
```

## 🎯 最佳实践

1. **文档预处理**: 确保PDF文件质量良好，避免OCR错误
2. **分块策略**: 根据文档类型调整chunk_size
3. **查询优化**: 使用具体、明确的查询词
4. **结果过滤**: 设置合理的相似度阈值
5. **定期更新**: 定期重新构建索引以包含新文档

## 📞 支持

如有问题，请检查：
1. 日志文件：`logs/data_ingestion_*.log`
2. 元数据文件：`data/embeddings/index.meta.jsonl`
3. 系统状态：运行 `python scripts/example_rag_usage.py --demo`
