"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { updateUser, resetUserPassword } from "@/lib/api";
import { Settings, Eye, EyeOff, Key } from "lucide-react";

interface User {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  can_upload: boolean;
  can_download: boolean;
  can_chat: boolean;
  created_at: string;
  last_login: string | null;
  notes: string | null;
}

interface UserPermissionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: User | null;
  token: string;
  onUserUpdated: () => void;
}

export function UserPermissionsModal({ 
  isOpen, 
  onClose, 
  user, 
  token, 
  onUserUpdated 
}: UserPermissionsModalProps) {
  const [formData, setFormData] = useState({
    username: "",
    role: "user",
    is_active: true,
    can_upload: false,
    can_download: false,
    can_chat: true,
    notes: "",
  });
  const [newPassword, setNewPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPasswordReset, setShowPasswordReset] = useState(false);

  // 当用户数据变化时更新表单
  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username,
        role: user.role,
        is_active: user.is_active,
        can_upload: user.can_upload,
        can_download: user.can_download,
        can_chat: user.can_chat,
        notes: user.notes || "",
      });
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setError("");
    setLoading(true);

    try {
      await updateUser(token, user.id, {
        username: formData.username,
        role: formData.role,
        is_active: formData.is_active,
        can_upload: formData.can_upload,
        can_download: formData.can_download,
        can_chat: formData.can_chat,
        notes: formData.notes || undefined,
      });

      // 如果设置了新密码，则重置密码
      if (newPassword.trim()) {
        await resetUserPassword(token, user.id, newPassword);
      }

      alert("用户信息更新成功！");
      onUserUpdated();
      handleClose();
    } catch (error) {
      setError((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setNewPassword("");
    setShowPassword(false);
    setShowPasswordReset(false);
    setError("");
    onClose();
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl p-6 mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center mb-6">
          <Settings className="h-5 w-5 mr-2 text-blue-600" />
          <h2 className="text-lg font-semibold">编辑用户权限</h2>
          <Badge variant="outline" className="ml-2">
            ID: {user.id}
          </Badge>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 基本信息 */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">基本信息</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名
                </label>
                <Input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="用户名"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  角色
                </label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="user">普通用户</option>
                  <option value="admin">管理员</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                备注
              </label>
              <Input
                type="text"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="用户备注信息（可选）"
              />
            </div>
          </div>

          {/* 账户状态 */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">账户状态</h3>
            
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                账户激活
              </label>
              <Badge variant={formData.is_active ? "default" : "destructive"}>
                {formData.is_active ? "已激活" : "已禁用"}
              </Badge>
            </div>
          </div>

          {/* 功能权限 */}
          <div className="space-y-4">
            <h3 className="text-md font-medium text-gray-900">功能权限</h3>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="can_chat"
                  checked={formData.can_chat}
                  onChange={(e) => setFormData({ ...formData, can_chat: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="can_chat" className="text-sm font-medium text-gray-700">
                  聊天权限
                </label>
                <span className="text-xs text-gray-500">允许用户使用聊天功能</span>
              </div>

              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="can_upload"
                  checked={formData.can_upload}
                  onChange={(e) => setFormData({ ...formData, can_upload: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="can_upload" className="text-sm font-medium text-gray-700">
                  文件上传权限
                </label>
                <span className="text-xs text-gray-500">允许用户上传文件</span>
              </div>

              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="can_download"
                  checked={formData.can_download}
                  onChange={(e) => setFormData({ ...formData, can_download: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="can_download" className="text-sm font-medium text-gray-700">
                  文件下载权限
                </label>
                <span className="text-xs text-gray-500">允许用户下载文件</span>
              </div>
            </div>
          </div>

          {/* 密码重置 */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-md font-medium text-gray-900">密码管理</h3>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setShowPasswordReset(!showPasswordReset)}
              >
                <Key className="h-4 w-4 mr-1" />
                {showPasswordReset ? "取消重置" : "重置密码"}
              </Button>
            </div>

            {showPasswordReset && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  新密码
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="输入新密码（至少6个字符）"
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  留空则不修改密码
                </p>
              </div>
            )}
          </div>

          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-3 rounded">
              {error}
            </div>
          )}

          <div className="flex space-x-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              className="flex-1"
              disabled={loading}
            >
              取消
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={loading}
            >
              {loading ? "保存中..." : "保存更改"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
