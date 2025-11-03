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
import { toast } from "sonner";
import {
    createWorkflow,
    listWorkflows,
    updateWorkflow,
    getWorkflow,
    type WorkflowResponse,
} from "@/lib/api/workflow";

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
    
    // 为每个模板维护独立的 savedWorkflowId（templateId -> workflowId 映射）
    const [savedWorkflowMap, setSavedWorkflowMap] = React.useState<Record<string, number>>(() => {
        if (typeof window !== "undefined") {
            const saved = localStorage.getItem("workflow_saved_map");
            
            // 清理旧版本的单个 workflow_saved_id（迁移到新的 map 结构）
            const oldSavedId = localStorage.getItem("workflow_saved_id");
            if (oldSavedId && !saved) {
                localStorage.removeItem("workflow_saved_id");
                console.log("🔄 已迁移旧版本的 workflow_saved_id 到新的 map 结构");
            }
            
            return saved ? JSON.parse(saved) : {};
        }
        return {};
    });
    
    const [isSaving, setIsSaving] = React.useState(false); // 保存中状态
    const [hasUnsavedChanges, setHasUnsavedChanges] = React.useState(false); // 是否有未保存的更改
    
    // 获取当前模板的 savedWorkflowId
    const savedWorkflowId = savedWorkflowMap[selectedTemplate.id] || null;
    
    // 持久化 savedWorkflowMap 到 localStorage
    React.useEffect(() => {
        if (typeof window !== "undefined") {
            localStorage.setItem("workflow_saved_map", JSON.stringify(savedWorkflowMap));
            
            // 调试信息：显示所有模板的保存状态
            const savedCount = Object.keys(savedWorkflowMap).length;
            if (savedCount > 0) {
                console.log(`📊 已保存 ${savedCount} 个模板的自定义流程:`, savedWorkflowMap);
            }
        }
    }, [savedWorkflowMap]);

    // 切换模板或页面加载时，自动加载该模板的已保存流程
    React.useEffect(() => {
        const templateWorkflowId = savedWorkflowMap[selectedTemplate.id];
        
        if (templateWorkflowId) {
            // 该模板有已保存的流程，从数据库加载
            const loadSavedWorkflow = async () => {
                try {
                    const workflow = await getWorkflow(templateWorkflowId);
                    setCustomNodes(workflow.nodes);
                    setCustomEdges(workflow.edges);
                    console.log(`✅ 已加载模板「${selectedTemplate.name}」的自定义流程 ID:${templateWorkflowId}`, {
                        nodes: workflow.nodes.length,
                        edges: workflow.edges.length,
                    });
                } catch (error) {
                    console.error("加载保存的工艺流程失败:", error);
                    // 如果加载失败，从 map 中移除该条目
                    setSavedWorkflowMap((prev) => {
                        const newMap = { ...prev };
                        delete newMap[selectedTemplate.id];
                        return newMap;
                    });
                    setCustomNodes([]);
                    setCustomEdges([]);
                    toast.error("加载自定义流程失败，已切换到模板视图");
                }
            };
            loadSavedWorkflow();
        } else {
            // 该模板没有已保存的流程，清空自定义数据
            setCustomNodes([]);
            setCustomEdges([]);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedTemplate.id]); // 当模板切换时执行
    
    // 当前显示的节点和连线
    // 优先级：1. 编辑模式显示 customNodes  2. 已保存的流程显示 customNodes  3. 否则显示模板数据
    const currentNodes = (isEditMode || savedWorkflowId) ? customNodes : selectedTemplate.nodes;
    const currentEdges = (isEditMode || savedWorkflowId) ? customEdges : selectedTemplate.edges;

    // 处理工艺流程切换
    const handleTemplateChange = (templateId: string) => {
        const template = getTemplateById(templateId);
        if (template) {
            // 如果正在编辑且有未保存的更改，提示用户
            if (isEditMode && hasUnsavedChanges) {
                if (!confirm("当前有未保存的更改，切换模板将丢失这些更改，是否继续？")) {
                    return; // 用户取消
                }
            }

            setSelectedTemplate(template);
            setSelectedNode(null);
            setIsEditMode(false);
            setHasUnsavedChanges(false);
            toast.info(`已切换到「${template.name}」模板`);
            
            // 自动加载该模板的已保存流程（在 useEffect 中处理）
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

    // 进入编辑模式（加载已保存的版本或模板数据）
    const handleEnterEditMode = async () => {
        // 如果有已保存的工艺流程，尝试加载它
        if (savedWorkflowId) {
            try {
                const workflow = await getWorkflow(savedWorkflowId);
                setCustomNodes(workflow.nodes);
                setCustomEdges(workflow.edges);
                toast.info("已加载保存的工艺流程");
            } catch (error) {
                console.error("加载保存的工艺流程失败:", error);
                toast.warning("无法加载保存的版本，使用模板数据");
                setCustomNodes([...selectedTemplate.nodes]);
                setCustomEdges([...selectedTemplate.edges]);
                // 从 map 中移除当前模板的无效 ID
                setSavedWorkflowMap((prev) => {
                    const newMap = { ...prev };
                    delete newMap[selectedTemplate.id];
                    return newMap;
                });
            }
        } else {
            // 没有保存的版本，使用模板数据
            setCustomNodes([...selectedTemplate.nodes]);
            setCustomEdges([...selectedTemplate.edges]);
        }
        setIsEditMode(true);
    };

    // 退出编辑模式
    const handleExitEditMode = () => {
        // 检查是否有未保存的更改
        if (hasUnsavedChanges) {
            if (!confirm("您有未保存的更改，确定要退出编辑模式吗？")) {
                return;
            }
        }
        setIsEditMode(false);
        setSelectedNode(null);
        setHasUnsavedChanges(false);
    };

    // 重置编辑
    const handleResetEdit = () => {
        if (confirm("确定要放弃所有修改吗？")) {
            setCustomNodes([...selectedTemplate.nodes]);
            setCustomEdges([...selectedTemplate.edges]);
            setSelectedNode(null);
            setHasUnsavedChanges(false);
            toast.info("已重置为模板数据");
        }
    };

    // 保存编辑到数据库
    const handleSaveEdit = async () => {
        if (customNodes.length === 0) {
            toast.error("工艺流程不能为空");
            return;
        }

        setIsSaving(true);
        try {
            const workflowName = `${selectedTemplate.name} (自定义)`;
            const workflowData = {
                name: workflowName,
                description: `基于 ${selectedTemplate.name} 创建的自定义工艺流程`,
                template_id: selectedTemplate.id,
                nodes: customNodes,
                edges: customEdges,
                workflow_metadata: {
                    original_template: selectedTemplate.id,
                    co2_range: selectedTemplate.co2Range,
                    modified_at: new Date().toISOString(),
                    node_count: customNodes.length,
                    edge_count: customEdges.length,
                },
            };

            if (savedWorkflowId) {
                // 更新已保存的工艺流程（包含新增/删除的节点）
                await updateWorkflow(savedWorkflowId, {
                    nodes: customNodes,
                    edges: customEdges,
                    workflow_metadata: workflowData.workflow_metadata,
                });
                toast.success(`✅ 工艺流程已更新！（${customNodes.length} 个节点）`);
                console.log(`✅ 已更新工艺流程 ID:${savedWorkflowId} (模板: ${selectedTemplate.id})`, {
                    nodes: customNodes.length,
                    edges: customEdges.length,
                });
            } else {
                // 创建新的工艺流程
                const result = await createWorkflow(workflowData);
                
                // 将新创建的 workflowId 保存到对应模板的映射中
                setSavedWorkflowMap((prev) => ({
                    ...prev,
                    [selectedTemplate.id]: result.id,
                }));
                
                toast.success(`✅ 工艺流程已保存！（ID: ${result.id}，可继续编辑）`);
                console.log(`✅ 已创建工艺流程 ID:${result.id} (模板: ${selectedTemplate.id})`, {
                    nodes: customNodes.length,
                    edges: customEdges.length,
                });
            }

            // 清除未保存标记，但保持在编辑模式
            setHasUnsavedChanges(false);
            // ✅ 不退出编辑模式，用户可以立即看到新节点并继续编辑
        } catch (error: any) {
            console.error("❌ 保存工艺流程失败:", error);
            toast.error(error.response?.data?.detail || "保存失败，请重试");
        } finally {
            setIsSaving(false);
        }
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
        const nodeToDelete = customNodes.find((n) => n.id === nodeId);
        if (!nodeToDelete) return;

        if (confirm(`确定要删除节点「${nodeToDelete.name}」吗？\n\n✅ 将自动重新连接前后节点`)) {
            // 1. 找到所有指向该节点的前驱节点（入边）
            const incomingEdges = customEdges.filter((e) => e.target === nodeId);
            const predecessors = incomingEdges.map((e) => e.source);
            
            // 2. 找到所有从该节点出发的后继节点（出边）
            const outgoingEdges = customEdges.filter((e) => e.source === nodeId);
            const successors = outgoingEdges.map((e) => e.target);
            
            // 3. 删除节点和所有相关连线
            const remainingNodes = customNodes.filter((n) => n.id !== nodeId);
            let remainingEdges = customEdges.filter((e) => e.source !== nodeId && e.target !== nodeId);
            
            // 4. 为每个前驱节点创建到每个后继节点的新连线（自动桥接）
            if (predecessors.length > 0 && successors.length > 0) {
                predecessors.forEach((pred) => {
                    successors.forEach((succ) => {
                        // 检查是否已存在该连线（避免重复）
                        const edgeExists = remainingEdges.some(
                            (e) => e.source === pred && e.target === succ
                        );
                        if (!edgeExists) {
                            remainingEdges.push({
                                id: `edge-${pred}-${succ}`,
                                source: pred,
                                target: succ,
                            });
                        }
                    });
                });
                console.log(`🔗 自动桥接: ${predecessors.length} 个前驱节点 → ${successors.length} 个后继节点`);
            }
            
            // 5. 删除后自动刷新布局
            const layoutedNodes = autoLayoutNodes(remainingNodes, remainingEdges);
            setCustomNodes(layoutedNodes);
            setCustomEdges(remainingEdges);
            
            if (selectedNode?.id === nodeId) {
                setSelectedNode(null);
            }

            // 标记有未保存的更改
            setHasUnsavedChanges(true);
            toast.success(`🗑️ 已删除节点「${nodeToDelete.name}」并自动重新连接前后节点`);
            console.log(`🗑️ 删除节点: ${nodeToDelete.name} (${nodeId})`, {
                predecessors,
                successors,
                newEdges: remainingEdges.length - customEdges.length + incomingEdges.length + outgoingEdges.length,
            });
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
            // 添加模式：根据插入位置创建连线关系，然后自动重排布局
            const newNode = { ...node, position: { x: 0, y: 0 } }; // 临时坐标，将由 autoLayoutNodes 重新计算
            let newEdges = [...customEdges];

            switch (insertPosition.type) {
                case "start": {
                    // 在开头插入：新节点作为起点
                    // 找到当前的第一个节点（入度为0的节点）
                    const startNodes = customNodes.filter(
                        (n) => !customEdges.some((e) => e.target === n.id)
                    );
                    // 创建新节点→所有起点节点的连线
                    startNodes.forEach((startNode) => {
                        newEdges.push({
                            id: `edge-${newNode.id}-${startNode.id}`,
                            source: newNode.id,
                            target: startNode.id,
                        });
                    });
                    break;
                }
                case "end": {
                    // 在末尾插入：新节点作为终点
                    // 找到当前的最后节点（出度为0的节点）
                    const endNodes = customNodes.filter(
                        (n) => !customEdges.some((e) => e.source === n.id)
                    );
                    // 创建所有终点节点→新节点的连线
                    endNodes.forEach((endNode) => {
                        newEdges.push({
                            id: `edge-${endNode.id}-${newNode.id}`,
                            source: endNode.id,
                            target: newNode.id,
                        });
                    });
                    break;
                }
                case "before": {
                    // 在指定节点之前插入
                    const targetNode = customNodes.find((n) => n.id === insertPosition.targetNodeId);
                    if (targetNode) {
                        // 找到所有指向目标节点的前驱节点
                        const incomingEdges = customEdges.filter((e) => e.target === targetNode.id);
                        
                        if (incomingEdges.length > 0) {
                            // 删除所有指向目标节点的连线
                            newEdges = newEdges.filter((e) => e.target !== targetNode.id);
                            
                            // 创建前驱节点→新节点的连线
                            incomingEdges.forEach((edge) => {
                                newEdges.push({
                                    id: `edge-${edge.source}-${newNode.id}`,
                                    source: edge.source,
                                    target: newNode.id,
                                });
                            });
                        }
                        
                        // 创建新节点→目标节点的连线
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
                        // 找到所有从目标节点出发的后继节点
                        const outgoingEdges = customEdges.filter((e) => e.source === targetNode.id);
                        
                        if (outgoingEdges.length > 0) {
                            // 删除所有从目标节点出发的连线
                            newEdges = newEdges.filter((e) => e.source !== targetNode.id);
                            
                            // 创建新节点→后继节点的连线
                            outgoingEdges.forEach((edge) => {
                                newEdges.push({
                                    id: `edge-${newNode.id}-${edge.target}`,
                                    source: newNode.id,
                                    target: edge.target,
                                });
                            });
                        }
                        
                        // 创建目标节点→新节点的连线
                        newEdges.push({
                            id: `edge-${targetNode.id}-${newNode.id}`,
                            source: targetNode.id,
                            target: newNode.id,
                        });
                    }
                    break;
                }
            }

            // 添加新节点到列表，然后自动重排整个流程图
            const updatedNodes = [...customNodes, newNode];
            const layoutedNodes = autoLayoutNodes(updatedNodes, newEdges);
            
            setCustomNodes(layoutedNodes);
            setCustomEdges(newEdges);

            // 标记有未保存的更改
            setHasUnsavedChanges(true);
            toast.success(`➕ 已添加节点「${node.name}」（未保存到数据库）`);
            console.log(`➕ 添加节点: ${node.name} (${node.id})`, { insertPosition });
        } else {
            // 编辑模式：只更新节点信息，不重排布局
            setCustomNodes(customNodes.map((n) => (n.id === node.id ? node : n)));
            if (selectedNode?.id === node.id) {
                setSelectedNode(node);
            }

            // 标记有未保存的更改
            setHasUnsavedChanges(true);
            toast.success(`✏️ 已修改节点「${node.name}」（未保存到数据库）`);
            console.log(`✏️ 编辑节点: ${node.name} (${node.id})`);
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
                        {!isEditMode && !savedWorkflowId && (
                            <Button variant="outline" size="sm" onClick={handleEnterEditMode}>
                                <Edit3 className="size-4 mr-1" />
                                编辑模式
                            </Button>
                        )}
                        {!isEditMode && savedWorkflowId && (
                            <>
                                <Button variant="outline" size="sm" onClick={handleEnterEditMode}>
                                    <Edit3 className="size-4 mr-1" />
                                    继续编辑
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        if (confirm("确定要清除当前模板的自定义流程并回到模板视图吗？\n\n⚠️ 其他模板的自定义流程不会受影响")) {
                                            // 从 map 中移除当前模板的 workflowId
                                            setSavedWorkflowMap((prev) => {
                                                const newMap = { ...prev };
                                                delete newMap[selectedTemplate.id];
                                                return newMap;
                                            });
                                            setCustomNodes([]);
                                            setCustomEdges([]);
                                            toast.info("已切换到模板视图");
                                        }
                                    }}
                                >
                                    <RotateCcw className="size-4 mr-1" />
                                    回到模板
                                </Button>
                            </>
                        )}
                        {isEditMode && (
                            <div className="flex gap-2">
                                <Button variant="outline" size="sm" onClick={handleResetEdit}>
                                    <RotateCcw className="size-4 mr-1" />
                                    重置
                                </Button>
                                <Button
                                    variant="default"
                                    size="sm"
                                    onClick={handleSaveEdit}
                                    disabled={isSaving}
                                >
                                    <Save className="size-4 mr-1" />
                                    {isSaving
                                        ? "保存中..."
                                        : savedWorkflowId
                                        ? "更新"
                                        : "保存"}
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
                            {!isEditMode && !savedWorkflowId && (
                                <Badge
                                    variant="secondary"
                                    className="gap-1"
                                    title={`吨钢碳排放：${selectedTemplate.co2Range.min}-${selectedTemplate.co2Range.max} t CO₂/t 钢`}
                                >
                                    <Leaf className="size-3" />
                                    {selectedTemplate.co2Range.min}-{selectedTemplate.co2Range.max} t CO₂
                                </Badge>
                            )}
                            {!isEditMode && savedWorkflowId && (
                                <Badge
                                    variant="default"
                                    className="gap-1"
                                    title={`当前查看的是自定义工艺流程（ID: ${savedWorkflowId}）`}
                                >
                                    <Save className="size-3" />
                                    自定义流程
                                </Badge>
                            )}
                            {isEditMode && (
                                <Badge 
                                    variant={hasUnsavedChanges ? "destructive" : "default"} 
                                    className="gap-1 animate-pulse"
                                >
                                    <Edit3 className="size-3" />
                                    {hasUnsavedChanges ? "未保存 ⚠️" : "编辑中"}
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

