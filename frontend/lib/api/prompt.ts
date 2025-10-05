import apiClient from './client';
import type { 
  Agent,
  SystemPrompt,
  ListAgentsParams,
  PaginatedAgentsResponse,
  AgentResponse,
} from '../types/prompt';

/**
 * 简化的 Prompt API 客户端
 * 只保留 Agent 列表获取和 Agent Prompt 获取功能
 */
class SimplifiedPromptAPI {
  // ============= Agent 相关 API =============

  /**
   * 获取 Agent 列表
   */
  async getAgents(params?: ListAgentsParams): Promise<Agent[] | PaginatedAgentsResponse> {
    const response = await apiClient.get<Agent[] | PaginatedAgentsResponse>('/api/prompt-management/agents', {
      params: {
        skip: params?.skip || 0,
        limit: params?.limit || 50,
        category: params?.category,
        is_active: params?.is_active,
        search: params?.search,
      },
    });
    return response.data;
  }

  /**
   * 获取单个 Agent 信息（包含其预设 Prompt）
   */
  async getAgent(id: string): Promise<AgentResponse> {
    const response = await apiClient.get<AgentResponse>(`/api/prompt-management/agents/${id}`);
    return response.data;
  }

  /**
   * 获取 Agent 的预设 System Prompt
   */
  async getAgentPrompt(agentId: string): Promise<SystemPrompt | null> {
    try {
      const response = await apiClient.get<SystemPrompt>(`/api/prompt-management/agents/${agentId}/active`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get prompt for agent ${agentId}:`, error);
      return null;
    }
  }
}

// 导出单例实例
export const promptAPI = new SimplifiedPromptAPI();

// 导出便捷方法
export const {
  getAgents,
  getAgent,
  getAgentPrompt,
} = promptAPI;

export default promptAPI;