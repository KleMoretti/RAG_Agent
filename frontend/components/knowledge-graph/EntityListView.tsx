"use client";

import { RefreshCw, Database, TrendingUp } from "lucide-react";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { Entity, KnowledgeGraphStats } from "@/lib/api/knowledge-graph";

interface EntityListViewProps {
    entities: Entity[];
    isLoading: boolean;
    stats?: KnowledgeGraphStats;
}

export function EntityListView({ entities, isLoading, stats }: EntityListViewProps) {
    if (isLoading) {
        return (
            <div className="text-center py-8">
                <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                <p className="text-muted-foreground">加载中...</p>
            </div>
        );
    }

    // 显示实体类型统计
    if (entities.length === 0 && stats) {
        return (
            <div className="space-y-6">
                <div>
                    <h3 className="text-lg font-semibold mb-4">实体类型分布</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(stats.entity_type_counts).map(([type, count]) => (
                            <div
                                key={type}
                                className="p-4 border rounded-lg hover:bg-accent transition-colors"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <Database className="h-4 w-4 text-muted-foreground" />
                                        <span className="font-medium">{type}</span>
                                    </div>
                                    <Badge variant="secondary">{count}</Badge>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div>
                    <h3 className="text-lg font-semibold mb-4">关系类型分布</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {Object.entries(stats.relation_type_counts).map(([type, count]) => (
                            <div
                                key={type}
                                className="p-4 border rounded-lg hover:bg-accent transition-colors"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <TrendingUp className="h-4 w-4 text-muted-foreground" />
                                        <span className="font-medium">{type}</span>
                                    </div>
                                    <Badge variant="secondary">{count}</Badge>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (entities.length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-muted-foreground">没有找到实体</p>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-4">
                <p className="text-sm text-muted-foreground">
                    共找到 {entities.length} 个实体
                </p>
            </div>
            <div className="border rounded-lg">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>实体名称</TableHead>
                            <TableHead>类型</TableHead>
                            <TableHead>描述</TableHead>
                            <TableHead>置信度</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {entities.map((entity) => (
                            <TableRow key={entity.id}>
                                <TableCell className="font-medium">{entity.name}</TableCell>
                                <TableCell>
                                    <Badge variant="outline">{entity.entity_type}</Badge>
                                </TableCell>
                                <TableCell className="max-w-md truncate">
                                    {entity.description || "-"}
                                </TableCell>
                                <TableCell>
                                    {entity.confidence
                                        ? `${(entity.confidence * 100).toFixed(1)}%`
                                        : "-"}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}

