"use client";

import { useEffect, useRef, useState } from "react";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { Entity } from "@/lib/api/knowledge-graph";

interface KnowledgeGraphVisualizationProps {
    searchResults: Entity[];
    isSearching: boolean;
}

export function KnowledgeGraphVisualization({
    searchResults,
    isSearching,
}: KnowledgeGraphVisualizationProps) {
    const canvasRef = useRef<HTMLDivElement>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!canvasRef.current || searchResults.length === 0) return;

        try {
            // TODO: 集成 D3.js 或 Cytoscape.js 进行图谱可视化
            // 这里先显示简单的占位符
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "渲染图谱时出错");
        }
    }, [searchResults]);

    if (isSearching) {
        return (
            <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4" />
                    <p className="text-muted-foreground">搜索中...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        );
    }

    if (searchResults.length === 0) {
        return (
            <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">
                        请在上方搜索框中输入关键词查看知识图谱
                    </p>
                </div>
            </div>
        );
    }

    // 简单的节点展示（临时实现）
    return (
        <div className="h-[600px] overflow-auto" ref={canvasRef}>
            <div className="p-4">
                <Alert className="mb-4">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        图谱可视化功能正在开发中。当前显示搜索结果列表。
                    </AlertDescription>
                </Alert>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {searchResults.map((entity) => (
                        <div
                            key={entity.id}
                            className="p-4 border rounded-lg hover:bg-accent transition-colors"
                        >
                            <div className="flex items-start justify-between mb-2">
                                <h3 className="font-semibold">{entity.name}</h3>
                                <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                                    {entity.entity_type}
                                </span>
                            </div>
                            {entity.description && (
                                <p className="text-sm text-muted-foreground">
                                    {entity.description}
                                </p>
                            )}
                            {entity.confidence && (
                                <div className="mt-2 text-xs text-muted-foreground">
                                    置信度: {(entity.confidence * 100).toFixed(1)}%
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

