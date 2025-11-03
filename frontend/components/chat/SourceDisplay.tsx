"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import {
    FileText,
    ChevronDown,
    ChevronUp,
    Star,
    Database,
} from "lucide-react";
import type { DocumentSource } from "@/lib/types/api";

interface SourceDisplayProps {
    sources: DocumentSource[];
    defaultExpanded?: boolean;
}

/**
 * 获取相关度等级
 */
const getRelevanceLevel = (score: number): "high" | "medium" | "low" => {
    if (score >= 0.8) return "high";
    if (score >= 0.6) return "medium";
    return "low";
};

/**
 * 相关度等级配置
 */
const relevanceConfig = {
    high: {
        label: "高度相关",
        color: "text-green-600 dark:text-green-400",
        bgColor: "bg-green-50 dark:bg-green-950/30",
        borderColor: "border-green-200 dark:border-green-800",
    },
    medium: {
        label: "中度相关",
        color: "text-yellow-600 dark:text-yellow-400",
        bgColor: "bg-yellow-50 dark:bg-yellow-950/30",
        borderColor: "border-yellow-200 dark:border-yellow-800",
    },
    low: {
        label: "低度相关",
        color: "text-gray-600 dark:text-gray-400",
        bgColor: "bg-gray-50 dark:bg-gray-950/30",
        borderColor: "border-gray-200 dark:border-gray-800",
    },
};

export function SourceDisplay({
    sources,
    defaultExpanded = false,
}: SourceDisplayProps) {
    const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);
    const [expandedSources, setExpandedSources] = React.useState<Set<number>>(
        new Set()
    );

    const toggleSource = (index: number) => {
        setExpandedSources((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(index)) {
                newSet.delete(index);
            } else {
                newSet.add(index);
            }
            return newSet;
        });
    };

    if (!sources || sources.length === 0) return null;

    // 按相关度排序
    const sortedSources = [...sources].sort((a, b) => {
        const scoreA = a.relevanceScore ?? 0;
        const scoreB = b.relevanceScore ?? 0;
        return scoreB - scoreA;
    });

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
                <Database className="h-3 w-3" />
                <span>{sources.length} 个参考来源</span>
            </button>

            {isExpanded && (
                <div className="mt-2 space-y-2">
                    {sortedSources.map((source, index) => {
                        const score = source.relevanceScore ?? 0;
                        const level = getRelevanceLevel(score);
                        const config = relevanceConfig[level];
                        const isSourceExpanded = expandedSources.has(index);

                        return (
                            <Card
                                key={index}
                                className={`p-3 border ${config.borderColor} ${config.bgColor} transition-all duration-200 hover:shadow-sm`}
                            >
                                <div className="flex items-start gap-3">
                                    {/* 文档图标 */}
                                    <div
                                        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${config.bgColor} border ${config.borderColor}`}
                                    >
                                        <FileText
                                            className={`w-4 h-4 ${config.color}`}
                                        />
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        {/* 文件名和相关度 */}
                                        <div className="flex items-center gap-2 mb-1.5">
                                            <span className="text-sm font-medium text-foreground truncate">
                                                {source.fileName}
                                            </span>
                                            {source.relevanceScore !==
                                                undefined && (
                                                <div className="flex items-center gap-1 flex-shrink-0">
                                                    <Star
                                                        className={`w-3 h-3 ${config.color}`}
                                                        fill="currentColor"
                                                    />
                                                    <span
                                                        className={`text-xs font-semibold ${config.color}`}
                                                    >
                                                        {(score * 100).toFixed(
                                                            1
                                                        )}
                                                        %
                                                    </span>
                                                </div>
                                            )}
                                        </div>

                                        {/* 相关度标签 */}
                                        {source.relevanceScore !== undefined && (
                                            <div className="mb-2">
                                                <span
                                                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.color} ${config.bgColor} border ${config.borderColor}`}
                                                >
                                                    {config.label}
                                                </span>
                                            </div>
                                        )}

                                        {/* 内容预览（可折叠） */}
                                        {source.content && (
                                            <div>
                                                <div
                                                    className={`text-xs text-muted-foreground ${
                                                        isSourceExpanded
                                                            ? ""
                                                            : "line-clamp-2"
                                                    } leading-relaxed mb-1`}
                                                >
                                                    {source.content}
                                                </div>

                                                {source.content.length > 100 && (
                                                    <button
                                                        onClick={() =>
                                                            toggleSource(index)
                                                        }
                                                        className="flex items-center gap-1 text-xs text-primary hover:text-primary/80 transition-colors"
                                                    >
                                                        {isSourceExpanded ? (
                                                            <>
                                                                <ChevronUp className="h-3 w-3" />
                                                                <span>
                                                                    收起
                                                                </span>
                                                            </>
                                                        ) : (
                                                            <>
                                                                <ChevronDown className="h-3 w-3" />
                                                                <span>
                                                                    查看更多
                                                                </span>
                                                            </>
                                                        )}
                                                    </button>
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

