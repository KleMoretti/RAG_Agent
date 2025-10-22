"use client";

import { useState, useCallback, useRef } from "react";
import type {
    ChatMessage,
    ReasoningStep,
    DocumentSource,
} from "@/lib/types/api";

interface UseStreamingChatOptions {
    sessionId?: string;
    agentId?: string;
    agentType?: string; // 新增：Agent 类型（general, process, equipment, market, quality, environment）
    onMessageComplete?: (message: ChatMessage) => void;
    onError?: (error: Error) => void;
}

interface StreamingState {
    isStreaming: boolean;
    streamingContent: string;
    streamingSources: DocumentSource[];
    streamingReasoning: ReasoningStep[];
    error: string | null;
}

export function useStreamingChat(options: UseStreamingChatOptions = {}) {
    const [state, setState] = useState<StreamingState>({
        isStreaming: false,
        streamingContent: "",
        streamingSources: [],
        streamingReasoning: [],
        error: null,
    });

    const abortControllerRef = useRef<AbortController | null>(null);

    const sendMessage = useCallback(
        async (message: string) => {
            // Cancel any existing stream
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }

            // Create new abort controller
            const abortController = new AbortController();
            abortControllerRef.current = abortController;

            // Reset state
            setState({
                isStreaming: true,
                streamingContent: "",
                streamingSources: [],
                streamingReasoning: [],
                error: null,
            });

            try {
                const apiUrl =
                    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const response = await fetch(`${apiUrl}/api/chat/stream`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        // Add auth token if needed
                        ...(typeof window !== "undefined" &&
                        localStorage.getItem("token")
                            ? {
                                  Authorization: `Bearer ${localStorage.getItem("token")}`,
                              }
                            : {}),
                    },
                    body: JSON.stringify({
                        message,
                        session_id: options.sessionId,
                        agent_type: options.agentType || "general", // 添加 agent_type 参数
                        user_role: null, // 可选：用户角色
                    }),
                    signal: abortController.signal,
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const reader = response.body?.getReader();
                const decoder = new TextDecoder();

                if (!reader) {
                    throw new Error("Response body is not readable");
                }

                let buffer = "";
                let accumulatedContent = "";
                let sources: DocumentSource[] = [];
                let reasoning: ReasoningStep[] = [];

                while (true) {
                    const { done, value } = await reader.read();

                    if (done) {
                        break;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n");
                    buffer = lines.pop() || "";

                    for (const line of lines) {
                        if (!line.trim() || !line.startsWith("data: ")) {
                            continue;
                        }

                        const data = line.slice(6).trim();

                        if (data === "[DONE]") {
                            continue;
                        }

                        try {
                            const event = JSON.parse(data);

                            switch (event.type) {
                                case "sources":
                                    if (
                                        event.sources &&
                                        Array.isArray(event.sources)
                                    ) {
                                        sources = event.sources.map(
                                            (s: Record<string, unknown>) => ({
                                                fileId: (s.file_id ||
                                                    s.fileId ||
                                                    "") as string,
                                                fileName: (s.file_name ||
                                                    s.fileName ||
                                                    s.file ||
                                                    "") as string,
                                                chunkId: (s.chunk_id ||
                                                    s.chunkId ||
                                                    0) as number,
                                                content: (s.content ||
                                                    s.preview ||
                                                    "") as string,
                                                relevanceScore:
                                                    (s.relevance_score ||
                                                        s.score ||
                                                        0) as number,
                                            }),
                                        );
                                        setState((prev) => ({
                                            ...prev,
                                            streamingSources: sources,
                                        }));
                                    }
                                    break;

                                case "reasoning":
                                    if (
                                        event.steps &&
                                        Array.isArray(event.steps)
                                    ) {
                                        reasoning = event.steps.map(
                                            (
                                                step: Record<string, unknown>,
                                            ) => ({
                                                thought: (step.thought ||
                                                    "") as string,
                                                toolName: (step.tool_name ||
                                                    step.toolName ||
                                                    step.tool) as
                                                    | string
                                                    | undefined,
                                                toolInput:
                                                    step.tool_input ||
                                                    step.toolInput,
                                                observation:
                                                    step.observation as
                                                        | string
                                                        | undefined,
                                            }),
                                        );
                                        setState((prev) => ({
                                            ...prev,
                                            streamingReasoning: reasoning,
                                        }));
                                    }
                                    break;

                                case "content":
                                    if (event.delta) {
                                        accumulatedContent += event.delta;
                                        setState((prev) => ({
                                            ...prev,
                                            streamingContent:
                                                accumulatedContent,
                                        }));
                                    }
                                    break;

                                case "done":
                                    // Stream complete
                                    break;

                                case "error":
                                    throw new Error(
                                        event.message || "Streaming error",
                                    );
                            }
                        } catch (parseError) {
                            console.error(
                                "Failed to parse SSE event:",
                                parseError,
                            );
                        }
                    }
                }

                // Complete - create final message
                const finalMessage: ChatMessage = {
                    id: Date.now().toString(),
                    role: "assistant",
                    content: accumulatedContent,
                    timestamp: new Date(),
                    reasoningSteps:
                        reasoning.length > 0 ? reasoning : undefined,
                    sources: sources.length > 0 ? sources : undefined,
                };

                setState({
                    isStreaming: false,
                    streamingContent: "",
                    streamingSources: [],
                    streamingReasoning: [],
                    error: null,
                });

                options.onMessageComplete?.(finalMessage);
            } catch (error) {
                if (error instanceof Error && error.name === "AbortError") {
                    // Streaming was cancelled
                    setState({
                        isStreaming: false,
                        streamingContent: "",
                        streamingSources: [],
                        streamingReasoning: [],
                        error: null,
                    });
                } else {
                    const errorMessage =
                        error instanceof Error
                            ? error.message
                            : "Unknown error";
                    setState({
                        isStreaming: false,
                        streamingContent: "",
                        streamingSources: [],
                        streamingReasoning: [],
                        error: errorMessage,
                    });
                    options.onError?.(
                        error instanceof Error
                            ? error
                            : new Error(errorMessage),
                    );
                }
            } finally {
                abortControllerRef.current = null;
            }
        },
        [options],
    );

    const cancelStreaming = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
    }, []);

    return {
        isStreaming: state.isStreaming,
        streamingContent: state.streamingContent,
        streamingSources: state.streamingSources,
        streamingReasoning: state.streamingReasoning,
        error: state.error,
        sendMessage,
        cancelStreaming,
    };
}
