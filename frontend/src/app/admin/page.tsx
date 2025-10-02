"use client";
import {useState, useEffect} from "react";
import {useRouter} from "next/navigation";
import {useAuth} from "@/lib/auth";
import {Button} from "@/components/ui/button";
import {Card} from "@/components/ui/card";
import {Badge} from "@/components/ui/badge";
import {Separator} from "@/components/ui/separator";
import {
    Users,
    FileText,
    Settings,
    BarChart3,
    Plus,
    Search,
    Filter,
    MoreHorizontal,
    Edit
} from "lucide-react";
import { UserPermissionsModal } from "@/components/user-permissions-modal";

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

interface FileInfo {
    file_name: string;
    file_size: number;
    upload_time: string;
    uploader: string | null;
    file_path: string;
}

interface SystemStats {
    users: {
        total: number;
        active: number;
        admins: number;
        regular: number;
    };
    files: {
        count: number;
        total_size: number;
        total_size_mb: number;
    };
}

export default function AdminPage() {
    const router = useRouter();
    const {user, isLoading} = useAuth();
    const [activeTab, setActiveTab] = useState<"users" | "files" | "stats">("users");
    const [users, setUsers] = useState<User[]>([]);
    const [files, setFiles] = useState<FileInfo[]>([]);
    const [stats, setStats] = useState<SystemStats | null>(null);
    const [loading, setLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [selectedUser, setSelectedUser] = useState<User | null>(null);
    const [showUserModal, setShowUserModal] = useState(false);

    // 检查权限
    useEffect(() => {
        if (isLoading) return;
        if (!user) {
            router.replace(`/login?next=${encodeURIComponent("/admin")}`);
            return;
        }
        if (user.role !== "admin") {
            router.replace("/chat");
        }
    }, [user, isLoading, router]);

    // 获取用户列表
    const fetchUsers = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/api/admin/users?page=${page}&page_size=10&search=${searchTerm}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setUsers(data.users);
                setTotalPages(Math.ceil(data.total / 10));
            }
        } catch (error) {
            console.error("Failed to fetch users:", error);
        } finally {
            setLoading(false);
        }
    };

    // 获取文件列表
    const fetchFiles = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/api/admin/files?page=${page}&page_size=10&search=${searchTerm}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setFiles(data.files);
                setTotalPages(Math.ceil(data.total / 10));
            }
        } catch (error) {
            console.error("Failed to fetch files:", error);
        } finally {
            setLoading(false);
        }
    };

    // 获取系统统计
    const fetchStats = async () => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch("http://localhost:8000/api/admin/stats", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error("Failed to fetch stats:", error);
        }
    };

    // 删除用户
    const deleteUser = async (userId: number) => {
        if (!confirm("确定要删除这个用户吗？")) return;

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/api/admin/users/${userId}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                fetchUsers();
            } else {
                alert("删除失败");
            }
        } catch (error) {
            console.error("Failed to delete user:", error);
            alert("删除失败");
        }
    };

    // 删除文件
    const deleteFile = async (fileName: string) => {
        if (!confirm("确定要删除这个文件吗？")) return;

        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/api/admin/files/${fileName}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                fetchFiles();
            } else {
                alert("删除失败");
            }
        } catch (error) {
            console.error("Failed to delete file:", error);
            alert("删除失败");
        }
    };

    // 切换用户状态
    const toggleUserStatus = async (userId: number, isActive: boolean) => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/api/admin/users/${userId}`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({is_active: !isActive}),
            });
            if (response.ok) {
                fetchUsers();
            } else {
                alert("更新失败");
            }
        } catch (error) {
            console.error("Failed to update user:", error);
            alert("更新失败");
        }
    };

    // 编辑用户权限
    const editUserPermissions = (user: User) => {
        setSelectedUser(user);
        setShowUserModal(true);
    };

    // 用户更新后的回调
    const handleUserUpdated = () => {
        fetchUsers();
    };

    useEffect(() => {
        if (user && user.role === "admin") {
            if (activeTab === "users") {
                fetchUsers();
            } else if (activeTab === "files") {
                fetchFiles();
            } else if (activeTab === "stats") {
                fetchStats();
            }
        }
    }, [activeTab, page, searchTerm, user]);

    if (isLoading) {
        return <div className="min-h-screen flex items-center justify-center">加载中...</div>;
    }

    if (!user || user.role !== "admin") {
        return null;
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* 头部 */}
            <div className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center">
                            <h1 className="text-xl font-semibold text-gray-900">管理员控制台</h1>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-500">欢迎，{user.username}</span>
                            <Button
                                variant="outline"
                                onClick={() => router.push("/chat")}
                            >
                                返回聊天
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* 标签页 */}
                <div className="flex space-x-8 mb-8">
                    <button
                        onClick={() => setActiveTab("users")}
                        className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md ${
                            activeTab === "users"
                                ? "bg-blue-100 text-blue-700"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        <Users className="h-4 w-4"/>
                        <span>用户管理</span>
                    </button>
                    <button
                        onClick={() => setActiveTab("files")}
                        className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md ${
                            activeTab === "files"
                                ? "bg-blue-100 text-blue-700"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        <FileText className="h-4 w-4"/>
                        <span>文件管理</span>
                    </button>
                    <button
                        onClick={() => setActiveTab("stats")}
                        className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-md ${
                            activeTab === "stats"
                                ? "bg-blue-100 text-blue-700"
                                : "text-gray-500 hover:text-gray-700"
                        }`}
                    >
                        <BarChart3 className="h-4 w-4"/>
                        <span>系统统计</span>
                    </button>
                </div>

                {/* 搜索栏 */}
                {(activeTab === "users" || activeTab === "files") && (
                    <div className="mb-6">
                        <div className="flex space-x-4">
                            <div className="flex-1 relative">
                                <Search
                                    className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400"/>
                                <input
                                    type="text"
                                    placeholder={`搜索${activeTab === "users" ? "用户" : "文件"}...`}
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <Button onClick={() => setPage(1)}>
                                搜索
                            </Button>
                        </div>
                    </div>
                )}

                {/* 内容区域 */}
                {activeTab === "users" && (
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <h2 className="text-lg font-medium text-gray-900">用户列表</h2>
                            <Button>
                                <Plus className="h-4 w-4 mr-2"/>
                                添加用户
                            </Button>
                        </div>

                        <Card className="overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            用户名
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            角色
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            状态
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            权限
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            最后登录
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            操作
                                        </th>
                                    </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                    {users.map((user) => (
                                        <tr key={user.id}>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="text-sm font-medium text-gray-900">{user.username}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <Badge variant={user.role === "admin" ? "default" : "secondary"}>
                                                    {user.role === "admin" ? "管理员" : "普通用户"}
                                                </Badge>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <Badge variant={user.is_active ? "default" : "destructive"}>
                                                    {user.is_active ? "活跃" : "禁用"}
                                                </Badge>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                <div className="flex space-x-1">
                                                    {user.can_upload &&
                                                        <Badge variant="outline" className="text-xs">上传</Badge>}
                                                    {user.can_download &&
                                                        <Badge variant="outline" className="text-xs">下载</Badge>}
                                                    {user.can_chat &&
                                                        <Badge variant="outline" className="text-xs">聊天</Badge>}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {user.last_login ? new Date(user.last_login).toLocaleString() : "从未登录"}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <div className="flex space-x-2">
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => editUserPermissions(user)}
                                                    >
                                                        <Edit className="h-3 w-3 mr-1" />
                                                        编辑
                                                    </Button>

                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => toggleUserStatus(user.id, user.is_active)}
                                                    >
                                                        {user.is_active ? "禁用" : "启用"}
                                                    </Button>

                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
                                                        onClick={() => deleteUser(user.id)}
                                                    >
                                                        删除
                                                    </Button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>

                        {/* 分页 */}
                        <div className="flex justify-center space-x-2">
                            <Button
                                variant="outline"
                                onClick={() => setPage(Math.max(1, page - 1))}
                                disabled={page === 1}
                            >
                                上一页
                            </Button>
                            <span className="flex items-center px-4 py-2 text-sm text-gray-700">
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
                )}

                {activeTab === "files" && (
                    <div className="space-y-6">
                        <div className="flex justify-between items-center">
                            <h2 className="text-lg font-medium text-gray-900">文件列表</h2>
                        </div>

                        <Card className="overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            文件名
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            大小
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            上传时间
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            操作
                                        </th>
                                    </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                    {files.map((file, index) => (
                                        <tr key={index}>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div
                                                    className="text-sm font-medium text-gray-900">{file.file_name}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {(file.file_size / 1024).toFixed(1)} KB
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(file.upload_time).toLocaleString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    className="text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
                                                    onClick={() => deleteFile(file.file_name)}
                                                >
                                                    删除
                                                </Button>
                                            </td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        </Card>
                    </div>
                )}

                {activeTab === "stats" && stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <Card className="p-6">
                            <div className="flex items-center">
                                <Users className="h-8 w-8 text-blue-600"/>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">总用户数</p>
                                    <p className="text-2xl font-semibold text-gray-900">{stats.users.total}</p>
                                </div>
                            </div>
                        </Card>

                        <Card className="p-6">
                            <div className="flex items-center">
                                <Users className="h-8 w-8 text-green-600"/>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">活跃用户</p>
                                    <p className="text-2xl font-semibold text-gray-900">{stats.users.active}</p>
                                </div>
                            </div>
                        </Card>

                        <Card className="p-6">
                            <div className="flex items-center">
                                <FileText className="h-8 w-8 text-purple-600"/>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">文件总数</p>
                                    <p className="text-2xl font-semibold text-gray-900">{stats.files.count}</p>
                                </div>
                            </div>
                        </Card>

                        <Card className="p-6">
                            <div className="flex items-center">
                                <BarChart3 className="h-8 w-8 text-orange-600"/>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">总存储</p>
                                    <p className="text-2xl font-semibold text-gray-900">{stats.files.total_size_mb} MB</p>
                                </div>
                            </div>
                        </Card>
                    </div>
                )}
            </div>

            {/* 用户权限编辑模态框 */}
            <UserPermissionsModal
                isOpen={showUserModal}
                onClose={() => {
                    setShowUserModal(false);
                    setSelectedUser(null);
                }}
                user={selectedUser}
                token={localStorage.getItem("token") || ""}
                onUserUpdated={handleUserUpdated}
            />
        </div>
    );
}
