from typing import List, Dict, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from .tools import Tool


@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process."""
    thought: str
    tool_name: Optional[str] = None
    tool_args: Dict[str, Any] = field(default_factory=dict)
    tool_input: Optional[str] = None
    result: Any = None


@dataclass
class ReasoningPath:
    """Represents a complete reasoning path with multiple steps."""
    query: str
    thoughts: str
    steps: List[ReasoningStep] = field(default_factory=list)
    final_answer: Optional[str] = None

class ReasoningEngine:
    """
    Engine for agent reasoning and decision making.
    """

    def __init__(self, model: Optional[Any] = None, verbose: bool = False):
        """
        Initialize the reasoning engine.

        Args:
            model: Optional language model to use for reasoning
            verbose: Whether to log detailed information about reasoning steps
        """
        self.model = model
        self.verbose = verbose
        self.tools = {}
        self.callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_step': [],
            'on_complete': []
        }

    def add_tool(self, tool):
        """
        Add a tool to the reasoning engine.

        Args:
            tool: The tool to add
        """
        self.tools[tool.name] = tool

    def add_callback(self, event: str, callback: Callable) -> None:
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def _trigger_callbacks(self, event: str, **kwargs) -> None:
        for cb in self.callbacks.get(event, []):
            try:
                cb(**kwargs)
            except Exception:
                pass

    def reason(self, query: str, available_tools: List[Any]) -> ReasoningPath:
        self._trigger_callbacks('on_start', query=query, tools=available_tools)

        # Here you would implement the logic to:
        # 1. Parse and understand the query
        # 2. Determine which tools might be helpful
        # 3. Plan a sequence of tool calls and reasoning steps

        # This is where you would integrate with the language model
        # to generate a reasoning path if self.model is provided

        reasoning_path = ReasoningPath(
            query=query,
            thoughts="Analyzing the query to determine the best approach...",
        )

        # Add reasoning steps here
        # For example:
        # reasoning_path.steps.append(
        #     ReasoningStep(
        #         thought="I need to search for information about X",
        #         tool_name="search_tool",
        #         tool_args={"query": "information about X"}
        #     )
        # )

        self._trigger_callbacks('on_complete', path=reasoning_path)
        return reasoning_path

    def execute(self, reasoning_path: ReasoningPath) -> Dict[str, Any]:
        """
        Execute a reasoning path and generate a response.

        Args:
            reasoning_path: The reasoning path to execute

        Returns:
            Final result after executing the reasoning path
        """
        # Execute each step in the reasoning path
        for i, step in enumerate(reasoning_path.steps):
            # This is where you would call the appropriate tool
            # and store the results in the step.result field

            self._trigger_callbacks('on_step', step=step, step_index=i)

            # Placeholder for now
            step.result = f"Result of step {i + 1}"

        # Generate the final answer based on the results of all steps
        final_answer = "This is a placeholder response based on the reasoning path."
        reasoning_path.final_answer = final_answer
        result = {
            "answer": final_answer,
            "reasoning": reasoning_path.thoughts,
            "steps": [],
        }
        return result

    def run(self, query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> tuple[str, List[ReasoningStep]]:
        """
        Process a query and return (final_answer, reasoning_steps).

        chat_history: optional list like [{"role": "user"|"assistant", "content": "..."}]
        """
        # Build prompt with recent history
        history_text = ""
        if chat_history:
            lines = []
            for t in chat_history:
                role = "User" if t.get("role") == "user" else "Assistant"
                lines.append(f"{role}: {t.get('content', '')}")
            history_text = "\n".join(lines)

        prompt_parts = [
            "You are a helpful assistant.",
        ]
        if history_text:
            prompt_parts.append("Here is the recent conversation (most recent last):")
            prompt_parts.append(history_text)
        prompt_parts.append(f"User: {query}")
        prompt_parts.append("Assistant:")
        prompt = "\n".join(prompt_parts)

        # If no model is configured, return a placeholder answer immediately
        if not self.model:
            final_answer = f"This is a placeholder response because no model is available. Query: {query}"
            steps = [ReasoningStep(thought="No LLM model available, providing a default response.")]
            return final_answer, steps

        # Otherwise, try to call the model (supports sync or async generate)
        final_answer: str = ""
        steps: list[ReasoningStep] = []
        try:
            result = self.model.generate(prompt)

            # Detect awaitable results (async generate) and execute them safely.
            import inspect
            import asyncio
            import concurrent.futures

            if inspect.isawaitable(result):
                try:
                    running_loop = asyncio.get_running_loop()
                except RuntimeError:
                    running_loop = None

                # Use the awaitable/coroutine directly (no static cast needed)
                coro = result

                if running_loop is None:
                    final_answer = asyncio.run(coro)
                else:
                    # If an event loop is already running, execute the coroutine
                    # in a separate thread with its own event loop.
                    def _run_coro_in_thread(coro):
                        new_loop = asyncio.new_event_loop()
                        try:
                            asyncio.set_event_loop(new_loop)
                            return new_loop.run_until_complete(coro)
                        finally:
                            try:
                                new_loop.close()
                            except Exception:
                                pass

                    with concurrent.futures.ThreadPoolExecutor() as ex:
                        final_answer = ex.submit(_run_coro_in_thread, coro).result()
            else:
                final_answer = result

            steps = [
                ReasoningStep(
                    thought=f"Generated a response for the query '{query}' using the LLM.",
                    tool_name=None,
                    tool_input=None,
                )
            ]
        except Exception as e:
            final_answer = f"An error occurred while generating a response: {e}"
            steps = [ReasoningStep(thought=f"Error during LLM call: {e}")]

        # Ensure we always return a string for final_answer
        try:
            final_answer = str(final_answer)
        except Exception:
            final_answer = ""

        return final_answer, steps

    def __repr__(self) -> str:
        """String representation of the reasoning engine."""
        model_name = getattr(self.model, 'name', str(self.model)) if self.model else 'None'
        # Also update repr to show the correct tool count from the dictionary
        return f"ReasoningEngine(model={model_name}, tools={len(self.tools)})"