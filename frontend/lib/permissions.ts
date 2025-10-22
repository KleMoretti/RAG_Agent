/**
 * 角色权限管理工具
 * 根据用户角色控制功能访问权限
 */

import type { UserRole, User } from "./types/api";

/**
 * 角色权限定义
 */
export interface RolePermissions {
  // 基础权限
  canChat: boolean;
  canUpload: boolean;
  canDownload: boolean;
  canDelete: boolean;

  // 功能模块权限
  canAccessKnowledge: boolean;
  canAccessEquipment: boolean;
  canAccessMarket: boolean;
  canAccessWorkflow: boolean;
  canAccessEnvironment: boolean;
  canAccessAdmin: boolean;

  // 操作权限
  canManageUsers: boolean;
  canManagePrompts: boolean;
  canManageVocabulary: boolean;
  canViewSystemStats: boolean;
}

/**
 * 默认 Agent 类型映射
 */
export const roleDefaultAgents: Record<UserRole, string> = {
  admin: "general",
  manager: "general",
  technician: "equipment",
  user: "general",
};

/**
 * 角色可用的 Agent 类型
 */
export const roleAvailableAgents: Record<UserRole, string[]> = {
  admin: ["general", "process", "equipment", "market", "quality", "environment"],
  manager: ["general", "process", "equipment", "market", "quality", "environment"],
  technician: ["equipment", "process", "general"],
  user: ["general"],
};

/**
 * 角色显示名称
 */
export const roleDisplayNames: Record<UserRole, string> = {
  admin: "管理员",
  manager: "技术经理",
  technician: "技术员",
  user: "普通用户",
};

/**
 * 角色描述
 */
export const roleDescriptions: Record<UserRole, string> = {
  admin: "系统管理员，拥有全部权限",
  manager: "技术经理，负责技术决策和跨部门协调",
  technician: "技术员，负责设备维护和故障诊断",
  user: "普通用户，基础查询功能",
};

/**
 * 根据角色获取权限配置
 */
export function getPermissionsByRole(role: UserRole): RolePermissions {
  switch (role) {
    case "admin":
      return {
        canChat: true,
        canUpload: true,
        canDownload: true,
        canDelete: true,
        canAccessKnowledge: true,
        canAccessEquipment: true,
        canAccessMarket: true,
        canAccessWorkflow: true,
        canAccessEnvironment: true,
        canAccessAdmin: true,
        canManageUsers: true,
        canManagePrompts: true,
        canManageVocabulary: true,
        canViewSystemStats: true,
      };

    case "manager":
      return {
        canChat: true,
        canUpload: true,
        canDownload: true,
        canDelete: true,
        canAccessKnowledge: true,
        canAccessEquipment: true,
        canAccessMarket: true,
        canAccessWorkflow: true,
        canAccessEnvironment: true,
        canAccessAdmin: false,
        canManageUsers: false,
        canManagePrompts: false,
        canManageVocabulary: false,
        canViewSystemStats: true,
      };

    case "technician":
      return {
        canChat: true,
        canUpload: false, // 技术员不能批量上传文档
        canDownload: true,
        canDelete: false,
        canAccessKnowledge: true, // 可以查看知识库
        canAccessEquipment: true, // 主要功能：设备管理
        canAccessMarket: false,
        canAccessWorkflow: true, // 可以查看工艺流程
        canAccessEnvironment: false,
        canAccessAdmin: false,
        canManageUsers: false,
        canManagePrompts: false,
        canManageVocabulary: false,
        canViewSystemStats: false,
      };

    case "user":
    default:
      return {
        canChat: true,
        canUpload: false,
        canDownload: true,
        canDelete: false,
        canAccessKnowledge: true,
        canAccessEquipment: false,
        canAccessMarket: false,
        canAccessWorkflow: false,
        canAccessEnvironment: false,
        canAccessAdmin: false,
        canManageUsers: false,
        canManagePrompts: false,
        canManageVocabulary: false,
        canViewSystemStats: false,
      };
  }
}

/**
 * 检查用户是否有特定权限
 */
export function hasPermission(
  user: User | null,
  permission: keyof RolePermissions
): boolean {
  if (!user) return false;

  const permissions = getPermissionsByRole(user.role);
  return permissions[permission];
}

/**
 * 检查用户是否可以访问某个路由
 */
export function canAccessRoute(user: User | null, pathname: string): boolean {
  if (!user) return false;

  const permissions = getPermissionsByRole(user.role);

  // 路由权限映射
  if (pathname.startsWith("/dashboard/admin")) {
    return permissions.canAccessAdmin;
  }

  if (pathname.startsWith("/dashboard/equipment")) {
    return permissions.canAccessEquipment;
  }

  if (pathname.startsWith("/dashboard/market")) {
    return permissions.canAccessMarket;
  }

  if (pathname.startsWith("/dashboard/workflow")) {
    return permissions.canAccessWorkflow;
  }

  if (pathname.startsWith("/dashboard/environment")) {
    return permissions.canAccessEnvironment;
  }

  if (pathname.startsWith("/dashboard/knowledge")) {
    return permissions.canAccessKnowledge;
  }

  // 默认允许访问 dashboard 首页和聊天页面
  if (
    pathname === "/dashboard" ||
    pathname.startsWith("/dashboard/chat") ||
    pathname === "/dashboard/profile"
  ) {
    return true;
  }

  return false;
}

/**
 * 获取用户的默认 Agent 类型
 */
export function getDefaultAgentType(role: UserRole): string {
  return roleDefaultAgents[role] || "general";
}

/**
 * 获取用户可用的 Agent 类型列表
 */
export function getAvailableAgents(role: UserRole): string[] {
  return roleAvailableAgents[role] || ["general"];
}

/**
 * 检查用户是否可以使用某个 Agent
 */
export function canUseAgent(role: UserRole, agentType: string): boolean {
  const availableAgents = getAvailableAgents(role);
  return availableAgents.includes(agentType);
}

/**
 * 获取角色主题色
 */
export function getRoleColor(role: UserRole): string {
  switch (role) {
    case "admin":
      return "hsl(var(--destructive))"; // 红色
    case "manager":
      return "hsl(var(--primary))"; // 蓝色
    case "technician":
      return "hsl(var(--chart-2))"; // 绿色
    default:
      return "hsl(var(--muted))"; // 灰色
  }
}

/**
 * 获取角色图标
 */
export function getRoleIcon(role: UserRole): string {
  switch (role) {
    case "admin":
      return "shield";
    case "manager":
      return "briefcase";
    case "technician":
      return "wrench";
    default:
      return "user";
  }
}
