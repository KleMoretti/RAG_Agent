import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/components/shared/QueryProvider";

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
    <html lang="zh-CN">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link 
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,100..700;1,100..700&display=swap" 
          rel="stylesheet" 
        />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
