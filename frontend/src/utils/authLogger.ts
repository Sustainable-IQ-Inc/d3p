/**
 * Utility for logging authentication events to the backend
 */

interface AuthLogData {
  event_type: 'login_page_visit' | 'magic_link_sent' | 'magic_link_accessed' | 'magic_link_error';
  email?: string;
  user_id?: string;
  ip_address?: string;
  magic_link_url?: string;
  user_agent?: string;
  error_message?: string;
}

export async function logAuthEvent(data: AuthLogData): Promise<void> {
  try {
    // Get the API URL from environment or default to backend
    // Use NEXT_PUBLIC_API_BASE_URL if available, otherwise fall back to localhost
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    
    // Add user agent if not provided
    const logData = {
      ...data,
      user_agent: data.user_agent || (typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown'),
    };
    
    // Send the log to the backend (fire and forget, don't block on errors)
    await fetch(`${apiUrl}/log-auth-event/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(logData),
    });
  } catch (error) {
    // Silently fail - we don't want logging to break the auth flow
    console.error('Failed to log auth event:', error);
  }
}

