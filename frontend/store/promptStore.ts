import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { promptAPI } from '@/lib/api/prompt';
import type { 
  Agent,
  SystemPrompt,
  AgentWithMetadata,
} from '@/lib/types/prompt';

/**
 * 简化的 Prompt Store State
 * 仅保留 Agent 管理和预设 Prompt 获取功能
 */
interface SimplifiedPromptState {
  // Agent 相关状态
  agents: AgentWithMetadata[];
  selectedAgent: AgentWithMetadata | null;
  agentsLoading: boolean;
  
  // 当前选中Agent的预设Prompt
  currentAgentPrompt: SystemPrompt | null;
  promptLoading: boolean;
  
  // Prompt缓存 - 避免重复请求
  promptCache: Record<string, SystemPrompt | null>;
  
  // 通用状态
  error: string | null;
  initialized: boolean;
}

/**
 * 简化的 Prompt Store Actions
 */
interface SimplifiedPromptActions {
  // 初始化
  initialize: () => Promise<void>;
  
  // Agent 操作
  loadAgents: () => Promise<void>;
  setSelectedAgent: (agent: AgentWithMetadata | null) => void;
  getAgentById: (id: string) => AgentWithMetadata | undefined;
  
  // 获取Agent的预设Prompt
  loadAgentPrompt: (agentId: string) => Promise<SystemPrompt | null>;
  
  // 错误处理
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // 重置状态
  reset: () => void;
}

type SimplifiedPromptStore = SimplifiedPromptState & SimplifiedPromptActions;

// 默认Agent元数据映射（用于向后兼容和UI显示）
// Agent专属配色方案定义
const agentColorSchemes = {
  general: {
    primary: 'text-blue-600',
    secondary: 'text-blue-500',
    background: 'bg-blue-50',
    border: 'border-blue-200',
    hover: 'hover:bg-blue-100',
    selected: 'border-blue-600',
  },
  process: {
    primary: 'text-orange-600',
    secondary: 'text-orange-500',
    background: 'bg-orange-50',
    border: 'border-orange-200',
    hover: 'hover:bg-orange-100',
    selected: 'border-orange-600',
  },
  equipment: {
    primary: 'text-purple-600',
    secondary: 'text-purple-500',
    background: 'bg-purple-50',
    border: 'border-purple-200',
    hover: 'hover:bg-purple-100',
    selected: 'border-purple-600',
  },
  market: {
    primary: 'text-green-600',
    secondary: 'text-green-500',
    background: 'bg-green-50',
    border: 'border-green-200',
    hover: 'hover:bg-green-100',
    selected: 'border-green-600',
  },
  quality: {
    primary: 'text-red-600',
    secondary: 'text-red-500',
    background: 'bg-red-50',
    border: 'border-red-200',
    hover: 'hover:bg-red-100',
    selected: 'border-red-600',
  },
  environment: {
    primary: 'text-emerald-600',
    secondary: 'text-emerald-500',
    background: 'bg-emerald-50',
    border: 'border-emerald-200',
    hover: 'hover:bg-emerald-100',
    selected: 'border-emerald-600',
  },
};

const defaultAgentMetadata: Record<string, Partial<AgentWithMetadata>> = {
  general: {
    displayName: '通用助手',
    iconComponent: undefined, // 将在组件中设置
    colorClass: agentColorSchemes.general.primary,
    colorScheme: agentColorSchemes.general,
    greeting: '您好！我是通用 AI 助手，可以帮您解答各类问题。',
    capabilities: ['多领域知识问答', '文档分析与总结', '数据解读与建议', '工作流程优化'],
    useCases: ['日常工作咨询', '技术问题解答', '文档处理', '决策支持'],
    tags: ['通用', '多功能', '智能问答'],
  },
  process: {
    displayName: '工艺专家',
    iconComponent: undefined,
    colorClass: agentColorSchemes.process.primary,
    colorScheme: agentColorSchemes.process,
    greeting: '您好！我是钢铁工艺专家，专注于生产工艺咨询和优化建议。',
    capabilities: ['工艺流程分析', '生产参数优化', '技术改进建议', '工艺故障诊断'],
    useCases: ['生产工艺咨询', '参数调优', '工艺改进', '技术升级'],
    tags: ['工艺', '生产', '技术优化'],
  },
  equipment: {
    displayName: '设备诊断',
    iconComponent: undefined,
    colorClass: agentColorSchemes.equipment.primary,
    colorScheme: agentColorSchemes.equipment,
    greeting: '您好！我是设备诊断专家，可以帮您诊断设备故障并提供维护建议。',
    capabilities: ['故障快速诊断', '预防性维护建议', '设备性能分析', '维修方案制定'],
    useCases: ['设备故障诊断', '预防性维护', '性能优化', '维修指导'],
    tags: ['设备', '诊断', '维护'],
  },
  market: {
    displayName: '市场分析',
    iconComponent: undefined,
    colorClass: agentColorSchemes.market.primary,
    colorScheme: agentColorSchemes.market,
    greeting: '您好！我是市场分析专家，为您提供钢铁行业市场洞察和价格分析。',
    capabilities: ['价格趋势分析', '市场供需预测', '竞争对手分析', '投资建议'],
    useCases: ['价格预测', '市场调研', '投资决策', '风险评估'],
    tags: ['市场', '分析', '预测'],
  },
  quality: {
    displayName: '质量控制',
    iconComponent: undefined,
    colorClass: agentColorSchemes.quality.primary,
    colorScheme: agentColorSchemes.quality,
    greeting: '您好！我是质量控制专家，专注于钢铁产品质量管理和标准制定。',
    capabilities: ['质量标准制定', '缺陷检测分析', '质量改进建议', '合规性检查'],
    useCases: ['质量检测', '标准制定', '缺陷分析', '质量改进'],
    tags: ['质量', '控制', '标准'],
  },
  environment: {
    displayName: '节能专家',
    iconComponent: undefined,
    colorClass: agentColorSchemes.environment.primary,
    colorScheme: agentColorSchemes.environment,
    greeting: '您好！我是节能专家，帮助您优化能源使用和降低成本。',
    capabilities: ['能耗分析', '节能方案设计', '能源成本优化', '环保合规指导'],
    useCases: ['能耗分析', '节能改造', '成本控制', '环保合规'],
    tags: ['能源', '优化', '节能'],
  },
};

// 增强Agent数据的函数
const enhanceAgentWithMetadata = (agent: Agent): AgentWithMetadata => {
  // 尝试多种匹配方式来找到正确的元数据
  let metadata = defaultAgentMetadata[agent.id] || 
                 defaultAgentMetadata[agent.name] || 
                 defaultAgentMetadata[agent.category] || {};
  
  // 如果仍然没有找到元数据，尝试通过名称模糊匹配
  if (!metadata.colorScheme) {
    const agentNameLower = agent.name.toLowerCase();
    const categoryLower = agent.category?.toLowerCase() || '';
    
    // 根据名称或类别进行模糊匹配
    if (agentNameLower.includes('通用') || agentNameLower.includes('general')) {
      metadata = defaultAgentMetadata.general;
    } else if (agentNameLower.includes('工艺') || agentNameLower.includes('process') || categoryLower.includes('process')) {
      metadata = defaultAgentMetadata.process;
    } else if (agentNameLower.includes('设备') || agentNameLower.includes('equipment') || categoryLower.includes('equipment')) {
      metadata = defaultAgentMetadata.equipment;
    } else if (agentNameLower.includes('市场') || agentNameLower.includes('market') || categoryLower.includes('market')) {
      metadata = defaultAgentMetadata.market;
    } else if (agentNameLower.includes('质量') || agentNameLower.includes('quality') || categoryLower.includes('quality')) {
      metadata = defaultAgentMetadata.quality;
    } else if (agentNameLower.includes('环境') || agentNameLower.includes('节能') || agentNameLower.includes('environment') || categoryLower.includes('environment')) {
      metadata = defaultAgentMetadata.environment;
    } else {
      // 默认使用通用助手的配色
      metadata = defaultAgentMetadata.general;
    }
  }
  
  return {
    ...agent,
    ...metadata,
    displayName: metadata.displayName || agent.name,
  };
};

export const usePromptStore = create<SimplifiedPromptStore>()(
  devtools(
    (set, get) => ({
      // 初始状态
      agents: [],
      selectedAgent: null,
      agentsLoading: false,
      currentAgentPrompt: null,
      promptLoading: false,
      promptCache: {},
      error: null,
      initialized: false,

      // 初始化
      initialize: async () => {
        if (get().initialized) return;
        
        try {
          await get().loadAgents();
          set({ initialized: true });
        } catch (error) {
          console.error('Failed to initialize prompt store:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to initialize',
            initialized: true 
          });
        }
      },

      // Agent 操作
      loadAgents: async () => {
        set({ agentsLoading: true, error: null });
        try {
          const response = await promptAPI.getAgents({ limit: 100 });
          
          // 后端直接返回 Agent[] 数组，不是分页格式
          let agents: Agent[] = [];
          
          if (Array.isArray(response)) {
            // 直接是数组格式
            agents = response;
          } else if (response && response.items && Array.isArray(response.items)) {
            // 分页格式
            agents = response.items;
          } else {
            console.warn('Invalid response from agents API:', response);
            set({ 
              agents: [], 
              agentsLoading: false,
              error: 'Invalid response from server'
            });
            return;
          }
          
          const enhancedAgents = agents.map(enhanceAgentWithMetadata);
          set({ agents: enhancedAgents, agentsLoading: false });
        } catch (error) {
          console.error('Failed to load agents:', error);
          set({ 
            agents: [], // 确保在错误时设置为空数组
            error: error instanceof Error ? error.message : 'Failed to load agents',
            agentsLoading: false 
          });
        }
      },

      setSelectedAgent: (agent: AgentWithMetadata | null) => {
        const currentState = get();
        
        // 如果选择的是同一个Agent，不需要重新加载
        if (currentState.selectedAgent?.id === agent?.id) {
          return;
        }
        
        set({ selectedAgent: agent, currentAgentPrompt: null });
        
        // 同步更新chatStore的状态
        // 动态导入chatStore以避免循环依赖
        import('./chatStore').then(({ useChatStore }) => {
          const chatStore = useChatStore.getState();
          chatStore.setSelectedAgentData(agent, null);
        });
        
        // 如果选择了Agent，自动加载其预设Prompt
        if (agent) {
          get().loadAgentPrompt(agent.id).then((prompt) => {
            // 加载完成后，再次同步prompt到chatStore
            if (prompt) {
              import('./chatStore').then(({ useChatStore }) => {
                const chatStore = useChatStore.getState();
                chatStore.setSelectedAgentData(agent, prompt);
              });
            }
          });
        }
      },

      getAgentById: (id: string) => {
        return get().agents.find(agent => agent.id === id);
      },

      // 获取Agent的预设Prompt
      loadAgentPrompt: async (agentId: string) => {
        const currentState = get();
        
        // 检查缓存中是否已有该Agent的prompt
        if (currentState.promptCache[agentId] !== undefined) {
          const cachedPrompt = currentState.promptCache[agentId];
          set({ currentAgentPrompt: cachedPrompt });
          return cachedPrompt;
        }
        
        // 如果正在加载相同的prompt，避免重复请求
        if (currentState.promptLoading) {
          return currentState.currentAgentPrompt;
        }
        
        set({ promptLoading: true, error: null });
        try {
          const prompt = await promptAPI.getAgentPrompt(agentId);
          set({ 
            currentAgentPrompt: prompt, 
            promptLoading: false,
            promptCache: {
              ...currentState.promptCache,
              [agentId]: prompt
            }
          });
          return prompt;
        } catch (error) {
          console.error('Failed to load agent prompt:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load agent prompt',
            promptLoading: false,
            currentAgentPrompt: null,
            promptCache: {
              ...currentState.promptCache,
              [agentId]: null
            }
          });
          return null;
        }
      },

      // 错误处理
      setError: (error: string | null) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },

      // 重置状态
      reset: () => {
        set({
          agents: [],
          selectedAgent: null,
          agentsLoading: false,
          currentAgentPrompt: null,
          promptLoading: false,
          error: null,
          initialized: false,
        });
      },
    }),
    {
      name: 'prompt-store',
    }
  )
);

// 导出便捷的选择器
export const useAgents = () => usePromptStore(state => state.agents);
export const useSelectedAgent = () => usePromptStore(state => state.selectedAgent);
export const useCurrentAgentPrompt = () => usePromptStore(state => state.currentAgentPrompt);
export const useAgentsLoading = () => usePromptStore(state => state.agentsLoading);
export const usePromptLoading = () => usePromptStore(state => state.promptLoading);
export const usePromptError = () => usePromptStore(state => state.error);