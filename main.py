#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main application for RAG_Agent system.
This module demonstrates how to use the RAG agent and LLM components.
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

def main():
    """
    Main function to run the RAG_Agent system.
    """
    parser = argparse.ArgumentParser(description="RAG_Agent CLI")
    # --- THIS LINE IS CHANGED ---
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
    model_name = getattr(llm_client, 'model', None) or (model_config.model_name if 'model_config' in locals() else 'unknown')
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