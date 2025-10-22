"use client";

import { useAuthStore } from "@/store/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, TrendingUp, TrendingDown, DollarSign, BarChart3 } from "lucide-react";
import { roleDisplayNames } from "@/lib/permissions";

export default function MarketPage() {
    const { user } = useAuthStore();

    const marketStats = [
        {
            title: "铁矿石价格",
            value: "¥890/吨",
            change: "+2.3%",
            trend: "up",
            icon: TrendingUp,
            description: "较上周上涨",
        },
        {
            title: "螺纹钢价格",
            value: "¥4,250/吨",
            change: "-1.5%",
            trend: "down",
            icon: TrendingDown,
            description: "较上周下跌",
        },
        {
            title: "焦炭价格",
            value: "¥2,180/吨",
            change: "+0.8%",
            trend: "up",
            icon: TrendingUp,
            description: "较上周上涨",
        },
        {
            title: "废钢价格",
            value: "¥2,650/吨",
            change: "+3.2%",
            trend: "up",
            icon: TrendingUp,
            description: "较上周上涨",
        },
    ];

    const marketNews = [
        {
            id: "1",
            title: "国内铁矿石港口库存持续下降",
            source: "钢铁行业资讯",
            time: "2小时前",
            category: "供应",
        },
        {
            id: "2",
            title: "建筑钢材需求季节性回升",
            source: "市场分析",
            time: "5小时前",
            category: "需求",
        },
        {
            id: "3",
            title: "环保限产政策调整影响产量",
            source: "政策动态",
            time: "昨天",
            category: "政策",
        },
        {
            id: "4",
            title: "进口铁矿石到港量预计增加",
            source: "国际贸易",
            time: "2天前",
            category: "供应",
        },
    ];

    const priceForecasts = [
        {
            material: "铁矿石",
            current: "¥890/吨",
            nextWeek: "¥900-920/吨",
            trend: "上涨",
            confidence: "中等",
        },
        {
            material: "螺纹钢",
            current: "¥4,250/吨",
            nextWeek: "¥4,200-4,280/吨",
            trend: "震荡",
            confidence: "较高",
        },
        {
            material: "热卷",
            current: "¥4,180/吨",
            nextWeek: "¥4,150-4,220/吨",
            trend: "震荡",
            confidence: "较高",
        },
    ];

    return (
        <div className="flex-1 space-y-6 p-8 overflow-y-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">市场分析</h1>
                    <p className="text-muted-foreground mt-2">
                        当前角色: {user?.role ? roleDisplayNames[user.role as keyof typeof roleDisplayNames] : "未知"}
                    </p>
                </div>
            </div>

            {/* 价格统计卡片 */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {marketStats.map((stat) => {
                    const Icon = stat.icon;
                    return (
                        <Card key={stat.title}>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    {stat.title}
                                </CardTitle>
                                <Icon
                                    className={`h-4 w-4 ${
                                        stat.trend === "up"
                                            ? "text-green-500"
                                            : "text-red-500"
                                    }`}
                                />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stat.value}</div>
                                <div className="flex items-center gap-2 mt-1">
                                    <span
                                        className={`text-xs font-medium ${
                                            stat.trend === "up"
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
                {/* 市场资讯 */}
                <Card>
                    <CardHeader>
                        <CardTitle>市场资讯</CardTitle>
                        <CardDescription>
                            最新的行业动态和市场信息
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {marketNews.map((news) => (
                                <div
                                    key={news.id}
                                    className="border-b pb-3 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="space-y-1 flex-1">
                                            <p className="font-medium text-sm leading-tight">
                                                {news.title}
                                            </p>
                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <span>{news.source}</span>
                                                <span>•</span>
                                                <span>{news.time}</span>
                                            </div>
                                        </div>
                                        <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded shrink-0">
                                            {news.category}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* 价格预测 */}
                <Card>
                    <CardHeader>
                        <CardTitle>价格预测</CardTitle>
                        <CardDescription>
                            下周价格走势预测（AI 分析）
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {priceForecasts.map((forecast) => (
                                <div
                                    key={forecast.material}
                                    className="border-b pb-3 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-center justify-between mb-1">
                                        <p className="font-medium">{forecast.material}</p>
                                        <span
                                            className={`text-xs px-2 py-0.5 rounded ${
                                                forecast.trend === "上涨"
                                                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                                                    : forecast.trend === "下跌"
                                                    ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                                                    : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                                            }`}
                                        >
                                            {forecast.trend}
                                        </span>
                                    </div>
                                    <div className="text-sm space-y-1">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">当前价格:</span>
                                            <span className="font-medium">{forecast.current}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">预测区间:</span>
                                            <span className="font-medium">{forecast.nextWeek}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">预测置信度:</span>
                                            <span className="text-xs">{forecast.confidence}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* 角色特定功能提示 */}
            {user?.role === "manager" && (
                <Card className="border-purple-200 bg-purple-50/50 dark:border-purple-900 dark:bg-purple-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                            经理功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">
                            ✅ 查看实时市场价格和趋势分析
                        </p>
                        <p className="text-sm">
                            ✅ 使用市场分析师 Agent 进行深度分析
                        </p>
                        <p className="text-sm">
                            ✅ 上传市场报告并提取关键信息
                        </p>
                        <p className="text-sm">
                            ✅ 采购决策支持和成本预测
                        </p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 切换到"市场分析师"Agent 询问"本季度铁矿石价格走势如何？"
                        </p>
                    </CardContent>
                </Card>
            )}

            {user?.role === "admin" && (
                <Card className="border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <DollarSign className="h-5 w-5 text-red-600 dark:text-red-400" />
                            管理员功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">
                            ✅ 配置市场数据源和更新频率
                        </p>
                        <p className="text-sm">
                            ✅ 管理市场分析报告库
                        </p>
                        <p className="text-sm">
                            ✅ 导出市场数据和分析报告
                        </p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 可在系统管理面板配置外部市场数据接口
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* 占位提示 */}
            <Card className="border-dashed">
                <CardHeader>
                    <CardTitle>🚧 功能开发中</CardTitle>
                    <CardDescription>
                        市场分析功能正在开发中，敬请期待...
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">
                        此页面将包含：价格趋势图表、市场情报聚合、AI 价格预测、供应商对比分析等功能
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
