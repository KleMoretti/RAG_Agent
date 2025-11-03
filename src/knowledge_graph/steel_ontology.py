"""
钢铁行业标准知识图谱本体（Ontology）

定义钢铁领域的核心概念、实体类型和关系类型，作为知识图谱构建的基准。
"""

from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class CoreEntityType(str, Enum):
    """核心实体类型（蛛网中心节点）"""
    STEEL_GRADE = "steel_grade"  # 钢种牌号（核心）
    PROCESS = "process"  # 工艺流程
    EQUIPMENT = "equipment"  # 设备
    PRODUCT = "product"  # 产品


class FeatureEntityType(str, Enum):
    """特征实体类型（蛛网分支节点）"""
    # 成分特征
    ALLOY_ELEMENT = "alloy_element"  # 合金元素
    COMPOSITION = "composition"  # 化学成分
    
    # 性能特征
    MECHANICAL_PROPERTY = "mechanical_property"  # 力学性能
    PHYSICAL_PROPERTY = "physical_property"  # 物理性能
    CHEMICAL_PROPERTY = "chemical_property"  # 化学性能
    
    # 工艺特征
    TREATMENT = "treatment"  # 热处理
    FORMING = "forming"  # 成型工艺
    QUALITY_CONTROL = "quality_control"  # 质量控制
    
    # 应用特征
    APPLICATION = "application"  # 应用领域
    STANDARD = "standard"  # 技术标准
    SPECIFICATION = "specification"  # 规格要求


@dataclass
class StandardEntity:
    """标准实体定义"""
    name: str
    entity_type: str
    description: str
    aliases: List[str]
    typical_values: List[str] = None
    

@dataclass
class StandardRelation:
    """标准关系定义"""
    source: str
    target: str
    relation_type: str
    description: str


class SteelIndustryOntology:
    """钢铁行业标准本体"""
    
    def __init__(self):
        self.core_entities = self._define_core_entities()
        self.standard_entities = self._define_standard_entities()
        self.standard_relations = self._define_standard_relations()
        
    def _define_core_entities(self) -> Dict[str, StandardEntity]:
        """定义核心实体（蛛网中心）"""
        return {
            # 钢种牌号系列
            "碳素结构钢": StandardEntity(
                name="碳素结构钢",
                entity_type=CoreEntityType.STEEL_GRADE,
                description="以碳元素为主的结构钢",
                aliases=["碳钢", "C钢"],
                typical_values=["Q235", "Q345", "Q420"]
            ),
            "不锈钢": StandardEntity(
                name="不锈钢",
                entity_type=CoreEntityType.STEEL_GRADE,
                description="耐腐蚀钢材",
                aliases=["不锈钢材"],
                typical_values=["304", "316L", "201"]
            ),
            "硅钢": StandardEntity(
                name="硅钢",
                entity_type=CoreEntityType.STEEL_GRADE,
                description="含硅电工钢",
                aliases=["电工钢", "矽钢"],
                typical_values=["B35A300", "HiB"]
            ),
            
            # 核心工艺
            "炼钢": StandardEntity(
                name="炼钢",
                entity_type=CoreEntityType.PROCESS,
                description="将生铁转化为钢水",
                aliases=["钢水冶炼"]
            ),
            "轧制": StandardEntity(
                name="轧制",
                entity_type=CoreEntityType.PROCESS,
                description="通过轧机使钢材变形",
                aliases=["轧钢", "压延"]
            ),
            "热处理": StandardEntity(
                name="热处理",
                entity_type=CoreEntityType.PROCESS,
                description="通过加热冷却改变钢材性能",
                aliases=["淬火回火", "退火正火"]
            ),
        }
    
    def _define_standard_entities(self) -> Dict[str, StandardEntity]:
        """定义标准特征实体（蛛网分支）"""
        return {
            # 合金元素
            "碳": StandardEntity(
                name="碳",
                entity_type=FeatureEntityType.ALLOY_ELEMENT,
                description="碳元素，影响钢材强度和硬度",
                aliases=["C", "Carbon"]
            ),
            "硅": StandardEntity(
                name="硅",
                entity_type=FeatureEntityType.ALLOY_ELEMENT,
                description="硅元素，提高钢材弹性和磁性",
                aliases=["Si", "Silicon"]
            ),
            "锰": StandardEntity(
                name="锰",
                entity_type=FeatureEntityType.ALLOY_ELEMENT,
                description="锰元素，提高钢材强度和韧性",
                aliases=["Mn", "Manganese"]
            ),
            "铬": StandardEntity(
                name="铬",
                entity_type=FeatureEntityType.ALLOY_ELEMENT,
                description="铬元素，提高耐腐蚀性",
                aliases=["Cr", "Chromium"]
            ),
            "镍": StandardEntity(
                name="镍",
                entity_type=FeatureEntityType.ALLOY_ELEMENT,
                description="镍元素，提高耐腐蚀性和韧性",
                aliases=["Ni", "Nickel"]
            ),
            
            # 力学性能
            "抗拉强度": StandardEntity(
                name="抗拉强度",
                entity_type=FeatureEntityType.MECHANICAL_PROPERTY,
                description="材料抵抗拉伸破坏的能力",
                aliases=["拉伸强度", "Tensile Strength"]
            ),
            "屈服强度": StandardEntity(
                name="屈服强度",
                entity_type=FeatureEntityType.MECHANICAL_PROPERTY,
                description="材料发生塑性变形的临界应力",
                aliases=["屈服点", "Yield Strength"]
            ),
            "延伸率": StandardEntity(
                name="延伸率",
                entity_type=FeatureEntityType.MECHANICAL_PROPERTY,
                description="材料拉伸断裂时的伸长率",
                aliases=["伸长率", "Elongation"]
            ),
            "硬度": StandardEntity(
                name="硬度",
                entity_type=FeatureEntityType.MECHANICAL_PROPERTY,
                description="材料抵抗压入的能力",
                aliases=["Hardness"]
            ),
            
            # 应用领域
            "建筑结构": StandardEntity(
                name="建筑结构",
                entity_type=FeatureEntityType.APPLICATION,
                description="用于建筑承重结构",
                aliases=["建筑用钢", "结构钢"]
            ),
            "桥梁工程": StandardEntity(
                name="桥梁工程",
                entity_type=FeatureEntityType.APPLICATION,
                description="用于桥梁建设",
                aliases=["桥梁钢"]
            ),
            "汽车制造": StandardEntity(
                name="汽车制造",
                entity_type=FeatureEntityType.APPLICATION,
                description="用于汽车车身和零件",
                aliases=["汽车钢"]
            ),
            "家电制造": StandardEntity(
                name="家电制造",
                entity_type=FeatureEntityType.APPLICATION,
                description="用于家用电器",
                aliases=["家电钢板"]
            ),
        }
    
    def _define_standard_relations(self) -> List[StandardRelation]:
        """定义标准关系"""
        return [
            # 钢种 -> 成分
            StandardRelation("碳素结构钢", "碳", "contains", "包含碳元素"),
            StandardRelation("碳素结构钢", "硅", "contains", "包含硅元素"),
            StandardRelation("碳素结构钢", "锰", "contains", "包含锰元素"),
            StandardRelation("不锈钢", "铬", "contains", "包含铬元素"),
            StandardRelation("不锈钢", "镍", "contains", "包含镍元素"),
            StandardRelation("硅钢", "硅", "contains", "包含硅元素"),
            
            # 钢种 -> 性能
            StandardRelation("碳素结构钢", "抗拉强度", "has_property", "具有抗拉强度性能"),
            StandardRelation("碳素结构钢", "屈服强度", "has_property", "具有屈服强度性能"),
            StandardRelation("碳素结构钢", "延伸率", "has_property", "具有延伸率性能"),
            StandardRelation("不锈钢", "硬度", "has_property", "具有硬度性能"),
            
            # 钢种 -> 工艺
            StandardRelation("碳素结构钢", "炼钢", "produced_by", "由炼钢工艺生产"),
            StandardRelation("碳素结构钢", "轧制", "produced_by", "由轧制工艺生产"),
            StandardRelation("不锈钢", "热处理", "requires", "需要热处理工艺"),
            
            # 钢种 -> 应用
            StandardRelation("碳素结构钢", "建筑结构", "used_in", "用于建筑结构"),
            StandardRelation("碳素结构钢", "桥梁工程", "used_in", "用于桥梁工程"),
            StandardRelation("不锈钢", "家电制造", "used_in", "用于家电制造"),
            StandardRelation("硅钢", "家电制造", "used_in", "用于家电制造（电机）"),
        ]
    
    def get_core_entity_types(self) -> Set[str]:
        """获取核心实体类型"""
        return set(CoreEntityType)
    
    def get_feature_categories(self) -> Dict[str, List[str]]:
        """获取特征分类（用于蛛网展示）"""
        return {
            "成分特征": [
                FeatureEntityType.ALLOY_ELEMENT,
                FeatureEntityType.COMPOSITION,
            ],
            "性能特征": [
                FeatureEntityType.MECHANICAL_PROPERTY,
                FeatureEntityType.PHYSICAL_PROPERTY,
                FeatureEntityType.CHEMICAL_PROPERTY,
            ],
            "工艺特征": [
                FeatureEntityType.TREATMENT,
                FeatureEntityType.FORMING,
                FeatureEntityType.QUALITY_CONTROL,
            ],
            "应用特征": [
                FeatureEntityType.APPLICATION,
                FeatureEntityType.STANDARD,
                FeatureEntityType.SPECIFICATION,
            ],
        }
    
    def is_core_entity(self, entity_name: str) -> bool:
        """判断是否为核心实体"""
        return entity_name in self.core_entities
    
    def get_entity_category(self, entity_type: str) -> str:
        """获取实体所属分类"""
        feature_categories = self.get_feature_categories()
        for category, types in feature_categories.items():
            # 将枚举转换为字符串进行比较
            if entity_type in [t.value for t in types]:
                return category
        # 检查是否为核心实体类型
        if entity_type in [t.value for t in CoreEntityType]:
            return "核心实体"
        return "其他"


# 全局单例
_steel_ontology = None


def get_steel_ontology() -> SteelIndustryOntology:
    """获取钢铁行业标准本体"""
    global _steel_ontology
    if _steel_ontology is None:
        _steel_ontology = SteelIndustryOntology()
    return _steel_ontology

