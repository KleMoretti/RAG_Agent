import apiClient from './client';
import { User } from '../types/user';

/**
 * 更新用户信息请求
 */
export interface UpdateProfileRequest {
    username?: string;
    email?: string;
}

/**
 * 修改密码请求
 */
export interface ChangePasswordRequest {
    current_password: string;
    new_password: string;
}

/**
 * 用户设置相关 API
 */
export const userApi = {
    /**
     * 更新当前用户信息
     */
    async updateProfile(data: UpdateProfileRequest): Promise<User> {
        const response = await apiClient.put<User>('/api/users/me', data);
        return response.data;
    },

    /**
     * 修改当前用户密码
     */
    async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
        const response = await apiClient.post<{ message: string }>(
            '/api/users/me/password',
            data
        );
        return response.data;
    },

    /**
     * 获取当前用户信息
     */
    async getCurrentUser(): Promise<User> {
        const response = await apiClient.get<User>('/api/users/me');
        return response.data;
    },
};

