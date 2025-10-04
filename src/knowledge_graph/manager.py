"""
钢铁领域知识图谱管理器

提供知识图谱的构建、管理和维护功能。
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from .builder import SteelKnowledgeGraphBuilder
from .query import SteelKnowledgeGraphQuery
from .models import SteelKnowledgeGraph

logger = logging.getLogger(__name__)


class SteelKnowledgeGraphManager:
    """钢铁领域知识图谱管理器"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.kg_file = self.data_dir / "knowledge_graph.json"
        self.builder = SteelKnowledgeGraphBuilder()
        self.query_engine = None
        
        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def build_from_processed_files(self) -> SteelKnowledgeGraph:
        """从已处理的文件中构建知识图谱"""
        logger.info("Building knowledge graph from processed files")
        
        processed_dir = self.data_dir / "processed"
        if not processed_dir.exists():
            logger.warning("No processed files directory found")
            return self.builder.knowledge_graph
        
        # 读取已处理的文件
        processed_files = []
        for file_path in processed_dir.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    processed_files.append({
                        'text': content,
                        'source': file_path.name
                    })
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                continue
        
        # 构建知识图谱
        if processed_files:
            self.builder.build_from_documents(processed_files)
            self._save_knowledge_graph()
            logger.info(f"Built knowledge graph from {len(processed_files)} files")
        else:
            logger.warning("No processed files found")
        
        return self.builder.knowledge_graph
    
    def build_from_text(self, text: str, source: str = "manual") -> SteelKnowledgeGraph:
        """从文本构建知识图谱"""
        logger.info(f"Building knowledge graph from text (source: {source})")
        
        self.builder.build_from_text(text, source)
        self._save_knowledge_graph()
        
        return self.builder.knowledge_graph
    
    def load_knowledge_graph(self) -> SteelKnowledgeGraph:
        """加载知识图谱"""
        if self.kg_file.exists():
            try:
                self.builder.load_from_file(str(self.kg_file))
                logger.info("Knowledge graph loaded from file")
            except Exception as e:
                logger.error(f"Error loading knowledge graph: {e}")
                logger.info("Creating new knowledge graph")
                self.builder = SteelKnowledgeGraphBuilder()
        else:
            logger.info("No existing knowledge graph found, creating new one")
            self.builder = SteelKnowledgeGraphBuilder()
        
        return self.builder.knowledge_graph
    
    def save_knowledge_graph(self) -> None:
        """保存知识图谱"""
        self._save_knowledge_graph()
    
    def _save_knowledge_graph(self) -> None:
        """内部保存方法"""
        try:
            self.builder.save_to_file(str(self.kg_file))
            logger.info(f"Knowledge graph saved to {self.kg_file}")
        except Exception as e:
            logger.error(f"Error saving knowledge graph: {e}")
    
    def get_query_engine(self) -> SteelKnowledgeGraphQuery:
        """获取查询引擎"""
        if self.query_engine is None:
            self.query_engine = SteelKnowledgeGraphQuery(self.builder.knowledge_graph)
        return self.query_engine
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        return self.builder.get_statistics()
    
    def search_entities(self, query: str, entity_types: Optional[List[str]] = None, 
                       min_confidence: float = 0.0, limit: int = 100) -> Dict[str, Any]:
        """搜索实体"""
        query_engine = self.get_query_engine()
        
        # 转换实体类型
        entity_type_enums = None
        if entity_types:
            from .models import SteelEntityType
            entity_type_enums = [SteelEntityType(et) for et in entity_types]
        
        result = query_engine.search_entities(
            query=query,
            entity_types=entity_type_enums,
            min_confidence=min_confidence,
            limit=limit
        )
        
        # 转换结果
        entities = []
        for entity in result.entities:
            entity_dict = {
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type.value,
                "description": entity.description,
                "properties": entity.properties,
                "aliases": entity.aliases,
                "confidence": entity.confidence,
                "created_at": entity.created_at.isoformat(),
                "updated_at": entity.updated_at.isoformat()
            }
            entities.append(entity_dict)
        
        return {
            "entities": entities,
            "total_count": result.total_count,
            "confidence_scores": result.confidence_scores
        }
    
    def get_steel_grades_by_properties(self, properties: List[str], 
                                     min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """根据性能查找钢种"""
        query_engine = self.get_query_engine()
        steel_grades = query_engine.get_steel_grades_by_properties(
            properties=properties,
            min_confidence=min_confidence
        )
        
        grade_list = []
        for grade in steel_grades:
            grade_dict = {
                "id": grade.id,
                "name": grade.name,
                "entity_type": grade.entity_type.value,
                "description": grade.description,
                "properties": grade.properties,
                "aliases": grade.aliases,
                "confidence": grade.confidence,
                "created_at": grade.created_at.isoformat(),
                "updated_at": grade.updated_at.isoformat()
            }
            grade_list.append(grade_dict)
        
        return grade_list
    
    def get_steel_composition(self, steel_grade: str) -> Dict[str, Any]:
        """获取钢种成分信息"""
        query_engine = self.get_query_engine()
        return query_engine.get_steel_composition(steel_grade=steel_grade)
    
    def get_steel_applications(self, steel_grade: str) -> List[Dict[str, Any]]:
        """获取钢种应用领域"""
        query_engine = self.get_query_engine()
        applications = query_engine.get_steel_applications_by_steel_grade(steel_grade=steel_grade)
        
        app_list = []
        for app in applications:
            app_dict = {
                "id": app.id,
                "name": app.name,
                "entity_type": app.entity_type.value,
                "description": app.description,
                "properties": app.properties,
                "aliases": app.aliases,
                "confidence": app.confidence,
                "created_at": app.created_at.isoformat(),
                "updated_at": app.updated_at.isoformat()
            }
            app_list.append(app_dict)
        
        return app_list
    
    def get_steel_processes(self, steel_grade: str) -> List[Dict[str, Any]]:
        """获取钢种生产工艺"""
        query_engine = self.get_query_engine()
        processes = query_engine.get_steel_processes(steel_grade=steel_grade)
        
        process_list = []
        for process in processes:
            process_dict = {
                "id": process.id,
                "name": process.name,
                "entity_type": process.entity_type.value,
                "description": process.description,
                "properties": process.properties,
                "aliases": process.aliases,
                "confidence": process.confidence,
                "created_at": process.created_at.isoformat(),
                "updated_at": process.updated_at.isoformat()
            }
            process_list.append(process_dict)
        
        return process_list
    
    def get_steel_standards(self, steel_grade: str) -> List[Dict[str, Any]]:
        """获取钢种相关标准"""
        query_engine = self.get_query_engine()
        standards = query_engine.get_steel_standards(steel_grade=steel_grade)
        
        standard_list = []
        for standard in standards:
            standard_dict = {
                "id": standard.id,
                "name": standard.name,
                "entity_type": standard.entity_type.value,
                "description": standard.description,
                "properties": standard.properties,
                "aliases": standard.aliases,
                "confidence": standard.confidence,
                "created_at": standard.created_at.isoformat(),
                "updated_at": standard.updated_at.isoformat()
            }
            standard_list.append(standard_dict)
        
        return standard_list
    
    def rebuild_knowledge_graph(self) -> SteelKnowledgeGraph:
        """重建知识图谱"""
        logger.info("Rebuilding knowledge graph")
        
        # 重新构建
        self.builder = SteelKnowledgeGraphBuilder()
        kg = self.build_from_processed_files()
        
        # 更新查询引擎
        self.query_engine = SteelKnowledgeGraphQuery(kg)
        
        logger.info("Knowledge graph rebuilt successfully")
        return kg
    
    def export_knowledge_graph(self, export_path: str) -> None:
        """导出知识图谱"""
        try:
            self.builder.save_to_file(export_path)
            logger.info(f"Knowledge graph exported to {export_path}")
        except Exception as e:
            logger.error(f"Error exporting knowledge graph: {e}")
            raise
    
    def import_knowledge_graph(self, import_path: str) -> SteelKnowledgeGraph:
        """导入知识图谱"""
        try:
            self.builder.load_from_file(import_path)
            self.query_engine = SteelKnowledgeGraphQuery(self.builder.knowledge_graph)
            logger.info(f"Knowledge graph imported from {import_path}")
            return self.builder.knowledge_graph
        except Exception as e:
            logger.error(f"Error importing knowledge graph: {e}")
            raise
