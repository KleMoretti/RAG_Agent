import apiClient from './client';

/**
 * Agent数据类型定义
 */
export interface AgentWithMetadata {
  id: number;
  name: string;
  displayName: string;
  agentType: string;
  description: string;
  capabilities: string[];
  isActive: boolean;
  iconComponent: string;
  colorClass: string;
  useCases: string[];
}

/**
 * 简化的Agents API客户端
 * 用于与后端的 /api/agents 端点交互
 */
export class AgentsAPI {
  
  /**
   * 获取所有可用的Agent列表
   */
  async getAgents(): Promise<AgentWithMetadata[]> {
    try {
      const response = await apiClient.get<AgentWithMetadata[]>('/api/agents');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      throw error;
    }
  }

  /**
   * 根据ID获取特定Agent
   */
  async getAgent(id: number): Promise<AgentWithMetadata | undefined> {
    try {
      const agents = await this.getAgents();
      return agents.find(agent => agent.id === id);
    } catch (error) {
      console.error(`Failed to fetch agent ${id}:`, error);
      throw error;
    }
  }

  /**
   * 根据类型获取Agent列表
   */
  async getAgentsByType(agentType: string): Promise<AgentWithMetadata[]> {
    try {
      const agents = await this.getAgents();
      return agents.filter(agent => agent.agentType === agentType);
    } catch (error) {
      console.error(`Failed to fetch agents by type ${agentType}:`, error);
      throw error;
    }
  }

  /**
   * 获取激活的Agent列表
   */
  async getActiveAgents(): Promise<AgentWithMetadata[]> {
    try {
      const agents = await this.getAgents();
      return agents.filter(agent => agent.isActive);
    } catch (error) {
      console.error('Failed to fetch active agents:', error);
      throw error;
    }
  }
}

// 创建单例实例
export const agentsAPI = new AgentsAPI();

// 导出便捷方法
export const {
  getAgents,
  getAgent,
  getAgentsByType,
  getActiveAgents,
} = agentsAPI;

export default agentsAPI;