import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.llm import EchoClient
from src.agent.base_agent import RAGAgent
from src.agent.reasoning import ReasoningEngine
from src.agent.tools import SearchTool


def test_agent_with_echo_client():
    llm = EchoClient(model="echo-test")
    engine = ReasoningEngine(model=llm)
    agent = RAGAgent(llm_client=llm, reasoning_engine=engine, name="TestAgent")
    agent.add_tool(SearchTool())

    resp = agent.run("Hello world")
    assert 'response' in resp
    assert 'echo' in resp['response'] or 'echo-test' in resp['response']
