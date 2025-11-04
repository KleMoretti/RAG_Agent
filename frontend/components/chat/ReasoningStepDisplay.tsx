"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import {
    Brain,
    Wrench,
    Search,
    CheckCircle2,
    AlertCircle,
    Lightbulb,
    ChevronDown,
    ChevronUp,
    FileText,
} from "lucide-react";
import type { ReasoningStep } from "@/lib/types/api";

interface ReasoningStepDisplayProps {
    steps: ReasoningStep[];
    defaultExpanded?: boolean;
}

/**
 * 推理步骤类型映射
 */
const getStepType = (step: ReasoningStep): "thought" | "tool" | "observation" | "conclusion" => {
    if (step.observation) return "observation";
    if (step.toolName) return "tool";
    if (step.thought.includes("结论") || step.thought.includes("总结")) return "conclusion";
    return "thought";
};

/**
 * 智能总结内容
 * - 移除元信息前缀（如 "Generated a response for the query"）
 * - 识别并总结【检索上下文】等冗长内容
 * - 提取关键信息而不是全部展示
 */
const summarizeContent = (content: string): { summary: string; details?: string; hasDetails: boolean } => {
    if (!content) return { summary: "", hasDetails: false };

    // 移除 "Generated a response for the query" 等元信息
    let cleaned = content
        .replace(/^Generated a response for the query\s*['""]?/i, "")
        .replace(/^生成回答：/i, "")
        .trim();

    // 检测是否包含【检索上下文】
    const hasContext = cleaned.includes("【检索上下文】");
    if (hasContext) {
        // 提取用户问题
        const questionMatch = cleaned.match(/^(.+?)【检索上下文】/);
        const userQuestion = questionMatch ? questionMatch[1].trim() : "";

        // 提取检索上下文（使用 [\s\S] 代替 . 以匹配换行符）
        const contextMatch = cleaned.match(/【检索上下文】([\s\S]+?)(?:【用户问题】|$)/);
        const contextContent = contextMatch ? contextMatch[1].trim() : "";

        // 提取用户问题（如果有独立的部分）
        const finalQuestionMatch = cleaned.match(/【用户问题】([\s\S]+)$/);
        const finalQuestion = finalQuestionMatch ? finalQuestionMatch[1].trim() : userQuestion;

        // 统计检索到的文档片段数量（简单统计）
        const snippetCount = (contextContent.match(/\n\n/g) || []).length + 1;
        const contextPreview = contextContent.slice(0, 150) + (contextContent.length > 150 ? "..." : "");

        // 生成简洁的摘要
        const summary = finalQuestion
            ? `分析问题：${finalQuestion}\n📚 检索到 ${snippetCount} 个相关文档片段`
            : `📚 检索到 ${snippetCount} 个相关文档片段用于回答`;

        return {
            summary,
            details: `**原始查询：**\n${userQuestion || finalQuestion}\n\n**检索上下文预览：**\n${contextPreview}`,
            hasDetails: true,
        };
    }

    // 对于超长内容（>300字符），截断并提供详情
    const MAX_LENGTH = 300;
    if (cleaned.length > MAX_LENGTH) {
        return {
            summary: cleaned.slice(0, MAX_LENGTH) + "...",
            details: cleaned,
            hasDetails: true,
        };
    }

    return { summary: cleaned, hasDetails: false };
};

/**
 * 推理步骤视觉配置
 */
const stepConfig = {
    thought: {
        icon: Brain,
        label: "思考",
        bgColor: "bg-blue-50 dark:bg-blue-950/30",
        borderColor: "border-blue-200 dark:border-blue-800",
        iconColor: "text-blue-600 dark:text-blue-400",
        textColor: "text-blue-900 dark:text-blue-100",
    },
    tool: {
        icon: Wrench,
        label: "工具调用",
        bgColor: "bg-purple-50 dark:bg-purple-950/30",
        borderColor: "border-purple-200 dark:border-purple-800",
        iconColor: "text-purple-600 dark:text-purple-400",
        textColor: "text-purple-900 dark:text-purple-100",
    },
    observation: {
        icon: Search,
        label: "观察结果",
        bgColor: "bg-green-50 dark:bg-green-950/30",
        borderColor: "border-green-200 dark:border-green-800",
        iconColor: "text-green-600 dark:text-green-400",
        textColor: "text-green-900 dark:text-green-100",
    },
    conclusion: {
        icon: CheckCircle2,
        label: "结论",
        bgColor: "bg-amber-50 dark:bg-amber-950/30",
        borderColor: "border-amber-200 dark:border-amber-800",
        iconColor: "text-amber-600 dark:text-amber-400",
        textColor: "text-amber-900 dark:text-amber-100",
    },
};

export function ReasoningStepDisplay({
    steps,
    defaultExpanded = false,
}: ReasoningStepDisplayProps) {
    const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);
    const [expandedSteps, setExpandedSteps] = React.useState<Set<number>>(
        new Set()
    );
    const [expandedDetails, setExpandedDetails] = React.useState<Set<number>>(
        new Set()
    );

    const toggleStep = (index: number) => {
        setExpandedSteps((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    const toggleDetails = (index: number) => {
        setExpandedDetails((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    if (!steps || steps.length === 0) return null;

    return (
        <div className="w-full">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
                {isExpanded ? (
                    <ChevronUp className="h-3 w-3" />
                ) : (
                    <ChevronDown className="h-3 w-3" />
                )}
                <Lightbulb className="h-3 w-3" />
                <span>{steps.length} 个推理步骤</span>
            </button>

            {isExpanded && (
                <div className="mt-2 space-y-2">
                    {steps.map((step, index) => {
                        const stepType = getStepType(step);
                        const config = stepConfig[stepType];
                        const StepIcon = config.icon;
                        const isStepExpanded = expandedSteps.has(index);
                        const isDetailsExpanded = expandedDetails.has(index);

                        // 处理思考内容
                        const thoughtContent = step.thought ? summarizeContent(step.thought) : null;
                        // 处理观察结果
                        const observationContent = step.observation ? summarizeContent(step.observation) : null;

                        return (
                            <Card
                                key={index}
                                className={`p-3 border ${config.borderColor} ${config.bgColor} transition-all duration-200`}
                            >
                                {/* 步骤头部 */}
                                <div className="flex items-start gap-3">
                                    <div
                                        className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${config.bgColor} border ${config.borderColor}`}
                                    >
                                        <StepIcon
                                            className={`w-3.5 h-3.5 ${config.iconColor}`}
                                        />
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        {/* 步骤标签和编号 */}
                                        <div className="flex items-center gap-2 mb-1">
                                            <span
                                                className={`text-xs font-semibold ${config.iconColor}`}
                                            >
                                                {config.label}
                                            </span>
                                            <span className="text-xs text-muted-foreground">
                                                #{index + 1}
                                            </span>
                                            {step.fallback_mode && (
                                                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800">
                                                    <AlertCircle className="w-3 h-3" />
                                                    降级模式
                                                </span>
                                            )}
                                        </div>

                                        {/* 思考内容（总结版） */}
                                        {thoughtContent && (
                                            <div className="space-y-2">
                                                <div
                                                    className={`text-sm ${config.textColor} leading-relaxed whitespace-pre-line`}
                                                >
                                                    {thoughtContent.summary}
                                                </div>

                                                {/* 查看详情按钮 */}
                                                {thoughtContent.hasDetails && (
                                                    <div>
                                                        <button
                                                            onClick={() => toggleDetails(index)}
                                                            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                                                        >
                                                            {isDetailsExpanded ? (
                                                                <ChevronUp className="h-3 w-3" />
                                                            ) : (
                                                                <ChevronDown className="h-3 w-3" />
                                                            )}
                                                            <FileText className="h-3 w-3" />
                                                            <span>
                                                                {isDetailsExpanded ? "收起详情" : "查看详情"}
                                                            </span>
                                                        </button>

                                                        {isDetailsExpanded && thoughtContent.details && (
                                                            <div className="mt-2 p-2 rounded bg-background/50 border border-border/30">
                                                                <div className="text-xs text-foreground/70 leading-relaxed whitespace-pre-line">
                                                                    {thoughtContent.details}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        {/* 工具信息 */}
                                        {step.toolName && (
                                            <div className="mt-2 space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs font-medium text-muted-foreground">
                                                        工具:
                                                    </span>
                                                    <code className="text-xs px-1.5 py-0.5 rounded bg-muted font-mono">
                                                        {step.toolName}
                                                    </code>
                                                </div>

                                                {/* 工具输入（可折叠） */}
                                                {step.toolInput &&
                                                    Object.keys(step.toolInput)
                                                        .length > 0 && (
                                                        <div>
                                                            <button
                                                                onClick={() =>
                                                                    toggleStep(
                                                                        index
                                                                    )
                                                                }
                                                                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                                                            >
                                                                {isStepExpanded ? (
                                                                    <ChevronUp className="h-3 w-3" />
                                                                ) : (
                                                                    <ChevronDown className="h-3 w-3" />
                                                                )}
                                                                <span>
                                                                    查看输入参数
                                                                </span>
                                                            </button>

                                                            {isStepExpanded && (
                                                                <div className="mt-1 p-2 rounded bg-muted/50 border border-border/50">
                                                                    <pre className="text-xs font-mono overflow-x-auto">
                                                                        {JSON.stringify(
                                                                            step.toolInput,
                                                                            null,
                                                                            2
                                                                        )}
                                                                    </pre>
                                                                </div>
                                                            )}
                                                        </div>
                                                    )}
                                            </div>
                                        )}

                                        {/* 观察结果（总结版） */}
                                        {observationContent && (
                                            <div className="mt-2 space-y-2">
                                                <div className="p-2 rounded bg-background/50 border border-border/30">
                                                    <div className="text-xs font-medium text-muted-foreground mb-1">
                                                        观察:
                                                    </div>
                                                    <div className="text-xs text-foreground/80 leading-relaxed whitespace-pre-line">
                                                        {observationContent.summary}
                                                    </div>
                                                </div>

                                                {/* 查看观察详情按钮 */}
                                                {observationContent.hasDetails && (
                                                    <div>
                                                        <button
                                                            onClick={() => toggleDetails(index + 1000)} // 使用不同的索引避免冲突
                                                            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
                                                        >
                                                            {expandedDetails.has(index + 1000) ? (
                                                                <ChevronUp className="h-3 w-3" />
                                                            ) : (
                                                                <ChevronDown className="h-3 w-3" />
                                                            )}
                                                            <FileText className="h-3 w-3" />
                                                            <span>
                                                                {expandedDetails.has(index + 1000) ? "收起完整观察" : "查看完整观察"}
                                                            </span>
                                                        </button>

                                                        {expandedDetails.has(index + 1000) && observationContent.details && (
                                                            <div className="mt-2 p-2 rounded bg-background/50 border border-border/30">
                                                                <div className="text-xs text-foreground/70 leading-relaxed whitespace-pre-line max-h-96 overflow-y-auto">
                                                                    {observationContent.details}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

