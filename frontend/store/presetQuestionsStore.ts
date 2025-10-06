/**
 * 预设问题状态管理
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { presetQuestionsAPI, type PresetQuestion, type AgentPresetQuestionsResponse } from '@/lib/api/presetQuestions';

interface PresetQuestionsState {
  // 所有预设问题（按Agent分组）
  allQuestions: AgentPresetQuestionsResponse[];
  
  // 当前选中Agent的预设问题
  currentAgentQuestions: PresetQuestion[];
  
  // 加载状态
  loading: boolean;
  
  // 错误状态
  error: string | null;
  
  // 是否已初始化
  initialized: boolean;
}

interface PresetQuestionsActions {
  // 初始化 - 加载所有预设问题
  initialize: () => Promise<void>;
  
  // 加载所有预设问题
  loadAllQuestions: () => Promise<void>;
  
  // 根据Agent名称获取预设问题
  loadQuestionsByAgentName: (agentName: string) => Promise<void>;
  
  // 根据Agent ID获取预设问题
  loadQuestionsByAgentId: (agentId: number) => Promise<void>;
  
  // 增加问题使用次数
  incrementQuestionUsage: (questionId: number) => Promise<void>;
  
  // 获取指定Agent的预设问题（从缓存中）
  getQuestionsByAgentName: (agentName: string) => PresetQuestion[];
  
  // 清除错误
  clearError: () => void;
  
  // 重置状态
  reset: () => void;
}

type PresetQuestionsStore = PresetQuestionsState & PresetQuestionsActions;

export const usePresetQuestionsStore = create<PresetQuestionsStore>()(
  devtools(
    (set, get) => ({
      // 初始状态
      allQuestions: [],
      currentAgentQuestions: [],
      loading: false,
      error: null,
      initialized: false,

      // 初始化
      initialize: async () => {
        if (get().initialized) return;
        
        try {
          await get().loadAllQuestions();
          set({ initialized: true });
        } catch (error) {
          console.error('Failed to initialize preset questions store:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to initialize',
            initialized: true 
          });
        }
      },

      // 加载所有预设问题
      loadAllQuestions: async () => {
        set({ loading: true, error: null });
        try {
          const allQuestions = await presetQuestionsAPI.getAll(true);
          set({ 
            allQuestions, 
            loading: false 
          });
        } catch (error) {
          console.error('Failed to load all preset questions:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load preset questions',
            loading: false 
          });
        }
      },

      // 根据Agent名称获取预设问题
      loadQuestionsByAgentName: async (agentName: string) => {
        set({ loading: true, error: null });
        try {
          const questions = await presetQuestionsAPI.getByAgentName(agentName, true);
          set({ 
            currentAgentQuestions: questions, 
            loading: false 
          });
        } catch (error) {
          console.error(`Failed to load questions for agent ${agentName}:`, error);
          set({ 
            error: error instanceof Error ? error.message : `Failed to load questions for ${agentName}`,
            loading: false 
          });
        }
      },

      // 根据Agent ID获取预设问题
      loadQuestionsByAgentId: async (agentId: number) => {
        set({ loading: true, error: null });
        try {
          const questions = await presetQuestionsAPI.getByAgentId(agentId, true);
          set({ 
            currentAgentQuestions: questions, 
            loading: false 
          });
        } catch (error) {
          console.error(`Failed to load questions for agent ID ${agentId}:`, error);
          set({ 
            error: error instanceof Error ? error.message : `Failed to load questions for agent ${agentId}`,
            loading: false 
          });
        }
      },

      // 增加问题使用次数
      incrementQuestionUsage: async (questionId: number) => {
        try {
          await presetQuestionsAPI.incrementUsage(questionId);
          
          // 更新本地状态中的使用次数
          const state = get();
          
          // 更新当前Agent问题列表
          const updatedCurrentQuestions = state.currentAgentQuestions.map(q => 
            q.id === questionId ? { ...q, usage_count: q.usage_count + 1 } : q
          );
          
          // 更新所有问题列表
          const updatedAllQuestions = state.allQuestions.map(agentGroup => ({
            ...agentGroup,
            questions: agentGroup.questions.map(q => 
              q.id === questionId ? { ...q, usage_count: q.usage_count + 1 } : q
            )
          }));
          
          set({ 
            currentAgentQuestions: updatedCurrentQuestions,
            allQuestions: updatedAllQuestions
          });
        } catch (error) {
          console.error(`Failed to increment usage for question ${questionId}:`, error);
          // 不设置错误状态，因为这是后台操作
        }
      },

      // 获取指定Agent的预设问题（从缓存中）
      getQuestionsByAgentName: (agentName: string) => {
        const state = get();
        const agentGroup = state.allQuestions.find(group => group.agent_name === agentName);
        return agentGroup?.questions || [];
      },

      // 清除错误
      clearError: () => {
        set({ error: null });
      },

      // 重置状态
      reset: () => {
        set({
          allQuestions: [],
          currentAgentQuestions: [],
          loading: false,
          error: null,
          initialized: false,
        });
      },
    }),
    {
      name: 'preset-questions-store',
    }
  )
);

// 导出便捷的选择器
export const useAllPresetQuestions = () => usePresetQuestionsStore(state => state.allQuestions);
export const useCurrentAgentQuestions = () => usePresetQuestionsStore(state => state.currentAgentQuestions);
export const usePresetQuestionsLoading = () => usePresetQuestionsStore(state => state.loading);
export const usePresetQuestionsError = () => usePresetQuestionsStore(state => state.error);