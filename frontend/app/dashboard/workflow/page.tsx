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
import { NodeEditorDialog, type InsertPosition } from "@/components/workflow/NodeEditorDialog";
import {
    PROCESS_TEMPLATES,
    getDefaultTemplate,
    getTemplateById,
    type ProcessTemplate,
} from "@/lib/constants/steelProcessTemplates";
import type { ProcessNode, ProcessEdge } from "@/lib/types/workflow";
import {
    Factory,
    Workflow,
    ZoomIn,
    ZoomOut,
    Maximize,
    FileText,
    Settings,
    BarChart3,
    Leaf,
    Info,
    Edit3,
    Plus,
    Trash2,
    Save,
    RotateCcw,
    LayoutGrid,
} from "lucide-react";

export default function WorkflowPage() {
    const [selectedTemplate, setSelectedTemplate] = React.useState<ProcessTemplate>(
        getDefaultTemplate()
    );
    const [selectedNode, setSelectedNode] = React.useState<ProcessNode | null>(null);
    const [viewMode, setViewMode] = React.useState<"flow" | "list">("flow");
    const [zoom, setZoom] = React.useState(100);
    
    // 编辑模式状态
    const [isEditMode, setIsEditMode] = React.useState(false);
    const [customNodes, setCustomNodes] = React.useState<ProcessNode[]>([]);
    const [customEdges, setCustomEdges] = React.useState<ProcessEdge[]>([]);
    const [isEditorOpen, setIsEditorOpen] = React.useState(false);
    const [editorMode, setEditorMode] = React.useState<"add" | "edit">("add");
    const [editingNode, setEditingNode] = React.useState<ProcessNode | null>(null);
    
    // 当前显示的节点和连线（编辑模式使用自定义数据，否则使用模板数据）
    const currentNodes = isEditMode ? customNodes : selectedTemplate.nodes;
    const currentEdges = isEditMode ? customEdges : selectedTemplate.edges;

    // 处理工艺流程切换
    const handleTemplateChange = (templateId: string) => {
        const template = getTemplateById(templateId);
        if (template) {
            setSelectedTemplate(template);
            setSelectedNode(null); // 清除选中的节点
        }
    };

    // 处理节点选择
    const handleNodeSelect = (node: ProcessNode) => {
        setSelectedNode(node);
    };

    // 缩放控制
    const handleZoomIn = () => setZoom((prev) => Math.min(prev + 10, 150));
    const handleZoomOut = () => setZoom((prev) => Math.max(prev - 10, 50));
    const handleResetZoom = () => setZoom(100);

    // 进入编辑模式
    const handleEnterEditMode = () => {
        setCustomNodes([...selectedTemplate.nodes]);
        setCustomEdges([...selectedTemplate.edges]);
        setIsEditMode(true);
    };

    // 退出编辑模式
    const handleExitEditMode = () => {
        setIsEditMode(false);
        setSelectedNode(null);
    };

    // 重置编辑
    const handleResetEdit = () => {
        if (confirm("确定要放弃所有修改吗？")) {
            setCustomNodes([...selectedTemplate.nodes]);
            setCustomEdges([...selectedTemplate.edges]);
            setSelectedNode(null);
        }
    };

    // 保存编辑（这里可以扩展为保存到数据库）
    const handleSaveEdit = () => {
        alert(`已保存自定义工艺流程！\n节点数: ${customNodes.length}`);
        setIsEditMode(false);
    };

    // 添加节点
    const handleAddNode = () => {
        setEditorMode("add");
        setEditingNode(null);
        setIsEditorOpen(true);
    };

    // 编辑节点
    const handleEditNode = (node: ProcessNode) => {
        setEditorMode("edit");
        setEditingNode(node);
        setIsEditorOpen(true);
    };

    // 删除节点
    const handleDeleteNode = (nodeId: string) => {
        if (confirm("确定要删除该节点吗？")) {
            const remainingNodes = customNodes.filter((n) => n.id !== nodeId);
            const remainingEdges = customEdges.filter((e) => e.source !== nodeId && e.target !== nodeId);
            
            // 删除后自动刷新布局
            const layoutedNodes = autoLayoutNodes(remainingNodes, remainingEdges);
            setCustomNodes(layoutedNodes);
            setCustomEdges(remainingEdges);
            
            if (selectedNode?.id === nodeId) {
                setSelectedNode(null);
            }
        }
    };

    // 手动刷新布局
    const handleRefreshLayout = () => {
        const layoutedNodes = autoLayoutNodes(customNodes, customEdges);
        setCustomNodes(layoutedNodes);
    };

    // 自动布局算法：根据节点连接关系优化布局
    const autoLayoutNodes = (nodes: ProcessNode[], edges: ProcessEdge[]): ProcessNode[] => {
        if (nodes.length === 0) return nodes;

        // 1. 构建邻接表
        const adjacency = new Map<string, string[]>();
        const inDegree = new Map<string, number>();
        
        nodes.forEach((n) => {
            adjacency.set(n.id, []);
            inDegree.set(n.id, 0);
        });
        
        edges.forEach((e) => {
            adjacency.get(e.source)?.push(e.target);
            inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
        });

        // 2. 拓扑排序确定层级
        const levels = new Map<string, number>();
        const queue: string[] = [];
        
        // 找到所有入度为0的节点（起点）
        nodes.forEach((n) => {
            if (inDegree.get(n.id) === 0) {
                queue.push(n.id);
                levels.set(n.id, 0);
            }
        });

        // BFS遍历
        while (queue.length > 0) {
            const nodeId = queue.shift()!;
            const currentLevel = levels.get(nodeId) || 0;
            
            adjacency.get(nodeId)?.forEach((neighborId) => {
                const newInDegree = (inDegree.get(neighborId) || 0) - 1;
                inDegree.set(neighborId, newInDegree);
                
                const neighborLevel = levels.get(neighborId) || 0;
                levels.set(neighborId, Math.max(neighborLevel, currentLevel + 1));
                
                if (newInDegree === 0) {
                    queue.push(neighborId);
                }
            });
        }

        // 处理孤立节点（没有连线的节点）
        nodes.forEach((n) => {
            if (!levels.has(n.id)) {
                levels.set(n.id, 0);
            }
        });

        // 3. 按层级分组节点
        const nodesByLevel = new Map<number, ProcessNode[]>();
        nodes.forEach((n) => {
            const level = levels.get(n.id) || 0;
            if (!nodesByLevel.has(level)) {
                nodesByLevel.set(level, []);
            }
            nodesByLevel.get(level)!.push(n);
        });

        // 4. 计算每个节点的新坐标
        const HORIZONTAL_SPACING = 250; // 水平间距
        const VERTICAL_SPACING = 150;   // 垂直间距
        const START_X = 100;            // 起始X坐标
        const START_Y = 200;            // 起始Y坐标

        const layoutedNodes = nodes.map((node) => {
            const level = levels.get(node.id) || 0;
            const nodesInLevel = nodesByLevel.get(level) || [];
            const indexInLevel = nodesInLevel.findIndex((n) => n.id === node.id);
            
            // 垂直居中：根据该层级节点数量调整起始Y坐标
            const totalNodesInLevel = nodesInLevel.length;
            const centerOffset = ((totalNodesInLevel - 1) * VERTICAL_SPACING) / 2;
            
            return {
                ...node,
                position: {
                    x: START_X + level * HORIZONTAL_SPACING,
                    y: START_Y + indexInLevel * VERTICAL_SPACING - centerOffset,
                },
            };
        });

        return layoutedNodes;
    };

    // 保存节点（添加或编辑）
    const handleSaveNode = (node: ProcessNode, insertPosition?: InsertPosition) => {
        if (editorMode === "add" && insertPosition) {
            // 添加模式：根据插入位置计算坐标和创建连接
            let newNode = { ...node };
            let newEdges = [...customEdges];

            switch (insertPosition.type) {
                case "start": {
                    // 在开头插入：找到第一个节点
                    const firstNode = customNodes.reduce((first, curr) =>
                        curr.position.x < first.position.x ? curr : first
                    );
                    newNode.position = {
                        x: firstNode.position.x - 200,
                        y: firstNode.position.y,
                    };
                    // 创建新节点→第一个节点的连线
                    newEdges.push({
                        id: `edge-${newNode.id}-${firstNode.id}`,
                        source: newNode.id,
                        target: firstNode.id,
                    });
                    break;
                }
                case "end": {
                    // 在末尾插入：找到最后一个节点
                    const lastNode = customNodes.reduce((last, curr) =>
                        curr.position.x > last.position.x ? curr : last
                    );
                    newNode.position = {
                        x: lastNode.position.x + 200,
                        y: lastNode.position.y,
                    };
                    // 创建最后节点→新节点的连线
                    newEdges.push({
                        id: `edge-${lastNode.id}-${newNode.id}`,
                        source: lastNode.id,
                        target: newNode.id,
                    });
                    break;
                }
                case "before": {
                    // 在指定节点之前插入
                    const targetNode = customNodes.find((n) => n.id === insertPosition.targetNodeId);
                    if (targetNode) {
                        // 找到指向目标节点的前驱节点
                        const incomingEdge = customEdges.find((e) => e.target === targetNode.id);
                        const prevNode = incomingEdge
                            ? customNodes.find((n) => n.id === incomingEdge.source)
                            : null;

                        // 计算新节点位置（在前驱和目标之间）
                        if (prevNode && incomingEdge) {
                            newNode.position = {
                                x: (prevNode.position.x + targetNode.position.x) / 2,
                                y: (prevNode.position.y + targetNode.position.y) / 2,
                            };
                            // 删除原有连线
                            newEdges = newEdges.filter((e) => e.id !== incomingEdge.id);
                            // 添加 前驱→新节点 和 新节点→目标 的连线
                            newEdges.push({
                                id: `edge-${prevNode.id}-${newNode.id}`,
                                source: prevNode.id,
                                target: newNode.id,
                            });
                        } else {
                            // 目标节点没有前驱，放在它前面
                            newNode.position = {
                                x: targetNode.position.x - 200,
                                y: targetNode.position.y,
                            };
                        }
                        // 添加 新节点→目标 的连线
                        newEdges.push({
                            id: `edge-${newNode.id}-${targetNode.id}`,
                            source: newNode.id,
                            target: targetNode.id,
                        });
                    }
                    break;
                }
                case "after": {
                    // 在指定节点之后插入
                    const targetNode = customNodes.find((n) => n.id === insertPosition.targetNodeId);
                    if (targetNode) {
                        // 找到从目标节点出发的后继节点
                        const outgoingEdge = customEdges.find((e) => e.source === targetNode.id);
                        const nextNode = outgoingEdge
                            ? customNodes.find((n) => n.id === outgoingEdge.target)
                            : null;

                        // 计算新节点位置（在目标和后继之间）
                        if (nextNode && outgoingEdge) {
                            newNode.position = {
                                x: (targetNode.position.x + nextNode.position.x) / 2,
                                y: (targetNode.position.y + nextNode.position.y) / 2,
                            };
                            // 删除原有连线
                            newEdges = newEdges.filter((e) => e.id !== outgoingEdge.id);
                            // 添加 新节点→后继 的连线
                            newEdges.push({
                                id: `edge-${newNode.id}-${nextNode.id}`,
                                source: newNode.id,
                                target: nextNode.id,
                            });
                        } else {
                            // 目标节点没有后继，放在它后面
                            newNode.position = {
                                x: targetNode.position.x + 200,
                                y: targetNode.position.y,
                            };
                        }
                        // 添加 目标→新节点 的连线
                        newEdges.push({
                            id: `edge-${targetNode.id}-${newNode.id}`,
                            source: targetNode.id,
                            target: newNode.id,
                        });
                    }
                    break;
                }
            }

            // 添加新节点并自动刷新布局
            const updatedNodes = [...customNodes, newNode];
            const layoutedNodes = autoLayoutNodes(updatedNodes, newEdges);
            
            setCustomNodes(layoutedNodes);
            setCustomEdges(newEdges);
        } else {
            // 编辑模式：只更新节点信息
            setCustomNodes(customNodes.map((n) => (n.id === node.id ? node : n)));
            if (selectedNode?.id === node.id) {
                setSelectedNode(node);
            }
        }
    };

    // 统计数据（基于当前显示的节点）
    const stats = {
        totalNodes: currentNodes.length,
        processNodes: currentNodes.filter((n) => n.type === "process").length,
        equipmentNodes: currentNodes.filter((n) => n.type === "equipment").length,
        normalNodes: currentNodes.filter((n) => n.status === "normal").length,
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
                        {/* 工艺流程选择器（编辑模式下禁用） */}
                        <div className="min-w-[280px]">
                            <Select
                                value={selectedTemplate.id}
                                onValueChange={handleTemplateChange}
                                disabled={isEditMode}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="选择工艺流程" />
                                </SelectTrigger>
                                <SelectContent>
                                    {PROCESS_TEMPLATES.map((template) => (
                                        <SelectItem key={template.id} value={template.id}>
                                            {template.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {/* 编辑模式控制按钮 */}
                        {!isEditMode ? (
                            <Button variant="outline" size="sm" onClick={handleEnterEditMode}>
                                <Edit3 className="size-4 mr-1" />
                                编辑模式
                            </Button>
                        ) : (
                            <div className="flex gap-2">
                                <Button variant="outline" size="sm" onClick={handleResetEdit}>
                                    <RotateCcw className="size-4 mr-1" />
                                    重置
                                </Button>
                                <Button variant="default" size="sm" onClick={handleSaveEdit}>
                                    <Save className="size-4 mr-1" />
                                    保存
                                </Button>
                                <Button variant="ghost" size="sm" onClick={handleExitEditMode}>
                                    退出编辑
                                </Button>
                            </div>
                        )}

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
                            {!isEditMode && (
                                <Badge
                                    variant="secondary"
                                    className="gap-1"
                                    title={`吨钢碳排放：${selectedTemplate.co2Range.min}-${selectedTemplate.co2Range.max} t CO₂/t 钢`}
                                >
                                    <Leaf className="size-3" />
                                    {selectedTemplate.co2Range.min}-{selectedTemplate.co2Range.max} t CO₂
                                </Badge>
                            )}
                            {isEditMode && (
                                <Badge variant="default" className="gap-1 animate-pulse">
                                    <Edit3 className="size-3" />
                                    编辑中
                                </Badge>
                            )}
                        </div>
                    </div>
                </div>

                {/* 工艺流程描述 */}
                <div className="mt-3 flex items-start gap-2 p-3 bg-muted/50 rounded-lg">
                    <Info className="size-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                    <div className="space-y-1">
                        <p className="text-sm font-medium">{selectedTemplate.description}</p>
                        <p className="text-xs text-muted-foreground">
                            {selectedTemplate.applicability}
                        </p>
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
                                    <Select value={viewMode} onValueChange={(v: string) => setViewMode(v as "flow" | "list")}>
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

                                    {/* 编辑模式：添加节点和刷新布局按钮 */}
                                    {isEditMode && (
                                        <>
                                            <Button variant="default" size="sm" onClick={handleAddNode}>
                                                <Plus className="size-4 mr-1" />
                                                添加节点
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={handleRefreshLayout}
                                                title="自动优化布局"
                                            >
                                                <LayoutGrid className="size-4 mr-1" />
                                                刷新布局
                                            </Button>
                                        </>
                                    )}
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
                        <div className="flex-1 overflow-hidden">
                            {viewMode === "flow" ? (
                                <ProcessFlowChart
                                    nodes={currentNodes}
                                    edges={currentEdges}
                                    selectedNodeId={selectedNode?.id}
                                    onNodeSelect={handleNodeSelect}
                                    zoom={zoom}
                                />
                            ) : (
                                <Card className="h-full overflow-auto">
                                    <CardContent className="p-4 space-y-2">
                                        {currentNodes.map((node) => (
                                            <div key={node.id} className="flex items-center gap-2">
                                                <Button
                                                    variant={
                                                        selectedNode?.id === node.id ? "default" : "outline"
                                                    }
                                                    className="flex-1 justify-start gap-2 h-auto py-3"
                                                    onClick={() => handleNodeSelect(node)}
                                                >
                                                    <div className="flex flex-col items-start gap-1 flex-1">
                                                        <span className="font-medium">{node.name}</span>
                                                        <span className="text-xs opacity-70">
                                                            {node.description}
                                                        </span>
                                                    </div>
                                                </Button>
                                                {isEditMode && (
                                                    <div className="flex gap-1">
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            onClick={() => handleEditNode(node)}
                                                        >
                                                            <Edit3 className="size-4" />
                                                        </Button>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            onClick={() => handleDeleteNode(node.id)}
                                                        >
                                                            <Trash2 className="size-4 text-destructive" />
                                                        </Button>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                    </div>

                    {/* 右侧：详情面板 */}
                    <div className="col-span-4 overflow-hidden">
                        {selectedNode ? (
                            <div className="h-full flex flex-col gap-2">
                                {isEditMode && (
                                    <Card className="flex-shrink-0">
                                        <CardContent className="p-3 flex gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="flex-1"
                                                onClick={() => handleEditNode(selectedNode)}
                                            >
                                                <Edit3 className="size-4 mr-1" />
                                                编辑节点
                                            </Button>
                                            <Button
                                                variant="destructive"
                                                size="sm"
                                                className="flex-1"
                                                onClick={() => handleDeleteNode(selectedNode.id)}
                                            >
                                                <Trash2 className="size-4 mr-1" />
                                                删除节点
                                            </Button>
                                        </CardContent>
                                    </Card>
                                )}
                                <div className="flex-1 overflow-hidden">
                                    <NodeDetailPanel
                                        node={selectedNode}
                                        onClose={() => setSelectedNode(null)}
                                    />
                                </div>
                            </div>
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

            {/* 节点编辑对话框 */}
            <NodeEditorDialog
                open={isEditorOpen}
                onOpenChange={setIsEditorOpen}
                node={editingNode}
                onSave={handleSaveNode}
                mode={editorMode}
                existingNodes={customNodes}
            />
        </div>
    );
}

