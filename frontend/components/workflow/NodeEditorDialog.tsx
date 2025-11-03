"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import type { ProcessNode, ProcessParameter } from "@/lib/types/workflow";
import { Plus, Trash2, GripVertical } from "lucide-react";

interface NodeEditorDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    node?: ProcessNode | null;
    onSave: (node: ProcessNode, insertPosition?: InsertPosition) => void;
    mode: "add" | "edit";
    existingNodes?: ProcessNode[];
}

export interface InsertPosition {
    type: "before" | "after" | "start" | "end";
    targetNodeId?: string;
}

export function NodeEditorDialog({
    open,
    onOpenChange,
    node,
    onSave,
    mode,
    existingNodes = [],
}: NodeEditorDialogProps) {
    const [formData, setFormData] = React.useState<ProcessNode>({
        id: "",
        name: "",
        type: "process",
        description: "",
        position: { x: 0, y: 0 },
        status: "normal",
        parameters: [],
    });

    // 插入位置状态
    const [insertPosition, setInsertPosition] = React.useState<InsertPosition>({
        type: "end",
    });

    // 初始化表单数据
    React.useEffect(() => {
        if (node && mode === "edit") {
            setFormData(node);
        } else if (mode === "add") {
            setFormData({
                id: `node-${Date.now()}`,
                name: "",
                type: "process",
                description: "",
                position: { x: 0, y: 0 }, // 坐标将由插入逻辑自动计算
                status: "normal",
                parameters: [],
            });
            // 重置插入位置
            setInsertPosition({
                type: existingNodes.length === 0 ? "start" : "end",
            });
        }
    }, [node, mode, open, existingNodes.length]);

    // 添加参数
    const handleAddParameter = () => {
        const newParam: ProcessParameter = {
            name: "",
            standardValue: "",
            unit: "",
        };
        setFormData({
            ...formData,
            parameters: [...(formData.parameters || []), newParam],
        });
    };

    // 删除参数
    const handleDeleteParameter = (index: number) => {
        const newParams = [...(formData.parameters || [])];
        newParams.splice(index, 1);
        setFormData({
            ...formData,
            parameters: newParams,
        });
    };

    // 更新参数
    const handleUpdateParameter = (
        index: number,
        field: keyof ProcessParameter,
        value: string | number
    ) => {
        const newParams = [...(formData.parameters || [])];
        newParams[index] = { ...newParams[index], [field]: value };
        setFormData({
            ...formData,
            parameters: newParams,
        });
    };

    // 保存
    const handleSave = () => {
        if (!formData.name.trim()) {
            alert("请输入节点名称");
            return;
        }
        // 添加模式传递插入位置，编辑模式不传
        if (mode === "add") {
            onSave(formData, insertPosition);
        } else {
            onSave(formData);
        }
        onOpenChange(false);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-3xl h-[85vh] flex flex-col overflow-hidden">
                {/* 固定头部 */}
                <DialogHeader className="flex-shrink-0">
                    <DialogTitle>
                        {mode === "add" ? "添加工艺节点" : "编辑工艺节点"}
                    </DialogTitle>
                    <DialogDescription>
                        {mode === "add"
                            ? "填写节点基本信息和工艺参数"
                            : "修改节点信息和工艺参数"}
                    </DialogDescription>
                </DialogHeader>

                {/* 可滚动内容区 */}
                <div className="flex-1 overflow-hidden -mx-6 px-6">
                    <ScrollArea className="h-full">
                        <div className="space-y-6 py-4 pr-4 pb-16">
                        {/* 基本信息 */}
                        <div className="space-y-4">
                            <h3 className="font-semibold text-sm flex items-center gap-2">
                                <div className="size-2 rounded-full bg-primary" />
                                基本信息
                            </h3>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="name">节点名称 *</Label>
                                    <Input
                                        id="name"
                                        placeholder="例如：转炉炼钢"
                                        value={formData.name}
                                        onChange={(e) =>
                                            setFormData({ ...formData, name: e.target.value })
                                        }
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="type">节点类型</Label>
                                    <Select
                                        value={formData.type}
                                        onValueChange={(value: any) =>
                                            setFormData({ ...formData, type: value })
                                        }
                                    >
                                        <SelectTrigger id="type">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="process">工艺流程</SelectItem>
                                            <SelectItem value="equipment">设备</SelectItem>
                                            <SelectItem value="inspection">检验点</SelectItem>
                                            <SelectItem value="material">物料</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="description">描述</Label>
                                <Textarea
                                    id="description"
                                    placeholder="简要描述该工艺节点的功能和作用"
                                    rows={3}
                                    value={formData.description}
                                    onChange={(e) =>
                                        setFormData({ ...formData, description: e.target.value })
                                    }
                                />
                            </div>

                            {/* 插入位置选择器（仅添加模式） */}
                            {mode === "add" && existingNodes.length > 0 && (
                                <div className="space-y-3">
                                    <Label>插入位置</Label>
                                    <div className="grid grid-cols-2 gap-3">
                                        <Select
                                            value={insertPosition.type}
                                            onValueChange={(value: "before" | "after" | "start" | "end") => {
                                                if (value === "start" || value === "end") {
                                                    setInsertPosition({ type: value });
                                                } else {
                                                    setInsertPosition({
                                                        type: value,
                                                        targetNodeId: existingNodes[0]?.id,
                                                    });
                                                }
                                            }}
                                        >
                                            <SelectTrigger>
                                                <SelectValue placeholder="选择位置" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="start">在流程开头</SelectItem>
                                                <SelectItem value="before">在指定节点之前</SelectItem>
                                                <SelectItem value="after">在指定节点之后</SelectItem>
                                                <SelectItem value="end">在流程末尾</SelectItem>
                                            </SelectContent>
                                        </Select>

                                        {(insertPosition.type === "before" ||
                                            insertPosition.type === "after") && (
                                            <Select
                                                value={insertPosition.targetNodeId}
                                                onValueChange={(nodeId) =>
                                                    setInsertPosition({
                                                        ...insertPosition,
                                                        targetNodeId: nodeId,
                                                    })
                                                }
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="选择节点" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {existingNodes.map((n) => (
                                                        <SelectItem key={n.id} value={n.id}>
                                                            {n.name}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        )}
                                    </div>
                                    <p className="text-xs text-muted-foreground">
                                        {insertPosition.type === "start" &&
                                            "新节点将添加在流程图的最开头"}
                                        {insertPosition.type === "end" &&
                                            "新节点将添加在流程图的末尾"}
                                        {insertPosition.type === "before" &&
                                            insertPosition.targetNodeId &&
                                            `新节点将添加在"${
                                                existingNodes.find(
                                                    (n) => n.id === insertPosition.targetNodeId
                                                )?.name
                                            }"之前`}
                                        {insertPosition.type === "after" &&
                                            insertPosition.targetNodeId &&
                                            `新节点将添加在"${
                                                existingNodes.find(
                                                    (n) => n.id === insertPosition.targetNodeId
                                                )?.name
                                            }"之后`}
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* 工艺参数 */}
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-sm flex items-center gap-2">
                                    <div className="size-2 rounded-full bg-primary" />
                                    工艺参数
                                    {formData.parameters && formData.parameters.length > 0 && (
                                        <Badge variant="secondary">
                                            {formData.parameters.length} 个参数
                                        </Badge>
                                    )}
                                </h3>
                                <Button
                                    type="button"
                                    variant="outline"
                                    size="sm"
                                    onClick={handleAddParameter}
                                >
                                    <Plus className="size-4 mr-1" />
                                    添加参数
                                </Button>
                            </div>

                            {formData.parameters && formData.parameters.length > 0 ? (
                                <div className="space-y-3">
                                    {formData.parameters.map((param, index) => (
                                        <Card key={index}>
                                            <CardContent className="p-4">
                                                <div className="flex items-start gap-3">
                                                    <div className="flex-shrink-0 pt-2">
                                                        <GripVertical className="size-4 text-muted-foreground" />
                                                    </div>
                                                    <div className="flex-1 grid grid-cols-3 gap-3">
                                                        <div className="space-y-2">
                                                            <Label className="text-xs">参数名称</Label>
                                                            <Input
                                                                placeholder="例如：温度"
                                                                value={param.name}
                                                                onChange={(e) =>
                                                                    handleUpdateParameter(
                                                                        index,
                                                                        "name",
                                                                        e.target.value
                                                                    )
                                                                }
                                                            />
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label className="text-xs">标准值</Label>
                                                            <Input
                                                                placeholder="例如：1600-1650"
                                                                value={param.standardValue}
                                                                onChange={(e) =>
                                                                    handleUpdateParameter(
                                                                        index,
                                                                        "standardValue",
                                                                        e.target.value
                                                                    )
                                                                }
                                                            />
                                                        </div>
                                                        <div className="space-y-2">
                                                            <Label className="text-xs">单位</Label>
                                                            <Input
                                                                placeholder="例如：℃"
                                                                value={param.unit}
                                                                onChange={(e) =>
                                                                    handleUpdateParameter(
                                                                        index,
                                                                        "unit",
                                                                        e.target.value
                                                                    )
                                                                }
                                                            />
                                                        </div>
                                                    </div>
                                                    <Button
                                                        type="button"
                                                        variant="ghost"
                                                        size="icon"
                                                        className="flex-shrink-0"
                                                        onClick={() => handleDeleteParameter(index)}
                                                    >
                                                        <Trash2 className="size-4 text-destructive" />
                                                    </Button>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            ) : (
                                <Card className="border-dashed">
                                    <CardContent className="p-8 text-center text-muted-foreground">
                                        <p className="text-sm">暂无工艺参数</p>
                                        <p className="text-xs mt-1">点击"添加参数"按钮添加工艺参数</p>
                                    </CardContent>
                                </Card>
                            )}
                        </div>
                        </div>
                    </ScrollArea>
                </div>

                {/* 固定底部 */}
                <DialogFooter className="flex-shrink-0">
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        取消
                    </Button>
                    <Button onClick={handleSave}>
                        {mode === "add" ? "添加节点" : "保存修改"}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

