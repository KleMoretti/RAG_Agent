/**
 * 钢铁领域知识图谱类型定义
 */

// 实体类型
export enum SteelEntityType {
  STEEL_GRADE = 'steel_grade',
  STEEL_TYPE = 'steel_type',
  ALLOY_ELEMENT = 'alloy_element',
  MATERIAL_PROPERTY = 'material_property',
  PROCESS = 'process',
  EQUIPMENT = 'equipment',
  APPLICATION = 'application',
  SPECIFICATION = 'specification',
  COMPANY = 'company',
  FACTORY = 'factory',
  PROJECT = 'project',
  STANDARD = 'standard',
  CERTIFICATION = 'certification',
  MARKET = 'market',
  PRICE = 'price',
  TREND = 'trend',
  ENVIRONMENT = 'environment',
  SUSTAINABILITY = 'sustainability',
  PERSON = 'person',
  LOCATION = 'location',
  TIME = 'time',
  CONCEPT = 'concept'
}

// 关系类型
export enum SteelRelationType {
  CONTAINS = 'contains',
  COMPOSED_OF = 'composed_of',
  HAS_PROPERTY = 'has_property',
  IMPROVES = 'improves',
  REDUCES = 'reduces',
  PRODUCED_BY = 'produced_by',
  USES_EQUIPMENT = 'uses_equipment',
  REQUIRES_TECHNOLOGY = 'requires_technology',
  APPLIES_TO = 'applies_to',
  USED_IN = 'used_in',
  SUITABLE_FOR = 'suitable_for',
  REPLACES = 'replaces',
  COMPETES_WITH = 'competes_with',
  OWNS = 'owns',
  OPERATES = 'operates',
  COLLABORATES_WITH = 'collaborates_with',
  SUPPLIES_TO = 'supplies_to',
  COMPLIES_WITH = 'complies_with',
  CERTIFIED_BY = 'certified_by',
  MEETS = 'meets',
  AFFECTS_PRICE = 'affects_price',
  INFLUENCES_TREND = 'influences_trend',
  TARGETS_MARKET = 'targets_market',
  IMPACTS_ENVIRONMENT = 'impacts_environment',
  PROMOTES_SUSTAINABILITY = 'promotes_sustainability',
  RELATED_TO = 'related_to',
  PART_OF = 'part_of',
  CAUSES = 'causes',
  MENTIONS = 'mentions',
  LOCATED_IN = 'located_in',
  WORKS_FOR = 'works_for',
  PUBLISHED_IN = 'published_in'
}

// 实体接口
export interface SteelEntity {
  id: string;
  name: string;
  entity_type: SteelEntityType;
  description?: string;
  properties: Record<string, any>;
  aliases: string[];
  confidence: number;
  created_at: string;
  updated_at: string;
}

// 关系接口
export interface SteelRelation {
  id: string;
  source_id: string;
  target_id: string;
  relation_type: SteelRelationType;
  properties: Record<string, any>;
  confidence: number;
  created_at: string;
  updated_at: string;
}

// 实体搜索请求
export interface EntitySearchRequest {
  query: string;
  entity_types?: SteelEntityType[];
  min_confidence?: number;
  limit?: number;
}

// 实体搜索响应
export interface EntitySearchResponse {
  entities: SteelEntity[];
  total_count: number;
  confidence_scores: Record<string, number>;
}

// 相关实体请求
export interface RelatedEntitiesRequest {
  entity_id: string;
  relation_types?: SteelRelationType[];
  max_depth?: number;
}

// 路径查找请求
export interface PathRequest {
  source_id: string;
  target_id: string;
  max_depth?: number;
}

// 钢种性能查询请求
export interface SteelGradePropertiesRequest {
  properties: string[];
  min_confidence?: number;
}

// 钢种成分查询请求
export interface SteelCompositionRequest {
  steel_grade: string;
}

// 钢种应用查询请求
export interface SteelApplicationsRequest {
  steel_grade: string;
}

// 钢种工艺查询请求
export interface SteelProcessesRequest {
  steel_grade: string;
}

// 钢种标准查询请求
export interface SteelStandardsRequest {
  steel_grade: string;
}

// 知识图谱统计响应
export interface KnowledgeGraphStatsResponse {
  total_entities: number;
  total_relations: number;
  entity_type_counts: Record<string, number>;
  relation_type_counts: Record<string, number>;
  average_confidence: number;
}

// 实体类型信息
export interface EntityTypeInfo {
  value: string;
  name: string;
}

// 关系类型信息
export interface RelationTypeInfo {
  value: string;
  name: string;
}

// 钢种成分信息
export interface SteelComposition {
  [element: string]: {
    confidence: number;
    context: string;
  };
}

// 钢种应用响应
export interface SteelApplicationsResponse {
  steel_grade: string;
  applications: SteelEntity[];
  total_count: number;
}

// 钢种工艺响应
export interface SteelProcessesResponse {
  steel_grade: string;
  processes: SteelEntity[];
  total_count: number;
}

// 钢种标准响应
export interface SteelStandardsResponse {
  steel_grade: string;
  standards: SteelEntity[];
  total_count: number;
}

// 钢种性能响应
export interface SteelGradePropertiesResponse {
  steel_grades: SteelEntity[];
  total_count: number;
}

// 路径响应
export interface PathResponse {
  relations: SteelRelation[];
  path_length: number;
}

// 相关实体响应
export interface RelatedEntitiesResponse {
  entities: SteelEntity[];
  total_count: number;
}

// 实体类型响应
export interface EntityTypesResponse {
  entity_types: EntityTypeInfo[];
}

// 关系类型响应
export interface RelationTypesResponse {
  relation_types: RelationTypeInfo[];
}
