'use client';

import { useState } from 'react';
import useSupabase from 'hooks/useSupabase';
import { Button, TextField, Typography, Box, Paper, Alert } from '@mui/material';

/**
 * OTP Test Page - Temporary debugging page for production
 * Remove this file after OTP flow is working properly
 * Access at: /test-otp
 */
export default function TestOtpPage() {
  const supabase = useSupabase();
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState('');

  const addLog = (message: string) => {
    console.log(message);
    setLogs(prev => [...prev, `${new Date().toISOString()}: ${message}`]);
  };

  const testSendOtp = async () => {
    setError('');
    setLogs([]);
    addLog('🚀 Starting OTP send test...');
    
    try {
      addLog(`Sending OTP to: ${email}`);
      
      const { data, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: false,
        },
      });
      
      if (error) {
        addLog(`❌ Error: ${error.message}`);
        setError(error.message);
      } else {
        addLog('✅ OTP sent successfully');
        addLog(`Response data: ${JSON.stringify(data)}`);
      }
    } catch (err: any) {
      addLog(`❌ Exception: ${err.message}`);
      setError(err.message);
    }
  };

  const testVerifyOtp = async () => {
    setError('');
    addLog('🔍 Starting OTP verification test...');
    
    try {
      addLog(`Verifying OTP for: ${email}`);
      addLog(`Token: ${otp}`);
      
      const { data, error } = await supabase.auth.verifyOtp({
        email,
        token: otp,
        type: 'email',
      });
      
      addLog(`Response received`);
      addLog(`  - Has data: ${!!data}`);
      addLog(`  - Has session: ${!!data?.session}`);
      addLog(`  - Has user: ${!!data?.user}`);
      addLog(`  - Error: ${error?.message || 'none'}`);
      
      if (error) {
        addLog(`❌ Verification failed: ${error.message}`);
        setError(error.message);
        return;
      }
      
      if (data?.session) {
        addLog('✅ Session created successfully!');
        addLog(`User ID: ${data.session.user.id}`);
        addLog(`User email: ${data.session.user.email}`);
        addLog(`Access token (first 20 chars): ${data.session.access_token.substring(0, 20)}...`);
        
        // Check if cookies were set
        addLog('Checking cookies...');
        const cookies = document.cookie;
        addLog(`Cookies: ${cookies.substring(0, 100)}...`);
        
        // Wait and check session
        addLog('Waiting 1 second...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        addLog('Checking if session persists...');
        const { data: sessionCheck } = await supabase.auth.getSession();
        if (sessionCheck?.session) {
          addLog('✅ Session persists! Cookie was saved correctly.');
          addLog(`Session user: ${sessionCheck.session.user.email}`);
          
          addLog('🎉 SUCCESS! Attempting redirect...');
          addLog('Redirecting in 2 seconds...');
          
          setTimeout(() => {
            addLog('Executing: window.location.href = "/dashboard/default"');
            window.location.href = '/dashboard/default';
          }, 2000);
        } else {
          addLog('❌ Session does NOT persist! Cookie issue detected.');
          addLog('This is the problem - cookies are not being saved properly.');
          setError('Session created but not persisted. Check cookie settings and CORS.');
        }
      } else if (data?.user) {
        addLog('⚠️ User returned but no session');
        addLog('Waiting 500ms and checking again...');
        
        await new Promise(resolve => setTimeout(resolve, 500));
        const { data: sessionData } = await supabase.auth.getSession();
        
        if (sessionData?.session) {
          addLog('✅ Session now available!');
          addLog('Redirecting...');
          setTimeout(() => {
            window.location.href = '/dashboard/default';
          }, 1000);
        } else {
          addLog('❌ Still no session after waiting');
          setError('User verified but session not created');
        }
      } else {
        addLog('❌ No session or user returned');
        setError('Verification failed - no data returned');
      }
    } catch (err: any) {
      addLog(`❌ Exception during verification: ${err.message}`);
      addLog(`Stack: ${err.stack}`);
      setError(err.message);
    }
  };

  const testGetSession = async () => {
    addLog('🔍 Checking current session...');
    try {
      const { data, error } = await supabase.auth.getSession();
      
      if (error) {
        addLog(`❌ Error getting session: ${error.message}`);
      } else if (data?.session) {
        addLog('✅ Session exists!');
        addLog(`User: ${data.session.user.email}`);
        addLog(`Expires at: ${new Date(data.session.expires_at! * 1000).toISOString()}`);
      } else {
        addLog('ℹ️ No active session');
      }
    } catch (err: any) {
      addLog(`❌ Exception: ${err.message}`);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 800, margin: '0 auto' }}>
      <Typography variant="h4" gutterBottom>
        OTP Test Page (Production Debug)
      </Typography>
      
      <Alert severity="warning" sx={{ mb: 3 }}>
        This is a temporary debugging page. Remove after OTP flow is working.
      </Alert>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Step 1: Send OTP
        </Typography>
        
        <TextField
          fullWidth
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{ mb: 2 }}
        />
        
        <Button 
          variant="contained" 
          onClick={testSendOtp}
          disabled={!email}
        >
          Send OTP Code
        </Button>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Step 2: Verify OTP
        </Typography>
        
        <TextField
          fullWidth
          label="6-Digit Code"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          sx={{ mb: 2 }}
        />
        
        <Button 
          variant="contained" 
          onClick={testVerifyOtp}
          disabled={!email || !otp || otp.length !== 6}
        >
          Verify Code
        </Button>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Diagnostics
        </Typography>
        
        <Button 
          variant="outlined" 
          onClick={testGetSession}
          sx={{ mr: 2 }}
        >
          Check Current Session
        </Button>
        
        <Button 
          variant="outlined" 
          onClick={() => setLogs([])}
        >
          Clear Logs
        </Button>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3, bgcolor: '#1e1e1e', color: '#d4d4d4' }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#d4d4d4' }}>
          Debug Logs
        </Typography>
        
        <Box 
          component="pre" 
          sx={{ 
            fontSize: '12px', 
            overflow: 'auto',
            maxHeight: '400px',
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}
        >
          {logs.length === 0 ? 'No logs yet...' : logs.join('\n')}
        </Box>
      </Paper>

      <Box sx={{ mt: 3 }}>
        <Typography variant="caption" color="text.secondary">
          Environment: {process.env.NEXT_PUBLIC_ENV || 'unknown'}
          <br />
          Supabase URL: {process.env.NEXT_PUBLIC_SUPABASE_URL}
          <br />
          Site URL: {process.env.NEXT_PUBLIC_SITE_URL}
        </Typography>
      </Box>
    </Box>
  );
}

