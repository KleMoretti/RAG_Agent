# AGENTS.md (Automation Cheatsheet)
1. Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (Python 3.10+).
2. Run API (if FastAPI app in `main.py`): `uvicorn main:app --reload`.
3. Tests: all `pytest -q`; single file `pytest tests/integration.py`; single test `pytest tests/integration.py::test_name`; keyword `pytest -k search`.
4. Async: use `pytest-asyncio`; mark coroutines with `@pytest.mark.asyncio`.
5. Imports order: stdlib, third-party, local (no wildcards); blank line between groups.
6. Types: annotate all public functions; prefer `list[str]` / `str | None`; no implicit Any.
7. Docstrings: Google style (Args, Returns, Raises) for public APIs; brief summary line first.
8. Naming: modules snake_case; classes PascalCase; functions/vars snake_case; constants UPPER_SNAKE; internal helpers `_prefixed`.
9. Errors: never silent; log then raise domain or ValueError; no bare `except`; preserve context (`raise ... from e`).
10. Logging: use `config.logging_config.setup_logging`; levels => INFO workflow, DEBUG internals, WARNING recoverable, ERROR failure, CRITICAL outage; no `print` in src.
11. Data/paths: use `pathlib.Path`; directories created lazily in `get_settings()`.
12. Vector/RAG metadata keys: `file, chunk_id, hash, preview, score, rank`; keep embeddings float32; batch for performance.
13. Tool/Agent: extend `Tool`, register via `BaseAgent.add_tool`; duplicate names raise ValueError; reasoning path via `ReasoningEngine`.
14. Formatting: recommend `ruff format` or `black`; line length ≤ 100; strip unused imports (ruff).
15. Lint (optional): `ruff check .`; type check (if added) `mypy src tests`.
16. Commits: Conventional (`feat:`, `fix:`, `refactor:`); PR must pass `pytest -q`; keep diffs focused.
17. Config: only through `get_settings()`; no hardcoded secrets; `.env` ignored; add `.env.example` when new vars.
18. Performance: batch embeddings; avoid redundant FAISS loads; consider caching frequent queries.
19. Security: validate user input before search/LLM; never log secrets; plan filters (`tenant_id`, `visibility`).
20. No Cursor/Copilot rule files present now—update line 20 if added.

## 用户权限系统

### 用户角色
- **admin**: 管理员，拥有所有权限，可以管理用户和文件
- **user**: 普通用户，根据权限设置访问功能

### 用户权限字段
- `is_active`: 账户是否激活
- `can_upload`: 是否可以上传文件
- `can_download`: 是否可以下载文件
- `can_chat`: 是否可以聊天

### API 接口

#### 认证接口 (`/api/auth/`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /me` - 获取当前用户信息
- `POST /refresh` - 刷新访问令牌

#### 管理员接口 (`/api/admin/`) - 需要管理员权限

**用户管理:**
- `GET /users` - 获取用户列表 (支持分页和搜索)
- `POST /users` - 创建新用户
- `GET /users/{user_id}` - 获取用户详情
- `PUT /users/{user_id}` - 更新用户信息
- `DELETE /users/{user_id}` - 删除用户

**文件管理:**
- `GET /files` - 获取文件列表 (支持分页和搜索)
- `DELETE /files/{file_name}` - 删除文件

**系统统计:**
- `GET /stats` - 获取系统统计信息

#### 聊天接口 (`/api/chat`)
- `POST /chat` - 发送聊天消息 (需要 `can_chat` 权限)

#### 文件上传接口 (`/api/upload`)
- `POST /upload` - 上传文件 (需要 `can_upload` 权限)

### 前端页面
- `/login` - 登录页面
- `/register` - 注册页面
- `/chat` - 聊天页面 (根据用户权限显示不同功能)
- `/admin` - 管理员控制台 (仅管理员可访问)

### 权限检查
系统使用 JWT 令牌进行身份验证，每个 API 端点都会检查相应的权限：
- 管理员接口需要 `role: "admin"`
- 文件上传需要 `can_upload: true`
- 聊天功能需要 `can_chat: true`

Fallback EchoClient (local testing)

- **When to use**: If you do not have a valid LLM API key (e.g. `QWEN_API_KEY`) or want to run the agent offline for tests and demos, the project falls back to a local `EchoClient` implementation.
- **Behavior**: `EchoClient` is a synchronous, deterministic client that returns a simple echo of the prompt. It is suitable for unit/integration tests and interactive local runs where real LLM responses are not required.
- **How to run**: Start the CLI without setting an API key:
  - `python main.py`  # will use `EchoClient` and show prompts/responses locally
- **Notes**: The echo client preserves the `LLMClient` interface so components (agents, reasoning engine, tools) can be exercised without network access.
