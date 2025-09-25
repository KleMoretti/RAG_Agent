"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload, File, X, CheckCircle, AlertCircle } from "lucide-react";
import { uploadFile, type FileUploadResponse } from "@/lib/api";

interface FileUploadProps {
  onUploadSuccess?: (response: FileUploadResponse) => void;
  onUploadError?: (error: string) => void;
}

export function FileUpload({ onUploadSuccess, onUploadError }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<FileUploadResponse | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    if (!file) return;

    setUploading(true);
    setUploadResult(null);

    try {
      const response = await uploadFile(file);
      setUploadResult(response);
      if (response.success) {
        onUploadSuccess?.(response);
      } else {
        onUploadError?.(response.message);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "上传失败";
      setUploadResult({
        success: false,
        message: errorMessage,
      });
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  const clearResult = () => {
    setUploadResult(null);
  };

  return (
    <div className="w-full">
      <Card
        className={`border-2 border-dashed transition-colors ${
          dragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="p-6 text-center">
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleChange}
            accept=".txt,.md,.py,.js,.ts,.json,.pdf,.doc,.docx"
          />
          
          <div className="flex flex-col items-center space-y-4">
            <div className="p-3 bg-gray-100 rounded-full">
              <Upload className="h-6 w-6 text-gray-600" />
            </div>
            
            <div>
              <p className="text-lg font-medium">上传文件</p>
              <p className="text-sm text-gray-500">
                拖拽文件到此处或点击选择文件
              </p>
              <p className="text-xs text-gray-400 mt-1">
                支持 .txt, .md, .py, .js, .ts, .json 等文本文件
              </p>
            </div>
            
            <Button
              onClick={onButtonClick}
              disabled={uploading}
              variant="outline"
            >
              {uploading ? "上传中..." : "选择文件"}
            </Button>
          </div>
        </div>
      </Card>

      {uploadResult && (
        <Card className="mt-4 p-4">
          <div className="flex items-start space-x-3">
            {uploadResult.success ? (
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
            )}
            
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <p className={`font-medium ${
                  uploadResult.success ? "text-green-700" : "text-red-700"
                }`}>
                  {uploadResult.success ? "上传成功" : "上传失败"}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearResult}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <p className="text-sm text-gray-600 mt-1">
                {uploadResult.message}
              </p>
              
              {uploadResult.success && uploadResult.file_name && (
                <div className="mt-2 space-y-1">
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <File className="h-4 w-4" />
                    <span>文件名: {uploadResult.file_name}</span>
                  </div>
                  
                  {uploadResult.file_size && (
                    <p className="text-sm text-gray-500">
                      大小: {(uploadResult.file_size / 1024).toFixed(1)} KB
                    </p>
                  )}
                  
                  {uploadResult.chunks && uploadResult.chunks.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm font-medium text-gray-700">
                        内容分块 ({uploadResult.chunks.length} 个):
                      </p>
                      <div className="mt-1 space-y-2 max-h-32 overflow-y-auto">
                        {uploadResult.chunks.map((chunk, index) => (
                          <div key={index} className="p-2 bg-gray-50 rounded text-xs">
                            <div className="flex justify-between items-center mb-1">
                              <span className="font-medium">块 {index + 1}</span>
                              <span className="text-gray-500">
                                {chunk.length} 字符
                              </span>
                            </div>
                            <p className="text-gray-600 line-clamp-2">
                              {chunk.content.substring(0, 100)}
                              {chunk.content.length > 100 && "..."}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
