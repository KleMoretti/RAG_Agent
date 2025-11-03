"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Network, Loader2, AlertCircle, X, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { getCoreEntities, getSpiderWebGraph, getEntity, type CoreEntity, type SpiderWebData, type Entity } from "@/lib/api/knowledge-graph";

interface SpiderWebViewProps {
    className?: string;
}

interface NodePosition {
    x: number;
    y: number;
    scale: number;
    opacity: number;
}

export function SpiderWebView({ className }: SpiderWebViewProps) {
    const [selectedCoreId, setSelectedCoreId] = useState<string | null>(null);
    const [maxDepth, setMaxDepth] = useState(2);
    const [hoveredNode, setHoveredNode] = useState<string | null>(null);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const [nodePositions, setNodePositions] = useState<Record<string, NodePosition>>({});

    // 获取核心实体列表
    const { data: coreEntities, isLoading: isCoreLoading } = useQuery<{ core_entities: CoreEntity[]; total: number }>({
        queryKey: ["coreEntities"],
        queryFn: getCoreEntities,
    });

    // 自动选择第一个核心实体（如果没有选择）
    useEffect(() => {
        if (coreEntities?.core_entities && coreEntities.core_entities.length > 0 && !selectedCoreId) {
            setSelectedCoreId(coreEntities.core_entities[0].id);
        }
    }, [coreEntities, selectedCoreId]);

    // 获取蛛网数据
    const { data: spiderWebData, isLoading: isWebLoading } = useQuery<SpiderWebData>({
        queryKey: ["spiderWeb", selectedCoreId, maxDepth],
        queryFn: () => getSpiderWebGraph(selectedCoreId!, maxDepth),
        enabled: !!selectedCoreId,
    });

    // 获取选中节点的详情
    const { data: selectedNodeData } = useQuery<Entity>({
        queryKey: ["entity", selectedNode],
        queryFn: () => getEntity(selectedNode!),
        enabled: !!selectedNode,
    });

    // 点击节点处理：切换为新的中心节点并同步更新选择栏
    const handleNodeClick = (entityId: string) => {
        setSelectedCoreId(entityId);
        setSelectedNode(entityId);
    };

    const getCategoryColor = (category: string) => {
        const colors: Record<string, string> = {
            "成分特征": "#10b981",   // emerald-500
            "性能特征": "#3b82f6",   // blue-500
            "工艺特征": "#f59e0b",   // amber-500
            "应用特征": "#8b5cf6",   // violet-500
            "其他": "#6b7280",       // gray-500
        };
        return colors[category] || colors["其他"];
    };

    const renderSpiderWeb = () => {
        if (!spiderWebData) return null;

        const { center, features, stats } = spiderWebData;
        const canvasSize = 900; // 适当增大画布以容纳更分散的节点
        const centerX = canvasSize / 2;
        const centerY = canvasSize / 2;
        
        // 层级大小定义（按比例缩小）
        const centerRadius = 70;      // 第0层：中心节点（最大）
        const categoryNodeRadius = 40; // 第1层：分类节点（中等）
        const entityNodeRadius = 16;   // 第2层：实体节点（增大以便查看）

        // 计算每个特征分类的位置（均匀圆形布局）
        const categories = Object.keys(features).filter(cat => features[cat].length > 0);
        const angleStep = (2 * Math.PI) / Math.max(categories.length, 1);

        // 第一层：分类节点（圆形均匀分布，距离缩小）
        const categoryRadius = 230; // 距离中心的半径
        const categoryPositions: Record<string, { x: number; y: number; angle: number }> = {};

        categories.forEach((category, index) => {
            const angle = index * angleStep - Math.PI / 2; // 从顶部开始
            categoryPositions[category] = {
                x: centerX + categoryRadius * Math.cos(angle),
                y: centerY + categoryRadius * Math.sin(angle),
                angle,
            };
        });

        // 第二层：实体节点（均匀圆形分布在分类节点周围，增大间距）
        const entityRadius = 140; // 实体距离分类节点的半径（增大以减少重叠）
        const allEntities: Array<{
            entity: any;
            x: number;
            y: number;
            category: string;
            categoryPos: { x: number; y: number };
        }> = [];

        categories.forEach((category) => {
            const categoryPos = categoryPositions[category];
            const entities = features[category];
            const entityCount = entities.length;
            
            if (entityCount === 0) return;
            
            // 计算该分类的扇形角度范围（增大角度以增加节点间距）
            const maxArcAngle = Math.PI * 0.8; // 最大117度扇形（增大）
            const arcAngle = Math.min(maxArcAngle, Math.max(Math.PI / 5, entityCount * 0.15));
            
            entities.forEach((entity, index) => {
                // 均匀分布在扇形区域内
                let angle;
                if (entityCount === 1) {
                    // 单个实体：直接沿着分类方向
                    angle = categoryPos.angle;
                } else {
                    // 多个实体：均匀分布在扇形范围内
                    const startAngle = categoryPos.angle - arcAngle / 2;
                    const anglePerEntity = arcAngle / (entityCount - 1);
                    angle = startAngle + index * anglePerEntity;
                }
                
                // 计算实体节点位置（围绕分类节点圆形分布）
                const x = categoryPos.x + entityRadius * Math.cos(angle);
                const y = categoryPos.y + entityRadius * Math.sin(angle);
                
                allEntities.push({
                    entity,
                    x,
                    y,
                    category,
                    categoryPos,
                });
            });
        });

        // 计算节点的显示状态（选中时降低其他节点的可见度）
        const getNodeOpacity = (entityId: string) => {
            if (!selectedNode) return 1;
            return entityId === selectedNode ? 1 : 0.3;
        };

        const getLineOpacity = (entityId: string) => {
            if (!selectedNode) return 0.4;
            return entityId === selectedNode ? 0.8 : 0.15;
        };

        return (
            <div className="relative flex gap-6 max-w-full">
                {/* SVG 蛛网图 */}
                <div className="flex-1 flex justify-center">
                <svg
                    width={canvasSize}
                    height={canvasSize}
                        viewBox={`0 0 ${canvasSize} ${canvasSize}`}
                        className="border rounded-lg bg-gradient-to-br from-muted/5 to-muted/20"
                        style={{ maxWidth: "100%", height: "auto", width: "100%", maxHeight: "85vh" }}
                >
                        {/* 定义渐变和滤镜 */}
                    <defs>
                        <marker
                            id="arrowhead"
                            markerWidth="10"
                            markerHeight="10"
                            refX="9"
                            refY="3"
                            orient="auto"
                            markerUnits="strokeWidth"
                        >
                            <path d="M0,0 L0,6 L9,3 z" fill="currentColor" opacity="0.4" />
                        </marker>
                            <filter id="glow">
                                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                                <feMerge>
                                    <feMergeNode in="coloredBlur"/>
                                    <feMergeNode in="SourceGraphic"/>
                                </feMerge>
                            </filter>
                    </defs>

                        {/* 背景圆环（装饰） */}
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={categoryRadius}
                            fill="none"
                            stroke="hsl(var(--border))"
                            strokeWidth="2"
                            strokeDasharray="8,6"
                            opacity="0.15"
                        />
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={categoryRadius + entityRadius}
                            fill="none"
                            stroke="hsl(var(--border))"
                            strokeWidth="1"
                            strokeDasharray="4,4"
                            opacity="0.1"
                        />

                    {/* 绘制从中心到分类的连线 */}
                    {categories.map((category) => {
                        const pos = categoryPositions[category];
                        const color = getCategoryColor(category);
                        return (
                                <motion.line
                                key={`cat-line-${category}`}
                                x1={centerX}
                                y1={centerY}
                                x2={pos.x}
                                y2={pos.y}
                                stroke={color}
                                strokeWidth="3"
                                    strokeOpacity="0.25"
                                    initial={{ pathLength: 0 }}
                                    animate={{ pathLength: 1 }}
                                    transition={{ duration: 0.8, ease: "easeOut" }}
                            />
                        );
                    })}

                        {/* 绘制从分类到实体的连线 */}
                        {allEntities.map(({ entity, x, y, category, categoryPos }) => {
                            const color = getCategoryColor(category);
                            const isSelected = entity.id === selectedNode;
                            const isHovered = entity.id === hoveredNode;

                            return (
                                <motion.line
                                    key={`entity-line-${entity.id}`}
                                        x1={categoryPos.x}
                                        y1={categoryPos.y}
                                        x2={x}
                                        y2={y}
                                        stroke={color}
                                    strokeWidth={isSelected || isHovered ? "2.5" : "1.5"}
                                    strokeOpacity={getLineOpacity(entity.id)}
                                    animate={{
                                        strokeOpacity: getLineOpacity(entity.id),
                                        strokeWidth: isSelected || isHovered ? 2.5 : 1.5,
                                    }}
                                    transition={{ duration: 0.3 }}
                                />
                            );
                        })}

                        {/* 绘制实体节点 */}
                        {allEntities.map(({ entity, x, y, category }) => {
                            const color = getCategoryColor(category);
                            const isHovered = hoveredNode === entity.id;
                            const isSelected = selectedNode === entity.id;
                            const isStandard = entity.is_standard;
                            
                            // 根据状态调整半径
                            const radius = isSelected 
                                ? entityNodeRadius * 1.3 
                                : isHovered 
                                    ? entityNodeRadius * 1.15 
                                    : entityNodeRadius;

                            return (
                                <motion.g
                                    key={entity.id}
                                        onMouseEnter={() => setHoveredNode(entity.id)}
                                        onMouseLeave={() => setHoveredNode(null)}
                                    onClick={() => handleNodeClick(entity.id)}
                                    className="cursor-pointer"
                                    animate={{
                                        opacity: getNodeOpacity(entity.id),
                                    }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <motion.circle
                                            cx={x}
                                            cy={y}
                                        r={radius}
                                            fill={isStandard ? color : "white"}
                                            stroke={color}
                                        strokeWidth={isStandard ? "2.5" : "2"}
                                        filter={isSelected ? "url(#glow)" : undefined}
                                        animate={{
                                            scale: isSelected ? 1.1 : isHovered ? 1.05 : 1,
                                        }}
                                        transition={{ type: "spring", stiffness: 300, damping: 20 }}
                                    />
                                    <text
                                        x={x}
                                        y={y + radius + 18}
                                        textAnchor="middle"
                                        className="text-xs font-medium fill-current pointer-events-none select-none"
                                        style={{ fontSize: isSelected ? "11px" : isHovered ? "10.5px" : "10px" }}
                                    >
                                        {entity.name.length > 8
                                            ? entity.name.substring(0, 8) + "..."
                                            : entity.name}
                                    </text>
                                </motion.g>
                            );
                    })}

                    {/* 绘制分类节点 */}
                    {categories.map((category) => {
                        const pos = categoryPositions[category];
                        const color = getCategoryColor(category);
                        const entityCount = features[category].length;

                        return (
                                <motion.g
                                    key={`cat-${category}`}
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ duration: 0.5, ease: "backOut", delay: 0.2 }}
                                >
                                    {/* 外圈光晕 */}
                                    <circle
                                        cx={pos.x}
                                        cy={pos.y}
                                        r={categoryNodeRadius + 12}
                                        fill={color}
                                        fillOpacity="0.08"
                                        stroke="none"
                                    />
                                    {/* 主节点 */}
                                <circle
                                    cx={pos.x}
                                    cy={pos.y}
                                        r={categoryNodeRadius}
                                    fill={color}
                                    fillOpacity="0.2"
                                    stroke={color}
                                        strokeWidth="4"
                                />
                                <text
                                    x={pos.x}
                                        y={pos.y - 8}
                                    textAnchor="middle"
                                    dominantBaseline="middle"
                                        className="text-sm font-bold select-none"
                                        style={{ fill: color }}
                                >
                                    {category}
                                </text>
                                <text
                                    x={pos.x}
                                        y={pos.y + 12}
                                    textAnchor="middle"
                                        className="text-xs select-none"
                                        style={{ fill: color, opacity: 0.8 }}
                                >
                                    ({entityCount})
                                </text>
                                </motion.g>
                        );
                    })}

                        {/* 绘制中心节点（带动画） */}
                        <motion.g
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 180, damping: 12, delay: 0.1 }}
                        >
                            {/* 外圈光晕 */}
                            <circle
                                cx={centerX}
                                cy={centerY}
                                r={centerRadius + 12}
                                fill="hsl(var(--primary))"
                                fillOpacity="0.1"
                                stroke="none"
                            />
                            {/* 主节点 */}
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={centerRadius}
                            fill="hsl(var(--primary))"
                            fillOpacity="0.9"
                            stroke="hsl(var(--primary))"
                                strokeWidth="5"
                                filter="url(#glow)"
                            />
                            {/* 内圈装饰 */}
                            <circle
                                cx={centerX}
                                cy={centerY}
                                r={centerRadius - 8}
                                fill="none"
                                stroke="white"
                                strokeWidth="2"
                                strokeOpacity="0.3"
                        />
                        <text
                            x={centerX}
                                y={centerY - 5}
                            textAnchor="middle"
                            dominantBaseline="middle"
                                className="text-lg font-bold fill-white select-none"
                        >
                            {center.name}
                        </text>
                        <text
                            x={centerX}
                                y={centerY + 15}
                            textAnchor="middle"
                                className="text-xs fill-white opacity-90 select-none"
                        >
                            {center.type}
                        </text>
                        </motion.g>
                </svg>

                    {/* 图例 - 单列布局 */}
                    <div className="mt-4 flex flex-col gap-2 items-center">
                        {categories.map((category) => (
                            <motion.div
                                key={category}
                                className="flex items-center gap-3 w-full max-w-sm px-2"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                            >
                            <div
                                className="w-3 h-3 rounded-full border-2 flex-shrink-0"
                                style={{
                                    backgroundColor: getCategoryColor(category),
                                    borderColor: getCategoryColor(category),
                                }}
                            />
                            <span className="text-xs flex-1 whitespace-nowrap">
                                {category}
                            </span>
                            <span className="text-xs text-muted-foreground font-medium">
                                {features[category].length}
                            </span>
                            </motion.div>
                        ))}
                    </div>
                </div>

                {/* 节点详情面板 - 桌面端（右侧固定） */}
                <AnimatePresence>
                    {selectedNode && selectedNodeData && (
                        <>
                            {/* 桌面端详情面板 */}
                            <motion.div
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: 20 }}
                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                className="w-80 flex-shrink-0 hidden lg:block"
                            >
                        <Card>
                                <CardHeader className="pb-3">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <CardTitle className="text-lg flex items-center gap-2">
                                                <Info className="h-5 w-5 text-primary" />
                                                节点详情
                                            </CardTitle>
                                        </div>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-6 w-6"
                                            onClick={() => setSelectedNode(null)}
                                        >
                                            <X className="h-4 w-4" />
                                        </Button>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {/* 节点名称 */}
                                    <div>
                                        <h3 className="text-xl font-bold mb-1">{selectedNodeData.name}</h3>
                                        <Badge variant="outline">{selectedNodeData.entity_type}</Badge>
                                    </div>

                                    <Separator />

                                    {/* 描述 */}
                                    {selectedNodeData.description && (
                                        <div>
                                            <h4 className="text-sm font-semibold mb-2 text-muted-foreground">描述</h4>
                                            <p className="text-sm leading-relaxed">{selectedNodeData.description}</p>
                                        </div>
                                    )}

                                    {/* 属性 */}
                                    {selectedNodeData.properties && Object.keys(selectedNodeData.properties).length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-semibold mb-2 text-muted-foreground">属性</h4>
                                            <div className="space-y-2">
                                                {Object.entries(selectedNodeData.properties).map(([key, value]) => (
                                                    <div key={key} className="flex justify-between text-sm">
                                                        <span className="text-muted-foreground">{key}:</span>
                                                        <span className="font-medium">{String(value)}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* 别名 */}
                                    {selectedNodeData.aliases && selectedNodeData.aliases.length > 0 && (
                                        <div>
                                            <h4 className="text-sm font-semibold mb-2 text-muted-foreground">别名</h4>
                                            <div className="flex flex-wrap gap-1">
                                                {selectedNodeData.aliases.map((alias, index) => (
                                                    <Badge key={index} variant="secondary" className="text-xs">
                                                        {alias}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* 置信度 */}
                                    {selectedNodeData.confidence !== undefined && (
                                        <div>
                                            <h4 className="text-sm font-semibold mb-2 text-muted-foreground">置信度</h4>
                                            <div className="flex items-center gap-2">
                                                <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-primary"
                                                        style={{ width: `${selectedNodeData.confidence * 100}%` }}
                                                    />
                                                </div>
                                                <span className="text-sm font-medium">
                                                    {(selectedNodeData.confidence * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                        </div>
                                    )}

                                    {/* 操作按钮 */}
                                    <Button
                                        className="w-full"
                                        onClick={() => handleNodeClick(selectedNode)}
                                        disabled={selectedNode === selectedCoreId}
                                    >
                                        <Network className="h-4 w-4 mr-2" />
                                        {selectedNode === selectedCoreId ? "当前中心节点" : "设为中心节点"}
                                    </Button>
                            </CardContent>
                        </Card>
                            </motion.div>

                            {/* 移动端详情面板（浮动覆盖） */}
                            <motion.div
                                initial={{ opacity: 0, y: 50 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 50 }}
                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                className="lg:hidden fixed bottom-0 left-0 right-0 z-50 p-4"
                            >
                                <Card className="shadow-2xl">
                                    <CardHeader className="pb-3">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <CardTitle className="text-base flex items-center gap-2">
                                                    <Info className="h-4 w-4 text-primary" />
                                                    {selectedNodeData.name}
                                                </CardTitle>
                                                <Badge variant="outline" className="mt-1 text-xs">
                                                    {selectedNodeData.entity_type}
                                                </Badge>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-6 w-6"
                                                onClick={() => setSelectedNode(null)}
                                            >
                                                <X className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </CardHeader>
                                    <CardContent className="space-y-3 max-h-64 overflow-y-auto">
                                        {selectedNodeData.description && (
                                            <p className="text-sm leading-relaxed">{selectedNodeData.description}</p>
                                        )}
                                        {selectedNodeData.confidence !== undefined && (
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-primary"
                                                            style={{ width: `${selectedNodeData.confidence * 100}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-xs font-medium">
                                                        {(selectedNodeData.confidence * 100).toFixed(1)}%
                                                    </span>
                                                </div>
                                            </div>
                                        )}
                            </CardContent>
                        </Card>
                            </motion.div>
                        </>
                    )}
                </AnimatePresence>
            </div>
        );
    };

    if (isCoreLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                <span className="ml-2 text-muted-foreground">加载核心实体...</span>
            </div>
        );
    }

    if (!coreEntities || coreEntities.core_entities.length === 0) {
        return (
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                    未找到核心实体。请先构建知识图谱。
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className={className}>
            {/* 控制面板 */}
            <div className="mb-6 flex items-center gap-4">
                <div className="flex-1">
                    <label className="text-sm font-medium mb-2 block">选择中心实体</label>
                    <Select value={selectedCoreId || ""} onValueChange={(value) => {
                        setSelectedCoreId(value);
                        setSelectedNode(null); // 清除之前选中的节点
                    }}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="选择核心实体" />
                        </SelectTrigger>
                        <SelectContent>
                            {coreEntities.core_entities.map((entity) => (
                                <SelectItem key={entity.id} value={entity.id}>
                                    <div className="flex items-center gap-2">
                                        <Badge variant={entity.is_standard ? "default" : "outline"} className="text-xs">
                                            {entity.type}
                                        </Badge>
                                        <span>{entity.name}</span>
                                        <span className="text-muted-foreground text-xs">
                                            ({entity.related_count} 个关联)
                                        </span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div>
                    <label className="text-sm font-medium mb-2 block">深度</label>
                    <Select value={maxDepth.toString()} onValueChange={(v) => setMaxDepth(parseInt(v))}>
                        <SelectTrigger className="w-32">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="1">1 层</SelectItem>
                            <SelectItem value="2">2 层</SelectItem>
                            <SelectItem value="3">3 层</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* 蛛网图谱 */}
            {isWebLoading ? (
                <div className="flex items-center justify-center h-96">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    <span className="ml-2 text-muted-foreground">生成蛛网图谱...</span>
                </div>
            ) : (
                renderSpiderWeb()
            )}

            {/* 说明 */}
            <div className="mt-6 space-y-2 text-sm text-muted-foreground">
                <p>
                    <strong>交互说明：</strong>
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>
                        <strong>悬停节点</strong>：高亮显示节点及其连接关系
                    </li>
                    <li>
                        <strong>点击节点</strong>：查看节点详情并可设为新的中心节点
                    </li>
                    <li>
                        <strong>实心节点</strong>：标准本体中的实体
                    </li>
                    <li>
                        <strong>空心节点</strong>：从文档中提取的实体
                    </li>
                    <li>
                        <strong>圆形布局</strong>：特征节点围绕中心圆形分布，易于查看关系
                    </li>
                </ul>
            </div>
        </div>
    );
}
