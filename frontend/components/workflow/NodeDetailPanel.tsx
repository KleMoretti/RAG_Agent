"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { ProcessNode, ProcessParameter } from "@/lib/types/workflow";
import {
    TrendingUp,
    TrendingDown,
    Minus,
    BookOpen,
    X,
} from "lucide-react";

interface NodeDetailPanelProps {
    node: ProcessNode | null;
    onClose: () => void;
}

export function NodeDetailPanel({ node, onClose }: NodeDetailPanelProps) {
    if (!node) return null;

    // 参数状态图标
    const getParamStatusIcon = (param: ProcessParameter) => {
        if (!param.actualValue || !param.range) return <Minus className="size-4 text-muted-foreground" />;
        
        const actual = typeof param.actualValue === 'string' ? parseFloat(param.actualValue) : param.actualValue;
        if (actual > param.range.max) return <TrendingUp className="size-4 text-red-500" />;
        if (actual < param.range.min) return <TrendingDown className="size-4 text-yellow-500" />;
        return <Minus className="size-4 text-green-500" />;
    };

    return (
        <Card className="h-full flex flex-col shadow-lg border-2">
            <CardHeader className="flex-shrink-0">
                <div className="flex items-start justify-between">
                    <div className="space-y-1 flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <CardTitle className="text-xl truncate">{node.name}</CardTitle>
                            {node.status && (
                                <Badge
                                    variant={
                                        node.status === "normal"
                                            ? "default"
                                            : node.status === "error"
                                              ? "destructive"
                                              : "secondary"
                                    }
                                >
                                    {node.status === "normal"
                                        ? "正常"
                                        : node.status === "warning"
                                          ? "预警"
                                          : node.status === "error"
                                            ? "异常"
                                            : "优化中"}
                                </Badge>
                            )}
                        </div>
                        <CardDescription>{node.description}</CardDescription>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="flex-shrink-0"
                        onClick={onClose}
                    >
                        <X className="size-4" />
                    </Button>
                </div>
            </CardHeader>

            <Separator />

            <ScrollArea className="flex-1">
                <CardContent className="space-y-6 p-6">
                    {/* 工艺参数 */}
                    {node.parameters && node.parameters.length > 0 && (
                        <div className="space-y-3">
                            <h3 className="font-semibold text-sm flex items-center gap-2">
                                <div className="size-2 rounded-full bg-primary" />
                                工艺参数
                            </h3>
                            <div className="space-y-2">
                                {node.parameters.map((param, idx) => (
                                    <Card key={idx} className="p-3">
                                        <div className="flex items-start justify-between gap-2">
                                            <div className="flex-1 min-w-0 space-y-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-medium text-sm">
                                                        {param.name}
                                                    </span>
                                                    {getParamStatusIcon(param)}
                                                </div>
                                                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                                    <span>
                                                        标准值: {param.standardValue} {param.unit}
                                                    </span>
                                                    {param.actualValue && (
                                                        <>
                                                            <span>•</span>
                                                            <span
                                                                className={cn(
                                                                    param.isOutOfRange &&
                                                                        "text-destructive font-medium",
                                                                )}
                                                            >
                                                                实际值: {param.actualValue} {param.unit}
                                                            </span>
                                                        </>
                                                    )}
                                                </div>
                                                {param.range && (
                                                    <div className="text-xs text-muted-foreground">
                                                        范围: {param.range.min} - {param.range.max} {param.unit}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 关联文档 */}
                    {node.relatedDocs && node.relatedDocs.length > 0 && (
                        <div className="space-y-3">
                            <h3 className="font-semibold text-sm flex items-center gap-2">
                                <div className="size-2 rounded-full bg-primary" />
                                关联文档
                            </h3>
                            <div className="space-y-2">
                                {node.relatedDocs.map((docId, idx) => (
                                    <Button
                                        key={idx}
                                        variant="outline"
                                        className="w-full justify-start gap-2"
                                        size="sm"
                                        disabled
                                    >
                                        <BookOpen className="size-4" />
                                        <span className="truncate">文档 {docId}（开发中）</span>
                                    </Button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 节点类型标签 */}
                    <div className="flex flex-wrap gap-2 pt-4 border-t">
                        <Badge variant="outline">
                            类型:{" "}
                            {node.type === "process"
                                ? "工艺流程"
                                : node.type === "equipment"
                                  ? "设备"
                                  : node.type === "inspection"
                                    ? "检验点"
                                    : "物料"}
                        </Badge>
                        {node.parameters && (
                            <Badge variant="outline">
                                {node.parameters.length} 个参数
                            </Badge>
                        )}
                    </div>
                </CardContent>
            </ScrollArea>
        </Card>
    );
}

