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
import { api } from './api';

/**
 * 知识图谱API客户端类
 */
export class KnowledgeGraphAPI {
  private baseUrl = '/api/knowledge-graph';

  /**
   * 搜索实体
   */
  async searchEntities(request: EntitySearchRequest): Promise<EntitySearchResponse> {
    const response = await api.post(`${this.baseUrl}/search/entities`, request);
    return response.data;
  }

  /**
   * 根据ID获取实体
   */
  async getEntity(entityId: string): Promise<SteelEntity> {
    const response = await api.get(`${this.baseUrl}/entities/${entityId}`);
    return response.data;
  }

  /**
   * 根据名称获取实体
   */
  async getEntityByName(name: string): Promise<SteelEntity> {
    const response = await api.get(`${this.baseUrl}/entities/name/${encodeURIComponent(name)}`);
    return response.data;
  }

  /**
   * 根据类型获取实体
   */
  async getEntitiesByType(entityType: string): Promise<{ entities: SteelEntity[]; total_count: number }> {
    const response = await api.get(`${this.baseUrl}/entities/type/${entityType}`);
    return response.data;
  }

  /**
   * 获取相关实体
   */
  async getRelatedEntities(
    entityId: string,
    request: Omit<RelatedEntitiesRequest, 'entity_id'>
  ): Promise<RelatedEntitiesResponse> {
    const response = await api.post(`${this.baseUrl}/entities/${entityId}/related`, request);
    return response.data;
  }

  /**
   * 查找实体间路径
   */
  async findPath(request: PathRequest): Promise<PathResponse> {
    const response = await api.post(`${this.baseUrl}/path`, request);
    return response.data;
  }

  /**
   * 根据性能查找钢种
   */
  async getSteelGradesByProperties(request: SteelGradePropertiesRequest): Promise<SteelGradePropertiesResponse> {
    const response = await api.post(`${this.baseUrl}/steel-grades/by-properties`, request);
    return response.data;
  }

  /**
   * 获取钢种成分信息
   */
  async getSteelComposition(request: SteelCompositionRequest): Promise<{ steel_grade: string; composition: SteelComposition }> {
    const response = await api.post(`${this.baseUrl}/steel-grades/composition`, request);
    return response.data;
  }

  /**
   * 获取钢种应用领域
   */
  async getSteelApplications(request: SteelApplicationsRequest): Promise<SteelApplicationsResponse> {
    const response = await api.post(`${this.baseUrl}/steel-grades/applications`, request);
    return response.data;
  }

  /**
   * 获取钢种生产工艺
   */
  async getSteelProcesses(request: SteelProcessesRequest): Promise<SteelProcessesResponse> {
    const response = await api.post(`${this.baseUrl}/steel-grades/processes`, request);
    return response.data;
  }

  /**
   * 获取钢种相关标准
   */
  async getSteelStandards(request: SteelStandardsRequest): Promise<SteelStandardsResponse> {
    const response = await api.post(`${this.baseUrl}/steel-grades/standards`, request);
    return response.data;
  }

  /**
   * 获取知识图谱统计信息
   */
  async getStatistics(): Promise<KnowledgeGraphStatsResponse> {
    const response = await api.get(`${this.baseUrl}/statistics`);
    return response.data;
  }

  /**
   * 获取所有实体类型
   */
  async getEntityTypes(): Promise<EntityTypesResponse> {
    const response = await api.get(`${this.baseUrl}/entity-types`);
    return response.data;
  }

  /**
   * 获取所有关系类型
   */
  async getRelationTypes(): Promise<RelationTypesResponse> {
    const response = await api.get(`${this.baseUrl}/relation-types`);
    return response.data;
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