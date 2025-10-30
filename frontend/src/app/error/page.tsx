'use client';

// next
import NextLink from 'next/link';

// material-ui
import { Button, Grid, Stack, Typography, Box } from '@mui/material';

// project import
import AnimateButton from 'components/@extended/AnimateButton';
import AuthWrapper from 'sections/auth/AuthWrapper';

// ================================|| ERROR PAGE ||================================ //

const ErrorPage = () => {
  return (
    <AuthWrapper>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box sx={{ mb: { xs: -0.5, sm: 0.5 } }}>
            <Typography variant="h3">Verification Failed</Typography>
            <Typography color="secondary" sx={{ mb: 0.5, mt: 1.25 }}>
              We couldn't verify your email link. This could happen if:
            </Typography>
            <Box component="ul" sx={{ mt: 2, mb: 2, pl: 3 }}>
              <Typography component="li" color="secondary">
                The link has expired (links are valid for a limited time)
              </Typography>
              <Typography component="li" color="secondary">
                The link has already been used
              </Typography>
              <Typography component="li" color="secondary">
                The link was copied incorrectly
              </Typography>
            </Box>
            <Typography color="secondary">
              Please request a new invitation or magic link and try again.
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Stack spacing={2}>
            <AnimateButton>
              <NextLink href="/login" passHref legacyBehavior>
                <Button 
                  disableElevation 
                  fullWidth 
                  size="large" 
                  variant="contained" 
                  color="primary"
                >
                  Go to Login
                </Button>
              </NextLink>
            </AnimateButton>
          </Stack>
        </Grid>
      </Grid>
    </AuthWrapper>
  );
};

export default ErrorPage;

