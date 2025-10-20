"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
    Search,
    Upload,
    Trash2,
    Edit,
    Eye,
    RefreshCw,
    Download,
    FileText,
    MoreVertical,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
    getDocuments,
    deleteDocument,
    batchDeleteDocuments,
    downloadDocument,
    previewDocument,
    reindexDocument,
} from "@/lib/api/documents";
import type { DocumentMetadata } from "@/lib/types/api";
import { formatBytes, formatDate } from "@/lib/utils";
import { PAGINATION } from "@/lib/constants";
import { DocumentEditDialog } from "@/components/knowledge/DocumentEditDialog";

export default function KnowledgeBasePage() {
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [pageSize] = useState(PAGINATION.DEFAULT_PAGE_SIZE);
    const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());
    const [previewDoc, setPreviewDoc] = useState<DocumentMetadata | null>(null);
    const [previewContent, setPreviewContent] = useState<string>("");
    const [isPreviewOpen, setIsPreviewOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [docToDelete, setDocToDelete] = useState<DocumentMetadata | null>(
        null,
    );
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
    const [docToEdit, setDocToEdit] = useState<DocumentMetadata | null>(null);

    const queryClient = useQueryClient();

    // 获取文档列表
    const { data, isLoading, error } = useQuery({
        queryKey: ["documents", page, pageSize, search],
        queryFn: () => getDocuments(page, pageSize, search || undefined),
    });

    // 删除单个文档
    const deleteMutation = useMutation({
        mutationFn: (fileName: string) => deleteDocument(fileName),
        onSuccess: () => {
            toast.success("删除成功", {
                description: "文档已成功删除",
            });
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            setIsDeleteDialogOpen(false);
            setDocToDelete(null);
        },
        onError: (error: unknown) => {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "删除文档时出错";
            toast.error("删除失败", {
                description: errorMessage,
            });
        },
    });

    // 批量删除文档
    const batchDeleteMutation = useMutation({
        mutationFn: (fileNames: string[]) => batchDeleteDocuments(fileNames),
        onSuccess: (data) => {
            toast.success("批量删除完成", {
                description: `成功删除 ${data.success.length} 个文档${data.failed.length > 0 ? `，${data.failed.length} 个失败` : ""}`,
            });
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            setSelectedDocs(new Set());
        },
        onError: (error: unknown) => {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "批量删除文档时出错";
            toast.error("批量删除失败", {
                description: errorMessage,
            });
        },
    });

    // 重新索引文档
    const reindexMutation = useMutation({
        mutationFn: (fileName: string) => reindexDocument(fileName),
        onSuccess: (data) => {
            toast.success("重新索引成功", {
                description: `文档已重新索引，共 ${data.chunkCount} 个文本块`,
            });
            queryClient.invalidateQueries({ queryKey: ["documents"] });
        },
        onError: (error: unknown) => {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "重新索引文档时出错";
            toast.error("重新索引失败", {
                description: errorMessage,
            });
        },
    });

    // 处理搜索
    const handleSearch = (value: string) => {
        setSearch(value);
        setPage(1); // 重置到第一页
    };

    // 处理选择文档
    const handleSelectDoc = (docId: string) => {
        const newSelected = new Set(selectedDocs);
        if (newSelected.has(docId)) {
            newSelected.delete(docId);
        } else {
            newSelected.add(docId);
        }
        setSelectedDocs(newSelected);
    };

    // 处理全选
    const handleSelectAll = () => {
        if (data?.data && selectedDocs.size === data.data.length) {
            setSelectedDocs(new Set());
        } else if (data?.data) {
            setSelectedDocs(new Set(data.data.map((doc) => doc.id)));
        }
    };

    // 处理预览
    const handlePreview = async (doc: DocumentMetadata) => {
        setPreviewDoc(doc);
        setIsPreviewOpen(true);
        setPreviewContent("加载中...");

        try {
            const preview = await previewDocument(doc.fileName);
            if (preview.chunks && preview.chunks.length > 0) {
                setPreviewContent(
                    preview.chunks.map((c) => c.content).join("\n\n"),
                );
            } else {
                setPreviewContent(preview.content || "无法预览此文件类型");
            }
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "未知错误";
            setPreviewContent("预览失败：" + errorMessage);
        }
    };

    // 处理下载
    const handleDownload = async (doc: DocumentMetadata) => {
        try {
            const blob = await downloadDocument(doc.fileName);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = doc.fileName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            toast.success("下载成功", {
                description: `${doc.fileName} 已开始下载`,
            });
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "下载文档时出错";
            toast.error("下载失败", {
                description: errorMessage,
            });
        }
    };

    // 处理删除确认
    const handleDeleteConfirm = () => {
        if (docToDelete) {
            deleteMutation.mutate(docToDelete.fileName);
        }
    };

    // 处理批量删除
    const handleBatchDelete = () => {
        if (selectedDocs.size === 0) return;

        const fileNames =
            data?.data
                ?.filter((doc) => selectedDocs.has(doc.id))
                .map((doc) => doc.fileName) || [];

        if (fileNames.length > 0) {
            batchDeleteMutation.mutate(fileNames);
        }
    };

    // 处理编辑
    const handleEdit = (doc: DocumentMetadata) => {
        setDocToEdit(doc);
        setIsEditDialogOpen(true);
    };

    // 处理重新索引
    const handleReindex = (doc: DocumentMetadata) => {
        reindexMutation.mutate(doc.fileName);
    };

    const documents = data?.data || [];
    const totalPages = data?.meta?.totalPages || 1;
    const total = data?.meta?.total || 0;

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* 页面标题 */}
            <div>
                <h1 className="text-3xl font-bold">知识库管理</h1>
                <p className="text-muted-foreground mt-2">
                    管理和查看已上传的文档，支持预览、编辑和删除操作
                </p>
            </div>

            {/* 操作栏 */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 flex-1">
                            <div className="relative flex-1 max-w-md">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    placeholder="搜索文档名称..."
                                    value={search}
                                    onChange={(e) =>
                                        handleSearch(e.target.value)
                                    }
                                    className="pl-10"
                                />
                            </div>
                            {selectedDocs.size > 0 && (
                                <Button
                                    variant="destructive"
                                    size="sm"
                                    onClick={handleBatchDelete}
                                    disabled={batchDeleteMutation.isPending}
                                >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    删除选中 ({selectedDocs.size})
                                </Button>
                            )}
                        </div>
                        <Button>
                            <Upload className="h-4 w-4 mr-2" />
                            上传文档
                        </Button>
                    </div>
                </CardHeader>
                <CardContent>
                    {/* 统计信息 */}
                    <div className="flex items-center gap-6 text-sm text-muted-foreground mb-4">
                        <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            <span>共 {total} 个文档</span>
                        </div>
                        {selectedDocs.size > 0 && (
                            <div className="flex items-center gap-2">
                                <Checkbox checked />
                                <span>已选择 {selectedDocs.size} 个</span>
                            </div>
                        )}
                    </div>

                    {/* 文档列表 */}
                    <div className="border rounded-lg">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-12">
                                        <Checkbox
                                            checked={
                                                documents.length > 0 &&
                                                selectedDocs.size ===
                                                    documents.length
                                            }
                                            onCheckedChange={handleSelectAll}
                                        />
                                    </TableHead>
                                    <TableHead>文件名</TableHead>
                                    <TableHead>大小</TableHead>
                                    <TableHead>上传时间</TableHead>
                                    <TableHead>上传者</TableHead>
                                    <TableHead>状态</TableHead>
                                    <TableHead className="text-right">
                                        操作
                                    </TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={7}
                                            className="text-center py-8"
                                        >
                                            <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                                            <p className="text-muted-foreground">
                                                加载中...
                                            </p>
                                        </TableCell>
                                    </TableRow>
                                ) : error ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={7}
                                            className="text-center py-8 text-destructive"
                                        >
                                            加载失败：
                                            {error instanceof Error
                                                ? error.message
                                                : "未知错误"}
                                        </TableCell>
                                    </TableRow>
                                ) : documents.length === 0 ? (
                                    <TableRow>
                                        <TableCell
                                            colSpan={7}
                                            className="text-center py-8"
                                        >
                                            <FileText className="h-12 w-12 mx-auto mb-2 text-muted-foreground" />
                                            <p className="text-muted-foreground">
                                                {search
                                                    ? "没有找到匹配的文档"
                                                    : "还没有上传任何文档"}
                                            </p>
                                        </TableCell>
                                    </TableRow>
                                ) : (
                                    documents.map((doc) => (
                                        <TableRow key={doc.id}>
                                            <TableCell>
                                                <Checkbox
                                                    checked={selectedDocs.has(
                                                        doc.id,
                                                    )}
                                                    onCheckedChange={() =>
                                                        handleSelectDoc(doc.id)
                                                    }
                                                />
                                            </TableCell>
                                            <TableCell className="font-medium">
                                                <div className="flex items-center gap-2">
                                                    <FileText className="h-4 w-4 text-muted-foreground" />
                                                    <span className="truncate max-w-xs">
                                                        {doc.fileName}
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                {formatBytes(doc.fileSize)}
                                            </TableCell>
                                            <TableCell>
                                                {formatDate(doc.uploadDate)}
                                            </TableCell>
                                            <TableCell>
                                                {doc.uploaderName || "未知"}
                                            </TableCell>
                                            <TableCell>
                                                {doc.isProcessed ? (
                                                    <Badge variant="default">
                                                        已处理
                                                    </Badge>
                                                ) : (
                                                    <Badge variant="secondary">
                                                        处理中
                                                    </Badge>
                                                )}
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger
                                                        asChild
                                                    >
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                        >
                                                            <MoreVertical className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                handlePreview(
                                                                    doc,
                                                                )
                                                            }
                                                        >
                                                            <Eye className="h-4 w-4 mr-2" />
                                                            预览
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                handleDownload(
                                                                    doc,
                                                                )
                                                            }
                                                        >
                                                            <Download className="h-4 w-4 mr-2" />
                                                            下载
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                handleEdit(doc)
                                                            }
                                                        >
                                                            <Edit className="h-4 w-4 mr-2" />
                                                            编辑
                                                        </DropdownMenuItem>
                                                        <DropdownMenuItem
                                                            onClick={() =>
                                                                handleReindex(
                                                                    doc,
                                                                )
                                                            }
                                                            disabled={
                                                                reindexMutation.isPending
                                                            }
                                                        >
                                                            <RefreshCw
                                                                className={`h-4 w-4 mr-2 ${reindexMutation.isPending ? "animate-spin" : ""}`}
                                                            />
                                                            重新索引
                                                        </DropdownMenuItem>
                                                        <DropdownMenuSeparator />
                                                        <DropdownMenuItem
                                                            className="text-destructive"
                                                            onClick={() => {
                                                                setDocToDelete(
                                                                    doc,
                                                                );
                                                                setIsDeleteDialogOpen(
                                                                    true,
                                                                );
                                                            }}
                                                        >
                                                            <Trash2 className="h-4 w-4 mr-2" />
                                                            删除
                                                        </DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* 分页 */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-between mt-4">
                            <p className="text-sm text-muted-foreground">
                                第 {page} 页，共 {totalPages} 页
                            </p>
                            <div className="flex items-center gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        setPage((p) => Math.max(1, p - 1))
                                    }
                                    disabled={page === 1}
                                >
                                    上一页
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() =>
                                        setPage((p) =>
                                            Math.min(totalPages, p + 1),
                                        )
                                    }
                                    disabled={page === totalPages}
                                >
                                    下一页
                                </Button>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* 预览对话框 */}
            <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
                <DialogContent className="max-w-4xl max-h-[80vh]">
                    <DialogHeader>
                        <DialogTitle>文档预览</DialogTitle>
                        <DialogDescription>
                            {previewDoc?.fileName}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="overflow-y-auto max-h-[60vh] p-4 bg-muted rounded-lg">
                        <pre className="whitespace-pre-wrap text-sm font-mono">
                            {previewContent}
                        </pre>
                    </div>
                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => setIsPreviewOpen(false)}
                        >
                            关闭
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* 删除确认对话框 */}
            <Dialog
                open={isDeleteDialogOpen}
                onOpenChange={setIsDeleteDialogOpen}
            >
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>确认删除</DialogTitle>
                        <DialogDescription>
                            确定要删除文档{" "}
                            <strong>{docToDelete?.fileName}</strong>{" "}
                            吗？此操作无法撤销。
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button
                            variant="outline"
                            onClick={() => {
                                setIsDeleteDialogOpen(false);
                                setDocToDelete(null);
                            }}
                        >
                            取消
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleDeleteConfirm}
                            disabled={deleteMutation.isPending}
                        >
                            {deleteMutation.isPending
                                ? "删除中..."
                                : "确认删除"}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* 编辑对话框 */}
            <DocumentEditDialog
                document={docToEdit}
                open={isEditDialogOpen}
                onOpenChange={setIsEditDialogOpen}
            />
        </div>
    );
}
