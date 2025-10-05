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
 * User entity interface
 */
export interface User {
  id: string;
  username: string;
  email?: string;
  role: UserRole;
  permissions: UserPermissions;
  isActive: boolean;
  createdAt: string;
  lastLogin?: string;
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
