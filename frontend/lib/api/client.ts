import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { env } from '../env';
import { STORAGE_KEYS } from '../constants';

/**
 * Axios instance with default configuration
 * Includes automatic JWT token injection and error handling
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: env.NEXT_PUBLIC_API_URL,
  timeout: 60000, // 增加到60秒，给后端RAG有足够时间（25s）+ 降级LLM时间（最多35s）
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
        // Zustand persist stores data in 'state' property
        const state = parsedData.state || parsedData;
        token = state.token || null;
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
    // Handle 401 Unauthorized - redirect to login (except when already on login page)
    if (error.response?.status === 401) {
      // Check if we're already on the login or register page to avoid redirect loops
      const isOnAuthPage = typeof window !== 'undefined' && 
        (window.location.pathname === '/login' || 
         window.location.pathname.startsWith('/login') ||
         window.location.pathname === '/register' ||
         window.location.pathname.startsWith('/register'));
      
      // Only clear auth data and redirect if NOT on auth pages
      // This allows login/register pages to handle their own errors
      if (!isOnAuthPage) {
        // Clear auth data from localStorage
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
        
        // Clear auth token from cookie to prevent middleware redirect loop
        if (typeof document !== 'undefined') {
          document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        }
        
        // Redirect to login page
        if (typeof window !== 'undefined') {
          // Use setTimeout to avoid interrupting the current navigation
          setTimeout(() => {
            window.location.href = '/login';
          }, 100);
        }
      }
      // If on auth pages, just reject the error without redirecting
      // The auth page will handle the error and display appropriate message
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
