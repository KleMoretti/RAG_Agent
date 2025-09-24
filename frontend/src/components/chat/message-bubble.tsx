import { cn } from "@/lib/utils";
import { MessageContent } from "./message-content";

export type MessageBubbleProps = {
  role: "user" | "assistant";
  content: string;
  time?: number;
};

export function MessageBubble({ role, content, time }: MessageBubbleProps) {
  const isUser = role === "user";
  const ts = time ? new Date(time) : null;
  const timeText = ts
    ? ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : "";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-xl px-3 py-2 text-sm leading-relaxed",
          isUser
            ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
            : "border border-[var(--border)] bg-[var(--card)] text-[var(--foreground)]"
        )}
        style={{ boxShadow: "var(--shadow-sm)" }}
      >
        <MessageContent text={content} />
        {timeText && (
          <div
            className={cn(
              "mt-1 text-[10px]",
              isUser
                ? "opacity-80"
                : "text-[color-mix(in_oklch,var(--foreground),transparent_40%)]"
            )}
          >
            {timeText}
          </div>
        )}
      </div>
    </div>
  );
}
