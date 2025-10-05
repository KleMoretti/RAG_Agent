"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function HomePage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    // 如果用户已登录，重定向到仪表板
    if (isAuthenticated) {
      router.replace("/dashboard");
    } else {
      // 如果用户未登录，重定向到登录页面
      router.replace("/login");
    }
  }, [isAuthenticated, router]);

  // 显示加载状态，避免闪烁
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-secondary dark:from-background dark:to-card">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">正在跳转...</p>
      </div>
    </div>
  );
}
