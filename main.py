#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application for RAG_Agent system.
This module demonstrates how to use the RAG agent and LLM components.
Also exposes a FastAPI app at /api/chat for frontend integration.
"""

import os
import argparse
import ast
import operator
from typing import Dict, List, Union

# Import components from our source folder
from src.agent import RAGAgent
from src.agent.tools import BaseTool
from src.agent.reasoning import ReasoningEngine
from src.llm import LLMClient, OpenAIClient, OpenAIConfig, EchoClient

# --- Tool Definitions ---
from src.agent.tools import SearchTool, CalculatorTool, BaseTool
from dotenv import load_dotenv
load_dotenv()

def create_agent(llm_client: LLMClient) -> RAGAgent:
    """
    Create and configure an agent with tools and a reasoning engine.

    Args:
        llm_client: LLM client for the reasoning engine.

    Returns:
        A configured RAGAgent.
    """
    # Create the reasoning engine with the LLM client
    reasoning_engine = ReasoningEngine(model=llm_client)

    # Create the RAG agent
    agent = RAGAgent(
        llm_client=llm_client,
        reasoning_engine=reasoning_engine,
        name="RAG Assistant"
    )

    # Add tools to the agent
    agent.add_tool(SearchTool())
    agent.add_tool(CalculatorTool())

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
    from fastapi import FastAPI, UploadFile, File, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import tempfile
    import os
    from pathlib import Path
    import mimetypes
    import hashlib

    app = FastAPI(title="RAG Agent API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "*"],  # dev convenience; tighten in prod
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ChatRequest(BaseModel):
        message: str
        session_id: str | None = None

    class ChatResponse(BaseModel):
        response: str
        reasoning_steps: list[dict] | None = None

    class FileUploadResponse(BaseModel):
        success: bool
        message: str
        file_id: str | None = None
        file_name: str | None = None
        file_size: int | None = None
        content_type: str | None = None
        chunks: list[dict] | None = None

    _app_agents: dict[str, RAGAgent] = {}

    def _get_agent(session_id: str | None) -> RAGAgent:
        key = session_id or "default"
        if key in _app_agents:
            return _app_agents[key]
        api_key = os.environ.get("QWEN_API_KEY")
        if api_key:
            cfg = OpenAIConfig(model_name=os.environ.get("LLM_MODEL", "qwen-plus"), api_key=api_key)
            llm = OpenAIClient(cfg)
        else:
            llm = EchoClient(model=os.environ.get("LLM_MODEL", "echo-ui"))
        agent = create_agent(llm)
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
        text = content.decode('utf-8', errors='ignore')
        # 简单的分块策略：按段落分割，每块最多1000字符
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > 1000 and current_chunk:
                chunks.append({
                    "content": current_chunk.strip(),
                    "type": "text",
                    "length": len(current_chunk)
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "type": "text", 
                "length": len(current_chunk)
            })
        
        return chunks

    def _process_file_content(file: UploadFile, content: bytes) -> list[dict]:
        """根据文件类型处理内容"""
        content_type = file.content_type or ""
        
        if content_type.startswith('text/') or file.filename.endswith(('.txt', '.md', '.py', '.js', '.ts', '.json')):
            return _process_text_file(content, file.filename)
        else:
            # 对于非文本文件，返回基本信息
            return [{
                "content": f"文件类型: {content_type}\n文件名: {file.filename}\n大小: {len(content)} 字节",
                "type": "file_info",
                "length": len(content)
            }]

    @app.post("/api/upload", response_model=FileUploadResponse)
    async def upload_file(file: UploadFile = File(...)):
        """上传文件并处理内容"""
        try:
            # 读取文件内容
            content = await file.read()
            
            # 生成文件ID（基于内容哈希）
            file_hash = hashlib.md5(content).hexdigest()
            file_id = f"{file_hash}_{file.filename}"
            
            # 处理文件内容
            chunks = _process_file_content(file, content)
            
            return FileUploadResponse(
                success=True,
                message=f"文件上传成功，已处理为 {len(chunks)} 个块",
                file_id=file_id,
                file_name=file.filename,
                file_size=len(content),
                content_type=file.content_type,
                chunks=chunks
            )
            
        except Exception as e:
            return FileUploadResponse(
                success=False,
                message=f"文件处理失败: {str(e)}"
            )

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(req: ChatRequest):
        agent = _get_agent(req.session_id)
        result = agent.run(req.message)
        steps = _serialize_steps(result.get("reasoning_steps", []))
        return {
            "response": result.get("response", ""),
            "reasoning_steps": steps,
        }
except Exception:
    # FastAPI not installed or import error; CLI remains usable
    app = None  # type: ignore

# --------------------------- CLI entrypoint --------------------------- #

def main():
    """
    Main function to run the RAG_Agent system via CLI.
    """
    parser = argparse.ArgumentParser(description="RAG_Agent CLI")
    parser.add_argument("--model", default="qwen-plus", help="LLM model to use (e.g., gpt-3.5-turbo, qwen-plus)")
    parser.add_argument("--api-base", default="https://dashscope.aliyuncs.com/compatible-mode/v1", help="The base URL for the LLM API.")
    parser.add_argument("--api-key", default=None, help="API key for the LLM. Can also be set via QWEN_API_KEY env var.")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for LLM generation.")
    parser.add_argument("--wrap-width", type=int, default=0, help="输出换行列宽，0 表示自动侦测。")
    args = parser.parse_args()

    # Use API key from arguments or environment variable
    api_key = args.api_key or os.environ.get("QWEN_API_KEY")
    if not api_key:
        print("Warning: No API key provided. Falling back to local EchoClient for offline/testing use.")
        # Use a local synchronous echo client so the agent remains usable without external API.
        llm_client = EchoClient(model=args.model)
    else:
        # Create model config and LLM client using the OpenAI-compatible interface
        model_config = OpenAIConfig(
            model_name=args.model,
            api_key=api_key,
            api_base=args.api_base,
            temperature=args.temperature,
            max_tokens=1500
        )
        llm_client = OpenAIClient(config=model_config)

    # Create and configure the agent
    agent = create_agent(llm_client)
    # Derive model name from client if available
    model_name = getattr(llm_client, 'model', None) or 'unknown'
    print(f"🤖 {agent.name} initialized with model: {model_name}")
    print(f"   Available tools: {[tool.name for tool in agent.tools]}")

    # Interactive loop for chatting with the agent
    print("\nType 'exit' or 'quit' to end the session.")
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit', 'q']:
            break
        # Process the query through the agent's run method
        term_width = shutil.get_terminal_size(fallback=(100, 24)).columns
        wrap_width = args.wrap_width or max(40, term_width - 4)  # 留点边距，且设置一个下限
        try:
            # 在打印模型回复时使用自动换行
            response = agent.run(query)
            text = response.get("response", "")
            print(f"\n🤖 {agent.name}:\n{wrap_text(text, wrap_width)}")

            # Optional: Display the reasoning steps and tool outputs for clarity
            if 'reasoning_steps' in response and response['reasoning_steps']:
                print("\n--- Reasoning Steps ---")
                for step in response['reasoning_steps']:
                    print(f"Thought: {step.thought}")
                    if step.tool_name:
                        print(f"Tool: {step.tool_name}, Input: {step.tool_input}")
                print("-----------------------")

        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    print("\nGoodbye!")

if __name__ == "__main__":
    main()
