import logging
    from typing import List, Dict, Any, Optional, Union, AsyncGenerator

    from src.llm.client import LLMClient
    from src.agent.base_agent import BaseAgent
    from src.agent.reasoning import ReasoningEngine
    from src.agent.tools import ToolRegistry

    logger = logging.getLogger(__name__)

    class AgentClient:
        """Agent客户端，用于协调推理引擎、工具调用和LLM交互"""

        def __init__(
            self,
            llm_client: LLMClient,
            tool_registry: Optional[ToolRegistry] = None,
            max_reasoning_steps: int = 3,
            reasoning_temperature: float = 0.2
        ):
            """
            初始化Agent客户端

            Args:
                llm_client: 大语言模型客户端
                tool_registry: 工具注册表，用于管理可用工具
                max_reasoning_steps: 最大推理步骤数
                reasoning_temperature: 推理时使用的温度参数(较低以提高确定性)
            """
            self.llm_client = llm_client
            self.tool_registry = tool_registry or ToolRegistry()
            self.max_reasoning_steps = max_reasoning_steps
            self.reasoning_engine = ReasoningEngine(
                llm_client=llm_client,
                temperature=reasoning_temperature
            )

        async def process_query(
            self,
            query: str,
            context: Optional[str] = None,
            history: Optional[List[Dict[str, str]]] = None,
            stream: bool = False
        ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
            """
            处理用户查询，通过推理引擎和工具执行完成任务

            Args:
                query: 用户查询
                context: 额外的上下文信息
                history: 对话历史
                stream: 是否使用流式输出

            Returns:
                包含回答和元数据的结果
            """
            history = history or []

            # 1. 进行推理，确定需要的工具和执行计划
            reasoning_result = await self.reasoning_engine.plan(
                query=query,
                context=context,
                available_tools=self.tool_registry.list_tools()
            )

            # 2. 执行工具调用
            execution_results = []
            for step in reasoning_result.steps[:self.max_reasoning_steps]:
                if step.tool_name and step.tool_name in self.tool_registry:
                    tool = self.tool_registry.get_tool(step.tool_name)
                    try:
                        result = await tool.execute(step.tool_input)
                        execution_results.append({
                            "tool": step.tool_name,
                            "input": step.tool_input,
                            "output": result
                        })
                    except Exception as e:
                        logger.error(f"工具执行出错: {str(e)}")
                        execution_results.append({
                            "tool": step.tool_name,
                            "input": step.tool_input,
                            "error": str(e)
                        })

            # 3. 生成最终回答
            prompt = self._build_final_prompt(
                query=query,
                context=context,
                history=history,
                reasoning=reasoning_result,
                executions=execution_results
            )

            # 4. 返回结果
            if stream:
                return self._stream_response(prompt, reasoning_result, execution_results)
            else:
                answer = await self.llm_client.generate(prompt)
                return {
                    "answer": answer,
                    "reasoning": reasoning_result.to_dict(),
                    "executions": execution_results
                }

        def _build_final_prompt(
            self,
            query: str,
            context: Optional[str],
            history: List[Dict[str, str]],
            reasoning: Any,
            executions: List[Dict]
        ) -> str:
            """构建最终提示词，整合推理过程和工具执行结果"""
            history_text = ""
            if history:
                for msg in history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    history_text += f"{role}: {content}\n"

            context_text = context or ""

            # 格式化工具执行结果
            execution_text = ""
            for i, exec_result in enumerate(executions):
                tool_name = exec_result.get("tool", "未知工具")
                tool_input = exec_result.get("input", "")
                if "output" in exec_result:
                    execution_text += f"工具[{i+1}] {tool_name}(输入: {tool_input}) => {exec_result['output']}\n"
                else:
                    execution_text += f"工具[{i+1}] {tool_name}(输入: {tool_input}) => 执行失败: {exec_result.get('error', '未知错误')}\n"

            prompt = f"""你是一个专业的信息助手。请基于以下信息回答用户问题。
    
    历史对话:
    {history_text}
    
    背景信息:
    {context_text}
    
    推理过程:
    {reasoning.to_string()}
    
    工具执行结果:
    {execution_text}
    
    用户问题: {query}
    
    请综合以上信息，给出清晰、准确的回答:"""

            return prompt

        async def _stream_response(self, prompt: str, reasoning: Any, executions: List[Dict]):
            """生成流式响应"""
            async for token in self.llm_client.generate_stream(prompt):
                yield {
                    "token": token,
                    "done": False
                }

            yield {
                "token": "",
                "reasoning": reasoning.to_dict(),
                "executions": executions,
                "done": True
            }