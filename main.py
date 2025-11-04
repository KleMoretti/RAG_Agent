#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application for RAG_Agent system.
This module demonstrates how to use the RAG agent and LLM components.
Also exposes a FastAPI app at /api/chat for frontend integration.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import argparse

# Import components from our source folder
from src.agent import RAGAgent
from src.agent.reasoning import ReasoningEngine
from src.llm import LLMClient, OpenAIClient, OpenAIConfig, EchoClient

# --- Tool Definitions ---
from src.agent.tools import SearchTool, CalculatorTool

# Load environment variables from .env files (root and src/llm/.env) early
try:
    # Load default .env in project root if present
    load_dotenv()
    # Explicitly load src/llm/.env if present
    llm_env_path = Path(__file__).parent / "src" / "llm" / ".env"
    if llm_env_path.exists():
        load_dotenv(llm_env_path)
except Exception:
    # Don't fail if dotenv isn't available; requirements include it but keep robust
    pass

# --------------------------- RAG Agent construction --------------------------- #
from functools import lru_cache

# Reuse data processing + retrieval stack for uploads
from src.data_processing.preprocessor import Preprocessor
from src.data_processing.loader import DataLoader
from src.data_processing.embedder import Embedder
from src.retrieval.vector_store_fast import VectorStoreFast
from src.retrieval.dual_vector_store import DualVectorStoreManager
from src.vocabulary import VocabularyService, QueryEnhancer
from config.settings import get_settings

# Project data directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EMBED_DIR = DATA_DIR / "embeddings"

# 读取配置
_settings = get_settings()

# 知识库目录
KB_RAW_DIR = Path(_settings.knowledge_base_raw_dir)
KB_PROCESSED_DIR = Path(_settings.knowledge_base_processed_dir)

# 用户上传目录
USER_RAW_DIR = Path(_settings.user_uploads_raw_dir)
USER_PROCESSED_DIR = Path(_settings.user_uploads_processed_dir)

for _d in (RAW_DIR, PROCESSED_DIR, EMBED_DIR, KB_RAW_DIR, KB_PROCESSED_DIR, USER_RAW_DIR, USER_PROCESSED_DIR):
    try:
        _d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


@lru_cache(maxsize=1)
def get_preprocessor() -> Preprocessor:
    return Preprocessor()


@lru_cache(maxsize=1)
def get_loader() -> DataLoader:
    return DataLoader()


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    # Model name can be overridden by env if needed
    model_name = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")
    return Embedder(model_name=model_name)


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStoreFast:
    """获取单一向量存储（向后兼容，已废弃）
    
    注意：新代码应使用 get_dual_vector_store() 以支持知识库和用户上传文件的隔离
    """
    emb = get_embedder()
    index_path = EMBED_DIR / "index.faiss"
    meta_path = EMBED_DIR / "index.meta.jsonl"
    # Vectors we add below are already L2-normalized by Embedder.encode
    # use_ivf=None: 自动判断（<10k用Flat，>=10k自动升级为IVF）
    return VectorStoreFast(
        dim=emb.dim,
        index_path=index_path,
        metadata_path=meta_path,
        normalize=False,
        use_ivf=None,  # 自动选择
        nlist=100,  # IVF聚类数
        m=8,  # PQ子向量数
        nbits=8,  # 每个子向量8位
    )


@lru_cache(maxsize=1)
def get_dual_vector_store() -> DualVectorStoreManager:
    """获取双向量存储管理器（知识库 + 用户上传）"""
    emb = get_embedder()
    settings = get_settings()
    
    return DualVectorStoreManager(
        kb_index_path=settings.knowledge_base_index_path,
        user_index_path=settings.user_uploads_index_path,
        dim=emb.dim,
        user_upload_score_threshold=settings.user_upload_score_threshold,
        enable_priority_search=settings.enable_priority_search,
    )


@lru_cache(maxsize=1)
def get_vocabulary_service():
    """获取专业词汇服务（单例，带缓存）"""
    from src.api.db import SessionLocal

    db = SessionLocal()
    vocab_service = VocabularyService(db)
    vocab_service.initialize()  # 预加载词汇库到内存
    return vocab_service


@lru_cache(maxsize=1)
def get_query_enhancer() -> QueryEnhancer:
    """获取查询增强器（单例）"""
    vocab_service = get_vocabulary_service()
    return QueryEnhancer(vocab_service)


def _safe_filename(name: str) -> str:
    # Very simple sanitization for filesystem compatibility
    bad = ["..", "/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    out = name
    for b in bad:
        out = out.replace(b, "_")
    return out


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Sliding-window chunking to preserve context, works for both CN/EN text."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _text_from_file(
    saved_path: Path, orig_filename: str, content_type: Optional[str]
) -> str:
    """Best-effort text extraction for various file types using DataLoader when applicable."""
    ext = saved_path.suffix.lower()
    loader = get_loader()
    try:
        # Use DataLoader for supported rich formats
        if ext in {".pdf", ".docx", ".doc", ".wav", ".mp3"}:
            return loader.load(str(saved_path))
    except Exception:
        # Fallback to plain text read below
        pass
    # Plain text fallback for common text/code formats
    try:
        return saved_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        # Final fallback: binary decode best-effort
        data = saved_path.read_bytes()
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            # As a last resort, return empty
            return ""


def process_and_index_file(
    saved_path: Path,
    file_id: str,
    orig_name: str,
    content_type: Optional[str],
    upload_type: str = "user_upload",  # "knowledge_base" 或 "user_upload"
    processed_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Extract text, clean and chunk, persist processed chunks, and index into vector store.

    Args:
        saved_path: 保存的文件路径
        file_id: 文件ID
        orig_name: 原始文件名
        content_type: 文件MIME类型
        upload_type: 上传类型（knowledge_base 或 user_upload）
        processed_dir: 处理后文件保存目录（可选）

    Returns:
        list of {content, type, length} dicts for API preview.
    """
    pre = get_preprocessor()
    text = _text_from_file(saved_path, orig_name, content_type)
    cleaned = pre.clean_text(text)
    # Prefer paragraph split then join or directly chunk cleaned
    if not cleaned:
        chunks: List[str] = []
    else:
        chunks = _chunk_text(cleaned, chunk_size=1000, overlap=150)

    # 确定处理后文件保存目录
    if processed_dir is None:
        if upload_type == "knowledge_base":
            processed_dir = KB_PROCESSED_DIR
        else:
            processed_dir = USER_PROCESSED_DIR

    # Persist processed chunks as JSONL for traceability
    out_jsonl = processed_dir / f"{file_id}.chunks.jsonl"
    try:
        with out_jsonl.open("w", encoding="utf-8") as f:
            for i, c in enumerate(chunks):
                import json

                f.write(
                    json.dumps(
                        {
                            "file_id": file_id,
                            "file_name": orig_name,
                            "chunk_id": i,
                            "content": c,
                            "length": len(c),
                            "upload_type": upload_type,  # 添加上传类型标记
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
    except Exception:
        # Don't fail upload if processed save encounters an error
        pass

    # Build embeddings and add to dual vector store
    if chunks:
        try:
            emb = get_embedder()
            vectors = emb.encode(chunks, normalize=True)
            dual_store = get_dual_vector_store()
            metadatas = []
            import hashlib

            for i, c in enumerate(chunks):
                metadatas.append(
                    {
                        "file": str(saved_path),
                        "chunk_id": i,
                        "hash": hashlib.md5(c.encode("utf-8")).hexdigest(),
                        "preview": c[:100],
                        "file_id": file_id,
                        "file_name": orig_name,
                        "upload_type": upload_type,  # 添加上传类型标记
                    }
                )
            # 添加到对应的索引
            dual_store.add(vectors, metadatas, store_type=upload_type)
            # Persist to disk
            dual_store.save(store_type=upload_type)
            
            print(f"✅ 已将 {len(chunks)} 个块索引到 {upload_type} 索引")
        except Exception as e:
            # Embedding/indexing errors shouldn't fully break the upload
            print(f"⚠️ 索引失败: {e}")
            pass

    # Prepare API preview chunks
    preview: List[Dict[str, Any]] = []
    for c in chunks[:50]:  # limit preview count to avoid large payloads
        preview.append({"content": c, "type": "text", "length": len(c)})
    return preview


def create_agent(llm_client: LLMClient, system_prompt: str | None = None) -> RAGAgent:
    """
    Create and configure an agent with tools and a reasoning engine.

    Args:
        llm_client: LLM client for the reasoning engine.
        system_prompt: Optional system prompt for the agent.

    Returns:
        A configured RAGAgent with steel industry tools.
    """
    # Create the reasoning engine with the LLM client
    reasoning_engine = ReasoningEngine(model=llm_client)

    # Create the RAG agent
    agent = RAGAgent(
        llm_client=llm_client,
        reasoning_engine=reasoning_engine,
        name="钢铁行业AI助手 (Steel Industry AI Assistant)",
    )

    # Add basic tools
    agent.add_tool(SearchTool())
    agent.add_tool(CalculatorTool())

    # Add steel industry specialized tools
    try:
        from src.agent.steel_tools import register_steel_tools

        tools_count = register_steel_tools(agent)
        print(f"✅ 已注册 {tools_count} 个钢铁专业工具")
    except Exception as e:
        print(f"⚠️ 钢铁工具注册失败: {e}")

    return agent


import shutil
import textwrap


# 可复用的换行工具函数
def wrap_text(text: str, width: int) -> str:
    lines = []
    for para in text.splitlines():
        if not para.strip():
            lines.append("")
        else:
            lines.extend(
                textwrap.wrap(
                    para,
                    width=width,
                    replace_whitespace=False,
                    drop_whitespace=False,
                    break_long_words=True,
                    break_on_hyphens=False,
                )
            )
    return "\n".join(lines)


# --------------------------- FastAPI app --------------------------- #
try:
    from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from src.api.models import User
    from src.api.auth import _get_current_user
    import tempfile
    import mimetypes
    import hashlib

    app = FastAPI(title="RAG Agent API")
    # CORS configuration - allow specific origins for security
    cors_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # Add common local network IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
    # This allows other computers on the same network to access the API
    import socket

    try:
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if local_ip.startswith(("192.168.", "10.", "172.")):
            cors_origins.extend(
                [
                    f"http://{local_ip}:3000",
                    f"http://{local_ip}:3001",
                ]
            )
    except Exception:
        pass  # Ignore network detection errors

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 添加全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        import traceback
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Global exception: {exc}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return {"error": "Internal server error", "detail": str(exc)}

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        try:
            # 检查数据库连接
            from src.api.db import get_db

            next(get_db())
            return {"status": "healthy", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    # 调试端点 - 帮助诊断认证问题
    @app.get("/api/debug/auth")
    async def debug_auth(request):
        """调试认证问题 - 显示请求头信息"""
        headers = dict(request.headers)
        return {
            "message": "Auth debug info",
            "headers": headers,
            "cors_origins": cors_origins,
            "authorization_header": headers.get("authorization", "NOT_FOUND"),
            "user_agent": headers.get("user-agent", "NOT_FOUND"),
            "origin": headers.get("origin", "NOT_FOUND"),
            "referer": headers.get("referer", "NOT_FOUND"),
        }

    class ChatRequest(BaseModel):
        message: str
        session_id: str | None = None
        agent_type: str = (
            "general"  # Agent类型：general, process, equipment, market, quality
        )
        user_role: str | None = (
            None  # 用户角色：ADMIN, TECHNICIAN, MANAGER, PURCHASER等
        )

    class ChatResponse(BaseModel):
        response: str
        reasoning_steps: list[dict] | None = None
        fallback_mode: bool = False  # 是否使用了降级模式（RAG超时）
        intent_skip_rag: bool = False  # 是否因意图判断跳过RAG
        intent_reason: str | None = None  # 意图判断理由
        domain_check_failed: bool = False  # 是否领域检查失败（需要转发）
        suggested_agent: str | None = None  # 建议咨询的 Agent ID

    class FileUploadResponse(BaseModel):
        success: bool
        message: str
        file_id: str | None = None
        file_name: str | None = None
        file_size: int | None = None
        content_type: str | None = None
        chunks: list[dict] | None = None
        raw_path: str | None = None
        processed_path: str | None = None

    # Mount auth routes
    try:
        from src.api.auth import router as auth_router

        app.include_router(auth_router)
        print(f"✅ Auth routes mounted at {auth_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount auth routes: {e}")

    # Mount admin routes
    try:
        from src.api.admin import router as admin_router

        app.include_router(admin_router)
        print(f"✅ Admin routes mounted at {admin_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount admin routes: {e}")

    # Mount prompt management routes
    try:
        from src.prompt_management.router import router as prompt_router

        app.include_router(prompt_router)
        print(f"✅ Prompt management routes mounted at {prompt_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount prompt management routes: {e}")

    # Mount preset questions routes
    try:
        from src.api.preset_questions import router as preset_questions_router

        app.include_router(preset_questions_router)
        print(f"✅ Preset questions routes mounted at {preset_questions_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount preset questions routes: {e}")

    # Mount knowledge graph routes
    try:
        from src.knowledge_graph.api import router as knowledge_graph_router

        app.include_router(knowledge_graph_router)
        print(f"✅ Knowledge graph routes mounted at {knowledge_graph_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount knowledge graph routes: {e}")

    # Mount market analysis routes
    try:
        from src.api.market import router as market_router

        app.include_router(market_router)
        print(f"✅ Market analysis routes mounted at {market_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount market analysis routes: {e}")

    # Mount equipment monitoring routes
    try:
        from src.api.equipment import router as equipment_router

        app.include_router(equipment_router)
        print(f"✅ Equipment monitoring routes mounted at {equipment_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount equipment monitoring routes: {e}")

    # Mount workflow management routes
    try:
        from src.api.workflow import router as workflow_router

        app.include_router(workflow_router)
        print(f"✅ Workflow management routes mounted at {workflow_router.prefix}")
    except Exception as e:
        print(f"❌ Failed to mount workflow management routes: {e}")

    _app_agents: dict[str, RAGAgent] = {}

    def _get_agent(
        session_id: str | None,
        agent_type: str = "general",
        user_role: str | None = None,
    ) -> RAGAgent:
        """
        获取或创建 Agent 实例，支持根据 agent_type 加载对应的 system_prompt

        Args:
            session_id: 会话ID
            agent_type: Agent类型（general, process, equipment, market, quality）
            user_role: 用户角色（ADMIN, TECHNICIAN, MANAGER等）
        """
        # 为不同的 agent_type 创建独立的 key
        key = f"{session_id or 'default'}_{agent_type}"
        if key in _app_agents:
            return _app_agents[key]

        # 从数据库加载对应的 system_prompt
        system_prompt = None
        try:
            from src.api.db import SessionLocal
            from src.prompt_management.service import PromptService

            db = SessionLocal()
            try:
                prompt_service = PromptService(db)

                # 尝试获取该 agent_type 的活跃 Agent
                agents = prompt_service.list_agents(
                    agent_type=agent_type, is_active=True, limit=1
                )
                if agents:
                    agent_id = agents[0].id
                    # 使用 get_agent_prompt 方法获取该 Agent 的活跃默认 prompt
                    prompt_response = prompt_service.get_agent_prompt(
                        agent_id=agent_id, language="zh-CN", use_cache=True
                    )
                    if prompt_response:
                        system_prompt = prompt_response.content
                        print(
                            f"✅ 已为 {agent_type} Agent 加载专属 Prompt (ID: {prompt_response.id}, 名称: {prompt_response.name})"
                        )
                    else:
                        print(f"⚠️ {agent_type} Agent 无活跃 Prompt，使用默认配置")
                else:
                    print(f"⚠️ 未找到 {agent_type} 类型的 Agent，使用默认配置")
            finally:
                db.close()
        except Exception as e:
            print(f"⚠️ 加载 Prompt 失败: {e}，使用默认配置")

        # Try multiple env var names for convenience
        api_key = os.environ.get("QWEN_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if api_key:
            cfg = OpenAIConfig(
                model_name=os.environ.get("LLM_MODEL", "qwen-plus"),
                api_key=api_key,
                max_tokens=10000,  # 增加token限制，支持复杂的知识图谱回答
                temperature=0.7,
            )
            llm = OpenAIClient(cfg, system_prompt=system_prompt)
        else:
            llm = EchoClient(model=os.environ.get("LLM_MODEL", "echo-ui"))

        agent = create_agent(llm, system_prompt=system_prompt)
        _app_agents[key] = agent
        return agent

    from dataclasses import is_dataclass, asdict
    from typing import Any

    def _serialize_steps(steps: list[Any] | None) -> list[dict]:
        if not steps:
            return []
        out: list[dict] = []
        for s in steps:
            # Convert dataclass instances safely; skip dataclass types
            if is_dataclass(s) and not isinstance(s, type):
                try:
                    out.append(asdict(s))
                    continue
                except Exception:
                    pass
            elif isinstance(s, dict):
                out.append(s)
                continue
            # Fallback: best-effort conversion
            try:
                out.append(dict(s))  # type: ignore[arg-type]
            except Exception:
                try:
                    out.append(getattr(s, "__dict__", {"value": str(s)}))
                except Exception:
                    out.append({"value": str(s)})
        return out

    def _process_text_file(content: bytes, file_name: str) -> list[dict]:
        """处理文本文件，进行分块"""
        text = content.decode("utf-8", errors="ignore")
        # 简单的分块策略：按段落分割，每块最多1000字符
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > 1000 and current_chunk:
                chunks.append(
                    {
                        "content": current_chunk.strip(),
                        "type": "text",
                        "length": len(current_chunk),
                    }
                )
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            chunks.append(
                {
                    "content": current_chunk.strip(),
                    "type": "text",
                    "length": len(current_chunk),
                }
            )

        return chunks

    def _process_file_content(file: UploadFile, content: bytes) -> list[dict]:
        """根据文件类型处理内容"""
        content_type = file.content_type or ""

        if content_type.startswith("text/") or file.filename.endswith(
            (".txt", ".md", ".py", ".js", ".ts", ".json")
        ):
            return _process_text_file(content, file.filename)
        else:
            # 对于非文本文件，返回基本信息
            return [
                {
                    "content": f"文件类型: {content_type}\n文件名: {file.filename}\n大小: {len(content)} 字节",
                    "type": "file_info",
                    "length": len(content),
                }
            ]

    @app.post("/api/upload", response_model=FileUploadResponse)
    async def upload_file(
        file: UploadFile = File(...),
        upload_type: str = "user_upload",  # "knowledge_base" 或 "user_upload"
        current_user: User = Depends(_get_current_user),  # 添加用户认证
    ):
        """上传文件到知识库或用户临时目录
        
        Args:
            file: 上传的文件
            upload_type: 上传类型
                - "knowledge_base": 上传到知识库（仅管理员/经理，持久化）
                - "user_upload": 上传到用户临时目录（所有用户，默认）
            current_user: 当前登录用户
        
        Returns:
            FileUploadResponse with file details
        """
        try:
            # 验证 upload_type 参数
            if upload_type not in ("knowledge_base", "user_upload"):
                return FileUploadResponse(
                    success=False,
                    message=f"无效的 upload_type: {upload_type}，必须是 'knowledge_base' 或 'user_upload'",
                )

            # 权限检查：只有管理员和经理可以上传到知识库
            if upload_type == "knowledge_base":
                if current_user.role not in ("ADMIN", "MANAGER"):
                    return FileUploadResponse(
                        success=False,
                        message="只有管理员和经理可以上传文件到知识库，普通用户只能上传到个人临时目录",
                    )
                print(f"👤 {current_user.username} (角色: {current_user.role}) 上传文件到知识库")

            # 读取文件内容
            content = await file.read()
            if not content:
                return FileUploadResponse(success=False, message="空文件，无法处理")

            # 生成文件ID（基于内容哈希）
            file_hash = hashlib.md5(content).hexdigest()
            safe_name = _safe_filename(file.filename or "upload")
            file_id = f"{file_hash}_{safe_name}"

            # 根据 upload_type 选择保存目录
            if upload_type == "knowledge_base":
                raw_dir = KB_RAW_DIR
                processed_dir = KB_PROCESSED_DIR
            else:
                raw_dir = USER_RAW_DIR
                processed_dir = USER_PROCESSED_DIR

            # 保存到对应的 raw 目录
            raw_path = raw_dir / file_id
            try:
                with raw_path.open("wb") as f:
                    f.write(content)
                print(f"📁 文件保存到: {raw_path}")
            except Exception as e:
                return FileUploadResponse(success=False, message=f"保存文件失败: {e}")

            # 处理并索引
            preview_chunks = process_and_index_file(
                raw_path,
                file_id=file_id,
                orig_name=file.filename,
                content_type=file.content_type,
                upload_type=upload_type,
                processed_dir=processed_dir,
            )

            # 写一个轻量处理完成标记文件（可选）
            try:
                (processed_dir / f"{file_id}.done").write_text("ok", encoding="utf-8")
            except Exception:
                pass

            # 根据类型设置提示信息
            location = "知识库" if upload_type == "knowledge_base" else "用户上传目录"
            message = f"文件上传成功（{location}），已处理为 {len(preview_chunks)} 个块"

            return FileUploadResponse(
                success=True,
                message=message,
                file_id=file_id,
                file_name=file.filename,
                file_size=len(content),
                content_type=file.content_type,
                chunks=preview_chunks,
                raw_path=str(raw_path),
                processed_path=str(processed_dir / f"{file_id}.chunks.jsonl"),
            )
        except Exception as e:
            return FileUploadResponse(success=False, message=f"文件处理失败: {str(e)}")

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        import asyncio
        import time
        from config.settings import get_settings
        from src.intent_classifier import get_intent_classifier

        # 根据 agent_type 和 user_role 获取对应的 Agent
        agent = _get_agent(req.session_id, req.agent_type, req.user_role)
        fallback_mode = False

        # 从配置获取RAG超时时间
        settings = get_settings()
        rag_timeout = settings.rag_timeout_seconds

        # 🚀 智能判断是否需要 RAG
        classifier = get_intent_classifier()
        should_use_rag, intent_reason = classifier.should_use_rag(req.message)
        
        if not should_use_rag:
            # 简单问候/闲聊，直接使用 LLM（不检索）
            print(f"💬 跳过RAG检索: {intent_reason}")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, agent.run, req.message)
            return ChatResponse(
                response=result.response,
                reasoning_steps=_serialize_steps(result.reasoning_steps),
                fallback_mode=False,
                intent_skip_rag=True,  # 标记：意图判断跳过RAG
                intent_reason=intent_reason,
            )
        
        # 需要 RAG 检索
        print(f"🔍 使用RAG检索: {intent_reason}")

        async def rag_with_timeout():
            """执行RAG检索和LLM调用，带超时控制"""
            # Retrieval: search vector store for relevant chunks
            retrieved_context = ""
            vocabulary_context = ""
            try:
                # 1. 查询增强：识别专业词汇
                enhancer = get_query_enhancer()
                enhanced = enhancer.enhance(
                    req.message, add_synonyms=True, add_related=True
                )

                # 如果识别到专业词汇，使用增强后的查询
                query_for_search = (
                    enhanced.enhanced_query
                    if enhanced.identified_terms
                    else req.message
                )
                vocabulary_context = enhanced.vocabulary_context  # 保存专业词汇上下文

                if enhanced.identified_terms:
                    print(
                        f"🔍 识别到专业词汇: {[t['term'] for t in enhanced.identified_terms]}"
                    )
                    print(f"📝 增强查询: {query_for_search}")

                # 2. 文本预处理和向量检索（优先检索策略）
                pre = get_preprocessor()
                cleaned_query = pre.clean_text(query_for_search)
                if cleaned_query:
                    emb = get_embedder()
                    vec = emb.encode([cleaned_query], normalize=True)[0]
                    # 使用双向量存储管理器（优先搜索用户上传文件）
                    dual_store = get_dual_vector_store()
                    hits = dual_store.search(vec, top_k=5, include_metadata=True, nprobe=10)

                    # Load chunk contents from processed JSONL if available
                    contexts: list[str] = []
                    for h in hits:
                        file_id = h.get("file_id")
                        chunk_id = h.get("chunk_id")
                        file_path = h.get("file")

                        # 兼容旧metadata格式：从file字段推断完整内容
                        if file_id is None and file_path:
                            try:
                                # 尝试从processed目录读取对应的txt文件（旧格式）
                                file_path_obj = Path(file_path)
                                if (
                                    file_path_obj.exists()
                                    and file_path_obj.suffix == ".txt"
                                ):
                                    with file_path_obj.open("r", encoding="utf-8") as f:
                                        full_text = f.read()
                                    # 简单分块：按chunk_size=1000字符分割
                                    chunk_size = 1000
                                    if chunk_id is not None:
                                        start = chunk_id * chunk_size
                                        end = start + chunk_size
                                        chunk_content = full_text[start:end]
                                        if chunk_content.strip():
                                            contexts.append(chunk_content.strip())
                                        continue
                            except Exception:
                                pass

                        # 新格式：使用file_id查找chunks文件
                        if file_id is None or chunk_id is None:
                            # Fallback to preview（只有前50字符）
                            preview = h.get("preview")
                            if isinstance(preview, str) and preview:
                                contexts.append(preview)
                            continue

                        # 根据 upload_type 确定从哪个目录读取
                        upload_type = h.get("upload_type", "user_upload")
                        if upload_type == "knowledge_base":
                            processed_dir = KB_PROCESSED_DIR
                        else:
                            processed_dir = USER_PROCESSED_DIR

                        jsonl_path = processed_dir / f"{file_id}.chunks.jsonl"
                        try:
                            if jsonl_path.exists():
                                # Read only the needed line(s)
                                with jsonl_path.open("r", encoding="utf-8") as f:
                                    for line in f:
                                        line = line.strip()
                                        if not line:
                                            continue
                                        import json as _json

                                        try:
                                            rec = _json.loads(line)
                                        except Exception:
                                            continue
                                        if rec.get("chunk_id") == chunk_id:
                                            content = rec.get("content")
                                            if isinstance(content, str) and content:
                                                contexts.append(content)
                                            break
                            else:
                                # 尝试从旧的 PROCESSED_DIR 读取（向后兼容）
                                old_jsonl_path = PROCESSED_DIR / f"{file_id}.chunks.jsonl"
                                if old_jsonl_path.exists():
                                    with old_jsonl_path.open("r", encoding="utf-8") as f:
                                        for line in f:
                                            line = line.strip()
                                            if not line:
                                                continue
                                            import json as _json

                                            try:
                                                rec = _json.loads(line)
                                            except Exception:
                                                continue
                                            if rec.get("chunk_id") == chunk_id:
                                                content = rec.get("content")
                                                if isinstance(content, str) and content:
                                                    contexts.append(content)
                                                break
                                else:
                                    # As a fallback, read from raw file and ignore precise chunking
                                    preview = h.get("preview")
                                    if isinstance(preview, str) and preview:
                                        contexts.append(preview)
                        except Exception:
                            # Do not block chat on retrieval errors
                            prev = h.get("preview")
                            if isinstance(prev, str) and prev:
                                contexts.append(prev)

                    if contexts:
                        # Deduplicate and limit length
                        seen = set()
                        uniq: list[str] = []
                        for c in contexts:
                            key = c[:80]
                            if key in seen:
                                continue
                            seen.add(key)
                            uniq.append(c)
                        # Build context section
                        retrieved_context = "\n\n".join(uniq[:5])
            except Exception:
                # Retrieval is best-effort; continue without context on errors
                retrieved_context = ""

            # If we have retrieved context or vocabulary context, prepend them to the user's message
            user_message = req.message
            context_parts = []

            # 添加专业词汇上下文（优先级最高）
            if vocabulary_context:
                context_parts.append(vocabulary_context)

            # 添加检索上下文
            if retrieved_context:
                context_parts.append("【检索上下文】\n" + retrieved_context)

            if context_parts:
                user_message = (
                    "请结合以下信息回答问题。\n\n"
                    + "\n\n".join(context_parts)
                    + "\n\n【用户问题】\n"
                    + req.message
                )

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, agent.run, user_message)
            return result

        try:
            # 尝试在超时时间内完成RAG检索和LLM调用
            start_time = time.time()
            result = await asyncio.wait_for(rag_with_timeout(), timeout=rag_timeout)
            elapsed = time.time() - start_time
            print(f"✅ RAG completed in {elapsed:.2f}s")

        except asyncio.TimeoutError:
            # 超时后降级：直接使用LLM，不带RAG上下文
            print(f"⚠️ RAG timeout after {rag_timeout}s, falling back to direct LLM")
            fallback_mode = True

            # 直接调用LLM，不带检索上下文
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, agent.run, req.message)

        except Exception as e:
            # 其他错误也降级
            print(f"❌ RAG error: {e}, falling back to direct LLM")
            fallback_mode = True
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, agent.run, req.message)

        steps = _serialize_steps(result.get("reasoning_steps", []))
        response_text = result.get("response", "")
        
        # 检测是否为领域转发建议
        is_domain_redirect = "🔄 **领域转发建议**" in response_text
        suggested_agent_id = None
        
        if is_domain_redirect:
            # 尝试从响应中提取建议的 Agent（简单匹配）
            agent_mapping = {
                "通用助手": "general",
                "工艺专家": "process",
                "设备诊断": "equipment",
                "市场分析师": "market",
                "质量顾问": "quality",
                "节能专家": "environment",
            }
            for agent_name, agent_id in agent_mapping.items():
                if f"**{agent_name}**" in response_text:
                    suggested_agent_id = agent_id
                    break
        
        return ChatResponse(
            response=response_text,
            reasoning_steps=steps,
            fallback_mode=fallback_mode,
            intent_skip_rag=False,  # 使用了 RAG（或降级）
            intent_reason=intent_reason if not fallback_mode else None,
            domain_check_failed=is_domain_redirect,
            suggested_agent=suggested_agent_id,
        )

    @app.post("/api/chat/stream")
    async def chat_stream(req: ChatRequest):
        """流式聊天端点 - 使用 SSE 返回流式响应"""
        import asyncio
        import time
        import json as json_lib
        from fastapi.responses import StreamingResponse
        from config.settings import get_settings

        async def generate():
            try:
                # 根据 agent_type 和 user_role 获取对应的 Agent
                agent = _get_agent(req.session_id, req.agent_type, req.user_role)
                fallback_mode = False

                # 从配置获取RAG超时时间
                settings = get_settings()
                rag_timeout = settings.rag_timeout_seconds

                # 1. 先执行 RAG 检索（带超时）
                retrieved_context = ""
                vocabulary_context = ""
                sources = []

                async def rag_retrieval():
                    nonlocal retrieved_context, vocabulary_context, sources
                    try:
                        # 1.1 查询增强：识别专业词汇
                        enhancer = get_query_enhancer()
                        enhanced = enhancer.enhance(
                            req.message, add_synonyms=True, add_related=True
                        )

                        # 如果识别到专业词汇，使用增强后的查询
                        query_for_search = (
                            enhanced.enhanced_query
                            if enhanced.identified_terms
                            else req.message
                        )
                        vocabulary_context = enhanced.vocabulary_context

                        if enhanced.identified_terms:
                            print(
                                f"🔍 [Stream] 识别到专业词汇: {[t['term'] for t in enhanced.identified_terms]}"
                            )

                        # 1.2 文本预处理和向量检索（优先检索策略）
                        pre = get_preprocessor()
                        cleaned_query = pre.clean_text(query_for_search)
                        if cleaned_query:
                            emb = get_embedder()
                            vec = emb.encode([cleaned_query], normalize=True)[0]
                            # 使用双向量存储管理器（优先搜索用户上传文件）
                            dual_store = get_dual_vector_store()
                            hits = dual_store.search(vec, top_k=5, include_metadata=True, nprobe=10)

                            contexts = []
                            for h in hits:
                                file_id = h.get("file_id")
                                chunk_id = h.get("chunk_id")
                                file_name = h.get("file", "unknown")
                                file_path = h.get("file")
                                score = h.get("score", 0.0)

                                # 兼容旧metadata格式：从file字段推断完整内容
                                if file_id is None and file_path:
                                    try:
                                        file_path_obj = Path(file_path)
                                        if (
                                            file_path_obj.exists()
                                            and file_path_obj.suffix == ".txt"
                                        ):
                                            with file_path_obj.open(
                                                "r", encoding="utf-8"
                                            ) as f:
                                                full_text = f.read()
                                            chunk_size = 1000
                                            if chunk_id is not None:
                                                start = chunk_id * chunk_size
                                                end = start + chunk_size
                                                chunk_content = full_text[start:end]
                                                if chunk_content.strip():
                                                    contexts.append(
                                                        chunk_content.strip()
                                                    )
                                                    sources.append(
                                                        {
                                                            "file": file_name,
                                                            "chunk_id": chunk_id,
                                                            "score": score,
                                                            "preview": chunk_content[
                                                                :200
                                                            ],
                                                        }
                                                    )
                                                continue
                                    except Exception:
                                        pass

                                # 尝试加载完整内容（支持不同目录）
                                content = ""
                                if file_id is not None and chunk_id is not None:
                                    # 根据 upload_type 确定从哪个目录读取
                                    upload_type = h.get("upload_type", "user_upload")
                                    if upload_type == "knowledge_base":
                                        processed_dir = KB_PROCESSED_DIR
                                    else:
                                        processed_dir = USER_PROCESSED_DIR

                                    jsonl_path = processed_dir / f"{file_id}.chunks.jsonl"
                                    try:
                                        if jsonl_path.exists():
                                            with jsonl_path.open(
                                                "r", encoding="utf-8"
                                            ) as f:
                                                for line in f:
                                                    line = line.strip()
                                                    if not line:
                                                        continue
                                                    try:
                                                        rec = json_lib.loads(line)
                                                    except Exception:
                                                        continue
                                                    if rec.get("chunk_id") == chunk_id:
                                                        content = rec.get("content", "")
                                                        break
                                        else:
                                            # 尝试从旧的 PROCESSED_DIR 读取（向后兼容）
                                            old_jsonl_path = PROCESSED_DIR / f"{file_id}.chunks.jsonl"
                                            if old_jsonl_path.exists():
                                                with old_jsonl_path.open(
                                                    "r", encoding="utf-8"
                                                ) as f:
                                                    for line in f:
                                                        line = line.strip()
                                                        if not line:
                                                            continue
                                                        try:
                                                            rec = json_lib.loads(line)
                                                        except Exception:
                                                            continue
                                                        if rec.get("chunk_id") == chunk_id:
                                                            content = rec.get("content", "")
                                                            break
                                    except Exception:
                                        pass

                                if not content:
                                    content = h.get("preview", "")

                                if content:
                                    contexts.append(content)
                                    sources.append(
                                        {
                                            "file_id": file_id or "",
                                            "file_name": file_name,
                                            "chunk_id": chunk_id or 0,
                                            "content": content[:200],  # 预览前200字符
                                            "relevance_score": float(score),
                                        }
                                    )

                            if contexts:
                                seen = set()
                                uniq = []
                                for c in contexts:
                                    key = c[:80]
                                    if key not in seen:
                                        seen.add(key)
                                        uniq.append(c)
                                retrieved_context = "\n\n".join(uniq[:5])
                    except Exception as e:
                        print(f"⚠️ Retrieval error: {e}")

                try:
                    # 尝试在超时时间内完成检索
                    await asyncio.wait_for(rag_retrieval(), timeout=rag_timeout)
                except asyncio.TimeoutError:
                    print(f"⚠️ RAG retrieval timeout after {rag_timeout}s")
                    fallback_mode = True

                # 2. 发送来源信息
                if sources:
                    yield f"data: {json_lib.dumps({'type': 'sources', 'sources': sources})}\n\n"

                # 3. 构建用户消息（包含专业词汇和检索上下文）
                user_message = req.message
                if (vocabulary_context or retrieved_context) and not fallback_mode:
                    context_parts = []

                    # 添加专业词汇上下文（优先级最高）
                    if vocabulary_context:
                        context_parts.append(vocabulary_context)

                    # 添加检索上下文
                    if retrieved_context:
                        context_parts.append("【检索上下文】\n" + retrieved_context)

                    if context_parts:
                        user_message = (
                            "请结合以下信息回答问题。\n\n"
                            + "\n\n".join(context_parts)
                            + "\n\n【用户问题】\n"
                            + req.message
                        )

                # 4. 执行 Agent 推理（同步调用，在线程池中执行）
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, agent.run, user_message)

                # 5. 发送推理步骤
                reasoning_steps = _serialize_steps(result.get("reasoning_steps", []))
                if reasoning_steps:
                    yield f"data: {json_lib.dumps({'type': 'reasoning', 'steps': reasoning_steps})}\n\n"

                # 6. 流式发送响应内容
                response_text = result.get("response", "")
                # 模拟流式输出 - 分批发送
                chunk_size = 20  # 每次发送20个字符
                for i in range(0, len(response_text), chunk_size):
                    chunk = response_text[i : i + chunk_size]
                    yield f"data: {json_lib.dumps({'type': 'content', 'delta': chunk})}\n\n"
                    await asyncio.sleep(0.05)  # 模拟打字效果

                # 7. 发送完成标记
                yield f"data: {json_lib.dumps({'type': 'done', 'fallback_mode': fallback_mode})}\n\n"
                yield "data: [DONE]\n\n"

            except Exception as e:
                print(f"❌ Stream error: {e}")
                error_msg = json_lib.dumps(
                    {"type": "error", "message": f"生成响应时出错: {str(e)}"}
                )
                yield f"data: {error_msg}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            },
        )

    # Simple agents endpoint for testing frontend integration
    @app.get("/api/agents")
    def get_agents():
        """获取可用的Agent列表 - 简化版本用于测试"""
        return [
            {
                "id": 1,
                "name": "RAG智能助手",
                "displayName": "RAG智能助手",
                "agentType": "rag_agent",
                "description": "基于检索增强生成的智能问答助手，能够结合文档内容回答问题",
                "capabilities": ["文档检索", "智能问答", "上下文理解"],
                "isActive": True,
                "iconComponent": "MessageSquare",
                "colorClass": "text-blue-600",
                "useCases": [
                    "根据上传的文档回答问题",
                    "提供基于知识库的建议",
                    "分析文档内容并总结要点",
                ],
            },
            {
                "id": 2,
                "name": "钢铁生产顾问",
                "displayName": "钢铁生产顾问",
                "agentType": "production_agent",
                "description": "专业的钢铁生产工艺顾问，提供生产优化建议",
                "capabilities": ["生产工艺分析", "质量控制", "成本优化"],
                "isActive": True,
                "iconComponent": "Factory",
                "colorClass": "text-orange-600",
                "useCases": ["分析生产工艺参数", "提供质量改进建议", "优化生产成本"],
            },
            {
                "id": 3,
                "name": "市场分析师",
                "displayName": "市场分析师",
                "agentType": "market_agent",
                "description": "钢铁市场趋势分析和价格预测专家",
                "capabilities": ["市场分析", "价格预测", "趋势识别"],
                "isActive": True,
                "iconComponent": "TrendingUp",
                "colorClass": "text-green-600",
                "useCases": ["分析市场价格趋势", "预测原材料价格", "提供采购建议"],
            },
        ]
except Exception:
    # FastAPI not installed or import error; CLI remains usable
    app = None  # type: ignore

# --------------------------- CLI entrypoint --------------------------- #


def main():
    """
    Main function to run the RAG_Agent system via CLI.
    """
    parser = argparse.ArgumentParser(description="RAG_Agent CLI")
    parser.add_argument(
        "--model",
        default="qwen-plus",
        help="LLM model to use (e.g., gpt-3.5-turbo, qwen-plus)",
    )
    parser.add_argument(
        "--api-base",
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        help="The base URL for the LLM API.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for the LLM. Can also be set via QWEN_API_KEY env var.",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature for LLM generation."
    )
    parser.add_argument(
        "--wrap-width", type=int, default=0, help="输出换行列宽，0 表示自动侦测。"
    )
    args = parser.parse_args()

    # Use API key from arguments or environment variable
    api_key = args.api_key or os.environ.get("QWEN_API_KEY")
    if not api_key:
        print(
            "Warning: No API key provided. Falling back to local EchoClient for offline/testing use."
        )
        # Use a local synchronous echo client so the agent remains usable without external API.
        llm_client = EchoClient(model=args.model)
    else:
        # Create model config and LLM client using the OpenAI-compatible interface
        model_config = OpenAIConfig(
            model_name=args.model,
            api_key=api_key,
            api_base=args.api_base,
            temperature=args.temperature,
            max_tokens=1500,
        )
        llm_client = OpenAIClient(config=model_config)

    # Create and configure the agent
    agent = create_agent(llm_client)
    # Derive model name from client if available
    model_name = getattr(llm_client, "model", None) or "unknown"
    print(f"🤖 {agent.name} initialized with model: {model_name}")
    print(f"   Available tools: {[tool.name for tool in agent.tools]}")

    # Interactive loop for chatting with the agent
    print("\nType 'exit' or 'quit' to end the session.")
    while True:
        query = input("\nYou: ")
        if query.lower() in ["exit", "quit", "q"]:
            break
        # Process the query through the agent's run method
        term_width = shutil.get_terminal_size(fallback=(100, 24)).columns
        wrap_width = args.wrap_width or max(
            40, term_width - 4
        )  # 留点边距，且设置一个下限
        try:
            # 在打印模型回复时使用自动换行
            response = agent.run(query)
            text = response.get("response", "")
            print(f"\n🤖 {agent.name}:\n{wrap_text(text, wrap_width)}")

            # Optional: Display the reasoning steps and tool outputs for clarity
            if "reasoning_steps" in response and response["reasoning_steps"]:
                print("\n--- Reasoning Steps ---")
                for step in response["reasoning_steps"]:
                    print(f"Thought: {step.thought}")
                    if step.tool_name:
                        print(f"Tool: {step.tool_name}, Input: {step.tool_input}")
                print("-----------------------")

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
