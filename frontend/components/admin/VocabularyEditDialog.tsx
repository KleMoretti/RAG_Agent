"use client";

import * as React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { VocabularyEntry } from "@/lib/api/admin";
import { adminApi } from "@/lib/api/admin";
import { AlertCircle, Loader2 } from "lucide-react";

interface VocabularyEditDialogProps {
  entry: VocabularyEntry | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedEntry: VocabularyEntry) => void;
}

export function VocabularyEditDialog({ entry, isOpen, onClose, onSave }: VocabularyEditDialogProps) {
  const [formData, setFormData] = useState<Partial<VocabularyEntry>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // 初始化表单数据
  React.useEffect(() => {
    if (entry) {
      setFormData({
        term: entry.term,
        definition: entry.definition,
        category: entry.category,
        synonyms: entry.synonyms.join(', '),
        relatedTerms: entry.relatedTerms.join(', '),
      });
    }
  }, [entry]);

  const handleSave = async () => {
    if (!entry) return;

    try {
      setLoading(true);
      setError("");

      const updateData = {
        term: formData.term,
        definition: formData.definition,
        category: formData.category,
        synonyms: formData.synonyms?.split(',').map(s => s.trim()).filter(s => s) || [],
        relatedTerms: formData.relatedTerms?.split(',').map(s => s.trim()).filter(s => s) || [],
      };

      const updatedEntry = await adminApi.updateVocabularyEntry(entry.id, updateData);
      onSave(updatedEntry);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "更新词汇失败");
    } finally {
      setLoading(false);
    }
  };

  if (!entry) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>编辑专业词汇</DialogTitle>
          <DialogDescription>
            修改词汇定义和相关信息
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 词汇术语 */}
          <div className="space-y-2">
            <Label htmlFor="term">词汇术语 *</Label>
            <Input
              id="term"
              value={formData.term || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, term: e.target.value }))}
              placeholder="输入词汇术语"
              required
            />
          </div>

          {/* 定义 */}
          <div className="space-y-2">
            <Label htmlFor="definition">定义 *</Label>
            <Textarea
              id="definition"
              value={formData.definition || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, definition: e.target.value }))}
              placeholder="输入词汇定义"
              rows={3}
              required
            />
          </div>

          {/* 分类 */}
          <div className="space-y-2">
            <Label htmlFor="category">分类</Label>
            <Input
              id="category"
              value={formData.category || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              placeholder="输入分类（如：设备、工艺、材料等）"
            />
          </div>

          {/* 同义词 */}
          <div className="space-y-2">
            <Label htmlFor="synonyms">同义词</Label>
            <Input
              id="synonyms"
              value={formData.synonyms || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, synonyms: e.target.value }))}
              placeholder="输入同义词，用逗号分隔"
            />
          </div>

          {/* 相关词汇 */}
          <div className="space-y-2">
            <Label htmlFor="relatedTerms">相关词汇</Label>
            <Input
              id="relatedTerms"
              value={formData.relatedTerms || ""}
              onChange={(e) => setFormData(prev => ({ ...prev, relatedTerms: e.target.value }))}
              placeholder="输入相关词汇，用逗号分隔"
            />
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
            disabled={loading || !formData.term || !formData.definition}
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            保存
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
