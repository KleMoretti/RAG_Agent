import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import { User, UserRole, UserPermissions } from '../types/user';
import { PaginatedResponse, ApiResponse } from '../types/api';

/**
 * Admin API response types
 */
export interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  totalFiles: number;
  totalSessions: number;
  systemHealth: 'healthy' | 'warning' | 'error';
  lastBackup?: string;
  diskUsage: {
    total: number;
    used: number;
    free: number;
  };
}

export interface FileInfo {
  id: string;
  fileName: string;
  filePath: string;
  fileSize: number;
  contentType: string;
  uploadDate: string;
  uploaderId: string;
  uploaderName: string;
  isProcessed: boolean;
  chunkCount?: number;
}

export interface VocabularyEntry {
  id: string;
  term: string;
  definition: string;
  category: string;
  synonyms: string[];
  relatedTerms: string[];
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

export interface UpdateUserRequest {
  username?: string;
  role?: string;
  is_active?: boolean;
  can_upload?: boolean;
  can_download?: boolean;
  can_chat?: boolean;
  can_access_admin?: boolean;
  notes?: string;
}

export interface CreateUserRequest {
  username: string;
  email?: string;
  password: string;
  role: UserRole;
  permissions?: Partial<UserPermissions>;
}

/**
 * Admin API methods
 */
export const adminApi = {
  /**
   * Get system statistics
   */
  async getSystemStats(): Promise<SystemStats> {
    const response = await apiClient.get<SystemStats>(API_ENDPOINTS.SYSTEM_STATS);
    return response.data;
  },

  /**
   * Get all users with pagination
   */
  async getUsers(page = 1, pageSize = 20): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get<PaginatedResponse<User>>(
      `${API_ENDPOINTS.USERS}?page=${page}&page_size=${pageSize}`
    );
    return response.data;
  },

  /**
   * Get user by ID
   */
  async getUserById(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`${API_ENDPOINTS.USERS}/${userId}`);
    return response.data;
  },

  /**
   * Update user
   */
  async updateUser(userId: string, data: UpdateUserRequest): Promise<User> {
    const response = await apiClient.put<User>(`${API_ENDPOINTS.USERS}/${userId}`, data);
    return response.data;
  },

  /**
   * Create new user
   */
  async createUser(data: CreateUserRequest): Promise<User> {
    const response = await apiClient.post<User>(API_ENDPOINTS.USERS, data);
    return response.data;
  },

  /**
   * Delete user
   */
  async deleteUser(userId: number): Promise<void> {
    await apiClient.delete(`${API_ENDPOINTS.USERS}/${userId}`);
  },

  /**
   * Get knowledge base files
   */
  async getKnowledgeFiles(page = 1, pageSize = 20): Promise<PaginatedResponse<FileInfo>> {
    const response = await apiClient.get<PaginatedResponse<FileInfo>>(
      `/api/admin/files?page=${page}&page_size=${pageSize}`
    );
    return response.data;
  },

  /**
   * Delete knowledge base file
   */
  async deleteKnowledgeFile(fileId: string): Promise<void> {
    await apiClient.delete(`/api/admin/files/${fileId}`);
  },

  /**
   * Reprocess knowledge base file
   */
  async reprocessKnowledgeFile(fileId: string): Promise<ApiResponse> {
    const response = await apiClient.post<ApiResponse>(`/api/admin/files/${fileId}/reprocess`);
    return response.data;
  },

  /**
   * Get vocabulary entries
   */
  async getVocabularyEntries(page = 1, pageSize = 20): Promise<PaginatedResponse<VocabularyEntry>> {
    const response = await apiClient.get<PaginatedResponse<VocabularyEntry>>(
      `/api/admin/vocabulary?page=${page}&page_size=${pageSize}`
    );
    return response.data;
  },

  /**
   * Create vocabulary entry
   */
  async createVocabularyEntry(data: Omit<VocabularyEntry, 'id' | 'createdAt' | 'updatedAt' | 'createdBy'>): Promise<VocabularyEntry> {
    const response = await apiClient.post<VocabularyEntry>('/api/admin/vocabulary', data);
    return response.data;
  },

  /**
   * Update vocabulary entry
   */
  async updateVocabularyEntry(entryId: string, data: Partial<VocabularyEntry>): Promise<VocabularyEntry> {
    const response = await apiClient.put<VocabularyEntry>(`/api/admin/vocabulary/${entryId}`, data);
    return response.data;
  },

  /**
   * Delete vocabulary entry
   */
  async deleteVocabularyEntry(entryId: string): Promise<void> {
    await apiClient.delete(`/api/admin/vocabulary/${entryId}`);
  },

  /**
   * Search vocabulary entries
   */
  async searchVocabularyEntries(query: string): Promise<VocabularyEntry[]> {
    const response = await apiClient.get<VocabularyEntry[]>(`/api/admin/vocabulary/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
};
