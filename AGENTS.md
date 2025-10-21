# AGENTS.md (Automation Cheatsheet)

## Quick Start

### System Management (Unified CLI)
```bash
# 初始化系统（首次运行）
python manage.py init

# 启动服务
python manage.py start backend       # 启动后端
python manage.py start frontend      # 启动前端  
python manage.py start all           # 同时启动前后端

# 检查状态
python manage.py check               # 检查数据库（Agent、用户、Prompt）
python manage.py check --verbose     # 详细信息
python manage.py status              # 查看系统运行状态
```

### Professional Vocabulary Management (专业词汇管理)
```bash
# 添加钢铁行业默认词汇（首次运行后执行）
python scripts/vocabulary_manager.py add-default

# 从 CSV 文件批量导入词汇
python scripts/vocabulary_manager.py import vocabulary.csv

# 查看词汇统计
python scripts/vocabulary_manager.py stats

# 搜索词汇
python scripts/vocabulary_manager.py search "Q235"

# 导出词汇到 CSV
python scripts/vocabulary_manager.py export output.csv

# 测试查询增强
python scripts/vocabulary_manager.py test-enhance "Q235钢板的抗拉强度是多少？"
```

### RAG System Management (scripts/rag_cli.py)
```bash
# 构建 RAG 索引
python scripts/rag_cli.py build --rebuild

# 搜索文档
python scripts/rag_cli.py search "钢铁生产流程" --top-k 5
python scripts/rag_cli.py search --interactive

# 查看系统信息
python scripts/rag_cli.py info
python scripts/rag_cli.py check      # 检查数据库状态

# 索引迁移（如需手动升级旧索引）
python scripts/migrate_to_fast_index.py --auto
```

### Database Management (scripts/db_migrate.py)
```bash
# 数据库迁移
python scripts/db_migrate.py reset          # 重置数据库
python scripts/db_migrate.py add-presets   # 添加预设问题表
python scripts/db_migrate.py add-prompts   # 添加 Prompt 管理表
python scripts/db_migrate.py status        # 查看数据库状态
```

### Knowledge Graph Management
```bash
# 知识图谱构建（从上传的文档自动提取实体和关系）
python scripts/init_steel_knowledge_graph.py

# 知识图谱查询（通过 Agent 工具）
# Agent 会自动使用 KnowledgeGraphQueryTool 查询知识图谱
# 支持的查询类型：
# - statistics: 获取知识图谱统计信息（实体数量、关系数量等）
# - search: 搜索实体（模糊匹配）
# - properties: 查询实体属性
# - relationships: 查询实体关系
# - similar: 查询相似实体
# - steel_composition: 查询钢种成分

# 知识图谱 API 端点
# GET /api/knowledge-graph/statistics         - 获取统计信息
# POST /api/knowledge-graph/search/entities   - 搜索实体
# GET /api/knowledge-graph/entities/{id}      - 获取实体详情
# POST /api/knowledge-graph/entities/{id}/related - 获取相关实体
```

**知识图谱数据位置**：
- 数据文件：`data/knowledge_graph.json`（~6MB，6669+ 实体）
- 自动加载：Agent 启动时自动加载知识图谱
- 更新方式：重新运行 `init_steel_knowledge_graph.py` 重建知识图谱
- 📚 **详细文档**: 查看 `docs/KNOWLEDGE_GRAPH_GUIDE.md` 了解完整使用说明

**为什么 Agent 返回文字描述而非可视化图谱？**
- Agent 的职责是回答问题（后端），不是渲染 UI（前端）
- 知识图谱可视化需要前端页面（D3.js/Cytoscape.js）
- Agent 通过 `KnowledgeGraphQueryTool` 查询数据，然后生成文字回答
- ✅ 后端已实现：API 接口 + Agent 工具
- ⏳ 待开发：前端可视化页面（`/dashboard/knowledge-graph`）

---

## Professional Vocabulary System (专业词汇系统)

### 功能说明
系统集成了专业词汇识别和查询增强功能，能够自动识别用户查询中的钢铁行业专业术语，并提供更准确的回答。

### 核心特性
1. **自动识别专业词汇**: 在用户查询中自动识别钢种、工艺、设备等专业术语
2. **查询增强 (Query Enhancement)**: 自动添加同义词和相关术语，提高检索准确性
3. **词汇上下文注入**: 将专业词汇的定义和相关信息注入到 Prompt，帮助 Agent 理解专业术语
4. **支持同义词和关联词**: 建立词汇之间的关联关系，提升语义理解

### 工作流程
```
用户查询 "Q235钢板的抗拉强度是多少？"
    ↓
1. 专业词汇识别
   识别到: Q235 (钢种牌号)
    ↓
2. 查询增强
   原始查询: Q235钢板的抗拉强度是多少？
   增强查询: Q235钢板的抗拉强度是多少？ 碳素结构钢 屈服强度
   (添加同义词和相关术语)
    ↓
3. 向量检索
   使用增强后的查询进行 RAG 检索
    ↓
4. 上下文注入
   【专业词汇上下文】
   Q235: 碳素结构钢，屈服强度≥235MPa
   相关术语: 抗拉强度、屈服强度、延伸率
   
   【检索上下文】
   (从知识库检索的文档片段)
    ↓
5. Agent 回答
   基于专业词汇定义 + 检索内容生成专业回答
```

### 数据库表结构
```sql
CREATE TABLE vocabulary (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    term VARCHAR(128) NOT NULL,           -- 术语名称
    definition TEXT NOT NULL,             -- 定义
    category VARCHAR(64) NOT NULL,        -- 分类 (steel_grade, process, equipment, etc.)
    synonyms JSON,                        -- 同义词列表
    related_terms JSON,                   -- 相关术语列表
    created_at DATETIME,
    updated_at DATETIME,
    created_by BIGINT,
    INDEX idx_term_category (term, category)
);
```

### API 端点
- `GET /api/admin/vocabulary` - 获取词汇列表（分页）
- `POST /api/admin/vocabulary` - 创建新词汇
- `PUT /api/admin/vocabulary/{id}` - 更新词汇
- `DELETE /api/admin/vocabulary/{id}` - 删除词汇
- `GET /api/admin/vocabulary/search?q=关键词` - 搜索词汇

### 词汇分类 (Category)
| 分类 | 说明 | 示例 |
|-----|------|-----|
| `steel_grade` | 钢种牌号 | Q235, Q345, 304, 316L |
| `steel_type` | 钢材类型 | 碳素钢、不锈钢、合金钢 |
| `alloy_element` | 合金元素 | 碳、硅、锰、铬、镍 |
| `material_property` | 材料性能 | 抗拉强度、屈服强度、延伸率 |
| `process` | 工艺流程 | 炼钢、热轧、冷轧、退火 |
| `equipment` | 设备名称 | 转炉、热轧机、冷轧机 |
| `application` | 应用领域 | 建筑结构、汽车制造、压力容器 |
| `standard` | 标准规范 | GB/T, ASTM, JIS, DIN |

### 使用示例

#### 1. 添加默认词汇库
```bash
# 添加钢铁行业常用词汇（~500个术语）
python scripts/vocabulary_manager.py add-default

# 输出示例：
# ✅ 成功添加词汇: Q235 (钢种牌号)
# ✅ 成功添加词汇: 转炉 (设备)
# ...
# 📊 总计添加: 478 个专业词汇
```

#### 2. 批量导入词汇
CSV 格式 (`vocabulary.csv`):
```csv
term,definition,category,synonyms,related_terms
Q235,碳素结构钢，屈服强度≥235MPa,steel_grade,"碳素钢,结构钢","Q345,抗拉强度,屈服强度"
转炉,炼钢的主要设备，用于将生铁转化为钢,equipment,炼钢炉,"电炉,炼钢,钢水"
```

导入命令:
```bash
python scripts/vocabulary_manager.py import vocabulary.csv
```

#### 3. 查询增强测试
```bash
python scripts/vocabulary_manager.py test-enhance "Q235钢板的抗拉强度是多少？"

# 输出示例：
# 🔍 原始查询: Q235钢板的抗拉强度是多少？
# 📝 识别到专业词汇: ['Q235', '抗拉强度']
# ✨ 增强查询: Q235钢板的抗拉强度是多少？ 碳素结构钢 屈服强度
# 
# === 专业词汇上下文 ===
# 【Q235】
# 定义: 碳素结构钢，屈服强度≥235MPa
# 分类: steel_grade
# 相关术语: Q345, 抗拉强度, 屈服强度
```

#### 4. 通过 API 管理词汇
```python
import requests

# 创建新词汇
response = requests.post("http://localhost:8000/api/admin/vocabulary", json={
    "term": "Q345",
    "definition": "低合金高强度结构钢，屈服强度≥345MPa",
    "category": "steel_grade",
    "synonyms": ["345钢", "低合金钢"],
    "relatedTerms": ["Q235", "Q420", "屈服强度"]
}, headers={"Authorization": "Bearer <admin_token>"})

# 搜索词汇
response = requests.get("http://localhost:8000/api/admin/vocabulary/search?q=Q235")
print(response.json())
```

### 代码集成示例

#### 在自定义 Agent 中使用专业词汇
```python
from src.vocabulary import VocabularyService, QueryEnhancer
from src.api.db import get_db

# 初始化服务
db = next(get_db())
vocab_service = VocabularyService(db)
vocab_service.initialize()  # 加载词汇到内存

# 创建查询增强器
enhancer = QueryEnhancer(vocab_service)

# 增强查询
query = "Q235钢板的抗拉强度是多少？"
enhanced = enhancer.enhance(query, add_synonyms=True, add_related=True)

print(f"原始查询: {enhanced.original_query}")
print(f"增强查询: {enhanced.enhanced_query}")
print(f"识别词汇: {[t['term'] for t in enhanced.identified_terms]}")
print(f"词汇上下文:\n{enhanced.vocabulary_context}")
```

#### 在文本中识别专业词汇
```python
text = "Q235和Q345是常用的碳素结构钢，广泛应用于建筑结构。"
found_terms = vocab_service.find_terms_in_text(text)

for term_info in found_terms:
    vocab = term_info['vocabulary']
    print(f"识别到: {vocab.term} ({vocab.category})")
    print(f"定义: {vocab.definition}")
    print(f"位置: {term_info['position']}")
```

### 配置选项

在 `main.py` 中配置查询增强行为:
```python
# 获取查询增强器
enhancer = get_query_enhancer()

# 增强选项
enhanced = enhancer.enhance(
    query="Q235钢板强度",
    add_synonyms=True,       # 添加同义词
    add_related=True,        # 添加相关术语
    max_related_terms=5      # 最多添加5个相关术语
)
```

### 性能优化
1. **内存缓存**: 词汇库启动时加载到内存，避免重复查询数据库
2. **索引优化**: 术语和同义词建立索引，快速查找
3. **边界检测**: 避免匹配子串（如避免将"Q2"识别为"Q235"的一部分）
4. **去重机制**: 避免重复识别重叠的术语

### 最佳实践
1. ✅ **定期维护词汇库**: 随着业务发展添加新的专业术语
2. ✅ **建立术语关联**: 为每个术语添加同义词和相关术语
3. ✅ **分类管理**: 按照分类组织词汇，便于管理和检索
4. ✅ **版本控制**: 导出词汇库到 CSV，纳入版本管理
5. ✅ **用户反馈**: 根据用户查询日志发现缺失的专业术语
6. ❌ 避免过度扩展查询（导致检索噪音）
7. ❌ 避免添加过于通用的词汇（如"钢"、"铁"）

### 故障排查

#### 问题：专业词汇未被识别
**解决方案**：
1. 检查词汇是否在数据库中：
   ```bash
   python scripts/vocabulary_manager.py search "Q235"
   ```
2. 检查大小写（词汇识别是大小写不敏感的）
3. 检查术语边界（避免子串匹配问题）
4. 刷新词汇缓存：
   ```python
   vocab_service.refresh_cache()
   ```

#### 问题：查询增强后检索结果变差
**原因**: 添加的相关术语引入噪音

**解决方案**：
1. 减少 `max_related_terms` 参数（默认5，可调整为2-3）
2. 检查相关术语的准确性
3. 暂时禁用相关术语扩展：
   ```python
   enhanced = enhancer.enhance(query, add_synonyms=True, add_related=False)
   ```

#### 问题：词汇加载慢
**解决方案**：
1. 词汇库使用单例模式（`@lru_cache`），只加载一次
2. 如果词汇量过大（>10000），考虑分类加载
3. 检查数据库索引是否正常

---

## Development Standards

1. Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (Python 3.10+)
2. Start: `python manage.py start all` or `python manage.py start backend` (FastAPI on port 8000)
3. Tests: all `pytest -q`; single file `pytest tests/integration.py`; single test `pytest tests/integration.py::test_name`; keyword `pytest -k search`.
4. Async: use `pytest-asyncio`; mark coroutines with `@pytest.mark.asyncio`.
5. Imports order: stdlib, third-party, local (no wildcards); blank line between groups.
6. Types: annotate all public functions; prefer `list[str]` / `str | None`; no implicit Any.
7. Docstrings: Google style (Args, Returns, Raises) for public APIs; brief summary line first.
8. Naming: modules snake_case; classes PascalCase; functions/vars snake_case; constants UPPER_SNAKE; internal helpers `_prefixed`.
9. Errors: never silent; log then raise domain or ValueError; no bare `except`; preserve context (`raise ... from e`).
10. Logging: use `config.logging_config.setup_logging`; levels => INFO workflow, DEBUG internals, WARNING recoverable, ERROR failjsonure, CRITICAL outage; no `print` in src.
11. Data/paths: use `pathlib.Path`; directories created lazily in `get_settings()`.
12. Vector/RAG metadata keys: `file, chunk_id, hash, preview, score, rank`; keep embeddings float32; batch for performance.
13. **Vector Store**: 已升级为 `VectorStoreFast` 自动优化版本（<10k向量用Flat精确检索，≥10k自动升级IVF+PQ近似检索，5-10倍加速）
14. Tool/Agent: extend `Tool`, register via `BaseAgent.add_tool`; duplicate names raise ValueError; reasoning path via `ReasoningEngine`.
15. Formatting: recommend `ruff format` or `black`; line length ≤ 100; strip unused imports (ruff).
16. Lint (optional): `ruff check .`; type check (if added) `mypy src tests`.
17. Commits: Conventional (`feat:`, `fix:`, `refactor:`); PR must pass `pytest -q`; keep diffs focused.
18. Config: only through `get_settings()`; no hardcoded secrets; `.env` ignored; add `.env.example` when new vars.
19. Performance: batch embeddings; avoid redundant FAISS loads; consider caching frequent queries.
20. Security: validate user input before search/LLM; never log secrets; plan filters (`tenant_id`, `visibility`).
21. **RAG Timeout & Fallback**: RAG检索+LLM调用有25秒超时（可配置`RAG_TIMEOUT_SECONDS`），超时自动降级为直接使用LLM（不带RAG上下文），确保用户始终能获得响应。前端总超时60秒。
22. **Documentation Management**: 
    - ✅ ONLY update AGENTS.md for project documentation, standards, and guides
    - ❌ NEVER create new documentation files (README.md, GUIDE.md, STANDARDS.md, FIX.md, etc.)
    - ❌ NEVER create temporary markdown files for fixes or features
    - ✅ Add sections to AGENTS.md instead: append to existing sections or create new ones
    - ✅ Keep AGENTS.md as single source of truth for all project information

---

## AI-Assisted Development Standards

### Project Initialization & Scaffolding
1. **Use Official CLI Tools**: Always use framework-specific CLI for project setup
   - ✅ `npx create-next-app@latest` for Next.js projects
   - ✅ `npm create vite@latest` for Vite projects
   - ✅ `npx create-react-app` for CRA projects
   - ❌ Never manually create boilerplate files when CLI exists
   - **Rationale**: CLI ensures correct configuration, dependencies, and structure

2. **Scaffold with Templates**: Leverage official templates when available
   - ✅ `create-next-app --typescript --tailwind --app`
   - ✅ `create-vite --template react-ts`
   - **Benefit**: Reduces initial setup errors, follows best practices

### Code Organization & Reusability

3. **DRY Principle (Don't Repeat Yourself)**
   - ✅ Extract repeated UI patterns into reusable components
   - ✅ Create custom hooks for shared logic
   - ✅ Use utility functions for common operations
   - ❌ Never copy-paste code blocks more than twice
   - **Rule**: If code appears 3+ times, refactor into shared module

4. **Component Composition**
   ```tsx
   // ✅ Good: Composable, reusable
   <Button variant="primary" size="lg" icon={<SaveIcon />}>
     Save Changes
   </Button>

   // ❌ Bad: Non-reusable, hardcoded
   <button className="bg-blue-500 text-white px-4 py-2">
     Save Changes
   </button>
   ```

5. **Atomic Design Hierarchy**
   - `components/ui/` - Atoms (Button, Input, Card)
     - **For shadcn/ui projects**: Use MCP tools to discover and install UI components
     - **MCP Query First**: Before creating custom components, search shadcn registry
   - `components/shared/` - Molecules (SearchBar, UserAvatar)
   - `components/layout/` - Organisms (Header, Sidebar)
   - `app/*/` - Templates & Pages

5a. **shadcn/ui Component Discovery Workflow**
   ```typescript
   // ❌ Don't manually create components that may exist in shadcn/ui
   // ✅ Do: Query MCP tools first
   
   // Step 1: Search for components
   // Use: mcp_shadcn_search_items_in_registries({ query: "button" })
   
   // Step 2: View component details and source
   // Use: mcp_shadcn_view_items_in_registries({ items: ["@shadcn/button"] })
   
   // Step 3: Check usage examples
   // Use: mcp_shadcn_get_item_examples_from_registries({ query: "button demo" })
   
   // Step 4: Get install command
   // Use: mcp_shadcn_get_add_command_for_items({ items: ["@shadcn/button"] })
   ```

### TypeScript Best Practices

6. **Type Safety First**
   - ✅ Define interfaces/types for all data structures
   - ✅ Use strict mode in `tsconfig.json`
   - ✅ Avoid `any` - use `unknown` or generics instead
   - ❌ Never disable TypeScript errors with `@ts-ignore` (use `@ts-expect-error` with explanation)

7. **Shared Type Definitions**
   ```typescript
   // lib/types/api.ts - Centralized API types
   export interface User {
     id: string;
     username: string;
     role: UserRole;
   }

   // ✅ Import from single source of truth
   import type { User } from '@/lib/types/api';
   ```

### State Management

8. **Collocate State Close to Usage**
   - ✅ Use local state (`useState`) when possible
   - ✅ Lift to context/store only when shared across 3+ components
   - ❌ Don't put everything in global store

9. **Zustand Store Organization**
   ```typescript
   // ✅ Good: Sliced stores by domain
   store/
   ├── authStore.ts      // Authentication state
   ├── chatStore.ts      // Chat messages & sessions
   └── uiStore.ts        // UI preferences

   // ❌ Bad: Monolithic store
   store/index.ts        // Everything in one file
   ```

### API & Data Fetching

10. **Centralized API Clients**
    ```typescript
    // ✅ Good: Single Axios instance with interceptors
    // lib/api/client.ts
    const apiClient = axios.create({ baseURL: API_URL });
    apiClient.interceptors.request.use(addAuthToken);

    // ❌ Bad: Scattered fetch calls throughout components
    ```

11. **Use TanStack Query for Server State**
    - ✅ Leverage caching, refetching, and invalidation
    - ✅ Separate server state from client state
    - ❌ Don't store API responses in Zustand/Redux

### Styling & UI

12. **Consistent Styling Approach**
    - ✅ Use **shadcn/ui** components as primary UI library
    - ✅ Built on Radix UI primitives with Tailwind CSS
    - ✅ CSS variables for theming (defined in `globals.css`)
    - ✅ OKLCH color space for better color perception
    - ❌ Avoid inline styles except for dynamic values
    - **⚡ shadcn/ui Workflow**:
      1. Search components using `mcp_shadcn_search_items_in_registries`
      2. View component details with `mcp_shadcn_view_items_in_registries`
      3. Check usage examples via `mcp_shadcn_get_item_examples_from_registries`
      4. Get install command from `mcp_shadcn_get_add_command_for_items`
      5. Never manually copy component code - always use MCP tools first

13. **Design System & Theming**
    - ✅ All colors defined as CSS variables in `app/globals.css`
    - ✅ Use semantic color tokens: `--primary`, `--secondary`, `--destructive`, `--muted`, etc.
    - ✅ Automatic dark/light mode support via CSS variables
    - ✅ Never use hardcoded color values or Tailwind color classes (e.g., `slate-500`)
    - ✅ Always reference colors via `var(--*)` or semantic Tailwind classes (e.g., `bg-primary`)
    - ❌ Don't define custom color values - extend existing CSS variables if needed

### Performance Optimization

14. **Code Splitting**
    - ✅ Use `React.lazy()` and `Suspense` for route-based splitting
    - ✅ Dynamic imports for heavy components (charts, editors)
    - ✅ Next.js `dynamic()` for SSR-safe lazy loading

15. **Image Optimization**
    - ✅ Always use Next.js `<Image>` component
    - ✅ Specify width/height to prevent layout shift
    - ✅ Use `priority` for above-the-fold images

16. **Memoization**
    ```tsx
    // ✅ Good: Memoize expensive computations
    const processedData = useMemo(() => 
      heavyCalculation(rawData), [rawData]
    );

    // ✅ Good: Prevent unnecessary re-renders
    const MemoizedChart = memo(ExpensiveChart);
    ```

### Error Handling

17. **Graceful Error Boundaries**
    ```tsx
    // ✅ Implement error boundaries for route segments
    // app/error.tsx (Next.js App Router)
    export default function Error({ error, reset }) {
      return <ErrorFallback error={error} onReset={reset} />;
    }
    ```

18. **User-Friendly Error Messages**
    - ✅ Show actionable error messages with recovery options
    - ✅ Log technical details, display simple messages to users
    - ❌ Never expose stack traces or API errors directly

### Testing Strategy

19. **Test Pyramid**
    - Unit Tests: Pure functions, utilities (70%)
    - Integration Tests: API clients, stores (20%)
    - E2E Tests: Critical user flows (10%)

20. **Test File Colocation**
    ```
    components/
    ├── Button/
    │   ├── Button.tsx
    │   ├── Button.test.tsx    ✅ Colocated
    │   └── Button.stories.tsx ✅ Storybook
    ```

### Security Best Practices

21. **Authentication & Authorization**
    - ✅ Store JWT in httpOnly cookies (not localStorage)
    - ✅ Implement CSRF protection for mutations
    - ✅ Validate permissions on both frontend and backend

22. **Input Validation**
    - ✅ Use Zod for schema validation
    - ✅ Sanitize user input before rendering
    - ✅ Validate file uploads (type, size, content)

### Documentation

23. **Self-Documenting Code**
    ```typescript
    // ✅ Good: Clear naming, JSDoc for complex logic
    /**
     * Calculates steel production cost based on raw material prices
     * @param materials - Raw material quantities and prices
     * @param energyCost - Current energy cost per kWh
     * @returns Total production cost in USD
     */
    function calculateProductionCost(
      materials: MaterialCost[],
      energyCost: number
    ): number {
      // Implementation...
    }
    ```

24. **Component Documentation**
    - ✅ Add prop descriptions for complex components
    - ✅ Include usage examples in Storybook or comments
    - ✅ Document edge cases and limitations

### Git & Version Control

25. **Conventional Commits**
    ```bash
    # ✅ Good commit messages
    feat(chat): add streaming AI response support
    fix(upload): resolve file size validation error
    refactor(api): extract auth logic to middleware
    docs(readme): update installation instructions

    # ❌ Bad commit messages
    "fix bug"
    "update"
    "wip"
    ```

26. **Atomic Commits**
    - ✅ One logical change per commit
    - ✅ All tests pass before committing
    - ❌ Don't commit commented-out code or console.logs

### AI Collaboration Guidelines

27. **Provide Context to AI**
    - ✅ Share relevant files, error messages, and goals
    - ✅ Specify framework versions and environment
    - ✅ Describe expected behavior vs actual behavior

28. **Review AI-Generated Code**
    - ✅ Always review suggested code before applying
    - ✅ Test AI-generated functions with edge cases
    - ✅ Verify security implications (especially auth/validation)
    - ❌ Never blindly accept code that you don't understand

29. **Iterative Refinement**
    - ✅ Start with high-level architecture questions
    - ✅ Drill down into specific implementation details
    - ✅ Request alternatives when unsure about approach

30. **Development Server Management**
    - ❌ 不要主动运行开发服务器或打开预览界面
    - ✅ Only start servers when explicitly requested by user
    - ✅ Confirm before launching any long-running processes

### Accessibility (a11y)

31. **WCAG Compliance**
    - ✅ Use semantic HTML (`<button>`, `<nav>`, `<main>`)
    - ✅ Provide alt text for images
    - ✅ Ensure keyboard navigation works
    - ✅ Maintain color contrast ratios (WCAG AA: 4.5:1)

32. **ARIA Labels**
    ```tsx
    // ✅ Good: Accessible button
    <button aria-label="Close dialog" onClick={onClose}>
      <X />
    </button>

    // ❌ Bad: Icon-only button without label
    <button onClick={onClose}>
      <X />
    </button>
    ```

### Environment Configuration

33. **Environment Variables**
    - ✅ Use `.env.local` for secrets (gitignored)
    - ✅ Provide `.env.example` with dummy values
    - ✅ Prefix public vars with `NEXT_PUBLIC_`
    - ❌ Never commit real API keys or credentials

34. **Type-Safe Environment**
    ```typescript
    // lib/env.ts
    import { z } from 'zod';

    const envSchema = z.object({
      NEXT_PUBLIC_API_URL: z.string().url(),
      DATABASE_URL: z.string(),
    });

    export const env = envSchema.parse(process.env);
    ```

### Deployment & CI/CD

35. **Pre-deployment Checks**
    ```json
    // package.json scripts
    {
      "scripts": {
        "build": "next build",
        "lint": "eslint . --ext .ts,.tsx",
        "type-check": "tsc --noEmit",
        "test": "jest",
        "precommit": "lint-staged",
        "prebuild": "npm run lint && npm run type-check"
      }
    }
    ```

36. **Continuous Integration**
    - ✅ Run tests on every PR
    - ✅ Enforce code coverage thresholds
    - ✅ Block merge if build fails



## Frontend Architecture Design (Steel Industry AI Decision Hub)

### Product Positioning
- **Domain**: Vertical AI decision hub for steel industry
- **Target Users**: Technicians, production managers, procurement staff, environmental experts
- **Core Value**: From "information retrieval" to "decision support"

### Tech Stack

#### Core Framework
- **Next.js 14+** (App Router) - React full-stack framework with SSR/SSG support
- **TypeScript** - Type safety
- **React 18+** - UI component foundation

#### UI Component Library
- **shadcn/ui** - Modern headless UI component library
  - Built on Radix UI primitives with full accessibility support
  - Customizable components (copy to your project, you own the code)
  - Tailwind CSS integration with CSS variables theming
  - OKLCH color space for better color perception
  - Automatic dark/light mode support
  - **🔧 MCP Tool Integration**: Use MCP shadcn tools for component management
    - `mcp_shadcn_list_items_in_registries` - List all available components
    - `mcp_shadcn_search_items_in_registries` - Search for specific components
    - `mcp_shadcn_view_items_in_registries` - View component source code
    - `mcp_shadcn_get_item_examples_from_registries` - Get usage examples
    - `mcp_shadcn_get_add_command_for_items` - Get CLI command to add components
  - **Best Practice**: Always query MCP tools before manually adding components

#### State Management
- **Zustand** - Lightweight state management
- **TanStack Query (React Query)** - Server state management and caching

#### Data Visualization
- **Apache ECharts** - Industry data charts (price trends, equipment monitoring)
- **D3.js** - Process flowcharts and knowledge graph visualization
- **Cytoscape.js** - Knowledge graph network display

#### Real-time Communication
- **Server-Sent Events (SSE)** - Streaming AI responses
- **Socket.io Client** (optional) - WebSocket real-time chat

#### Utility Libraries
- **Axios** - HTTP request wrapper
- **React Hook Form + Zod** - Form management and validation
- **date-fns** - Date manipulation
- **react-markdown** - Markdown rendering (AI responses)
- **framer-motion** - Animation effects

#### Internationalization (i18n)
- **Default Language**: Chinese (zh-CN) - Primary language for steel industry users in China
- **Secondary Language**: English (en-US) - For international collaboration and documentation
- **i18n Implementation**: Custom translation hook (`useTranslation`) with locale files
- **Language Switching**: Stored in `uiStore.language` state, persisted in localStorage
- **Translation Scope**:
  - UI labels, buttons, navigation
  - Form validation messages
  - System notifications and alerts
  - AI response interface labels
  - Technical terminology (bilingual support for steel industry terms)
- **Content Strategy**:
  - User-uploaded documents: Support both Chinese and English analysis
  - AI responses: Match user's selected language preference
  - Knowledge base: Multilingual document indexing with language detection
- **Translation Management**:
  ```typescript
  // lib/i18n/locales/zh-CN.ts
  export const zhCN = {
    common: { login: '登录', logout: '退出', submit: '提交', cancel: '取消' },
    auth: { username: '用户名', password: '密码', loginTitle: '钢铁行业 AI 决策中心' },
  };
  // lib/i18n/locales/en-US.ts
  export const enUS = {
    common: { login: 'Login', logout: 'Logout', submit: 'Submit', cancel: 'Cancel' },
    auth: { username: 'Username', password: 'Password', loginTitle: 'Steel Industry AI Hub' },
  };
  ```
- **Best Practices**:
  - ✅ All user-facing text must be translatable (no hardcoded strings)
  - ✅ Use semantic keys: `auth.loginButton` not `button1`
  - ✅ Support Chinese technical terminology with English equivalents
  - ✅ Date/number formatting according to locale (date-fns with locale)
  - ❌ Never mix languages in the same UI component

### Directory Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Authentication page group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/       # Main app page group (requires auth)
│   │   │   ├── layout.tsx     # Dashboard layout
│   │   │   ├── page.tsx       # Home/Overview
│   │   │   ├── chat/          # Intelligent Q&A
│   │   │   ├── equipment/     # Equipment management
│   │   │   ├── market/        # Market analysis
│   │   │   ├── knowledge/     # Knowledge base management
│   │   │   ├── workflow/      # Process workflow
│   │   │   └── admin/         # Admin panel
│   │   ├── api/               # API routes (optional, Next.js middleware)
│   │   ├── layout.tsx         # Global layout
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── ui/                # Base UI components (buttons, cards, etc.)
│   │   ├── layout/            # Layout components (Header, Sidebar, etc.)
│   │   ├── chat/              # Chat-related components
│   │   ├── equipment/         # Equipment-related components
│   │   ├── market/            # Market analysis components
│   │   ├── knowledge/         # Knowledge graph components
│   │   └── shared/            # Shared components
│   ├── lib/                   # Utility library
│   │   ├── api/               # API client wrappers
│   │   │   ├── client.ts      # Axios instance
│   │   │   ├── auth.ts        # Authentication API
│   │   │   ├── chat.ts        # Chat API
│   │   │   ├── upload.ts      # File upload API
│   │   │   └── admin.ts       # Admin API
│   │   ├── hooks/             # Custom hooks
│   │   ├── utils/             # Utility functions
│   │   ├── constants/         # Constants
│   │   └── types/             # TypeScript type definitions
│   ├── store/                 # Zustand state management
│   │   ├── authStore.ts       # Authentication state
│   │   ├── chatStore.ts       # Chat state
│   │   └── uiStore.ts         # UI state
│   ├── styles/                # Style files
│   │   └── globals.css
│   └── middleware.ts          # Next.js middleware (auth guard)
├── public/                    # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
└── tailwind.config.ts
```

### Core Feature Modules

> **Note**: Features support both **production mode** (with real data integration) and **demo mode** (with simulated/sample data for testing).

#### 1. Role-based Permission System
- **Role Definitions**: ADMIN, PRODUCTION, MANAGER, PURCHASER, ENV_EXPERT, TECHNICIAN
- **Permission Control**: canUpload, canChat, canViewMarket, canManageEquipment, canAccessAdmin
- **Role-specific Prompts**: Customized AI conversation presets for each role
- 🆕 **Smart Role Switching**: AI automatically adjusts response depth and terminology based on detected user expertise
- 🆕 **Collaboration Mode**: Multi-role team chat rooms for cross-functional decision-making
- 🆕 **Conversation Context Sharing**: Share chat sessions with annotations between team members

#### 2. Steel Process Intelligent Q&A
- 💬 Streaming AI responses (typewriter effect)
- 📎 File upload as context (PDF, DOCX, images of equipment/diagrams)
- 🔍 Display retrieved document snippets with source attribution
- 🧠 Visualize reasoning steps (show Agent's thought process)
- 🏷️ Role-based preset prompts
- 📌 Conversation history management
- 🆕 **Multi-modal Input**: Support image upload (equipment photos, process diagrams) for visual Q&A
- 🆕 **Smart Follow-up Questions**: AI proactively suggests 3-5 related questions based on context
- 🆕 **Answer Confidence Score**: Display retrieval relevance score and reasoning confidence
- 🆕 **Comparative Analysis**: "Compare A vs B" - Agent analyzes multiple solutions side-by-side
- 🆕 **Solution Templates**: AI generates actionable checklists/step-by-step guides from knowledge base
- 🆕 **Citation Tracking**: Trace every claim back to source documents with snippets
- 🆕 **Question Refinement**: Agent helps rephrase vague questions for better results

#### 3. Intelligent Equipment Maintenance Assistant
- 📋 Equipment knowledge base (manuals, fault logs, maintenance guides)
- 🔧 Conversational fault diagnosis based on symptoms
- 📖 Retrieve relevant troubleshooting procedures from documents
- 💡 Multi-step reasoning for complex equipment issues
- 🆕 **Symptom-to-Solution Mapping**: Agent asks clarifying questions to narrow down fault causes
- 🆕 **Maintenance Procedure Generator**: Auto-generate step-by-step repair guides from manuals
- 🆕 **Historical Case Retrieval**: "Similar issues in the past" based on RAG search
- 🆕 **Safety Protocol Advisor**: Auto-extract and highlight safety warnings from manuals
- 🆕 **Parts Cross-reference**: Agent helps find alternative part numbers across different suppliers
- 🆕 **Diagnostic Decision Tree**: Interactive fault diagnosis with yes/no questions

#### 4. Market Intelligence & Analysis Assistant
- 📰 Industry news and report aggregation (uploaded documents)
- 📊 Document-based trend analysis (AI summarizes price reports, market analyses)
- 🤖 AI-powered insight extraction from market reports
- 🆕 **Multi-document Synthesis**: Agent combines insights from multiple reports into unified analysis
- 🆕 **Trend Narrative Generation**: AI writes executive summaries from raw data/reports
- 🆕 **Competitive Intelligence Extraction**: Auto-extract competitor info from news/reports
- 🆕 **Custom Alert Builder**: Define keywords/topics, Agent monitors new uploads and notifies
- 🆕 **What-If Scenario Analysis**: "What if iron ore price increases 20%?" - Agent reasons through implications
- 🆕 **Report Comparison Tool**: Side-by-side comparison of different analyst reports with discrepancy highlights

#### 5. Knowledge Base Management
- 📁 File upload and management (PDF, DOCX, TXT, Markdown, code files)
- 🔍 Full-text semantic search across all documents
- 🕸️ Knowledge graph visualization (entity extraction and relationship mapping)
- 📝 Document preview and metadata editing
- 🏷️ AI-powered auto-tagging and categorization
- 🆕 **Auto-tagging & Categorization**: AI automatically tags documents by content (equipment type, process stage, etc.)
- 🆕 **Version Control**: Track document uploads with diff visualization for text files
- 🆕 **Smart Recommendations**: "Documents similar to this" based on embedding similarity
- 🆕 **Knowledge Gap Detection**: AI identifies missing documentation based on frequent unanswered queries
- 🆕 **Multi-language Support**: Auto-translate document snippets between Chinese/English during retrieval
- 🆕 **Collaborative Annotation**: Team members can highlight and comment on documents
- 🆕 **Document Quality Score**: Rate document usefulness based on retrieval frequency and user feedback
- 🆕 **Intelligent Chunking Preview**: Show how documents are split into chunks with overlap visualization
- 🆕 **Entity Extraction Dashboard**: Auto-extract equipment names, process parameters, standards from documents

#### 6. Process Workflow & Quality Intelligence

**📊 Production Mode (with real data)**:
- 🏭 **Real-time Process Monitoring**: Live data overlay on flowchart (temperature, pressure, flow rates)
- 📊 **Quality Prediction Dashboard**: Predict product quality based on current process parameters
- ⚡ **Bottleneck Detection**: AI identifies process bottlenecks from production data
- 📈 **Parameter Optimization**: ML suggests optimal parameter ranges for quality/efficiency
- 🎯 **Yield Analysis**: Track and analyze production yield with defect categorization
- 🔔 **Process Deviation Alerts**: Real-time alerts when parameters drift from optimal ranges

**🎭 Demo Mode (without real data)**:
- 📋 Process SOP document repository
- 🔄 **Static Flowchart**: Interactive steel production flowchart with knowledge linking
- 📊 **Sample Process Data**: Historical process runs for case study analysis
- 🎲 **Simulated Scenarios**: Pre-configured parameter sets showing good/bad outcomes

**🤖 Agent Capabilities (both modes)**:
- 🎯 Parameter reasoning: "Why does temperature affect quality?" - Agent explains from knowledge base and data
- 🆕 **SOP Query Interface**: Natural language queries like "How to handle furnace overheating?"
- 🆕 **Process Parameter Explainer**: Agent explains correlations between parameters using documents + data patterns
- 🆕 **Best Practice Extraction**: AI extracts best practices from successful production runs in knowledge base
- 🆕 **Workflow Comparison**: Compare different process variants documented in knowledge base
- 🆕 **Root Cause Analysis Assistant**: Guide users through 5-Whys analysis with knowledge base + data support
- 🆕 **Standard Compliance Checker**: Agent cross-references processes with uploaded regulatory documents
- 🆕 **Automated SOP Summarization**: Generate concise summaries of lengthy procedures
- 🆕 **Quality Issue Diagnosis**: Agent analyzes quality problems by correlating parameters with defect patterns
- 🆕 **Energy Efficiency Advisor**: Identify energy-intensive stages and suggest optimizations

#### 7. Admin Panel
- 👥 User management (CRUD)
- 🔐 Permission configuration
- 📊 System usage statistics (chat volume, upload frequency, top queries)
- 🗂️ Data management (vector store, document library)
- ⚙️ Model configuration (embedding model, LLM settings)
- 🆕 **Query Analytics Dashboard**: Track most common questions, failed queries, response quality
- 🆕 **Document Performance Metrics**: Which documents are most/least retrieved
- 🆕 **RAG Performance Monitor**: Track retrieval accuracy, average response time, token usage
- 🆕 **Prompt Template Manager**: Create and test different system prompts for each role
- 🆕 **A/B Testing Framework**: Test different retrieval strategies or prompt variations
- 🆕 **Feedback Loop**: Collect user ratings on AI responses (👍👎) to improve prompts
- 🆕 **Knowledge Base Health Check**: Identify outdated documents, low-quality chunks, orphaned files
- 🆕 **Semantic Search Debugger**: Visualize embedding similarity scores for troubleshooting

### Backend Integration Design

#### API Client
- Axios instance configuration
- Automatic JWT token injection
- Unified error handling
- Request/response interceptors

#### Key API Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/chat` - Send chat message
- `POST /api/upload` - File upload (multipart/form-data, field: `file`, max 50MB)
  - Supported formats: PDF, DOC, DOCX, TXT, MD, CSV, JSON, XML
  - Auto-indexes into vector store after upload
  - Returns: `{success, message, fileId, fileName, fileSize, contentType, chunks}`
- `GET /api/admin/users` - Get user list
- `PUT /api/admin/users/:id` - Update user
- `GET /api/admin/files` - Get file list (with pagination & search)
- `DELETE /api/admin/files/{file_name}` - Delete single file
- `POST /api/admin/files/batch-delete` - Batch delete files (body: `{"fileNames": ["file1.pdf", "file2.txt"]}`)

#### Streaming Response Handling
- Receive AI streaming output via SSE or WebSocket
- Typewriter effect display
- Support interruption of generation

#### RAG Timeout & Fallback Strategy
**问题**: RAG检索或LLM调用可能因网络、模型响应慢等原因导致超时（30秒前端超时）

**解决方案**: 智能降级机制
- ⏱️ **后端超时**: 25秒（可通过`RAG_TIMEOUT_SECONDS`配置）
- 🔄 **降级策略**: 超时时自动跳过RAG检索，直接使用原生LLM回答
- 📊 **前端超时**: 60秒（给降级LLM留35秒余量）
- 🏷️ **降级标志**: 响应中包含`fallback_mode: true`，前端可显示提示

**配置方法**:
```bash
# .env文件
RAG_TIMEOUT_SECONDS=25  # 默认25秒
```

**工作流程**:
1. 用户发送消息 → 后端开始RAG检索
2. 如果25秒内完成 → 返回带上下文的答案（`fallback_mode: false`）
3. 如果超过25秒 → 自动降级，跳过RAG，直接用LLM（`fallback_mode: true`）
4. 前端收到响应后，如果`fallback_mode: true`可显示："⚠️ 检索超时，已使用通用模式回答"

**优势**:
- ✅ 确保用户始终能获得响应（不会因为RAG慢导致完全失败）
- ✅ 降级后仍有LLM的推理能力（只是缺少知识库上下文）
- ✅ 透明化：前端可知道是否使用了降级模式

### UI/UX Design

#### Design Style
- **Theme System**: 
  - Dark/light mode toggle via CSS variables
  - OKLCH color space for consistent colors across themes
  - Semantic color tokens: `primary`, `secondary`, `destructive`, `muted`, `accent`
  - All colors defined in `app/globals.css` using CSS variables
- **Color Usage**:
  - ✅ Always use semantic tokens: `bg-primary`, `text-muted-foreground`, etc.
  - ✅ Use `var(--primary)` when direct CSS variable access is needed
  - ❌ Never hardcode color values or use Tailwind color classes like `blue-500`

#### Responsive Layout
- Desktop (≥1280px): Three-column layout
- Tablet (768-1279px): Two-column layout
- Mobile (<768px): Single column + bottom navigation

#### Key Interactions
- Skeleton screen loading
- Toast notifications
- Keyboard shortcuts (Ctrl+K for search)
- First-time user onboarding

### Performance Optimization
1. Code splitting (Next.js dynamic imports)
2. Image optimization (Next.js Image component)
3. TanStack Query caching
4. Virtual scrolling (react-window)
5. Debouncing/throttling

### Development Roadmap
- **Phase 1**: Foundation setup (auth, layout)
- **Phase 2**: Core features (Q&A, knowledge base)
- **Phase 3**: Data visualization (market analysis, workflows)
- **Phase 4**: Optimization and testing

### Data Integration Architecture

#### Production Data Connectors (Optional)
```typescript
// lib/connectors/productionData.ts
interface DataConnector {
  type: 'equipment' | 'market' | 'process';
  isConnected: boolean;
  fetchRealTimeData: () => Promise<any>;
  fallbackToDemo: () => DemoData;
}
```

**Supported Data Sources**:
1. **Equipment Sensors**: OPC UA, MQTT, Modbus protocols
2. **Market Data APIs**: Bloomberg, Refinitiv, custom feeds
3. **MES/ERP Systems**: SAP, Oracle, custom databases via REST API
4. **Quality Systems**: LIMS, QMS data exports

**Demo Mode Features**:
- 🎬 **Scenario Library**: Pre-loaded realistic scenarios for each feature
- 📊 **Sample Datasets**: Historical data (anonymized) for visualization
- 🔄 **Data Generator**: Synthetic data generator for continuous simulation
- 🎭 **Interactive Playback**: Step through historical events in demo mode

### Competitive Advantages
1. **Dual-mode Operation**: Seamlessly works with or without production data integration
2. **Industry-specific depth**: Dedicated steel domain embedding model, 30% improvement in technical terminology understanding
3. **Role-based agents**: Customized prompts and permissions for different roles
4. **Knowledge graph**: Process parameter correlation reasoning
5. **Real-time + Historical**: Combines live data analysis with document-based knowledge
6. **Graceful Degradation**: Full functionality in demo mode for testing and training
7. **Incremental Deployment**: Start with documents, add data sources progressively

---

## Knowledge Base File Upload

### 功能说明
知识库页面提供拖拽上传和点击上传两种方式，支持批量上传多个文件。

**支持的文件格式**：
- 文档：`.pdf`, `.doc`, `.docx`, `.txt`, `.md`
- 数据：`.csv`, `.json`, `.xml`

**文件大小限制**：50MB

**上传流程**：
1. 点击"上传文档"按钮或拖拽文件到上传区域
2. 自动验证文件类型和大小
3. 显示上传进度条（实时进度）
4. 上传完成后自动索引到向量库
5. 刷新文档列表显示新文件

**前端组件**：
- `FileUploadDialog` (`frontend/components/knowledge/FileUploadDialog.tsx`)
  - 拖拽上传区域
  - 多文件批量上传
  - 实时进度显示
  - 错误处理和重试功能
  - 上传统计信息

**后端接口**：
- `POST /api/upload`
- Content-Type: `multipart/form-data`
- Form field: `file`
- 自动保存到 `data/raw/`
- 自动处理并索引到 `data/processed/` 和 FAISS 向量库

**使用示例**：
```typescript
import { uploadChatFile } from '@/lib/api/files';

const handleUpload = async (file: File) => {
  const result = await uploadChatFile(file, (progress) => {
    console.log(`Upload progress: ${progress.loaded}/${progress.total}`);
  });
  console.log('Uploaded:', result.fileId);
};
```

---

## Vector Store Architecture (Fast Version)

### 概述
系统已升级为 **VectorStoreFast** 优化版本，支持自动索引选择和性能优化。

### 技术特性

#### 1. 自动索引选择策略
```python
# VectorStoreFast 自动选择最优索引类型
- 向量数 < 10,000:  IndexFlatIP (精确检索，O(n))
- 向量数 ≥ 10,000:  IndexIVFPQ (近似检索，O(log n)，5-10倍加速)
```

#### 2. 性能对比

| 索引类型 | 向量数 | 搜索速度 | 精度 | 适用场景 |
|---------|-------|---------|-----|---------|
| **IndexFlatIP** | < 10k | 快 (~1ms) | 100% | 小型知识库 |
| **IndexIVFPQ** | ≥ 10k | 极快 (~0.1ms) | ~98% | 大型知识库 |

#### 3. 自动升级机制
当向量数量达到 10,000 时，系统会自动升级索引：

```python
# 自动触发条件
if vector_count >= 10000 and not is_ivf:
    print("🚀 向量数量达到 10000，升级为IVF+PQ索引...")
    upgrade_to_ivf()  # 自动完成，无需手动操作
```

**升级过程**：
1. 提取现有向量
2. 训练 IVF 聚类中心（nlist=100）
3. 应用 PQ 压缩（m=8, nbits=8）
4. 重新添加所有向量
5. 保存新索引（自动备份旧索引）

#### 4. 配置参数

```python
# main.py 中的配置
VectorStoreFast(
    dim=384,                 # 向量维度（all-MiniLM-L6-v2）
    use_ivf=None,           # None=自动判断，True=强制IVF，False=强制Flat
    nlist=100,              # IVF聚类数（影响检索速度和精度）
    m=8,                    # PQ子向量数（压缩率）
    nbits=8,                # 每个子向量位数
)
```

**参数调优建议**：
- `nlist`: 聚类数 = sqrt(向量数)，100-1000 之间
- `m`: 子向量数，越大压缩率越低、精度越高，推荐 8-16
- `nbits`: 比特数，推荐 8（平衡精度和内存）

#### 5. 使用场景

**✅ 当前使用 Flat（推荐）**：
- 向量数 < 10,000
- 精度要求 100%
- 搜索速度已足够快（< 1ms）

**🚀 未来自动升级到 IVF**：
- 向量数 ≥ 10,000
- 需要更快检索速度
- 可接受 ~2% 精度损失

#### 6. 手动迁移（可选）

如果需要立即升级到 IVF（不推荐，除非向量数已 > 10k）：

```bash
# 备份现有索引并升级
python scripts/migrate_to_fast_index.py --auto

# 性能对比测试
python scripts/benchmark_rag_performance.py
```

#### 7. 监控和统计

```bash
# 查看索引状态
python scripts/rag_cli.py info

# 输出示例：
# 📥 加载向量库: 1345 个向量, 索引类型: Flat
# 向量库大小: 1345 个块
# 索引路径: D:\...\data\embeddings\index.faiss
```

**关键指标**：
- `索引类型`: Flat（精确）或 IVF+PQ（近似）
- `向量数量`: 当前存储的向量数
- `搜索性能`: 平均检索时间（通过 benchmark 测试）

#### 8. 故障排查

**问题：升级后搜索结果不准确**
- **原因**: IVF 近似检索可能丢失部分结果
- **解决**: 增加 `nprobe` 参数（探测更多聚类）
  ```python
  store.search(query_vec, top_k=5, nprobe=20)  # 默认10，增加到20提高召回
  ```

**问题：索引文件损坏或不兼容**
- **原因**: Fast 版本索引格式不同
- **解决**: 重新构建索引
  ```bash
  python scripts/rag_cli.py build --rebuild
  ```

---

## Troubleshooting & Known Issues

### 批量删除文档功能 (Batch Delete Documents)

#### 问题：前端批量删除返回 405 Method Not Allowed
**症状**：点击批量删除按钮后，控制台显示：
```
POST /api/admin/files/batch-delete HTTP/1.1" 405 Method Not Allowed
```

**原因**：后端缺少批量删除接口（已修复）

**解决方案**：
1. 确认后端 `src/api/admin.py` 包含批量删除接口：
   ```python
   @router.post("/files/batch-delete")
   def batch_delete_files(
       request: BatchDeleteRequest,
       db: Session = Depends(get_db),
       admin: User = Depends(require_admin),
   ):
   ```

2. 重启后端服务：
   ```bash
   python manage.py start backend
   ```

3. 测试批量删除：
   - 登录管理员账号
   - 访问 `http://localhost:3000/dashboard/knowledge`
   - 勾选多个文档
   - 点击"批量删除"按钮
   - 应该看到成功通知

**API 规格**：
- **端点**：`POST /api/admin/files/batch-delete`
- **权限**：管理员
- **请求体**：
  ```json
  {
    "fileNames": ["file1.pdf", "file2.txt"]
  }
  ```
- **响应体**：
  ```json
  {
    "success": ["file1.pdf"],
    "failed": [{"fileName": "file2.txt", "reason": "文件不存在"}],
    "total": 2
  }
  ```

**安全措施**：
- ✅ 路径遍历防护（拒绝包含 `..`、`/`、`\` 的文件名）
- ✅ 管理员权限验证
- ✅ 详细的操作日志记录

**前端类型定义** (`frontend/lib/types/api.ts`)：
```typescript
export interface BatchDeleteRequest {
    fileNames: string[];  // 使用 fileNames 而非 fileIds
}

export interface BatchDeleteResponse {
    success: string[];    // 成功删除的文件名列表
    failed: Array<{ fileName: string; reason: string }>;
    total: number;
}
```

#### 问题：删除后文件仍显示在列表中
**解决方案**：
1. 检查前端是否调用了缓存失效：
   ```typescript
   queryClient.invalidateQueries({ queryKey: ["documents"] });
   ```
2. 手动刷新页面验证
3. 检查后端日志确认删除成功

#### 问题：权限错误 403 Forbidden
**解决方案**：
1. 确认当前用户是管理员角色（role = "ADMIN"）
2. 检查 JWT token 有效性
3. 重新登录

### RAG 检索超时问题

#### 问题：查询响应缓慢或超时
**解决方案**：
1. 检查 `.env` 配置：
   ```bash
   RAG_TIMEOUT_SECONDS=25  # 调整超时时间
   ```
2. 检查后端日志是否显示 `fallback_mode: true`（表示已降级）
3. 优化 FAISS 索引或减少文档数量

### PDF 文档显示异常问题

#### 问题 1：检索结果显示全角字符（半角转全角）
**症状**：
- 文档预览中英文和数字显示为全角字符，例如：
  ```
  ｈｏｗｔｏｃｏｎｔｒｏｌｔｈｅｔｙｐｅ，ｔｏｔａｌａｍｏｕｎｔａｎｄｓｉｚｅ
  ２０２４，Ｖｏｌ. ３８，Ｎｏ. ３
  ```
- 搜索时使用半角字符无法正确匹配文档中的全角内容
- 影响搜索准确性和可读性

**原因**：
某些 PDF 文件（特别是学术期刊）使用特殊字体编码，导致提取的文本为全角字符。原有的 `_postprocess_pdf_text` 方法只处理了字母空格分离问题，未处理全角转半角。

**解决方案（已修复）**：
1. **代码修复**：在 `src/data_processing/loader.py` 中新增 `_convert_fullwidth_to_halfwidth` 方法
   - 自动将全角数字（０-９）转换为半角（0-9）
   - 自动将全角英文字母（Ａ-Ｚ，ａ-ｚ）转换为半角（A-Z, a-z）
   - 自动将全角标点和空格转换为半角
   - 基于 Unicode 范围 `0xFF01-0xFF5E` 和 `0x3000` 进行转换

2. **重建索引**：修复后需重建 RAG 索引以应用更新
   ```bash
   python scripts/rag_cli.py build --rebuild
   ```

3. **验证修复**：
   ```bash
   # 测试 PDF 加载是否正确转换
   python -c "from src.data_processing.loader import DataLoader; \
              loader = DataLoader(); \
              text = loader.load('your_file.pdf'); \
              print(text[:500])"
   ```

**技术细节**：
```python
def _convert_fullwidth_to_halfwidth(self, text: str) -> str:
    """全角转半角：
    - 全角空格 (0x3000) -> 半角空格 (0x0020)
    - 全角 ASCII (0xFF01-0xFF5E) -> 半角 ASCII (0x0021-0x007E)
    - 转换公式：半角码 = 全角码 - 0xFEE0
    """
    result = []
    for char in text:
        code = ord(char)
        if code == 0x3000:
            result.append(' ')
        elif 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        else:
            result.append(char)
    return ''.join(result)
```

**已修复 - 连续英文智能分词**：
- **问题**：某些 PDF 中英文为连续全角字母无分隔（如 `Ｔｈｉｓｗｏｒｋｗａｓ`）
- **解决方案**：集成 `wordninja` 智能分词工具
  - 自动检测长连续英文字符串（10+ 字符）
  - 智能分词为正常单词，如 `Thisworkwas` → `This work was`
  - 对正常单词不产生影响（避免误伤）
- **效果对比**：
  ```
  查询: "how to control micro inclusions"
  
  ❌ 全角字符（修复前）:      -0.8% 相似度
  ⚠️  半角无空格（简单转换）:  14.0% 相似度
  ✅ 智能分词（修复后）:      98.8% 相似度 🎉
  ```
- **性能提升**：相比简单转换提升 **605.7%**，接近完美！
- **依赖安装**：
  ```bash
  pip install wordninja
  # 或重新安装依赖
  pip install -r requirements.txt
  ```

#### 问题 2：明确存在的文档检索不到或相关度低
**症状**：
- 知识库中存在文件 `高精度冷连轧数字孪生与信息.CPS关键技术研发及应用.pdf`
- 查询 "高精度冷连轧数字孪生与信息是什么" 时，该文档未出现在 Top 10 结果中
- 或相关度得分较低（如 64.9%），排名靠后

**原因分析**：
1. **文档结构问题**：
   - 文档标题在第一个分块中，但没有实际内容解释"是什么"
   - 其他分块包含具体技术细节，但缺少概念性解释
   - 查询意图（"是什么"）与文档内容（技术实现）语义不匹配

2. **分块策略问题**：
   - 默认分块大小 600 字符，overlap 100 字符
   - 标题和正文可能被分隔到不同块中
   - 关键信息分散在多个块中，降低单块相关度

3. **查询-文档语义差距**：
   - 用户查询："高精度冷连轧数字孪生与信息是什么"（概念查询）
   - 文档内容："多策略厚度张力解耦控制算法"（技术实现）
   - Embedding 模型将它们视为不同语义空间

**解决方案**：

1. **优化查询策略**：
   ```bash
   # 使用更具体的关键词
   "高精度冷连轧数字孪生 CPS 关键技术"  # ✅ 更接近文档内容
   "高精度冷连轧数字孪生与信息是什么"    # ❌ 过于概念化
   ```

2. **调整分块参数**（可选）：
   ```bash
   # 增大分块大小以保留更多上下文
   python scripts/rag_cli.py build --chunk-size 1000 --chunk-overlap 200
   ```

3. **增加 top_k 值**：
   ```python
   # 在 config/settings.py 中调整
   top_k: int = 10  # 默认 5，增加到 10 可能找到更多相关文档
   ```

4. **使用文件名搜索**（临时方案）：
   - 如果知道文件名，可以在知识库页面直接搜索文件名
   - 或使用管理后台的文件列表筛选

5. **检查文档内容**：
   ```bash
   # 查看文档的实际分块内容
   python -c "import json; from pathlib import Path; \
              p = Path('data/processed/YOUR_FILE.pdf.chunks.jsonl'); \
              lines = p.read_text(encoding='utf-8').split('\n'); \
              [print(f'块{i}:', json.loads(line)['content'][:200], '\n') \
               for i, line in enumerate(lines[:5])]"
   ```

**为什么相关度是 64.9%？**
- FAISS 使用归一化余弦相似度，范围 `[0, 1]`
- 0.649 表示查询向量与文档向量的余弦相似度为 64.9%
- 这个得分说明**语义相关但不完全匹配**
- 对于概念查询 vs 技术实现文档，60-70% 的相关度是正常的

**最佳实践**：
1. ✅ 上传文档时确保包含概念性介绍（摘要、引言）
2. ✅ **查询时使用文档中实际出现的技术术语**（如"板形控制"、"张力解耦"、"协同优化"）
3. ✅ 对于特定文档查询，结合文件名搜索
4. ✅ 定期检查分块质量（使用 `rag_cli.py info`）
5. ✅ **使用诊断工具测试查询效果**（`python scripts/diagnose_retrieval.py`）
6. ❌ 避免过于宽泛或概念化的查询（"是什么"、"介绍一下"等）
7. ❌ 避免只使用文档标题查询（标题可能被元数据稀释）

### 前端开发服务器问题

#### 问题：npm run dev 失败
**解决方案**：
1. 删除依赖并重新安装：
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```
2. 检查 Node.js 版本（需要 18+）：
   ```bash
   node --version
   ```

#### 问题：shadcn 组件未正确显示
**解决方案**：
1. 确认已安装 shadcn 组件：
   ```bash
   npx shadcn@latest add sonner
   ```
2. 检查 `components.json` 配置
3. 验证 Tailwind CSS 配置正确

### 数据库问题

#### 问题：数据库连接失败
**解决方案**：
1. 重置数据库：
   ```bash
   python scripts/db_migrate.py reset
   ```
2. 重新初始化：
   ```bash
   python manage.py init
   ```

#### 问题：找不到表或字段
**解决方案**：
1. 运行迁移：
   ```bash
   python scripts/db_migrate.py add-prompts
   ```
2. 检查数据库状态：
   ```bash
   python manage.py check --verbose
   ```

### 文件上传问题

#### 问题：上传后显示重复文件或文件名包含哈希前缀
**症状**：
- 上传一个文件后，列表中显示两个文件
- 其中一个文件大小为 2 Bytes（.done 文件）
- 文件名包含 `.chunks.jsonl` 扩展名
- 预览/下载失败，返回 404 错误

**根本原因**：
1. `list_files` 接口原本从 `data/processed` 读取，列出了内部处理文件（.chunks.jsonl, .done）
2. 文件 ID 使用 `doc.fileName`（显示名称）而不是完整的 `doc.id`（包含哈希前缀）

**解决方案（已修复）**：
1. **后端修改** (`src/api/admin.py`):
   - `list_files` 改为从 `data/raw` 读取原始文件
   - 过滤掉内部处理文件（.chunks.jsonl, .done）
   - 使用实际文件名作为 ID，提取显示名称（移除哈希前缀）
   - `delete_file` 同时删除 `data/raw` 和 `data/processed` 中的文件
   - 新增 `preview_file` 和 `download_file` 接口

2. **前端修改** (`frontend/app/dashboard/knowledge/page.tsx`):
   - 所有 API 调用使用 `doc.id`（完整文件 ID）而不是 `doc.fileName`
   - 预览：`previewDocument(doc.id)`
   - 下载：`downloadDocument(doc.id)`
   - 删除：`deleteDocument(doc.id)`
   - 批量删除：使用 `doc.id` 数组
   - 重新索引：`reindexDocument(doc.id)`

**文件存储结构**：
```
data/
├── raw/                          # 原始上传文件
│   └── {hash}_{filename}         # 完整 file_id
└── processed/                    # 处理后的文件
    ├── {hash}_{filename}.chunks.jsonl  # 分块数据
    └── {hash}_{filename}.done          # 处理完成标记
```

**API 端点更新**：
- `GET /api/admin/files` - 从 data/raw 读取，返回 `{id: 完整file_id, fileName: 显示名称}`
- `GET /api/admin/files/{file_name}/preview` - 预览原始文件 + 分块信息
- `GET /api/admin/files/{file_name}/download` - 下载原始文件
- `DELETE /api/admin/files/{file_name}` - 删除原始文件 + 处理文件

#### 问题：上传按钮点击无反应
**解决方案**：
1. 检查 `FileUploadDialog` 组件是否正确导入
2. 确认 `isUploadDialogOpen` 状态已添加
3. 验证按钮 `onClick` 事件绑定正确

#### 问题：文件上传失败
**常见原因**：
1. 文件大小超过 50MB 限制
2. 文件格式不支持（只支持 PDF, DOC, DOCX, TXT, MD, CSV, JSON, XML）
3. 后端服务未启动或无权限
4. 磁盘空间不足

**解决方案**：
1. 检查文件大小：`ls -lh data/raw/`
2. 验证文件格式扩展名
3. 检查后端日志是否有错误
4. 确认 `data/raw/` 和 `data/processed/` 目录存在且可写

#### 问题：文件上传后无法检索
**解决方案**：
1. 检查向量索引是否成功：
   ```bash
   python scripts/rag_cli.py info
   ```
2. 重建 RAG 索引：
   ```bash
   python scripts/rag_cli.py build --rebuild
   ```
3. 检查文档是否在 `data/processed` 目录
4. 验证 `.done` 标记文件是否存在

#### 问题：上传进度条不显示
**解决方案**：
1. 检查 `Progress` 组件是否正确安装
2. 验证 Axios `onUploadProgress` 回调是否正确
3. 检查浏览器控制台是否有 JavaScript 错误

#### 问题：预览/下载返回 404 Not Found
**症状**：
```
GET /api/admin/files/xxx.chunks.jsonl/preview HTTP/1.1" 404 Not Found
```

**原因**：前端使用 `doc.fileName`（显示名称）而不是 `doc.id`（完整文件 ID）

**解决方案**：
1. 确保前端所有文件操作使用 `doc.id`
2. 检查后端接口从 `data/raw` 读取文件
3. 验证文件 ID 格式正确：`{hash}_{original_name}`

### 通用调试步骤

1. **检查后端日志**：查看详细错误信息
2. **检查前端 Console**：查看 JavaScript 错误
3. **检查 Network 标签**：验证 API 请求/响应
4. **重启服务**：
   ```bash
   python manage.py start backend
   npm run dev  # 在 frontend 目录
   ```
5. **清除缓存**：浏览器开发者工具 → Application → Clear storage