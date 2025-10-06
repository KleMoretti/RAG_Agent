/**
 * 预设问题 API 客户端
 */

import apiClient from './client';

// 预设问题类型定义
export interface PresetQuestion {
  id: number;
  agent_id: number;
  title: string;
  question: string;
  category?: string;
  order_index: number;
  is_active: boolean;
  usage_count: number;
  tags?: string[];
  difficulty_level?: string;
  expected_response_type?: string;
  created_at: string;
  updated_at: string;
}

export interface AgentPresetQuestionsResponse {
  agent_id: number;
  agent_name: string;
  questions: PresetQuestion[];
}

export interface PresetQuestionCreate {
  agent_id: number;
  title: string;
  question: string;
  category?: string;
  order_index?: number;
  is_active?: boolean;
  tags?: string[];
  difficulty_level?: string;
  expected_response_type?: string;
}

export interface PresetQuestionUpdate {
  title?: string;
  question?: string;
  category?: string;
  order_index?: number;
  is_active?: boolean;
  tags?: string[];
  difficulty_level?: string;
  expected_response_type?: string;
}

export interface UsageStats {
  total_questions: number;
  total_usage: number;
  agent_stats: Array<{
    agent_id: number;
    agent_name: string;
    question_count: number;
    total_usage: number;
  }>;
}

/**
 * 预设问题 API 客户端
 */
export const presetQuestionsAPI = {
  /**
   * 根据 Agent ID 获取预设问题
   */
  getByAgentId: async (agentId: number, activeOnly: boolean = true): Promise<PresetQuestion[]> => {
    const response = await apiClient.get(`/api/preset-questions/agent/${agentId}`, {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  /**
   * 根据 Agent 名称获取预设问题
   */
  getByAgentName: async (agentName: string, activeOnly: boolean = true): Promise<PresetQuestion[]> => {
    const response = await apiClient.get(`/api/preset-questions/agent/${agentName}/by-name`, {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  /**
   * 获取所有预设问题（按 Agent 分组）
   */
  getAll: async (activeOnly: boolean = true): Promise<AgentPresetQuestionsResponse[]> => {
    const response = await apiClient.get('/api/preset-questions/all', {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  /**
   * 创建新的预设问题（需要管理员权限）
   */
  create: async (questionData: PresetQuestionCreate): Promise<PresetQuestion> => {
    const response = await apiClient.post('/api/preset-questions/', questionData);
    return response.data;
  },

  /**
   * 更新预设问题（需要管理员权限）
   */
  update: async (questionId: number, questionData: PresetQuestionUpdate): Promise<PresetQuestion> => {
    const response = await apiClient.put(`/api/preset-questions/${questionId}`, questionData);
    return response.data;
  },

  /**
   * 删除预设问题（需要管理员权限）
   */
  delete: async (questionId: number): Promise<void> => {
    await apiClient.delete(`/api/preset-questions/${questionId}`);
  },

  /**
   * 增加问题使用次数
   */
  incrementUsage: async (questionId: number): Promise<void> => {
    await apiClient.post(`/api/preset-questions/${questionId}/increment-usage`);
  },

  /**
   * 获取问题分类列表
   */
  getCategories: async (): Promise<string[]> => {
    const response = await apiClient.get('/api/preset-questions/categories');
    return response.data;
  },

  /**
   * 获取使用统计（需要管理员权限）
   */
  getUsageStats: async (agentId?: number): Promise<UsageStats> => {
    const response = await apiClient.get('/api/preset-questions/stats/usage', {
      params: agentId ? { agent_id: agentId } : {}
    });
    return response.data;
  },
};