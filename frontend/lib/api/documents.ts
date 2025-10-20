import type { AxiosProgressEvent } from 'axios';
import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import type {
    DocumentMetadata,
    DocumentListResponse,
    DocumentUpdateRequest,
    DocumentDeleteResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
} from '../types/api';

/**
 * 获取文档列表
 * @param page - 页码（从1开始）
 * @param pageSize - 每页数量
 * @param search - 搜索关键词
 */
export async function getDocuments(
    page: number = 1,
    pageSize: number = 20,
    search?: string
): Promise<DocumentListResponse> {
    const params: Record<string, string | number> = {
        page,
        page_size: pageSize,
    };

    if (search) {
        params.search = search;
    }

    const response = await apiClient.get<DocumentListResponse>(
        API_ENDPOINTS.KNOWLEDGE_FILES,
        { params }
    );

    return response.data;
}

/**
 * 获取单个文档详情
 * @param fileId - 文档ID
 */
export async function getDocument(fileId: string): Promise<DocumentMetadata> {
    const response = await apiClient.get<DocumentMetadata>(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/${fileId}`
    );

    return response.data;
}

/**
 * 更新文档元数据
 * @param fileId - 文档ID
 * @param updates - 更新内容
 */
export async function updateDocument(
    fileId: string,
    updates: DocumentUpdateRequest
): Promise<DocumentMetadata> {
    const response = await apiClient.put<DocumentMetadata>(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/${fileId}`,
        updates
    );

    return response.data;
}

/**
 * 删除单个文档
 * @param fileName - 文件名
 */
export async function deleteDocument(
    fileName: string
): Promise<DocumentDeleteResponse> {
    const response = await apiClient.delete<DocumentDeleteResponse>(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/${fileName}`
    );

    return response.data;
}

/**
 * 批量删除文档
 * @param fileNames - 文件名数组
 */
export async function batchDeleteDocuments(
    fileNames: string[]
): Promise<BatchDeleteResponse> {
    const response = await apiClient.post<BatchDeleteResponse>(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/batch-delete`,
        { fileNames }
    );

    return response.data;
}

/**
 * 下载文档
 * @param fileName - 文件名
 */
export async function downloadDocument(fileName: string): Promise<Blob> {
    const response = await apiClient.get(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/${fileName}/download`,
        {
            responseType: 'blob',
        }
    );

    return response.data;
}

/**
 * 预览文档内容
 * @param fileName - 文件名
 */
export async function previewDocument(fileName: string): Promise<{
    content: string;
    contentType: string;
    chunks?: Array<{ content: string; type: string; length: number }>;
}> {
    const response = await apiClient.get(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/${fileName}/preview`
    );

    return response.data;
}

/**
 * 重新索引文档
 * @param fileName - 文件名
 */
export async function reindexDocument(fileName: string): Promise<{
    message: string;
    chunkCount: number;
}> {
    const response = await apiClient.post(
        `${API_ENDPOINTS.KNOWLEDGE_FILES}/${fileName}/reindex`
    );

    return response.data;
}
