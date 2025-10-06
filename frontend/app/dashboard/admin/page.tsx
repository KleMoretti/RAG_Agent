"use client";

import * as React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { useAuthStore } from "@/store/authStore";
import { adminApi } from "@/lib/api/admin";
import { User, UserRole, UserPermissions } from "@/lib/types/user";
import { SystemStats, FileInfo, VocabularyEntry } from "@/lib/api/admin";
import { PaginatedResponse } from "@/lib/types/api";
import { useTranslation } from "@/lib/hooks/useTranslation";
import { UserEditDialog } from "@/components/admin/UserEditDialog";
import { UserCreateDialog } from "@/components/admin/UserCreateDialog";
import { VocabularyEditDialog } from "@/components/admin/VocabularyEditDialog";
import { VocabularyCreateDialog } from "@/components/admin/VocabularyCreateDialog";
import { AdminGuard } from "@/components/shared/PermissionGuard";
import {
  Users,
  Database,
  BookOpen,
  Settings,
  Shield,
  AlertCircle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Trash2,
  Edit,
  Plus,
  Search,
  Download,
  Upload,
  HardDrive,
  Activity,
  Clock,
  UserCheck,
  FileText,
  BookMarked,
} from "lucide-react";


// 系统统计组件
function SystemStatsCard({ stats }: { stats: SystemStats }) {
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      case 'unknown': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy': return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'warning': return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      case 'error': return <XCircle className="h-4 w-4 text-red-600" />;
      case 'unknown': return <Activity className="h-4 w-4 text-gray-600" />;
      default: return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">系统状态</CardTitle>
          {getHealthIcon(stats.systemHealth || 'unknown')}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            <Badge variant={(stats.systemHealth || 'unknown') === 'healthy' ? 'default' : 'destructive'}>
              {(stats.systemHealth || 'unknown') === 'healthy' ? '正常' : (stats.systemHealth || 'unknown') === 'warning' ? '警告' : '错误'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">用户总数</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totalUsers || 0}</div>
          <p className="text-xs text-muted-foreground">
            活跃用户: {stats.activeUsers || 0}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">知识库文件</CardTitle>
          <Database className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totalFiles || 0}</div>
          <p className="text-xs text-muted-foreground">
            总会话数: {stats.totalSessions || 0}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">磁盘使用</CardTitle>
          <HardDrive className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats.diskUsage ? (
              <>
                {formatBytes(stats.diskUsage.used)} / {formatBytes(stats.diskUsage.total)}
              </>
            ) : (
              'N/A'
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            剩余: {stats.diskUsage ? formatBytes(stats.diskUsage.free) : 'N/A'}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

// 用户管理组件
function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getUsers(page, 20);
      setUsers(response.data);
      setTotalPages(response.meta.totalPages);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载用户失败");
    } finally {
      setLoading(false);
    }
  };

  const handleUserSave = (updatedUser: User) => {
    setUsers(prev => prev.map(user => user.id === updatedUser.id ? updatedUser : user));
    setEditingUser(null);
  };

  const handleUserCreate = (newUser: User) => {
    setUsers(prev => [newUser, ...prev]);
    setShowCreateDialog(false);
  };

  const handleDeleteUser = async (userId: number) => {
    if (window.confirm('确定要删除这个用户吗？此操作不可撤销。')) {
      try {
        await adminApi.deleteUser(userId);
        setUsers(prev => prev.filter(user => user.id !== userId));
      } catch (err) {
        setError(err instanceof Error ? err.message : "删除用户失败");
      }
    }
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case 'admin': return 'destructive';
      case 'manager': return 'default';
      case 'production': return 'secondary';
      case 'technician': return 'outline';
      case 'purchaser': return 'outline';
      case 'env_expert': return 'outline';
      default: return 'outline';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'admin': return '管理员';
      case 'manager': return '经理';
      case 'production': return '生产';
      case 'technician': return '技术员';
      case 'purchaser': return '采购';
      case 'env_expert': return '环保专家';
      default: return role;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="h-6 w-6 animate-spin mr-2" />
        <span>加载用户数据中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">用户管理</h3>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          添加用户
        </Button>
      </div>

      <div className="space-y-2">
        {users.map((user, index) => (
          <Card key={user.id || `user-${index}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <UserCheck className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <div className="font-medium">{user.username}</div>
                      <div className="text-sm text-muted-foreground">{user.email}</div>
                    </div>
                  </div>
                  <Badge variant={getRoleBadgeVariant(user.role)}>
                    {getRoleLabel(user.role)}
                  </Badge>
                  <Badge variant={user.is_active ? 'default' : 'secondary'}>
                    {user.is_active ? '活跃' : '禁用'}
                  </Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setEditingUser(user)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    编辑
                  </Button>
                  {user.role !== 'admin' && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleDeleteUser(user.id)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      删除
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 分页 */}
      <div className="flex justify-center space-x-2">
        <Button
          variant="outline"
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
        >
          上一页
        </Button>
        <span className="flex items-center px-4">
          第 {page} 页，共 {totalPages} 页
        </span>
        <Button
          variant="outline"
          onClick={() => setPage(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
        >
          下一页
        </Button>
      </div>

      {/* 用户编辑对话框 */}
      <UserEditDialog
        user={editingUser}
        isOpen={!!editingUser}
        onClose={() => setEditingUser(null)}
        onSave={handleUserSave}
      />

      {/* 用户创建对话框 */}
      <UserCreateDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onSave={handleUserCreate}
      />
    </div>
  );
}

// 知识库管理组件
function KnowledgeManagement() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getKnowledgeFiles(page, 20);
      setFiles(response.data);
      setTotalPages(response.meta.totalPages);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载文件失败");
    } finally {
      setLoading(false);
    }
  };

  const handleReprocessFile = async (fileId: string) => {
    try {
      await adminApi.reprocessKnowledgeFile(fileId);
      // 重新加载文件列表
      loadFiles();
    } catch (err) {
      setError(err instanceof Error ? err.message : "重新处理文件失败");
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (window.confirm('确定要删除这个文件吗？此操作不可撤销。')) {
      try {
        await adminApi.deleteKnowledgeFile(fileId);
        setFiles(prev => prev.filter(file => file.id !== fileId));
      } catch (err) {
        setError(err instanceof Error ? err.message : "删除文件失败");
      }
    }
  };

  useEffect(() => {
    loadFiles();
  }, [page]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="h-6 w-6 animate-spin mr-2" />
        <span>加载文件数据中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">知识库文件管理</h3>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            上传文件
          </Button>
          <Button variant="outline" onClick={loadFiles}>
            <RefreshCw className="h-4 w-4 mr-2" />
            刷新
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        {files.map((file, index) => (
          <Card key={file.id || `file-${index}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <div className="font-medium">{file.fileName}</div>
                    <div className="text-sm text-muted-foreground">
                      {formatFileSize(file.fileSize)} • {formatDate(file.uploadDate)} • {file.uploaderName}
                    </div>
                  </div>
                  <Badge variant={file.isProcessed ? 'default' : 'secondary'}>
                    {file.isProcessed ? '已处理' : '未处理'}
                  </Badge>
                  {file.chunkCount && (
                    <Badge variant="outline">
                      {file.chunkCount} 个片段
                    </Badge>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleReprocessFile(file.id)}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    重新处理
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    下载
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeleteFile(file.id)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    删除
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 分页 */}
      <div className="flex justify-center space-x-2">
        <Button
          variant="outline"
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
        >
          上一页
        </Button>
        <span className="flex items-center px-4">
          第 {page} 页，共 {totalPages} 页
        </span>
        <Button
          variant="outline"
          onClick={() => setPage(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
        >
          下一页
        </Button>
      </div>
    </div>
  );
}

// 专业词汇管理组件
function VocabularyManagement() {
  const [vocabulary, setVocabulary] = useState<VocabularyEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingEntry, setEditingEntry] = useState<VocabularyEntry | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const loadVocabulary = async () => {
    try {
      setLoading(true);
      const response = await adminApi.getVocabularyEntries(page, 20);
      setVocabulary(response.data);
      setTotalPages(response.meta.totalPages);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载词汇失败");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadVocabulary();
      return;
    }

    try {
      setLoading(true);
      const results = await adminApi.searchVocabularyEntries(searchQuery);
      setVocabulary(results);
      setTotalPages(1);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "搜索词汇失败");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteEntry = async (entryId: string) => {
    if (window.confirm('确定要删除这个词汇条目吗？此操作不可撤销。')) {
      try {
        await adminApi.deleteVocabularyEntry(entryId);
        setVocabulary(prev => prev.filter(entry => entry.id !== entryId));
      } catch (err) {
        setError(err instanceof Error ? err.message : "删除词汇失败");
      }
    }
  };

  const handleEntrySave = (updatedEntry: VocabularyEntry) => {
    setVocabulary(prev => prev.map(entry => entry.id === updatedEntry.id ? updatedEntry : entry));
    setEditingEntry(null);
  };

  const handleEntryCreate = (newEntry: VocabularyEntry) => {
    setVocabulary(prev => [newEntry, ...prev]);
    setShowCreateDialog(false);
  };

  useEffect(() => {
    loadVocabulary();
  }, [page]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="h-6 w-6 animate-spin mr-2" />
        <span>加载词汇数据中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">专业词汇管理</h3>
        <div className="flex space-x-2">
          <div className="flex space-x-2">
            <Input
              placeholder="搜索词汇..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-48"
            />
            <Button variant="outline" onClick={handleSearch}>
              <Search className="h-4 w-4 mr-2" />
              搜索
            </Button>
          </div>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            添加词汇
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        {vocabulary.map((entry, index) => (
          <Card key={entry.id || `entry-${index}`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <BookMarked className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <div className="font-medium">{entry.term}</div>
                    <div className="text-sm text-muted-foreground">
                      {entry.definition}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {entry.category} • {formatDate(entry.createdAt)}
                    </div>
                  </div>
                  <Badge variant="outline">
                    {entry.category}
                  </Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setEditingEntry(entry)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    编辑
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDeleteEntry(entry.id)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    删除
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 分页 */}
      <div className="flex justify-center space-x-2">
        <Button
          variant="outline"
          onClick={() => setPage(Math.max(1, page - 1))}
          disabled={page === 1}
        >
          上一页
        </Button>
        <span className="flex items-center px-4">
          第 {page} 页，共 {totalPages} 页
        </span>
        <Button
          variant="outline"
          onClick={() => setPage(Math.min(totalPages, page + 1))}
          disabled={page === totalPages}
        >
          下一页
        </Button>
      </div>

      {/* 词汇编辑对话框 */}
      <VocabularyEditDialog
        entry={editingEntry}
        isOpen={!!editingEntry}
        onClose={() => setEditingEntry(null)}
        onSave={handleEntrySave}
      />

      {/* 词汇创建对话框 */}
      <VocabularyCreateDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onSave={handleEntryCreate}
      />
    </div>
  );
}

// 主管理员页面组件
export default function AdminPage() {
  const t = useTranslation();
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [statsError, setStatsError] = useState<string>("");

  const loadSystemStats = async () => {
    try {
      setStatsLoading(true);
      const stats = await adminApi.getSystemStats();
      setSystemStats(stats);
      setStatsError("");
    } catch (err) {
      setStatsError(err instanceof Error ? err.message : "加载系统统计失败");
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    loadSystemStats();
  }, []);

  return (
    <AdminGuard>
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            {/* 页面标题 */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">系统管理</h1>
                <p className="text-muted-foreground">
                  管理用户权限、知识库文件和专业词汇
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <Settings className="h-5 w-5 text-muted-foreground" />
                <Shield className="h-5 w-5 text-muted-foreground" />
              </div>
            </div>

            {/* 系统统计 */}
            {statsLoading ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                <span>加载系统统计中...</span>
              </div>
            ) : statsError ? (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{statsError}</AlertDescription>
              </Alert>
            ) : systemStats ? (
              <SystemStatsCard stats={systemStats} />
            ) : null}

            {/* 管理功能标签页 */}
            <Tabs defaultValue="users" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="users" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>用户管理</span>
                </TabsTrigger>
                <TabsTrigger value="knowledge" className="flex items-center space-x-2">
                  <Database className="h-4 w-4" />
                  <span>知识库</span>
                </TabsTrigger>
                <TabsTrigger value="vocabulary" className="flex items-center space-x-2">
                  <BookOpen className="h-4 w-4" />
                  <span>专业词汇</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="users" className="mt-6">
                <UserManagement />
              </TabsContent>

              <TabsContent value="knowledge" className="mt-6">
                <KnowledgeManagement />
              </TabsContent>

              <TabsContent value="vocabulary" className="mt-6">
                <VocabularyManagement />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </AdminGuard>
  );
}
