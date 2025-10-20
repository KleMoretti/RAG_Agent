"use client";

import { useState, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, X, FileText, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { uploadChatFile } from "@/lib/api/files";
import { formatBytes } from "@/lib/utils";

interface FileUploadDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

interface UploadingFile {
    file: File;
    progress: number;
    status: "pending" | "uploading" | "success" | "error";
    error?: string;
}

export function FileUploadDialog({
    open,
    onOpenChange,
}: FileUploadDialogProps) {
    const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const queryClient = useQueryClient();

    // 支持的文件类型
    const SUPPORTED_TYPES = [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".xml",
    ];

    const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

    // 上传单个文件
    const uploadMutation = useMutation({
        mutationFn: async ({
            file,
            index,
        }: {
            file: File;
            index: number;
        }) => {
            return uploadChatFile(file, (progressEvent) => {
                if (progressEvent.total) {
                    const progress = Math.round(
                        (progressEvent.loaded * 100) / progressEvent.total
                    );
                    setUploadingFiles((prev) =>
                        prev.map((f, i) =>
                            i === index
                                ? { ...f, progress, status: "uploading" }
                                : f
                        )
                    );
                }
            });
        },
        onSuccess: (data, variables) => {
            setUploadingFiles((prev) =>
                prev.map((f, i) =>
                    i === variables.index
                        ? { ...f, status: "success", progress: 100 }
                        : f
                )
            );
            queryClient.invalidateQueries({ queryKey: ["documents"] });
        },
        onError: (error: unknown, variables) => {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "上传失败";

            setUploadingFiles((prev) =>
                prev.map((f, i) =>
                    i === variables.index
                        ? { ...f, status: "error", error: errorMessage }
                        : f
                )
            );
        },
    });

    // 验证文件
    const validateFile = (file: File): string | null => {
        // 检查文件大小
        if (file.size > MAX_FILE_SIZE) {
            return `文件大小超过限制 (${formatBytes(MAX_FILE_SIZE)})`;
        }

        // 检查文件类型
        const fileExt = "." + file.name.split(".").pop()?.toLowerCase();
        if (!SUPPORTED_TYPES.includes(fileExt)) {
            return `不支持的文件类型。支持: ${SUPPORTED_TYPES.join(", ")}`;
        }

        return null;
    };

    // 处理文件选择
    const handleFileSelect = (files: FileList | null) => {
        if (!files || files.length === 0) return;

        const newFiles: UploadingFile[] = [];
        const validFiles: File[] = [];

        Array.from(files).forEach((file) => {
            const error = validateFile(file);
            if (error) {
                toast.error(`${file.name}: ${error}`);
            } else {
                newFiles.push({
                    file,
                    progress: 0,
                    status: "pending",
                });
                validFiles.push(file);
            }
        });

        if (newFiles.length === 0) return;

        setUploadingFiles((prev) => [...prev, ...newFiles]);

        // 开始上传所有有效文件
        const startIndex = uploadingFiles.length;
        validFiles.forEach((file, i) => {
            uploadMutation.mutate({
                file,
                index: startIndex + i,
            });
        });
    };

    // 拖拽事件处理
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        handleFileSelect(e.dataTransfer.files);
    };

    // 移除文件
    const handleRemoveFile = (index: number) => {
        setUploadingFiles((prev) => prev.filter((_, i) => i !== index));
    };

    // 关闭对话框
    const handleClose = () => {
        const hasUploading = uploadingFiles.some(
            (f) => f.status === "uploading"
        );
        if (hasUploading) {
            toast.error("请等待所有文件上传完成");
            return;
        }

        // 如果有成功上传的文件，显示通知
        const successCount = uploadingFiles.filter(
            (f) => f.status === "success"
        ).length;
        if (successCount > 0) {
            toast.success(`成功上传 ${successCount} 个文件`);
        }

        setUploadingFiles([]);
        onOpenChange(false);
    };

    // 重试失败的文件
    const handleRetry = (index: number) => {
        const file = uploadingFiles[index].file;
        setUploadingFiles((prev) =>
            prev.map((f, i) =>
                i === index ? { ...f, status: "pending", progress: 0 } : f
            )
        );
        uploadMutation.mutate({ file, index });
    };

    // 计算统计信息
    const stats = {
        total: uploadingFiles.length,
        success: uploadingFiles.filter((f) => f.status === "success").length,
        error: uploadingFiles.filter((f) => f.status === "error").length,
        uploading: uploadingFiles.filter((f) => f.status === "uploading")
            .length,
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>上传文档</DialogTitle>
                    <DialogDescription>
                        上传文档到知识库。支持格式：{SUPPORTED_TYPES.join(", ")}
                        <br />
                        最大文件大小：{formatBytes(MAX_FILE_SIZE)}
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    {/* 拖拽上传区域 */}
                    <div
                        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                            isDragging
                                ? "border-primary bg-primary/5"
                                : "border-muted-foreground/25 hover:border-primary/50"
                        }`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                        <div className="space-y-2">
                            <p className="text-sm font-medium">
                                拖拽文件到这里，或点击选择文件
                            </p>
                            <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                选择文件
                            </Button>
                        </div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept={SUPPORTED_TYPES.join(",")}
                            className="hidden"
                            onChange={(e) => handleFileSelect(e.target.files)}
                        />
                    </div>

                    {/* 文件列表 */}
                    {uploadingFiles.length > 0 && (
                        <div className="space-y-2 max-h-[300px] overflow-y-auto">
                            {uploadingFiles.map((uploadFile, index) => (
                                <div
                                    key={index}
                                    className="border rounded-lg p-3 space-y-2"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex items-start gap-2 flex-1 min-w-0">
                                            <FileText className="h-5 w-5 mt-0.5 flex-shrink-0 text-muted-foreground" />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium truncate">
                                                    {uploadFile.file.name}
                                                </p>
                                                <p className="text-xs text-muted-foreground">
                                                    {formatBytes(
                                                        uploadFile.file.size
                                                    )}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-2 flex-shrink-0">
                                            {uploadFile.status ===
                                                "success" && (
                                                <CheckCircle2 className="h-5 w-5 text-green-500" />
                                            )}
                                            {uploadFile.status === "error" && (
                                                <Button
                                                    type="button"
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() =>
                                                        handleRetry(index)
                                                    }
                                                >
                                                    重试
                                                </Button>
                                            )}
                                            {uploadFile.status ===
                                                "uploading" && (
                                                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                                            )}
                                            {(uploadFile.status === "pending" ||
                                                uploadFile.status ===
                                                    "error") && (
                                                <Button
                                                    type="button"
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() =>
                                                        handleRemoveFile(index)
                                                    }
                                                >
                                                    <X className="h-4 w-4" />
                                                </Button>
                                            )}
                                        </div>
                                    </div>

                                    {/* 进度条 */}
                                    {(uploadFile.status === "uploading" ||
                                        uploadFile.status === "success") && (
                                        <Progress value={uploadFile.progress} />
                                    )}

                                    {/* 错误信息 */}
                                    {uploadFile.status === "error" && (
                                        <div className="flex items-start gap-2 text-sm text-destructive">
                                            <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                                            <p>{uploadFile.error}</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* 统计信息 */}
                    {uploadingFiles.length > 0 && (
                        <div className="text-xs text-muted-foreground space-y-1">
                            <p>
                                总计：{stats.total} 个文件 | 成功：
                                {stats.success} | 失败：{stats.error}
                                {stats.uploading > 0 &&
                                    ` | 上传中：${stats.uploading}`}
                            </p>
                        </div>
                    )}
                </div>

                <DialogFooter>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={handleClose}
                        disabled={stats.uploading > 0}
                    >
                        {stats.uploading > 0 ? "上传中..." : "完成"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
