import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import { LoginCredentials, RegisterData, User } from '../types/user';
import axios from 'axios';
import { env } from '../env';

/**
 * Authentication API responses
 */
interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface RegisterResponse {
  message: string;
  user: User;
}

/**
 * Authentication API methods
 */
export const authApi = {
  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>(
        API_ENDPOINTS.LOGIN,
        credentials
      );
      return response.data;
    } catch (error: unknown) {
      // Extract error message from backend response
      if (error instanceof Error) {
        throw error;
      }
      
      const axiosError = error as { response?: { data?: { detail?: string }; status?: number }; message?: string };
      if (axiosError.response?.data?.detail) {
        // Backend returned a specific error message (e.g., "用户名或密码错误")
        throw new Error(axiosError.response.data.detail);
      } else if (axiosError.response?.status === 401) {
        // Generic 401 error
        throw new Error("用户名或密码错误");
      } else if (axiosError.message) {
        // Network or other errors
        throw new Error(axiosError.message);
      } else {
        throw new Error("登录失败，请稍后重试");
      }
    }
  },

  /**
   * Register new user
   */
  async register(data: RegisterData): Promise<RegisterResponse> {
    const response = await apiClient.post<RegisterResponse>(
      API_ENDPOINTS.REGISTER,
      data
    );
    return response.data;
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    await apiClient.post(API_ENDPOINTS.LOGOUT);
  },

  /**
   * Get current user info
   */
  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  },

  /**
   * Get current user info with specific token
   */
  async getMeWithToken(token: string): Promise<User> {
    const response = await axios.get<User>(`${env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refresh(): Promise<{ access_token: string }> {
    const response = await apiClient.post<{ access_token: string }>(
      API_ENDPOINTS.REFRESH
    );
    return response.data;
  },
};
