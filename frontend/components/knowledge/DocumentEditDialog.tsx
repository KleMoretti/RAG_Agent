"use client";

import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, X, Tag } from "lucide-react";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { updateDocument } from "@/lib/api/documents";
import type { DocumentMetadata, DocumentUpdateRequest } from "@/lib/types/api";

interface DocumentEditDialogProps {
    document: DocumentMetadata | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function DocumentEditDialog({
    document,
    open,
    onOpenChange,
}: DocumentEditDialogProps) {
    const [fileName, setFileName] = useState("");
    const [description, setDescription] = useState("");
    const [tags, setTags] = useState<string[]>([]);
    const [tagInput, setTagInput] = useState("");

    const queryClient = useQueryClient();

    // 当文档改变时更新表单
    useEffect(() => {
        if (document) {
            setFileName(document.fileName);
            setDescription(document.description || "");
            setTags(document.tags || []);
        } else {
            resetForm();
        }
    }, [document]);

    const resetForm = () => {
        setFileName("");
        setDescription("");
        setTags([]);
        setTagInput("");
    };

    // 更新文档mutation
    const updateMutation = useMutation({
        mutationFn: (updates: DocumentUpdateRequest) => {
            if (!document) throw new Error("No document selected");
            return updateDocument(document.id, updates);
        },
        onSuccess: () => {
            toast.success("更新成功", {
                description: "文档元数据已成功更新",
            });
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            onOpenChange(false);
            resetForm();
        },
        onError: (error: unknown) => {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : (error as { response?: { data?: { detail?: string } } })
                          ?.response?.data?.detail || "更新文档时出错";
            toast.error("更新失败", {
                description: errorMessage,
            });
        },
    });

    const handleAddTag = () => {
        const trimmedTag = tagInput.trim();
        if (trimmedTag && !tags.includes(trimmedTag)) {
            setTags([...tags, trimmedTag]);
            setTagInput("");
        }
    };

    const handleRemoveTag = (tagToRemove: string) => {
        setTags(tags.filter((tag) => tag !== tagToRemove));
    };

    const handleTagInputKeyDown = (
        e: React.KeyboardEvent<HTMLInputElement>,
    ) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleAddTag();
        } else if (e.key === "Backspace" && !tagInput && tags.length > 0) {
            // 如果输入框为空且按下退格键，删除最后一个标签
            setTags(tags.slice(0, -1));
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const updates: DocumentUpdateRequest = {
            fileName: fileName !== document?.fileName ? fileName : undefined,
            description:
                description !== (document?.description || "")
                    ? description
                    : undefined,
            tags:
                tags.length > 0 || (document?.tags && document.tags.length > 0)
                    ? tags
                    : undefined,
        };

        // 只提交有变化的字段
        const hasChanges =
            updates.fileName ||
            updates.description !== undefined ||
            updates.tags;

        if (!hasChanges) {
            toast.info("无变化", {
                description: "没有检测到任何更改",
            });
            return;
        }

        updateMutation.mutate(updates);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                    <DialogTitle>编辑文档元数据</DialogTitle>
                    <DialogDescription>
                        修改文档的名称、描述和标签信息
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* 文件名 */}
                    <div className="space-y-2">
                        <Label htmlFor="fileName">文件名</Label>
                        <Input
                            id="fileName"
                            value={fileName}
                            onChange={(e) => setFileName(e.target.value)}
                            placeholder="输入文件名"
                            required
                        />
                        <p className="text-sm text-muted-foreground">
                            修改文件名不会改变实际文件，仅用于显示
                        </p>
                    </div>

                    {/* 描述 */}
                    <div className="space-y-2">
                        <Label htmlFor="description">描述</Label>
                        <Textarea
                            id="description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="添加文档描述（可选）"
                            rows={4}
                            className="resize-none"
                        />
                        <p className="text-sm text-muted-foreground">
                            简要描述文档内容，便于后续检索
                        </p>
                    </div>

                    {/* 标签 */}
                    <div className="space-y-2">
                        <Label htmlFor="tags">标签</Label>
                        <div className="flex flex-wrap gap-2 mb-2">
                            {tags.map((tag) => (
                                <Badge
                                    key={tag}
                                    variant="secondary"
                                    className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground transition-colors"
                                    onClick={() => handleRemoveTag(tag)}
                                >
                                    {tag}
                                    <X className="h-3 w-3 ml-1" />
                                </Badge>
                            ))}
                        </div>
                        <div className="flex gap-2">
                            <Input
                                id="tags"
                                value={tagInput}
                                onChange={(e) => setTagInput(e.target.value)}
                                onKeyDown={handleTagInputKeyDown}
                                placeholder="输入标签后按回车"
                            />
                            <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={handleAddTag}
                                disabled={!tagInput.trim()}
                            >
                                <Tag className="h-4 w-4 mr-1" />
                                添加
                            </Button>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            添加标签以便分类和检索，按回车或点击添加按钮
                        </p>
                    </div>

                    {/* 文档信息 */}
                    {document && (
                        <div className="border-t pt-4 space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">
                                    文件大小:
                                </span>
                                <span>
                                    {document.fileSize
                                        ? `${(document.fileSize / 1024).toFixed(2)} KB`
                                        : "未知"}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">
                                    上传时间:
                                </span>
                                <span>
                                    {new Date(
                                        document.uploadDate,
                                    ).toLocaleString("zh-CN")}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">
                                    上传者:
                                </span>
                                <span>{document.uploaderName || "未知"}</span>
                            </div>
                            {document.chunkCount !== undefined && (
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">
                                        文档块数:
                                    </span>
                                    <span>{document.chunkCount}</span>
                                </div>
                            )}
                        </div>
                    )}

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                                onOpenChange(false);
                                resetForm();
                            }}
                        >
                            取消
                        </Button>
                        <Button
                            type="submit"
                            disabled={updateMutation.isPending}
                        >
                            {updateMutation.isPending ? (
                                <>
                                    <Save className="h-4 w-4 mr-2 animate-spin" />
                                    保存中...
                                </>
                            ) : (
                                <>
                                    <Save className="h-4 w-4 mr-2" />
                                    保存更改
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
