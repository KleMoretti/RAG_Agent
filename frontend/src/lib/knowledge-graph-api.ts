/**
 * 钢铁领域知识图谱API客户端
 */

import {
  EntitySearchRequest,
  EntitySearchResponse,
  RelatedEntitiesRequest,
  RelatedEntitiesResponse,
  PathRequest,
  PathResponse,
  SteelGradePropertiesRequest,
  SteelGradePropertiesResponse,
  SteelCompositionRequest,
  SteelComposition,
  SteelApplicationsRequest,
  SteelApplicationsResponse,
  SteelProcessesRequest,
  SteelProcessesResponse,
  SteelStandardsRequest,
  SteelStandardsResponse,
  KnowledgeGraphStatsResponse,
  EntityTypesResponse,
  RelationTypesResponse,
  SteelEntity,
  SteelRelation
} from '@/types/knowledge-graph';
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

/**
 * 知识图谱API客户端类
 */
export class KnowledgeGraphAPI {
  private baseUrl = '/api/knowledge-graph';

  /**
   * 搜索实体
   */
  async searchEntities(request: EntitySearchRequest): Promise<EntitySearchResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/search/entities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Search entities error: ${response.status}`);
    return response.json();
  }

  /**
   * 根据ID获取实体
   */
  async getEntity(entityId: string): Promise<SteelEntity> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/entities/${entityId}`);
    if (!response.ok) throw new Error(`Get entity error: ${response.status}`);
    return response.json();
  }

  /**
   * 根据名称获取实体
   */
  async getEntityByName(name: string): Promise<SteelEntity> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/entities/name/${encodeURIComponent(name)}`);
    if (!response.ok) throw new Error(`Get entity by name error: ${response.status}`);
    return response.json();
  }

  /**
   * 根据类型获取实体
   */
  async getEntitiesByType(entityType: string): Promise<{ entities: SteelEntity[]; total_count: number }> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/entities/type/${entityType}`);
    if (!response.ok) throw new Error(`Get entities by type error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取相关实体
   */
  async getRelatedEntities(
    entityId: string,
    request: Omit<RelatedEntitiesRequest, 'entity_id'>
  ): Promise<RelatedEntitiesResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/entities/${entityId}/related`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Get related entities error: ${response.status}`);
    return response.json();
  }

  /**
   * 查找实体间路径
   */
  async findPath(request: PathRequest): Promise<PathResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/path`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Find path error: ${response.status}`);
    return response.json();
  }

  /**
   * 根据性能查找钢种
   */
  async getSteelGradesByProperties(request: SteelGradePropertiesRequest): Promise<SteelGradePropertiesResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/steel-grades/by-properties`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Get steel grades by properties error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取钢种成分信息
   */
  async getSteelComposition(request: SteelCompositionRequest): Promise<{ steel_grade: string; composition: SteelComposition }> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/steel-grades/composition`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Get steel composition error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取钢种应用领域
   */
  async getSteelApplications(request: SteelApplicationsRequest): Promise<SteelApplicationsResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/steel-grades/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Get steel applications error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取钢种生产工艺
   */
  async getSteelProcesses(request: SteelProcessesRequest): Promise<SteelProcessesResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/steel-grades/processes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Get steel processes error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取钢种相关标准
   */
  async getSteelStandards(request: SteelStandardsRequest): Promise<SteelStandardsResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/steel-grades/standards`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error(`Get steel standards error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取知识图谱统计信息
   */
  async getStatistics(): Promise<KnowledgeGraphStatsResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/statistics`);
    if (!response.ok) throw new Error(`Get statistics error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取所有实体类型
   */
  async getEntityTypes(): Promise<EntityTypesResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/entity-types`);
    if (!response.ok) throw new Error(`Get entity types error: ${response.status}`);
    return response.json();
  }

  /**
   * 获取所有关系类型
   */
  async getRelationTypes(): Promise<RelationTypesResponse> {
    const response = await fetch(`${API_BASE}${this.baseUrl}/relation-types`);
    if (!response.ok) throw new Error(`Get relation types error: ${response.status}`);
    return response.json();
  }
}

// 创建单例实例
export const knowledgeGraphAPI = new KnowledgeGraphAPI();

// 导出便捷方法
export const {
  searchEntities,
  getEntity,
  getEntityByName,
  getEntitiesByType,
  getRelatedEntities,
  findPath,
  getSteelGradesByProperties,
  getSteelComposition,
  getSteelApplications,
  getSteelProcesses,
  getSteelStandards,
  getStatistics,
  getEntityTypes,
  getRelationTypes
} = knowledgeGraphAPI;