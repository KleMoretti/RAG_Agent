import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware for basic route protection
 * Detailed authentication validation is handled by client-side AuthGuard
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // For now, let all requests pass through
  // Client-side AuthGuard will handle detailed authentication validation
  // This prevents server-side/client-side token sync issues
  
  return NextResponse.next();
}

/**
 * Middleware configuration
 */
export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register'],
};
