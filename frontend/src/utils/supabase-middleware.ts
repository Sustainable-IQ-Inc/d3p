import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

// Helper to log auth events to backend
async function logAuthEvent(data: {
  event_type: string;
  error_message?: string;
  ip_address?: string;
}) {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    await fetch(`${apiUrl}/log-auth-event/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  } catch (error) {
    // Silently fail - we don't want logging to break the middleware
    console.error('Failed to log auth event in middleware:', error);
  }
}

// Helper to get client IP
function getClientIp(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  const realIp = request.headers.get('x-real-ip');
  if (realIp) {
    return realIp;
  }
  return 'unknown';
}

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          request.cookies.set({
            name,
            value,
            ...options,
          })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({
            name,
            value,
            ...options,
          })
        },
        remove(name: string, options: CookieOptions) {
          request.cookies.set({
            name,
            value: '',
            ...options,
          })
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          })
          response.cookies.set({
            name,
            value: '',
            ...options,
          })
        },
      },
    }
  )

  // First check if we have a valid session before trying to get user
  const { data: sessionData, error: sessionError } = await supabase.auth.getSession()
  
  // If there's a session error (like invalid token), clean up and redirect
  if (sessionError) {
    console.error('Session error in middleware:', sessionError.message)
    const clientIp = getClientIp(request)
    
    // Check if it's an invalid token error
    if (sessionError.message?.includes('invalid claim') || 
        sessionError.message?.includes('JWT') ||
        sessionError.message?.includes('missing sub')) {
      console.log('Invalid token detected in middleware, clearing cookies')
      
      // Log this error
      await logAuthEvent({
        event_type: 'magic_link_error',
        error_message: `Middleware: Invalid token - ${sessionError.message}`,
        ip_address: clientIp,
      })
      
      // Create response that redirects to login
      const loginResponse = NextResponse.redirect(new URL('/login', request.url))
      
      // Clear all Supabase auth cookies
      const cookieNames = [
        'sb-access-token',
        'sb-refresh-token',
        'supabase-auth-token',
      ]
      
      cookieNames.forEach(cookieName => {
        loginResponse.cookies.delete(cookieName)
        // Also try with Supabase project ID prefix
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
        const projectRef = supabaseUrl.split('//')[1]?.split('.')[0]
        if (projectRef) {
          loginResponse.cookies.delete(`${projectRef}-auth-token`)
          loginResponse.cookies.delete(`${projectRef}-auth-token-code-verifier`)
        }
      })
      
      return loginResponse
    }
    
    // For other session errors, just redirect to login
    await logAuthEvent({
      event_type: 'magic_link_error',
      error_message: `Middleware: Session error - ${sessionError.message}`,
      ip_address: clientIp,
    })
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // If we have a session, verify the user
  if (sessionData?.session) {
    const { data, error } = await supabase.auth.getUser()
    
    if (error) {
      console.error('Get user error in middleware:', error.message)
      const clientIp = getClientIp(request)
      
      // If token is invalid, clear it and redirect
      if (error.message?.includes('invalid claim') || 
          error.message?.includes('JWT') ||
          error.message?.includes('missing sub')) {
        console.log('Invalid user token in middleware, signing out')
        
        // Log this specific error that was causing the 403
        await logAuthEvent({
          event_type: 'magic_link_error',
          error_message: `Middleware getUser(): Invalid claim - ${error.message}`,
          ip_address: clientIp,
        })
        
        await supabase.auth.signOut()
        return NextResponse.redirect(new URL('/login', request.url))
      }
      
      // Log other getUser errors
      await logAuthEvent({
        event_type: 'magic_link_error',
        error_message: `Middleware getUser(): ${error.message}`,
        ip_address: clientIp,
      })
      
      return NextResponse.redirect(new URL('/login', request.url))
    }
    
    if (!data?.user) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  } else {
    // No session, redirect to login
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return response
}