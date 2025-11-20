# Authentication Logging Documentation

## Overview

This document describes the comprehensive authentication logging system implemented to help diagnose magic link login issues. The system logs three key events in the authentication flow:

1. **Login Page Visits** - When a user lands on the login page
2. **Magic Link Sends** - When a magic link is requested and sent
3. **Magic Link Accesses** - When a user clicks on a magic link

## Implementation Details

### Backend Components

#### 1. Auth Logging Endpoint (`/log-auth-event/`)

**Location:** `backend/main.py`

A new POST endpoint that accepts authentication event logs from the frontend. This endpoint:
- Does not require authentication (to allow logging of login attempts)
- Extracts the real client IP address (handling proxies and load balancers)
- Logs events to Google Cloud Logging with structured data
- Returns the captured IP address for verification

**Request Model:** `backend/models.py` - `AuthLog`

```python
class AuthLog(BaseModel):
    event_type: str  # 'login_page_visit', 'magic_link_sent', 'magic_link_accessed', 'magic_link_error'
    email: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    magic_link_url: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None
```

#### 2. IP Address Extraction

The backend includes a helper function `get_client_ip()` that properly extracts the client's IP address by checking:
1. `X-Forwarded-For` header (for Cloud Run, proxies)
2. `X-Real-IP` header
3. Direct client host as fallback

### Frontend Components

#### 1. Auth Logger Utility

**Location:** `frontend/src/utils/authLogger.ts`

A reusable utility function that sends authentication events to the backend. Features:
- Automatically includes user agent information
- Uses environment variable for API URL (`NEXT_PUBLIC_API_BASE_URL`)
- Fails silently to prevent blocking the authentication flow
- Fire-and-forget pattern for performance

#### 2. Login Page Visit Logging

**Location:** `frontend/src/sections/auth/auth-forms/AuthLogin.tsx`

Added a `useEffect` hook that logs when the login page is mounted:
```typescript
useEffect(() => {
  logAuthEvent({
    event_type: 'login_page_visit',
  });
}, []);
```

#### 3. Magic Link Send Logging

**Location:** `frontend/src/sections/auth/auth-forms/AuthLogin.tsx`

Logs are created when:
- Magic link is successfully requested (after `signInWithOtp` succeeds)
- Magic link request fails (with error details)

Captured data:
- Email address
- User ID (when available)
- Redirect URL where the magic link points
- Error messages (if any)

#### 4. Magic Link Access Logging

**Location:** `frontend/src/app/callback/route.ts`

Logs when a magic link is clicked and processed. This includes:
- Successful authentication attempts
- Failed authentication attempts (expired links, invalid codes, etc.)
- User ID (on success)
- Full URL accessed
- IP address of the client

## Log Formats

### Login Page Visit
```
🔐 LOGIN PAGE VISIT - IP: 192.168.1.100, User-Agent: Mozilla/5.0...
```

### Magic Link Sent
```
📧 MAGIC LINK SENT - Email: user@example.com, User ID: abc-123, URL: https://app.example.com/callback, IP: 192.168.1.100
```

### Magic Link Accessed
```
🔗 MAGIC LINK ACCESSED - User ID: abc-123, URL: https://app.example.com/callback?code=xyz, IP: 192.168.1.100
```

### Magic Link Error
```
❌ MAGIC LINK ERROR - Error: This magic link has expired, IP: 192.168.1.100
```

## Viewing Logs

### Google Cloud Logging

All logs are sent to Google Cloud Logging and can be viewed in the Google Cloud Console:

1. Go to Google Cloud Console
2. Navigate to "Logging" → "Logs Explorer"
3. Select your project
4. Use these filters to find auth logs:

**All auth events:**
```
resource.type="cloud_run_revision"
jsonPayload.message=~"LOGIN PAGE VISIT|MAGIC LINK SENT|MAGIC LINK ACCESSED|MAGIC LINK ERROR"
```

**Login page visits only:**
```
resource.type="cloud_run_revision"
jsonPayload.message=~"LOGIN PAGE VISIT"
```

**Magic link sends:**
```
resource.type="cloud_run_revision"
jsonPayload.message=~"MAGIC LINK SENT"
```

**Magic link accesses:**
```
resource.type="cloud_run_revision"
jsonPayload.message=~"MAGIC LINK ACCESSED"
```

**Errors only:**
```
resource.type="cloud_run_revision"
jsonPayload.message=~"MAGIC LINK ERROR"
severity>=ERROR
```

### Local Development

When running locally, logs will appear in:
- Terminal/console output where the backend is running
- `backend/std.log` file

## Configuration

### Environment Variables

**Frontend (`frontend/env.local.example`):**
```bash
# API Configuration - used for logging endpoint
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

**Backend (`backend/env.example`):**
- No additional configuration needed
- Existing Google Cloud Logging setup is used

## Troubleshooting

### Logs not appearing

1. **Check API URL**: Ensure `NEXT_PUBLIC_API_BASE_URL` is correctly set in your frontend environment
2. **Check Network**: Open browser DevTools → Network tab to see if `/log-auth-event/` requests are being made
3. **Check Backend Logs**: Verify the backend is receiving the requests
4. **Check CORS**: Ensure the frontend origin is in `ALLOWED_ORIGINS` in backend config

### IP Address shows as "unknown"

This can happen if:
- The request doesn't go through a proxy
- Headers are not being forwarded correctly
- Local development without proper headers

For production, Cloud Run automatically sets the `X-Forwarded-For` header.

## Security Considerations

1. **No Authentication Required**: The logging endpoint intentionally does not require authentication to log failed login attempts and page visits.

2. **Rate Limiting**: Consider adding rate limiting to the `/log-auth-event/` endpoint to prevent abuse.

3. **PII Data**: Email addresses and user IDs are logged. Ensure compliance with your data retention and privacy policies.

4. **Error Messages**: Full error messages are logged, which can be helpful for debugging but may contain sensitive information.

## Example Use Cases

### Tracking Login Attempts from Specific IP

Filter logs by IP address to see all authentication activity:
```
jsonPayload.message=~"IP: 192.168.1.100"
```

### Finding Failed Magic Links for a User

Search for a specific email and look for errors:
```
jsonPayload.message=~"user@example.com"
severity>=ERROR
```

### Monitoring Authentication Flow

Use the timestamps to track the complete flow:
1. User visits login page (login_page_visit)
2. User requests magic link (magic_link_sent)
3. User clicks magic link (magic_link_accessed)

Time gaps between events can help identify where users are getting stuck.

## Future Enhancements

Potential improvements to consider:

1. **Rate Limiting**: Add rate limiting to prevent log flooding
2. **Analytics Dashboard**: Create a dashboard showing login metrics
3. **Alerts**: Set up alerts for high error rates or suspicious activity
4. **Session Tracking**: Add session IDs to track the complete user journey
5. **Geolocation**: Add IP geolocation to understand where login issues occur
6. **Browser Fingerprinting**: Add more detailed browser/device information

## Files Modified

### Backend
- `backend/models.py` - Added `AuthLog` model
- `backend/main.py` - Added `/log-auth-event/` endpoint and IP extraction helper

### Frontend
- `frontend/src/utils/authLogger.ts` - New utility for logging
- `frontend/src/sections/auth/auth-forms/AuthLogin.tsx` - Added logging for page visits and magic link sends
- `frontend/src/app/callback/route.ts` - Added logging for magic link accesses

## Testing

### Manual Testing

1. **Test Login Page Visit Logging:**
   - Navigate to `/login`
   - Check logs for "LOGIN PAGE VISIT" message
   - Verify IP address is captured

2. **Test Magic Link Send Logging:**
   - Enter email and click "Send Magic Link"
   - Check logs for "MAGIC LINK SENT" message
   - Verify email and URL are logged

3. **Test Magic Link Access Logging:**
   - Click on a magic link from email
   - Check logs for "MAGIC LINK ACCESSED" message
   - Verify user ID and URL are logged

4. **Test Error Logging:**
   - Try using an expired magic link
   - Check logs for "MAGIC LINK ERROR" message
   - Verify error details are captured

### Automated Testing

Consider adding integration tests for:
- Logging endpoint availability
- Log data structure validation
- IP address extraction accuracy
- Error handling and silent failures

