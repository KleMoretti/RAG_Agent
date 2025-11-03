/**
 * 工艺流程管理 API 客户端
 */

import apiClient from "./client";
import type { ProcessNode, ProcessEdge } from "@/lib/types/workflow";

// 重新导出类型，方便使用
export type { ProcessNode, ProcessEdge };

export interface WorkflowCreate {
    name: string;
    description?: string;
    template_id?: string;
    nodes: ProcessNode[];
    edges: ProcessEdge[];
    workflow_metadata?: Record<string, any>;
}

export interface WorkflowUpdate {
    name?: string;
    description?: string;
    is_active?: boolean;
    nodes?: ProcessNode[];
    edges?: ProcessEdge[];
    workflow_metadata?: Record<string, any>;
}

export interface WorkflowResponse {
    id: number;
    name: string;
    description: string | null;
    template_id: string | null;
    is_custom: boolean;
    is_active: boolean;
    nodes: ProcessNode[];
    edges: ProcessEdge[];
    workflow_metadata: Record<string, any> | null;
    created_at: string;
    updated_at: string;
    created_by: number | null;
}

/**
 * 创建自定义工艺流程
 */
export async function createWorkflow(data: WorkflowCreate): Promise<WorkflowResponse> {
    const response = await apiClient.post<WorkflowResponse>("/api/workflow/workflows", data);
    return response.data;
}

/**
 * 获取工艺流程列表
 */
export async function listWorkflows(params?: {
    is_active?: boolean;
    is_custom?: boolean;
}): Promise<WorkflowResponse[]> {
    const response = await apiClient.get<WorkflowResponse[]>("/api/workflow/workflows", {
        params,
    });
    return response.data;
}

/**
 * 获取单个工艺流程详情
 */
export async function getWorkflow(workflowId: number): Promise<WorkflowResponse> {
    const response = await apiClient.get<WorkflowResponse>(
        `/api/workflow/workflows/${workflowId}`
    );
    return response.data;
}

/**
 * 更新工艺流程
 */
export async function updateWorkflow(
    workflowId: number,
    data: WorkflowUpdate
): Promise<WorkflowResponse> {
    const response = await apiClient.put<WorkflowResponse>(
        `/api/workflow/workflows/${workflowId}`,
        data
    );
    return response.data;
}

/**
 * 删除工艺流程
 */
export async function deleteWorkflow(workflowId: number): Promise<void> {
    await apiClient.delete(`/api/workflow/workflows/${workflowId}`);
}

