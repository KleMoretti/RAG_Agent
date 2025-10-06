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
 * Chat message interface
 */
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
  role: 'user' | 'assistant';
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
} from './prompt';
