"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuthStore } from "@/store/authStore";
import { useUIStore } from "@/store/uiStore";
import { useTheme } from "next-themes";
import { toast } from "sonner";
import { Loader2, User, Lock, Palette, Globe } from "lucide-react";
import { userApi } from "@/lib/api/user";

// 用户信息表单验证
const profileSchema = z.object({
    username: z
        .string()
        .min(3, "用户名至少3个字符")
        .max(20, "用户名最多20个字符"),
    email: z.string().email("请输入有效的邮箱地址").optional().or(z.literal("")),
});

// 密码修改表单验证
const passwordSchema = z
    .object({
        currentPassword: z.string().min(1, "请输入当前密码"),
        newPassword: z
            .string()
            .min(6, "新密码至少6个字符")
            .max(50, "新密码最多50个字符"),
        confirmPassword: z.string().min(1, "请确认新密码"),
    })
    .refine((data) => data.newPassword === data.confirmPassword, {
        message: "两次输入的密码不一致",
        path: ["confirmPassword"],
    });

type ProfileFormValues = z.infer<typeof profileSchema>;
type PasswordFormValues = z.infer<typeof passwordSchema>;

interface SettingsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function SettingsDialog({ open, onOpenChange }: SettingsDialogProps) {
    const { user, setUser } = useAuthStore();
    const { language, setLanguage } = useUIStore();
    const { theme, setTheme } = useTheme();
    const [activeTab, setActiveTab] = React.useState("profile");

    // 用户信息表单
    const profileForm = useForm<ProfileFormValues>({
        resolver: zodResolver(profileSchema),
        defaultValues: {
            username: user?.username || "",
            email: user?.email || "",
        },
    });

    // 密码修改表单
    const passwordForm = useForm<PasswordFormValues>({
        resolver: zodResolver(passwordSchema),
        defaultValues: {
            currentPassword: "",
            newPassword: "",
            confirmPassword: "",
        },
    });

    // 更新用户信息
    const handleProfileSubmit = async (data: ProfileFormValues) => {
        try {
            const updatedUser = await userApi.updateProfile({
                username: data.username,
                email: data.email || undefined,
            });
            
            // 更新本地用户状态
            setUser(updatedUser);
            
            toast.success("用户信息更新成功");
        } catch (error: any) {
            const errorMessage =
                error?.response?.data?.detail || "更新失败，请稍后重试";
            toast.error(errorMessage);
            console.error("Profile update error:", error);
        }
    };

    // 修改密码
    const handlePasswordSubmit = async (data: PasswordFormValues) => {
        try {
            await userApi.changePassword({
                current_password: data.currentPassword,
                new_password: data.newPassword,
            });
            
            toast.success("密码修改成功，请重新登录");
            passwordForm.reset();
            
            // 3秒后关闭对话框
            setTimeout(() => {
                onOpenChange(false);
            }, 1500);
        } catch (error: any) {
            const errorMessage =
                error?.response?.data?.detail || "密码修改失败，请检查当前密码是否正确";
            toast.error(errorMessage);
            console.error("Password change error:", error);
        }
    };

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

    // 当对话框打开时，重置表单数据为最新用户信息
    React.useEffect(() => {
        if (open && user) {
            profileForm.reset({
                username: user.username || "",
                email: user.email || "",
            });
        }
    }, [open, user, profileForm]);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="text-2xl font-bold">
                        个人设置
                    </DialogTitle>
                    <DialogDescription>
                        管理您的账户设置和偏好
                    </DialogDescription>
                </DialogHeader>

                <Tabs
                    value={activeTab}
                    onValueChange={setActiveTab}
                    className="w-full"
                >
                    <TabsList className="grid w-full grid-cols-4">
                        <TabsTrigger value="profile" className="gap-2">
                            <User className="size-4" />
                            <span className="hidden sm:inline">个人信息</span>
                        </TabsTrigger>
                        <TabsTrigger value="security" className="gap-2">
                            <Lock className="size-4" />
                            <span className="hidden sm:inline">安全设置</span>
                        </TabsTrigger>
                        <TabsTrigger value="appearance" className="gap-2">
                            <Palette className="size-4" />
                            <span className="hidden sm:inline">外观</span>
                        </TabsTrigger>
                        <TabsTrigger value="language" className="gap-2">
                            <Globe className="size-4" />
                            <span className="hidden sm:inline">语言</span>
                        </TabsTrigger>
                    </TabsList>

                    {/* 个人信息 Tab */}
                    <TabsContent value="profile" className="space-y-4">
                        <Form {...profileForm}>
                            <form
                                onSubmit={profileForm.handleSubmit(
                                    handleProfileSubmit,
                                )}
                                className="space-y-4"
                            >
                                <FormField
                                    control={profileForm.control}
                                    name="username"
                                    render={({ field }: { field: any }) => (
                                        <FormItem>
                                            <FormLabel>用户名</FormLabel>
                                            <FormControl>
                                                <Input
                                                    placeholder="请输入用户名"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormDescription>
                                                您在系统中显示的名称
                                            </FormDescription>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={profileForm.control}
                                    name="email"
                                    render={({ field }: { field: any }) => (
                                        <FormItem>
                                            <FormLabel>邮箱地址（可选）</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="email"
                                                    placeholder="请输入邮箱地址"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormDescription>
                                                用于接收系统通知和密码重置
                                            </FormDescription>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <div className="flex items-center gap-2 pt-4">
                                    <Label className="text-sm text-muted-foreground">
                                        角色:
                                    </Label>
                                    <span className="text-sm font-medium">
                                        {user?.role === "admin"
                                            ? "管理员"
                                            : user?.role === "manager"
                                              ? "技术经理"
                                              : user?.role === "technician"
                                                ? "技术员"
                                                : "用户"}
                                    </span>
                                </div>

                                <Button
                                    type="submit"
                                    disabled={profileForm.formState.isSubmitting}
                                    className="w-full"
                                >
                                    {profileForm.formState.isSubmitting && (
                                        <Loader2 className="mr-2 size-4 animate-spin" />
                                    )}
                                    保存更改
                                </Button>
                            </form>
                        </Form>
                    </TabsContent>

                    {/* 安全设置 Tab */}
                    <TabsContent value="security" className="space-y-4">
                        <Form {...passwordForm}>
                            <form
                                onSubmit={passwordForm.handleSubmit(
                                    handlePasswordSubmit,
                                )}
                                className="space-y-4"
                            >
                                <FormField
                                    control={passwordForm.control}
                                    name="currentPassword"
                                    render={({ field }: { field: any }) => (
                                        <FormItem>
                                            <FormLabel>当前密码</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="password"
                                                    placeholder="请输入当前密码"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={passwordForm.control}
                                    name="newPassword"
                                    render={({ field }: { field: any }) => (
                                        <FormItem>
                                            <FormLabel>新密码</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="password"
                                                    placeholder="请输入新密码"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormDescription>
                                                密码长度至少6个字符
                                            </FormDescription>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={passwordForm.control}
                                    name="confirmPassword"
                                    render={({ field }: { field: any }) => (
                                        <FormItem>
                                            <FormLabel>确认新密码</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="password"
                                                    placeholder="请再次输入新密码"
                                                    {...field}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <Button
                                    type="submit"
                                    disabled={passwordForm.formState.isSubmitting}
                                    className="w-full"
                                >
                                    {passwordForm.formState.isSubmitting && (
                                        <Loader2 className="mr-2 size-4 animate-spin" />
                                    )}
                                    修改密码
                                </Button>
                            </form>
                        </Form>
                    </TabsContent>

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

