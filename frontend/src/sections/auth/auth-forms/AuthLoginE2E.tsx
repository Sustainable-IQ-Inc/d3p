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

import { wakeUpApi } from "app/api/WakeUp";

// assets
import { useRouter } from "next/navigation";

// ============================|| AWS CONNITO - LOGIN ||============================ //

const AuthLogin = () => {
  const supabase = useSupabase();

  // eslint-disable-next-line
  const [success, setSuccess] = useState(false);
  console.log("success", success);

  // eslint-disable-next-line
  const [captureError, setCaptureError] = useState("");
  console.log("captureError", captureError);
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

  const login = async (supabase: any, email: string, password: string) => {
    try {
      let { data: dataUser, error } = await supabase.auth.signInWithPassword({
        email,
        password,
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
          password: "",
          submit: null,
        }}
        validationSchema={Yup.object().shape({
          email: Yup.string()
            .email("Must be a valid email")
            .max(255)
            .required("Email is required"),
          password: Yup.string().max(255).required("Password is required"),
        })}
        onSubmit={(values, { setSubmitting }) => {
          wakeUpApi();
          login(supabase, values.email, values.password);
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
                <InputLabel htmlFor="password-login">Password</InputLabel>
                <OutlinedInput
                  id="password-login"
                  type="password"
                  value={values.password}
                  name="password"
                  onBlur={handleBlur}
                  onChange={handleChange}
                  placeholder="Enter password"
                  fullWidth
                  error={Boolean(touched.password && errors.password)}
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
            <Button
              id="submit-button"
              disableElevation
              disabled={isSubmitting}
              fullWidth
              size="large"
              type="submit"
              variant="contained"
              color="primary"
            >
              Login
            </Button>
          </form>
        )}
      </Formik>
    </>
  );
};

export default AuthLogin;
