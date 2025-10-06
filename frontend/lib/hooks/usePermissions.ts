import { useAuthStore } from "@/store/authStore";
import { UserRole, UserPermissions } from "@/lib/types/user";

/**
 * Hook for checking user permissions
 */
export function usePermissions() {
  const { user } = useAuthStore();

  const hasRole = (role: UserRole): boolean => {
    return user?.role === role;
  };

  const hasPermission = (permission: keyof UserPermissions): boolean => {
    return user?.permissions?.[permission] ?? false;
  };

  const isAdmin = (): boolean => {
    return hasRole(UserRole.ADMIN);
  };

  const canAccessAdmin = (): boolean => {
    return isAdmin() || hasPermission('canAccessAdmin');
  };

  const canUpload = (): boolean => {
    return hasPermission('canUpload');
  };

  const canChat = (): boolean => {
    return hasPermission('canChat');
  };

  const canViewMarket = (): boolean => {
    return hasPermission('canViewMarket');
  };

  const canManageEquipment = (): boolean => {
    return hasPermission('canManageEquipment');
  };

  return {
    user,
    hasRole,
    hasPermission,
    isAdmin,
    canAccessAdmin,
    canUpload,
    canChat,
    canViewMarket,
    canManageEquipment,
  };
}
