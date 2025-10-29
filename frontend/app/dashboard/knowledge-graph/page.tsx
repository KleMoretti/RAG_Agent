"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
    Network,
    RefreshCw,
    Search,
    Database,
    TrendingUp,
    AlertCircle,
    CheckCircle2,
    Layers,
} from "lucide-react";
import { toast } from "sonner";
import { useAuthStore } from "@/store/authStore";
import { hasPermission } from "@/lib/permissions";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
    getKnowledgeGraphStats,
    searchEntities,
    buildKnowledgeGraph,
    getEntityTypes,
    type KnowledgeGraphStats,
    type SearchEntitiesRequest,
} from "@/lib/api/knowledge-graph";
import { KnowledgeGraphVisualization } from "@/components/knowledge-graph/KnowledgeGraphVisualization";
import { EntityListView } from "@/components/knowledge-graph/EntityListView";

export default function KnowledgeGraphPage() {
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedEntityType, setSelectedEntityType] = useState<string | undefined>();
    const [viewMode, setViewMode] = useState<"graph" | "list">("graph");

    const queryClient = useQueryClient();
    const { user } = useAuthStore();

    // 检查权限
    const canBuildGraph = hasPermission(user, "canUpload"); // 管理员和经理可以构建知识图谱

    // 获取知识图谱统计信息
    const { data: stats, isLoading: isStatsLoading } = useQuery<KnowledgeGraphStats>({
        queryKey: ["knowledgeGraphStats"],
        queryFn: getKnowledgeGraphStats,
    });

    // 获取实体类型列表
    const { data: entityTypes } = useQuery<string[]>({
        queryKey: ["entityTypes"],
        queryFn: getEntityTypes,
    });

    // 搜索实体
    const { data: searchResults, isLoading: isSearching } = useQuery({
        queryKey: ["searchEntities", searchQuery, selectedEntityType],
        queryFn: () => {
            if (!searchQuery) return { entities: [], total_count: 0 };
            const params: SearchEntitiesRequest = {
                query: searchQuery,
                limit: 100,
            };
            if (selectedEntityType) {
                params.entity_types = [selectedEntityType];
            }
            return searchEntities(params);
        },
        enabled: searchQuery.length > 0,
    });

    // 构建知识图谱
    const buildMutation = useMutation({
        mutationFn: buildKnowledgeGraph,
        onSuccess: (data) => {
            toast.success("知识图谱构建成功", {
                description: `实体数量: ${data.stats?.total_entities || 0}, 关系数量: ${data.stats?.total_relations || 0}`,
            });
            queryClient.invalidateQueries({ queryKey: ["knowledgeGraphStats"] });
        },
        onError: (error: unknown) => {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })?.response?.data
                          ?.detail || "构建知识图谱时出错";
            toast.error("构建失败", {
                description: errorMessage,
            });
        },
    });

    const handleBuildGraph = () => {
        if (!canBuildGraph) {
            toast.error("权限不足", {
                description: "只有管理员和经理可以构建知识图谱",
            });
            return;
        }
        buildMutation.mutate();
    };

    return (
        <div className="h-full overflow-y-auto">
            <div className="container mx-auto p-6 space-y-6">
                {/* 页面标题 */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold flex items-center gap-2">
                            <Network className="h-8 w-8" />
                            知识图谱
                        </h1>
                        <p className="text-muted-foreground mt-2">
                            探索钢铁行业实体和关系的知识网络
                        </p>
                    </div>
                    {canBuildGraph && (
                        <Button
                            onClick={handleBuildGraph}
                            disabled={buildMutation.isPending}
                        >
                            <RefreshCw
                                className={`h-4 w-4 mr-2 ${buildMutation.isPending ? "animate-spin" : ""}`}
                            />
                            {buildMutation.isPending ? "构建中..." : "重新构建图谱"}
                        </Button>
                    )}
                </div>

                {/* 统计卡片 */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">总实体数</CardTitle>
                            <Database className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {isStatsLoading ? (
                                    <RefreshCw className="h-6 w-6 animate-spin" />
                                ) : (
                                    stats?.total_entities?.toLocaleString() || 0
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground">
                                包含钢种、工艺、设备等
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">总关系数</CardTitle>
                            <TrendingUp className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {isStatsLoading ? (
                                    <RefreshCw className="h-6 w-6 animate-spin" />
                                ) : (
                                    stats?.total_relations?.toLocaleString() || 0
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground">
                                实体之间的关联关系
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">实体类型</CardTitle>
                            <Layers className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {isStatsLoading ? (
                                    <RefreshCw className="h-6 w-6 animate-spin" />
                                ) : (
                                    Object.keys(stats?.entity_type_counts || {}).length
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground">
                                不同类型的实体分类
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">数据状态</CardTitle>
                            {stats && stats.total_entities > 0 ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                            ) : (
                                <AlertCircle className="h-4 w-4 text-yellow-500" />
                            )}
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {stats && stats.total_entities > 0 ? (
                                    <Badge variant="default">已加载</Badge>
                                ) : (
                                    <Badge variant="secondary">未构建</Badge>
                                )}
                            </div>
                            <p className="text-xs text-muted-foreground">
                                {stats && stats.total_entities > 0
                                    ? "知识图谱已准备就绪"
                                    : "请先构建知识图谱"}
                            </p>
                        </CardContent>
                    </Card>
                </div>

                {/* 提示信息 */}
                {(!stats || stats.total_entities === 0) && (
                    <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>知识图谱未构建</AlertTitle>
                        <AlertDescription>
                            知识图谱尚未构建。
                            {canBuildGraph ? (
                                <>
                                    请点击右上角的
                                    <strong>&ldquo;重新构建图谱&rdquo;</strong>
                                    按钮从已上传的文档中构建知识图谱。
                                </>
                            ) : (
                                "请联系管理员构建知识图谱。"
                            )}
                        </AlertDescription>
                    </Alert>
                )}

                {/* 搜索栏 */}
                <Card>
                    <CardHeader>
                        <CardTitle>搜索实体</CardTitle>
                        <CardDescription>
                            在知识图谱中搜索钢种、工艺、设备等实体
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-4">
                            <div className="relative flex-1">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="输入实体名称，如 Q235、热轧、转炉..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                            <select
                                value={selectedEntityType || ""}
                                onChange={(e) =>
                                    setSelectedEntityType(e.target.value || undefined)
                                }
                                className="px-3 py-2 border rounded-md bg-background"
                            >
                                <option value="">全部类型</option>
                                {entityTypes?.map((type) => (
                                    <option key={type} value={type}>
                                        {type}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* 搜索结果提示 */}
                        {searchQuery && searchResults && (
                            <div className="mt-4">
                                <Badge variant="outline">
                                    找到 {searchResults.total_count} 个结果
                                </Badge>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* 视图切换 */}
                <div className="flex items-center gap-2">
                    <Button
                        variant={viewMode === "graph" ? "default" : "outline"}
                        onClick={() => setViewMode("graph")}
                        size="sm"
                    >
                        <Network className="h-4 w-4 mr-2" />
                        图谱视图
                    </Button>
                    <Button
                        variant={viewMode === "list" ? "default" : "outline"}
                        onClick={() => setViewMode("list")}
                        size="sm"
                    >
                        <Layers className="h-4 w-4 mr-2" />
                        列表视图
                    </Button>
                </div>

                {/* 主要内容区 */}
                {stats && stats.total_entities > 0 ? (
                    <Card>
                        <CardContent className="p-6">
                            {viewMode === "graph" ? (
                                <KnowledgeGraphVisualization
                                    searchResults={searchResults?.entities || []}
                                    isSearching={isSearching}
                                />
                            ) : (
                                <EntityListView
                                    entities={searchResults?.entities || []}
                                    isLoading={isSearching}
                                    stats={stats}
                                />
                            )}
                        </CardContent>
                    </Card>
                ) : null}
            </div>
        </div>
    );
}

