'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Box, CircularProgress, Typography } from '@mui/material';

export default function CallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    console.log('=== CALLBACK PAGE (CLIENT-SIDE) ===');
    console.log('URL:', window.location.href);
    console.log('Search params:', Object.fromEntries(searchParams));

    const error = searchParams.get('error');
    const errorCode = searchParams.get('error_code');
    const errorDescription = searchParams.get('error_description');

    // Check for errors from Supabase (expired links, etc.)
    if (error) {
      console.error('Auth callback error:', { error, errorCode, errorDescription });
      
      // Create user-friendly error message
      let message = errorDescription || error;
      
      // Customize message for common errors
      if (errorCode === 'otp_expired' || error === 'access_denied') {
        message = 'This magic link has expired or has already been used. Please request a new one.';
      }
      
      const encodedMessage = encodeURIComponent(message);
      console.log('Redirecting to login with error:', message);
      console.log('Redirect URL:', `/login?error=auth_failed&message=${encodedMessage}`);
      
      // Use window.location.href for a full page redirect (more reliable than router.push)
      window.location.href = `/login?error=auth_failed&message=${encodedMessage}`;
      return;
    }

    // If no error, the server-side route handler should have handled the code exchange
    // But if we're here, something went wrong
    console.log('No error in URL, checking for code...');
    const code = searchParams.get('code');
    
    if (code) {
      console.log('Code found, but we should not be here. Server route should have handled it.');
      console.log('This suggests the route handler is not running.');
      // Redirect to login as fallback using window.location
      window.location.href = '/login?error=auth_failed&message=' + encodeURIComponent('Authentication processing failed. Please try again.');
    } else {
      console.log('No code and no error, redirecting to login');
      window.location.href = '/login';
    }
  }, [router, searchParams]);

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
      <Typography variant="h5">Processing authentication...</Typography>
      <Typography variant="body2" color="text.secondary">
        Please wait while we redirect you
      </Typography>
    </Box>
  );
}

