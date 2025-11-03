"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ProcessNode, ProcessEdge } from "@/lib/types/workflow";
import { NODE_COLORS, STATUS_COLORS } from "@/lib/constants/steelProcessTemplates";
import {
    Factory,
    Flame,
    FlaskConical,
    Droplets,
    Thermometer,
    Settings,
    CheckCircle2,
    Package,
    AlertCircle,
    AlertTriangle,
    Zap,
} from "lucide-react";

interface ProcessFlowChartProps {
    nodes: ProcessNode[];
    edges: ProcessEdge[];
    selectedNodeId?: string;
    onNodeSelect: (node: ProcessNode) => void;
    zoom?: number;
}

// 图标映射
const getNodeIcon = (nodeType: string, nodeName: string) => {
    if (nodeName.includes("炼铁") || nodeName.includes("高炉")) return Flame;
    if (nodeName.includes("炼钢") || nodeName.includes("转炉")) return FlaskConical;
    if (nodeName.includes("精炼")) return Droplets;
    if (nodeName.includes("加热")) return Thermometer;
    if (nodeName.includes("检验")) return CheckCircle2;
    if (nodeName.includes("原料") || nodeName.includes("成品")) return Package;
    if (nodeType === "equipment") return Settings;
    return Factory;
};

// 状态图标
const getStatusIcon = (status?: string) => {
    switch (status) {
        case "error":
            return <AlertCircle className="size-4 text-red-500" />;
        case "warning":
            return <AlertTriangle className="size-4 text-yellow-500" />;
        case "optimizing":
            return <Zap className="size-4 text-blue-500" />;
        default:
            return null;
    }
};

export function ProcessFlowChart({
    nodes,
    edges,
    selectedNodeId,
    onNodeSelect,
    zoom = 100,
}: ProcessFlowChartProps) {
    const [hoveredNodeId, setHoveredNodeId] = React.useState<string | null>(null);

    // SVG连线路径计算
    const getEdgePath = (edge: ProcessEdge) => {
        const sourceNode = nodes.find((n) => n.id === edge.source);
        const targetNode = nodes.find((n) => n.id === edge.target);
        if (!sourceNode || !targetNode) return "";

        const sx = sourceNode.position.x + 120; // 节点宽度的一半
        const sy = sourceNode.position.y + 40; // 节点高度的一半
        const tx = targetNode.position.x;
        const ty = targetNode.position.y + 40;

        const mx = (sx + tx) / 2;

        return `M ${sx} ${sy} C ${mx} ${sy}, ${mx} ${ty}, ${tx} ${ty}`;
    };

    // 计算缩放后的尺寸
    const scaledWidth = 2200 * (zoom / 100);
    const scaledHeight = 600 * (zoom / 100);

    return (
        <div className="relative w-full h-full overflow-auto bg-muted/30 rounded-lg border">
            <div
                className="relative"
                style={{
                    width: `${scaledWidth}px`,
                    height: `${scaledHeight}px`,
                    transformOrigin: "top left",
                    transform: `scale(${zoom / 100})`,
                }}
            >
                <svg
                    className="absolute top-0 left-0 w-full h-full pointer-events-none"
                    style={{ width: "2200px", height: "600px" }}
                >
                    <defs>
                        <marker
                            id="arrowhead"
                            markerWidth="10"
                            markerHeight="7"
                            refX="9"
                            refY="3.5"
                            orient="auto"
                        >
                            <polygon
                                points="0 0, 10 3.5, 0 7"
                                fill="currentColor"
                                className="text-border"
                            />
                        </marker>
                    </defs>

                {/* 绘制连线 */}
                {edges.map((edge) => (
                    <g key={edge.id}>
                        <path
                            d={getEdgePath(edge)}
                            stroke="currentColor"
                            strokeWidth="2"
                            fill="none"
                            markerEnd="url(#arrowhead)"
                            className={cn(
                                "text-border transition-colors",
                                edge.type === "material" && "stroke-dasharray-0",
                                edge.type === "energy" && "stroke-dasharray-5",
                            )}
                        />
                        {edge.label && (() => {
                            const sourceNode = nodes.find((n) => n.id === edge.source);
                            const targetNode = nodes.find((n) => n.id === edge.target);
                            if (!sourceNode || !targetNode) return null;
                            
                            return (
                                <text
                                    x={(sourceNode.position.x + 120 + targetNode.position.x) / 2}
                                    y={(sourceNode.position.y + 40 + targetNode.position.y + 40) / 2 - 5}
                                    fill="currentColor"
                                    className="text-xs text-muted-foreground pointer-events-none"
                                    textAnchor="middle"
                                >
                                    {edge.label}
                                </text>
                            );
                        })()}
                    </g>
                ))}
                </svg>

                {/* 绘制节点 */}
                <div className="relative" style={{ width: "2200px", height: "600px" }}>
                    {nodes.map((node) => {
                        const Icon = getNodeIcon(node.type, node.name);
                        const colors = NODE_COLORS[node.type];
                        const isSelected = selectedNodeId === node.id;
                        const isHovered = hoveredNodeId === node.id;

                        return (
                            <Card
                                key={node.id}
                                className={cn(
                                    "absolute cursor-pointer transition-all duration-200",
                                    "hover:shadow-lg hover:scale-105",
                                    "w-60 p-3",
                                    colors.bg,
                                    "border-2",
                                    node.status ? STATUS_COLORS[node.status] : colors.border,
                                    isSelected && "ring-2 ring-primary shadow-xl scale-105",
                                    isHovered && !isSelected && "shadow-md scale-102",
                                )}
                                style={{
                                    left: `${node.position.x}px`,
                                    top: `${node.position.y}px`,
                                }}
                                onClick={() => onNodeSelect(node)}
                                onMouseEnter={() => setHoveredNodeId(node.id)}
                                onMouseLeave={() => setHoveredNodeId(null)}
                            >
                                <div className="space-y-2">
                                    {/* 节点头部 */}
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-center gap-2 flex-1 min-w-0">
                                            <Icon className={cn("size-5 flex-shrink-0", colors.text)} />
                                            <h3 className={cn("font-semibold text-sm truncate", colors.text)}>
                                                {node.name}
                                            </h3>
                                        </div>
                                        {getStatusIcon(node.status)}
                                    </div>

                                    {/* 节点描述 */}
                                    <p className="text-xs text-muted-foreground line-clamp-2">
                                        {node.description}
                                    </p>

                                    {/* 关键参数预览 */}
                                    {node.parameters && node.parameters.length > 0 && (
                                        <div className="flex flex-wrap gap-1">
                                            {node.parameters.slice(0, 2).map((param, idx) => (
                                                <Badge
                                                    key={idx}
                                                    variant="secondary"
                                                    className="text-xs px-1.5 py-0.5"
                                                >
                                                    {param.name}
                                                </Badge>
                                            ))}
                                            {node.parameters.length > 2 && (
                                                <Badge variant="outline" className="text-xs px-1.5 py-0.5">
                                                    +{node.parameters.length - 2}
                                                </Badge>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

