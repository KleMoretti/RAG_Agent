"use client";

import * as React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { cn } from "@/lib/utils";

interface MarkdownContentProps {
    content: string;
    className?: string;
}

export function MarkdownContent({ content, className }: MarkdownContentProps) {
    return (
        <div
            className={cn(
                "prose prose-sm dark:prose-invert max-w-none",
                className,
            )}
        >
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={{
                    // 标题样式
                    h1: ({ children, ...props }) => (
                        <h1 className="text-xl font-bold mt-4 mb-2" {...props}>
                            {children}
                        </h1>
                    ),
                    h2: ({ children, ...props }) => (
                        <h2 className="text-lg font-bold mt-3 mb-2" {...props}>
                            {children}
                        </h2>
                    ),
                    h3: ({ children, ...props }) => (
                        <h3
                            className="text-base font-semibold mt-2 mb-1"
                            {...props}
                        >
                            {children}
                        </h3>
                    ),
                    h4: ({ children, ...props }) => (
                        <h4
                            className="text-sm font-semibold mt-2 mb-1"
                            {...props}
                        >
                            {children}
                        </h4>
                    ),
                    h5: ({ children, ...props }) => (
                        <h5
                            className="text-sm font-medium mt-1 mb-1"
                            {...props}
                        >
                            {children}
                        </h5>
                    ),
                    h6: ({ children, ...props }) => (
                        <h6
                            className="text-xs font-medium mt-1 mb-1"
                            {...props}
                        >
                            {children}
                        </h6>
                    ),

                    // 段落样式
                    p: ({ children, ...props }) => (
                        <p
                            className="mb-2 last:mb-0 leading-relaxed"
                            {...props}
                        >
                            {children}
                        </p>
                    ),

                    // 列表样式
                    ul: ({ children, ...props }) => (
                        <ul
                            className="list-disc list-inside mb-2 space-y-1"
                            {...props}
                        >
                            {children}
                        </ul>
                    ),
                    ol: ({ children, ...props }) => (
                        <ol
                            className="list-decimal list-inside mb-2 space-y-1"
                            {...props}
                        >
                            {children}
                        </ol>
                    ),
                    li: ({ children, ...props }) => (
                        <li className="leading-relaxed" {...props}>
                            {children}
                        </li>
                    ),

                    // 代码块样式
                    code: (props) => {
                        const { children, className, ...rest } = props;
                        const inline = !className?.includes("language-");
                        const match = /language-(\w+)/.exec(className || "");
                        const language = match ? match[1] : "";

                        if (!inline && className) {
                            return (
                                <div className="relative group">
                                    {language && (
                                        <div className="absolute right-2 top-2 text-xs text-muted-foreground bg-background/50 px-2 py-1 rounded">
                                            {language}
                                        </div>
                                    )}
                                    <pre className="bg-muted p-3 rounded-md overflow-x-auto mb-2 mt-2">
                                        <code className={className} {...rest}>
                                            {children}
                                        </code>
                                    </pre>
                                </div>
                            );
                        }

                        return (
                            <code
                                className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono"
                                {...rest}
                            >
                                {children}
                            </code>
                        );
                    },

                    // 引用块样式
                    blockquote: ({ children, ...props }) => (
                        <blockquote
                            className="border-l-4 border-primary pl-4 py-1 my-2 italic text-muted-foreground"
                            {...props}
                        >
                            {children}
                        </blockquote>
                    ),

                    // 表格样式
                    table: ({ children, ...props }) => (
                        <div className="overflow-x-auto my-2">
                            <table
                                className="min-w-full border-collapse border border-border"
                                {...props}
                            >
                                {children}
                            </table>
                        </div>
                    ),
                    thead: ({ children, ...props }) => (
                        <thead className="bg-muted" {...props}>
                            {children}
                        </thead>
                    ),
                    tbody: ({ children, ...props }) => (
                        <tbody {...props}>{children}</tbody>
                    ),
                    tr: ({ children, ...props }) => (
                        <tr className="border-b border-border" {...props}>
                            {children}
                        </tr>
                    ),
                    th: ({ children, ...props }) => (
                        <th
                            className="px-3 py-2 text-left font-semibold text-sm"
                            {...props}
                        >
                            {children}
                        </th>
                    ),
                    td: ({ children, ...props }) => (
                        <td className="px-3 py-2 text-sm" {...props}>
                            {children}
                        </td>
                    ),

                    // 链接样式
                    a: ({ children, ...props }) => (
                        <a
                            className="text-primary hover:underline"
                            target="_blank"
                            rel="noopener noreferrer"
                            {...props}
                        >
                            {children}
                        </a>
                    ),

                    // 分割线样式
                    hr: ({ ...props }) => (
                        <hr className="my-4 border-border" {...props} />
                    ),

                    // 强调样式
                    strong: ({ children, ...props }) => (
                        <strong className="font-bold" {...props}>
                            {children}
                        </strong>
                    ),
                    em: ({ children, ...props }) => (
                        <em className="italic" {...props}>
                            {children}
                        </em>
                    ),

                    // 删除线样式
                    del: ({ children, ...props }) => (
                        <del
                            className="line-through text-muted-foreground"
                            {...props}
                        >
                            {children}
                        </del>
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
}
