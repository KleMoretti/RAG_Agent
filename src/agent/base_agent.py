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

# -*- coding: utf-8 -*-
from typing import Dict, Any, List, Optional
from .tools import Tool
from .reasoning import ReasoningEngine
from ..llm import LLMClient
from .memory import ConversationMemory

class RAGAgent:
    """
    A ReAct-style agent that uses a reasoning engine to answer queries.
    """

    def __init__(self, llm_client: LLMClient, reasoning_engine: ReasoningEngine, name: str = "RAG Agent"):
        self.name = name
        self.llm_client = llm_client
        self.reasoning_engine = reasoning_engine
        # Wire LLM into reasoning engine if not already
        if getattr(self.reasoning_engine, "model", None) is None:
            self.reasoning_engine.model = self.llm_client

        self.memory = ConversationMemory(max_turns=50)
        self._tools: List[Tool] = []

    @property
    def tools(self) -> List[Tool]:
        return self._tools

    def add_tool(self, tool: Tool) -> None:
        # Avoid duplicate tools
        if not any(t.name == tool.name for t in self._tools):
            self._tools.append(tool)
            # Optional: also register into reasoning engine if it tracks tools
            if hasattr(self.reasoning_engine, "add_tool"):
                self.reasoning_engine.add_tool(tool)
        else:
            raise ValueError(f"Tool with name '{tool.name}' already exists")

    def reset_memory(self) -> None:
        self.memory.clear()

    # --- meta question detectors ---
    def _is_prev_question_query(self, text: str) -> bool:
        key_phrases = [
            "上一个问题是什么", "上一个问题是啥", "上个问题是什么", "上个问题是啥",
            "刚才问了什么", "上一题是什么", "上一问是什么",
            "what was the previous question", "previous question",
        ]
        return any(k in text.lower() for k in key_phrases)

    def _is_first_question_query(self, text: str) -> bool:
        key_phrases = [
            "第一个问题是什么", "第一问是什么", "最开始的问题是什么",
            "first question", "what was the first question",
        ]
        return any(k in text.lower() for k in key_phrases)

    def run(self, query: str) -> Dict[str, Any]:
        """
        Processes a query and returns {"response": str, "reasoning_steps": [...]}
        """
        # Handle meta-questions directly from memory (before adding current user input)
        if self._is_prev_question_query(query):
            last_q = self.memory.last_user_question()
            answer = "还没有上一个问题。" if not last_q else f"上一个问题是：{last_q}"
            # Record this turn
            self.memory.add_user(query)
            self.memory.add_assistant(answer)
            return {"response": answer, "reasoning_steps": []}

        if self._is_first_question_query(query):
            first_q = self.memory.first_user_question()
            answer = "还没有记录到任何问题。" if not first_q else f"第一个问题是：{first_q}"
            # Record this turn
            self.memory.add_user(query)
            self.memory.add_assistant(answer)
            return {"response": answer, "reasoning_steps": []}

        # Normal flow: keep history, then reason with LLM
        self.memory.add_user(query)

        # Let the reasoning engine build a prompt with recent history
        final_answer, reasoning_steps = self.reasoning_engine.run(
            query=query,
            chat_history=self.memory.as_messages(max_turns=10),  # recent 10 turns
        )

        # Record assistant's answer to memory
        self.memory.add_assistant(final_answer)

        return {
            "response": final_answer,
            "reasoning_steps": reasoning_steps
        }