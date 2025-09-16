# RAG_Agent 开发规范

本文档面向团队内部开发成员，明确项目结构、编码规范、协作流程、RAG 体系设计约定与扩展方式，保证后续功能演进一致性与可维护性。(AI 写的)

---

## 目录
1. 项目定位 & MVP 范围
2. 目录结构与模块职责
3. RAG 数据流与接口契约
4. 环境与依赖管理
5. 编码规范
6. 日志 / 错误 / 异常约定
7. 配置与敏感信息管理
8. 测试策略
9. Git 分支 / 提交 / PR 流程
10. 性能与扩展建议
11. 安全与权限预留
12. 常见坑与排查
13. 下一阶段里程碑（建议）
14. 附录：代码片段示例

---

## 1. 项目定位 & MVP 范围

当前目标：实现一个最小可用的 Retrieval-Augmented Generation 闭环：
1. 文本文件（先支持 `.txt`）→ 清洗、分句、切块
2. 生成向量并写入本地 FAISS
3. 查询：输入自然语言 → 向量检索 Top-K
4. 简单组装上下文 → 调用 LLM（可先 mock / echo）
5. 返回答案 + 来源引用（chunk preview）

超出 MVP（后续迭代再做）：多模态、权限过滤、Rerank、Hybrid 检索、对话记忆、指标监控、评测体系、知识图谱。

---

## 2. 目录结构与模块职责

```
config/                 配置与日志
src/
  agent/                Agent 编排（RAG 主逻辑与推理策略）
  api/                  FastAPI 路由与中间件
  data_processing/      数据加载、清洗、切分、向量化
  retrieval/            向量存储、索引构建、检索
  llm/                  LLM 客户端封装
scripts/                运维 & 批处理脚本（索引、评测）
tests/                  单元与集成测试
notebooks/              试验性探索
```

核心文件（当前或计划实现）：
- `config/settings.py`：集中读取环境变量，提供 `get_settings()`
- `config/logging_config.py`：统一初始化日志
- `src/data_processing/preprocessor.py`：基础清洗与分句
- `src/data_processing/embedder.py`：Embedding 生成（封装 sentence-transformers）
- `src/retrieval/vector_store.py`：FAISS 封装（增、查）
- `src/retrieval/indexer.py`：索引构建流程
- `src/retrieval/searcher.py`：查询封装
- `src/agent/base_agent.py`（将添加）：RAG 核心 orchestrator
- `src/llm/client.py`（将添加）：LLM API 调用抽象

---

## 3. RAG 数据流与接口契约

| 阶段           | 输入          | 输出                          | 说明                                      |
| -------------- | ------------- | ----------------------------- | ----------------------------------------- |
| Ingest Loader  | 原始文件文本  | 原始字符串                    | 现阶段只支持 `.txt`                       |
| Preprocess     | 原始字符串    | 清洗后句子列表                | 去空白、去噪点                            |
| Chunking       | 句子列表      | Chunk 列表                    | 保留顺序，存 preview                      |
| Embedding      | Chunk 列表    | 向量矩阵 (N, D)               | 统一 float32 & 归一化                     |
| Index Upsert   | 向量 + 元数据 | FAISS Index + metadata JSONL  | 元数据含 file / chunk_id / hash / preview |
| Query Embed    | 用户 query    | 向量 (1, D)                   | 同一模型                                  |
| Search         | Query 向量    | Top-K 结果（带 score + meta） | Score 采用 内积/IP                        |
| Answer Compose | Query + Top-K | Prompt 上下文                 | 去重 + 截断                               |
| LLM Call       | Prompt        | 回答文本                      | 控制超时与重试                            |

约定：
- 元数据字段最少包含：`file`, `chunk_id`, `hash`, `preview`, `score`(查询后), `rank`
- Embedding 模型需可热替换，统一通过 `get_embedder()`
- VectorStore 必须保证：添加后立即可查询；写入落盘原子性（后续可引入临时文件 + rename）

---

## 4. 环境与依赖管理

建议 Python 3.10+。  
步骤：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

添加依赖原则：
1. 必须评估是否可被轻量替代（避免库膨胀）
2. 生产强依赖需锁 minor 版本（例：`fastapi==0.111.0`）
3. 模型/向量库升级需回归测试（兼容性）

后续可迁移到 `pyproject.toml` + Poetry（等功能稳定后）。

---

## 5. 编码规范

- 语言：Python 3.10+
- 风格：PEP8 基础 + 类型注解强制
- 每个对外接口/类必须写 docstring（Google 或 NumPy 风格择一统一）
- 禁止在库代码中写 `print`，统一用日志
- 模块导入顺序：
  1. 标准库
  2. 第三方库
  3. 本地模块
- 禁止循环依赖：如需要共享常量 → 建 `src/common/constants.py`
- Public 接口函数名使用动宾结构：`ingest_file`, `search`, `compose_answer`
- 错误不可吞掉：捕获后必须日志 + 抛出自定义异常或返回显式错误对象
- Magic number/字符串需提升为常量
- Token 计数（后续加）：抽象工具层避免散落在业务逻辑

示例：
```python
def search(self, query: str, top_k: int | None = None) -> list[dict]:
    """
    执行向量检索。

    Args:
        query: 用户自然语言查询
        top_k: 返回条数（None 时使用 settings.top_k）

    Returns:
        带分数与元数据的检索结果列表
    """
```

---

## 6. 日志 / 错误 / 异常约定

等级使用约定：
- `DEBUG`: 仅开发调试（可包括向量维度、chunk 数量）
- `INFO`: 关键工作流节点（ingest 开始/结束，search 次数）
- `WARNING`: 可恢复异常（重试、部分文件失败）
- `ERROR`: 单次操作失败
- `CRITICAL`: 服务降级或核心资源不可用（索引加载失败）

`loguru` 用法：
```python
from config.logging_config import setup_logging
logger = setup_logging(get_settings().log_level)
```

异常：
- 建议新增 `src/common/exceptions.py`
- 自定义：`EmbeddingError`, `IndexNotLoadedError`, `EmptyQueryError`

---

## 7. 配置与敏感信息管理

- 所有可变配置进入 `config/settings.py`
- 不在代码中硬编码 API Key
- `.env` 不提交；提供 `.env.example`
- 运行期通过 `Settings` 单例（`lru_cache`）访问

---

## 8. 测试策略

| 类型     | 范围                 | 工具               | 覆盖点              |
| -------- | -------------------- | ------------------ | ------------------- |
| 单元测试 | 纯函数/小类          | pytest             | 预处理、chunk、hash |
| 集成测试 | ingest+search 流程   | pytest-asyncio     | 构建临时 index      |
| 契约测试 | API JSON schema      | fastapi testclient | `/query` 响应结构   |
| 性能冒烟 | 大批文件 ingest 时间 | 脚本               | 指标采集（后续）    |

最小示例（伪）：
```python
def test_chunk_non_empty(tmp_path):
    # 构造一个临时文件 -> ingest -> assert store 有内容
    ...
```

---

## 9. Git 分支 / 提交 / PR 流程

分支模型（简化 Git Flow）：
- `main`: 永远可部署
- `feature/<短描述>`：功能开发
- `fix/<问题标识>`：缺陷修复
- `exp/<实验名>`：不稳定实验（不直接合并 main）

提交规范（推荐 Conventional Commits）：
```
feat: add vector store persistence
fix: correct sentence splitting regex
refactor: extract chunk overlap logic
docs: update ingest pipeline section
test: add searcher top-k test
chore: bump faiss version
```

PR 要求：
- 标题：`[feat] 向量检索器加入 rerank 占位`
- 描述：目的 / 主要改动 / 影响面 / 回归风险 / 后续 TODO
- 必须：通过本地测试 `pytest -q`
- 禁止：在 PR 中同时做结构性变更 + 多个功能合并（超过 400 行 diff 需拆分）

---

## 10. 性能与扩展建议（预埋点）

未来要点：
- 批量嵌入：控制 batch size（显式参数化）
- 检索重构：预留 hybrid（BM25 + 向量）接口，在 `Searcher` 中加策略模式
- Reranker 接口：`def rerank(self, query: str, docs: list[dict]) -> list[dict]`
- 缓存：对重复 query（短期）可以加最近 LRU 缓存
- 并发：索引写入加文件锁（`fcntl` 或临时 rename）

---

## 11. 安全与权限预留

即使 MVP 不做，也请：
- 元数据结构预留 `tenant_id`, `visibility`, `owner`
- 查询时保留过滤参数：`search(query, top_k, filters=None)`
- 日志屏蔽潜在敏感字段（后续脱敏 hook）

---

## 12. 常见坑与排查

| 问题                 | 现象                    | 解决                                         |
| -------------------- | ----------------------- | -------------------------------------------- |
| FAISS 安装失败       | `No module named faiss` | `pip install faiss-cpu`；M 系列注意 `libomp` |
| 模型下载慢           | encode 卡住             | 预先单独安装 `torch`；换镜像源               |
| 索引空结果           | 搜索返回空列表          | 确认是否 ingest 执行；检查 index path        |
| Embedding 维度不匹配 | 添加时报错              | 重建 index：删除旧索引文件                   |
| 导入失败             | `ModuleNotFoundError`   | 确认启动前 `export PYTHONPATH=$(pwd)`        |

---

## 13. 下一阶段里程碑（建议）

| 阶段  | 目标                          | 验收指标                                                |
| ----- | ----------------------------- | ------------------------------------------------------- |
| MVP-1 | ingest + search + mock answer | 本地 query 返回 Top-K preview                           |
| MVP-2 | 接入真实 LLM（或占位 echo）   | 响应含 answer + sources                                 |
| MVP-3 | 添加 FastAPI 三个路由         | `/health` 200，`/ingest` 可触发索引，`/query` 返回 JSON |
| MVP-4 | 简单评测脚本                  | 能输出 recall@k                                         |
| MVP-5 | 权限字段预留 + API 过滤       | `filters={"tenant_id": "x"}` 可生效                     |
| MVP-6 | 文档化 & 自动化测试           | CI 通过；README 有架构图                                |

---

## 14. 附录：代码片段示例

统一获取配置：
```python
from config.settings import get_settings
settings = get_settings()
```

日志：
```python
from config.logging_config import setup_logging
logger = setup_logging(settings.log_level)
logger.info("Index building started")
```

检索：
```python
from src.retrieval.searcher import Searcher
results = Searcher().search("什么是 RAG 系统？")
for r in results:
    print(r["rank"], r["score"], r["preview"])
```

Agent （占位结构设想）：
```python
class RAGAgent:
    def __init__(self, searcher, llm_client, prompt_builder):
        self.searcher = searcher
        self.llm = llm_client
        self.prompt_builder = prompt_builder

    def answer(self, query: str) -> dict:
        docs = self.searcher.search(query)
        prompt = self.prompt_builder.build(query, docs)
        raw = self.llm.generate(prompt)
        return {
            "answer": raw,
            "sources": [{ "file": d["file"], "preview": d["preview"], "score": d["score"] } for d in docs]
        }
```

---

## 结束语

此规范会随着功能推进版本化。提交新模块或引入新技术栈（如 Milvus、Rerank 模型）时，请同步更新本文件相关章节，保持“文档即系统事实”原则。

（如果你读到这里，有改进建议直接在 PR 添加 “docs:update developing spec” 即可。）
