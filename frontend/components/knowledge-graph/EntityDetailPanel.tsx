"use client";

import { useState } from "react";
import { X, Network, Tag, TrendingUp, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { GraphNode } from "@/lib/api/knowledge-graph";

interface EntityDetailPanelProps {
    entity: GraphNode | null;
    onClose: () => void;
}

export function EntityDetailPanel({ entity, onClose }: EntityDetailPanelProps) {
    if (!entity) return null;

    const getTypeColor = (type: string) => {
        const colors: Record<string, string> = {
            steel_grade: "bg-primary/10 text-primary",
            steel_type: "bg-secondary/10 text-secondary",
            alloy_element: "bg-accent/10 text-accent",
            material_property: "bg-green-500/10 text-green-600",
            process: "bg-orange-500/10 text-orange-600",
            equipment: "bg-purple-500/10 text-purple-600",
            application: "bg-blue-500/10 text-blue-600",
            standard: "bg-yellow-500/10 text-yellow-600",
            company: "bg-pink-500/10 text-pink-600",
            product: "bg-cyan-500/10 text-cyan-600",
        };
        return colors[type] || "bg-muted text-muted-foreground";
    };

    return (
        <Card className="absolute top-0 right-0 w-96 h-full border-l shadow-lg z-10">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                <CardTitle className="text-lg font-semibold">实体详情</CardTitle>
                <Button variant="ghost" size="icon" onClick={onClose}>
                    <X className="h-4 w-4" />
                </Button>
            </CardHeader>
            <CardContent className="space-y-4">
                <ScrollArea className="h-[calc(100vh-180px)]">
                    {/* 实体名称 */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <Network className="h-5 w-5 text-primary" />
                            <h3 className="text-xl font-bold">{entity.label}</h3>
                        </div>
                        {entity.matched && (
                            <Badge variant="default" className="animate-pulse">
                                搜索匹配
                            </Badge>
                        )}
                    </div>

                    <Separator className="my-4" />

                    {/* 实体类型 */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <Tag className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium text-muted-foreground">类型</span>
                        </div>
                        <Badge className={getTypeColor(entity.type)} variant="secondary">
                            {entity.type}
                        </Badge>
                    </div>

                    {/* 描述 */}
                    {entity.description && (
                        <>
                            <Separator className="my-4" />
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <Info className="h-4 w-4 text-muted-foreground" />
                                    <span className="text-sm font-medium text-muted-foreground">
                                        描述
                                    </span>
                                </div>
                                <p className="text-sm text-foreground leading-relaxed">
                                    {entity.description}
                                </p>
                            </div>
                        </>
                    )}

                    {/* 置信度 */}
                    {entity.confidence !== undefined && (
                        <>
                            <Separator className="my-4" />
                            <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                                    <span className="text-sm font-medium text-muted-foreground">
                                        置信度
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="flex-1 bg-muted rounded-full h-2">
                                        <div
                                            className="bg-primary rounded-full h-2 transition-all"
                                            style={{ width: `${entity.confidence * 100}%` }}
                                        />
                                    </div>
                                    <span className="text-sm font-medium">
                                        {(entity.confidence * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        </>
                    )}

                    {/* 属性 */}
                    {entity.properties && Object.keys(entity.properties).length > 0 && (
                        <>
                            <Separator className="my-4" />
                            <div className="space-y-2">
                                <span className="text-sm font-medium text-muted-foreground">
                                    属性
                                </span>
                                <div className="space-y-2">
                                    {Object.entries(entity.properties).map(([key, value]) => (
                                        <div
                                            key={key}
                                            className="flex justify-between items-start gap-2 text-sm"
                                        >
                                            <span className="text-muted-foreground font-medium">
                                                {key}:
                                            </span>
                                            <span className="text-right text-foreground break-all">
                                                {typeof value === "object"
                                                    ? JSON.stringify(value, null, 2)
                                                    : String(value)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}
                </ScrollArea>
            </CardContent>
        </Card>
    );
}

