"""
钢铁领域知识图谱构建器

负责从文档中构建钢铁领域知识图谱。
采用标准本体（Ontology）作为基准，构建蛛网结构的知识图谱。
"""

import logging
import uuid
from typing import List, Dict, Set, Optional, Any, Tuple
from pathlib import Path
import json
from datetime import datetime

from .models import (
    SteelEntity, SteelRelation, SteelKnowledgeGraph,
    SteelEntityType, SteelRelationType
)
from .steel_extractor import SteelEntityExtractor, SteelRelationExtractor
from .steel_ontology import get_steel_ontology, CoreEntityType, FeatureEntityType

logger = logging.getLogger(__name__)


class SteelKnowledgeGraphBuilder:
    """钢铁领域知识图谱构建器（基于标准本体）"""
    
    def __init__(self):
        self.entity_extractor = SteelEntityExtractor()
        self.relation_extractor = SteelRelationExtractor()
        self.knowledge_graph = SteelKnowledgeGraph()
        self.entity_name_to_id: Dict[str, str] = {}
        self.entity_aliases: Dict[str, str] = {}  # 别名 -> 实体ID
        self.ontology = get_steel_ontology()  # 加载标准本体
        self._initialize_from_ontology()  # 初始化基准图谱
    
    def _initialize_from_ontology(self):
        """从标准本体初始化基准知识图谱"""
        logger.info("正在从标准本体初始化基准知识图谱...")
        
        # 添加核心实体
        for entity_name, entity_def in self.ontology.core_entities.items():
            entity_id = str(uuid.uuid4())
            entity = SteelEntity(
                id=entity_id,
                name=entity_def.name,
                entity_type=SteelEntityType(entity_def.entity_type.value),
                description=entity_def.description,
                properties={
                    'is_standard': True,
                    'aliases': entity_def.aliases,
                    'typical_values': entity_def.typical_values or []
                },
                aliases=entity_def.aliases,
                confidence=1.0
            )
            self.knowledge_graph.add_entity(entity)
            self.entity_name_to_id[entity_name] = entity_id
            
            # 添加别名映射
            for alias in entity_def.aliases:
                self.entity_aliases[alias] = entity_id
        
        # 添加特征实体
        for entity_name, entity_def in self.ontology.standard_entities.items():
            entity_id = str(uuid.uuid4())
            entity = SteelEntity(
                id=entity_id,
                name=entity_def.name,
                entity_type=SteelEntityType(entity_def.entity_type.value),
                description=entity_def.description,
                properties={
                    'is_standard': True,
                    'aliases': entity_def.aliases,
                    'category': self.ontology.get_entity_category(entity_def.entity_type.value)
                },
                aliases=entity_def.aliases,
                confidence=1.0
            )
            self.knowledge_graph.add_entity(entity)
            self.entity_name_to_id[entity_name] = entity_id
            
            # 添加别名映射
            for alias in entity_def.aliases:
                self.entity_aliases[alias] = entity_id
        
        # 添加标准关系
        for relation_def in self.ontology.standard_relations:
            source_id = self.entity_name_to_id.get(relation_def.source)
            target_id = self.entity_name_to_id.get(relation_def.target)
            
            if source_id and target_id:
                relation = SteelRelation(
                    id=str(uuid.uuid4()),
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=SteelRelationType(relation_def.relation_type),
                    properties={
                        'is_standard': True,
                        'description': relation_def.description
                    },
                    confidence=1.0
                )
                self.knowledge_graph.add_relation(relation)
        
        logger.info(
            f"✅ 基准知识图谱已初始化: "
            f"{len(self.ontology.core_entities)} 个核心实体, "
            f"{len(self.ontology.standard_entities)} 个特征实体, "
            f"{len(self.ontology.standard_relations)} 个标准关系"
        )
    
    def build_from_text(self, text: str, source: str = "unknown") -> SteelKnowledgeGraph:
        """
        从文本构建知识图谱
        
        Args:
            text: 输入文本
            source: 文本来源
            
        Returns:
            构建的知识图谱
        """
        logger.info(f"Building knowledge graph from text (source: {source})")
        
        # 抽取实体
        entity_mentions = self.entity_extractor.extract_entities(text)
        logger.info(f"Extracted {len(entity_mentions)} entity mentions")
        
        # 抽取关系
        relation_mentions = self.relation_extractor.extract_relations(text, entity_mentions)
        logger.info(f"Extracted {len(relation_mentions)} relation mentions")
        
        # 创建实体
        entities = self._create_entities(entity_mentions, source)
        logger.info(f"Created {len(entities)} entities")
        
        # 创建关系
        relations = self._create_relations(relation_mentions, source)
        logger.info(f"Created {len(relations)} relations")
        
        # 添加到知识图谱
        for entity in entities:
            self.knowledge_graph.add_entity(entity)
        
        for relation in relations:
            self.knowledge_graph.add_relation(relation)
        
        logger.info(f"Knowledge graph built successfully: {len(self.knowledge_graph.entities)} entities, {len(self.knowledge_graph.relations)} relations")
        return self.knowledge_graph
    
    def build_from_documents(self, documents: List[Dict[str, Any]]) -> SteelKnowledgeGraph:
        """
        从多个文档构建知识图谱
        
        Args:
            documents: 文档列表，每个文档包含 'text' 和 'source' 字段
            
        Returns:
            构建的知识图谱
        """
        logger.info(f"Building knowledge graph from {len(documents)} documents")
        
        for doc in documents:
            text = doc.get('text', '')
            source = doc.get('source', 'unknown')
            if text:
                self.build_from_text(text, source)
        
        logger.info(f"Final knowledge graph: {len(self.knowledge_graph.entities)} entities, {len(self.knowledge_graph.relations)} relations")
        return self.knowledge_graph
    
    def _create_entities(self, entity_mentions: List, source: str) -> List[SteelEntity]:
        """创建实体"""
        entities = []
        
        for mention in entity_mentions:
            # 检查是否已存在相同名称的实体
            entity_id = self._get_or_create_entity_id(mention.text, mention.entity_type)
            
            if entity_id not in self.knowledge_graph.entities:
                # 创建新实体
                entity = SteelEntity(
                    id=entity_id,
                    name=mention.text,
                    entity_type=mention.entity_type,
                    description=self._generate_entity_description(mention),
                    properties={
                        'confidence': mention.confidence,
                        'context': mention.context,
                        'source': source,
                        'first_mentioned': datetime.utcnow().isoformat()
                    },
                    aliases=[],
                    confidence=mention.confidence
                )
                entities.append(entity)
                self.entity_name_to_id[mention.text] = entity_id
            else:
                # 更新现有实体
                existing_entity = self.knowledge_graph.entities[entity_id]
                if mention.confidence > existing_entity.confidence:
                    existing_entity.confidence = mention.confidence
                    existing_entity.properties['confidence'] = mention.confidence
                    existing_entity.properties['context'] = mention.context
                    existing_entity.updated_at = datetime.utcnow()
        
        return entities
    
    def _create_relations(self, relation_mentions: List, source: str) -> List[SteelRelation]:
        """创建关系"""
        relations = []
        
        for mention in relation_mentions:
            # 获取源实体和目标实体的ID
            source_id = self._get_entity_id_by_name(mention.source_text)
            target_id = self._get_entity_id_by_name(mention.target_text)
            
            if source_id and target_id:
                relation_id = str(uuid.uuid4())
                
                relation = SteelRelation(
                    id=relation_id,
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=mention.relation_type,
                    properties={
                        'confidence': mention.confidence,
                        'context': mention.context,
                        'source': source,
                        'created_at': datetime.utcnow().isoformat()
                    },
                    confidence=mention.confidence
                )
                relations.append(relation)
        
        return relations
    
    def _get_or_create_entity_id(self, name: str, entity_type: SteelEntityType) -> str:
        """获取或创建实体ID"""
        # 首先检查是否已存在
        if name in self.entity_name_to_id:
            return self.entity_name_to_id[name]
        
        # 检查别名
        if name in self.entity_aliases:
            return self.entity_aliases[name]
        
        # 创建新ID
        entity_id = str(uuid.uuid4())
        self.entity_name_to_id[name] = entity_id
        return entity_id
    
    def _get_entity_id_by_name(self, name: str) -> Optional[str]:
        """根据名称获取实体ID"""
        # 直接匹配
        if name in self.entity_name_to_id:
            return self.entity_name_to_id[name]
        
        # 别名匹配
        if name in self.entity_aliases:
            return self.entity_aliases[name]
        
        # 模糊匹配
        for entity_name, entity_id in self.entity_name_to_id.items():
            if self._is_similar_name(name, entity_name):
                return entity_id
        
        return None
    
    def _is_similar_name(self, name1: str, name2: str) -> bool:
        """判断两个名称是否相似"""
        # 简单的相似度判断
        if name1 == name2:
            return True
        
        # 去除空格和特殊字符后比较
        clean1 = ''.join(name1.split()).lower()
        clean2 = ''.join(name2.split()).lower()
        
        if clean1 == clean2:
            return True
        
        # 包含关系
        if clean1 in clean2 or clean2 in clean1:
            return True
        
        return False
    
    def _generate_entity_description(self, mention) -> str:
        """生成实体描述"""
        descriptions = {
            SteelEntityType.STEEL_GRADE: f"钢种 {mention.text}",
            SteelEntityType.STEEL_TYPE: f"钢材类型 {mention.text}",
            SteelEntityType.ALLOY_ELEMENT: f"合金元素 {mention.text}",
            SteelEntityType.MATERIAL_PROPERTY: f"材料性能 {mention.text}",
            SteelEntityType.PROCESS: f"工艺 {mention.text}",
            SteelEntityType.EQUIPMENT: f"设备 {mention.text}",
            SteelEntityType.APPLICATION: f"应用领域 {mention.text}",
            SteelEntityType.STANDARD: f"标准 {mention.text}",
            SteelEntityType.COMPANY: f"公司 {mention.text}",
            SteelEntityType.PRODUCT: f"产品 {mention.text}",
        }
        
        return descriptions.get(mention.entity_type, f"实体 {mention.text}")
    
    def save_to_file(self, file_path: str) -> None:
        """保存知识图谱到文件"""
        data = {
            'entities': {
                eid: {
                    'id': entity.id,
                    'name': entity.name,
                    'entity_type': entity.entity_type.value,
                    'description': entity.description,
                    'properties': entity.properties,
                    'aliases': entity.aliases,
                    'confidence': entity.confidence,
                    'created_at': entity.created_at.isoformat(),
                    'updated_at': entity.updated_at.isoformat()
                }
                for eid, entity in self.knowledge_graph.entities.items()
            },
            'relations': {
                rid: {
                    'id': relation.id,
                    'source_id': relation.source_id,
                    'target_id': relation.target_id,
                    'relation_type': relation.relation_type.value,
                    'properties': relation.properties,
                    'confidence': relation.confidence,
                    'created_at': relation.created_at.isoformat(),
                    'updated_at': relation.updated_at.isoformat()
                }
                for rid, relation in self.knowledge_graph.relations.items()
            },
            'entity_index': {
                etype.value: list(eids) for etype, eids in self.knowledge_graph.entity_index.items()
            },
            'relation_index': {
                rtype.value: list(rids) for rtype, rids in self.knowledge_graph.relation_index.items()
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Knowledge graph saved to {file_path}")
    
    def load_from_file(self, file_path: str) -> SteelKnowledgeGraph:
        """从文件加载知识图谱"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 重建实体
        for eid, entity_data in data['entities'].items():
            entity = SteelEntity(
                id=entity_data['id'],
                name=entity_data['name'],
                entity_type=SteelEntityType(entity_data['entity_type']),
                description=entity_data.get('description'),
                properties=entity_data.get('properties', {}),
                aliases=entity_data.get('aliases', []),
                confidence=entity_data.get('confidence', 1.0),
                created_at=datetime.fromisoformat(entity_data['created_at']),
                updated_at=datetime.fromisoformat(entity_data['updated_at'])
            )
            self.knowledge_graph.entities[eid] = entity
        
        # 重建关系
        for rid, relation_data in data['relations'].items():
            relation = SteelRelation(
                id=relation_data['id'],
                source_id=relation_data['source_id'],
                target_id=relation_data['target_id'],
                relation_type=SteelRelationType(relation_data['relation_type']),
                properties=relation_data.get('properties', {}),
                confidence=relation_data.get('confidence', 1.0),
                created_at=datetime.fromisoformat(relation_data['created_at']),
                updated_at=datetime.fromisoformat(relation_data['updated_at'])
            )
            self.knowledge_graph.relations[rid] = relation
        
        # 重建索引
        self.knowledge_graph.entity_index = {
            SteelEntityType(etype): set(eids) for etype, eids in data['entity_index'].items()
        }
        self.knowledge_graph.relation_index = {
            SteelRelationType(rtype): set(rids) for rtype, rids in data['relation_index'].items()
        }
        
        logger.info(f"Knowledge graph loaded from {file_path}")
        return self.knowledge_graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        entity_type_counts = {}
        for entity_type in SteelEntityType:
            entities = self.knowledge_graph.get_entities_by_type(entity_type)
            entity_type_counts[entity_type.value] = len(entities)
        
        relation_type_counts = {}
        for relation_type in SteelRelationType:
            relations = self.knowledge_graph.get_relations_by_type(relation_type)
            relation_type_counts[relation_type.value] = len(relations)
        
        return {
            'total_entities': len(self.knowledge_graph.entities),
            'total_relations': len(self.knowledge_graph.relations),
            'entity_type_counts': entity_type_counts,
            'relation_type_counts': relation_type_counts,
            'average_confidence': self._calculate_average_confidence()
        }
    
    def _calculate_average_confidence(self) -> float:
        """计算平均置信度"""
        if not self.knowledge_graph.entities and not self.knowledge_graph.relations:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        for entity in self.knowledge_graph.entities.values():
            total_confidence += entity.confidence
            count += 1
        
        for relation in self.knowledge_graph.relations.values():
            total_confidence += relation.confidence
            count += 1
        
        return total_confidence / count if count > 0 else 0.0
