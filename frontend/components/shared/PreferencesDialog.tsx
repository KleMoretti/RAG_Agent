"use client";

import * as React from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useUIStore } from "@/store/uiStore";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import { Palette, Globe } from "lucide-react";

interface PreferencesDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function PreferencesDialog({ open, onOpenChange }: PreferencesDialogProps) {
    const { language, setLanguage } = useUIStore();
    const { theme, setTheme } = useTheme();
    const [activeTab, setActiveTab] = React.useState("appearance");

    // 主题切换
    const handleThemeChange = (value: string) => {
        setTheme(value);
        toast.success(`已切换到${value === "light" ? "浅色" : value === "dark" ? "深色" : "系统"}主题`);
    };

    // 快速切换主题
    const handleToggleTheme = () => {
        const newTheme = theme === "light" ? "dark" : "light";
        setTheme(newTheme);
        toast.success(`已切换到${newTheme === "light" ? "浅色" : "深色"}主题`);
    };

    // 语言切换
    const handleLanguageChange = (value: string) => {
        setLanguage(value as "zh-CN" | "en-US");
        toast.success(`语言已切换为${value === "zh-CN" ? "中文" : "English"}`);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="text-2xl font-bold">
                        系统设置
                    </DialogTitle>
                    <DialogDescription>
                        管理系统的外观和语言偏好
                    </DialogDescription>
                </DialogHeader>

                <Tabs
                    value={activeTab}
                    onValueChange={setActiveTab}
                    className="w-full"
                >
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="appearance" className="gap-2">
                            <Palette className="size-4" />
                            <span className="hidden sm:inline">外观</span>
                        </TabsTrigger>
                        <TabsTrigger value="language" className="gap-2">
                            <Globe className="size-4" />
                            <span className="hidden sm:inline">语言</span>
                        </TabsTrigger>
                    </TabsList>

                    {/* 外观 Tab */}
                    <TabsContent value="appearance" className="space-y-4">
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-lg font-medium mb-4">
                                    主题模式
                                </h3>
                                <RadioGroup
                                    value={theme}
                                    onValueChange={handleThemeChange}
                                >
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem
                                            value="light"
                                            id="light"
                                        />
                                        <Label htmlFor="light" className="flex items-center gap-2 cursor-pointer">
                                            <span>浅色模式</span>
                                        </Label>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem value="dark" id="dark" />
                                        <Label htmlFor="dark" className="flex items-center gap-2 cursor-pointer">
                                            <span>深色模式</span>
                                            <span className="text-xs text-muted-foreground">
                                                （护眼）
                                            </span>
                                        </Label>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem value="system" id="system" />
                                        <Label htmlFor="system" className="flex items-center gap-2 cursor-pointer">
                                            <span>跟随系统</span>
                                            <span className="text-xs text-muted-foreground">
                                                （推荐）
                                            </span>
                                        </Label>
                                    </div>
                                </RadioGroup>
                            </div>

                            <div className="pt-4 border-t">
                                <Button
                                    variant="outline"
                                    onClick={handleToggleTheme}
                                    className="w-full"
                                >
                                    快速切换主题（浅色/深色）
                                </Button>
                                <p className="text-xs text-muted-foreground mt-2 text-center">
                                    当前主题：{theme === "light" ? "浅色" : theme === "dark" ? "深色" : "跟随系统"}
                                </p>
                            </div>
                        </div>
                    </TabsContent>

                    {/* 语言 Tab */}
                    <TabsContent value="language" className="space-y-4">
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-lg font-medium mb-4">
                                    界面语言
                                </h3>
                                <RadioGroup
                                    value={language}
                                    onValueChange={handleLanguageChange}
                                >
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem
                                            value="zh-CN"
                                            id="zh-CN"
                                        />
                                        <Label htmlFor="zh-CN" className="flex items-center gap-2 cursor-pointer">
                                            <span>简体中文</span>
                                            <span className="text-xs text-muted-foreground">
                                                （默认）
                                            </span>
                                        </Label>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <RadioGroupItem
                                            value="en-US"
                                            id="en-US"
                                        />
                                        <Label htmlFor="en-US" className="flex items-center gap-2 cursor-pointer">
                                            <span>English (US)</span>
                                        </Label>
                                    </div>
                                </RadioGroup>
                                <p className="text-sm text-muted-foreground mt-4">
                                    💡 提示：语言切换后部分内容需要刷新页面才能生效
                                </p>
                            </div>
                        </div>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}

