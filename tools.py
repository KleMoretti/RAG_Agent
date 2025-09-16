class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, callable] = {}

    def register_tool(self, name: str, tool: callable) -> None:
        self.tools[name] = tool

    def get_tool(self, name: str) -> callable:
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    def __contains__(self, name: str) -> bool:
        return name in self.tools

    @classmethod
    def create_default_registry(cls) -> 'ToolRegistry':
        registry = cls()
        # Add default tools here
        return registry
