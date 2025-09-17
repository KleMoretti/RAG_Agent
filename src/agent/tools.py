from typing import Callable, Dict, Any, List, Optional, Union
import inspect
import functools


class Tool:
    """
    Base class for all agent tools.
    """

    def __init__(self, name: str, description: str, function: Callable):
        """
        Initialize a new tool.

        Args:
            name: Unique name for the tool
            description: Human-readable description of what the tool does
            function: The function that implements the tool's functionality
        """
        self.name = name
        self.description = description
        self.function = function
        self._validate_function()

    def _validate_function(self) -> None:
        """Validate that the function has proper signature and docstring."""
        if not callable(self.function):
            raise TypeError("Tool function must be callable")

        if not self.function.__doc__:
            raise ValueError(f"Tool '{self.name}' function must have a docstring")

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the tool with given arguments.

        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call

        Raises:
            Exception: Any exception raised by the underlying function
        """
        try:
            return self.function(*args, **kwargs)
        except Exception as e:
            # You might want to add logging here
            raise

    def get_signature(self) -> Dict[str, Any]:
        """
        Get the signature of the tool function.

        Returns:
            Dict containing parameter information
        """
        sig = inspect.signature(self.function)
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