"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Bot, Loader2 } from "lucide-react";

interface StreamingMessageProps {
  content: string;
  isGenerating?: boolean;
}

export function StreamingMessage({ content, isGenerating = true }: StreamingMessageProps) {
  return (
    <div className="flex gap-3 justify-start">
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="bg-primary text-primary-foreground">
          <Bot className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>

      <div className="flex flex-col gap-2 max-w-[80%]">
        <Card className="p-3 bg-muted">
          <div className="whitespace-pre-wrap break-words text-sm">
            {content}
            {isGenerating && (
              <span className="inline-block ml-1 animate-pulse">▊</span>
            )}
          </div>
        </Card>

        {isGenerating && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>AI 正在生成回答...</span>
          </div>
        )}
      </div>
    </div>
  );
}
