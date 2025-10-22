import type { Metadata } from "next";
import "./globals.css";
import { cn } from "@/lib/utils";
import { QueryProvider } from "@/components/shared/QueryProvider";
import { ThemeProvider } from "@/components/shared/ThemeProvider";
import { Toaster } from "@/components/ui/sonner";

export const metadata: Metadata = {
    title: "钢铁行业 AI 决策中心 | Steel Industry AI Decision Hub",
    description:
        "钢铁制造智能决策支持系统 | Intelligent decision support system for steel manufacturing",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="zh-CN" suppressHydrationWarning>
            <body
                className={cn(
                    "min-h-screen bg-background font-sans antialiased",
                )}
            >
                <ThemeProvider
                    attribute="class"
                    defaultTheme="system"
                    enableSystem
                    disableTransitionOnChange
                >
                    <QueryProvider>{children}</QueryProvider>
                    <Toaster />
                </ThemeProvider>
            </body>
        </html>
    );
}
