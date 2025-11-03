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
import { usePresetQuestionsStore } from "@/store/presetQuestionsStore";
import { uploadChatFile } from "@/lib/api/files";
import { useTranslation } from "@/lib/hooks/useTranslation";
import { useStreamingChat } from "@/lib/hooks/useStreamingChat";
import type { ChatAttachment, ChatMessage } from "@/lib/types/api";
import { MAX_FILE_SIZE, SUPPORTED_FILE_TYPES } from "@/lib/constants";
import type { AgentWithMetadata } from "@/lib/types/prompt";
import {
    ChatMessage as ChatMessageComponent,
    StreamingMessage,
    FileUploadProgress,
    UploadStatus,
} from "@/components/chat";
import {
    Loader2,
    Bot,
    Lightbulb,
    Wrench,
    TrendingUp,
    FlaskConical,
    Plus,
    ArrowUp,
    ShieldCheck,
    Zap,
    FileText,
    X,
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

const SUPPORTED_EXTENSIONS = Object.values(SUPPORTED_FILE_TYPES).reduce<
    string[]
>((acc, group) => acc.concat(group), []);

const ACCEPTED_FILE_TYPES = SUPPORTED_EXTENSIONS.join(",");

const formatFileSize = (size?: number) => {
    if (!size) {
        return "0 B";
    }
    const units = ["B", "KB", "MB", "GB"];
    let value = size;
    let unitIndex = 0;

    while (value >= 1024 && unitIndex < units.length - 1) {
        value /= 1024;
        unitIndex += 1;
    }

    const precision = value >= 10 || unitIndex === 0 ? 0 : 1;
    return `${value.toFixed(precision)} ${units[unitIndex]}`;
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
        greeting:
            "您好！我是设备诊断专家，可以帮您诊断设备故障并提供维护建议。",
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
            question:
                "连铸过程中出现拉坯断裂问题，可能的原因和解决方案有哪些？",
        },
    ],
    equipment: [
        {
            title: "高炉设备诊断",
            question: "高炉炉温异常升高，伴有炉况不稳，应该如何诊断和处理？",
        },
        {
            title: "轧机故障分析",
            question:
                "轧机出现异常振动和噪音，可能的故障原因和检修方案是什么？",
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
            question:
                "在原料价格波动的情况下，钢企如何制定有效的成本控制策略？",
        },
    ],
    quality: [
        {
            title: "化学成分控制",
            question: "如何精确控制钢材的碳含量和合金元素，确保产品质量稳定？",
        },
        {
            title: "表面质量改善",
            question:
                "钢板表面出现氧化皮和划痕缺陷，如何改进工艺来提升表面质量？",
        },
        {
            title: "力学性能优化",
            question: "如何通过热处理工艺调整来提高钢材的强度和韧性？",
        },
        {
            title: "质量检测方法",
            question:
                "钢材生产中有哪些先进的无损检测技术可以提高质量控制水平？",
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
            question:
                "钢铁生产过程中如何有效监测和管理碳排放，实现碳中和目标？",
        },
    ],
};

export default function DashboardPage() {
    const t = useTranslation();
    const [inputValue, setInputValue] = useState("");
    const [error, setError] = useState<string>("");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState<UploadStatus>("uploading");
    const [uploadError, setUploadError] = useState<string>("");
    const [currentUploadFile, setCurrentUploadFile] = useState<string>("");

    // 新增：文件预览状态
    const [pendingFile, setPendingFile] = useState<{
        file: File;
        attachment: ChatAttachment;
    } | null>(null);

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
            const generalAgent = agents.find(
                (agent) => agent.name === "general",
            );
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

    const getMessageAgentInfo = () =>
        currentAgentData
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

    // 流式聊天Hook
    const {
        isStreaming,
        streamingContent,
        sendMessage: sendStreamingMessage,
        cancelStreaming,
    } = useStreamingChat({
        sessionId: currentSessionId || undefined,
        agentId: selectedAgent,
        agentType: currentAgentData?.name || selectedAgent, // 修正：使用 Agent 的 name 字段（如 "general", "process"）作为 agent_type
        onMessageComplete: (message: ChatMessage) => {
            const sessionId =
                currentSessionId || createSession(`${currentAgent.name}对话`);
            addMessage(sessionId, {
                ...message,
                agentId: selectedAgent,
                agentInfo: getMessageAgentInfo(),
            });
        },
        onError: (err: Error) => {
            setError(err.message);
        },
    });

    // Get current session messages
    const currentSession = sessions.find((s) => s.id === currentSessionId);
    const messages = React.useMemo(
        () => currentSession?.messages ?? [],
        [currentSession],
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
    }, [
        currentAgentData,
        currentAgentPrompt,
        initialized,
        currentSystemPrompt,
        setSelectedAgentData,
    ]);

    const handleUploadClick = () => {
        if (isUploading) {
            return;
        }
        fileInputRef.current?.click();
    };

    const handleFileChange = async (
        event: React.ChangeEvent<HTMLInputElement>,
    ) => {
        const input = event.target as HTMLInputElement;
        const file = input.files?.[0];
        if (!file) {
            return;
        }

        const extension = file.name.includes(".")
            ? `.${file.name.split(".").pop()?.toLowerCase() || ""}`
            : "";
        if (
            SUPPORTED_EXTENSIONS.length > 0 &&
            extension &&
            !SUPPORTED_EXTENSIONS.includes(extension)
        ) {
            setError(t.chat.uploadUnsupported);
            input.value = "";
            return;
        }

        if (file.size > MAX_FILE_SIZE) {
            setError(t.chat.uploadTooLarge);
            input.value = "";
            return;
        }

        setIsUploading(true);
        setUploadProgress(0);
        setUploadStatus("uploading");
        setUploadError("");
        setCurrentUploadFile(file.name);
        setError("");

        try {
            const response = await uploadChatFile(file, (progressEvent) => {
                if (!progressEvent.total) {
                    return;
                }
                const percent = Math.round(
                    (progressEvent.loaded / progressEvent.total) * 100,
                );
                setUploadProgress(percent);
            });

            if (!response.success) {
                setUploadStatus("error");
                setUploadError(response.message || t.chat.uploadFailed);
                throw new Error(response.message || t.chat.uploadFailed);
            }

            setUploadStatus("success");

            const attachment: ChatAttachment = {
                fileId: response.fileId || `upload_${Date.now()}`,
                fileName: response.fileName || file.name,
                fileSize: response.fileSize ?? file.size,
                contentType: response.contentType || file.type,
                chunks: response.chunks,
                rawPath: response.rawPath,
                processedPath: response.processedPath,
                uploadedAt: new Date(),
            };

            // 修改：不立即发送消息，而是设置为待发送状态
            setPendingFile({ file, attachment });
        } catch (err) {
            console.error("File upload failed:", err);
            setUploadStatus("error");
            const serverMessage = (
                err as { response?: { data?: { message?: string } } }
            ).response?.data?.message;
            setUploadError(
                serverMessage ||
                    (err instanceof Error ? err.message : t.chat.uploadFailed),
            );
            const fallback = err instanceof Error ? err.message : undefined;
            setError(serverMessage || fallback || t.chat.uploadFailed);
        } finally {
            setIsUploading(false);
            setUploadProgress(0);
            input.value = "";
        }
    };

    // 新增：移除待发送文件
    const handleRemovePendingFile = () => {
        setPendingFile(null);
    };

    const handleSend = async () => {
        if ((!inputValue.trim() && !pendingFile) || isStreaming) return;

        const userMessage = inputValue.trim();
        const sessionId =
            currentSessionId || createSession(`${currentAgent.name}对话`);

        // 准备Agent信息用于存储在消息中
        const agentInfo = getMessageAgentInfo();

        // 如果有待发送的文件，创建包含附件的消息
        if (pendingFile) {
            const template = "文件上传成功";
            const fileMessage = `${template}: ${pendingFile.attachment.fileName}`;

            const content = userMessage
                ? `${userMessage}\n\n${fileMessage}`
                : fileMessage;

            const userMsg: ChatMessage = {
                id: `msg_${Date.now()}_user`,
                role: "user",
                content,
                timestamp: new Date(),
                agentId: selectedAgent,
                agentInfo,
                attachments: [pendingFile.attachment],
            };

            // Add user message to store
            addMessage(sessionId, userMsg);

            // 清除待发送文件和输入内容
            setPendingFile(null);
            setInputValue("");
        } else {
            // 普通文本消息
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
        }

        setError("");

        // 使用流式发送
        try {
            await sendStreamingMessage(userMessage);

            // Auto-generate title for new conversations
            const session = sessions.find((s) => s.id === sessionId);
            if (session && session.messages.length === 0) {
                const title =
                    userMessage.length > 20
                        ? userMessage.substring(0, 20) + "..."
                        : userMessage;
                updateSessionTitle(sessionId, title);
            }
        } catch (err) {
            console.error("Failed to send message:", err);
            setError(
                err instanceof Error ? err.message : "消息发送失败，请重试",
            );
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
                                            currentAgent.colorScheme
                                                ?.background ||
                                            currentAgent.color
                                        } p-6 rounded-2xl border-2 ${
                                            currentAgent.colorScheme?.border ||
                                            "border-transparent"
                                        }`}
                                    >
                                        <AgentIcon
                                            className={`w-12 h-12 ${
                                                currentAgent.colorScheme
                                                    ?.primary || "text-white"
                                            }`}
                                        />
                                    </div>
                                </div>
                                <h1 className="text-3xl font-bold mb-2">
                                    {currentAgent.name}
                                </h1>
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
                                                    加载预设问题失败:{" "}
                                                    {questionsError}
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
                                                    setInputValue(
                                                        preset.question,
                                                    );
                                                    // 增加使用次数
                                                    try {
                                                        await incrementQuestionUsage(
                                                            preset.id,
                                                        );
                                                    } catch (error) {
                                                        console.warn(
                                                            "Failed to increment question usage:",
                                                            error,
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
                                                                分类:{" "}
                                                                {
                                                                    preset.category
                                                                }
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
                                                agentPresetQuestions[
                                                    selectedAgent
                                                ] ||
                                                agentPresetQuestions.general;
                                            return fallbackQuestions.map(
                                                (preset, index) => (
                                                    <Card
                                                        key={`fallback-${index}`}
                                                        className="p-4 cursor-pointer hover:shadow-md hover:scale-[1.02] transition-all duration-200 border-2 hover:border-primary/20"
                                                        onClick={() => {
                                                            setInputValue(
                                                                preset.question,
                                                            );
                                                        }}
                                                    >
                                                        <div className="flex items-start gap-3">
                                                            <AgentIcon className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                                                            <div className="flex-1 min-w-0">
                                                                <div className="text-sm font-medium mb-1 text-foreground">
                                                                    {
                                                                        preset.title
                                                                    }
                                                                </div>
                                                                <div className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                                                                    {
                                                                        preset.question
                                                                    }
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </Card>
                                                ),
                                            );
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
                                const MessageIcon = getIconByName(
                                    messageAgent.icon,
                                ) as React.ComponentType<{
                                    className?: string;
                                }>;

                                return (
                                    <ChatMessageComponent
                                        key={message.id || index}
                                        message={message}
                                        agentIcon={MessageIcon}
                                        agentName={messageAgent.name}
                                        agentColorScheme={
                                            messageAgent.colorScheme
                                        }
                                        showReasoningSteps={true}
                                    />
                                );
                            })}

                            {/* 流式响应显示 */}
                            {isStreaming && (
                                <StreamingMessage
                                    content={streamingContent}
                                    agentIcon={
                                        AgentIcon as React.ComponentType<{
                                            className?: string;
                                        }>
                                    }
                                    agentName={currentAgent.name}
                                    agentColorScheme={currentAgent.colorScheme}
                                    isTyping={true}
                                />
                            )}

                            {/* 旧版加载指示器（兼容非流式模式） - 已移除 */}
                            {false && !isStreaming && (
                                <div className="flex gap-4 justify-start">
                                    <Avatar className="h-8 w-8 flex-shrink-0">
                                        <AvatarFallback
                                            className={
                                                currentAgent.colorScheme
                                                    ?.background ||
                                                currentAgent.color
                                            }
                                        >
                                            <AgentIcon
                                                className={`w-4 h-4 ${
                                                    currentAgent.colorScheme
                                                        ?.primary ||
                                                    "text-white"
                                                }`}
                                            />
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="bg-white text-gray-900 border-gray-200 rounded-xl px-3 py-2 border">
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

                {/* Error Alert - 放在消息区域内 */}
                {error && (
                    <div className="px-4 md:px-6 flex-shrink-0">
                        <Alert
                            variant="destructive"
                            className="max-w-4xl mx-auto"
                        >
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    </div>
                )}
            </div>

            {/* Input Area - 固定在容器底部 */}
            <div className="sticky bottom-0 flex-shrink-0 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 p-4 md:p-6 shadow-lg shadow-black/5">
                <div className="max-w-4xl mx-auto space-y-3">
                    {/* 文件上传进度条 */}
                    {isUploading && currentUploadFile && (
                        <FileUploadProgress
                            fileName={currentUploadFile}
                            progress={uploadProgress}
                            status={uploadStatus}
                            errorMessage={uploadError}
                        />
                    )}

                    <InputGroup>
                        {/* 文件预览区域 */}
                        {pendingFile && (
                            <div className="mb-3 p-3 bg-muted/50 rounded-lg border border-border/50">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <FileText className="w-5 h-5 text-muted-foreground" />
                                        <div className="flex-1 min-w-0">
                                            <div className="font-medium text-sm truncate">
                                                {
                                                    pendingFile.attachment
                                                        .fileName
                                                }
                                            </div>
                                            <div className="text-xs text-muted-foreground">
                                                {formatFileSize(
                                                    pendingFile.attachment
                                                        .fileSize,
                                                )}
                                                {pendingFile.attachment.chunks
                                                    ?.length && (
                                                    <span className="ml-2">
                                                        •{" "}
                                                        {
                                                            pendingFile
                                                                .attachment
                                                                .chunks.length
                                                        }{" "}
                                                        个片段
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                    <button
                                        onClick={handleRemovePendingFile}
                                        className="flex items-center justify-center w-6 h-6 rounded-full hover:bg-muted transition-colors"
                                        title="移除文件"
                                    >
                                        <X className="w-4 h-4 text-muted-foreground" />
                                    </button>
                                </div>

                                {/* 文件内容预览 */}
                                {pendingFile.attachment.chunks?.length ? (
                                    <details className="mt-2 text-xs text-muted-foreground">
                                        <summary className="cursor-pointer select-none hover:text-foreground">
                                            {`${t.chat.uploadPreview} (${pendingFile.attachment.chunks.length})`}
                                        </summary>
                                        <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                                            {pendingFile.attachment.chunks
                                                .slice(0, 3)
                                                .map((chunk, index) => (
                                                    <div
                                                        key={`${pendingFile.attachment.fileId}-${index}`}
                                                        className="rounded-md bg-muted/60 px-2 py-1 leading-snug"
                                                    >
                                                        {chunk.content.length >
                                                        160
                                                            ? `${chunk.content.substring(0, 160)}...`
                                                            : chunk.content}
                                                    </div>
                                                ))}
                                            {pendingFile.attachment.chunks
                                                .length > 3 && (
                                                <div className="text-center text-muted-foreground">
                                                    ... 还有{" "}
                                                    {pendingFile.attachment
                                                        .chunks.length - 3}{" "}
                                                    个片段
                                                </div>
                                            )}
                                        </div>
                                    </details>
                                ) : null}
                            </div>
                        )}

                        <InputGroupTextarea
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder={
                                pendingFile
                                    ? "添加消息内容（可选）..."
                                    : "提问、搜索或聊天..."
                            }
                            className="min-h-[60px] max-h-[200px] resize-none"
                            disabled={isStreaming}
                        />

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept={ACCEPTED_FILE_TYPES}
                            className="hidden"
                            onChange={handleFileChange}
                        />

                        {/* Bottom row with buttons and disclaimer inside InputGroup */}
                        <InputGroupAddon align="block-end">
                            <div className="flex items-center justify-between w-full">
                                {/* Left side - Upload button */}
                                <button
                                    className="flex items-center justify-center w-8 h-8 rounded-full border border-border hover:bg-accent transition-colors disabled:opacity-60"
                                    title={t.chat.upload}
                                    onClick={handleUploadClick}
                                    disabled={isUploading || isStreaming}
                                    aria-busy={isUploading}
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
                                        (!inputValue.trim() && !pendingFile) ||
                                        isStreaming
                                            ? "bg-muted hover:bg-muted text-muted-foreground"
                                            : "bg-primary hover:bg-primary/90 text-primary-foreground"
                                    }`}
                                    onClick={
                                        isStreaming
                                            ? cancelStreaming
                                            : handleSend
                                    }
                                    disabled={
                                        !inputValue.trim() && !pendingFile
                                    }
                                    title={
                                        isStreaming ? "取消生成" : "发送消息"
                                    }
                                >
                                    {isStreaming ? (
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
