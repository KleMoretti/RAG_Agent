"use client";

import * as React from "react";
import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupAddon,
} from "@/components/ui/input-group";
import { useChatStore } from "@/store/chatStore";
import { usePromptStore } from "@/store/promptStore";
import { sendMessage } from "@/lib/api/chat";
import { useTranslation } from "@/lib/hooks/useTranslation";
import type { ChatMessage } from "@/lib/types/api";
import type { AgentWithMetadata } from "@/lib/types/prompt";
import {
  Loader2,
  Bot,
  User,
  Lightbulb,
  Wrench,
  TrendingUp,
  FlaskConical,
  Plus,
  ArrowUp,
  ShieldCheck,
  Zap,
} from "lucide-react";

// 默认图标映射（用于向后兼容）
const defaultIcons: Record<string, React.ElementType> = {
  general: Bot,
  process: FlaskConical,
  equipment: Wrench,
  market: TrendingUp,
  quality: ShieldCheck,
  environment: Zap,
};

// 获取Agent图标的辅助函数
const getAgentIcon = (agent: AgentWithMetadata): React.ElementType => {
  if (agent.iconComponent) {
    return agent.iconComponent;
  }
  return defaultIcons[agent.category] || defaultIcons[agent.id] || Bot;
};

// Agent metadata (保留作为fallback)
const agentMetadata: Record<
  string,
  {
    name: string;
    icon: React.ElementType;
    color: string;
    colorScheme?: import('@/lib/types/prompt').AgentColorScheme;
    greeting: string;
  }
> = {
  general: {
    name: "通用助手",
    icon: Bot,
    color: "bg-primary",
    greeting: "您好！我是通用 AI 助手，可以帮您解答各类问题。",
  },
  process: {
    name: "工艺专家",
    icon: FlaskConical,
    color: "bg-secondary",
    greeting: "您好！我是钢铁工艺专家，专注于生产工艺咨询和优化建议。",
  },
  equipment: {
    name: "设备诊断",
    icon: Wrench,
    color: "bg-primary",
    greeting: "您好！我是设备诊断专家，可以帮您诊断设备故障并提供维护建议。",
  },
  market: {
    name: "市场分析师",
    icon: TrendingUp,
    color: "bg-accent",
    greeting: "您好！我是市场分析师，为您提供市场行情和趋势分析。",
  },
  quality: {
    name: "质量顾问",
    icon: Bot,
    color: "bg-muted",
    greeting: "您好！我是质量顾问，专注于质量控制和参数优化。",
  },
  environment: {
    name: "节能专家",
    icon: Lightbulb,
    color: "bg-secondary",
    greeting: "您好！我是节能专家，帮助您优化能源使用和降低成本。",
  },
};

// Suggested prompts
const suggestedPrompts = [
  {
    icon: FlaskConical,
    title: "钢铁工艺咨询",
    description: "询问关于炼钢、轧制等工艺流程的问题",
  },
  {
    icon: Wrench,
    title: "设备故障诊断",
    description: "描述设备症状，获取故障排查建议",
  },
  {
    icon: TrendingUp,
    title: "市场行情分析",
    description: "了解铁矿石、钢材价格趋势和市场动态",
  },
  {
    icon: Lightbulb,
    title: "质量参数优化",
    description: "获取生产参数调整和质量改进建议",
  },
];

export default function DashboardPage() {
  const t = useTranslation();
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { 
    selectedAgent, 
    selectedAgentData,
    currentSystemPrompt, // 更新：使用currentSystemPrompt替代selectedPrompt
    currentSessionId, 
    sessions, 
    createSession, 
    addMessage,
    updateSessionTitle,
    setSelectedAgentData, // 添加：用于设置Agent和System Prompt
    initializeStore, // 添加：初始化store
    isInitialized // 添加：检查是否已初始化
  } = useChatStore();

  const { 
    agents, 
    agentsLoading,
    error: agentsError,
    initialized,
    initialize,
    loadAgentPrompt, // 更新：使用loadAgentPrompt替代getAgentSystemPrompt
    currentAgentPrompt, // 添加：当前Agent的预设Prompt
    setSelectedAgent // 添加：设置选中的Agent（带缓存）
  } = usePromptStore();

  // 初始化Prompt Store
  useEffect(() => {
    if (!initialized) {
      initialize();
    }
  }, [initialized, initialize]);
  
  // 获取当前Agent数据
  const currentAgentData = selectedAgentData || agents.find(a => a.id === selectedAgent);
  const fallbackAgent = agentMetadata[selectedAgent] || agentMetadata.general;
  
  // 使用真实Agent数据或fallback
  const currentAgent = currentAgentData ? {
    name: currentAgentData.displayName || currentAgentData.name,
    icon: getAgentIcon(currentAgentData),
    color: fallbackAgent.color, // 保留作为后备
    colorScheme: currentAgentData.colorScheme,
    greeting: currentAgentData.greeting || fallbackAgent.greeting,
  } : fallbackAgent;
  
  const AgentIcon = currentAgent.icon;
  
  // Get current session messages
  const currentSession = sessions.find(s => s.id === currentSessionId);
  const messages = currentSession?.messages || [];

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 初始化store，确保只创建一次默认会话
  useEffect(() => {
    if (!isInitialized) {
      initializeStore();
    }
  }, [isInitialized, initializeStore]);

  // 当Agent变化时，应用已加载的System Prompt
  useEffect(() => {
    if (currentAgentData && currentAgentPrompt && initialized) {
      // 只有当prompt与当前系统prompt不同时才更新
      if (currentAgentPrompt !== currentSystemPrompt) {
        setSelectedAgentData(currentAgentData, currentAgentPrompt);
      }
    }
  }, [currentAgentData, currentAgentPrompt, initialized, currentSystemPrompt, setSelectedAgentData]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    const sessionId =
      currentSessionId || createSession(`${currentAgent.name}对话`);

    const userMsg: ChatMessage = {
      id: `msg_${Date.now()}_user`,
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };

    // Add user message to store
    addMessage(sessionId, userMsg);
    setInputValue("");
    setIsLoading(true);
    setError("");

    try {
      const response = await sendMessage(userMessage, sessionId, selectedAgent);

      const assistantMsg: ChatMessage = {
        id: `msg_${Date.now()}_assistant`,
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
        reasoningSteps: response.reasoningSteps,
      };

      // Add assistant message to store
      addMessage(sessionId, assistantMsg);

      // Auto-generate title for new conversations
      const session = sessions.find(s => s.id === sessionId);
      if (session && session.messages.length === 0) {
        // Generate a short title from the user message
        const title = userMessage.length > 20 
          ? userMessage.substring(0, 20) + "..." 
          : userMessage;
        updateSessionTitle(sessionId, title);
      }
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(err instanceof Error ? err.message : "消息发送失败，请重试");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 处理Agent选择（从建议卡片点击）
  const handleAgentSelect = (agentId: string) => {
    const agent = agents.find(a => a.id === agentId);
    if (agent) {
      // 使用setSelectedAgent方法，它会自动处理prompt加载和缓存
      setSelectedAgent(agent);
      
      // 创建新会话使用选中的Agent
      const newSessionId = createSession(`${agent.displayName || agent.name}对话`, agentId);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          // Welcome screen
          <div className="flex flex-col items-center justify-center h-full max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <div className="flex justify-center mb-6">
                <div className={`${currentAgent.colorScheme?.background || currentAgent.color} p-6 rounded-2xl border-2 ${currentAgent.colorScheme?.border || 'border-transparent'}`}>
                  <AgentIcon className={`w-12 h-12 ${currentAgent.colorScheme?.primary || 'text-white'}`} />
                </div>
              </div>
              <h1 className="text-3xl font-bold mb-2">{currentAgent.name}</h1>
              <p className="text-sm text-muted-foreground">
                {currentAgent.greeting}
              </p>
            </div>

            {/* Suggested prompts */}
            <div className="w-full max-w-3xl">
              <p className="text-xs text-muted-foreground mb-4 text-center">
                💡 试试这些功能：
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {agentsLoading ? (
                  // Loading state
                  Array.from({ length: 4 }).map((_, index) => (
                    <Card key={index} className="p-4">
                      <div className="flex items-start gap-3">
                        <div className="w-5 h-5 bg-muted rounded animate-pulse mt-0.5" />
                        <div className="flex-1">
                          <div className="h-4 bg-muted rounded animate-pulse mb-2" />
                          <div className="h-3 bg-muted rounded animate-pulse" />
                        </div>
                      </div>
                    </Card>
                  ))
                ) : agentsError ? (
                  // Error state
                  <div className="col-span-full text-center text-sm text-muted-foreground">
                    加载建议失败，请稍后重试
                  </div>
                ) : (
                  // Dynamic prompts based on available agents
                   (agents && agents.length > 0 ? agents : Object.keys(agentMetadata).map(id => ({ 
                     id, 
                     displayName: agentMetadata[id].name,
                     useCases: [`使用${agentMetadata[id].name}进行专业咨询`]
                   }))).slice(0, 4).map((agent, index) => {
                     const isRealAgent = agents.length > 0;
                     const AgentIcon = isRealAgent ? getAgentIcon(agent as AgentWithMetadata) : agentMetadata[agent.id]?.icon || Bot;
                     const title = agent.displayName || (isRealAgent ? (agent as AgentWithMetadata).name : undefined) || agentMetadata[agent.id]?.name || '专业助手';
                     const description = isRealAgent ? (agent as AgentWithMetadata).useCases?.[0] : (agent as any).useCases?.[0] || `咨询${title}相关问题`;
                    
                    return (
                      <Card
                        key={agent.id || index}
                        className="p-4 cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => {
                          // 如果是真实Agent，选择该Agent并应用预设Prompt
                          if (isRealAgent && agent.id) {
                            handleAgentSelect(agent.id);
                          } else {
                            // 否则只设置输入值（向后兼容）
                            setInputValue(description);
                          }
                        }}
                      >
                        <div className="flex items-start gap-3">
                          <AgentIcon className="w-5 h-5 text-primary mt-0.5" />
                          <div>
                            <div className="text-sm font-medium mb-1">{title}</div>
                            <div className="text-xs text-muted-foreground">
                              {description}
                            </div>
                          </div>
                        </div>
                      </Card>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        ) : (
          // Messages display
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div
                key={message.id || index}
                className={`flex gap-4 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role === "assistant" && (
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback className={currentAgent.colorScheme?.background || currentAgent.color}>
                      <AgentIcon className={`w-4 h-4 ${currentAgent.colorScheme?.primary || 'text-white'}`} />
                    </AvatarFallback>
                  </Avatar>
                )}

                <div
                  className={`rounded-xl px-3 py-2 max-w-[60%] shadow-sm border text-sm ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-card text-card-foreground border-border"
                  }`}
                >
                  <div className="whitespace-pre-wrap break-words">
                    {message.content}
                  </div>

                  {/* Reasoning steps */}
                  {message.reasoningSteps &&
                    message.reasoningSteps.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-border/50">
                        <p className="text-xs font-semibold uppercase text-muted-foreground mb-1">
                          🧠 推理过程：
                        </p>
                        {message.reasoningSteps.map((step, idx) => (
                          <div
                            key={idx}
                            className="text-xs text-muted-foreground mb-0.5 leading-tight"
                          >
                            • {step.thought}
                          </div>
                        ))}
                      </div>
                    )}
                </div>

                {message.role === "user" && (
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback>
                      <User className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-4 justify-start">
                <Avatar className="h-8 w-8 flex-shrink-0">
                  <AvatarFallback className={currentAgent.colorScheme?.background || currentAgent.color}>
                    <AgentIcon className={`w-4 h-4 ${currentAgent.colorScheme?.primary || 'text-white'}`} />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-card text-card-foreground border-border rounded-xl px-3 py-2 shadow-sm border">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-3 h-3 animate-spin text-primary" />
                    <span className="text-sm">
                      {t.chat.thinking}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="px-6 pb-2">
          <Alert variant="destructive" className="max-w-4xl mx-auto">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t bg-background p-6">
        <div className="max-w-4xl mx-auto">
          <InputGroup>
            <InputGroupTextarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask, Search or Chat..."
              className="min-h-[60px] max-h-[200px]"
              disabled={isLoading}
            />
            
            {/* Bottom row with buttons and disclaimer inside InputGroup */}
            <InputGroupAddon align="block-end">
              <div className="flex items-center justify-between w-full">
                {/* Left side - Upload button */}
                <button
                  className="flex items-center justify-center w-8 h-8 rounded-full border border-border hover:bg-accent transition-colors"
                  title="上传文件"
                  disabled={isLoading}
                >
                  <Plus className="w-4 h-4 text-muted-foreground" />
                </button>
                
                {/* Center - Disclaimer */}
                <p className="text-xs text-muted-foreground flex-1 text-center mx-4">
                  {t.chat.aiDisclaimer}
                </p>
                
                {/* Right side - Send button */}
                <button
                  className={`flex items-center justify-center w-8 h-8 rounded-full transition-colors ${
                    !inputValue.trim() || isLoading
                      ? "bg-muted hover:bg-muted text-muted-foreground"
                      : "bg-primary hover:bg-primary/90 text-primary-foreground"
                  }`}
                  onClick={handleSend}
                  disabled={!inputValue.trim() || isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <ArrowUp className="w-4 h-4" />
                  )}
                </button>
              </div>
            </InputGroupAddon>
          </InputGroup>
        </div>
      </div>
    </div>
  );
}
