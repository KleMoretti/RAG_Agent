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
```

### Database Management (scripts/db_migrate.py)
```bash
# 数据库迁移
python scripts/db_migrate.py reset          # 重置数据库
python scripts/db_migrate.py add-presets   # 添加预设问题表
python scripts/db_migrate.py add-prompts   # 添加 Prompt 管理表
python scripts/db_migrate.py status        # 查看数据库状态
```

---

## Development Standards

1. Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (Python 3.10+)
2. Start: `python manage.py start all` or `python manage.py start backend` (FastAPI on port 8000)
3. Tests: all `pytest -q`; single file `pytest tests/integration.py`; single test `pytest tests/integration.py::test_name`; keyword `pytest -k search`.

**📊 Production Mode (with real data)**:
- 💹 **Live Price Feed**: Real-time iron ore, coal, steel product prices from market APIs
- 📈 **Interactive Price Charts**: Historical trends with predictive forecasting
- 🌐 **Supply Chain Monitoring**: Track raw material availability and logistics status
- 📊 **Cost Impact Calculator**: Real-time calculation of price changes on production costs
- 🔔 **Smart Price Alerts**: ML-filtered alerts for significant market movements

**🎭 Demo Mode (without real data)**:
- 📰 Industry news and report aggregation (uploaded documents)
- 📊 **Sample Price Data**: Historical datasets for demonstration (2020-2024 trends)
- 🎲 **Scenario Simulation**: Pre-configured market scenarios (bull/bear markets, supply shocks)
- 📈 **Static Visualizations**: Sample charts showing typical price patterns

**🤖 Agent Capabilities (both modes)**:
- 🤖 AI-powered insight extraction from market reports and real-time data
- 📊 Document-based trend analysis (AI summarizes price reports, market analyses)
- 🆕 **Multi-document Synthesis**: Agent combines insights from multiple reports into unified analysis
- 🆕 **Trend Narrative Generation**: AI writes executive summaries from raw data/reports
- 🆕 **Competitive Intelligence Extraction**: Auto-extract competitor info from news/reports
- 🆕 **Custom Alert Builder**: Define keywords/topics, Agent monitors new uploads/data and notifies
- 🆕 **What-If Scenario Analysis**: "What if iron ore price increases 20%?" - Agent reasons through implications
- 🆕 **Report Comparison Tool**: Side-by-side comparison of different analyst reports with discrepancy highlights
- 🆕 **Procurement Recommendation**: Agent suggests optimal buying windows based on price trends and inventory
- 🆕 **Market Event Correlation**: Link price movements to news events using NLP analysisstant

**📊 Production Mode (with real data)**:
- 🏭 **Real-time Equipment Status**: Live data from sensors (temperature, vibration, pressure)
- 📈 **Health Score Dashboard**: Equipment health trends with predictive analytics
- ⚠️ **Anomaly Detection**: ML-based detection of abnormal patterns triggering Agent investigation
- 📅 **Smart Maintenance Scheduling**: AI suggests optimal maintenance timing based on usage patterns
- 🔔 **Alert-triggered Q&A**: Automatic Agent responses when equipment alerts occur

**🎭 Demo Mode (without real data)**:
- 📋 Equipment knowledge base (manuals, fault logs, maintenance guides)
- 🎲 **Simulated Equipment Status**: Sample data showing typical operational scenarios
- 📊 **Historical Case Studies**: Pre-loaded fault scenarios for interactive demonstration
- 🎬 **Interactive Scenarios**: "What-if" simulations using documented cases

**🤖 Agent Capabilities (both modes)**:
- 🔧 Conversational fault diagnosis based on symptoms
- 📖 Retrieve relevant troubleshooting procedures from documents
- 💡 Multi-step reasoning for complex equipment issues
- 🆕 **Symptom-to-Solution Mapping**: Agent asks clarifying questions to narrow down fault causes
- 🆕 **Maintenance Procedure Generator**: Auto-generate step-by-step repair guides from manuals
- 🆕 **Historical Case Retrieval**: "Similar issues in the past" based on RAG search
- 🆕 **Safety Protocol Advisor**: Auto-extract and highlight safety warnings from manuals
- 🆕 **Parts Cross-reference**: Agent helps find alternative part numbers across different suppliers
- 🆕 **Diagnostic Decision Tree**: Interactive fault diagnosis with yes/no questions
- 🆕 **Root Cause Analysis**: Agent guides users through 5-Whys methodology with knowledge base supportAPI (if FastAPI app in `main.py`): `uvicorn main:app --reload`.
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
13. Tool/Agent: extend `Tool`, register via `BaseAgent.add_tool`; duplicate names raise ValueError; reasoning path via `ReasoningEngine`.
14. Formatting: recommend `ruff format` or `black`; line length ≤ 100; strip unused imports (ruff).
15. Lint (optional): `ruff check .`; type check (if added) `mypy src tests`.
16. Commits: Conventional (`feat:`, `fix:`, `refactor:`); PR must pass `pytest -q`; keep diffs focused.
17. Config: only through `get_settings()`; no hardcoded secrets; `.env` ignored; add `.env.example` when new vars.
18. Performance: batch embeddings; avoid redundant FAISS loads; consider caching frequent queries.
19. Security: validate user input before search/LLM; never log secrets; plan filters (`tenant_id`, `visibility`).
20. **RAG Timeout & Fallback**: RAG检索+LLM调用有25秒超时（可配置`RAG_TIMEOUT_SECONDS`），超时自动降级为直接使用LLM（不带RAG上下文），确保用户始终能获得响应。前端总超时60秒。
21. **Documentation Updates Only**: All project documentation and standards MUST be maintained in AGENTS.md. Never create new separate documentation files (e.g., no new README files, GUIDE.md, STANDARDS.md, etc.). Update existing AGENTS.md instead.

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

### Internationalization (i18n)

37. **Language Configuration**
    - ✅ **Default Language**: Chinese (zh-CN) as primary language
    - ✅ **Secondary Language**: English (en-US) for international support
    - ✅ Use custom `useTranslation` hook for all translatable text
    - ✅ Store language preference in `uiStore.language` with localStorage persistence

38. **Translation Management**
    ```typescript
    // lib/i18n/locales/zh-CN.ts
    export const zhCN = {
      common: {
        login: '登录',
        logout: '退出',
        submit: '提交',
        cancel: '取消',
      },
      auth: {
        username: '用户名',
        password: '密码',
        loginTitle: '钢铁行业 AI 决策中心',
      },
      // ... more translations
    };

    // lib/i18n/locales/en-US.ts
    export const enUS = {
      common: {
        login: 'Login',
        logout: 'Logout',
        submit: 'Submit',
        cancel: 'Cancel',
      },
      auth: {
        username: 'Username',
        password: 'Password',
        loginTitle: 'Steel Industry AI Hub',
      },
      // ... more translations
    };
    ```

39. **i18n Best Practices**
    - ✅ All user-facing text must be translatable (no hardcoded strings)
    - ✅ Use semantic keys: `auth.loginButton` not `button1`
    - ✅ Support Chinese technical terminology with English equivalents
    - ✅ Date/number formatting according to locale (date-fns with locale)
    - ✅ RTL support not required (Chinese/English are LTR)
    - ❌ Never mix languages in the same UI component

---

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
- � Equipment knowledge base (manuals, fault logs, maintenance guides)
- 🔧 Conversational fault diagnosis based on symptoms
- 📖 Retrieve relevant troubleshooting procedures from documents
- � Multi-step reasoning for complex equipment issues
- 🆕 **Symptom-to-Solution Mapping**: Agent asks clarifying questions to narrow down fault causes
- 🆕 **Maintenance Procedure Generator**: Auto-generate step-by-step repair guides from manuals
- 🆕 **Historical Case Retrieval**: "Similar issues in the past" based on RAG search
- 🆕 **Safety Protocol Advisor**: Auto-extract and highlight safety warnings from manuals
- 🆕 **Parts Cross-reference**: Agent helps find alternative part numbers across different suppliers
- 🆕 **Diagnostic Decision Tree**: Interactive fault diagnosis with yes/no questions

#### 4. Market Intelligence & Analysis Assistant
- � Industry news and report aggregation (uploaded documents)
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
- `POST /api/upload` - File upload
- `GET /api/admin/users` - Get user list
- `PUT /api/admin/users/:id` - Update user

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