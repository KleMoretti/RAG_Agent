/**
 * Prompt Management API Types
 * 对应后端 src/prompt_management/schemas.py 的类型定义
 */

// ============= 基础类型 =============

/**
 * Simplified Prompt Management Types
 * 简化后的Prompt管理类型定义，仅保留Agent和预设System Prompt相关类型
 */

// ============= 核心类型 =============

export interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  icon?: string;
  color?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
  metadata?: Record<string, any>;
}

export interface SystemPrompt {
  id: string;
  name: string;
  content: string;
  description?: string;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
  metadata?: Record<string, any>;
}

// ============= 响应类型 =============

export interface AgentResponse {
  agent: Agent;
  active_prompt?: SystemPrompt;
}

// ============= 查询参数 =============

export interface ListAgentsParams {
  skip?: number;
  limit?: number;
  category?: string;
  is_active?: boolean;
  search?: string;
}

// ============= 分页响应 =============

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export type PaginatedAgentsResponse = PaginatedResponse<Agent>;

// ============= 错误类型 =============

export interface APIError {
  detail: string;
  code?: string;
  field?: string;
}

export interface ValidationError {
  detail: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

// ============= 扩展类型 =============

// Agent配色方案类型
export interface AgentColorScheme {
  primary: string;
  secondary: string;
  background: string;
  border: string;
  hover: string;
  selected: string;
}

export interface AgentWithMetadata extends Agent {
  // UI显示相关的元数据
  displayName?: string;
  iconComponent?: React.ComponentType;
  colorClass?: string;
  colorScheme?: AgentColorScheme;
  greeting?: string;
  capabilities?: string[];
  useCases?: string[];
  tags?: string[];
}

// ============= 简化的状态管理类型 =============

export interface SimplifiedPromptState {
  agents: Agent[];
  currentAgentPrompt: SystemPrompt | null;
  loading: boolean;
  error: string | null;
}

export interface SimplifiedPromptActions {
  // Agent 操作
  loadAgents: () => Promise<void>;
  loadAgentPrompt: (agentId: string) => Promise<SystemPrompt | null>;
  
  // 错误处理
  setError: (error: string | null) => void;
  clearError: () => void;
}