import sys, pathlib
import asyncio
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent.reasoning import ReasoningEngine
from src.agent.base_agent import RAGAgent
from src.agent.tools import SearchTool


class AsyncLLM:
    """A simple async LLM stub that returns a coroutine from generate."""
    def __init__(self, model: str = "async-test"):
        self.model = model

    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(0)
        return f"[async:{self.model}] {prompt}"


def test_async_llm_integration():
    llm = AsyncLLM(model="async-test")
    engine = ReasoningEngine(model=llm)
    agent = RAGAgent(llm_client=llm, reasoning_engine=engine, name="AsyncAgent")
    agent.add_tool(SearchTool())

    resp = agent.run("Hello async")
    assert 'response' in resp
    assert '[async:async-test]' in resp['response'] or 'async-test' in resp['response']
