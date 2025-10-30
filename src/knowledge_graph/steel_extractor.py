"""
钢铁领域知识图谱抽取器

专门针对钢铁行业的实体识别和关系抽取。
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, Counter

from .models import (
    SteelEntity, SteelRelation, SteelEntityMention, SteelRelationMention,
    SteelEntityType, SteelRelationType,
    STEEL_GRADES, STEEL_TYPES, ALLOY_ELEMENTS, MATERIAL_PROPERTIES,
    PROCESSES, EQUIPMENT, APPLICATIONS, STANDARDS
)

logger = logging.getLogger(__name__)


class SteelEntityExtractor:
    """钢铁领域实体抽取器"""
    
    def __init__(self):
        self.patterns = self._build_patterns()
        self.stop_words = self._build_stop_words()
        self.steel_terms = self._build_steel_terms()
    
    def _build_patterns(self) -> Dict[SteelEntityType, List[str]]:
        """构建钢铁领域实体识别模式"""
        return {
            SteelEntityType.STEEL_GRADE: [
                r'Q\d{3}[A-Z]?',  # Q235, Q345B等
                r'\d+#',  # 20#, 45#等
                r'\d+Mn[A-Z]?',  # 65Mn, 65MnA等
                r'T\d+[A-Z]?',  # T8, T10A等
                r'\d{3}[A-Z]?',  # 304, 316L等
                r'SUS\d{3}[A-Z]?',  # SUS304, SUS316L等
                r'A\d{3}[A-Z]?',  # A36, A572等
                r'S\d{3}[A-Z]?',  # S235, S355等
                r'P\d{3}[A-Z]?',  # P235, P355等
            ],
            SteelEntityType.STEEL_TYPE: [
                r'碳素钢|碳钢',
                r'合金钢',
                r'不锈钢',
                r'工具钢',
                r'弹簧钢',
                r'轴承钢',
                r'结构钢',
                r'耐热钢',
                r'耐腐蚀钢',
                r'电工钢',
                r'硅钢',
                r'热轧钢',
                r'冷轧钢',
                r'镀锌钢',
                r'镀铝钢',
                r'彩涂钢',
            ],
            SteelEntityType.ALLOY_ELEMENT: [
                r'[碳硅锰磷硫铬镍钼钒钛钨钴铜铝硼氮铌锆稀土]',
                r'C|Si|Mn|P|S|Cr|Ni|Mo|V|Ti|W|Co|Cu|Al|B|N|Nb|Zr|RE',
            ],
            SteelEntityType.MATERIAL_PROPERTY: [
                r'抗拉强度|拉伸强度|σb|Rm',
                r'屈服强度|σs|ReL|ReH',
                r'延伸率|δ|A',
                r'断面收缩率|ψ|Z',
                r'冲击韧性|冲击功|Akv|KV',
                r'硬度|HB|HRC|HV',
                r'疲劳强度|疲劳极限',
                r'蠕变强度|蠕变极限',
                r'耐腐蚀性|耐蚀性',
                r'耐热性|热稳定性',
                r'焊接性|可焊性',
                r'切削性|可切削性',
                r'冷加工性|冷变形性',
                r'热处理性|淬透性',
                r'磁性|导磁性',
            ],
            SteelEntityType.PROCESS: [
                r'炼钢|转炉炼钢|电炉炼钢',
                r'连铸|连续铸造',
                r'热轧|热轧制',
                r'冷轧|冷轧制',
                r'退火|完全退火|球化退火',
                r'正火|正火处理',
                r'淬火|淬火处理',
                r'回火|回火处理',
                r'调质|调质处理',
                r'渗碳|渗碳处理',
                r'渗氮|渗氮处理',
                r'表面处理|表面改性',
                r'镀层|镀锌|镀铝',
                r'涂层|彩涂',
                r'酸洗|酸洗处理',
                r'抛丸|抛丸处理',
                r'矫直|矫直处理',
                r'切割|切割加工',
                r'焊接|焊接工艺',
                r'成型|成型加工',
            ],
            SteelEntityType.EQUIPMENT: [
                r'转炉|LD转炉|BOF',
                r'电炉|电弧炉|EAF',
                r'连铸机|连铸设备',
                r'热轧机|热轧设备',
                r'冷轧机|冷轧设备',
                r'退火炉|退火设备',
                r'淬火炉|淬火设备',
                r'回火炉|回火设备',
                r'矫直机|矫直设备',
                r'切割机|切割设备',
                r'焊接机|焊接设备',
                r'镀锌线|镀锌设备',
                r'彩涂线|彩涂设备',
                r'酸洗线|酸洗设备',
                r'抛丸机|抛丸设备',
                r'检测设备|检测仪器',
                r'包装设备|包装机械',
            ],
            SteelEntityType.APPLICATION: [
                r'建筑结构|建筑用钢',
                r'桥梁工程|桥梁用钢',
                r'汽车制造|汽车用钢',
                r'船舶建造|船舶用钢',
                r'压力容器|容器用钢',
                r'管道工程|管道用钢',
                r'机械制造|机械用钢',
                r'家电制造|家电用钢',
                r'食品工业|食品级钢',
                r'化工设备|化工用钢',
                r'电力设备|电力用钢',
                r'轨道交通|轨道用钢',
                r'航空航天|航空用钢',
                r'海洋工程|海洋用钢',
                r'新能源|新能源用钢',
            ],
            SteelEntityType.STANDARD: [
                r'GB/T\s*\d+[\.\-]?\d*',
                r'GB\s*\d+[\.\-]?\d*',
                r'YB/T\s*\d+[\.\-]?\d*',
                r'JB/T\s*\d+[\.\-]?\d*',
                r'ASTM\s*[A-Z]\d+',
                r'AISI\s*\d+',
                r'SAE\s*\d+',
                r'JIS\s*[A-Z]\d+',
                r'DIN\s*\d+',
                r'EN\s*\d+',
                r'ISO\s*\d+',
                r'API\s*\d+',
                r'ASME\s*[A-Z]\d+',
                r'AWS\s*[A-Z]\d+',
            ],
            SteelEntityType.COMPANY: [
                r'[A-Za-z\u4e00-\u9fff]+(?:钢铁|钢铁集团|钢铁公司|钢铁厂|钢厂|钢铁企业)',
                r'[A-Za-z\u4e00-\u9fff]+(?:集团|公司|企业|厂|有限公司|股份有限公司)',
            ],
            SteelEntityType.PRODUCT: [
                r'[A-Za-z\u4e00-\u9fff]+(?:板|管|棒|线|带|型材|板材|管材|棒材|线材|带材)',
                r'[A-Za-z\u4e00-\u9fff]+(?:钢板|钢管|钢棒|钢丝|钢带|型钢)',
            ],
            SteelEntityType.LOCATION: [
                r'[A-Za-z\u4e00-\u9fff]+(?:省|市|县|区|镇|村)',
                r'[A-Za-z\u4e00-\u9fff]+(?:钢铁基地|工业园区|经济开发区)',
            ],
            SteelEntityType.TIME: [
                r'\d{4}年',
                r'\d{1,2}月',
                r'\d{1,2}日',
                r'\d{4}-\d{1,2}-\d{1,2}',
                r'\d{1,2}/\d{1,2}/\d{4}',
            ],
        }
    
    def _build_stop_words(self) -> Set[str]:
        """构建停用词列表"""
        return {
            '的', '了', '在', '是', '有', '和', '与', '及', '或', '但', '而', '则', '因此', '所以',
            '如果', '虽然', '但是', '因为', '所以', '由于', '通过', '根据', '按照', '依据',
            '进行', '实现', '完成', '达到', '获得', '取得', '形成', '产生', '出现', '发生',
            '可以', '能够', '应该', '必须', '需要', '要求', '规定', '标准', '方法', '技术',
            '工艺', '过程', '步骤', '阶段', '环节', '方面', '内容', '特点', '性质', '性能',
            '质量', '效果', '结果', '影响', '作用', '意义', '价值', '优势', '缺点', '问题',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        }
    
    def _build_steel_terms(self) -> Dict[SteelEntityType, Set[str]]:
        """构建钢铁领域术语词典"""
        return {
            SteelEntityType.STEEL_GRADE: set(STEEL_GRADES),
            SteelEntityType.STEEL_TYPE: set(STEEL_TYPES),
            SteelEntityType.ALLOY_ELEMENT: set(ALLOY_ELEMENTS),
            SteelEntityType.MATERIAL_PROPERTY: set(MATERIAL_PROPERTIES),
            SteelEntityType.PROCESS: set(PROCESSES),
            SteelEntityType.EQUIPMENT: set(EQUIPMENT),
            SteelEntityType.APPLICATION: set(APPLICATIONS),
            SteelEntityType.STANDARD: set(STANDARDS),
        }
    
    def extract_entities(self, text: str, min_confidence: float = 0.5) -> List[SteelEntityMention]:
        """
        从文本中抽取钢铁领域实体
        
        Args:
            text: 输入文本
            min_confidence: 最小置信度阈值
            
        Returns:
            实体提及列表
        """
        entities = []
        
        # 使用正则表达式模式匹配
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_text = match.group().strip()
                    
                    # 过滤停用词和过短的实体
                    if (len(entity_text) < 2 or 
                        entity_text.lower() in self.stop_words or
                        not self._is_valid_entity(entity_text, entity_type)):
                        continue
                    
                    # 计算置信度
                    confidence = self._calculate_confidence(entity_text, entity_type, text, match.start())
                    
                    if confidence >= min_confidence:
                        # 获取上下文
                        context = self._get_context(text, match.start(), match.end())
                        
                        entity = SteelEntityMention(
                            text=entity_text,
                            start_pos=match.start(),
                            end_pos=match.end(),
                            entity_type=entity_type,
                            confidence=confidence,
                            context=context
                        )
                        entities.append(entity)
        
        # 使用术语词典匹配
        for entity_type, terms in self.steel_terms.items():
            for term in terms:
                if term in text:
                    start_pos = text.find(term)
                    if start_pos != -1:
                        confidence = 0.9  # 词典匹配置信度较高
                        context = self._get_context(text, start_pos, start_pos + len(term))
                        
                        entity = SteelEntityMention(
                            text=term,
                            start_pos=start_pos,
                            end_pos=start_pos + len(term),
                            entity_type=entity_type,
                            confidence=confidence,
                            context=context
                        )
                        entities.append(entity)
        
        # 去重和合并
        entities = self._deduplicate_entities(entities)
        
        logger.info(f"Extracted {len(entities)} steel entities from text")
        return entities
    
    def _is_valid_entity(self, text: str, entity_type: SteelEntityType) -> bool:
        """验证实体是否有效"""
        if len(text) < 1:
            return False
        
        # 检查是否包含特殊字符（除了钢种等特殊情况）
        if entity_type not in [SteelEntityType.STEEL_GRADE, SteelEntityType.STANDARD]:
            if re.search(r'[^\w\s\u4e00-\u9fff\-\.]', text):
                return False
        
        return True
    
    def _calculate_confidence(self, text: str, entity_type: SteelEntityType, full_text: str, position: int) -> float:
        """计算实体置信度"""
        confidence = 0.5  # 基础置信度
        
        # 长度因子
        if len(text) > 5:
            confidence += 0.1
        elif len(text) < 3:
            confidence -= 0.1
        
        # 位置因子（标题、开头等位置权重更高）
        if position < 100:  # 文本开头
            confidence += 0.1
        
        # 上下文因子
        context = self._get_context(full_text, position, position + len(text))
        steel_keywords = ['钢铁', '钢材', '钢种', '性能', '工艺', '设备', '应用', '标准']
        if any(keyword in context.lower() for keyword in steel_keywords):
            confidence += 0.2
        
        # 实体类型特定规则
        if entity_type == SteelEntityType.STEEL_GRADE:
            if re.match(r'[QAT]\d+[A-Z]?', text):
                confidence += 0.3
        elif entity_type == SteelEntityType.ALLOY_ELEMENT:
            if text in ALLOY_ELEMENTS:
                confidence += 0.3
        elif entity_type == SteelEntityType.STANDARD:
            if re.match(r'[A-Z]{2,4}\s*\d+', text):
                confidence += 0.3
        
        return min(1.0, max(0.0, confidence))
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """获取实体上下文"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _deduplicate_entities(self, entities: List[SteelEntityMention]) -> List[SteelEntityMention]:
        """去重实体"""
        # 按位置排序
        entities.sort(key=lambda x: x.start_pos)
        
        deduplicated = []
        for entity in entities:
            # 检查是否与已有实体重叠
            is_duplicate = False
            for existing in deduplicated:
                if (entity.start_pos < existing.end_pos and 
                    entity.end_pos > existing.start_pos):
                    # 如果新实体置信度更高，替换
                    if entity.confidence > existing.confidence:
                        deduplicated.remove(existing)
                        break
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                deduplicated.append(entity)
        
        return deduplicated


class SteelRelationExtractor:
    """钢铁领域关系抽取器"""
    
    def __init__(self):
        self.patterns = self._build_patterns()
        self.entity_extractor = SteelEntityExtractor()
    
    def _build_patterns(self) -> Dict[SteelRelationType, List[str]]:
        """构建钢铁领域关系抽取模式（增强版）"""
        return {
            SteelRelationType.CONTAINS: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:含有|包含|包括|含|由)\s*([\w\u4e00-\u9fff]+)\s*(?:组成|构成|元素|成分)?',
                r'([\w\u4e00-\u9fff#]+)\s*(?:的|中)\s*(?:成分|组成|元素|化学成分)\s*(?:包括|含有|为|有)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:添加|加入|掺入)\s*([\w\u4e00-\u9fff]+)',
            ],
            SteelRelationType.COMPOSED_OF: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:由|通过)\s*([\w\u4e00-\u9fff]+)\s*(?:组成|构成|形成)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:主要|主要由)\s*([\w\u4e00-\u9fff]+)',
            ],
            SteelRelationType.HAS_PROPERTY: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:具有|拥有|具备|表现出|有着)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:的|其)\s*([\w\u4e00-\u9fff]+)\s*(?:为|是|达到|≥|≤|>|<)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:的|其)\s*(?:性能|特性|性质)\s*(?:包括|为|是|有)\s*([\w\u4e00-\u9fff]+)',
            ],
            SteelRelationType.PRODUCED_BY: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:通过|采用|使用|经过|由)\s*([\w\u4e00-\u9fff]+)\s*(?:生产|制造|制备|加工|处理)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:由|通过|经)\s*([\w\u4e00-\u9fff]+)\s*(?:工艺|方法|技术|流程)\s*(?:生产|制造|加工)',
                r'(?:采用|使用)\s*([\w\u4e00-\u9fff]+)\s*(?:工艺|方法|技术)\s*(?:生产|制造)\s*([\w\u4e00-\u9fff#]+)',
            ],
            SteelRelationType.USES_EQUIPMENT: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:使用|采用|利用|通过)\s*([\w\u4e00-\u9fff]+)\s*(?:设备|装置|机械|炉)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:在|通过)\s*([\w\u4e00-\u9fff]+)\s*(?:上|中)\s*(?:进行|完成|实现)',
                r'在\s*([\w\u4e00-\u9fff]+)\s*(?:中|上|内)\s*(?:生产|制造|加工)\s*([\w\u4e00-\u9fff#]+)',
            ],
            SteelRelationType.USED_IN: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:用于|应用于|适用于|广泛应用于)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:在|于)\s*([\w\u4e00-\u9fff]+)\s*(?:中|方面|领域|行业)\s*(?:使用|应用)',
                r'([\w\u4e00-\u9fff]+)\s*(?:需要|使用|采用)\s*([\w\u4e00-\u9fff#]+)',
            ],
            SteelRelationType.SUITABLE_FOR: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:适合|适用于|适宜|可用于)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:可以|能够|可)\s*(?:用于|应用于|满足)\s*([\w\u4e00-\u9fff]+)',
            ],
            SteelRelationType.COMPLIES_WITH: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:符合|遵循|遵守|满足|达到)\s*([\w\u4e00-\u9fff/\-\d]+)\s*(?:标准|规范|要求)?',
                r'([\w\u4e00-\u9fff#]+)\s*(?:按照|依据|根据|参照)\s*([\w\u4e00-\u9fff/\-\d]+)\s*(?:标准|规范|要求)',
                r'([\w\u4e00-\u9fff/\-\d]+)\s*(?:标准|规范)\s*(?:的|对)\s*([\w\u4e00-\u9fff#]+)',
            ],
            SteelRelationType.IMPROVES: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:提高|改善|增强|提升|增加)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:使|让|能使|可使)\s*([\w\u4e00-\u9fff]+)\s*(?:提高|改善|增强|提升)',
                r'(?:添加|加入)\s*([\w\u4e00-\u9fff#]+)\s*(?:可以|能够|可)\s*(?:提高|改善|增强)\s*([\w\u4e00-\u9fff]+)',
            ],
            SteelRelationType.REDUCES: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:降低|减少|减轻|降低|减小)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:使|让|能使|可使)\s*([\w\u4e00-\u9fff]+)\s*(?:降低|减少|减轻|减小)',
            ],
            SteelRelationType.APPLIES_TO: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:应用于|用于|适用于)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff]+)\s*(?:采用|使用)\s*([\w\u4e00-\u9fff#]+)\s*(?:技术|工艺|方法)',
            ],
            SteelRelationType.REQUIRES_TECHNOLOGY: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:需要|要求|必须)\s*([\w\u4e00-\u9fff]+)\s*(?:技术|工艺|方法)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:的|其)\s*(?:生产|制造|加工)\s*(?:需要|要求)\s*([\w\u4e00-\u9fff]+)',
            ],
            SteelRelationType.RELATED_TO: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:与|和|及)\s*([\w\u4e00-\u9fff#]+)\s*(?:相关|有关|联系|关联)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:和|与)\s*([\w\u4e00-\u9fff#]+)\s*(?:之间|的)\s*(?:关系|关联)',
            ],
            SteelRelationType.PART_OF: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:是|为|作为)\s*([\w\u4e00-\u9fff#]+)\s*(?:的|中)\s*(?:一部分|组成部分|部分|一种)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:属于|归入|归属)\s*([\w\u4e00-\u9fff#]+)',
            ],
            SteelRelationType.CAUSES: [
                r'([\w\u4e00-\u9fff#]+)\s*(?:导致|引起|造成|产生|引发)\s*([\w\u4e00-\u9fff]+)',
                r'([\w\u4e00-\u9fff#]+)\s*(?:使|让|能使|可使)\s*([\w\u4e00-\u9fff]+)\s*(?:发生|出现|产生)',
            ],
        }
    
    def extract_relations(self, text: str, entities: List[SteelEntityMention], 
                         min_confidence: float = 0.5) -> List[SteelRelationMention]:
        """
        从文本中抽取钢铁领域关系
        
        Args:
            text: 输入文本
            entities: 已识别的实体列表
            min_confidence: 最小置信度阈值
            
        Returns:
            关系提及列表
        """
        relations = []
        
        # 创建实体位置映射
        entity_positions = {entity.text: (entity.start_pos, entity.end_pos) for entity in entities}
        
        for relation_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    source_text = match.group(1).strip()
                    target_text = match.group(2).strip()
                    
                    # 检查是否为已知实体
                    if (source_text not in entity_positions or 
                        target_text not in entity_positions):
                        continue
                    
                    # 计算置信度
                    confidence = self._calculate_relation_confidence(
                        source_text, target_text, relation_type, text, match.start()
                    )
                    
                    if confidence >= min_confidence:
                        source_start, source_end = entity_positions[source_text]
                        target_start, target_end = entity_positions[target_text]
                        
                        relation = SteelRelationMention(
                            source_text=source_text,
                            target_text=target_text,
                            relation_type=relation_type,
                            confidence=confidence,
                            context=self._get_context(text, match.start(), match.end()),
                            source_start=source_start,
                            source_end=source_end,
                            target_start=target_start,
                            target_end=target_end
                        )
                        relations.append(relation)
        
        # 去重
        relations = self._deduplicate_relations(relations)
        
        logger.info(f"Extracted {len(relations)} steel relations from text")
        return relations
    
    def _calculate_relation_confidence(self, source: str, target: str, 
                                     relation_type: SteelRelationType, text: str, position: int) -> float:
        """计算关系置信度"""
        confidence = 0.5  # 基础置信度
        
        # 实体长度因子
        if len(source) > 2 and len(target) > 2:
            confidence += 0.1
        
        # 位置因子
        if position < 200:  # 文本开头
            confidence += 0.1
        
        # 上下文因子
        context = self._get_context(text, position, position + 50)
        steel_keywords = ['钢铁', '钢材', '钢种', '性能', '工艺', '设备', '应用', '标准']
        if any(keyword in context.lower() for keyword in steel_keywords):
            confidence += 0.1
        
        return min(1.0, max(0.0, confidence))
    
    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """获取关系上下文"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def _deduplicate_relations(self, relations: List[SteelRelationMention]) -> List[SteelRelationMention]:
        """去重关系"""
        seen = set()
        deduplicated = []
        
        for relation in relations:
            key = (relation.source_text, relation.target_text, relation.relation_type)
            if key not in seen:
                seen.add(key)
                deduplicated.append(relation)
        
        return deduplicated
