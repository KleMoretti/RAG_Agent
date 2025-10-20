/**
 * Application-wide constants
 */

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
    // Authentication
    LOGIN: "/api/auth/login",
    REGISTER: "/api/auth/register",
    LOGOUT: "/api/auth/logout",
    REFRESH: "/api/auth/refresh",

    // Chat
    CHAT: "/api/chat",
    CHAT_STREAM: "/api/chat/stream",
    CHAT_HISTORY: "/api/chat/history",

    // File upload
    UPLOAD: "/api/upload",
    FILES: "/api/files",

    // Admin
    USERS: "/api/admin/users",
    SYSTEM_STATS: "/api/admin/stats",
    KNOWLEDGE_FILES: "/api/admin/files",
    VOCABULARY: "/api/admin/vocabulary",

    // Agent Management (Simplified)
    AGENTS: "/api/prompt-management/agents",
    AGENT_BY_ID: (id: string) => `/api/prompt-management/agents/${id}`,
    AGENT_PROMPT: (id: string) => `/api/prompt-management/agents/${id}/prompt`,
} as const;

/**
 * Storage keys for localStorage/sessionStorage
 */
export const STORAGE_KEYS = {
    AUTH_TOKEN: "auth_token",
    REFRESH_TOKEN: "refresh_token",
    USER: "user",
    THEME: "theme",
    LANGUAGE: "language",
    CHAT_SESSIONS: "chat_sessions",
} as const;

/**
 * Query keys for TanStack Query
 */
export const QUERY_KEYS = {
    USER: "user",
    USERS: "users",
    CHAT_HISTORY: "chatHistory",
    FILES: "files",
    SYSTEM_STATS: "systemStats",
    EQUIPMENT: "equipment",
    MARKET_DATA: "marketData",
    KNOWLEDGE_BASE: "knowledgeBase",
} as const;

/**
 * Route paths
 */
export const ROUTES = {
    HOME: "/",
    LOGIN: "/login",
    REGISTER: "/register",
    DASHBOARD: "/dashboard",
    // 以下路由对应的页面尚未实现
    // CHAT: '/dashboard/chat',
    // EQUIPMENT: '/dashboard/equipment',
    // MARKET: '/dashboard/market',
    KNOWLEDGE: "/dashboard/knowledge",
    // WORKFLOW: '/dashboard/workflow',
    ADMIN: "/dashboard/admin",
} as const;

/**
 * Supported file types for upload
 */
export const SUPPORTED_FILE_TYPES = {
    DOCUMENTS: [".pdf", ".docx", ".doc", ".txt", ".md"],
    IMAGES: [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    CODE: [".py", ".js", ".ts", ".java", ".cpp", ".c"],
    DATA: [".csv", ".xlsx", ".json", ".xml"],
} as const;

/**
 * Maximum file size (in bytes)
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

/**
 * Pagination defaults
 */
export const PAGINATION = {
    DEFAULT_PAGE: 1,
    DEFAULT_PAGE_SIZE: 20,
    PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
} as const;

/**
 * Chat configuration
 */
export const CHAT_CONFIG = {
    MAX_MESSAGE_LENGTH: 2000,
    TYPING_DELAY_MS: 20,
    MAX_HISTORY_LENGTH: 100,
    STREAM_CHUNK_SIZE: 100,
} as const;

/**
 * Theme modes
 */
export const THEME_MODES = {
    LIGHT: "light",
    DARK: "dark",
    AUTO: "auto",
} as const;
