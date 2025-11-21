# Authentication Logging Documentation

## Overview

This document describes the comprehensive authentication logging system implemented to help diagnose login issues. The system logs key events in the authentication flow:

### Current OTP-Based Authentication
1. **Login Page Visits** - When a user lands on the login page
2. **OTP Sends** - When a 6-digit verification code is requested and sent
3. **OTP Verifications** - When a user successfully verifies their OTP code
4. **OTP Errors** - When OTP send or verification fails

### Legacy Magic Link Authentication (Deprecated)
For backwards compatibility, magic link events are still logged:
1. **Magic Link Sends** - When a magic link was requested and sent
2. **Magic Link Accesses** - When a user clicked on a magic link

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
    event_type: str  # 'login_page_visit', 'otp_sent', 'otp_verified', 'otp_send_error', 'otp_verify_error', 'magic_link_sent', 'magic_link_accessed', 'magic_link_error'
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

#### 3. OTP Send Logging

**Location:** `frontend/src/sections/auth/auth-forms/AuthLogin.tsx`

Logs are created when:
- OTP (6-digit verification code) is successfully requested (after `signInWithOtp` succeeds)
- OTP request fails (with error details)

Captured data:
- Email address
- Error messages (if any)

#### 4. OTP Verification Logging

**Location:** `frontend/src/sections/auth/auth-forms/AuthLogin.tsx`

Logs when an OTP code is verified. This includes:
- Successful verification attempts
- Failed verification attempts (expired codes, invalid codes, etc.)
- User ID (on success)
- Email address
- IP address of the client

#### 5. Legacy Magic Link Access Logging (Deprecated)

**Location:** `frontend/src/app/callback/route.ts`

For backwards compatibility, still logs when old magic links are clicked and processed. This includes:
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

### OTP Sent
```
📧 OTP SENT - Email: user@example.com, IP: 192.168.1.100
```

### OTP Verified
```
✅ OTP VERIFIED - Email: user@example.com, User ID: abc-123, IP: 192.168.1.100
```

### OTP Send Error
```
❌ OTP SEND ERROR - Email: user@example.com, Error: Too many requests, IP: 192.168.1.100
```

### OTP Verify Error
```
❌ OTP VERIFY ERROR - Email: user@example.com, Error: Invalid code, IP: 192.168.1.100
```

### Legacy Magic Link Formats (Deprecated)

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

All logs are sent to Google Cloud Logging and can be viewed in the Google Cloud Console.

**IMPORTANT:** Different events log to different services:
- **Login Page Visits** → Backend logs (Python/FastAPI)
- **Magic Link Sent** → Backend logs (Python/FastAPI)  
- **Magic Link Accessed** → **Frontend logs (Next.js/Node)** ⚠️
- **Magic Link Errors** → Both Frontend and Backend logs

#### Finding Logs in Google Cloud Console

1. Go to Google Cloud Console
2. Navigate to "Logging" → "Logs Explorer"
3. Select your project

**All auth events (both frontend and backend):**
```
resource.type="cloud_run_revision"
(jsonPayload.message=~"LOGIN PAGE VISIT|OTP SENT|OTP VERIFIED|OTP.*ERROR|MAGIC LINK" OR textPayload=~"OTP|MAGIC LINK|AUTH EVENT")
```

**Login page visits only (backend):**
```
resource.type="cloud_run_revision"
resource.labels.service_name=~"backend|api"
jsonPayload.message=~"LOGIN PAGE VISIT"
```

**OTP sends (backend):**
```
resource.type="cloud_run_revision"
resource.labels.service_name=~"backend|api"
jsonPayload.message=~"OTP SENT"
```

**OTP verifications (backend):**
```
resource.type="cloud_run_revision"
resource.labels.service_name=~"backend|api"
jsonPayload.message=~"OTP VERIFIED"
```

**Legacy magic link sends (backend):**
```
resource.type="cloud_run_revision"
resource.labels.service_name=~"backend|api"
jsonPayload.message=~"MAGIC LINK SENT"
```

**Magic link accesses (FRONTEND logs):**
```
resource.type="cloud_run_revision"
resource.labels.service_name=~"frontend|web"
(jsonPayload.message=~"MAGIC LINK ACCESSED" OR textPayload=~"MAGIC LINK ACCESSED")
```

**Errors only (both services):**
```
resource.type="cloud_run_revision"
(jsonPayload.message=~"MAGIC LINK ERROR" OR textPayload=~"MAGIC LINK ERROR")
severity>=ERROR
```

**View by service:**
```
# Backend logs only
resource.type="cloud_run_revision"
resource.labels.service_name=~"backend|api"

# Frontend logs only
resource.type="cloud_run_revision"
resource.labels.service_name=~"frontend|web"
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

### "403: invalid claim: missing sub claim" Error

**What it means:** This error occurs when Supabase receives a JWT token that's missing the `sub` (subject/user ID) claim. This usually happens when a token is malformed, expired, or corrupted.

**Common causes:**
1. Partial token in cookies from a failed auth attempt
2. Token corruption during the authentication flow
3. Browser/antivirus clicking magic links before the user (creates partial sessions)
4. Race conditions where the middleware checks auth before session is fully established

**How it's fixed:**
The middleware now:
1. Checks for a valid session BEFORE trying to get user details
2. Detects invalid token errors and clears corrupted cookies
3. Signs out properly to clean up bad auth state
4. Logs these errors so you can track when they occur

**In the logs, you'll see:**
```
❌ MAGIC LINK ERROR - Error: Middleware getUser(): Invalid claim - invalid claim: missing sub claim, IP: xxx.xxx.xxx.xxx
```

**If you still see this error after the fix:**
1. Check that the middleware changes are deployed
2. Look for patterns - is it the same IP? Same time of day?
3. Check if users are clicking links multiple times
4. Verify email scanners aren't pre-clicking links (common with enterprise email)

### "Magic Link Accessed" logs not appearing

**The most common issue!** These logs appear in the **FRONTEND service logs**, not the backend.

**How to find them:**

1. Go to Cloud Logging in Google Cloud Console
2. **Filter by your frontend service:**
   ```
   resource.type="cloud_run_revision"
   resource.labels.service_name=~"frontend|web|bem-reports-web"
   textPayload=~"MAGIC LINK ACCESSED"
   ```

3. Look for logs like:
   ```
   🔗 MAGIC LINK ACCESSED - User: abc-123, IP: xxx.xxx.xxx.xxx, URL: https://...
   ```

4. If you still don't see them:
   - Check that the callback URL is being hit (look for any logs from `/callback`)
   - Verify the magic link actually redirects to `/callback` (check the email)
   - Look for error logs in the frontend service
   - Check if the auth is completing (does the user successfully log in?)

**The callback route logs will show:**
- The exact moment the magic link is clicked
- User ID from the session
- IP address of the client
- Full URL that was accessed

### Other logs not appearing

1. **Check API URL**: Ensure `NEXT_PUBLIC_API_BASE_URL` is correctly set in your frontend environment
2. **Check Network**: Open browser DevTools → Network tab to see if `/log-auth-event/` requests are being made
3. **Check Backend Logs**: Verify the backend is receiving the requests
4. **Check CORS**: Ensure the frontend origin is in `ALLOWED_ORIGINS` in backend config
5. **Check Service Names**: Make sure you're looking at logs from the correct service (frontend vs backend)

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

### Finding Failed OTP Attempts for a User

Search for a specific email and look for errors:
```
jsonPayload.message=~"user@example.com"
severity>=ERROR
```

### Monitoring Authentication Flow

Use the timestamps to track the complete flow:
1. User visits login page (login_page_visit)
2. User requests OTP code (otp_sent)
3. User verifies OTP code (otp_verified)

Time gaps between events can help identify where users are getting stuck.

### Legacy Magic Link Flow (Deprecated)

For old magic link-based authentication:
1. User visits login page (login_page_visit)
2. User requests magic link (magic_link_sent)
3. User clicks magic link (magic_link_accessed)

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
- `frontend/src/sections/auth/auth-forms/AuthLogin.tsx` - Added logging for page visits and magic link sends, plus improved error handling
- `frontend/src/app/callback/route.ts` - Added logging for magic link accesses
- `frontend/src/utils/supabase-middleware.ts` - Fixed "invalid claim: missing sub claim" errors with better token validation and cleanup

## Testing

### Manual Testing

1. **Test Login Page Visit Logging:**
   - Navigate to `/login`
   - Check logs for "LOGIN PAGE VISIT" message
   - Verify IP address is captured

2. **Test OTP Send Logging:**
   - Enter email and click "Send Verification Code"
   - Check logs for "OTP SENT" message
   - Verify email is logged

3. **Test OTP Verification Logging:**
   - Enter the 6-digit code from email
   - Click "Verify Code"
   - Check logs for "OTP VERIFIED" message
   - Verify user ID and email are logged

4. **Test Error Logging:**
   - Try entering an invalid OTP code
   - Check logs for "OTP VERIFY ERROR" message
   - Verify error details are captured
   - Try requesting too many OTPs quickly
   - Check logs for "OTP SEND ERROR" message

### Automated Testing

Consider adding integration tests for:
- Logging endpoint availability
- Log data structure validation
- IP address extraction accuracy
- Error handling and silent failures

