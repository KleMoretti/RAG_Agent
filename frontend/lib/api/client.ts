import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { env } from '../env';
import { STORAGE_KEYS } from '../constants';

/**
 * Axios instance with default configuration
 * Includes automatic JWT token injection and error handling
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - automatically adds JWT token to requests
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from authStore persist data
    let token: string | null = null;
    
    try {
      const authData = localStorage.getItem(STORAGE_KEYS.USER);
      if (authData) {
        const parsedData = JSON.parse(authData);
        token = parsedData.state?.token || null;
      }
    } catch (error) {
      console.error('Failed to parse auth data from localStorage:', error);
    }
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - handles common error cases
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      // Clear auth data from localStorage
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER);
      
      // Clear auth token from cookie to prevent middleware redirect loop
      if (typeof document !== 'undefined') {
        document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      }
      
      // Redirect to login page (client-side only)
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error('Permission denied');
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error - please check your connection');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
