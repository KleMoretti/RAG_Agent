import logging
from typing import List, Dict, Any, Optional, Union
import json

from src.llm.client import LLMClient

logger = logging.getLogger(__name__)


class ReasoningStep:
    """推理步骤，包含每个步骤的思考过程和工具调用信息"""

    def __init__(
            self,
            thought: str,
            tool_name: Optional[str] = None,
            tool_input: Optional[Dict[str, Any]] = None
    ):
        """
        初始化推理步骤

        Args:
            thought: 推理思考内容
            tool_name: 要调用的工具名称（如果有）
            tool_input: 工具的输入参数（如果有）
        """
        self.thought = thought
        self.tool_name = tool_name
        self.tool_input = tool_input

    def to_dict(self) -> Dict[str, Any]:
        """将步骤转换为字典"""
        return {
            "thought": self.thought,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input
        }

    def __str__(self) -> str:
        """步骤的字符串表示"""
        result = f"思考: {self.thought}"
        if self.tool_name:
            result += f"\n工具: {self.tool_name}"
            if self.tool_input:
                result += f"\n参数: {json.dumps(self.tool_input, ensure_ascii=False)}"
        return result


class ReasoningResult:
    """推理结果，包含整体总结和所有推理步骤"""

    def __init__(
            self,
            summary: str,
            steps: List[ReasoningStep] = None
    ):
        """
        初始化推理结果

        Args:
            summary: 推理总结
            steps: 推理步骤列表
        """
        self.summary = summary
        self.steps = steps or []

    def add_step(self, step: ReasoningStep) -> None:
        """添加推理步骤"""
        self.steps.append(step)

    def to_dict(self) -> Dict[str, Any]:
        """将结果转换为字典"""
        return {
            "summary": self.summary,
            "steps": [step.to_dict() for step in self.steps]
        }

    def to_string(self) -> str:
        """结果的字符串表示"""
        result = f"推理总结: {self.summary}\n\n推理步骤:\n"
        for i, step in enumerate(self.steps):
            result += f"步骤 {i + 1}: {step}\n\n"
        return result


class ReasoningEngine:
    """推理引擎，负责分析问题，确定工具使用，生成执行计划"""

    def __init__(
            self,
            llm_client: LLMClient,
            temperature: float = 0.2,
            max_tokens: int = 1024
    ):
        """
        初始化推理引擎

        Args:
            llm_client: 大语言模型客户端
            temperature: 生成温度，较低以提高确定性
            max_tokens: 最大生成token数
        """
        self.llm_client = llm_client
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def plan(
            self,
            query: str,
            context: Optional[str] = None,
            available_tools: List[Dict[str, str]] = None
    ) -> ReasoningResult:
        """
        对用户查询进行推理规划，确定使用的工具和执行步骤

        Args:
            query: 用户查询
            context: 上下文信息
            available_tools: 可用工具列表，每个工具包含name和description

        Returns:
            推理结果对象
        """
        logger.info(f"开始为查询进行推理规划: {query}")

        # 准备工具信息
        tools_text = "可用工具:\n"
        if available_tools:
            for i, tool in enumerate(available_tools):
                tools_text += f"{i + 1}. {tool['name']}: {tool['description']}\n"
        else:
            tools_text += "无可用工具\n"

        # 构建推理提示词
        prompt = self._build_planning_prompt(query, context, tools_text)

        # 调用LLM获取推理结果
        try:
            reasoning_text = await self.llm_client.generate(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # 解析推理结果
            return self._parse_reasoning(reasoning_text)
        except Exception as e:
            logger.error(f"推理过程出错: {str(e)}")
            # 返回一个简单的错误推理结果
            return ReasoningResult(
                summary=f"推理过程出错: {str(e)}",
                steps=[ReasoningStep(thought="处理用户查询时发生错误，将直接回答用户问题")]
            )

    async def react(
            self,
            query: str,
            context: Optional[str] = None,
            available_tools: List[Dict[str, str]] = None,
            max_steps: int = 5
    ) -> ReasoningResult:
        """
        使用ReAct（Reasoning+Acting）方法进行交互式推理

        Args:
            query: 用户查询
            context: 上下文信息
            available_tools: 可用工具列表
            max_steps: 最大推理步骤数

        Returns:
            推理结果对象
        """
        logger.info(f"开始ReAct交互式推理: {query}")

        # 准备工具信息
        tools_text = self._format_tools_text(available_tools)

        # 初始化推理结果
        result = ReasoningResult(summary="")

        # 构建初始提示词
        observation = ""
        prompt_base = self._build_react_prompt_base(query, context, tools_text)

        # 开始迭代推理过程
        for step_num in range(max_steps):
            # 构建当前步骤的提示词
            prompt = f"{prompt_base}\n\n当前推理历史:\n"
            for i, step in enumerate(result.steps):
                prompt += f"步骤 {i + 1}:\n{step}\n"
                if i < len(result.steps) - 1:
                    prompt += f"观察: {observation}\n"

            # 最后添加新步骤提示
            prompt += f"\n步骤 {len(result.steps) + 1}:"

            # 调用LLM获取本步骤推理
            try:
                step_text = await self.llm_client.generate(
                    prompt=prompt,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                # 解析步骤结果
                thought, tool_name, tool_input = self._parse_step(step_text)

                # 添加步骤到结果
                step = ReasoningStep(thought=thought, tool_name=tool_name, tool_input=tool_input)
                result.add_step(step)

                # 检查是否完成
                if not tool_name:
                    # 无工具调用表示推理完成
                    break

                # 这里实际工具执行会在Agent中进行，这里只是占位
                observation = "工具执行结果将在实际运行时填充"

            except Exception as e:
                logger.error(f"步骤 {step_num + 1} 推理失败: {str(e)}")
                result.add_step(ReasoningStep(
                    thought=f"推理过程出错: {str(e)}",
                    tool_name=None,
                    tool_input=None
                ))
                break

        # 生成总结
        summary_prompt = f"""基于以下推理步骤，总结解决用户问题的整体方法:

用户问题: {query}

推理步骤:
{result.to_string()}

总结:"""

        try:
            result.summary = await self.llm_client.generate(
                prompt=summary_prompt,
                temperature=self.temperature,
                max_tokens=200
            )
        except Exception as e:
            logger.error(f"生成推理总结失败: {str(e)}")
            result.summary = "无法生成推理总结"

        return result

    def _build_planning_prompt(self, query: str, context: Optional[str], tools_text: str) -> str:
        """构建规划推理的提示词"""
        context_text = f"\n相关上下文信息:\n{context}" if context else ""

        prompt = f"""作为一个专业的推理引擎，你需要分析用户查询，制定解决问题的计划，并确定需要使用的工具。

用户查询: {query}{context_text}

{tools_text}

请按照以下格式进行推理:

思考: 分析用户需求是什么，需要解决什么问题
工具: 如果需要使用工具，写出工具名称，否则留空
参数: 如果使用工具，以JSON格式提供工具所需参数

思考: 继续分析问题的下一个部分
工具: 工具名称或留空
参数: {{工具参数}}

总结: 总结你的推理过程和解决方案

请确保你的推理清晰、合理，并且只使用列出的可用工具。如果没有合适的工具，可以不使用工具。"""

        return prompt

    def _build_react_prompt_base(self, query: str, context: Optional[str], tools_text: str) -> str:
        """构建ReAct方法的基础提示词"""
        context_text = f"\n相关上下文信息:\n{context}" if context else ""

        prompt = f"""作为一个专业的推理引擎，你需要通过思考和使用工具来解决用户的问题。

用户查询: {query}{context_text}

{tools_text}

推理过程应遵循以下格式:
思考: <你对问题的分析和思考>
工具: <要使用的工具名称，如果不需要工具则留空>
参数: <以JSON格式提供的工具参数>

每个推理步骤后，你将看到执行结果的观察，然后进行下一步推理。
当你认为已经解决了问题，提供最终答案时，不要指定工具。"""

        return prompt

    def _format_tools_text(self, available_tools: List[Dict[str, str]]) -> str:
        """格式化工具信息文本"""
        tools_text = "可用工具:\n"
        if available_tools:
            for i, tool in enumerate(available_tools):
                tools_text += f"{i + 1}. {tool['name']}: {tool['description']}\n"
        else:
            tools_text += "无可用工具\n"
        return tools_text

    def _parse_reasoning(self, reasoning_text: str) -> ReasoningResult:
        """解析推理文本，提取步骤和总结"""
        lines = reasoning_text.split("\n")

        result = ReasoningResult(summary="")
        current_thought = ""
        current_tool = None
        current_input = None

        for line in lines:
            line = line.strip()

            if line.startswith("思考:"):
                # 如果已有思考内容，说明是新步骤，保存上一步骤
                if current_thought:
                    result.add_step(ReasoningStep(
                        thought=current_thought,
                        tool_name=current_tool,
                        tool_input=current_input
                    ))
                    current_thought = ""
                    current_tool = None
                    current_input = None

                # 提取新的思考内容
                current_thought = line[3:].strip()

            elif line.startswith("工具:"):
                current_tool = line[3:].strip() or None

            elif line.startswith("参数:"):
                param_text = line[3:].strip()
                if param_text:
                    try:
                        current_input = json.loads(param_text)
                    except json.JSONDecodeError:
                        # 如果不是有效JSON，作为字符串处理
                        current_input = {"text": param_text}

            elif line.startswith("总结:"):
                # 提取总结
                result.summary = line[3:].strip()
                # 可能总结跨多行
                summary_index = lines.index(line)
                if summary_index < len(lines) - 1:
                    additional_summary = "\n".join(lines[summary_index + 1:])
                    result.summary += " " + additional_summary.strip()
                break

        # 添加最后一个步骤（如果有）
        if current_thought:
            result.add_step(ReasoningStep(
                thought=current_thought,
                tool_name=current_tool,
                tool_input=current_input
            ))

        # 如果没有提取到总结，生成一个默认总结
        if not result.summary and result.steps:
            result.summary = "基于以上推理步骤处理用户查询"

        return result

    def _parse_step(self, step_text: str) -> tuple:
        """解析单个推理步骤文本，返回思考、工具名和参数"""
        thought = ""
        tool_name = None
        tool_input = None

        lines = step_text.split('\n')

        for line in lines:
            line = line.strip()

            if line.startswith("思考:"):
                thought = line[3:].strip()

            elif line.startswith("工具:"):
                tool_name = line[3:].strip() or None

            elif line.startswith("参数:"):
                param_text = line[3:].strip()
                if param_text:
                    try:
                        tool_input = json.loads(param_text)
                    except json.JSONDecodeError:
                        # 如果不是有效JSON，作为字符串处理
                        tool_input = {"text": param_text}

        return thought, tool_name, tool_input