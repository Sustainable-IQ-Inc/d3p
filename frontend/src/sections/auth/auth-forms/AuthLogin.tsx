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

// project import
import AnimateButton from "components/@extended/AnimateButton";

import { wakeUpApi } from "app/api/WakeUp";
import { logAuthEvent } from "utils/authLogger";

// assets
import { useRouter } from "next/navigation";

// ============================|| AWS CONNITO - LOGIN ||============================ //

const AuthLogin = () => {
  const supabase = useSupabase();
  const searchParams = useSearchParams();

  const [success, setSuccess] = useState(false);
  const [captureError, setCaptureError] = useState("");
  const [showExpiredLinkMessage, setShowExpiredLinkMessage] = useState(false);
  const [authFailedMessage, setAuthFailedMessage] = useState("");

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
        const { data } = await supabase.auth.getUser();
        if (data.user) {
          console.log('User already logged in, redirecting...');
          router.push("/dashboard/default");
          router.refresh();
        }
      }
    };
    
    checkAuth();

    // Set up the listener for future auth state changes (like after successful login)
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        console.log('Auth state change:', event, 'has session:', !!session);
        
        // SIGNED_IN event means user just logged in successfully - always redirect
        if (event === "SIGNED_IN" && session) {
          console.log('User signed in, redirecting to dashboard...');
          router.push("/dashboard/default");
          router.refresh();
        }
        // INITIAL_SESSION only redirect if not from expired link or auth failed page
        else if (event === "INITIAL_SESSION" && session && !showExpiredLinkMessage && !authFailedMessage) {
          console.log('Initial session found, redirecting to dashboard...');
          router.push("/dashboard/default");
          router.refresh();
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
      console.log('Requesting magic link for:', email);
      
      // Construct redirect URL - use window.location.origin for client-side
      const redirectUrl = typeof window !== 'undefined' 
        ? `${window.location.origin}/callback`
        : `${process.env.REDIRECT_URL || 'http://localhost:8081'}/callback`;
      
      console.log('Email redirect URL:', redirectUrl);
      
      let { data: dataUser, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: redirectUrl,
          shouldCreateUser: false,
        },
      });

      console.log('signInWithOtp result:', { data: dataUser, error });

      if (dataUser) {
        const { user } = dataUser;

        if (user) {
          console.log('User returned in OTP response, redirecting to dashboard');
          
          // Log successful magic link send (user.id may not be available in OTP response)
          const userId = (user as any)?.id;
          if (userId) {
            logAuthEvent({
              event_type: 'magic_link_sent',
              email: email,
              user_id: userId,
              magic_link_url: redirectUrl,
            });
          }
          
          router.push("/dashboard/default");
        }
      }
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
          setCaptureError("An error occurred while sending the magic link. Please try again.");
        }
        
        // Log the error
        logAuthEvent({
          event_type: 'magic_link_error',
          email: email,
          error_message: error.message || 'Unknown error during magic link send',
        });
      } else {
        console.log('Magic link sent successfully');
        setSuccess(true);
        
        // Log successful magic link send
        // Note: We don't have user_id at this point since Supabase doesn't return it
        // for security reasons, but we log the email and redirect URL
        logAuthEvent({
          event_type: 'magic_link_sent',
          email: email,
          magic_link_url: redirectUrl,
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

  // Debug: Log state changes
  console.log('AuthLogin render:', { 
    authFailedMessage, 
    showExpiredLinkMessage,
    hasAuthFailedMessage: !!authFailedMessage,
    authFailedMessageLength: authFailedMessage?.length 
  });

  return (
    <>
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
          setSuccess(false);
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
              {showExpiredLinkMessage ? (
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
                      <strong>Please contact your administrator to resend your invitation.</strong>
                    </Typography>
                  </Alert>
                </Grid>
              ) : (
                <>
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
                    Send Magic Link
                  </Button>
                </AnimateButton>
                {success && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    An email has been sent with a link to login.
                  </Alert>
                )}
                {captureError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {captureError}
                  </Alert>
                )}
              </Grid>
                </>
              )}
            </Grid>
          </form>
        )}
      </Formik>
    </>
  );
};

export default AuthLogin;
