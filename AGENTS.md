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