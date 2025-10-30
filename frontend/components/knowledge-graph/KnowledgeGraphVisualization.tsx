"use client";

import { useEffect, useState, useCallback } from "react";
import ReactFlow, {
    Node,
    Edge,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    ConnectionMode,
    Panel,
    NodeTypes,
    MarkerType,
    NodeMouseHandler,
    useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";
import { AlertCircle, Info, Maximize2, Minimize2, Layout, Circle, Network as NetworkIcon } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getGraphVisualizationData, searchGraphVisualizationData, type GraphNode, type GraphEdge, type SearchEntitiesRequest } from "@/lib/api/knowledge-graph";
import { EntityDetailPanel } from "./EntityDetailPanel";

// 自定义节点组件 - 优化版本
function CustomNode({ data }: { data: any }) {
    const getNodeColor = (type: string) => {
        const colors: Record<string, string> = {
            steel_grade: "hsl(221 83% 53%)",      // 蓝色
            steel_type: "hsl(262 83% 58%)",       // 紫色
            alloy_element: "hsl(142 76% 36%)",    // 绿色
            material_property: "hsl(173 58% 39%)", // 青色
            process: "hsl(24 95% 53%)",           // 橙色
            equipment: "hsl(280 65% 60%)",        // 紫罗兰
            application: "hsl(199 89% 48%)",      // 天蓝
            standard: "hsl(45 93% 47%)",          // 黄色
            company: "hsl(339 90% 51%)",          // 粉色
            product: "hsl(160 60% 45%)",          // 翠绿
        };
        return colors[type] || "hsl(var(--muted))";
    };

    const getTypeLabel = (type: string) => {
        const labels: Record<string, string> = {
            steel_grade: "钢种",
            steel_type: "类型",
            alloy_element: "元素",
            material_property: "性能",
            process: "工艺",
            equipment: "设备",
            application: "应用",
            standard: "标准",
            company: "企业",
            product: "产品",
        };
        return labels[type] || type;
    };

    return (
        <div
            style={{
                padding: "10px 14px",
                borderRadius: "12px",
                border: data.matched ? `3px solid ${getNodeColor(data.type)}` : `2px solid ${getNodeColor(data.type)}`,
                background: data.matched ? getNodeColor(data.type) : "hsl(var(--card))",
                color: data.matched ? "white" : "hsl(var(--foreground))",
                minWidth: "100px",
                maxWidth: "180px",
                boxShadow: data.matched
                    ? `0 0 25px ${getNodeColor(data.type)}cc, 0 4px 12px rgba(0,0,0,0.15)`
                    : "0 3px 12px rgba(0, 0, 0, 0.12)",
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                cursor: "pointer",
            }}
            className="hover:scale-105"
        >
            {/* 实体名称 */}
            <div 
                className="font-bold text-base truncate mb-1" 
                title={data.label}
                style={{
                    textShadow: data.matched ? "0 1px 2px rgba(0,0,0,0.2)" : "none"
                }}
            >
                {data.label}
            </div>
            
            {/* 类型标签 */}
            <div className="flex items-center justify-between gap-2">
                <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                        data.matched 
                            ? "bg-white/20 backdrop-blur-sm" 
                            : "bg-opacity-10"
                    }`}
                    style={{
                        backgroundColor: data.matched ? "rgba(255,255,255,0.2)" : `${getNodeColor(data.type)}20`,
                        color: data.matched ? "white" : getNodeColor(data.type),
                        fontWeight: 600,
                    }}
                >
                    {getTypeLabel(data.type)}
                </span>
                
                {/* 置信度指示器 */}
                {data.confidence && (
                    <span className="text-xs font-semibold opacity-80">
                        {(data.confidence * 100).toFixed(0)}%
                    </span>
                )}
            </div>
        </div>
    );
}

const nodeTypes: NodeTypes = {
    custom: CustomNode,
};

type LayoutType = "force" | "hierarchical" | "circular";

interface KnowledgeGraphVisualizationProps {
    searchResults?: GraphNode[];
    isSearching: boolean;
    searchQuery?: string;
}

export function KnowledgeGraphVisualization({
    searchResults,
    isSearching,
    searchQuery,
}: KnowledgeGraphVisualizationProps) {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [graphStats, setGraphStats] = useState<{ nodes: number; edges: number } | null>(null);
    const [selectedEntity, setSelectedEntity] = useState<GraphNode | null>(null);
    const [graphData, setGraphData] = useState<{ nodes: GraphNode[]; edges: GraphEdge[] } | null>(null);
    const [layoutType, setLayoutType] = useState<LayoutType>("force");
    const [nodeLimit, setNodeLimit] = useState(50); // 限制显示节点数量

    // 加载图谱数据
    const loadGraphData = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            let data;
            
            if (searchQuery && searchQuery.trim()) {
                // 搜索模式
                const searchParams: SearchEntitiesRequest = {
                    query: searchQuery,
                    limit: nodeLimit,
                };
                data = await searchGraphVisualizationData(searchParams);
            } else {
                // 全量加载（根据nodeLimit限制）
                data = await getGraphVisualizationData(undefined, nodeLimit);
            }

            // 限制节点数量（防止过多节点导致性能问题）
            const limitedNodes = data.nodes.slice(0, nodeLimit);
            const limitedNodeIds = new Set(limitedNodes.map(n => n.id));
            
            // 只保留连接限制节点的边
            const limitedEdges = data.edges.filter(
                e => limitedNodeIds.has(e.source) && limitedNodeIds.has(e.target)
            );

            // 转换为 ReactFlow 格式
            const flowNodes: Node[] = limitedNodes.map((node, index) => ({
                id: node.id,
                type: "custom",
                position: calculateNodePosition(index, limitedNodes.length, node, limitedNodes, limitedEdges),
                data: {
                    label: node.label,
                    type: node.type,
                    description: node.description,
                    confidence: node.confidence,
                    matched: node.matched,
                },
            }));

            const flowEdges: Edge[] = limitedEdges.map((edge) => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
                type: "smoothstep",
                label: edge.label,
                animated: edge.confidence ? edge.confidence > 0.8 : false,
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    width: 20,
                    height: 20,
                },
                style: {
                    stroke: edge.confidence && edge.confidence > 0.8
                        ? "hsl(var(--primary))"
                        : "hsl(var(--muted-foreground))",
                    strokeWidth: edge.confidence ? edge.confidence * 3 : 2,
                },
                labelStyle: {
                    fontSize: 10,
                    fontWeight: 500,
                },
                labelBgStyle: {
                    fill: "hsl(var(--background))",
                    fillOpacity: 0.8,
                },
            }));

            setNodes(flowNodes);
            setEdges(flowEdges);
            setGraphStats({ nodes: limitedNodes.length, edges: limitedEdges.length });
            setGraphData({ nodes: limitedNodes, edges: limitedEdges });
        } catch (err) {
            console.error("加载图谱数据失败:", err);
            setError(err instanceof Error ? err.message : "加载图谱数据时出错");
        } finally {
            setIsLoading(false);
        }
    }, [searchQuery, setNodes, setEdges, layoutType, nodeLimit]);

    // 计算节点位置 - 多种布局算法
    const calculateNodePosition = (index: number, total: number, node: GraphNode, allNodes: GraphNode[], edges: GraphEdge[]) => {
        switch (layoutType) {
            case "force":
                return calculateForceDirectedPosition(index, node, allNodes, edges);
            case "hierarchical":
                return calculateHierarchicalPosition(index, node, allNodes);
            case "circular":
            default:
                return calculateCircularPosition(index, total);
        }
    };

    // 圆形布局（改进版）
    const calculateCircularPosition = (index: number, total: number) => {
        const radius = Math.min(350, Math.max(200, total * 15));
        const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
        const x = radius * Math.cos(angle) + 500;
        const y = radius * Math.sin(angle) + 400;
        return { x, y };
    };

    // 层次布局（按类型分层）
    const calculateHierarchicalPosition = (index: number, node: GraphNode, allNodes: GraphNode[]) => {
        // 按类型分组
        const typeGroups: Record<string, GraphNode[]> = {};
        allNodes.forEach(n => {
            if (!typeGroups[n.type]) typeGroups[n.type] = [];
            typeGroups[n.type].push(n);
        });

        const types = Object.keys(typeGroups);
        const typeIndex = types.indexOf(node.type);
        const nodesInType = typeGroups[node.type];
        const nodeIndexInType = nodesInType.findIndex(n => n.id === node.id);

        // 垂直分层
        const layerHeight = 150;
        const nodeSpacing = 180;
        const layerWidth = nodesInType.length * nodeSpacing;
        
        const y = typeIndex * layerHeight + 100;
        const x = (nodeIndexInType * nodeSpacing) - (layerWidth / 2) + 500;

        return { x, y };
    };

    // 力导向布局（简化版）
    const calculateForceDirectedPosition = (index: number, node: GraphNode, allNodes: GraphNode[], edges: GraphEdge[]) => {
        // 使用节点的连接度来计算初始位置
        const connectedEdges = edges.filter(e => e.source === node.id || e.target === node.id);
        const connectionCount = connectedEdges.length;

        // 连接度高的节点靠近中心
        const centerDistance = 200 + (10 - Math.min(connectionCount, 10)) * 30;
        const angle = (index / allNodes.length) * 2 * Math.PI;
        
        // 添加随机偏移避免重叠
        const randomOffset = Math.random() * 50 - 25;
        const x = centerDistance * Math.cos(angle) + 500 + randomOffset;
        const y = centerDistance * Math.sin(angle) + 400 + randomOffset;

        return { x, y };
    };

    useEffect(() => {
        loadGraphData();
    }, [loadGraphData]);

    const toggleFullscreen = () => {
        setIsFullscreen(!isFullscreen);
    };

    // 节点点击事件
    const onNodeClick: NodeMouseHandler = useCallback((event, node) => {
        if (graphData) {
            const entity = graphData.nodes.find(n => n.id === node.id);
            if (entity) {
                setSelectedEntity(entity);
            }
        }
    }, [graphData]);

    if (isLoading || isSearching) {
        return (
            <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4" />
                    <p className="text-muted-foreground">
                        {isSearching ? "搜索中..." : "加载图谱数据..."}
                    </p>
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

    if (nodes.length === 0) {
        return (
            <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">
                        {searchQuery
                            ? "未找到相关实体，请尝试其他关键词"
                            : "知识图谱为空，请先构建知识图谱"}
                    </p>
                </div>
            </div>
        );
    }

    const containerClass = isFullscreen
        ? "fixed inset-0 z-50 bg-background"
        : "relative h-[600px]";

    return (
        <div className={containerClass}>
            <div className="relative h-full">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onNodeClick={onNodeClick}
                    nodeTypes={nodeTypes}
                    connectionMode={ConnectionMode.Loose}
                    fitView
                    attributionPosition="bottom-left"
                >
                    <Background />
                    <Controls />
                    <MiniMap
                        nodeColor={(node) => {
                            const colors: Record<string, string> = {
                                steel_grade: "#3b82f6",
                                steel_type: "#8b5cf6",
                                alloy_element: "#10b981",
                                material_property: "#22c55e",
                                process: "#f97316",
                                equipment: "#a855f7",
                                application: "#0ea5e9",
                                standard: "#eab308",
                            };
                            return colors[node.data.type] || "#6b7280";
                        }}
                        maskColor="rgba(0, 0, 0, 0.2)"
                    />
                    {/* 控制面板 */}
                    <Panel position="top-right" className={`bg-card/80 backdrop-blur-sm rounded-lg p-4 shadow-lg space-y-3 ${selectedEntity ? "mr-96" : ""}`}>
                        {/* 统计信息 */}
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <Info className="h-4 w-4" />
                                <span className="text-sm font-semibold">图谱统计</span>
                            </div>
                            {graphStats && (
                                <div className="flex gap-2">
                                    <Badge variant="secondary">
                                        节点: {graphStats.nodes}
                                    </Badge>
                                    <Badge variant="secondary">
                                        关系: {graphStats.edges}
                                    </Badge>
                                </div>
                            )}
                        </div>

                        {/* 布局选择 */}
                        <div>
                            <div className="flex items-center gap-2 mb-2">
                                <Layout className="h-4 w-4" />
                                <span className="text-xs font-semibold">布局算法</span>
                            </div>
                            <div className="grid grid-cols-3 gap-1">
                                <Button
                                    variant={layoutType === "force" ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => setLayoutType("force")}
                                    className="text-xs p-1 h-auto"
                                    title="力导向布局"
                                >
                                    <NetworkIcon className="h-3 w-3" />
                                </Button>
                                <Button
                                    variant={layoutType === "hierarchical" ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => setLayoutType("hierarchical")}
                                    className="text-xs p-1 h-auto"
                                    title="层次布局"
                                >
                                    <Layout className="h-3 w-3" />
                                </Button>
                                <Button
                                    variant={layoutType === "circular" ? "default" : "outline"}
                                    size="sm"
                                    onClick={() => setLayoutType("circular")}
                                    className="text-xs p-1 h-auto"
                                    title="圆形布局"
                                >
                                    <Circle className="h-3 w-3" />
                                </Button>
                            </div>
                        </div>

                        {/* 节点数量限制 */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-semibold">显示节点</span>
                                <Badge variant="outline" className="text-xs">
                                    {nodeLimit}
                                </Badge>
                            </div>
                            <div className="flex gap-1">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setNodeLimit(30)}
                                    className="text-xs flex-1 h-7"
                                    disabled={nodeLimit === 30}
                                >
                                    30
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setNodeLimit(50)}
                                    className="text-xs flex-1 h-7"
                                    disabled={nodeLimit === 50}
                                >
                                    50
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setNodeLimit(100)}
                                    className="text-xs flex-1 h-7"
                                    disabled={nodeLimit === 100}
                                >
                                    100
                                </Button>
                            </div>
                        </div>

                        {/* 全屏按钮 */}
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={toggleFullscreen}
                            className="w-full"
                        >
                            {isFullscreen ? (
                                <>
                                    <Minimize2 className="h-4 w-4 mr-2" />
                                    退出全屏
                                </>
                            ) : (
                                <>
                                    <Maximize2 className="h-4 w-4 mr-2" />
                                    全屏显示
                                </>
                            )}
                        </Button>
                    </Panel>
                </ReactFlow>

                {/* 实体详情面板 */}
                {selectedEntity && (
                    <EntityDetailPanel
                        entity={selectedEntity}
                        onClose={() => setSelectedEntity(null)}
                    />
                )}
            </div>
        </div>
    );
}
