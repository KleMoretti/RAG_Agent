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

# 启动时自动加载已保存的知识图谱
def _initialize_knowledge_graph():
    """初始化知识图谱：自动加载已保存的数据"""
    global knowledge_graph_builder, knowledge_graph_query
    from pathlib import Path
    
    kg_file = Path("./data/knowledge_graph.json")
    if kg_file.exists():
        try:
            logger.info(f"正在加载知识图谱: {kg_file}")
            knowledge_graph_builder.load_from_file(str(kg_file))
            knowledge_graph_query = SteelKnowledgeGraphQuery(knowledge_graph_builder.knowledge_graph)
            
            # 输出统计信息
            stats = knowledge_graph_builder.get_statistics()
            logger.info(
                f"✅ 知识图谱已加载: {stats['total_entities']} 个实体, "
                f"{stats['total_relations']} 个关系"
            )
        except Exception as e:
            logger.error(f"❌ 加载知识图谱失败: {e}")
            logger.info("将使用空的知识图谱")
    else:
        logger.info(f"未找到知识图谱文件 ({kg_file})，将在首次构建时创建")

# 立即初始化
_initialize_knowledge_graph()


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
        # 返回实体类型值的数组，用于前端筛选
        entity_type_values = [et.value for et in SteelEntityType]
        return entity_type_values
    
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


@router.get("/graph-data")
async def get_graph_visualization_data(
    entity_types: Optional[str] = Query(None, description="实体类型过滤（逗号分隔）"),
    limit: int = Query(100, description="最大节点数量"),
    current_user: User = Depends(get_current_user)
):
    """
    获取知识图谱可视化数据（nodes + edges 格式）
    用于前端图谱渲染
    """
    try:
        query_engine = get_knowledge_graph_query()
        kg = knowledge_graph_builder.knowledge_graph
        
        # 过滤实体类型
        entity_type_filters = None
        if entity_types:
            entity_type_filters = [SteelEntityType(et.strip()) for et in entity_types.split(',')]
        
        # 获取实体
        all_entities = []
        if entity_type_filters:
            for etype in entity_type_filters:
                all_entities.extend(kg.get_entities_by_type(etype))
        else:
            all_entities = list(kg.entities.values())
        
        # 限制数量
        entities = all_entities[:limit]
        entity_ids = {e.id for e in entities}
        
        # 构建节点数据
        nodes = []
        for entity in entities:
            node = {
                "id": entity.id,
                "label": entity.name,
                "type": entity.entity_type.value,
                "description": entity.description,
                "confidence": entity.confidence,
                "properties": entity.properties,
            }
            nodes.append(node)
        
        # 获取这些实体之间的关系（边）
        edges = []
        for relation in kg.relations.values():
            if relation.source_id in entity_ids and relation.target_id in entity_ids:
                edge = {
                    "id": relation.id,
                    "source": relation.source_id,
                    "target": relation.target_id,
                    "type": relation.relation_type.value,
                    "label": relation.relation_type.value,
                    "confidence": relation.confidence,
                    "properties": relation.properties,
                }
                edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "available_types": list(set(e.entity_type.value for e in all_entities))
        }
    
    except Exception as e:
        logger.error(f"Error getting graph visualization data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/graph-data")
async def search_graph_visualization_data(
    request: EntitySearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    根据搜索条件获取知识图谱可视化数据
    返回搜索结果实体及其关系
    """
    try:
        query_engine = get_knowledge_graph_query()
        kg = knowledge_graph_builder.knowledge_graph
        
        # 转换实体类型
        entity_types = None
        if request.entity_types:
            entity_types = [SteelEntityType(et) for et in request.entity_types]
        
        # 搜索实体
        result = query_engine.search_entities(
            query=request.query,
            entity_types=entity_types,
            min_confidence=request.min_confidence,
            limit=request.limit
        )
        
        entities = result.entities
        entity_ids = {e.id for e in entities}
        
        # 构建节点
        nodes = []
        for entity in entities:
            node = {
                "id": entity.id,
                "label": entity.name,
                "type": entity.entity_type.value,
                "description": entity.description,
                "confidence": entity.confidence,
                "properties": entity.properties,
                "matched": True,  # 标记为搜索匹配的节点
            }
            nodes.append(node)
        
        # 获取相关实体和关系
        related_entity_ids = set()
        edges = []
        
        for entity in entities:
            # 获取实体的所有关系
            relations = kg.get_entity_relations(entity.id)
            for relation in relations:
                # 添加关系边
                if relation.source_id in entity_ids or relation.target_id in entity_ids:
                    edge = {
                        "id": relation.id,
                        "source": relation.source_id,
                        "target": relation.target_id,
                        "type": relation.relation_type.value,
                        "label": relation.relation_type.value,
                        "confidence": relation.confidence,
                        "properties": relation.properties,
                    }
                    edges.append(edge)
                    
                    # 收集相关实体
                    if relation.source_id not in entity_ids:
                        related_entity_ids.add(relation.source_id)
                    if relation.target_id not in entity_ids:
                        related_entity_ids.add(relation.target_id)
        
        # 添加相关实体节点（一跳关系）
        for related_id in related_entity_ids:
            if related_id in kg.entities:
                related_entity = kg.entities[related_id]
                node = {
                    "id": related_entity.id,
                    "label": related_entity.name,
                    "type": related_entity.entity_type.value,
                    "description": related_entity.description,
                    "confidence": related_entity.confidence,
                    "properties": related_entity.properties,
                    "matched": False,  # 非直接匹配的节点
                }
                nodes.append(node)
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "matched_count": result.total_count,
        }
    
    except Exception as e:
        logger.error(f"Error searching graph visualization data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build")
async def build_knowledge_graph(
    current_user: User = Depends(get_current_user)
):
    """
    构建/重建知识图谱（管理员和经理专用）
    从已处理的文档中构建知识图谱
    """
    try:
        # 检查权限（只允许管理员和经理）
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=403,
                detail="只有管理员和经理可以构建知识图谱"
            )
        
        logger.info(f"User {current_user.username} ({current_user.role}) started building knowledge graph")
        
        # 导入管理器
        from ..knowledge_graph.manager import SteelKnowledgeGraphManager
        
        # 创建管理器并构建知识图谱
        kg_manager = SteelKnowledgeGraphManager()
        kg = kg_manager.build_from_processed_files()
        
        # 更新全局知识图谱实例
        global knowledge_graph_builder, knowledge_graph_query
        knowledge_graph_builder = kg_manager.builder
        knowledge_graph_query = SteelKnowledgeGraphQuery(kg)
        
        # 获取统计信息
        stats = kg_manager.get_statistics()
        
        logger.info(f"Knowledge graph built successfully: {stats}")
        
        return {
            "success": True,
            "message": "知识图谱构建成功",
            "stats": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=f"构建知识图谱时出错: {str(e)}")


@router.get("/spider-web/{center_entity_id}")
def get_spider_web_graph(
    center_entity_id: str = Path(..., description="中心实体ID"),
    max_depth: int = Query(2, description="最大深度"),
    current_user: User = Depends(get_current_user)
):
    """
    获取蛛网结构的知识图谱数据
    
    以指定实体为中心，按特征分类展示周围关联实体
    """
    global knowledge_graph_query
    
    if not knowledge_graph_query:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    try:
        from .steel_ontology import get_steel_ontology
        ontology = get_steel_ontology()
        
        # 获取中心实体
        center_entity = knowledge_graph_query.kg.entities.get(center_entity_id)
        if not center_entity:
            raise HTTPException(status_code=404, detail=f"实体不存在: {center_entity_id}")
        
        # 构建蛛网结构
        spider_web = {
            "center": {
                "id": center_entity.id,
                "name": center_entity.name,
                "type": center_entity.entity_type.value,
                "description": center_entity.description,
                "properties": center_entity.properties,
                "is_core": center_entity.properties.get('is_standard', False)
            },
            "features": {},  # 按特征分类的节点
            "relations": []
        }
        
        # 获取特征分类
        feature_categories = ontology.get_feature_categories()
        for category_name in feature_categories.keys():
            spider_web["features"][category_name] = []
        spider_web["features"]["其他"] = []
        
        # 获取相关实体
        related = knowledge_graph_query.get_related_entities(
            center_entity_id,
            max_depth=max_depth
        )
        
        # 按特征分类组织节点
        related_ids = set()  # 用于快速查找的ID集合
        for entity in related:
            if entity.id == center_entity_id:
                continue
            
            related_ids.add(entity.id)
            
            # 获取实体所属分类
            category = ontology.get_entity_category(entity.entity_type.value)
            
            node_data = {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type.value,
                "description": entity.description,
                "confidence": entity.confidence,
                "depth": 1,  # 简化：不追踪深度信息
                "is_standard": entity.properties.get('is_standard', False)
            }
            
            if category in spider_web["features"]:
                spider_web["features"][category].append(node_data)
            else:
                spider_web["features"]["其他"].append(node_data)
        
        # 收集关系
        for relation in knowledge_graph_query.kg.relations.values():
            if relation.source_id == center_entity_id or relation.target_id == center_entity_id:
                spider_web["relations"].append({
                    "id": relation.id,
                    "source": relation.source_id,
                    "target": relation.target_id,
                    "type": relation.relation_type.value,
                    "confidence": relation.confidence,
                    "is_standard": relation.properties.get('is_standard', False)
                })
            elif relation.source_id in related_ids and relation.target_id in related_ids:
                # 相关实体之间的关系
                spider_web["relations"].append({
                    "id": relation.id,
                    "source": relation.source_id,
                    "target": relation.target_id,
                    "type": relation.relation_type.value,
                    "confidence": relation.confidence,
                    "is_standard": relation.properties.get('is_standard', False)
                })
        
        # 统计信息
        total_nodes = sum(len(nodes) for nodes in spider_web["features"].values())
        spider_web["stats"] = {
            "total_feature_nodes": total_nodes,
            "total_relations": len(spider_web["relations"]),
            "categories": {k: len(v) for k, v in spider_web["features"].items() if v}
        }
        
        return spider_web
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating spider web graph: {e}")
        raise HTTPException(status_code=500, detail=f"生成蛛网图谱失败: {str(e)}")


@router.get("/core-entities")
def get_core_entities(current_user: User = Depends(get_current_user)):
    """
    获取核心实体列表（适合作为蛛网中心）
    """
    global knowledge_graph_query
    
    if not knowledge_graph_query:
        raise HTTPException(status_code=503, detail="知识图谱未加载")
    
    try:
        from .steel_ontology import CoreEntityType
        
        core_entities = []
        for entity in knowledge_graph_query.kg.entities.values():
            # 筛选核心实体类型
            if entity.entity_type.value in [t.value for t in CoreEntityType]:
                # 统计关联实体数量
                related_count = len(knowledge_graph_query.get_related_entities(
                    entity.id, max_depth=1
                ))
                
                core_entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type.value,
                    "description": entity.description,
                    "is_standard": entity.properties.get('is_standard', False),
                    "related_count": related_count,
                    "confidence": entity.confidence
                })
        
        # 按关联数量排序
        core_entities.sort(key=lambda x: x['related_count'], reverse=True)
        
        return {
            "core_entities": core_entities,
            "total": len(core_entities)
        }
    
    except Exception as e:
        logger.error(f"Error getting core entities: {e}")
        raise HTTPException(status_code=500, detail=f"获取核心实体失败: {str(e)}")