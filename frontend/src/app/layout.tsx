import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { ThemeStylesController } from "@/components/theme-styles-controller";

export const metadata: Metadata = {
  title: "RAG Agent UI",
  description: "A modern UI for RAG Agent",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={`antialiased`}>
        <ThemeStylesController />
        {children}
        <Toaster />
      </body>
    </html>
  );
}
