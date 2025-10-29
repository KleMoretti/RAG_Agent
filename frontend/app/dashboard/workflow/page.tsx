"use client";

import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { ProcessFlowChart } from "@/components/workflow/ProcessFlowChart";
import { NodeDetailPanel } from "@/components/workflow/NodeDetailPanel";
import {
    STEEL_PROCESS_NODES,
    STEEL_PROCESS_EDGES,
} from "@/lib/constants/processData";
import type { ProcessNode } from "@/lib/types/workflow";
import {
    Factory,
    Workflow,
    ZoomIn,
    ZoomOut,
    Maximize,
    FileText,
    Settings,
    BarChart3,
} from "lucide-react";

export default function WorkflowPage() {
    const [selectedNode, setSelectedNode] = React.useState<ProcessNode | null>(null);
    const [viewMode, setViewMode] = React.useState<"flow" | "list">("flow");
    const [zoom, setZoom] = React.useState(100);

    // 处理节点选择
    const handleNodeSelect = (node: ProcessNode) => {
        setSelectedNode(node);
    };

    // 缩放控制
    const handleZoomIn = () => setZoom((prev) => Math.min(prev + 10, 150));
    const handleZoomOut = () => setZoom((prev) => Math.max(prev - 10, 50));
    const handleResetZoom = () => setZoom(100);

    // 统计数据
    const stats = {
        totalNodes: STEEL_PROCESS_NODES.length,
        processNodes: STEEL_PROCESS_NODES.filter((n) => n.type === "process").length,
        equipmentNodes: STEEL_PROCESS_NODES.filter((n) => n.type === "equipment").length,
        normalNodes: STEEL_PROCESS_NODES.filter((n) => n.status === "normal").length,
    };

    return (
        <div className="flex flex-col h-screen">
            {/* 页面头部 */}
            <div className="flex-shrink-0 border-b bg-background px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            <Factory className="size-6 text-primary" />
                            <h1 className="text-2xl font-bold">工艺流程管理</h1>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            钢铁生产全流程可视化与智能分析
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* 统计信息 */}
                        <div className="flex gap-2">
                            <Badge variant="outline" className="gap-1">
                                <Workflow className="size-3" />
                                {stats.totalNodes} 个节点
                            </Badge>
                            <Badge variant="outline" className="gap-1">
                                <Settings className="size-3" />
                                {stats.equipmentNodes} 台设备
                            </Badge>
                            <Badge variant="default" className="gap-1">
                                ✓ {stats.normalNodes} 正常运行
                            </Badge>
                        </div>
                    </div>
                </div>
            </div>

            {/* 主内容区 */}
            <div className="flex-1 overflow-hidden">
                <div className="grid grid-cols-12 gap-4 h-full p-6">
                    {/* 左侧：工艺流程图 */}
                    <div className="col-span-8 flex flex-col gap-4 overflow-hidden">
                        {/* 工具栏 */}
                        <Card className="flex-shrink-0">
                            <CardContent className="p-3 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Select value={viewMode} onValueChange={(v: any) => setViewMode(v)}>
                                        <SelectTrigger className="w-32">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="flow">流程视图</SelectItem>
                                            <SelectItem value="list">列表视图</SelectItem>
                                        </SelectContent>
                                    </Select>

                                    <div className="flex items-center gap-1 border rounded-md">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={handleZoomOut}
                                            disabled={zoom <= 50}
                                        >
                                            <ZoomOut className="size-4" />
                                        </Button>
                                        <span className="text-xs px-2 min-w-[50px] text-center">
                                            {zoom}%
                                        </span>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={handleZoomIn}
                                            disabled={zoom >= 150}
                                        >
                                            <ZoomIn className="size-4" />
                                        </Button>
                                    </div>

                                    <Button variant="ghost" size="sm" onClick={handleResetZoom}>
                                        <Maximize className="size-4" />
                                    </Button>
                                </div>

                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                        <div className="size-3 rounded-full bg-blue-500" />
                                        工艺流程
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <div className="size-3 rounded-full bg-purple-500" />
                                        设备
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <div className="size-3 rounded-full bg-green-500" />
                                        检验点
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <div className="size-3 rounded-full bg-amber-500" />
                                        物料
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* 流程图 */}
                        <div
                            className="flex-1 overflow-hidden"
                            style={{ transform: `scale(${zoom / 100})`, transformOrigin: "top left" }}
                        >
                            {viewMode === "flow" ? (
                                <ProcessFlowChart
                                    nodes={STEEL_PROCESS_NODES}
                                    edges={STEEL_PROCESS_EDGES}
                                    selectedNodeId={selectedNode?.id}
                                    onNodeSelect={handleNodeSelect}
                                />
                            ) : (
                                <Card className="h-full overflow-auto">
                                    <CardContent className="p-4 space-y-2">
                                        {STEEL_PROCESS_NODES.map((node) => (
                                            <Button
                                                key={node.id}
                                                variant={
                                                    selectedNode?.id === node.id ? "default" : "outline"
                                                }
                                                className="w-full justify-start gap-2 h-auto py-3"
                                                onClick={() => handleNodeSelect(node)}
                                            >
                                                <div className="flex flex-col items-start gap-1 flex-1">
                                                    <span className="font-medium">{node.name}</span>
                                                    <span className="text-xs opacity-70">
                                                        {node.description}
                                                    </span>
                                                </div>
                                            </Button>
                                        ))}
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                    </div>

                    {/* 右侧：详情面板 */}
                    <div className="col-span-4 overflow-hidden">
                        {selectedNode ? (
                            <NodeDetailPanel
                                node={selectedNode}
                                onClose={() => setSelectedNode(null)}
                            />
                        ) : (
                            <Card className="h-full flex flex-col items-center justify-center text-center p-6">
                                <Workflow className="size-16 text-muted-foreground mb-4" />
                                <h3 className="font-semibold text-lg mb-2">选择工艺节点</h3>
                                <p className="text-sm text-muted-foreground mb-4">
                                    点击左侧流程图中的任意节点查看详细信息
                                </p>
                                <div className="space-y-2 w-full">
                                    <Button variant="outline" className="w-full gap-2" disabled>
                                        <FileText className="size-4" />
                                        查看工艺文档（开发中）
                                    </Button>
                                    <Button variant="outline" className="w-full gap-2" disabled>
                                        <BarChart3 className="size-4" />
                                        查看数据分析（开发中）
                                    </Button>
                                </div>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

