"use client";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
//
//
import { MessageBubble } from "@/components/chat/message-bubble";
import {
  chat,
  type ChatResponse,
  type ReasoningStep as APIStep,
} from "@/lib/api";
//
import { useConversations } from "@/lib/conversations";
import { ReasoningPanel } from "@/components/reasoning-panel";

type Message = { role: "user" | "assistant"; content: string };
const LS_MESSAGES_PREFIX = "rag_messages_";

function readConvMessages(id: string): Message[] {
  try {
    const raw = localStorage.getItem(LS_MESSAGES_PREFIX + id);
    if (!raw) return [];
    const arr = JSON.parse(raw) as Message[];
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

function writeConvMessages(id: string, list: Message[]) {
  localStorage.setItem(LS_MESSAGES_PREFIX + id, JSON.stringify(list));
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const { currentId, create } = useConversations();
  const listRef = useRef<HTMLDivElement>(null);
  const [lastSteps, setLastSteps] = useState<APIStep[] | undefined>([]);

  // 切换会话时，加载该会话消息；无会话则清空
  useEffect(() => {
    if (currentId) {
      const data = readConvMessages(currentId);
      setMessages(data);
    } else {
      setMessages([]);
    }
    setLastSteps([]);
  }, [currentId]);

  useEffect(() => {
    listRef.current?.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text) return;
  const optimistic: Message = { role: "user", content: text };
    // 如果当前没有会话，创建一个
    const sid = currentId ?? create("新会话");
    setMessages((m) => {
      const next: Message[] = [...m, optimistic];
      writeConvMessages(sid, next);
      return next;
    });
    setInput("");
    setLoading(true);
    try {
      const res: ChatResponse = await chat({ message: text, session_id: sid });
      setMessages((m) => {
        const next: Message[] = [
          ...m,
          { role: "assistant" as const, content: res.response },
        ];
        writeConvMessages(sid, next);
        return next;
      });
      setLastSteps(res.reasoning_steps || []);
  // session is managed in sidebar hook
    } catch (e) {
      setMessages((m) => {
        const next: Message[] = [
          ...m,
          {
            role: "assistant" as const,
            content: `请求失败，请稍后再试。${(e as Error).message}`,
          },
        ];
        writeConvMessages(sid, next);
        return next;
      });
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  return (
    <div className="flex h-[calc(100dvh-2rem)] flex-col py-4">
      {/* 消息列表，占据剩余空间，独立滚动 */}
      <div ref={listRef} className="flex-1 overflow-y-auto pr-2">
        <div className="space-y-3">
          {messages.length === 0 && (
            <p className="text-sm text-gray-500">开始对话吧～</p>
          )}
          {messages.map((m: Message, i: number) => (
            <MessageBubble key={i} role={m.role} content={m.content} />
          ))}
        </div>
      </div>

      {/* 底部固定区域：先 Reasoning，再输入框 */}
      <div className="sticky bottom-0 z-10 bg-[var(--background)] pt-3">
        <ReasoningPanel
          defaultOpen={false}
          steps={(lastSteps || []).map((s) => ({
            thought: s.thought,
            tool_name: s.tool_name ?? null,
            tool_input: s.tool_input ?? null,
          }))}
        />
        <div className="mt-3 flex gap-2">
          <Textarea
            placeholder="输入消息，Enter 发送，Shift+Enter 换行"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
          />
          <Button onClick={() => void send()} disabled={loading}>
            {loading ? "发送中..." : "发送"}
          </Button>
        </div>
      </div>
    </div>
  );
}
