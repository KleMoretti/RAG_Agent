"use client";

import * as React from "react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { FileText, Loader2, CheckCircle2, AlertCircle, X } from "lucide-react";

export type UploadStatus = "uploading" | "processing" | "success" | "error";

interface FileUploadProgressProps {
  filename: string;
  progress: number;
  status: UploadStatus;
  error?: string;
  onCancel?: () => void;
}

export function FileUploadProgress({
  filename,
  progress,
  status,
  error,
  onCancel,
}: FileUploadProgressProps) {
  const getStatusIcon = () => {
    switch (status) {
      case "uploading":
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      default:
        return <FileText className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case "uploading":
        return `上传中... ${progress}%`;
      case "processing":
        return "处理中...";
      case "success":
        return "上传成功";
      case "error":
        return error || "上传失败";
      default:
        return "";
    }
  };

  return (
    <Card className="p-3 bg-background/50">
      <div className="flex items-start gap-3">
        <div className="shrink-0 mt-0.5">{getStatusIcon()}</div>

        <div className="flex-1 min-w-0 space-y-2">
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm font-medium truncate">{filename}</span>
            {(status === "uploading" || status === "processing") && onCancel && (
              <button
                onClick={onCancel}
                className="shrink-0 text-muted-foreground hover:text-foreground transition-colors"
                aria-label="取消上传"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {(status === "uploading" || status === "processing") && (
            <Progress value={progress} className="h-1" />
          )}

          <div
            className={`text-xs ${
              status === "error" ? "text-destructive" : "text-muted-foreground"
            }`}
          >
            {getStatusText()}
          </div>
        </div>
      </div>
    </Card>
  );
}
