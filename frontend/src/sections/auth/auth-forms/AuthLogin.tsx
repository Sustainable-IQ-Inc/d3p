"use client";

import React, { useEffect, useState } from "react";

// next
import useSupabase from "../../../hooks/useSupabase";
import { useSearchParams } from "next/navigation";

// material-ui
import {
  Button,
  FormHelperText,
  InputLabel,
  Grid,
  OutlinedInput,
  Stack,
  Alert,
  Typography,
} from "@mui/material";

// third party
import * as Yup from "yup";
import { Formik } from "formik";
import OtpInput from 'react18-input-otp';

// project import
import AnimateButton from "components/@extended/AnimateButton";
import { useTheme } from '@mui/material/styles';

import { wakeUpApi } from "app/api/WakeUp";
import { logAuthEvent } from "utils/authLogger";

// assets
import { useRouter } from "next/navigation";

// types
import { ThemeMode } from 'types/config';

// ============================|| AWS CONNITO - LOGIN ||============================ //

const AuthLogin = () => {
  const supabase = useSupabase();
  const searchParams = useSearchParams();
  const theme = useTheme();

  const [captureError, setCaptureError] = useState("");
  const [showExpiredLinkMessage, setShowExpiredLinkMessage] = useState(false);
  const [authFailedMessage, setAuthFailedMessage] = useState("");
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);

  const router = useRouter();
  
  // Log login page visit
  useEffect(() => {
    logAuthEvent({
      event_type: 'login_page_visit',
    });
  }, []); // Run only once when component mounts
  
  // Check for error parameters and clean up
  useEffect(() => {
    const handleErrors = async () => {
      console.log('=== LOGIN PAGE ERROR CHECK ===');
      console.log('searchParams:', searchParams);
      console.log('Current URL:', window.location.href);
      
      if (searchParams) {
        const error = searchParams.get('error');
        const message = searchParams.get('message');
        
        console.log('Error params:', { error, message });
        
        if (error === 'link_expired') {
          console.log('Expired link detected - cleaning up...');
          
          // Clean up any leftover auth state
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          // CRITICAL: Sign out existing session to prevent logging in as wrong account
          const { data: sessionData } = await supabase.auth.getSession();
          if (sessionData?.session) {
            console.log('Signing out existing session:', sessionData.session.user.email);
            await supabase.auth.signOut();
            console.log('Session signed out successfully');
          }
          
          setShowExpiredLinkMessage(true);
          
          // Clear the error parameter from URL to prevent flash on reload
          router.replace('/login', { scroll: false });
        } else if (error === 'auth_failed') {
          console.log('Authentication failed - cleaning up...');
          console.log('Setting authFailedMessage to:', message);
          
          // Clean up any leftover auth state
          localStorage.removeItem('auth-phase-cleared');
          localStorage.removeItem('auth-pending-tokens');
          
          // CRITICAL: Sign out existing session to prevent logging in as wrong account
          const { data: sessionData } = await supabase.auth.getSession();
          if (sessionData?.session) {
            console.log('Signing out existing session:', sessionData.session.user.email);
            await supabase.auth.signOut();
            console.log('Session signed out successfully');
          }
          
          const decodedMessage = message ? decodeURIComponent(message) : 'Authentication failed. Please try again.';
          console.log('Decoded message:', decodedMessage);
          setAuthFailedMessage(decodedMessage);
          
          // Clear the error parameter from URL to prevent flash on reload
          router.replace('/login', { scroll: false });
        }
      } else {
        console.log('No searchParams available');
      }
    };
    
    handleErrors();
  }, [searchParams, router, supabase.auth]);
  
  // Check if user is already authenticated (for normal page visits)
  useEffect(() => {
    const checkAuth = async () => {
      // Only check for existing session if NOT from expired link or auth failed
      if (!showExpiredLinkMessage && !authFailedMessage) {
        try {
          // First check if we have a session before trying to get user
          const { data: sessionData, error: sessionError } = await supabase.auth.getSession();
          
          if (sessionError) {
            console.warn('Error getting session on login page:', sessionError);
            // Log the error for debugging
            logAuthEvent({
              event_type: 'magic_link_error',
              error_message: `Session check error: ${sessionError.message}`,
            });
            return;
          }
          
          // Only try to get user if we have a valid session
          if (sessionData?.session) {
            const { data, error: userError } = await supabase.auth.getUser();
            
            if (userError) {
              console.warn('Error getting user on login page:', userError);
              // If token is invalid, sign out to clean up
              if (userError.message?.includes('invalid claim') || userError.message?.includes('JWT')) {
                console.log('Invalid token detected, signing out...');
                await supabase.auth.signOut();
                logAuthEvent({
                  event_type: 'magic_link_error',
                  error_message: `Invalid token on login page: ${userError.message}`,
                });
              }
              return;
            }
            
            if (data.user) {
              console.log('User already logged in, redirecting...');
              router.push("/dashboard/default");
              router.refresh();
            }
          }
        } catch (error) {
          console.error('Unexpected error checking auth on login page:', error);
          logAuthEvent({
            event_type: 'magic_link_error',
            error_message: `Unexpected auth check error: ${(error as Error)?.message || 'Unknown error'}`,
          });
        }
      }
    };
    
    checkAuth();

    // Set up the listener for future auth state changes (like after successful login)
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state change:', event, 'has session:', !!session);
        
        // Handle TOKEN_REFRESHED event with error
        if (event === "TOKEN_REFRESHED" && !session) {
          console.warn('Token refresh failed, no session available');
          logAuthEvent({
            event_type: 'magic_link_error',
            error_message: 'Token refresh failed - no session',
          });
          return;
        }
        
        // SIGNED_IN event means user just logged in successfully - always redirect
        if (event === "SIGNED_IN" && session) {
          console.log('User signed in via auth listener, redirecting to dashboard...');
          // Clear any error states that might interfere
          setAuthFailedMessage("");
          setShowExpiredLinkMessage(false);
          router.push("/dashboard/default");
          router.refresh();
        }
        // INITIAL_SESSION only redirect if not from expired link or auth failed page
        else if (event === "INITIAL_SESSION" && session && !showExpiredLinkMessage && !authFailedMessage) {
          console.log('Initial session found, redirecting to dashboard...');
          router.push("/dashboard/default");
          router.refresh();
        }
        // Handle sign out events
        else if (event === "SIGNED_OUT") {
          console.log('User signed out');
        }
        else {
          console.log('Auth state change not handled:', event);
        }
      }
    );

    return () => {
      // Cleanup the listener when the component unmounts
      authListener.subscription.unsubscribe();
    };
  }, [supabase.auth, router, showExpiredLinkMessage, authFailedMessage]);

  const login = async (email: string) => {
    try {
      console.log('Requesting OTP for:', email);
      
      // Clear any previous error states when starting fresh OTP flow
      setAuthFailedMessage("");
      setShowExpiredLinkMessage(false);
      setCaptureError("");
      
      // Send OTP via email (no redirect URL - this sends a 6-digit code instead of a magic link)
      let { data: dataUser, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          shouldCreateUser: false,
        },
      });

      console.log('signInWithOtp result:', { data: dataUser, error });

      if (error) {
        console.error('Error in signInWithOtp:', error);
        console.error('Error details:', { 
          message: error.message, 
          status: error.status,
          name: error.name
        });
        
        // Check for rate limit error (429)
        if (error.status === 429 || error.message?.toLowerCase().includes('rate limit') || error.message?.toLowerCase().includes('too many requests')) {
          setCaptureError(
            "Too many login attempts. Please wait a few minutes before trying again."
          );
        } else if (error.message === "Signups not allowed for otp") {
          setCaptureError(
            "There is no account for this email. Please reach out to our team."
          );
        } else if (error.message) {
          setCaptureError(error.message);
        } else {
          setCaptureError("An error occurred while sending the verification code. Please try again.");
        }
        
        // Log the error
        logAuthEvent({
          event_type: 'otp_send_error',
          email: email,
          error_message: error.message || 'Unknown error during OTP send',
        });
      } else {
        console.log('OTP sent successfully');
        setEmail(email);
        setShowOtpInput(true);
        
        // Log successful OTP send
        logAuthEvent({
          event_type: 'otp_sent',
          email: email,
        });
      }
    } catch (error) {
      console.error('Unexpected error in login:', error);
      console.error('Error type:', typeof error, error);
      
      // Try to extract meaningful error message
      const err = error as any;
      if (err?.status === 429 || err?.message?.toLowerCase().includes('rate limit')) {
        setCaptureError('Too many login attempts. Please wait a few minutes before trying again.');
      } else if (err?.message) {
        setCaptureError(err.message);
      } else {
        setCaptureError('An unexpected error occurred. Please try again.');
      }
    }
  };

  const verifyOtp = async () => {
    if (!otp || otp.length !== 6) {
      setCaptureError("Please enter a valid 6-digit code.");
      return;
    }

    setIsVerifying(true);
    setCaptureError("");

    try {
      console.log('Verifying OTP for:', email);
      
      const { data, error } = await supabase.auth.verifyOtp({
        email,
        token: otp,
        type: 'email',
      });

      console.log('verifyOtp response:', { 
        hasData: !!data, 
        hasSession: !!data?.session, 
        hasUser: !!data?.user,
        error: error 
      });

      if (error) {
        console.error('Error verifying OTP:', error);
        
        if (error.message?.toLowerCase().includes('expired')) {
          setCaptureError("This code has expired. Please request a new one.");
        } else if (error.message?.toLowerCase().includes('invalid')) {
          setCaptureError("Invalid code. Please check and try again.");
        } else {
          setCaptureError(error.message || "Failed to verify code. Please try again.");
        }
        
        // Log the error
        logAuthEvent({
          event_type: 'otp_verify_error',
          email: email,
          error_message: error.message || 'Unknown error during OTP verification',
        });
      } else if (data?.session) {
        console.log('OTP verified successfully with session, user logged in');
        
        // Log successful OTP verification
        logAuthEvent({
          event_type: 'otp_verified',
          email: email,
          user_id: data.session.user.id,
        });
        
        // Clear any error states that might interfere with redirect
        setAuthFailedMessage("");
        setShowExpiredLinkMessage(false);
        
        // Redirect to dashboard
        console.log('Redirecting to dashboard...');
        
        // Use hard redirect for production reliability
        // This ensures cookies are properly read on the next page load
        window.location.href = '/dashboard/default';
      } else if (data?.user) {
        // Sometimes session isn't immediately available but user is
        console.log('OTP verified with user but no session, checking session...');
        
        // Wait a moment and check for session
        await new Promise(resolve => setTimeout(resolve, 500));
        const { data: sessionData } = await supabase.auth.getSession();
        
        if (sessionData?.session) {
          console.log('Session now available, redirecting...');
          
          // Log successful OTP verification
          logAuthEvent({
            event_type: 'otp_verified',
            email: email,
            user_id: sessionData.session.user.id,
          });
          
          // Clear any error states
          setAuthFailedMessage("");
          setShowExpiredLinkMessage(false);
          
          // Use hard redirect for production reliability
          window.location.href = '/dashboard/default';
        } else {
          console.error('No session available after verification');
          setCaptureError("Verification succeeded but session not established. Please try logging in again.");
        }
      } else {
        console.error('No session or user data returned from verifyOtp');
        setCaptureError("Failed to establish session. Please try again.");
      }
    } catch (error) {
      console.error('Unexpected error verifying OTP:', error);
      const err = error as any;
      setCaptureError(err?.message || 'An unexpected error occurred. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  const resendOtp = async () => {
    setCaptureError("");
    setOtp("");
    await login(email);
  };

  // Debug: Log state changes
  console.log('AuthLogin render:', { 
    authFailedMessage, 
    showExpiredLinkMessage,
    hasAuthFailedMessage: !!authFailedMessage,
    authFailedMessageLength: authFailedMessage?.length 
  });

  const borderColor = theme.palette.mode === ThemeMode.DARK ? theme.palette.grey[200] : theme.palette.grey[300];

  return (
    <>
      {!showOtpInput ? (
      <Formik
        initialValues={{
          email: "",
          submit: null,
        }}
        validationSchema={Yup.object().shape({
          email: Yup.string()
            .email("Must be a valid email")
            .max(255)
            .required("Email is required"),
        })}
        onSubmit={(values, { setSubmitting }) => {
          wakeUpApi();
          // Clear previous messages
          setCaptureError("");
          login(values.email);
          setSubmitting(false);
        }}
      >
        {({
          errors,
          handleBlur,
          handleChange,
          handleSubmit,
          isSubmitting,
          touched,
          values,
        }) => (
          <form noValidate onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              {showExpiredLinkMessage && (
                <Grid item xs={12}>
                  <Alert severity="warning">
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      <strong>Invite Link Expired</strong>
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      Your invite link has expired or has already been used.
                      This often happens when antivirus software or email scanners automatically click links.
                    </Typography>
                    <Typography variant="body2">
                      <strong>You can still log in by entering your email below to receive a verification code.</strong>
                    </Typography>
                  </Alert>
                </Grid>
              )}
              {authFailedMessage && (
                <Grid item xs={12}>
                  <Alert severity="error">
                    {authFailedMessage}
                  </Alert>
                </Grid>
              )}
              <Grid item xs={12}>
                <Stack spacing={1}>
                  <InputLabel htmlFor="email-login">Email Address</InputLabel>
                  <OutlinedInput
                    id="email-login"
                    type="email"
                    value={values.email}
                    name="email"
                    onBlur={handleBlur}
                    onChange={handleChange}
                    placeholder="Enter email address"
                    fullWidth
                    error={Boolean(touched.email && errors.email)}
                  />
                </Stack>
                {touched.email && errors.email && (
                  <FormHelperText
                    error
                    id="standard-weight-helper-text-email-login"
                  >
                    {errors.email}
                  </FormHelperText>
                )}
              </Grid>

              <Grid item xs={12} sx={{ mt: -1 }}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="center"
                  spacing={2}
                ></Stack>
              </Grid>
              {errors.submit && (
                <Grid item xs={12}>
                  <FormHelperText error>{errors.submit}</FormHelperText>
                </Grid>
              )}
              <Grid item xs={12}>
                <AnimateButton>
                  <Button
                    disableElevation
                    disabled={isSubmitting}
                    fullWidth
                    size="large"
                    type="submit"
                    variant="contained"
                    color="primary"
                  >
                      Send Verification Code
                  </Button>
                </AnimateButton>
                {captureError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {captureError}
                  </Alert>
                )}
              </Grid>
            </Grid>
          </form>
        )}
      </Formik>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="success">
              A 6-digit verification code has been sent to <strong>{email}</strong>
            </Alert>
          </Grid>
          <Grid item xs={12}>
            <Stack spacing={1}>
              <InputLabel>Enter Verification Code</InputLabel>
              <OtpInput
                value={otp}
                onChange={(newOtp: string) => setOtp(newOtp)}
                numInputs={6}
                isInputNum={true}
                containerStyle={{ justifyContent: 'space-between' }}
                inputStyle={{
                  width: '100%',
                  margin: '8px',
                  padding: '10px',
                  border: `1px solid ${borderColor}`,
                  borderRadius: 4,
                  fontSize: '18px',
                  textAlign: 'center',
                }}
                focusStyle={{
                  outline: 'none',
                  boxShadow: theme.customShadows.primary,
                  border: `1px solid ${theme.palette.primary.main}`
                }}
              />
            </Stack>
          </Grid>
          <Grid item xs={12}>
            <AnimateButton>
              <Button
                disableElevation
                disabled={isVerifying || otp.length !== 6}
                fullWidth
                size="large"
                variant="contained"
                color="primary"
                onClick={verifyOtp}
              >
                {isVerifying ? 'Verifying...' : 'Verify Code'}
              </Button>
            </AnimateButton>
            {captureError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {captureError}
              </Alert>
            )}
          </Grid>
          <Grid item xs={12}>
            <Stack direction="row" justifyContent="space-between" alignItems="baseline">
              <Typography>Did not receive the code?</Typography>
              <Typography 
                variant="body1" 
                sx={{ minWidth: 85, ml: 2, textDecoration: 'none', cursor: 'pointer' }} 
                color="primary"
                onClick={resendOtp}
              >
                Resend code
              </Typography>
            </Stack>
          </Grid>
        </Grid>
      )}
    </>
  );
};

export default AuthLogin;
