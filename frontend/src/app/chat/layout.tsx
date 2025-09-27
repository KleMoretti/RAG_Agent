"use client";
import { useConversationsContext } from "@/lib/conversations";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Plus, MessageSquare, Pencil, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import {ThemeToggle} from "@/components/theme-toggle";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { list, currentId, select, create, rename, remove } = useConversationsContext();
  const current = list.find((c) => c.id === currentId) || null;
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("user");
    if (raw) {
      try {
        const u = JSON.parse(raw);
        setUserRole(u?.role || null);
      } catch {}
    }
  }, []);

  function createWithPrompt() {
    const t = window.prompt("输入会话名称", "新会话");
    if (t === null) return;
    const name = t.trim() || "新会话";
    create(name);
  }

  function renameWithPrompt(id: string, currentTitle: string) {
    const t = window.prompt("重命名会话", currentTitle);
    if (t === null) return;
    const name = t.trim();
    if (name) rename(id, name);
  }

  function deleteConversation(id: string) {
    const ok = window.confirm("确定要删除该会话吗？此操作不可恢复。");
    if (!ok) return;
    remove(id);
    // 清理该会话的本地消息
    try {
      localStorage.removeItem("rag_messages_" + id);
    } catch {}
  }

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
              {userRole && (
                <span className="text-xs text-[var(--sidebar-foreground)]">角色: {userRole}</span>
              )}
              <ThemeToggle />
              <Button
                size="sm"
                variant="outline"
                onClick={createWithPrompt}
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
            <div
              key={c.id}
              className={`group flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
                currentId === c.id
                  ? "bg-[var(--sidebar-accent)] text-[var(--sidebar-accent-foreground)]"
                  : "hover:bg-[var(--sidebar-accent)]/60"
              }`}
              title={new Date(c.updatedAt).toLocaleString()}
            >
              <button
                onClick={() => select(c.id)}
                className="flex min-w-0 flex-1 items-center gap-2 text-left"
              >
                <MessageSquare className="h-4 w-4" />
                <span className="truncate">{c.title}</span>
              </button>
              <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100">
                <Button
                  size="sm"
                  variant="ghost"
                  title="重命名"
                  onClick={(e) => {
                    e.stopPropagation();
                    renameWithPrompt(c.id, c.title);
                  }}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  title="删除"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteConversation(c.id);
                  }}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
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