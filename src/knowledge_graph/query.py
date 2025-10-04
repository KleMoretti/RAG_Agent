"""
钢铁领域知识图谱查询引擎

提供各种查询接口来检索知识图谱中的信息。
"""

import logging
from typing import List, Dict, Set, Optional, Any, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict, deque

from .models import (
    SteelEntity, SteelRelation, SteelKnowledgeGraph,
    SteelEntityType, SteelRelationType
)

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """查询结果"""
    entities: List[SteelEntity]
    relations: List[SteelRelation]
    total_count: int
    confidence_scores: Dict[str, float]


class SteelKnowledgeGraphQuery:
    """钢铁领域知识图谱查询引擎"""
    
    def __init__(self, knowledge_graph: SteelKnowledgeGraph):
        self.kg = knowledge_graph
    
    def search_entities(self, 
                       query: str,
                       entity_types: Optional[List[SteelEntityType]] = None,
                       min_confidence: float = 0.0,
                       limit: int = 100) -> QueryResult:
        """
        搜索实体
        
        Args:
            query: 搜索查询
            entity_types: 实体类型过滤
            min_confidence: 最小置信度
            limit: 结果数量限制
            
        Returns:
            查询结果
        """
        logger.info(f"Searching entities with query: {query}")
        
        entities = []
        confidence_scores = {}
        
        # 在所有实体中搜索
        for entity in self.kg.entities.values():
            # 类型过滤
            if entity_types and entity.entity_type not in entity_types:
                continue
            
            # 置信度过滤
            if entity.confidence < min_confidence:
                continue
            
            # 名称匹配
            score = self._calculate_entity_score(entity, query)
            if score > 0:
                entities.append(entity)
                confidence_scores[entity.id] = score
        
        # 按分数排序
        entities.sort(key=lambda e: confidence_scores[e.id], reverse=True)
        
        # 限制结果数量
        entities = entities[:limit]
        
        logger.info(f"Found {len(entities)} entities")
        return QueryResult(
            entities=entities,
            relations=[],
            total_count=len(entities),
            confidence_scores=confidence_scores
        )
    
    def get_entity_by_id(self, entity_id: str) -> Optional[SteelEntity]:
        """根据ID获取实体"""
        return self.kg.entities.get(entity_id)
    
    def get_entity_by_name(self, name: str) -> Optional[SteelEntity]:
        """根据名称获取实体"""
        for entity in self.kg.entities.values():
            if entity.name == name or name in entity.aliases:
                return entity
        return None
    
    def get_entities_by_type(self, entity_type: SteelEntityType) -> List[SteelEntity]:
        """根据类型获取实体"""
        return self.kg.get_entities_by_type(entity_type)
    
    def get_entity_relations(self, entity_id: str) -> List[SteelRelation]:
        """获取实体的所有关系"""
        return self.kg.get_entity_relations(entity_id)
    
    def get_related_entities(self, 
                           entity_id: str,
                           relation_types: Optional[List[SteelRelationType]] = None,
                           max_depth: int = 1) -> List[SteelEntity]:
        """
        获取相关实体
        
        Args:
            entity_id: 实体ID
            relation_types: 关系类型过滤
            max_depth: 最大深度
            
        Returns:
            相关实体列表
        """
        logger.info(f"Getting related entities for {entity_id}, max_depth: {max_depth}")
        
        visited = set()
        related_entities = []
        queue = deque([(entity_id, 0)])  # (entity_id, depth)
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            
            # 获取当前实体的关系
            relations = self.kg.get_entity_relations(current_id)
            
            for relation in relations:
                # 关系类型过滤
                if relation_types and relation.relation_type not in relation_types:
                    continue
                
                # 获取相关实体
                related_id = relation.target_id if relation.source_id == current_id else relation.source_id
                
                if related_id not in visited:
                    related_entity = self.kg.entities.get(related_id)
                    if related_entity:
                        related_entities.append(related_entity)
                        if depth < max_depth:
                            queue.append((related_id, depth + 1))
        
        logger.info(f"Found {len(related_entities)} related entities")
        return related_entities
    
    def find_path(self, 
                 source_id: str, 
                 target_id: str,
                 max_depth: int = 5) -> List[SteelRelation]:
        """
        查找两个实体之间的路径
        
        Args:
            source_id: 源实体ID
            target_id: 目标实体ID
            max_depth: 最大深度
            
        Returns:
            路径关系列表
        """
        logger.info(f"Finding path from {source_id} to {target_id}")
        
        if source_id == target_id:
            return []
        
        # BFS搜索
        queue = deque([(source_id, [])])  # (current_id, path)
        visited = {source_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            if len(path) >= max_depth:
                continue
            
            # 获取当前实体的关系
            relations = self.kg.get_entity_relations(current_id)
            
            for relation in relations:
                next_id = relation.target_id if relation.source_id == current_id else relation.source_id
                
                if next_id == target_id:
                    return path + [relation]
                
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [relation]))
        
        logger.info("No path found")
        return []
    
    def get_steel_grades_by_properties(self, 
                                     properties: List[str],
                                     min_confidence: float = 0.0) -> List[SteelEntity]:
        """
        根据性能查找钢种
        
        Args:
            properties: 性能列表
            min_confidence: 最小置信度
            
        Returns:
            钢种实体列表
        """
        logger.info(f"Finding steel grades by properties: {properties}")
        
        steel_grades = self.kg.get_entities_by_type(SteelEntityType.STEEL_GRADE)
        matching_grades = []
        
        for grade in steel_grades:
            if grade.confidence < min_confidence:
                continue
            
            # 检查是否有相关性能关系
            relations = self.kg.get_entity_relations(grade.id)
            has_properties = set()
            
            for relation in relations:
                if relation.relation_type == SteelRelationType.HAS_PROPERTY:
                    related_entity = self.kg.entities.get(relation.target_id)
                    if related_entity and related_entity.entity_type == SteelEntityType.MATERIAL_PROPERTY:
                        has_properties.add(related_entity.name)
            
            # 检查是否包含所需性能
            if any(prop in has_properties for prop in properties):
                matching_grades.append(grade)
        
        logger.info(f"Found {len(matching_grades)} matching steel grades")
        return matching_grades
    
    def get_applications_by_steel_grade(self, steel_grade: str) -> List[SteelEntity]:
        """
        根据钢种查找应用领域
        
        Args:
            steel_grade: 钢种名称
            
        Returns:
            应用领域实体列表
        """
        logger.info(f"Finding applications for steel grade: {steel_grade}")
        
        # 查找钢种实体
        steel_entity = self.get_entity_by_name(steel_grade)
        if not steel_entity:
            return []
        
        applications = []
        relations = self.kg.get_entity_relations(steel_entity.id)
        
        for relation in relations:
            if relation.relation_type in [SteelRelationType.USED_IN, SteelRelationType.SUITABLE_FOR]:
                related_entity = self.kg.entities.get(relation.target_id)
                if related_entity and related_entity.entity_type == SteelEntityType.APPLICATION:
                    applications.append(related_entity)
        
        logger.info(f"Found {len(applications)} applications")
        return applications
    
    def get_steel_grades_by_application(self, application: str) -> List[SteelEntity]:
        """
        根据应用领域查找钢种
        
        Args:
            application: 应用领域名称
            
        Returns:
            钢种实体列表
        """
        logger.info(f"Finding steel grades for application: {application}")
        
        # 查找应用实体
        app_entity = self.get_entity_by_name(application)
        if not app_entity:
            return []
        
        steel_grades = []
        relations = self.kg.get_entity_relations(app_entity.id)
        
        for relation in relations:
            if relation.relation_type in [SteelRelationType.USED_IN, SteelRelationType.SUITABLE_FOR]:
                related_entity = self.kg.entities.get(relation.source_id)
                if related_entity and related_entity.entity_type == SteelEntityType.STEEL_GRADE:
                    steel_grades.append(related_entity)
        
        logger.info(f"Found {len(steel_grades)} steel grades")
        return steel_grades
    
    def get_steel_composition(self, steel_grade: str) -> Dict[str, Any]:
        """
        获取钢种成分信息
        
        Args:
            steel_grade: 钢种名称
            
        Returns:
            成分信息字典
        """
        logger.info(f"Getting composition for steel grade: {steel_grade}")
        
        steel_entity = self.get_entity_by_name(steel_grade)
        if not steel_entity:
            return {}
        
        composition = {}
        relations = self.kg.get_entity_relations(steel_entity.id)
        
        for relation in relations:
            if relation.relation_type in [SteelRelationType.CONTAINS, SteelRelationType.COMPOSED_OF]:
                related_entity = self.kg.entities.get(relation.target_id)
                if related_entity and related_entity.entity_type == SteelEntityType.ALLOY_ELEMENT:
                    composition[related_entity.name] = {
                        'confidence': relation.confidence,
                        'context': relation.properties.get('context', '')
                    }
        
        logger.info(f"Found composition with {len(composition)} elements")
        return composition
    
    def get_steel_processes(self, steel_grade: str) -> List[SteelEntity]:
        """
        获取钢种生产工艺
        
        Args:
            steel_grade: 钢种名称
            
        Returns:
            工艺实体列表
        """
        logger.info(f"Getting processes for steel grade: {steel_grade}")
        
        steel_entity = self.get_entity_by_name(steel_grade)
        if not steel_entity:
            return []
        
        processes = []
        relations = self.kg.get_entity_relations(steel_entity.id)
        
        for relation in relations:
            if relation.relation_type == SteelRelationType.PRODUCED_BY:
                related_entity = self.kg.entities.get(relation.target_id)
                if related_entity and related_entity.entity_type == SteelEntityType.PROCESS:
                    processes.append(related_entity)
        
        logger.info(f"Found {len(processes)} processes")
        return processes
    
    def get_steel_standards(self, steel_grade: str) -> List[SteelEntity]:
        """
        获取钢种相关标准
        
        Args:
            steel_grade: 钢种名称
            
        Returns:
            标准实体列表
        """
        logger.info(f"Getting standards for steel grade: {steel_grade}")
        
        steel_entity = self.get_entity_by_name(steel_grade)
        if not steel_entity:
            return []
        
        standards = []
        relations = self.kg.get_entity_relations(steel_entity.id)
        
        for relation in relations:
            if relation.relation_type == SteelRelationType.COMPLIES_WITH:
                related_entity = self.kg.entities.get(relation.target_id)
                if related_entity and related_entity.entity_type == SteelEntityType.STANDARD:
                    standards.append(related_entity)
        
        logger.info(f"Found {len(standards)} standards")
        return standards
    
    def _calculate_entity_score(self, entity: SteelEntity, query: str) -> float:
        """计算实体匹配分数"""
        query_lower = query.lower()
        name_lower = entity.name.lower()
        
        # 完全匹配
        if query_lower == name_lower:
            return 1.0
        
        # 包含匹配
        if query_lower in name_lower:
            return 0.8
        
        # 别名匹配
        for alias in entity.aliases:
            if query_lower == alias.lower():
                return 0.9
            if query_lower in alias.lower():
                return 0.7
        
        # 描述匹配
        if entity.description and query_lower in entity.description.lower():
            return 0.6
        
        # 属性匹配
        for prop_value in entity.properties.values():
            if isinstance(prop_value, str) and query_lower in prop_value.lower():
                return 0.5
        
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        return self.kg.get_statistics()
