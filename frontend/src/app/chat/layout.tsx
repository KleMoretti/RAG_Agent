"use client";
import {useConversations, useConversationsContext} from "@/lib/conversations";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Plus, MessageSquare } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { list, currentId, select, create } = useConversationsContext();
  const current = list.find((c) => c.id === currentId) || null;

  return (
    <div className="flex h-[100dvh]">
      {/* Sidebar */}
      <aside className="w-[280px] shrink-0 border-r border-[var(--sidebar-border)] bg-[var(--sidebar)]">
        <div className="px-3 py-3 space-y-2">
          <div className="flex items-center justify-between gap-2">
            <div className="text-sm font-medium text-[var(--sidebar-foreground)]">
              会话
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <Button
                size="sm"
                variant="outline"
                onClick={() => create("新会话")}
                title="新建会话"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="truncate text-xs text-[color-mix(in_oklch,var(--sidebar-foreground),transparent_35%)]">
            {current ? current.title : "未选择会话"}
          </div>
        </div>
        <Separator />
        <div className="overflow-y-auto p-2 space-y-1">
          {list.length === 0 && (
            <div className="px-3 py-2 text-xs text-[color-mix(in_oklch,var(--sidebar-foreground),transparent_40%)]">
              暂无会话，点击右上角新建
            </div>
          )}
          {list.map((c) => (
            <button
              key={c.id}
              onClick={() => select(c.id)}
              className={`flex w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors ${
                currentId === c.id
                  ? "bg-[var(--sidebar-accent)] text-[var(--sidebar-accent-foreground)]"
                  : "hover:bg-[var(--sidebar-accent)]/60"
              }`}
              title={new Date(c.updatedAt).toLocaleString()}
            >
              <MessageSquare className="h-4 w-4" />
              <span className="truncate">{c.title}</span>
            </button>
          ))}
        </div>
      </aside>

      {/* Content */}
      <main className="flex-1 overflow-hidden">
        <div className="mx-auto h-full max-w-4xl px-4">{children}</div>
      </main>
    </div>
  );
}
