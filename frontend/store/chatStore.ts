import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ChatMessage } from '../lib/types/api';
import type { AgentWithMetadata, SystemPrompt } from '../lib/types/prompt';

/**
 * Chat session interface
 */
export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  agentId?: string; // 关联的Agent ID
  systemPrompt?: SystemPrompt; // 使用的预设System Prompt
}

/**
 * Chat store state
 */
interface ChatState {
  currentSessionId: string | null;
  sessions: ChatSession[];
  isStreaming: boolean;
  streamingContent: string;
  selectedAgent: string; // Currently selected AI agent (for backward compatibility)
  selectedAgentData: AgentWithMetadata | null; // 完整的Agent数据
  currentSystemPrompt: SystemPrompt | null; // 当前Agent的预设System Prompt
  isInitialized: boolean; // 标记store是否已初始化，防止重复创建会话
}

/**
 * Chat store actions
 */
interface ChatActions {
  createSession: (title?: string, agentId?: string, systemPrompt?: SystemPrompt) => string;
  setCurrentSession: (sessionId: string) => void;
  addMessage: (sessionId: string, message: ChatMessage) => void;
  updateLastMessage: (sessionId: string, content: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  deleteSession: (sessionId: string) => void;
  clearSessions: () => void;
  setStreaming: (streaming: boolean) => void;
  setStreamingContent: (content: string) => void;
  appendStreamingContent: (chunk: string) => void;
  setSelectedAgent: (agentId: string) => void; // Set selected agent (backward compatibility)
  setSelectedAgentData: (agent: AgentWithMetadata | null, systemPrompt?: SystemPrompt | null) => void; // Set complete agent data with prompt
  updateSessionAgent: (sessionId: string, agentId: string, systemPrompt?: SystemPrompt) => void; // Update session's agent and prompt
  initializeStore: () => void; // 初始化store，确保只创建一次默认会话
}

/**
 * Combined chat store type
 */
type ChatStore = ChatState & ChatActions;

/**
 * Generate a unique session ID
 */
function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(7)}`;
}

/**
 * Chat store using Zustand
 * Manages chat sessions and messages with integrated Agent and System Prompt support
 */
export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      // Initial state
      currentSessionId: null,
      sessions: [],
      isStreaming: false,
      streamingContent: '',
      selectedAgent: 'general', // Default to general agent (backward compatibility)
      selectedAgentData: null, // Complete agent data
      currentSystemPrompt: null, // Current agent's system prompt
      isInitialized: false, // 标记store是否已初始化

      // Actions
      createSession: (title = 'New Conversation', agentId?: string, systemPrompt?: SystemPrompt) => {
        const sessionId = generateSessionId();
        const newSession: ChatSession = {
          id: sessionId,
          title,
          messages: [],
          createdAt: new Date(),
          updatedAt: new Date(),
          agentId: agentId || get().selectedAgent,
          systemPrompt,
        };

        set((state) => ({
          sessions: [...state.sessions, newSession],
          currentSessionId: sessionId,
        }));

        return sessionId;
      },

      setCurrentSession: (sessionId) => {
        set({ currentSessionId: sessionId });
        
        // 当切换会话时，同步Agent和System Prompt
        const session = get().sessions.find(s => s.id === sessionId);
        if (session) {
          // 动态导入promptStore以获取完整的Agent数据
          import('./promptStore').then(({ usePromptStore }) => {
            const promptStore = usePromptStore.getState();
            const agentData = promptStore.getAgentById(session.agentId || 'general');
            
            set({
              selectedAgent: session.agentId || 'general',
              selectedAgentData: agentData || null,
              currentSystemPrompt: session.systemPrompt || null,
            });
          }).catch((error) => {
            console.error('Failed to load agent data during session switch:', error);
            // 回退到基本设置
            set({
              selectedAgent: session.agentId || 'general',
              selectedAgentData: null,
              currentSystemPrompt: session.systemPrompt || null,
            });
          });
        }
      },

      addMessage: (sessionId, message) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: [...session.messages, message],
                  updatedAt: new Date(),
                }
              : session
          ),
        }));
      },

      updateLastMessage: (sessionId, content) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.map((msg, index) =>
                    index === session.messages.length - 1
                      ? { ...msg, content }
                      : msg
                  ),
                  updatedAt: new Date(),
                }
              : session
          ),
        }));
      },

      updateSessionTitle: (sessionId, title) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? { ...session, title, updatedAt: new Date() }
              : session
          ),
        }));
      },

      deleteSession: (sessionId) => {
        set((state) => ({
          sessions: state.sessions.filter((session) => session.id !== sessionId),
          currentSessionId:
            state.currentSessionId === sessionId ? null : state.currentSessionId,
        }));
      },

      clearSessions: () => {
        set({
          sessions: [],
          currentSessionId: null,
        });
      },

      setStreaming: (streaming) => {
        set({ isStreaming: streaming });
      },

      setStreamingContent: (content) => {
        set({ streamingContent: content });
      },

      appendStreamingContent: (chunk) => {
        set((state) => ({
          streamingContent: state.streamingContent + chunk,
        }));
      },

      setSelectedAgent: (agentId) => {
        set({ selectedAgent: agentId });
      },

      setSelectedAgentData: (agent, systemPrompt = null) => {
        set({ 
          selectedAgentData: agent,
          selectedAgent: agent?.id || 'general', // 保持向后兼容性
          currentSystemPrompt: systemPrompt,
        });
        
        // 如果有当前会话，更新会话的Agent和System Prompt
        const currentSessionId = get().currentSessionId;
        if (currentSessionId && agent) {
          get().updateSessionAgent(currentSessionId, agent.id, systemPrompt || undefined);
        }
      },

      updateSessionAgent: (sessionId, agentId, systemPrompt) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  agentId,
                  systemPrompt,
                  updatedAt: new Date(),
                }
              : session
          ),
        }));
      },

      initializeStore: () => {
        const state = get();
        // 只有在未初始化且没有当前会话时才创建默认会话
        if (!state.isInitialized && !state.currentSessionId && state.sessions.length === 0) {
          const sessionId = generateSessionId();
          const newSession: ChatSession = {
            id: sessionId,
            title: '新对话',
            messages: [],
            createdAt: new Date(),
            updatedAt: new Date(),
            agentId: state.selectedAgent,
            systemPrompt: state.currentSystemPrompt || undefined,
          };

          set({
            sessions: [newSession],
            currentSessionId: sessionId,
            isInitialized: true,
          });
        } else {
          // 如果已经有会话或已初始化，只标记为已初始化
          set({ isInitialized: true });
        }
      },
    }),
    {
      name: 'chat-store',
      partialize: (state) => ({
        // 持久化会话数据和选中的Agent/System Prompt
        sessions: state.sessions,
        currentSessionId: state.currentSessionId,
        selectedAgent: state.selectedAgent,
        selectedAgentData: state.selectedAgentData,
        currentSystemPrompt: state.currentSystemPrompt,
        isInitialized: state.isInitialized,
      }),
    }
  )
);

// 导出便捷的选择器
export const useCurrentSession = () => {
  const { currentSessionId, sessions } = useChatStore();
  return sessions.find(s => s.id === currentSessionId) || null;
};

export const useCurrentSessionMessages = () => {
  const currentSession = useCurrentSession();
  return currentSession?.messages || [];
};

export const useSelectedAgentData = () => useChatStore(state => state.selectedAgentData);
export const useCurrentSystemPrompt = () => useChatStore(state => state.currentSystemPrompt);
