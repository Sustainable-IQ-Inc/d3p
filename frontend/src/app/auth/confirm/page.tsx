'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Box, CircularProgress, Typography } from '@mui/material';
import useSupabase from 'hooks/useSupabase';

export default function ConfirmPage() {
  const router = useRouter();
  const supabase = useSupabase();
  const [status, setStatus] = useState<'loading' | 'success'>('loading');
  const [hasRun, setHasRun] = useState(false);

  useEffect(() => {
    // Prevent multiple executions
    if (hasRun) {
      console.log('Auth confirmation already running, skipping...');
      return;
    }
    
    setHasRun(true);
    
    const confirmAuth = async () => {
      try {
        console.log('=== CLIENT-SIDE AUTH CONFIRM DEBUG ===');
        console.log('Current URL:', window.location.href);
        console.log('Full hash:', window.location.hash);
        console.log('Environment:', {
          nodeEnv: process.env.NODE_ENV,
          supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL,
          isProduction: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1'
        });
        console.log('Cookies:', document.cookie);
        console.log('LocalStorage keys:', Object.keys(localStorage));
        
        // Extract tokens and error params from URL hash
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const refreshToken = hashParams.get('refresh_token');
        const type = hashParams.get('type');
        const hashError = hashParams.get('error');
        const errorCode = hashParams.get('error_code');
        const errorDescription = hashParams.get('error_description');

        console.log('Hash parameters:', { 
          hasAccessToken: !!accessToken, 
          hasRefreshToken: !!refreshToken,
          type,
          hashError,
          errorCode,
          errorDescription,
          accessTokenLength: accessToken?.length,
          refreshTokenLength: refreshToken?.length
        });
        
        // Check for errors from Supabase (expired/already used links)
        if (hashError) {
          console.error('Auth confirm error:', { hashError, errorCode, errorDescription });
          
          // Clean up any leftover auth state
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          // Create user-friendly error message
          let message = errorDescription || hashError;
          
          // Customize message for common errors
          if (errorCode === 'otp_expired' || hashError === 'access_denied') {
            message = 'This magic link has expired or has already been used. Please request a new one.';
          }
          
          const encodedMessage = encodeURIComponent(message);
          console.log('Redirecting to login with error:', message);
          
          // Use window.location.href for a full page redirect
          window.location.href = `/login?error=auth_failed&message=${encodedMessage}`;
          return;
        }

        if (!accessToken || !refreshToken) {
          console.error('No auth tokens found in URL hash');
          console.error('This should not happen - tokens should be in hash after reload');
          // Clear the flag if tokens are missing
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          const message = 'No authentication tokens found in the confirmation link.';
          console.log('Redirecting to login with error:', message);
          window.location.href = `/login?error=auth_failed&message=${encodeURIComponent(message)}`;
          return;
        }
        
        // TWO-PHASE APPROACH to ensure clean session switch
        const hasCleared = localStorage.getItem('auth-phase-cleared');
        const savedTokens = localStorage.getItem('auth-pending-tokens');
        
        // If we have saved tokens, use them (hash was lost on reload)
        let finalAccessToken = accessToken;
        let finalRefreshToken = refreshToken;
        
        if (!accessToken && savedTokens) {
          console.log('Hash lost on reload, restoring from localStorage...');
          const parsed = JSON.parse(savedTokens);
          finalAccessToken = parsed.accessToken;
          finalRefreshToken = parsed.refreshToken;
          console.log('Restored tokens:', {
            hasAccessToken: !!finalAccessToken,
            hasRefreshToken: !!finalRefreshToken
          });
        }
        
        if (!hasCleared) {
          // ===== PHASE 1: Nuclear clear of all auth data =====
          console.log('🔥 PHASE 1: Clearing all existing auth data...');
          
          // CRITICAL: Save tokens to localStorage BEFORE clearing (hash might be lost on reload)
          if (accessToken && refreshToken) {
            console.log('Saving tokens to survive reload...');
            localStorage.setItem('auth-pending-tokens', JSON.stringify({
              accessToken,
              refreshToken
            }));
          }
          
          // STEP 1: Sign out any existing session FIRST (before clearing storage)
          console.log('Step 1: Checking for existing Supabase session...');
          try {
            const { data: currentSession } = await supabase.auth.getSession();
            if (currentSession?.session) {
              console.log('⚠️ Found active session for:', currentSession.session.user.email);
              console.log('⚠️ Signing out this session...');
              
              // Sign out - this tells Supabase server to invalidate the session
              await supabase.auth.signOut({ scope: 'local' });
              console.log('✓ Session signed out on Supabase');
              
              // Wait a moment for server to process
              await new Promise(resolve => setTimeout(resolve, 500));
            } else {
              console.log('✓ No active session found');
            }
          } catch (signOutError) {
            console.log('⚠️ Sign out error (continuing anyway):', signOutError);
            // Continue even if sign out fails - we'll clear everything anyway
          }
          
          // STEP 2: Now clear all local storage
          console.log('Step 2: Clearing all local cookies and storage...');
          
          // Function to aggressively delete cookies
          const deleteCookie = (name: string) => {
            const domain = window.location.hostname;
            const variations = [
              `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`,
              `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${domain};`,
              `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.${domain};`,
              `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; secure;`,
              `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${domain}; secure;`,
              `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.${domain}; secure;`,
            ];
            variations.forEach(cookieStr => {
              document.cookie = cookieStr;
            });
          };
          
          // Get Supabase project ref
          const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
          const projectRef = supabaseUrl.split('//')[1]?.split('.')[0] || '';
          
          // Delete all possible cookie names
          const cookieNames = [
            `sb-${projectRef}-auth-token`,
            `sb-${projectRef}-auth-token.0`,
            `sb-${projectRef}-auth-token.1`,
            `sb-${projectRef}-auth-token.2`,
            'sb-access-token',
            'sb-refresh-token',
          ];
          
          console.log('Deleting cookies:', cookieNames);
          cookieNames.forEach(deleteCookie);
          
          // Clear all storage EXCEPT the flags we need to survive reload
          console.log('Clearing all storage...');
          const keysToSave = ['auth-phase-cleared', 'auth-pending-tokens'];
          const savedValues: Record<string, string> = {};
          
          // Save important keys temporarily
          keysToSave.forEach(key => {
            const val = localStorage.getItem(key);
            if (val) savedValues[key] = val;
          });
          
          // Clear everything
          localStorage.clear();
          sessionStorage.clear();
          
          // Restore saved keys
          Object.entries(savedValues).forEach(([key, val]) => {
            localStorage.setItem(key, val);
          });
          
          // Mark phase 1 complete and reload
          localStorage.setItem('auth-phase-cleared', 'true');
          console.log('✓ Phase 1 complete. Reloading page for clean slate...');
          console.log('Note: NOT calling signOut to avoid session_id errors');
          
          // Reload the page to get a completely fresh start
          // The reload will clear any in-memory Supabase client state
          window.location.reload();
          return; // Stop execution here
        }
        
        // ===== PHASE 2: Set new session with clean slate =====
        console.log('✅ PHASE 2: Setting new session with clean slate...');
        
        // Verify we have tokens
        if (!finalAccessToken || !finalRefreshToken) {
          console.error('❌ No tokens available in Phase 2');
          console.error('accessToken from hash:', !!accessToken);
          console.error('savedTokens from localStorage:', !!savedTokens);
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          const message = 'Authentication tokens were lost. Please try clicking the link again.';
          console.log('Redirecting to login with error:', message);
          window.location.href = `/login?error=auth_failed&message=${encodeURIComponent(message)}`;
          return;
        }
        
        // Now set the new session
        console.log('Setting session for new user...');
        const { data, error } = await supabase.auth.setSession({
          access_token: finalAccessToken,
          refresh_token: finalRefreshToken,
        });

        if (error) {
          console.error('❌ Error setting session:', error);
          // Clear the flags so user can try again
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          console.log('Redirecting to login with error:', error.message);
          window.location.href = `/login?error=auth_failed&message=${encodeURIComponent(error.message)}`;
          return;
        }

        if (data.user) {
          console.log('✓ Successfully authenticated as:', data.user.email);
          console.log('✓ User ID:', data.user.id);
          
          // Verify session is actually set
          const { data: verifyData } = await supabase.auth.getSession();
          console.log('✓ Session verification:', verifyData.session?.user?.email);
          
          setStatus('success');
          
          // IMPORTANT: Clean up all flags after session is confirmed
          console.log('Cleaning up and redirecting...');
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          // Use replace instead of push to prevent back button issues
          setTimeout(() => {
            console.log('Redirecting to dashboard...');
            window.location.href = '/dashboard/default';
          }, 1000);
        } else {
          console.error('❌ No user data returned');
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          const message = 'Failed to establish user session.';
          console.log('Redirecting to login with error:', message);
          window.location.href = `/login?error=auth_failed&message=${encodeURIComponent(message)}`;
        }
      } catch (err) {
        console.error('Unexpected error:', err);
        console.error('Error details:', {
          message: (err as Error)?.message,
          stack: (err as Error)?.stack,
          type: typeof err
        });
        
        // Clear flags on error so user can try again
        localStorage.removeItem('auth-phase-cleared');
        localStorage.removeItem('auth-pending-tokens');
        
        const errorMessage = (err as Error)?.message || 'An unexpected error occurred during authentication.';
        console.log('Redirecting to login with error:', errorMessage);
        window.location.href = `/login?error=auth_failed&message=${encodeURIComponent(errorMessage)}`;
      }
    };

    confirmAuth();
  }, [hasRun, router, supabase]);

  if (status === 'loading') {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress size={60} />
        <Typography variant="h5">Confirming your authentication...</Typography>
        <Typography variant="body2" color="text.secondary">
          Please wait while we log you in
        </Typography>
      </Box>
    );
  }

  if (status === 'success') {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <Typography variant="h5" color="success.main">
          ✓ Authentication successful!
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Redirecting you to the dashboard...
        </Typography>
      </Box>
    );
  }

  // Error state is now handled by redirecting to login page with error message
  // No need to show error UI here
  return null;
}
