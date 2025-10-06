import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import { FileUploadResponse } from '../types/api';

/**
 * File upload API methods
 */
export const uploadApi = {
  /**
   * Upload a file
   */
  async uploadFile(file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<FileUploadResponse>(
      API_ENDPOINTS.UPLOAD,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};

/**
 * Helper function to upload file (exported for direct use)
 */
export async function uploadFile(file: File): Promise<FileUploadResponse> {
  return uploadApi.uploadFile(file);
}
