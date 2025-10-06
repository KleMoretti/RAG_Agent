"use client";

import * as React from "react";
import { useState, useCallback } from "react";
import { Upload, X, FileText, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { uploadFile } from "@/lib/api/upload";
import type { FileUploadResponse } from "@/lib/types/api";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface FileUploadProps {
  onUploadSuccess?: (response: FileUploadResponse) => void;
  onUploadError?: (error: string) => void;
  onClose?: () => void;
  maxSizeMB?: number;
  acceptedTypes?: string[];
}

export function FileUpload({
  onUploadSuccess,
  onUploadError,
  onClose,
  maxSizeMB = 10,
  acceptedTypes = [
    '.txt', '.md', '.pdf', '.doc', '.docx',
    '.py', '.js', '.ts', '.json', '.csv'
  ],
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<FileUploadResponse | null>(null);
  const [error, setError] = useState<string>("");
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxSizeBytes) {
      return `文件大小超过限制 (${maxSizeMB}MB)`;
    }

    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (acceptedTypes.length > 0 && !acceptedTypes.includes(extension)) {
      return `不支持的文件类型: ${extension}`;
    }

    return null;
  };

  const handleFileUpload = useCallback(async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      onUploadError?.(validationError);
      return;
    }

    setIsUploading(true);
    setError("");
    setUploadResult(null);

    try {
      const response = await uploadFile(file);
      
      if (response.success) {
        setUploadResult(response);
        onUploadSuccess?.(response);
      } else {
        const errorMsg = response.message || "上传失败";
        setError(errorMsg);
        onUploadError?.(errorMsg);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "上传文件时发生错误";
      setError(errorMsg);
      onUploadError?.(errorMsg);
    } finally {
      setIsUploading(false);
    }
  }, [maxSizeBytes, acceptedTypes, onUploadSuccess, onUploadError]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]); // Only handle first file
    }
  }, [handleFileUpload]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, [handleFileUpload]);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">上传文件</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 hover:bg-accent rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Drag and drop area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-border hover:border-primary/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
        />

        {isUploading ? (
          <div className="space-y-3">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto" />
            <p className="text-sm text-muted-foreground">上传中...</p>
          </div>
        ) : uploadResult ? (
          <div className="space-y-3">
            <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto" />
            <p className="text-sm font-medium text-green-600">
              {uploadResult.message}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <Upload className="w-12 h-12 text-muted-foreground mx-auto" />
            <div>
              <p className="text-sm font-medium">
                拖拽文件到此处或{' '}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="text-primary hover:underline"
                >
                  选择文件
                </button>
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                支持的格式: {acceptedTypes.join(', ')} (最大 {maxSizeMB}MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Upload result details */}
      {uploadResult && uploadResult.success && (
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
            <FileText className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0 space-y-1">
              <p className="text-sm font-medium truncate">
                {uploadResult.fileName}
              </p>
              <div className="flex gap-4 text-xs text-muted-foreground">
                <span>大小: {formatFileSize(uploadResult.fileSize || 0)}</span>
                <span>类型: {uploadResult.contentType}</span>
                {uploadResult.chunks && (
                  <span>分块: {uploadResult.chunks.length}</span>
                )}
              </div>
            </div>
          </div>

          {/* Chunks preview */}
          {uploadResult.chunks && uploadResult.chunks.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">
                文件分块预览 (前3块):
              </p>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {uploadResult.chunks.slice(0, 3).map((chunk, index) => (
                  <div
                    key={index}
                    className="p-2 bg-muted/50 rounded text-xs border border-border"
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium">块 {index + 1}</span>
                      <span className="text-muted-foreground">
                        {chunk.length} 字符
                      </span>
                    </div>
                    <p className="text-muted-foreground line-clamp-2">
                      {chunk.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
