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

                                        {/* 思考内容 */}
                                        {step.thought && (
                                            <div
                                                className={`text-sm ${config.textColor} leading-relaxed`}
                                            >
                                                {step.thought}
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

                                        {/* 观察结果 */}
                                        {step.observation && (
                                            <div className="mt-2 p-2 rounded bg-background/50 border border-border/30">
                                                <div className="text-xs font-medium text-muted-foreground mb-1">
                                                    观察:
                                                </div>
                                                <div className="text-xs text-foreground/80 leading-relaxed">
                                                    {step.observation}
                                                </div>
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

