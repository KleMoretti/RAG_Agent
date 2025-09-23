from abc import abstractmethod, ABC
from typing import Callable, Dict, Any, List, Optional, Union
import inspect
import functools


class Tool:
    """
    Base class for all agent tools.

    This class supports two usage patterns:
    - Function-backed tools: provide a `function` callable at init and `execute` will call it.
    - Subclass-backed tools: subclass `Tool` and implement a `run(self, input_data)` method.
    """

    def __init__(self, name: str, description: str, function: Optional[Callable] = None):
        """
        Initialize a new tool.

        Args:
            name: Unique name for the tool
            description: Human-readable description of what the tool does
            function: Optional callable implementing the tool's functionality
        """
        self.name = name
        self.description = description
        self.function = function
        if self.function is not None:
            self._validate_function()

    def _validate_function(self) -> None:
        """Validate that the function has proper signature and docstring (only for function-backed tools)."""
        if not callable(self.function):
            raise TypeError("Tool function must be callable")

        # Docstring is recommended for function-backed tools
        if not self.function.__doc__:
            raise ValueError(f"Tool '{self.name}' function must have a docstring")

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the tool with given arguments. Prefers the provided function, otherwise
        falls back to a `run` method on the instance (subclass-backed tool).
        """
        try:
            if self.function is not None:
                return self.function(*args, **kwargs)
            elif hasattr(self, 'run'):
                return getattr(self, 'run')(*args, **kwargs)
            else:
                raise TypeError("Tool has no callable `function` and no `run` method")
        except Exception:
            # Re-raise so callers can handle/log as needed
            raise

    def get_signature(self) -> Dict[str, Any]:
        """
        Get the signature of the tool function or the instance `run` method.

        Returns:
            Dict containing parameter information
        """
        target = self.function if self.function is not None else getattr(self, 'run', None)
        if target is None:
            return {"parameters": {}, "return_type": "Any"}

        sig = inspect.signature(target)
        return {
            "parameters": {
                name: {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                    "default": None if param.default == inspect.Parameter.empty else param.default,
                    "required": param.default == inspect.Parameter.empty and param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.VAR_KEYWORD
                }
                for name, param in sig.parameters.items()
            },
            "return_type": str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else "Any"
        }

    def __repr__(self) -> str:
        """String representation of the tool."""
        return f"Tool(name='{self.name}')"

# -*- coding: utf-8 -*-
"""
Collection of tools for the RAG Agent.
This file contains concrete implementations of BaseTool.
"""
import ast
import operator
from typing import Dict, List, Union

class SearchTool(Tool):
    """Simple search tool that returns mock results."""
    def __init__(self):
        super().__init__(
            name="search",
            description="Search for information on a given topic. Returns a list of titles and URLs.",
            function=None
        )

    def run(self, query: str) -> List[Dict[str, str]]:
        print(f"--- Running Search Tool with query: '{query}' ---")
        return [
            {"title": f"Result 1 for '{query}'", "url": "https://example.com/1"},
            {"title": f"Result 2 for '{query}'", "url": "https://example.com/2"},
        ]

class CalculatorTool(Tool):
    """
    A safe calculator tool that evaluates mathematical expressions.
    Supports basic arithmetic operations: +, -, *, /.
    """
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Calculate mathematical expressions. Example input: '2 + 3 * 4'",
            function=None
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
            tree = ast.parse(expression, mode='eval').body
            return self._eval_expr(tree)
        except (TypeError, KeyError, SyntaxError, ZeroDivisionError) as e:
            return f"Error: Invalid or unsupported expression. {str(e)}"

class ToolRegistry:
    """
    Registry for managing and accessing tools.
    """

    def __init__(self):
        """Initialize a new tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[str, List[str]] = {}

    def register(self, tool: Tool, categories: Optional[List[str]] = None) -> None:
        """
        Register a new tool.

        Args:
            tool: Tool instance to register
            categories: Optional list of categories to associate with the tool

        Raises:
            ValueError: If a tool with the same name already exists
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' already exists")

        self.tools[tool.name] = tool

        # Add to categories if provided
        if categories:
            for category in categories:
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(tool.name)

    def unregister(self, tool_name: str) -> bool:
        """
        Unregister a tool.

        Args:
            tool_name: Name of the tool to unregister

        Returns:
            True if the tool was found and unregistered, False otherwise
        """
        if tool_name in self.tools:
            # Remove from all categories
            for category in self.categories:
                if tool_name in self.categories[category]:
                    self.categories[category].remove(tool_name)

            # Remove from tools dict
            del self.tools[tool_name]
            return True
        return False

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Retrieve a tool by name.

        Args:
            name: Name of the tool to retrieve

        Returns:
            Tool instance or None if not found
        """
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """
        List all registered tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tools_by_category(self, category: str) -> List[Tool]:
        """
        Get all tools in a specific category.

        Args:
            category: Category name

        Returns:
            List of Tool instances in the category
        """
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]

    def list_categories(self) -> List[str]:
        """
        List all categories.

        Returns:
            List of category names
        """
        return list(self.categories.keys())

    def clear(self) -> None:
        """Clear all registered tools and categories."""
        self.tools.clear()
        self.categories.clear()

    def __repr__(self) -> str:
        """String representation of the registry."""
        return f"ToolRegistry(tools={len(self.tools)}, categories={len(self.categories)})"


def register_as_tool(registry: ToolRegistry, name: Optional[str] = None,
                     description: Optional[str] = None,
                     categories: Optional[List[str]] = None):
    """
    Decorator to register a function as a tool.

    Args:
        registry: ToolRegistry instance
        name: Optional name for the tool (defaults to function name)
        description: Optional description (defaults to function docstring)
        categories: Optional list of categories

    Returns:
        Decorator function
    """

    def decorator(func):
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"Tool {tool_name}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        tool = Tool(tool_name, tool_desc, func)
        registry.register(tool, categories)
        return wrapper

    return decorator


class BaseTool(ABC):
    """Base abstract class for all tools."""

    def __init__(self, name: str, description: str):
        """
        Initialize the base tool.

        Args:
            name: Name of the tool
            description: Description of what the tool does
        """
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """
        Execute the tool's functionality.

        Args:
            input_data: Input data for the tool

        Returns:
            Tool execution results
        """
        pass

    def get_spec(self) -> Dict[str, str]:
        """Get tool specification for the agent."""
        return {
            "name": self.name,
            "description": self.description
        }
