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
          setIsLoading(false);
          router.push(redirectTo);
          return;
        }

        // If user is authenticated but shouldn't be (e.g., on login page)
        if (!requireAuth && isAuthenticated && token) {
          // On login/register pages, verify token before redirecting to dashboard
          try {
            const { authApi } = await import('@/lib/api/auth');
            await authApi.getMeWithToken(token);
            // Token is valid, redirect to dashboard
            router.push(ROUTES.DASHBOARD);
            return;
          } catch (error) {
            // Token is invalid, clear auth state and let user stay on login page
            // Silently handle error - this is expected for expired tokens
            logout();
            setIsLoading(false);
            return;
          }
        }

        // If on non-auth pages and not authenticated, just finish loading
        if (!requireAuth && !isAuthenticated) {
          setIsLoading(false);
          return;
        }

        // If user is authenticated and on protected pages, verify token validity
        if (requireAuth && isAuthenticated && token) {
          try {
            // Use getMeWithToken to verify token is still valid
            const { authApi } = await import('@/lib/api/auth');
            await authApi.getMeWithToken(token);
            setIsLoading(false);
          } catch (error) {
            // Token is invalid, logout and redirect to login
            // Silently handle error - logout will clear the state
            logout();
            setIsLoading(false);
            router.push(redirectTo);
            return;
          }
        } else {
          // No authentication needed or no token to verify
          setIsLoading(false);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        if (requireAuth) {
          logout();
          router.push(redirectTo);
        }
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