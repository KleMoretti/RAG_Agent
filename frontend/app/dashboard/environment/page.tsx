"use client";

import { useAuthStore } from "@/store/authStore";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Leaf,
    Zap,
    Droplets,
    Wind,
    TrendingDown,
    TrendingUp,
    RefreshCw,
    AlertTriangle,
    CheckCircle2,
    Activity,
    Gauge,
    Target,
} from "lucide-react";
import { roleDisplayNames } from "@/lib/permissions";
import { useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function EnvironmentPage() {
    const { user } = useAuthStore();
    const [refreshing, setRefreshing] = useState(false);

    // 环保指标统计
    const environmentStats = [
        {
            title: "能源消耗",
            value: "4,520 MWh",
            change: "-8.5%",
            trend: "down" as const,
            icon: Zap,
            description: "较上月下降",
            color: "text-yellow-500",
            status: "good",
        },
        {
            title: "CO₂ 排放",
            value: "2,850 吨",
            change: "-12.3%",
            trend: "down" as const,
            icon: Wind,
            description: "较上月下降",
            color: "text-blue-500",
            status: "good",
        },
        {
            title: "水资源消耗",
            value: "15,600 m³",
            change: "-5.2%",
            trend: "down" as const,
            icon: Droplets,
            description: "较上月下降",
            color: "text-cyan-500",
            status: "good",
        },
        {
            title: "废物回收率",
            value: "92.4%",
            change: "+3.1%",
            trend: "up" as const,
            icon: Leaf,
            description: "较上月提升",
            color: "text-green-500",
            status: "excellent",
        },
    ];

    // 实时监控指标
    const realtimeMetrics = [
        {
            id: "1",
            parameter: "烟气排放浓度",
            current: "45 mg/m³",
            standard: "≤ 50 mg/m³",
            status: "normal" as const,
            percentage: 90,
        },
        {
            id: "2",
            parameter: "噪声水平",
            current: "78 dB",
            standard: "≤ 85 dB",
            status: "normal" as const,
            percentage: 92,
        },
        {
            id: "3",
            parameter: "废水 COD",
            current: "42 mg/L",
            standard: "≤ 50 mg/L",
            status: "normal" as const,
            percentage: 84,
        },
        {
            id: "4",
            parameter: "粉尘浓度",
            current: "18 mg/m³",
            standard: "≤ 20 mg/m³",
            status: "warning" as const,
            percentage: 90,
        },
    ];

    // 节能优化建议
    const optimizationSuggestions = [
        {
            id: "1",
            title: "优化加热炉温度控制",
            impact: "预计节能 12%",
            priority: "high" as const,
            description: "采用智能温度控制算法，减少能源浪费",
            savings: "约 540 MWh/月",
        },
        {
            id: "2",
            title: "提升余热回收效率",
            impact: "预计节能 8%",
            priority: "medium" as const,
            description: "改进余热回收系统，提高能源利用率",
            savings: "约 360 MWh/月",
        },
        {
            id: "3",
            title: "水循环系统改造",
            impact: "节水 15%",
            priority: "medium" as const,
            description: "优化水循环系统，减少新鲜水消耗",
            savings: "约 2,340 m³/月",
        },
        {
            id: "4",
            title: "照明系统LED升级",
            impact: "预计节能 5%",
            priority: "low" as const,
            description: "更换为高效LED照明，降低电力消耗",
            savings: "约 225 MWh/月",
        },
    ];

    // 环保合规性检查
    const complianceChecks = [
        {
            item: "排放许可证",
            status: "compliant" as const,
            expiryDate: "2025-12-31",
            description: "已通过年度审查",
        },
        {
            item: "环境影响评估",
            status: "compliant" as const,
            expiryDate: "2025-06-30",
            description: "符合环保要求",
        },
        {
            item: "危废处理资质",
            status: "pending" as const,
            expiryDate: "2025-03-15",
            description: "需要续期",
        },
        {
            item: "在线监测系统",
            status: "compliant" as const,
            expiryDate: "-",
            description: "运行正常",
        },
    ];

    const handleRefresh = async () => {
        setRefreshing(true);
        // 模拟刷新数据
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setRefreshing(false);
    };

    const canManageEnvironment = user?.role === "admin" || user?.role === "manager";

    return (
        <div className="flex-1 space-y-6 p-8 overflow-y-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        环保监控
                    </h1>
                    <p className="text-muted-foreground mt-2">
                        当前角色:{" "}
                        {user?.role
                            ? roleDisplayNames[
                                  user.role as keyof typeof roleDisplayNames
                              ]
                            : "未知"}
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        disabled={refreshing}
                    >
                        <RefreshCw
                            className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`}
                        />
                        刷新数据
                    </Button>
                </div>
            </div>

            {/* 系统提示 */}
            <Alert>
                <Activity className="h-4 w-4" />
                <AlertDescription>
                    环保监控系统运行正常。所有指标均在标准范围内，{canManageEnvironment && "您可以"}查看详细数据和优化建议。
                </AlertDescription>
            </Alert>

            {/* 环保指标统计卡片 */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {environmentStats.map((stat) => {
                    const Icon = stat.icon;
                    const TrendIcon = stat.trend === "down" ? TrendingDown : TrendingUp;
                    return (
                        <Card key={stat.title}>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    {stat.title}
                                </CardTitle>
                                <Icon className={`h-4 w-4 ${stat.color}`} />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {stat.value}
                                </div>
                                <div className="flex items-center gap-2 mt-1">
                                    <TrendIcon
                                        className={`h-3 w-3 ${
                                            stat.status === "good" || stat.status === "excellent"
                                                ? "text-green-600 dark:text-green-400"
                                                : "text-red-600 dark:text-red-400"
                                        }`}
                                    />
                                    <span
                                        className={`text-xs font-medium ${
                                            stat.status === "good" || stat.status === "excellent"
                                                ? "text-green-600 dark:text-green-400"
                                                : "text-red-600 dark:text-red-400"
                                        }`}
                                    >
                                        {stat.change}
                                    </span>
                                    <p className="text-xs text-muted-foreground">
                                        {stat.description}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* 实时监控指标 */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Gauge className="h-5 w-5" />
                            实时监控指标
                        </CardTitle>
                        <CardDescription>
                            关键环保参数实时监测
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {realtimeMetrics.map((metric) => (
                                <div
                                    key={metric.id}
                                    className="border-b pb-4 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="space-y-1">
                                            <p className="font-medium text-sm">
                                                {metric.parameter}
                                            </p>
                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <span>当前: {metric.current}</span>
                                                <span>•</span>
                                                <span>标准: {metric.standard}</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            {metric.status === "normal" ? (
                                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                                            ) : (
                                                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                                            )}
                                            <span
                                                className={`text-xs ${
                                                    metric.status === "normal"
                                                        ? "text-green-600 dark:text-green-400"
                                                        : "text-yellow-600 dark:text-yellow-400"
                                                }`}
                                            >
                                                {metric.status === "normal" ? "正常" : "预警"}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2">
                                        <div
                                            className={`h-2 rounded-full transition-all ${
                                                metric.status === "normal"
                                                    ? "bg-green-500"
                                                    : "bg-yellow-500"
                                            }`}
                                            style={{ width: `${metric.percentage}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* 环保合规性检查 */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <CheckCircle2 className="h-5 w-5" />
                            合规性检查
                        </CardTitle>
                        <CardDescription>
                            环保法规和标准符合性状态
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {complianceChecks.map((check) => (
                                <div
                                    key={check.item}
                                    className="border-b pb-4 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <p className="font-medium text-sm">
                                                    {check.item}
                                                </p>
                                                <span
                                                    className={`text-xs px-2 py-0.5 rounded ${
                                                        check.status === "compliant"
                                                            ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                                                            : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                                                    }`}
                                                >
                                                    {check.status === "compliant"
                                                        ? "合规"
                                                        : "待处理"}
                                                </span>
                                            </div>
                                            <p className="text-xs text-muted-foreground">
                                                {check.description}
                                            </p>
                                            {check.expiryDate !== "-" && (
                                                <p className="text-xs text-muted-foreground">
                                                    有效期至: {check.expiryDate}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* 节能优化建议 */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5" />
                        节能优化建议
                    </CardTitle>
                    <CardDescription>
                        AI 分析生成的节能降耗优化方案
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {optimizationSuggestions.map((suggestion) => (
                            <div
                                key={suggestion.id}
                                className="border rounded-lg p-4 hover:bg-accent/50 transition-colors"
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div className="space-y-1 flex-1">
                                        <div className="flex items-center gap-2">
                                            <p className="font-medium">
                                                {suggestion.title}
                                            </p>
                                            <span
                                                className={`text-xs px-2 py-0.5 rounded ${
                                                    suggestion.priority === "high"
                                                        ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                                        : suggestion.priority === "medium"
                                                          ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                                                          : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                                }`}
                                            >
                                                {suggestion.priority === "high"
                                                    ? "高优先级"
                                                    : suggestion.priority === "medium"
                                                      ? "中优先级"
                                                      : "低优先级"}
                                            </span>
                                        </div>
                                        <p className="text-sm text-muted-foreground">
                                            {suggestion.description}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4 text-sm">
                                    <span className="text-green-600 dark:text-green-400 font-medium">
                                        {suggestion.impact}
                                    </span>
                                    <span className="text-muted-foreground">
                                        {suggestion.savings}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* 角色特定功能提示 */}
            {user?.role === "manager" && (
                <Card className="border-purple-200 bg-purple-50/50 dark:border-purple-900 dark:bg-purple-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Leaf className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                            经理功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">
                            ✅ 查看环保指标和合规性状态
                        </p>
                        <p className="text-sm">
                            ✅ 使用节能专家 Agent 获取优化建议
                        </p>
                        <p className="text-sm">
                            ✅ 分析能源消耗趋势和成本
                        </p>
                        <p className="text-sm">
                            ✅ 制定节能减排计划
                        </p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 切换到&ldquo;节能专家&rdquo;Agent
                            询问&ldquo;如何降低生产能耗？&rdquo;
                        </p>
                    </CardContent>
                </Card>
            )}

            {user?.role === "admin" && (
                <Card className="border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Leaf className="h-5 w-5 text-red-600 dark:text-red-400" />
                            管理员功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">✅ 配置环保监测系统和报警阈值</p>
                        <p className="text-sm">✅ 管理环保合规性文档和证书</p>
                        <p className="text-sm">
                            ✅ 导出环保数据报告（供监管部门审查）
                        </p>
                        <p className="text-sm">
                            ✅ 系统集成（连接在线监测设备）
                        </p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 可在系统管理面板配置环保数据采集源
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* 功能扩展提示 */}
            <Card className="border-dashed">
                <CardHeader>
                    <CardTitle>🚀 功能扩展计划</CardTitle>
                    <CardDescription>
                        未来将集成更多环保监控功能
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2 text-sm text-muted-foreground">
                        <p>📊 实时数据大屏（设备传感器数据接入）</p>
                        <p>📈 历史趋势分析和对比</p>
                        <p>🔔 环保指标超标自动报警</p>
                        <p>📋 环保报告自动生成（月报、年报）</p>
                        <p>🤖 AI 预测排放趋势和优化路径</p>
                        <p>🌍 碳足迹追踪和碳排放核算</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

