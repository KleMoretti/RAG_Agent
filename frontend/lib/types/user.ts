/**
 * User role definitions matching backend UserRole enum
 */
export enum UserRole {
    ADMIN = "admin",
    MANAGER = "manager",
    TECHNICIAN = "technician",
    USER = "user",
}

/**
 * User role type (compatible with api.ts)
 */
export type UserRoleType = "admin" | "manager" | "technician" | "user";

/**
 * User permission interface
 */
export interface UserPermissions {
    canChat: boolean;
    canUpload: boolean;
    canDownload: boolean;
    canDelete: boolean;
    canAccessKnowledge: boolean;
    canAccessEquipment: boolean;
    canAccessMarket: boolean;
    canAccessWorkflow: boolean;
    canAccessEnvironment: boolean;
    canAccessAdmin: boolean;
}

/**
 * User entity interface matching backend response
 */
export interface User {
    id: number;
    username: string;
    email?: string;
    role: UserRoleType;  // 使用联合类型而非 string
    is_active: boolean;
    can_upload: boolean;
    can_download: boolean;
    can_chat: boolean;
    can_access_admin: boolean;
    created_at: string;
    updated_at: string;
    last_login?: string;
    created_by?: number;
    notes?: string;
}

/**
 * Login credentials
 */
export interface LoginCredentials {
    username: string;
    password: string;
}

/**
 * Registration data
 */
export interface RegisterData {
    username: string;
    email?: string;
    password: string;
    role?: UserRole;
}
