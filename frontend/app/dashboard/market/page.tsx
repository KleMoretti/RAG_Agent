"use client";

import { useAuthStore } from "@/store/authStore";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { LineChart, TrendingUp, TrendingDown, DollarSign, BarChart3, Upload, RefreshCw, AlertCircle } from "lucide-react";
import { roleDisplayNames } from "@/lib/permissions";
import { useEffect, useState, useCallback } from "react";
import { getMarketSummary, getNews, getTrendAnalysis, batchUploadPrices } from "@/lib/api/market";
import type { MarketSummary, MarketNews, TrendAnalysis } from "@/lib/api/market";
import { toast } from "sonner";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function MarketPage() {
    const { user } = useAuthStore();
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [summary, setSummary] = useState<MarketSummary | null>(null);
    const [news, setNews] = useState<MarketNews[]>([]);
    const [trends, setTrends] = useState<TrendAnalysis[]>([]);
    const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
    const [uploadFile, setUploadFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);

    // 加载市场数据
    const loadMarketData = useCallback(async () => {
        try {
            setLoading(true);
            const [summaryData, newsData, trendsData] = await Promise.all([
                getMarketSummary(),
                getNews({ limit: 10 }),
                getTrendAnalysis(["铁矿石", "螺纹钢", "焦炭", "废钢"]),
            ]);
            setSummary(summaryData);
            setNews(newsData);
            setTrends(trendsData);
        } catch (error) {
            console.error("加载市场数据失败:", error);
            toast.error("加载市场数据失败，显示模拟数据");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadMarketData();
    }, [loadMarketData]);

    // 刷新数据
    const handleRefresh = async () => {
        setRefreshing(true);
        await loadMarketData();
        setRefreshing(false);
        toast.success("数据已刷新");
    };

    // 处理文件上传
    const handleFileUpload = async () => {
        if (!uploadFile) {
            toast.error("请选择文件");
            return;
        }

        try {
            setUploading(true);
            const result = await batchUploadPrices(uploadFile);
            toast.success(result.message);
            setIsUploadDialogOpen(false);
            setUploadFile(null);
            // 重新加载数据
            await loadMarketData();
        } catch (error: any) {
            console.error("上传失败:", error);
            toast.error(error.response?.data?.detail || "上传失败");
        } finally {
            setUploading(false);
        }
    };

    // 使用真实数据或模拟数据
    const displayPrices = summary?.latest_prices.slice(0, 4) || [];
    const marketStats = displayPrices.length > 0
        ? displayPrices.map((p) => ({
              id: p.id,  // 传递唯一ID
              title: p.material_type,
              value: `¥${p.price}${p.unit || "/吨"}`,
              change: p.change_rate != null ? `${p.change_rate > 0 ? "+" : ""}${p.change_rate.toFixed(1)}%` : "N/A",
              trend: p.change_rate != null && p.change_rate > 0 ? ("up" as const) : ("down" as const),
              icon: p.change_rate != null && p.change_rate > 0 ? TrendingUp : TrendingDown,
              description: p.change_rate != null 
                  ? (p.change_rate > 0 ? "较上周上涨" : p.change_rate < 0 ? "较上周下跌" : "较上周持平")
                  : "暂无对比数据",
          }))
        : [
              {
                  id: 1,  // 模拟数据ID
                  title: "铁矿石价格",
                  value: "¥890/吨",
                  change: "+2.3%",
                  trend: "up" as const,
                  icon: TrendingUp,
                  description: "较上周上涨",
              },
              {
                  id: 2,
                  title: "螺纹钢价格",
                  value: "¥4,250/吨",
                  change: "-1.5%",
                  trend: "down" as const,
                  icon: TrendingDown,
                  description: "较上周下跌",
              },
              {
                  id: 3,
                  title: "焦炭价格",
                  value: "¥2,180/吨",
                  change: "+0.8%",
                  trend: "up" as const,
                  icon: TrendingUp,
                  description: "较上周上涨",
              },
              {
                  id: 4,
                  title: "废钢价格",
                  value: "¥2,650/吨",
                  change: "+3.2%",
                  trend: "up" as const,
                  icon: TrendingUp,
                  description: "较上周上涨",
              },
          ];

    // 显示新闻（真实数据或模拟数据）
    const displayNews = news.length > 0
        ? news.map((n) => ({
              id: n.id.toString(),
              title: n.title,
              source: n.source,
              time: new Date(n.publish_time).toLocaleString("zh-CN", {
                  month: "numeric",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
              }),
              category: n.category,
          }))
        : [
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

    // 显示趋势预测（真实数据或模拟数据）
    const displayForecasts = trends.length > 0
        ? trends.map((t) => ({
              material: t.material_type,
              current: `¥${t.current_price}/吨`,
              nextWeek: `¥${t.forecast_7d.min}-${t.forecast_7d.max}/吨`,
              trend: t.trend,
              confidence: t.confidence,
          }))
        : [
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

    const canManageMarket = user?.role === "admin" || user?.role === "manager";

    return (
        <div className="flex-1 space-y-6 p-8 overflow-y-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        市场分析
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
                        <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
                        刷新数据
                    </Button>
                    {canManageMarket && (
                        <Button
                            size="sm"
                            onClick={() => setIsUploadDialogOpen(true)}
                        >
                            <Upload className="h-4 w-4 mr-2" />
                            上传数据
                        </Button>
                    )}
                </div>
            </div>

            {/* 无数据提示 */}
            {!loading && displayPrices.length === 0 && (
                <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        暂无市场数据，显示模拟数据。请{canManageMarket ? "上传数据文件或" : ""}联系管理员配置数据源。
                    </AlertDescription>
                </Alert>
            )}

            {/* 价格统计卡片 */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {marketStats.map((stat, index) => {
                    const Icon = stat.icon;
                    return (
                        <Card key={stat.id || `stat-${index}`}>
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
                                <div className="text-2xl font-bold">
                                    {stat.value}
                                </div>
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
                            {displayNews.map((newsItem) => (
                                <div
                                    key={newsItem.id}
                                    className="border-b pb-3 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="space-y-1 flex-1">
                                            <p className="font-medium text-sm leading-tight">
                                                {newsItem.title}
                                            </p>
                                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                <span>{newsItem.source}</span>
                                                <span>•</span>
                                                <span>{newsItem.time}</span>
                                            </div>
                                        </div>
                                        <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded shrink-0">
                                            {newsItem.category}
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
                            {displayForecasts.map((forecast) => (
                                <div
                                    key={forecast.material}
                                    className="border-b pb-3 last:border-0 last:pb-0"
                                >
                                    <div className="flex items-center justify-between mb-1">
                                        <p className="font-medium">
                                            {forecast.material}
                                        </p>
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
                                            <span className="text-muted-foreground">
                                                当前价格:
                                            </span>
                                            <span className="font-medium">
                                                {forecast.current}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">
                                                预测区间:
                                            </span>
                                            <span className="font-medium">
                                                {forecast.nextWeek}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">
                                                预测置信度:
                                            </span>
                                            <span className="text-xs">
                                                {forecast.confidence}
                                            </span>
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
                        <p className="text-sm">✅ 查看实时市场价格和趋势分析</p>
                        <p className="text-sm">
                            ✅ 使用市场分析师 Agent 进行深度分析
                        </p>
                        <p className="text-sm">✅ 上传市场报告并提取关键信息</p>
                        <p className="text-sm">✅ 采购决策支持和成本预测</p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 切换到&ldquo;市场分析师&rdquo;Agent
                            询问&ldquo;本季度铁矿石价格走势如何？&rdquo;
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
                        <p className="text-sm">✅ 配置市场数据源和更新频率</p>
                        <p className="text-sm">✅ 管理市场分析报告库</p>
                        <p className="text-sm">✅ 导出市场数据和分析报告</p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 可上传Excel/CSV文件批量导入市场数据
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* 数据上传对话框 */}
            <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>上传市场数据</DialogTitle>
                        <DialogDescription>
                            支持 Excel (.xlsx, .xls) 和 CSV 格式。
                            <br />
                            文件应包含以下列: material_type, category, price, price_date
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg p-8 text-center">
                            <input
                                type="file"
                                accept=".xlsx,.xls,.csv"
                                onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                        setUploadFile(file);
                                    }
                                }}
                                className="hidden"
                                id="file-upload"
                            />
                            <label
                                htmlFor="file-upload"
                                className="cursor-pointer flex flex-col items-center space-y-2"
                            >
                                <Upload className="h-12 w-12 text-gray-400" />
                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                    点击选择文件或拖拽文件到这里
                                </span>
                                {uploadFile && (
                                    <span className="text-sm font-medium text-primary">
                                        {uploadFile.name}
                                    </span>
                                )}
                            </label>
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button
                                variant="outline"
                                onClick={() => {
                                    setIsUploadDialogOpen(false);
                                    setUploadFile(null);
                                }}
                            >
                                取消
                            </Button>
                            <Button
                                onClick={handleFileUpload}
                                disabled={!uploadFile || uploading}
                            >
                                {uploading ? "上传中..." : "上传"}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
