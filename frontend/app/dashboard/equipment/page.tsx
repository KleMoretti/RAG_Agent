"use client";

import { useAuthStore } from "@/store/authStore";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Wrench,
    AlertCircle,
    CheckCircle,
    Clock,
    TrendingUp,
} from "lucide-react";
import { roleDisplayNames } from "@/lib/permissions";

export default function EquipmentPage() {
    const { user } = useAuthStore();

    const equipmentStats = [
        {
            title: "设备总数",
            value: "156",
            icon: Wrench,
            description: "总设备数量",
            color: "text-blue-500",
        },
        {
            title: "运行中",
            value: "142",
            icon: CheckCircle,
            description: "正常运行设备",
            color: "text-green-500",
        },
        {
            title: "维护中",
            value: "8",
            icon: Clock,
            description: "计划维护设备",
            color: "text-yellow-500",
        },
        {
            title: "故障",
            value: "6",
            icon: AlertCircle,
            description: "需要维修设备",
            color: "text-red-500",
        },
    ];

    const recentIssues = [
        {
            id: "1",
            equipment: "冷轧机 #3",
            issue: "辊压力异常",
            severity: "高",
            status: "处理中",
            time: "2小时前",
        },
        {
            id: "2",
            equipment: "转炉 #2",
            issue: "温度传感器故障",
            severity: "中",
            status: "待处理",
            time: "4小时前",
        },
        {
            id: "3",
            equipment: "热轧机 #1",
            issue: "液压系统压力下降",
            severity: "中",
            status: "已完成",
            time: "昨天",
        },
    ];

    return (
        <div className="flex-1 space-y-6 p-8 overflow-y-auto">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        设备管理
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
            </div>

            {/* 设备统计卡片 */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {equipmentStats.map((stat) => {
                    const Icon = stat.icon;
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
                                <p className="text-xs text-muted-foreground">
                                    {stat.description}
                                </p>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* 最近故障/维护记录 */}
            <Card>
                <CardHeader>
                    <CardTitle>最近故障与维护</CardTitle>
                    <CardDescription>最近的设备问题和维护任务</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        {recentIssues.map((issue, index) => (
                            <div
                                key={issue.id}
                                className={`flex items-center justify-between p-3 rounded-lg transition-colors ${
                                    // 根据严重程度添加背景色
                                    issue.severity === "高"
                                        ? "bg-red-50/50 hover:bg-red-50 dark:bg-red-950/20 dark:hover:bg-red-950/30"
                                        : issue.severity === "中"
                                          ? "bg-yellow-50/50 hover:bg-yellow-50 dark:bg-yellow-950/20 dark:hover:bg-yellow-950/30"
                                          : index % 2 === 0
                                            ? "bg-muted/30 hover:bg-muted/50"
                                            : "hover:bg-muted/30"
                                }`}
                            >
                                {/* 左侧：设备名称 + 故障描述 + 时间（紧凑排列） */}
                                <div className="flex items-center gap-3 flex-1 min-w-0">
                                    {/* 设备名称 */}
                                    <div className="font-medium text-sm shrink-0">
                                        {issue.equipment}
                                    </div>
                                    
                                    {/* 分隔符 */}
                                    <div className="h-4 w-px bg-border shrink-0" />
                                    
                                    {/* 故障描述 */}
                                    <div className="text-sm text-muted-foreground truncate">
                                        {issue.issue}
                                    </div>
                                    
                                    {/* 时间 */}
                                    <div className="text-xs text-muted-foreground shrink-0 flex items-center gap-1">
                                        <Clock className="h-3 w-3" />
                                        {issue.time}
                                    </div>
                                </div>

                                {/* 右侧：严重程度 + 状态 */}
                                <div className="flex items-center gap-2 shrink-0">
                                    {/* 严重程度标签 */}
                                    <span
                                        className={`text-xs px-2 py-1 rounded-md font-medium ${
                                            issue.severity === "高"
                                                ? "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300"
                                                : issue.severity === "中"
                                                  ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300"
                                                  : "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300"
                                        }`}
                                    >
                                        {issue.severity}
                                    </span>
                                    
                                    {/* 状态标签 */}
                                    <span
                                        className={`text-sm font-medium px-3 py-1 rounded-md ${
                                            issue.status === "已完成"
                                                ? "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300"
                                                : issue.status === "处理中"
                                                  ? "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300"
                                                  : "bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300"
                                        }`}
                                    >
                                        {issue.status}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* 角色特定功能提示 */}
            {user?.role === "technician" && (
                <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                            技术员功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">✅ 查看设备状态和故障记录</p>
                        <p className="text-sm">
                            ✅ 使用设备诊断 Agent 进行故障排查
                        </p>
                        <p className="text-sm">✅ 查询设备维修手册和历史案例</p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 切换到&ldquo;设备诊断&rdquo;Agent
                            开始对话式故障诊断
                        </p>
                    </CardContent>
                </Card>
            )}

            {user?.role === "manager" && (
                <Card className="border-purple-200 bg-purple-50/50 dark:border-purple-900 dark:bg-purple-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                            经理功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">
                            ✅ 查看全部设备运行数据和分析报告
                        </p>
                        <p className="text-sm">✅ 设备升级投资决策支持</p>
                        <p className="text-sm">✅ 跨设备类型的综合分析</p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 使用 AI 分析设备维护成本和效率优化方案
                        </p>
                    </CardContent>
                </Card>
            )}

            {user?.role === "admin" && (
                <Card className="border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5 text-red-600 dark:text-red-400" />
                            管理员功能
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                        <p className="text-sm">✅ 全部设备管理权限</p>
                        <p className="text-sm">✅ 设备数据导入导出</p>
                        <p className="text-sm">✅ 系统配置和权限管理</p>
                        <p className="text-sm text-muted-foreground">
                            💡 提示: 可在系统管理面板配置设备监控参数
                        </p>
                    </CardContent>
                </Card>
            )}

            {/* 占位提示 */}
            <Card className="border-dashed">
                <CardHeader>
                    <CardTitle>🚧 功能开发中</CardTitle>
                    <CardDescription>
                        设备管理功能正在开发中，敬请期待...
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">
                        此页面将包含：设备列表、实时监控、维护计划、故障诊断等功能
                    </p>
                </CardContent>
            </Card>
        </div>
    );
}
