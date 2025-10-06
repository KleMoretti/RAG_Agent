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

interface UserCreateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (newUser: User) => void;
}

export function UserCreateDialog({ isOpen, onClose, onSave }: UserCreateDialogProps) {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: UserRole.TECHNICIAN,
  });
  const [permissions, setPermissions] = useState<UserPermissions>({
    canUpload: true,
    canChat: true,
    canViewMarket: false,
    canManageEquipment: false,
    canAccessAdmin: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleSave = async () => {
    try {
      setLoading(true);
      setError("");

      const createData = {
        username: formData.username,
        email: formData.email || undefined,
        password: formData.password,
        role: formData.role,
        permissions,
      };

      const newUser = await adminApi.createUser(createData);
      onSave(newUser);
      onClose();
      
      // 重置表单
      setFormData({
        username: "",
        email: "",
        password: "",
        role: UserRole.TECHNICIAN,
      });
      setPermissions({
        canUpload: true,
        canChat: true,
        canViewMarket: false,
        canManageEquipment: false,
        canAccessAdmin: false,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建用户失败");
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>创建新用户</DialogTitle>
          <DialogDescription>
            添加新的系统用户并设置权限
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 基本信息 */}
          <div className="space-y-2">
            <Label htmlFor="username">用户名 *</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
              placeholder="输入用户名"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">邮箱</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              placeholder="输入邮箱地址"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">密码 *</Label>
            <Input
              id="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              placeholder="输入密码"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="role">角色</Label>
            <Select
              value={formData.role}
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
          <Button 
            onClick={handleSave} 
            disabled={loading || !formData.username || !formData.password}
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            创建用户
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
