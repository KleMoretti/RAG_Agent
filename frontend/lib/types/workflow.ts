/**
 * 工艺流程类型定义
 */

export interface ProcessNode {
    id: string;
    name: string;
    type: "process" | "equipment" | "inspection" | "material";
    description: string;
    position: { x: number; y: number };
    status?: "normal" | "warning" | "error" | "optimizing";
    parameters?: ProcessParameter[];
    relatedDocs?: string[]; // 关联文档ID
    icon?: string;
}

export interface ProcessParameter {
    name: string;
    standardValue: string | number;
    unit: string;
    actualValue?: string | number;
    range?: {
        min: number;
        max: number;
    };
    isOutOfRange?: boolean;
}

export interface ProcessEdge {
    id: string;
    source: string;
    target: string;
    label?: string;
    type?: "material" | "energy" | "data";
}

export interface ProcessFlow {
    nodes: ProcessNode[];
    edges: ProcessEdge[];
}

export interface WorkflowDocument {
    id: string;
    fileName: string;
    type: "SOP" | "工艺卡片" | "作业指导书" | "异常处理手册" | "工艺变更";
    relatedNodes: string[];
    uploadedAt: string;
}

