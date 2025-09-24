"use client";
import { useEffect } from "react";

// 动态按主题注入 highlight.js 的样式，避免在 CSS 中静态导入导致的冲突。
export function ThemeStylesController() {
  useEffect(() => {
    const key = "hljs-theme-link";
    const ensure = (href: string) => {
      let link = document.getElementById(key) as HTMLLinkElement | null;
      if (!link) {
        link = document.createElement("link");
        link.id = key;
        link.rel = "stylesheet";
        document.head.appendChild(link);
      }
      if (link.href !== href) link.href = href;
    };

    const update = () => {
      const dark = document.documentElement.classList.contains("dark");
      const base =
        "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/";
      const href = dark
        ? `${base}github-dark.min.css`
        : `${base}github.min.css`;
      ensure(href);
    };

    // 初始注入
    update();

    // 监听主题切换（通过监控 html.className 变化）
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
    return () => observer.disconnect();
  }, []);

  return null;
}
