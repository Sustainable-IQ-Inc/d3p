"use client";

import React, { useEffect, useState } from "react";

// next
import useSupabase from "../../../hooks/useSupabase";

// material-ui
import {
  Button,
  FormHelperText,
  InputLabel,
  Grid,
  OutlinedInput,
  Stack,
} from "@mui/material";

// third party
import * as Yup from "yup";
import { Formik } from "formik";

// project import
import AnimateButton from "components/@extended/AnimateButton";

import { wakeUpApi } from "app/api/WakeUp";

// assets
import { useRouter } from "next/navigation";

// ============================|| AWS CONNITO - LOGIN ||============================ //

const AuthLogin = () => {
  const supabase = useSupabase();

  const [success, setSuccess] = useState(false);
  const [captureError, setCaptureError] = useState("");

  const router = useRouter();
  // Immediately check if the user is already authenticated

  useEffect(() => {
    const userPromise = supabase.auth.getUser();

    userPromise.then((result) => {
      const userSession = result.data;
      if (userSession.user) {
        router.push("/dashboard/default");
        router.refresh();
      }
    });

    // Set up the listener for future auth state changes
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === "INITIAL_SESSION" && session) {
          router.push("/dashboard/default");
          router.refresh();
        } else if (event === "SIGNED_OUT" && session) {
          //do nothing
        }
      }
    );

    return () => {
      // Cleanup the listener when the component unmounts
      authListener.subscription.unsubscribe();
    };
  }, [supabase.auth, router]);

  const login = async (email: string) => {
    try {
      let { data: dataUser, error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: process.env.REDIRECT_URL,
          shouldCreateUser: false,
        },
      });

      if (dataUser) {
        const { user } = dataUser;

        if (user) {
          router.push("/dashboard/default");
        }
      }
      if (error) {
        if (error.message === "Signups not allowed for otp") {
          setCaptureError(
            "There is no account for this email. Please reach out to our team."
          );
        }
      } else {
        setSuccess(true);
      }
    } catch (error) {
      
    }
  };

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
                  <div style={{ backgroundColor: "lightgreen" }}>
                    An email has been sent with a link to login.
                  </div>
                )}
                {captureError && (
                  <div style={{ backgroundColor: "lightcoral" }}>
                    {captureError}
                  </div>
                )}
              </Grid>
            </Grid>
          </form>
        )}
      </Formik>
    </>
  );
};

export default AuthLogin;
