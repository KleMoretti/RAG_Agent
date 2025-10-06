"use client";

import * as React from "react";
import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  InputGroup,
  InputGroupTextarea,
  InputGroupAddon,
} from "@/components/ui/input-group";
import { cn } from "@/lib/utils";
import { useChatStore } from "@/store/chatStore";
import { usePromptStore } from "@/store/promptStore";
import { usePresetQuestionsStore } from "@/store/presetQuestionsStore";
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

// 获取Agent图标
const getAgentIcon = (agent: AgentWithMetadata): React.ElementType => {
  if (agent.icon && defaultIcons[agent.icon]) {
    return defaultIcons[agent.icon];
  }
  return defaultIcons[agent.id] || Bot;
};

// 获取图标名称（用于存储在消息中）
const getAgentIconName = (agent: AgentWithMetadata): string => {
  if (agent.icon && defaultIcons[agent.icon]) {
    return agent.icon;
  }
  return agent.id in defaultIcons ? agent.id : "general";
};

// 根据图标名称获取图标组件
const getIconByName = (iconName: string): React.ElementType => {
  return defaultIcons[iconName] || Bot;
};

// Agent metadata (保留作为fallback)
const agentMetadata: Record<
  string,
  {
    name: string;
    icon: React.ElementType;
    color: string;
    colorScheme?: import("@/lib/types/prompt").AgentColorScheme;
    greeting: string;
  }
> = {
  general: {
    name: "通用助手",
    icon: Bot,
    color: "bg-blue-500",
    colorScheme: {
      primary: "text-white",
      secondary: "text-blue-100",
      background: "bg-blue-500",
      border: "border-blue-500",
      hover: "hover:bg-blue-600",
      selected: "bg-blue-600",
      bubble: {
        background: "bg-blue-500",
        text: "text-white",
        border: "border-blue-500",
      },
    },
    greeting: "您好！我是通用 AI 助手，可以帮您解答各类问题。",
  },
  process: {
    name: "工艺专家",
    icon: FlaskConical,
    color: "bg-orange-500",
    colorScheme: {
      primary: "text-white",
      secondary: "text-orange-100",
      background: "bg-orange-500",
      border: "border-orange-500",
      hover: "hover:bg-orange-600",
      selected: "bg-orange-600",
      bubble: {
        background: "bg-orange-500",
        text: "text-white",
        border: "border-orange-500",
      },
    },
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

const markdownComponents: Components = {
  p: ({ children }) => (
    <p className="mb-2 last:mb-0 leading-relaxed break-words">{children}</p>
  ),
  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="font-medium text-primary underline underline-offset-4 hover:text-primary/80"
    >
      {children}
    </a>
  ),
  ul: ({ children }) => (
    <ul className="mb-2 last:mb-0 ml-4 list-disc space-y-1">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-2 last:mb-0 ml-4 list-decimal space-y-1">{children}</ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="mb-2 last:mb-0 border-l-2 border-primary/40 pl-3 italic text-muted-foreground">
      {children}
    </blockquote>
  ),
  code: ({ inline, className, children, ...props }) => {
    if (inline) {
      return (
        <code
          className={cn(
            "rounded-md bg-primary/10 px-1.5 py-0.5 text-xs font-medium text-primary",
            className
          )}
          {...props}
        >
          {children}
        </code>
      );
    }

    return (
      <code
        className={cn(
          "block max-w-full overflow-x-auto rounded-lg bg-muted/70 p-4 text-xs leading-relaxed text-muted-foreground",
          className
        )}
        {...props}
      >
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre className="mb-2 last:mb-0 overflow-x-auto rounded-lg bg-muted/70 p-0">
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div className="mb-2 last:mb-0 overflow-x-auto rounded-lg border border-border/60">
      <table className="w-full text-left text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-muted/50 text-muted-foreground">{children}</thead>
  ),
  tbody: ({ children }) => (
    <tbody className="divide-y divide-border/60">{children}</tbody>
  ),
  th: ({ children }) => (
    <th className="px-3 py-2 font-medium text-muted-foreground">{children}</th>
  ),
  td: ({ children }) => <td className="px-3 py-2">{children}</td>,
  hr: () => <hr className="my-4 border-border/60" />,
};

// Suggested prompts
// 为每个Agent定制的预设问题
const agentPresetQuestions: Record<
  string,
  Array<{
    title: string;
    question: string;
  }>
> = {
  general: [
    {
      title: "钢铁行业概况",
      question: "请介绍一下当前中国钢铁行业的发展现状和主要特点",
    },
    {
      title: "技术发展趋势",
      question: "钢铁行业有哪些新兴技术和发展趋势值得关注？",
    },
    {
      title: "政策法规解读",
      question: "最近有哪些影响钢铁行业的重要政策和法规变化？",
    },
    {
      title: "可持续发展",
      question: "钢铁企业如何实现绿色低碳转型和可持续发展？",
    },
  ],
  process: [
    {
      title: "炼钢工艺优化",
      question: "如何优化转炉炼钢工艺，提高钢水质量和生产效率？",
    },
    {
      title: "轧制参数调整",
      question: "热轧过程中如何调整轧制温度和压下量来改善产品性能？",
    },
    {
      title: "合金化技术",
      question: "生产高强度钢材时，合金元素的添加顺序和比例如何控制？",
    },
    {
      title: "工艺故障排查",
      question: "连铸过程中出现拉坯断裂问题，可能的原因和解决方案有哪些？",
    },
  ],
  equipment: [
    {
      title: "高炉设备诊断",
      question: "高炉炉温异常升高，伴有炉况不稳，应该如何诊断和处理？",
    },
    {
      title: "轧机故障分析",
      question: "轧机出现异常振动和噪音，可能的故障原因和检修方案是什么？",
    },
    {
      title: "预防性维护",
      question: "转炉设备的预防性维护计划应该包含哪些关键检查项目？",
    },
    {
      title: "设备升级改造",
      question: "老旧烧结机如何进行技术改造以提高环保性能和生产效率？",
    },
  ],
  market: [
    {
      title: "铁矿石价格分析",
      question: "当前铁矿石价格走势如何？影响价格变动的主要因素有哪些？",
    },
    {
      title: "钢材需求预测",
      question: "未来6个月建筑钢材和板材的市场需求趋势如何？",
    },
    {
      title: "国际贸易影响",
      question: "国际贸易政策变化对中国钢铁出口有什么影响？",
    },
    {
      title: "成本控制策略",
      question: "在原料价格波动的情况下，钢企如何制定有效的成本控制策略？",
    },
  ],
  quality: [
    {
      title: "化学成分控制",
      question: "如何精确控制钢材的碳含量和合金元素，确保产品质量稳定？",
    },
    {
      title: "表面质量改善",
      question: "钢板表面出现氧化皮和划痕缺陷，如何改进工艺来提升表面质量？",
    },
    {
      title: "力学性能优化",
      question: "如何通过热处理工艺调整来提高钢材的强度和韧性？",
    },
    {
      title: "质量检测方法",
      question: "钢材生产中有哪些先进的无损检测技术可以提高质量控制水平？",
    },
  ],
  environment: [
    {
      title: "节能减排方案",
      question: "钢铁企业有哪些有效的节能减排技术和实施方案？",
    },
    {
      title: "废气处理优化",
      question: "如何优化烧结烟气脱硫脱硝系统，提高环保处理效果？",
    },
    {
      title: "循环经济模式",
      question: "钢铁企业如何构建循环经济模式，实现资源的高效利用？",
    },
    {
      title: "碳排放管理",
      question: "钢铁生产过程中如何有效监测和管理碳排放，实现碳中和目标？",
    },
  ],
};

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
    isInitialized, // 添加：检查是否已初始化
  } = useChatStore();

  const {
    agents,
    initialized,
    initialize,
    currentAgentPrompt, // 添加：当前Agent的预设Prompt
    setSelectedAgent, // 添加：设置选中的Agent（带缓存）
  } = usePromptStore();

  const {
    currentAgentQuestions,
    loading: questionsLoading,
    error: questionsError,
    loadQuestionsByAgentName,
    incrementQuestionUsage,
    initialize: initializeQuestions,
    initialized: questionsInitialized,
  } = usePresetQuestionsStore();

  // 初始化Prompt Store
  useEffect(() => {
    if (!initialized) {
      initialize();
    }
  }, [initialized, initialize]);

  // 初始化预设问题Store
  useEffect(() => {
    if (!questionsInitialized) {
      initializeQuestions();
    }
  }, [questionsInitialized, initializeQuestions]);

  // 自动选中通用助手作为默认选项
  useEffect(() => {
    if (initialized && agents.length > 0 && !selectedAgentData) {
      // 查找通用助手（使用name字段）
      const generalAgent = agents.find((agent) => agent.name === "general");
      if (generalAgent) {
        // 自动选中通用助手
        setSelectedAgent(generalAgent);
      }
    }
  }, [initialized, agents, selectedAgentData, setSelectedAgent]);

  // 根据选中的Agent加载预设问题
  useEffect(() => {
    if (questionsInitialized && selectedAgentData) {
      // 使用Agent的name字段作为API参数
      const agentName = selectedAgentData.name;
      loadQuestionsByAgentName(agentName);
    }
  }, [questionsInitialized, selectedAgentData, loadQuestionsByAgentName]);

  // 获取当前Agent数据
  const currentAgentData =
    selectedAgentData || agents.find((a) => a.id === selectedAgent);
  const fallbackAgent = agentMetadata[selectedAgent] || agentMetadata.general;

  // 使用真实Agent数据或fallback
  const currentAgent = currentAgentData
    ? {
        name: currentAgentData.displayName || currentAgentData.name,
        icon: getAgentIcon(currentAgentData),
        color: fallbackAgent.color, // 保留作为后备
        colorScheme: currentAgentData.colorScheme,
        greeting: currentAgentData.greeting || fallbackAgent.greeting,
      }
    : fallbackAgent;

  const AgentIcon = currentAgent.icon;

  // Get current session messages
  const currentSession = sessions.find((s) => s.id === currentSessionId);
  const messages = React.useMemo(
    () => currentSession?.messages ?? [],
    [currentSession]
  );

  // Auto-scroll to bottom when messages change or loading state changes
  useEffect(() => {
    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "nearest",
      });
    };

    // 使用 requestAnimationFrame 确保 DOM 更新后再滚动
    const timeoutId = setTimeout(() => {
      requestAnimationFrame(scrollToBottom);
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [messages, isLoading]);

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
  }, [
    currentAgentData,
    currentAgentPrompt,
    initialized,
    currentSystemPrompt,
    setSelectedAgentData,
  ]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    const sessionId =
      currentSessionId || createSession(`${currentAgent.name}对话`);

    // 准备Agent信息用于存储在消息中
    const agentInfo = currentAgentData
      ? {
          name: currentAgentData.displayName || currentAgentData.name,
          icon: getAgentIconName(currentAgentData),
          colorScheme: currentAgentData.colorScheme,
        }
      : {
          name: currentAgent.name,
          icon: selectedAgent,
          colorScheme: currentAgent.colorScheme,
        };

    const userMsg: ChatMessage = {
      id: `msg_${Date.now()}_user`,
      role: "user",
      content: userMessage,
      timestamp: new Date(),
      agentId: selectedAgent,
      agentInfo,
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
        agentId: selectedAgent,
        agentInfo,
      };

      // Add assistant message to store
      addMessage(sessionId, assistantMsg);

      // Auto-generate title for new conversations
      const session = sessions.find((s) => s.id === sessionId);
      if (session && session.messages.length === 0) {
        // Generate a short title from the user message
        const title =
          userMessage.length > 20
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
  return (
    <div className="flex flex-1 h-full min-h-0 flex-col overflow-hidden">
      {/* 固定高度的聊天容器 */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* 可滚动的消息显示区域 - 自动填充剩余高度 */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent hover:scrollbar-thumb-gray-400">
          {messages.length === 0 ? (
            // Welcome screen
            <div className="flex flex-col items-center justify-center h-full max-w-4xl mx-auto">
              <div className="text-center mb-12">
                <div className="flex justify-center mb-6">
                  <div
                    className={`${
                      currentAgent.colorScheme?.background || currentAgent.color
                    } p-6 rounded-2xl border-2 ${
                      currentAgent.colorScheme?.border || "border-transparent"
                    }`}
                  >
                    <AgentIcon
                      className={`w-12 h-12 ${
                        currentAgent.colorScheme?.primary || "text-white"
                      }`}
                    />
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
                  {questionsLoading ? (
                    // 加载状态
                    <div className="col-span-full flex justify-center items-center py-8">
                      <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                      <span className="ml-2 text-sm text-muted-foreground">
                        加载预设问题中...
                      </span>
                    </div>
                  ) : questionsError ? (
                    // 错误状态
                    <div className="col-span-full">
                      <Alert>
                        <AlertDescription>
                          加载预设问题失败: {questionsError}
                        </AlertDescription>
                      </Alert>
                    </div>
                  ) : currentAgentQuestions.length > 0 ? (
                    // 显示API数据
                    currentAgentQuestions.map((preset) => (
                      <Card
                        key={preset.id}
                        className="p-4 cursor-pointer hover:shadow-md hover:scale-[1.02] transition-all duration-200 border-2 hover:border-primary/20"
                        onClick={async () => {
                          // 点击后自动填充问题到输入框
                          setInputValue(preset.question);
                          // 增加使用次数
                          try {
                            await incrementQuestionUsage(preset.id);
                          } catch (error) {
                            console.warn(
                              "Failed to increment question usage:",
                              error
                            );
                          }
                        }}
                      >
                        <div className="flex items-start gap-3">
                          <AgentIcon className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium mb-1 text-foreground">
                              {preset.title}
                            </div>
                            <div className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                              {preset.question}
                            </div>
                            {preset.category && (
                              <div className="text-xs text-muted-foreground/70 mt-1">
                                分类: {preset.category}
                              </div>
                            )}
                          </div>
                        </div>
                      </Card>
                    ))
                  ) : (
                    // 回退到硬编码数据
                    (() => {
                      const fallbackQuestions =
                        agentPresetQuestions[selectedAgent] ||
                        agentPresetQuestions.general;
                      return fallbackQuestions.map((preset, index) => (
                        <Card
                          key={`fallback-${index}`}
                          className="p-4 cursor-pointer hover:shadow-md hover:scale-[1.02] transition-all duration-200 border-2 hover:border-primary/20"
                          onClick={() => {
                            setInputValue(preset.question);
                          }}
                        >
                          <div className="flex items-start gap-3">
                            <AgentIcon className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="text-sm font-medium mb-1 text-foreground">
                                {preset.title}
                              </div>
                              <div className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                                {preset.question}
                              </div>
                            </div>
                          </div>
                        </Card>
                      ));
                    })()
                  )}
                </div>
              </div>
            </div>
          ) : (
            // Messages display
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((message, index) => {
                // 获取消息对应的Agent信息
                const messageAgent = message.agentInfo || {
                  name: currentAgent.name,
                  icon: selectedAgent,
                  colorScheme: currentAgent.colorScheme,
                };

                // 获取消息对应的图标组件
                const MessageIcon = getIconByName(messageAgent.icon);
                const isUserMessage = message.role === "user";
                const userBackgroundClass =
                  messageAgent.colorScheme?.background || "bg-primary";
                const userTextClass =
                  messageAgent.colorScheme?.primary ||
                  "text-primary-foreground";
                const userBorderClass =
                  messageAgent.colorScheme?.border || "border-primary";
                const assistantBackgroundClass = "bg-card";
                const assistantTextClass = "text-card-foreground";
                const assistantBorderClass = "border-border";

                return (
                  <div
                    key={message.id || index}
                    className={`flex gap-4 ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    {message.role === "assistant" && (
                      <Avatar className="h-8 w-8 flex-shrink-0">
                        <AvatarFallback
                          className={
                            messageAgent.colorScheme?.background ||
                            currentAgent.color
                          }
                        >
                          <MessageIcon
                            className={`w-4 h-4 ${
                              messageAgent.colorScheme?.primary || "text-white"
                            }`}
                          />
                        </AvatarFallback>
                      </Avatar>
                    )}

                    <div
                      className={cn(
                        "rounded-xl px-3 py-2 max-w-[60%] border text-sm space-y-2",
                        isUserMessage
                          ? [
                              userBackgroundClass,
                              userTextClass,
                              userBorderClass,
                            ]
                          : [
                              assistantBackgroundClass,
                              assistantTextClass,
                              assistantBorderClass,
                            ]
                      )}
                    >
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeRaw]}
                        components={markdownComponents}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>

                    {message.role === "user" && (
                      <Avatar className="h-8 w-8 flex-shrink-0">
                        <AvatarFallback className="bg-gray-100">
                          <User className="w-4 h-4 text-gray-600" />
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                );
              })}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex gap-4 justify-start">
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback
                      className={
                        currentAgent.colorScheme?.background ||
                        currentAgent.color
                      }
                    >
                      <AgentIcon
                        className={`w-4 h-4 ${
                          currentAgent.colorScheme?.primary || "text-white"
                        }`}
                      />
                    </AvatarFallback>
                  </Avatar>
                  <div className="bg-white text-gray-900 border-gray-200 rounded-xl px-3 py-2 border">
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-3 h-3 animate-spin text-primary" />
                      <span className="text-sm">{t.chat.thinking}</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Error Alert - 放在消息区域内 */}
        {error && (
          <div className="px-4 md:px-6 flex-shrink-0">
            <Alert variant="destructive" className="max-w-4xl mx-auto">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </div>
        )}
      </div>

      {/* Input Area - 固定在容器底部 */}
      <div className="sticky bottom-0 flex-shrink-0 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 p-4 md:p-6 shadow-lg shadow-black/5">
        <div className="max-w-4xl mx-auto">
          <InputGroup>
            <InputGroupTextarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask, Search or Chat..."
              className="min-h-[60px] max-h-[200px] resize-none"
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
