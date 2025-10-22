/**
 * Common API response types
 */

export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

/**
 * User roles
 */
export type UserRole = "admin" | "manager" | "technician" | "user";

/**
 * User interface
 */
export interface User {
    id: number;
    username: string;
    role: UserRole;
    email?: string;
    is_active: boolean;
    can_upload: boolean;
    can_download: boolean;
    can_chat: boolean;
    can_access_admin?: boolean;
    created_at?: string;
    updated_at?: string;
    last_login?: string;
    notes?: string;
}

/**
 * Auth response
 */
export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export interface MeResponse extends User {}

/**
 * Chat message interface
 */
export interface ChatAttachment {</parameter>
export interface ChatAttachment {
    fileId: string;
    fileName: string;
    fileSize?: number;
    contentType?: string;
    chunks?: DocumentChunk[];
    rawPath?: string;
    processedPath?: string;
    uploadedAt?: Date;
}

export interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    reasoningSteps?: ReasoningStep[];
    sources?: DocumentSource[];
    attachments?: ChatAttachment[];
    agentId?: string; // Agent ID when message was sent
    agentInfo?: {
        name: string;
        icon: string; // Icon name for lookup
        colorScheme?: {
            background?: string;
            primary?: string;
            border?: string;
        };
    }; // Agent display info when message was sent
}

/**
 * Reasoning step from Agent
 */
export interface ReasoningStep {
    thought: string;
    toolName?: string;
    toolInput?: Record<string, unknown>;
    observation?: string;
    fallback_mode?: boolean; // 是否使用了降级模式（跳过RAG直接用LLM）
}

/**
 * Document source citation
 */
export interface DocumentSource {
    fileId: string;
    fileName: string;
    chunkId: number;
    content: string;
    relevanceScore: number;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
    message: string;
    sessionId?: string;
    agentId?: string;
}

/**
 * Chat response payload
 */
export interface ChatResponse {
    response: string;
    reasoningSteps?: ReasoningStep[];
}

/**
 * File upload response
 */
export interface FileUploadResponse {
    success: boolean;
    message: string;
    fileId?: string;
    fileName?: string;
    fileSize?: number;
    contentType?: string;
    chunks?: DocumentChunk[];
    rawPath?: string;
    processedPath?: string;
}

/**
 * Document chunk
 */
export interface DocumentChunk {
    content: string;
    type: string;
    length: number;
}

/**
 * Pagination metadata
 */
export interface PaginationMeta {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
}

/**
 * Paginated response
 */
export interface PaginatedResponse<T> {
    data: T[];
    meta: PaginationMeta;
}

/**
 * Document/File management types
 */
export interface DocumentMetadata {
    id: string;
    fileName: string;
    fileSize: number;
    uploadDate: string;
    uploaderName?: string;
    filePath: string;
    isProcessed: boolean;
    chunkCount?: number;
    contentType?: string;
    tags?: string[];
    description?: string;
}

export interface DocumentListResponse {
    data: DocumentMetadata[];
    meta: PaginationMeta;
}

export interface DocumentUpdateRequest {
    fileName?: string;
    tags?: string[];
    description?: string;
}

export interface DocumentDeleteResponse {
    message: string;
}

export interface BatchDeleteRequest {
    fileNames: string[];
}

export interface BatchDeleteResponse {
    success: string[];
    failed: Array<{ fileName: string; reason: string }>;
    total: number;
}

// Re-export simplified Prompt Management types for convenience
export type {
    Agent,
    SystemPrompt,
    AgentResponse,
    PaginatedAgentsResponse,
    ListAgentsParams,
    AgentWithMetadata,
    SimplifiedPromptState,
    SimplifiedPromptActions,
} from "./prompt";
