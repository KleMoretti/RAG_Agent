#!/usr/bin/env python3
"""
Agent领域分类器 - 判断用户问题属于哪个专业领域
"""
from typing import Dict, List, Tuple, Optional
import re


class DomainClassifier:
    """
    领域分类器：判断用户问题属于哪个Agent的专业领域
    """
    
    # 定义每个Agent的领域关键词和职责范围
    DOMAIN_KEYWORDS = {
        "process": {
            "name": "工艺专家",
            "keywords": [
                # 工艺术语
                "工艺", "生产", "炼钢", "炼铁", "轧钢", "热轧", "冷轧", "退火",
                "转炉", "高炉", "连铸", "精炼", "脱硫", "脱碳", "温度控制",
                "工序", "流程", "参数", "配方", "工艺路线", "生产线",
                # 材料和成分
                "钢种", "合金", "化学成分", "碳含量", "硅锰", "铬镍",
                # 工艺优化
                "优化", "改进", "调整", "提升", "效率", "产能", "收率",
                # 技术问题
                "如何生产", "如何控制", "工艺要点", "注意事项", "操作规程"
            ],
            "responsibility": "钢铁生产工艺、工艺参数优化、生产流程改进、工艺技术咨询"
        },
        
        "equipment": {
            "name": "设备诊断",
            "keywords": [
                # 设备相关
                "设备", "机器", "装置", "机械", "电机", "泵", "风机", "传感器",
                "加热炉", "轧机", "冷却塔", "除尘器", "压缩机", "液压",
                # 故障和诊断
                "故障", "损坏", "异常", "报警", "停机", "振动", "噪音", "漏油",
                "诊断", "检修", "维修", "维护", "保养", "更换", "备件",
                # 预防性维护
                "预防", "巡检", "点检", "润滑", "清洁", "校准", "寿命",
                # 设备问题描述
                "不转", "过热", "卡死", "泄漏", "磨损", "腐蚀", "断裂"
            ],
            "responsibility": "设备故障诊断、设备维护保养、维修方案、预防性维护、备件管理"
        },
        
        "market": {
            "name": "市场分析师",
            "keywords": [
                # 市场术语
                "市场", "价格", "行情", "趋势", "预测", "分析", "走势",
                "铁矿石", "焦炭", "废钢", "螺纹钢", "板材", "型材",
                # 经济指标
                "供需", "供应", "需求", "库存", "产量", "销量", "出口", "进口",
                "成本", "利润", "盈亏", "竞争", "定价", "议价",
                # 投资决策
                "采购", "销售", "合同", "订单", "报价", "投资", "决策",
                # 市场动态
                "政策", "补贴", "关税", "限产", "环保", "淡季", "旺季"
            ],
            "responsibility": "市场行情分析、价格趋势预测、供需分析、采购决策支持、竞争情报"
        },
        
        "quality": {
            "name": "质量顾问",
            "keywords": [
                # 质量术语
                "质量", "品质", "检测", "检验", "测试", "化验", "分析",
                "标准", "规范", "指标", "合格", "不合格", "超标", "偏差",
                # 性能指标
                "强度", "硬度", "韧性", "延伸率", "屈服", "抗拉", "冲击",
                "表面", "光洁度", "粗糙度", "缺陷", "夹杂", "裂纹", "气泡",
                # 质量管理
                "质检", "抽检", "全检", "监控", "追溯", "记录", "报告",
                "改善", "提升", "控制", "管理", "体系", "认证", "审核"
            ],
            "responsibility": "产品质量控制、质量检测、质量标准制定、质量问题分析、质量改进方案"
        },
        
        "environment": {
            "name": "节能专家",
            "keywords": [
                # 能源术语
                "能源", "能耗", "节能", "用电", "用气", "用水", "蒸汽",
                "电力", "燃料", "煤炭", "天然气", "余热", "回收",
                # 环保术语
                "环保", "排放", "污染", "废气", "废水", "废渣", "烟尘",
                "除尘", "脱硫", "脱硝", "处理", "治理", "达标", "超标",
                # 节能减排
                "降低", "减少", "优化", "提效", "改造", "升级", "绿色",
                "碳排放", "碳中和", "低碳", "清洁", "循环", "可持续"
            ],
            "responsibility": "能源消耗分析、节能方案、环保合规、减排措施、能效优化、绿色技术"
        },
        
        "general": {
            "name": "通用助手",
            "keywords": [
                # 通用问候和闲聊
                "你好", "谢谢", "再见", "帮助", "介绍", "什么",
                "为什么", "怎么", "如何", "能不能", "可以",
                # 基础概念
                "定义", "概念", "解释", "含义", "区别", "联系",
                # 通用查询
                "查询", "搜索", "查找", "信息", "资料", "文档"
            ],
            "responsibility": "通用问答、基础概念解释、信息查询、跨领域问题引导"
        }
    }
    
    def __init__(self):
        """初始化领域分类器"""
        pass
    
    def classify(self, query: str) -> Tuple[str, float, List[Tuple[str, float]]]:
        """
        分类用户查询到对应的领域
        
        Args:
            query: 用户查询文本
            
        Returns:
            (primary_domain, confidence, all_scores)
            - primary_domain: 主要领域 (agent_type)
            - confidence: 置信度 (0-1)
            - all_scores: 所有领域的得分列表 [(domain, score), ...]
        """
        query_lower = query.lower()
        domain_scores = {}
        
        # 计算每个领域的匹配得分
        for domain, config in self.DOMAIN_KEYWORDS.items():
            keywords = config["keywords"]
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            # 归一化得分 (考虑查询长度)
            normalized_score = score / max(len(query_lower.split()), 1)
            domain_scores[domain] = {
                "score": normalized_score,
                "matched_keywords": matched_keywords,
                "count": score
            }
        
        # 按得分排序
        sorted_domains = sorted(
            domain_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # 如果最高得分为0或过低，归为general
        if not sorted_domains or sorted_domains[0][1]["score"] < 0.1:
            return "general", 0.5, [("general", 0.5)]
        
        # 提取主要领域和置信度
        primary_domain = sorted_domains[0][0]
        confidence = min(sorted_domains[0][1]["score"] * 2, 1.0)  # 放大置信度
        
        # 如果第二高的得分很接近，降低置信度（可能是跨领域问题）
        if len(sorted_domains) > 1:
            second_score = sorted_domains[1][1]["score"]
            if second_score > 0.7 * sorted_domains[0][1]["score"]:
                confidence *= 0.7  # 降低置信度
        
        # 构建所有得分列表
        all_scores = [(d, s["score"]) for d, s in sorted_domains if s["score"] > 0]
        
        return primary_domain, confidence, all_scores
    
    def check_domain_match(
        self,
        query: str,
        current_agent: str,
        threshold: float = 0.6
    ) -> Tuple[bool, Optional[str], str]:
        """
        检查查询是否属于当前Agent的领域
        
        Args:
            query: 用户查询
            current_agent: 当前Agent类型
            threshold: 置信度阈值
            
        Returns:
            (is_match, suggested_agent, reason)
            - is_match: 是否匹配当前Agent的领域
            - suggested_agent: 如果不匹配，建议咨询的Agent
            - reason: 判断理由
        """
        primary_domain, confidence, all_scores = self.classify(query)
        
        # 特殊处理：general Agent 可以回答所有问题
        if current_agent == "general":
            # 但如果问题明显属于专业领域，建议转给专家
            if primary_domain != "general" and confidence > 0.7:
                reason = f"这个问题更适合咨询 **{self.DOMAIN_KEYWORDS[primary_domain]['name']}**（匹配度：{confidence:.0%}）"
                return True, primary_domain, reason  # general可以回答，但给出建议
            return True, None, "通用问题"
        
        # 检查是否匹配当前Agent
        if primary_domain == current_agent and confidence >= threshold:
            return True, None, f"属于{self.DOMAIN_KEYWORDS[current_agent]['name']}领域（置信度：{confidence:.0%}）"
        
        # 不匹配，建议转给对应的Agent
        if primary_domain == "general":
            # 问题太通用，当前专家也可以尝试回答
            return True, None, "通用问题，可以尝试回答"
        
        suggested = primary_domain
        reason = (
            f"此问题更适合咨询 **{self.DOMAIN_KEYWORDS[suggested]['name']}**。\n"
            f"该问题涉及：{self.DOMAIN_KEYWORDS[suggested]['responsibility']}"
        )
        
        return False, suggested, reason
    
    def get_domain_info(self, domain: str) -> Dict[str, any]:
        """获取领域信息"""
        if domain not in self.DOMAIN_KEYWORDS:
            return {
                "name": "未知领域",
                "responsibility": "未定义"
            }
        return self.DOMAIN_KEYWORDS[domain]


# 全局单例
_classifier_instance: Optional[DomainClassifier] = None


def get_domain_classifier() -> DomainClassifier:
    """获取领域分类器单例"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DomainClassifier()
    return _classifier_instance

