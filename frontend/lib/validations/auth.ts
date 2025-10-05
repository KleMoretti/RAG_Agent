import { z } from 'zod';

/**
 * Login form validation schema
 */
export const loginSchema = z.object({
  username: z
    .string()
    .min(3, '用户名至少 3 个字符')
    .max(50, '用户名最多 50 个字符'),
  password: z
    .string()
    .min(6, '密码至少 6 个字符')
    .max(100, '密码最多 100 个字符'),
  rememberMe: z.boolean().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;

/**
 * Register form validation schema
 */
export const registerSchema = z.object({
  username: z
    .string()
    .min(3, '用户名至少 3 个字符')
    .max(50, '用户名最多 50 个字符')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母、数字和下划线'),
  email: z
    .string()
    .email('请输入有效的邮箱地址')
    .optional()
    .or(z.literal('')),
  password: z
    .string()
    .min(6, '密码至少 6 个字符')
    .max(100, '密码最多 100 个字符'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: '两次密码输入不一致',
  path: ['confirmPassword'],
});

export type RegisterFormData = z.infer<typeof registerSchema>;
