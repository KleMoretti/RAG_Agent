from typing import List, Optional, Dict, Any, Union
from .tools import Tool
from .reasoning import ReasoningEngine


class BaseAgent:
    """
    Base Agent class that provides common functionality for all RAG agents.

    A RAG (Retrieval-Augmented Generation) agent combines information retrieval
    with generative capabilities to provide more accurate and contextually
    relevant responses.
    """

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a new BaseAgent.

        Args:
            name: Unique identifier for the agent
            description: Optional human-readable description of the agent's purpose
        """
        self.name = name
        self.description = description
        self.tools: List[Tool] = []
        self.reasoning_engine: Optional[ReasoningEngine] = None
        self.context: Dict[str, Any] = {}  # Store contextual information for the agent

    def add_tool(self, tool: Tool) -> None:
        """
        Add a tool to the agent's toolset.

        Args:
            tool: The tool to add
        """
        # Avoid duplicate tools
        if not any(t.name == tool.name for t in self.tools):
            self.tools.append(tool)
        else:
            raise ValueError(f"Tool with name '{tool.name}' already exists")

    def remove_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the agent's toolset.

        Args:
            tool_name: Name of the tool to remove

        Returns:
            True if the tool was found and removed, False otherwise
        """
        for i, tool in enumerate(self.tools):
            if tool.name == tool_name:
                self.tools.pop(i)
                return True
        return False

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        Get a tool by its name.

        Args:
            tool_name: Name of the tool to retrieve

        Returns:
            Tool if found, None otherwise
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def set_reasoning_engine(self, engine: ReasoningEngine) -> None:
        """
        Set the reasoning engine for the agent.

        Args:
            engine: ReasoningEngine instance
        """
        self.reasoning_engine = engine

    def set_context(self, key: str, value: Any) -> None:
        """
        Set a contextual value for the agent.

        Args:
            key: Context identifier
            value: Context value
        """
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get a contextual value from the agent.

        Args:
            key: Context identifier
            default: Default value to return if key not found

        Returns:
            The context value or default if not found
        """
        return self.context.get(key, default)

    def process(self, query: str) -> Dict[str, Any]:
        """
        Process a user query using the agent's reasoning and tools.

        Args:
            query: User's input query

        Returns:
            The agent's response containing answer and reasoning

        Raises:
            ValueError: If the reasoning engine is not set
        """
        if not self.reasoning_engine:
            raise ValueError("Reasoning engine not set")

        # Generate reasoning path
        reasoning_path = self.reasoning_engine.reason(query, self.tools)

        # Execute the reasoning path
        result = self.reasoning_engine.execute(reasoning_path)

        return result

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"BaseAgent(name='{self.name}', tools={len(self.tools)})"

# -*- coding: utf-8 -*-
"""
RAGAgent implementation.
"""
from typing import Dict, Any

from .reasoning import ReasoningEngine
from ..llm import LLMClient
# -*- coding: utf-8 -*-
"""
RAGAgent implementation.
"""
from typing import Dict, Any, List

from .reasoning import ReasoningEngine
from ..llm import LLMClient

class RAGAgent:
    """
    A ReAct-style agent that uses a reasoning engine to answer queries.
    """
    def __init__(self, llm_client: LLMClient, reasoning_engine: ReasoningEngine, name: str = "RAG Agent"):
        self.name = name
        self.llm_client = llm_client
        self.reasoning_engine = reasoning_engine
        self.tools = []  # Changed from a dictionary reference to a simple list

    def add_tool(self, tool):
        """Adds a tool to the agent's reasoning engine."""
        self.reasoning_engine.add_tool(tool)
        self.tools.append(tool)  # Also add to the agent's tools list for easy access

    def run(self, query: str) -> Dict[str, Any]:
        """
        Processes a query using the reasoning engine and returns a structured response.

        Args:
            query: The user's input query.

        Returns:
            A dictionary containing the final response and the reasoning steps.
            Example:
            {
                "response": "The final answer is...",
                "reasoning_steps": [...]
            }
        """
        # The reasoning engine is expected to produce the final answer and the thought process.
        final_answer, reasoning_steps = self.reasoning_engine.run(query)

        # Structure the output as expected by main.py
        return {
            "response": final_answer,
            "reasoning_steps": reasoning_steps
        }