/**
 * Agent 数据适配器
 * 处理后端和前端数据结构不匹配的问题
 */

import type { Agent } from '@/lib/types/prompt';

// 后端返回的原始 Agent 数据结构
export interface BackendAgent {
  id: number;
  name: string;
  agent_type: string;
  display_name: string;
  description: string;
  icon?: string;
  color?: string;
  is_active: boolean;
  capabilities?: {
    primary?: string[];
    greeting?: string;
  };
  use_cases?: {
    examples?: string[];
    scenarios?: string[];
  };
  tags?: {
    level?: string;
    category?: string[];
  };
  created_at: string;
  updated_at: string;
  created_by: number;
}

/**
 * 将后端 Agent 数据转换为前端期望的格式
 */
export function adaptBackendAgent(backendAgent: BackendAgent): Agent {
  return {
    id: backendAgent.id.toString(), // 数字转字符串
    name: backendAgent.name,
    description: backendAgent.description,
    category: backendAgent.agent_type, // agent_type 映射到 category
    icon: backendAgent.icon,
    color: backendAgent.color,
    is_active: backendAgent.is_active,
    created_at: backendAgent.created_at,
    updated_at: backendAgent.updated_at,
    created_by: backendAgent.created_by.toString(), // 数字转字符串
    metadata: {
      display_name: backendAgent.display_name,
      capabilities: backendAgent.capabilities,
      use_cases: backendAgent.use_cases,
      tags: backendAgent.tags,
    },
  };
}

/**
 * 批量转换后端 Agent 数据
 */
export function adaptBackendAgents(backendAgents: BackendAgent[]): Agent[] {
  return backendAgents.map(adaptBackendAgent);
}

/**
 * 类型守卫：检查是否为后端 Agent 格式
 */
export function isBackendAgent(agent: any): agent is BackendAgent {
  return (
    typeof agent === 'object' &&
    agent !== null &&
    typeof agent.id === 'number' &&
    typeof agent.agent_type === 'string' &&
    typeof agent.display_name === 'string'
  );
}

/**
 * 类型守卫：检查是否为后端 Agent 数组格式
 */
export function isBackendAgentArray(data: any): data is BackendAgent[] {
  return Array.isArray(data) && data.every(isBackendAgent);
}