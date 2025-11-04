"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { FileText, User, Bot } from "lucide-react";
import type { ChatMessage as ChatMessageType } from "@/lib/types/api";
import { MarkdownContent } from "./MarkdownContent";
import { ReasoningStepDisplay } from "./ReasoningStepDisplay";
import { SourceDisplay } from "./SourceDisplay";
import { DomainBoundaryAlert } from "./DomainBoundaryAlert";

interface ChatMessageProps {
    message: ChatMessageType;
    onSwitchAgent?: (agentId: string) => void;
}

export function ChatMessage({ message, onSwitchAgent }: ChatMessageProps) {
    const isUser = message.role === "user";
    const hasAttachments =
        message.attachments && message.attachments.length > 0;
    const hasSources = message.sources && message.sources.length > 0;
    const hasReasoning =
        message.reasoningSteps && message.reasoningSteps.length > 0;
    const isDomainCheckFailed = message.domain_check_failed === true;

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

                {/* 来源显示 - 使用新组件 */}
                {!isUser && hasSources && (
                    <SourceDisplay sources={message.sources!} defaultExpanded={false} />
                )}

                {/* 推理步骤显示 - 使用新组件 */}
                {!isUser && hasReasoning && (
                    <ReasoningStepDisplay steps={message.reasoningSteps!} defaultExpanded={false} />
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
