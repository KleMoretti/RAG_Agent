import apiClient from './client';
import { API_ENDPOINTS } from '../constants';
import { LoginCredentials, RegisterData, User } from '../types/user';

/**
 * Authentication API responses
 */
interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
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
    const response = await apiClient.post<LoginResponse>(
      API_ENDPOINTS.LOGIN,
      credentials
    );
    return response.data;
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
   * Refresh access token
   */
  async refresh(): Promise<{ access_token: string }> {
    const response = await apiClient.post<{ access_token: string }>(
      API_ENDPOINTS.REFRESH
    );
    return response.data;
  },
};
