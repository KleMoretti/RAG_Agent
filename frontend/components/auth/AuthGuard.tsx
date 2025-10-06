"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/lib/constants';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

/**
 * Authentication guard component
 * Handles client-side authentication state validation
 */
export function AuthGuard({ 
  children, 
  requireAuth = true, 
  redirectTo = ROUTES.LOGIN 
}: AuthGuardProps) {
  const router = useRouter();
  const { isAuthenticated, token, logout } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // If authentication is required but user is not authenticated
        if (requireAuth && !isAuthenticated) {
          router.push(redirectTo);
          return;
        }

        // If user is authenticated but shouldn't be (e.g., on login page)
        if (!requireAuth && isAuthenticated) {
          // Only redirect if we have a valid token
          if (token) {
            try {
              const { authApi } = await import('@/lib/api/auth');
              await authApi.getMeWithToken(token);
              // Token is valid, redirect to dashboard
              router.push(ROUTES.DASHBOARD);
              return;
            } catch (error) {
              // Token is invalid, clear auth state and continue
              console.error('Token validation failed on login page:', error);
              logout();
            }
          } else {
            // No token, clear auth state
            logout();
          }
        }

        // If user is authenticated, verify token validity by making a test API call
        if (requireAuth && isAuthenticated && token) {
          try {
            // Use getMeWithToken to bypass interceptor issues
            const { authApi } = await import('@/lib/api/auth');
            await authApi.getMeWithToken(token);
          } catch (error) {
            // Token is invalid, logout and redirect
            console.error('Token validation failed:', error);
            logout();
            router.push(redirectTo);
            return;
          }
        }

        setIsLoading(false);
      } catch (error) {
        console.error('Auth check failed:', error);
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [isAuthenticated, token, requireAuth, redirectTo, router, logout]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return <>{children}</>;
}