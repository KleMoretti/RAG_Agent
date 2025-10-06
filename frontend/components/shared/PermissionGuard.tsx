"use client";

import * as React from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, Shield } from "lucide-react";
import { usePermissions } from "@/lib/hooks/usePermissions";
import { UserRole } from "@/lib/types/user";

interface PermissionGuardProps {
  children: React.ReactNode;
  requiredRole?: UserRole;
  requiredPermission?: keyof import("@/lib/types/user").UserPermissions;
  fallback?: React.ReactNode;
  showError?: boolean;
}

/**
 * Permission guard component that conditionally renders children based on user permissions
 */
export function PermissionGuard({
  children,
  requiredRole,
  requiredPermission,
  fallback,
  showError = true,
}: PermissionGuardProps) {
  const { user, hasRole, hasPermission, isAdmin } = usePermissions();

  // Check if user has required role
  const hasRequiredRole = requiredRole ? hasRole(requiredRole) : true;

  // Check if user has required permission
  const hasRequiredPermission = requiredPermission ? hasPermission(requiredPermission) : true;

  // Admin always has access
  const hasAccess = isAdmin() || (hasRequiredRole && hasRequiredPermission);

  if (!hasAccess) {
    if (fallback) {
      return <>{fallback}</>;
    }

    if (showError) {
      return (
        <div className="flex items-center justify-center h-full min-h-[400px]">
          <Alert variant="destructive" className="max-w-md">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <div className="font-semibold">权限不足</div>
                <div className="text-sm">
                  {requiredRole && `需要 ${getRoleLabel(requiredRole)} 权限`}
                  {requiredRole && requiredPermission && " 或 "}
                  {requiredPermission && `需要 ${getPermissionLabel(requiredPermission)} 权限`}
                </div>
                <div className="text-xs text-muted-foreground">
                  请联系管理员获取相应权限
                </div>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      );
    }

    return null;
  }

  return <>{children}</>;
}

/**
 * Admin-only guard component
 */
export function AdminGuard({ children, fallback }: { children: React.ReactNode; fallback?: React.ReactNode }) {
  return (
    <PermissionGuard
      requiredRole={UserRole.ADMIN}
      fallback={fallback}
    >
      {children}
    </PermissionGuard>
  );
}

/**
 * Helper function to get role label
 */
function getRoleLabel(role: UserRole): string {
  switch (role) {
    case UserRole.ADMIN: return '管理员';
    case UserRole.MANAGER: return '经理';
    case UserRole.PRODUCTION: return '生产';
    case UserRole.TECHNICIAN: return '技术员';
    case UserRole.PURCHASER: return '采购';
    case UserRole.ENV_EXPERT: return '环保专家';
    default: return role;
  }
}

/**
 * Helper function to get permission label
 */
function getPermissionLabel(permission: keyof import("@/lib/types/user").UserPermissions): string {
  switch (permission) {
    case 'canUpload': return '文件上传';
    case 'canChat': return 'AI对话';
    case 'canViewMarket': return '市场数据查看';
    case 'canManageEquipment': return '设备管理';
    case 'canAccessAdmin': return '系统管理';
    default: return permission;
  }
}
