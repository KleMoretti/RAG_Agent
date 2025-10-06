"use client";

import * as React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { User, UserRole, UserPermissions } from "@/lib/types/user";
import { adminApi } from "@/lib/api/admin";
import { AlertCircle, Loader2 } from "lucide-react";

interface UserEditDialogProps {
  user: User | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedUser: User) => void;
}

export function UserEditDialog({ user, isOpen, onClose, onSave }: UserEditDialogProps) {
  const [formData, setFormData] = useState<Partial<User>>({});
  const [permissions, setPermissions] = useState<UserPermissions>({
    canUpload: false,
    canChat: false,
    canViewMarket: false,
    canManageEquipment: false,
    canAccessAdmin: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // 初始化表单数据
  React.useEffect(() => {
    if (user) {
      setFormData({
        username: user.username,
        role: user.role,
        is_active: user.is_active,
        notes: user.notes,
      });
      setPermissions({
        canUpload: user.can_upload,
        canChat: user.can_chat,
        canViewMarket: false, // 这个字段在后端不存在，设为false
        canManageEquipment: false, // 这个字段在后端不存在，设为false
        canAccessAdmin: user.can_access_admin,
      });
    }
  }, [user]);

  const handleSave = async () => {
    if (!user) return;

    try {
      setLoading(true);
      setError("");

      const updateData = {
        username: formData.username,
        role: formData.role,
        is_active: formData.is_active,
        can_upload: permissions.canUpload,
        can_download: user.can_download, // 保持原有值
        can_chat: permissions.canChat,
        can_access_admin: permissions.canAccessAdmin,
        notes: formData.notes || user.notes, // 使用表单中的值或原有值
      };

      const updatedUser = await adminApi.updateUser(user.id.toString(), updateData);
      onSave(updatedUser);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "更新用户失败");
    } finally {
      setLoading(false);
    }
  };

  const handlePermissionChange = (permission: keyof UserPermissions, checked: boolean) => {
    setPermissions(prev => ({
      ...prev,
      [permission]: checked,
    }));
  };

  const getRoleLabel = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN: return '管理员';
      case UserRole.MANAGER: return '经理';
      case UserRole.PRODUCTION: return '生产';
      case UserRole.TECHNICIAN: return '技术员';
      case UserRole.PURCHASER: return '采购';
      case UserRole.ENV_EXPERT: return '环保专家';
      default: return role;
    }
  };

  if (!user) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>编辑用户</DialogTitle>
          <DialogDescription>
            修改用户信息和权限设置
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 基本信息 */}
          <div className="space-y-2">
            <Label htmlFor="username">用户名</Label>
            <Input
              id="username"
              value={formData.username || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
              placeholder="输入用户名"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">备注</Label>
            <Input
              id="notes"
              value={user.notes || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              placeholder="输入备注信息"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">角色</Label>
            <Select
              value={formData.role || UserRole.TECHNICIAN}
              onValueChange={(value) => setFormData(prev => ({ ...prev, role: value as UserRole }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="选择角色" />
              </SelectTrigger>
              <SelectContent>
                {Object.values(UserRole).map((role) => (
                  <SelectItem key={role} value={role}>
                    {getRoleLabel(role)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 权限设置 */}
          <div className="space-y-3">
            <Label>权限设置</Label>
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="canUpload"
                  checked={permissions.canUpload}
                  onCheckedChange={(checked) => handlePermissionChange('canUpload', !!checked)}
                />
                <Label htmlFor="canUpload" className="text-sm font-normal">
                  可以上传文件
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="canChat"
                  checked={permissions.canChat}
                  onCheckedChange={(checked) => handlePermissionChange('canChat', !!checked)}
                />
                <Label htmlFor="canChat" className="text-sm font-normal">
                  可以使用AI对话
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="canViewMarket"
                  checked={permissions.canViewMarket}
                  onCheckedChange={(checked) => handlePermissionChange('canViewMarket', !!checked)}
                />
                <Label htmlFor="canViewMarket" className="text-sm font-normal">
                  可以查看市场数据
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="canManageEquipment"
                  checked={permissions.canManageEquipment}
                  onCheckedChange={(checked) => handlePermissionChange('canManageEquipment', !!checked)}
                />
                <Label htmlFor="canManageEquipment" className="text-sm font-normal">
                  可以管理设备
                </Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="canAccessAdmin"
                  checked={permissions.canAccessAdmin}
                  onCheckedChange={(checked) => handlePermissionChange('canAccessAdmin', !!checked)}
                />
                <Label htmlFor="canAccessAdmin" className="text-sm font-normal">
                  可以访问系统管理
                </Label>
              </div>
            </div>
          </div>

          {/* 状态设置 */}
          <div className="flex items-center space-x-2">
            <Checkbox
              id="is_active"
              checked={formData.is_active ?? true}
              onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: !!checked }))}
            />
            <Label htmlFor="is_active" className="text-sm font-normal">
              用户状态：{formData.is_active ? '活跃' : '禁用'}
            </Label>
          </div>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            取消
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            保存
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
