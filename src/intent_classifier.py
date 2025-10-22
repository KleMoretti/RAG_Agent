"""
意图识别模块 - 智能判断查询是否需要 RAG 检索

判断逻辑：
- 简单问候/闲聊 → 不需要 RAG
- 常识性问题 → 不需要 RAG
- 专业领域问题 → 需要 RAG
- 包含专业术语 → 需要 RAG
"""

import re
from typing import Literal

IntentType = Literal["greeting", "chitchat", "knowledge_query", "professional_query"]


class IntentClassifier:
    """意图分类器 - 快速判断查询类型"""
    
    def __init__(self):
        # 问候语关键词
        self.greeting_patterns = [
            r"^(你好|您好|hi|hello|嗨|早|午安|晚安|早上好|下午好|晚上好)",
            r"^(谢谢|感谢|多谢|thanks|thank you)",
            r"^(再见|拜拜|bye|goodbye)",
        ]
        
        # 闲聊关键词（不需要专业知识）
        self.chitchat_patterns = [
            r"(天气|心情|吃饭|喝水|休息|睡觉)",
            r"(怎么样|如何|好吗|可以吗|能不能)",
            r"^(介绍.{0,5}自己|你是谁|你叫什么)",
        ]
        
        # 专业术语关键词（钢铁行业）
        self.professional_keywords = [
            # 钢种
            "Q235", "Q345", "304", "316L", "不锈钢", "碳素钢", "合金钢",
            "硅钢", "取向硅钢", "HiB", "CGO",
            # 工艺
            "炼钢", "轧钢", "热轧", "冷轧", "退火", "淬火", "回火",
            "转炉", "电炉", "连铸", "板坯", "带钢",
            # 性能指标
            "抗拉强度", "屈服强度", "延伸率", "硬度", "韧性",
            "铁损", "磁感", "磁导率",
            # 设备
            "加热炉", "轧机", "冷却塔", "精轧机", "卷取机",
            # 质量控制
            "化学成分", "金相组织", "表面质量", "尺寸精度",
            "织构", "Goss织构", "晶粒",
            # 市场相关
            "铁矿石", "焦炭", "废钢", "螺纹钢", "价格", "趋势",
            "供需", "库存", "产量",
        ]
        
        # 知识查询关键词（需要检索文档）
        self.knowledge_query_keywords = [
            "是什么", "什么是", "如何", "怎么", "为什么",
            "原因", "方法", "步骤", "流程", "过程",
            "定义", "解释", "说明", "介绍", "区别",
            "标准", "规范", "要求", "参数", "指标",
        ]
    
    def classify(self, query: str) -> tuple[IntentType, float, str]:
        """
        分类查询意图
        
        Returns:
            (intent_type, confidence, reason)
            - intent_type: 意图类型
            - confidence: 置信度 (0-1)
            - reason: 判断理由
        """
        query = query.strip()
        
        # 1. 检测问候语
        for pattern in self.greeting_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return "greeting", 0.95, "检测到问候语模式"
        
        # 2. 检测专业术语（优先级高）
        professional_count = sum(
            1 for keyword in self.professional_keywords 
            if keyword.lower() in query.lower()
        )
        if professional_count >= 2:
            return "professional_query", 0.9, f"包含{professional_count}个专业术语"
        elif professional_count == 1:
            # 单个专业术语，需要进一步判断
            has_knowledge_keyword = any(
                kw in query for kw in self.knowledge_query_keywords
            )
            if has_knowledge_keyword:
                return "professional_query", 0.85, "包含专业术语+知识查询关键词"
        
        # 3. 检测知识查询
        knowledge_count = sum(
            1 for keyword in self.knowledge_query_keywords
            if keyword in query
        )
        if knowledge_count >= 1 and len(query) > 10:
            return "knowledge_query", 0.8, f"包含知识查询关键词，查询长度{len(query)}"
        
        # 4. 检测闲聊
        for pattern in self.chitchat_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return "chitchat", 0.7, "匹配闲聊模式"
        
        # 5. 基于查询长度判断
        if len(query) < 5:
            return "chitchat", 0.6, "查询过短，可能是简单问候"
        elif len(query) > 20:
            return "knowledge_query", 0.7, "查询较长，可能需要专业知识"
        
        # 默认：当作知识查询（保守策略）
        return "knowledge_query", 0.5, "无明确特征，默认为知识查询"
    
    def should_use_rag(self, query: str, threshold: float = 0.7) -> tuple[bool, str]:
        """
        判断是否需要使用 RAG
        
        Args:
            query: 用户查询
            threshold: 置信度阈值
            
        Returns:
            (should_use_rag, reason)
        """
        intent, confidence, reason = self.classify(query)
        
        # 问候和闲聊不需要 RAG
        if intent in ["greeting", "chitchat"]:
            return False, f"意图类型={intent}，无需检索（{reason}）"
        
        # 知识查询和专业查询需要 RAG
        if intent in ["knowledge_query", "professional_query"]:
            if confidence >= threshold:
                return True, f"意图类型={intent}，置信度{confidence:.0%}（{reason}）"
            else:
                # 置信度不足，保守使用 RAG
                return True, f"置信度不足但保守使用RAG（{reason}）"
        
        # 默认使用 RAG（保守策略）
        return True, f"未明确判断，保守使用RAG（{reason}）"


# 单例模式
_intent_classifier: IntentClassifier | None = None


def get_intent_classifier() -> IntentClassifier:
    """获取意图分类器单例"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()
    return _intent_classifier


# 测试代码
if __name__ == "__main__":
    classifier = IntentClassifier()
    
    test_queries = [
        "你好",
        "早上好！",
        "谢谢你的帮助",
        "天气怎么样",
        "你叫什么名字",
        "钢铁生产中最重要的是什么？",
        "Q235的抗拉强度是多少？",
        "如何控制炼钢过程中的温度？",
        "转炉和电炉有什么区别？",
        "介绍一下热轧工艺流程",
        "不锈钢304和316L的化学成分对比",
        "铁矿石价格趋势如何？",
        "什么是Goss织构？",
        "这是什么",
        "为什么",
    ]
    
    print("=" * 80)
    print("意图识别测试")
    print("=" * 80)
    
    for query in test_queries:
        should_use, reason = classifier.should_use_rag(query)
        intent, confidence, detail = classifier.classify(query)
        
        print(f"\n查询: {query}")
        print(f"  意图: {intent} (置信度: {confidence:.0%})")
        print(f"  理由: {detail}")
        print(f"  使用RAG: {'✅ 是' if should_use else '❌ 否'} - {reason}")

