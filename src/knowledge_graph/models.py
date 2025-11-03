"""
钢铁领域知识图谱数据模型

定义钢铁行业相关的实体类型、关系类型和数据结构。
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from datetime import datetime


class SteelEntityType(str, Enum):
    """钢铁领域实体类型"""
    
    # 材料相关
    STEEL_GRADE = "steel_grade"  # 钢种
    STEEL_TYPE = "steel_type"    # 钢材类型
    ALLOY_ELEMENT = "alloy_element"  # 合金元素
    COMPOSITION = "composition"  # 化学成分
    MATERIAL_PROPERTY = "material_property"  # 材料性能（通用）
    MECHANICAL_PROPERTY = "mechanical_property"  # 力学性能
    PHYSICAL_PROPERTY = "physical_property"  # 物理性能
    CHEMICAL_PROPERTY = "chemical_property"  # 化学性能
    
    # 工艺相关
    PROCESS = "process"  # 工艺（通用）
    TREATMENT = "treatment"  # 热处理
    FORMING = "forming"  # 成型工艺
    QUALITY_CONTROL = "quality_control"  # 质量控制
    EQUIPMENT = "equipment"  # 设备
    TECHNOLOGY = "technology"  # 技术
    
    # 产品相关
    PRODUCT = "product"  # 产品
    APPLICATION = "application"  # 应用领域
    SPECIFICATION = "specification"  # 规格
    
    # 企业相关
    COMPANY = "company"  # 公司
    FACTORY = "factory"  # 工厂
    PROJECT = "project"  # 项目
    
    # 标准相关
    STANDARD = "standard"  # 标准
    CERTIFICATION = "certification"  # 认证
    
    # 市场相关
    MARKET = "market"  # 市场
    PRICE = "price"  # 价格
    TREND = "trend"  # 趋势
    
    # 环境相关
    ENVIRONMENT = "environment"  # 环境
    SUSTAINABILITY = "sustainability"  # 可持续性
    
    # 通用实体
    PERSON = "person"  # 人员
    LOCATION = "location"  # 地点
    TIME = "time"  # 时间
    CONCEPT = "concept"  # 概念


class SteelRelationType(str, Enum):
    """钢铁领域关系类型"""
    
    # 材料关系
    CONTAINS = "contains"  # 包含（钢种包含合金元素）
    COMPOSED_OF = "composed_of"  # 由...组成
    HAS_PROPERTY = "has_property"  # 具有性能
    IMPROVES = "improves"  # 改善（性能）
    REDUCES = "reduces"  # 降低（性能）
    
    # 工艺关系
    PRODUCED_BY = "produced_by"  # 由...生产
    USES_EQUIPMENT = "uses_equipment"  # 使用设备
    REQUIRES = "requires"  # 需要（通用）
    REQUIRES_TECHNOLOGY = "requires_technology"  # 需要技术
    APPLIES_TO = "applies_to"  # 应用于
    
    # 产品关系
    USED_IN = "used_in"  # 用于
    SUITABLE_FOR = "suitable_for"  # 适用于
    REPLACES = "replaces"  # 替代
    COMPETES_WITH = "competes_with"  # 竞争
    
    # 企业关系
    OWNS = "owns"  # 拥有
    OPERATES = "operates"  # 运营
    COLLABORATES_WITH = "collaborates_with"  # 合作
    SUPPLIES_TO = "supplies_to"  # 供应给
    
    # 标准关系
    COMPLIES_WITH = "complies_with"  # 符合标准
    CERTIFIED_BY = "certified_by"  # 通过认证
    MEETS = "meets"  # 满足要求
    
    # 市场关系
    AFFECTS_PRICE = "affects_price"  # 影响价格
    INFLUENCES_TREND = "influences_trend"  # 影响趋势
    TARGETS_MARKET = "targets_market"  # 目标市场
    
    # 环境关系
    IMPACTS_ENVIRONMENT = "impacts_environment"  # 环境影响
    PROMOTES_SUSTAINABILITY = "promotes_sustainability"  # 促进可持续性
    
    # 通用关系
    RELATED_TO = "related_to"  # 相关
    PART_OF = "part_of"  # 部分
    CAUSES = "causes"  # 导致
    MENTIONS = "mentions"  # 提及
    LOCATED_IN = "located_in"  # 位于
    WORKS_FOR = "works_for"  # 工作于
    PUBLISHED_IN = "published_in"  # 发表于


@dataclass
class SteelEntity:
    """钢铁领域实体"""
    id: str
    name: str
    entity_type: SteelEntityType
    description: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class SteelRelation:
    """钢铁领域关系"""
    id: str
    source_id: str
    target_id: str
    relation_type: SteelRelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class SteelEntityMention:
    """钢铁领域实体提及"""
    text: str
    start_pos: int
    end_pos: int
    entity_type: SteelEntityType
    confidence: float
    context: str
    entity_id: Optional[str] = None  # 链接到的实体ID


@dataclass
class SteelRelationMention:
    """钢铁领域关系提及"""
    source_text: str
    target_text: str
    relation_type: SteelRelationType
    confidence: float
    context: str
    source_start: int
    source_end: int
    target_start: int
    target_end: int
    source_id: Optional[str] = None  # 链接到的源实体ID
    target_id: Optional[str] = None  # 链接到的目标实体ID


@dataclass
class SteelKnowledgeGraph:
    """钢铁领域知识图谱"""
    entities: Dict[str, SteelEntity] = field(default_factory=dict)
    relations: Dict[str, SteelRelation] = field(default_factory=dict)
    entity_index: Dict[str, Set[str]] = field(default_factory=dict)  # 实体类型 -> 实体ID集合
    relation_index: Dict[SteelRelationType, Set[str]] = field(default_factory=dict)  # 关系类型 -> 关系ID集合
    
    def add_entity(self, entity: SteelEntity) -> None:
        """添加实体"""
        self.entities[entity.id] = entity
        if entity.entity_type not in self.entity_index:
            self.entity_index[entity.entity_type] = set()
        self.entity_index[entity.entity_type].add(entity.id)
    
    def add_relation(self, relation: SteelRelation) -> None:
        """添加关系"""
        self.relations[relation.id] = relation
        if relation.relation_type not in self.relation_index:
            self.relation_index[relation.relation_type] = set()
        self.relation_index[relation.relation_type].add(relation.id)
    
    def get_entities_by_type(self, entity_type: SteelEntityType) -> List[SteelEntity]:
        """根据类型获取实体"""
        entity_ids = self.entity_index.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def get_relations_by_type(self, relation_type: SteelRelationType) -> List[SteelRelation]:
        """根据类型获取关系"""
        relation_ids = self.relation_index.get(relation_type, set())
        return [self.relations[rid] for rid in relation_ids if rid in self.relations]
    
    def get_entity_relations(self, entity_id: str) -> List[SteelRelation]:
        """获取实体的所有关系"""
        relations = []
        for relation in self.relations.values():
            if relation.source_id == entity_id or relation.target_id == entity_id:
                relations.append(relation)
        return relations
    
    def find_entities_by_name(self, name: str, entity_type: Optional[SteelEntityType] = None) -> List[SteelEntity]:
        """根据名称查找实体"""
        results = []
        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            if (name.lower() in entity.name.lower() or 
                any(name.lower() in alias.lower() for alias in entity.aliases)):
                results.append(entity)
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        # 实体类型统计
        entity_type_counts = {}
        for entity_type, entity_ids in self.entity_index.items():
            entity_type_counts[entity_type.value] = len(entity_ids)
        
        # 关系类型统计
        relation_type_counts = {}
        for relation_type, relation_ids in self.relation_index.items():
            relation_type_counts[relation_type.value] = len(relation_ids)
        
        # 平均置信度
        total_confidence = sum(entity.confidence for entity in self.entities.values())
        average_confidence = total_confidence / len(self.entities) if self.entities else 0.0
        
        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "entity_type_counts": entity_type_counts,
            "relation_type_counts": relation_type_counts,
            "average_confidence": average_confidence
        }


# 钢铁领域特定常量
STEEL_GRADES = [
    "Q235", "Q345", "Q420", "Q460", "Q500", "Q550", "Q620", "Q690",
    "20#", "45#", "65Mn", "T8", "T10", "T12",
    "304", "316", "316L", "321", "347", "310S",
    "SUS304", "SUS316", "SUS316L", "SUS321", "SUS347",
    "A36", "A572", "A992", "A500", "A501",
    "S235", "S275", "S355", "S420", "S460",
    "P235", "P265", "P295", "P355", "P420"
]

STEEL_TYPES = [
    "碳素钢", "合金钢", "不锈钢", "工具钢", "弹簧钢", "轴承钢",
    "结构钢", "耐热钢", "耐腐蚀钢", "电工钢", "硅钢",
    "热轧钢", "冷轧钢", "镀锌钢", "镀铝钢", "彩涂钢"
]

ALLOY_ELEMENTS = [
    "碳", "硅", "锰", "磷", "硫", "铬", "镍", "钼", "钒", "钛",
    "钨", "钴", "铜", "铝", "硼", "氮", "铌", "锆", "稀土"
]

MATERIAL_PROPERTIES = [
    "抗拉强度", "屈服强度", "延伸率", "断面收缩率", "冲击韧性",
    "硬度", "疲劳强度", "蠕变强度", "耐腐蚀性", "耐热性",
    "焊接性", "切削性", "冷加工性", "热处理性", "磁性"
]

PROCESSES = [
    "炼钢", "连铸", "热轧", "冷轧", "退火", "正火", "淬火", "回火",
    "调质", "渗碳", "渗氮", "表面处理", "镀层", "涂层", "酸洗",
    "抛丸", "矫直", "切割", "焊接", "成型"
]

EQUIPMENT = [
    "转炉", "电炉", "连铸机", "热轧机", "冷轧机", "退火炉",
    "淬火炉", "回火炉", "矫直机", "切割机", "焊接机", "镀锌线",
    "彩涂线", "酸洗线", "抛丸机", "检测设备", "包装设备"
]

APPLICATIONS = [
    "建筑结构", "桥梁工程", "汽车制造", "船舶建造", "压力容器",
    "管道工程", "机械制造", "家电制造", "食品工业", "化工设备",
    "电力设备", "轨道交通", "航空航天", "海洋工程", "新能源"
]

STANDARDS = [
    "GB/T", "GB", "YB", "JB", "HG", "SH", "SY", "TB", "JT", "CJ",
    "ASTM", "AISI", "SAE", "JIS", "DIN", "EN", "ISO", "API", "ASME", "AWS"
]
