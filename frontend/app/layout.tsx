import type { Metadata } from "next";
import "./globals.css";
import { IBM_Plex_Sans, Michroma } from "next/font/google";
import { cn } from "@/lib/utils";
import { QueryProvider } from "@/components/shared/QueryProvider";

const ibmPlexSans = IBM_Plex_Sans({
  weight: ["100", "200", "300", "400", "500", "600", "700"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-plex-sans",
});

const michroma = Michroma({
  weight: "400",
  subsets: ["latin"],
  display: "swap",
  variable: "--font-michroma",
});

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
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          ibmPlexSans.variable,
          michroma.variable
        )}
      >
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
