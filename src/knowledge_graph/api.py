"""
钢铁领域知识图谱API接口

提供RESTful API接口来访问知识图谱功能。
"""

import logging
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
from datetime import datetime

from .models import SteelEntityType, SteelRelationType
from .builder import SteelKnowledgeGraphBuilder
from .query import SteelKnowledgeGraphQuery
from ..api.auth import _get_current_user as get_current_user
from ..api.models import User

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge-graph"])

# 全局知识图谱实例
knowledge_graph_builder = SteelKnowledgeGraphBuilder()
knowledge_graph_query = None


class EntitySearchRequest(BaseModel):
    """实体搜索请求"""
    query: str = Field(..., description="搜索查询")
    entity_types: Optional[List[str]] = Field(None, description="实体类型过滤")
    min_confidence: float = Field(0.0, description="最小置信度")
    limit: int = Field(100, description="结果数量限制")


class EntitySearchResponse(BaseModel):
    """实体搜索响应"""
    entities: List[Dict[str, Any]]
    total_count: int
    confidence_scores: Dict[str, float]


class RelatedEntitiesRequest(BaseModel):
    """相关实体请求"""
    entity_id: str = Field(..., description="实体ID")
    relation_types: Optional[List[str]] = Field(None, description="关系类型过滤")
    max_depth: int = Field(1, description="最大深度")


class PathRequest(BaseModel):
    """路径查找请求"""
    source_id: str = Field(..., description="源实体ID")
    target_id: str = Field(..., description="目标实体ID")
    max_depth: int = Field(5, description="最大深度")


class SteelGradePropertiesRequest(BaseModel):
    """钢种性能查询请求"""
    properties: List[str] = Field(..., description="性能列表")
    min_confidence: float = Field(0.0, description="最小置信度")


class SteelCompositionRequest(BaseModel):
    """钢种成分查询请求"""
    steel_grade: str = Field(..., description="钢种名称")


class SteelApplicationsRequest(BaseModel):
    """钢种应用查询请求"""
    steel_grade: str = Field(..., description="钢种名称")


class SteelProcessesRequest(BaseModel):
    """钢种工艺查询请求"""
    steel_grade: str = Field(..., description="钢种名称")


class SteelStandardsRequest(BaseModel):
    """钢种标准查询请求"""
    steel_grade: str = Field(..., description="钢种名称")


class KnowledgeGraphStatsResponse(BaseModel):
    """知识图谱统计响应"""
    total_entities: int
    total_relations: int
    entity_type_counts: Dict[str, int]
    relation_type_counts: Dict[str, int]
    average_confidence: float


def get_knowledge_graph_query() -> SteelKnowledgeGraphQuery:
    """获取知识图谱查询实例"""
    global knowledge_graph_query
    if knowledge_graph_query is None:
        knowledge_graph_query = SteelKnowledgeGraphQuery(knowledge_graph_builder.knowledge_graph)
    return knowledge_graph_query


@router.post("/search/entities", response_model=EntitySearchResponse)
async def search_entities(
    request: EntitySearchRequest,
    current_user: User = Depends(get_current_user)
):
    """搜索实体"""
    try:
        query_engine = get_knowledge_graph_query()
        
        # 转换实体类型
        entity_types = None
        if request.entity_types:
            entity_types = [SteelEntityType(et) for et in request.entity_types]
        
        result = query_engine.search_entities(
            query=request.query,
            entity_types=entity_types,
            min_confidence=request.min_confidence,
            limit=request.limit
        )
        
        # 转换实体为字典
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
        
        return EntitySearchResponse(
            entities=entities,
            total_count=result.total_count,
            confidence_scores=result.confidence_scores
        )
    
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}")
async def get_entity(
    entity_id: str = Path(..., description="实体ID"),
    current_user: User = Depends(get_current_user)
):
    """获取实体详情"""
    try:
        query_engine = get_knowledge_graph_query()
        entity = query_engine.get_entity_by_id(entity_id)
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return {
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
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/name/{name}")
async def get_entity_by_name(
    name: str = Path(..., description="实体名称"),
    current_user: User = Depends(get_current_user)
):
    """根据名称获取实体"""
    try:
        query_engine = get_knowledge_graph_query()
        entity = query_engine.get_entity_by_name(name)
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return {
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
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity by name: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/type/{entity_type}")
async def get_entities_by_type(
    entity_type: str = Path(..., description="实体类型"),
    current_user: User = Depends(get_current_user)
):
    """根据类型获取实体"""
    try:
        query_engine = get_knowledge_graph_query()
        entity_type_enum = SteelEntityType(entity_type)
        entities = query_engine.get_entities_by_type(entity_type_enum)
        
        entity_list = []
        for entity in entities:
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
            entity_list.append(entity_dict)
        
        return {"entities": entity_list, "total_count": len(entity_list)}
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    except Exception as e:
        logger.error(f"Error getting entities by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entities/{entity_id}/related")
async def get_related_entities(
    entity_id: str = Path(..., description="实体ID"),
    request: RelatedEntitiesRequest = None,
    current_user: User = Depends(get_current_user)
):
    """获取相关实体"""
    try:
        query_engine = get_knowledge_graph_query()
        
        # 转换关系类型
        relation_types = None
        if request and request.relation_types:
            relation_types = [SteelRelationType(rt) for rt in request.relation_types]
        
        max_depth = request.max_depth if request else 1
        entities = query_engine.get_related_entities(
            entity_id=entity_id,
            relation_types=relation_types,
            max_depth=max_depth
        )
        
        entity_list = []
        for entity in entities:
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
            entity_list.append(entity_dict)
        
        return {"entities": entity_list, "total_count": len(entity_list)}
    
    except Exception as e:
        logger.error(f"Error getting related entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/path")
async def find_path(
    request: PathRequest,
    current_user: User = Depends(get_current_user)
):
    """查找实体间路径"""
    try:
        query_engine = get_knowledge_graph_query()
        relations = query_engine.find_path(
            source_id=request.source_id,
            target_id=request.target_id,
            max_depth=request.max_depth
        )
        
        relation_list = []
        for relation in relations:
            relation_dict = {
                "id": relation.id,
                "source_id": relation.source_id,
                "target_id": relation.target_id,
                "relation_type": relation.relation_type.value,
                "properties": relation.properties,
                "confidence": relation.confidence,
                "created_at": relation.created_at.isoformat(),
                "updated_at": relation.updated_at.isoformat()
            }
            relation_list.append(relation_dict)
        
        return {"relations": relation_list, "path_length": len(relation_list)}
    
    except Exception as e:
        logger.error(f"Error finding path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/steel-grades/by-properties")
async def get_steel_grades_by_properties(
    request: SteelGradePropertiesRequest,
    current_user: User = Depends(get_current_user)
):
    """根据性能查找钢种"""
    try:
        query_engine = get_knowledge_graph_query()
        steel_grades = query_engine.get_steel_grades_by_properties(
            properties=request.properties,
            min_confidence=request.min_confidence
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
        
        return {"steel_grades": grade_list, "total_count": len(grade_list)}
    
    except Exception as e:
        logger.error(f"Error getting steel grades by properties: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/steel-grades/composition")
async def get_steel_composition(
    request: SteelCompositionRequest,
    current_user: User = Depends(get_current_user)
):
    """获取钢种成分信息"""
    try:
        query_engine = get_knowledge_graph_query()
        composition = query_engine.get_steel_composition(steel_grade=request.steel_grade)
        
        return {"steel_grade": request.steel_grade, "composition": composition}
    
    except Exception as e:
        logger.error(f"Error getting steel composition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/steel-grades/applications")
async def get_steel_applications(
    request: SteelApplicationsRequest,
    current_user: User = Depends(get_current_user)
):
    """获取钢种应用领域"""
    try:
        query_engine = get_knowledge_graph_query()
        applications = query_engine.get_steel_applications_by_steel_grade(steel_grade=request.steel_grade)
        
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
        
        return {"steel_grade": request.steel_grade, "applications": app_list, "total_count": len(app_list)}
    
    except Exception as e:
        logger.error(f"Error getting steel applications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/steel-grades/processes")
async def get_steel_processes(
    request: SteelProcessesRequest,
    current_user: User = Depends(get_current_user)
):
    """获取钢种生产工艺"""
    try:
        query_engine = get_knowledge_graph_query()
        processes = query_engine.get_steel_processes(steel_grade=request.steel_grade)
        
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
        
        return {"steel_grade": request.steel_grade, "processes": process_list, "total_count": len(process_list)}
    
    except Exception as e:
        logger.error(f"Error getting steel processes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/steel-grades/standards")
async def get_steel_standards(
    request: SteelStandardsRequest,
    current_user: User = Depends(get_current_user)
):
    """获取钢种相关标准"""
    try:
        query_engine = get_knowledge_graph_query()
        standards = query_engine.get_steel_standards(steel_grade=request.steel_grade)
        
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
        
        return {"steel_grade": request.steel_grade, "standards": standard_list, "total_count": len(standard_list)}
    
    except Exception as e:
        logger.error(f"Error getting steel standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=KnowledgeGraphStatsResponse)
async def get_statistics(
    current_user: User = Depends(get_current_user)
):
    """获取知识图谱统计信息"""
    try:
        query_engine = get_knowledge_graph_query()
        stats = query_engine.get_statistics()
        
        return KnowledgeGraphStatsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entity-types")
async def get_entity_types(
    current_user: User = Depends(get_current_user)
):
    """获取所有实体类型"""
    try:
        entity_types = [{"value": et.value, "name": et.name} for et in SteelEntityType]
        return {"entity_types": entity_types}
    
    except Exception as e:
        logger.error(f"Error getting entity types: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relation-types")
async def get_relation_types(
    current_user: User = Depends(get_current_user)
):
    """获取所有关系类型"""
    try:
        relation_types = [{"value": rt.value, "name": rt.name} for rt in SteelRelationType]
        return {"relation_types": relation_types}
    
    except Exception as e:
        logger.error(f"Error getting relation types: {e}")
        raise HTTPException(status_code=500, detail=str(e))
