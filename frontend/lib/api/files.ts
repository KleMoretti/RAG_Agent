import type { AxiosProgressEvent } from 'axios';
import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import type { FileUploadResponse } from '../types/api';

/**
 * Upload a single file to the chat upload endpoint.
 * Accepts an optional progress callback for UI updates.
 */
export async function uploadChatFile(
  file: File,
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void
): Promise<FileUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<FileUploadResponse>(
    API_ENDPOINTS.UPLOAD,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    }
  );

  return response.data;
}
