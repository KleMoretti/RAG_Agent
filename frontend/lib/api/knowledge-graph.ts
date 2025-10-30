/**
 * 知识图谱API客户端
 */

import apiClient from './client';

// ==================== 类型定义 ====================

export interface KnowledgeGraphStats {
    total_entities: number;
    total_relations: number;
    entity_type_counts: Record<string, number>;
    relation_type_counts: Record<string, number>;
}

export interface Entity {
    id: string;
    name: string;
    entity_type: string;
    description?: string;
    properties?: Record<string, unknown>;
    aliases?: string[];
    confidence?: number;
}

export interface Relation {
    id: string;
    source_id: string;
    target_id: string;
    relation_type: string;
    properties?: Record<string, unknown>;
    confidence?: number;
}

export interface SearchEntitiesRequest {
    query: string;
    entity_types?: string[];
    min_confidence?: number;
    limit?: number;
}

export interface SearchEntitiesResponse {
    entities: Entity[];
    total_count: number;
}

export interface GraphNode {
    id: string;
    label: string;
    type: string;
    description?: string;
    confidence?: number;
    properties?: Record<string, any>;
    matched?: boolean;  // 搜索匹配的节点
}

export interface GraphEdge {
    id: string;
    source: string;
    target: string;
    type: string;
    label: string;
    confidence?: number;
    properties?: Record<string, any>;
}

export interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
    total_nodes: number;
    total_edges: number;
    available_types?: string[];
    matched_count?: number;
}

export interface BuildGraphResponse {
    success: boolean;
    message: string;
    stats?: KnowledgeGraphStats;
}

// ==================== API 函数 ====================

/**
 * 获取知识图谱统计信息
 */
export async function getKnowledgeGraphStats(): Promise<KnowledgeGraphStats> {
    const response = await apiClient.get<KnowledgeGraphStats>('/api/knowledge-graph/statistics');
    return response.data;
}

/**
 * 搜索实体
 */
export async function searchEntities(params: SearchEntitiesRequest): Promise<SearchEntitiesResponse> {
    const response = await apiClient.post<SearchEntitiesResponse>(
        '/api/knowledge-graph/search/entities',
        params
    );
    return response.data;
}

/**
 * 获取实体详情
 */
export async function getEntity(entityId: string): Promise<Entity> {
    const response = await apiClient.get<Entity>(`/api/knowledge-graph/entities/${entityId}`);
    return response.data;
}

/**
 * 根据名称获取实体
 */
export async function getEntityByName(name: string): Promise<Entity> {
    const response = await apiClient.get<Entity>(`/api/knowledge-graph/entities/name/${name}`);
    return response.data;
}

/**
 * 根据类型获取实体列表
 */
export async function getEntitiesByType(entityType: string): Promise<{ entities: Entity[]; total: number }> {
    const response = await apiClient.get<{ entities: Entity[]; total: number }>(
        `/api/knowledge-graph/entities/type/${entityType}`
    );
    return response.data;
}

/**
 * 获取相关实体
 */
export async function getRelatedEntities(
    entityId: string,
    relationTypes?: string[],
    maxDepth: number = 2
): Promise<GraphData> {
    const response = await apiClient.post<GraphData>(
        `/api/knowledge-graph/entities/${entityId}/related`,
        {
            relation_types: relationTypes,
            max_depth: maxDepth,
        }
    );
    return response.data;
}

/**
 * 获取实体类型列表
 */
export async function getEntityTypes(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/knowledge-graph/entity-types');
    return response.data;
}

/**
 * 获取关系类型列表
 */
export async function getRelationTypes(): Promise<string[]> {
    const response = await apiClient.get<string[]>('/api/knowledge-graph/relation-types');
    return response.data;
}

/**
 * 构建/重建知识图谱（管理员专用）
 */
export async function buildKnowledgeGraph(): Promise<BuildGraphResponse> {
    const response = await apiClient.post<BuildGraphResponse>('/api/knowledge-graph/build');
    return response.data;
}

/**
 * 获取钢种成分
 */
export async function getSteelComposition(steelGrade: string): Promise<{
    steel_grade: string;
    elements: Array<{ element: string; percentage: string }>;
}> {
    const response = await apiClient.post('/api/knowledge-graph/steel-grades/composition', {
        steel_grade: steelGrade,
    });
    return response.data;
}

/**
 * 获取钢种应用领域
 */
export async function getSteelApplications(steelGrade: string): Promise<{
    steel_grade: string;
    applications: Entity[];
}> {
    const response = await apiClient.post('/api/knowledge-graph/steel-grades/applications', {
        steel_grade: steelGrade,
    });
    return response.data;
}

/**
 * 获取知识图谱可视化数据（全量或按类型过滤）
 */
export async function getGraphVisualizationData(
    entityTypes?: string[],
    limit: number = 100
): Promise<GraphData> {
    const params = new URLSearchParams();
    if (entityTypes && entityTypes.length > 0) {
        params.append('entity_types', entityTypes.join(','));
    }
    params.append('limit', limit.toString());

    const response = await apiClient.get<GraphData>(
        `/api/knowledge-graph/graph-data?${params.toString()}`
    );
    return response.data;
}

/**
 * 根据搜索条件获取知识图谱可视化数据
 */
export async function searchGraphVisualizationData(
    params: SearchEntitiesRequest
): Promise<GraphData> {
    const response = await apiClient.post<GraphData>(
        '/api/knowledge-graph/search/graph-data',
        params
    );
    return response.data;
}

