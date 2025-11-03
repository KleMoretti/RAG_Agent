#!/usr/bin/env python3
"""
领域边界检查工具 - Agent用于检查问题是否属于自己的专业领域
"""
from typing import Dict, Any
from .tools import Tool
from .domain_classifier import get_domain_classifier


class DomainBoundaryTool(Tool):
    """
    领域边界检查工具
    
    用途：
    1. Agent在回答前先检查问题是否属于自己的领域
    2. 如果不属于，返回转发建议
    3. 如果属于，继续回答
    """
    
    def __init__(self, agent_type: str):
        """
        初始化领域边界检查工具
        
        Args:
            agent_type: 当前Agent的类型 (process/equipment/market/quality/environment/general)
        """
        super().__init__(
            name="check_domain_boundary",
            description=(
                f"检查用户问题是否属于{agent_type} Agent的专业领域。"
                "如果问题超出专业范围，返回转发建议；如果属于专业范围，返回确认信息。"
            )
        )
        self.agent_type = agent_type
        self.classifier = get_domain_classifier()
    
    def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        检查问题是否属于当前Agent的领域
        
        Args:
            query: 用户查询文本
            
        Returns:
            {
                "is_in_domain": bool,           # 是否属于当前领域
                "confidence": float,            # 置信度
                "suggested_agent": str | None,  # 建议咨询的Agent (如果不属于)
                "reason": str,                  # 判断理由
                "agent_info": dict             # 建议Agent的详细信息
            }
        """
        # 检查领域匹配
        is_match, suggested_agent, reason = self.classifier.check_domain_match(
            query=query,
            current_agent=self.agent_type,
            threshold=0.5  # 可调整的阈值
        )
        
        # 分类查询以获取置信度
        primary_domain, confidence, all_scores = self.classifier.classify(query)
        
        result = {
            "is_in_domain": is_match,
            "confidence": confidence,
            "suggested_agent": suggested_agent,
            "reason": reason,
            "primary_domain": primary_domain,
            "all_scores": all_scores
        }
        
        # 如果有建议的Agent，添加详细信息
        if suggested_agent:
            agent_info = self.classifier.get_domain_info(suggested_agent)
            result["agent_info"] = {
                "name": agent_info["name"],
                "responsibility": agent_info["responsibility"]
            }
        else:
            result["agent_info"] = None
        
        return result
    
    def format_redirect_message(self, result: Dict[str, Any]) -> str:
        """
        格式化转发消息
        
        Args:
            result: execute() 的返回结果
            
        Returns:
            格式化的转发消息
        """
        if result["is_in_domain"]:
            return ""  # 属于当前领域，不需要转发
        
        agent_info = result.get("agent_info")
        if not agent_info:
            return "抱歉，我无法准确判断这个问题属于哪个领域。"
        
        message = (
            f"🔄 **领域转发建议**\n\n"
            f"您的问题似乎更适合咨询 **{agent_info['name']}**。\n\n"
            f"**{agent_info['name']}** 的专业领域包括：\n"
            f"{agent_info['responsibility']}\n\n"
            f"💡 **建议**：请切换到 **{agent_info['name']}** 以获得更专业的解答。\n\n"
            f"---\n\n"
            f"当然，如果您确认这个问题确实与我的专业领域相关，我也可以尽力为您解答。"
        )
        
        return message


def create_domain_boundary_tool(agent_type: str) -> DomainBoundaryTool:
    """
    工厂函数：为指定Agent类型创建领域边界检查工具
    
    Args:
        agent_type: Agent类型
        
    Returns:
        DomainBoundaryTool实例
    """
    return DomainBoundaryTool(agent_type)

