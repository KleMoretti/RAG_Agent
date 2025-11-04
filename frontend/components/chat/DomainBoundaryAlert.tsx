"use client";

import * as React from "react";
import { AlertTriangle, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MarkdownContent } from "./MarkdownContent";

interface DomainBoundaryAlertProps {
    content: string;
    suggestedAgent?: string;
    onSwitchAgent?: (agentId: string) => void;
}

/**
 * Agent 名称映射
 */
const AGENT_NAMES: Record<string, string> = {
    general: "通用助手",
    process: "工艺专家",
    equipment: "设备诊断",
    market: "市场分析师",
    quality: "质量顾问",
    environment: "节能专家",
};

export function DomainBoundaryAlert({
    content,
    suggestedAgent,
    onSwitchAgent,
}: DomainBoundaryAlertProps) {
    const agentName = suggestedAgent
        ? AGENT_NAMES[suggestedAgent] || suggestedAgent
        : null;

    return (
        <Card className="border-l-4 border-amber-500 bg-amber-50 dark:bg-amber-950/20 p-4 mt-2 max-w-full">
            <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-500 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0 space-y-3">
                    <div className="space-y-2">
                        <h4 className="font-semibold text-amber-900 dark:text-amber-100">
                            建议切换 Agent
                        </h4>
                        <div className="max-h-[300px] overflow-y-auto pr-2 [&_.prose]:text-amber-900 dark:[&_.prose]:text-amber-100">
                            <MarkdownContent
                                content={content}
                                className="text-amber-900 dark:text-amber-100 [&_strong]:font-bold [&_strong]:text-amber-950 dark:[&_strong]:text-amber-50"
                            />
                        </div>
                    </div>

                    {suggestedAgent && onSwitchAgent && (
                        <Button
                            onClick={() => onSwitchAgent(suggestedAgent)}
                            variant="outline"
                            size="sm"
                            className="border-amber-600 text-amber-900 hover:bg-amber-100 dark:text-amber-100 dark:hover:bg-amber-900/20"
                        >
                            <span>切换到 {agentName}</span>
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                    )}
                </div>
            </div>
        </Card>
    );
}

