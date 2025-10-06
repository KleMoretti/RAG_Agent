/**
 * User role definitions matching backend UserRole enum
 */
export enum UserRole {
  ADMIN = 'admin',
  PRODUCTION = 'production',
  MANAGER = 'manager',
  PURCHASER = 'purchaser',
  ENV_EXPERT = 'env_expert',
  TECHNICIAN = 'technician',
}

/**
 * User permission interface
 */
export interface UserPermissions {
  canUpload: boolean;
  canChat: boolean;
  canViewMarket: boolean;
  canManageEquipment: boolean;
  canAccessAdmin: boolean;
}

/**
 * User entity interface matching backend response
 */
export interface User {
  id: number;
  username: string;
  role: string;
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
