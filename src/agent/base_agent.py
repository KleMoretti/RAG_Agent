from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, AsyncGenerator, Tuple
import logging

from src.retrieval.searcher import Searcher
from src.llm.client import LLMClient

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """私域公司信息处理基础Agent类，提供RAG流程的核心实现"""

    def __init__(
        self,
        llm_client: LLMClient,
        searcher: Searcher,
        max_context_length: int = 4000,
        top_k: int = 5
    ):
        """
        初始化基础Agent

        Args:
            llm_client: 大语言模型客户端
            searcher: 向量检索器
            max_context_length: 上下文最大长度
            top_k: 检索返回文档数量
        """
        self.llm_client = llm_client
        self.searcher = searcher
        self.max_context_length = max_context_length
        self.top_k = top_k

    async def process(
        self,
        query: str,
        history: List[Dict[str, str]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        处理用户查询

        Args:
            query: 用户查询
            history: 对话历史 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            stream: 是否使用流式输出
            **kwargs: 额外参数

        Returns:
            如果stream=False，返回字典: {"answer": str, "sources": List[Dict]}
            如果stream=True，返回异步生成器，产生流式响应片段
        """
        history = history or []

        # 检索相关文档
        search_results = await self.search(query, self.top_k)

        # 准备上下文
        context = self._prepare_context(search_results)

        # 构造提示词
        prompt = self._build_prompt(query, context, history)

        # 生成回答
        if stream:
            return self._generate_stream_response(prompt, search_results)
        else:
            answer = await self.llm_client.generate(prompt)
            return {
                "answer": answer,
                "sources": self._format_sources(search_results)
            }

    async def search(self, query: str, top_k: int) -> List[Dict]:
        """执行检索"""
        try:
            results = await self.searcher.search(query, top_k=top_k)
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def _prepare_context(self, search_results: List[Dict]) -> str:
        """将检索结果格式化为上下文字符串"""
        if not search_results:
            return ""

        context_parts = []
        for i, doc in enumerate(search_results):
            context_parts.append(f"文档[{i+1}] {doc.get('title', '未知文档')}:\n{doc.get('content', '')}")

        return "\n\n".join(context_parts)

    def _build_prompt(self, query: str, context: str, history: List[Dict[str, str]]) -> str:
        """构建提示词模板"""
        history_text = ""
        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

        prompt = f"""你是一个专业的公司内部信息助手。请根据提供的公司文档回答问题。
如果文档中没有相关信息，请明确说明"根据提供的文档，我无法回答这个问题"。
不要编造信息，只基于提供的文档回答。

历史对话:
{history_text}

相关文档信息:
{context}

用户问题: {query}

请根据提供的文档信息回答用户问题:"""

        return prompt

    def _format_sources(self, search_results: List[Dict]) -> List[Dict]:
        """格式化来源信息"""
        sources = []
        for doc in search_results:
            sources.append({
                "title": doc.get("title", "未知文档"),
                "url": doc.get("url", ""),
                "score": doc.get("score", 0.0)
            })
        return sources

    async def _generate_stream_response(self, prompt: str, search_results: List[Dict]):
        """生成流式响应"""
        sources = self._format_sources(search_results)

        async for token in self.llm_client.generate_stream(prompt):
            yield {
                "token": token,
                "done": False
            }

        yield {
            "token": "",
            "sources": sources,
            "done": True
        }