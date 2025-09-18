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
from src.llm import OpenAIClient, OpenAIConfig


# --- Tool Definitions ---

class SearchTool(BaseTool):
    """Simple search tool that returns mock results."""
    def __init__(self):
        super().__init__(
            name="search",
            description="Search for information on a given topic. Returns a list of titles and URLs."
        )

    def run(self, query: str) -> List[Dict[str, str]]:
        print(f"--- Running Search Tool with query: '{query}' ---")
        return [
            {"title": f"Result 1 for '{query}'", "url": "https://example.com/1"},
            {"title": f"Result 2 for '{query}'", "url": "https://example.com/2"},
        ]

class CalculatorTool(BaseTool):
    """
    A safe calculator tool that evaluates mathematical expressions.
    Supports basic arithmetic operations: +, -, *, /.
    """
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Calculate mathematical expressions. Example input: '2 + 3 * 4'"
        )
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }

    def _eval_expr(self, node):
        """Safely evaluate an AST node."""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_expr(node.left)
            right = self._eval_expr(node.right)
            return self.operators[type(node.op)](left, right)
        else:
            raise TypeError(f"Unsupported operation: {type(node)}")

    def run(self, expression: str) -> Union[float, str]:
        """Safely evaluate the mathematical expression."""
        print(f"--- Running Calculator Tool with expression: '{expression}' ---")
        try:
            # Parse the expression into an Abstract Syntax Tree (AST)
            tree = ast.parse(expression, mode='eval').body
            return self._eval_expr(tree)
        except (TypeError, KeyError, SyntaxError, ZeroDivisionError) as e:
            return f"Error: Invalid or unsupported expression. {str(e)}"

def create_agent(llm_client: OpenAIClient) -> RAGAgent:
    """
    Create and configure an agent with tools and a reasoning engine.

    Args:
        llm_client: LLM client for the reasoning engine.

    Returns:
        A configured RAGAgent.
    """
    # Create the reasoning engine with the LLM client
    reasoning_engine = ReasoningEngine()

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
    args = parser.parse_args()

    # Use API key from arguments or environment variable
    api_key = args.api_key or os.environ.get("QWEN_API_KEY")
    if not api_key:
        print("Warning: No API key provided. Set the QWEN_API_KEY environment variable or use the --api-key argument.")
        # Exit if no key is found, as the API will fail.
        return

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
    print(f"🤖 {agent.name} initialized with model: {model_config.model_name}")
    print(f"   Available tools: {[tool.name for tool in agent.tools]}")

    # Interactive loop for chatting with the agent
    print("\nType 'exit' or 'quit' to end the session.")
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit', 'q']:
            break

        try:
            # Process the query through the agent's run method
            response = agent.run(query)
            print(f"\n🤖 {agent.name}: {response['response']}")

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