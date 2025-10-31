import type { AxiosProgressEvent } from 'axios';
import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import type { FileUploadResponse } from '../types/api';

/**
 * Upload a single file with optional upload type specification.
 * 
 * @param file - The file to upload
 * @param uploadType - Where to store the file: "knowledge_base" (managed knowledge) or "user_upload" (temporary, default)
 * @param onUploadProgress - Optional progress callback for UI updates
 */
export async function uploadChatFile(
  file: File,
  uploadType: 'knowledge_base' | 'user_upload' = 'user_upload',
  onUploadProgress?: (progressEvent: AxiosProgressEvent) => void
): Promise<FileUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('upload_type', uploadType);

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
