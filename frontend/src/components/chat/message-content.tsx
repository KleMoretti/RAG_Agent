"use client"
import React, { useMemo, useState } from "react"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"
import rehypeSanitize, { defaultSchema, type Options as SanitizeOptions } from "rehype-sanitize"
import { Button } from "@/components/ui/button"

export function MessageContent({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch {}
  }

  const components: Components = useMemo(() => {
    const extractText = (node: unknown): string => {
      if (typeof node === "string") return node
      if (Array.isArray(node)) return (node as unknown[]).map(extractText).join("")
      if (React.isValidElement(node)) {
        const props = (node as React.ReactElement).props as { children?: unknown }
        return extractText(props.children)
      }
      return ""
    }

    return {
      pre: (p) => {
        const { children } = p as { children?: React.ReactNode }
        const raw = extractText(children)
        return (
          <pre className="relative my-2 overflow-x-auto rounded-lg">
            {children}
            <Button
              size="sm"
              variant="outline"
              className="absolute right-2 top-2 h-7 px-2 text-xs"
              onClick={() => navigator.clipboard.writeText(raw)}
              title="复制代码"
            >
              复制
            </Button>
          </pre>
        )
      },
      code: (p) => {
        const { inline, className, children } = p as {
          inline?: boolean
          className?: string
          children?: React.ReactNode
        }
        if (inline) {
          return (
            <code className="rounded bg-[color-mix(in_oklch,var(--muted),black_10%)] px-1 py-0.5">{children}</code>
          )
        }
        // 非内联的代码块由自定义 pre 渲染器包裹，这里仅传递 className 以便语法高亮生效
        return <code className={className ?? ""}>{children}</code>
      },
    }
  }, [])

  const sanitize = useMemo<SanitizeOptions>(() => {
    const base = defaultSchema as SanitizeOptions
    const attributes = {
      ...(base.attributes || {}),
      code: [...(base.attributes?.code || []), ["className"], ["data-language"]],
      pre: [...(base.attributes?.pre || []), ["className"]],
    } as NonNullable<SanitizeOptions["attributes"]>
    return { ...base, attributes }
  }, [])

  return (
    <div className="group relative">
      <div className="markdown-body">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[[rehypeSanitize, sanitize], rehypeHighlight]}
          components={components}
        >
          {text}
        </ReactMarkdown>
      </div>
      <Button
        size="sm"
        variant="ghost"
        className="invisible absolute -right-2 -top-2 h-7 px-2 text-xs group-hover:visible"
        onClick={onCopy}
        title="复制消息"
      >
        {copied ? "已复制" : "复制"}
      </Button>
    </div>
  )
}
