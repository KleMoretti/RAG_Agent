"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ChevronDown, ChevronUp, FileText, User, Bot } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/lib/types/api";
import { MarkdownContent } from "./MarkdownContent";

interface ChatMessageProps {
    message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
    const [showSources, setShowSources] = React.useState(false);
    const [showReasoning, setShowReasoning] = React.useState(false);

    const isUser = message.role === "user";
    const hasAttachments =
        message.attachments && message.attachments.length > 0;
    const hasSources = message.sources && message.sources.length > 0;
    const hasReasoning =
        message.reasoningSteps && message.reasoningSteps.length > 0;

    return (
        <div
            className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
        >
            {!isUser && (
                <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                        <Bot className="h-4 w-4" />
                    </AvatarFallback>
                </Avatar>
            )}

            <div
                className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}
            >
                <Card
                    className={`p-3 ${
                        isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                    }`}
                >
                    {isUser ? (
                        <div className="whitespace-pre-wrap break-words text-sm">
                            {message.content}
                        </div>
                    ) : (
                        <MarkdownContent
                            content={message.content}
                            className="text-sm"
                        />
                    )}

                    {/* 附件显示 */}
                    {hasAttachments && (
                        <div className="mt-2 pt-2 border-t border-border/50 space-y-1">
                            {message.attachments!.map((attachment, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center gap-2 text-xs opacity-80"
                                >
                                    <FileText className="h-3 w-3" />
                                    <span className="truncate">
                                        {attachment.fileName}
                                    </span>
                                    {attachment.fileSize && (
                                        <span className="text-xs opacity-60">
                                            (
                                            {(
                                                attachment.fileSize / 1024
                                            ).toFixed(1)}{" "}
                                            KB)
                                        </span>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </Card>

                {/* 来源显示 */}
                {!isUser && hasSources && (
                    <div className="w-full">
                        <button
                            onClick={() => setShowSources(!showSources)}
                            className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
                        >
                            {showSources ? (
                                <ChevronUp className="h-3 w-3" />
                            ) : (
                                <ChevronDown className="h-3 w-3" />
                            )}
                            <span>{message.sources!.length} 个来源</span>
                        </button>

                        {showSources && (
                            <div className="mt-2 space-y-2">
                                {message.sources!.map((source, idx) => (
                                    <Card
                                        key={idx}
                                        className="p-2 bg-background/50"
                                    >
                                        <div className="flex items-start gap-2">
                                            <FileText className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                                            <div className="flex-1 min-w-0">
                                                <div className="text-xs font-medium truncate">
                                                    {source.fileName}
                                                </div>
                                                {source.content && (
                                                    <div className="text-xs text-muted-foreground mt-1 line-clamp-2">
                                                        {source.content}
                                                    </div>
                                                )}
                                                {source.relevanceScore !==
                                                    undefined && (
                                                    <div className="text-xs text-muted-foreground mt-1">
                                                        相关度:{" "}
                                                        {(
                                                            source.relevanceScore *
                                                            100
                                                        ).toFixed(1)}
                                                        %
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* 推理步骤显示 */}
                {!isUser && hasReasoning && (
                    <div className="w-full">
                        <button
                            onClick={() => setShowReasoning(!showReasoning)}
                            className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
                        >
                            {showReasoning ? (
                                <ChevronUp className="h-3 w-3" />
                            ) : (
                                <ChevronDown className="h-3 w-3" />
                            )}
                            <span>
                                {message.reasoningSteps!.length} 个推理步骤
                            </span>
                        </button>

                        {showReasoning && (
                            <div className="mt-2 space-y-2">
                                {message.reasoningSteps!.map((step, idx) => (
                                    <Card
                                        key={idx}
                                        className="p-2 bg-background/50"
                                    >
                                        <div className="space-y-1">
                                            {step.thought && (
                                                <div className="text-xs text-foreground">
                                                    思考: {step.thought}
                                                </div>
                                            )}
                                            {step.toolName && (
                                                <div className="text-xs font-medium text-primary">
                                                    工具: {step.toolName}
                                                </div>
                                            )}
                                        </div>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            {isUser && (
                <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback className="bg-secondary text-secondary-foreground">
                        <User className="h-4 w-4" />
                    </AvatarFallback>
                </Avatar>
            )}
        </div>
    );
}
