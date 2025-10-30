'use client';

// next
import Image from 'next/legacy/image';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Box, Container, Stack, Typography, useMediaQuery } from '@mui/material';

// project imports
import MainCard from 'components/MainCard';

// types
import { ThemeDirection, ThemeMode } from 'types/config';

// assets
const worldMap = '/assets/images/contact/worldMap.png';

// ==============================|| CONTACT US - HEADER ||============================== //

function ContactHeader() {
  const theme = useTheme();
  const matchDownSM = useMediaQuery(theme.breakpoints.down('sm'));
  const matchDownLG = useMediaQuery(theme.breakpoints.down('lg'));
  const matchDownMD = useMediaQuery(theme.breakpoints.down('md'));

  let imagWidth = 600;
  imagWidth = matchDownLG ? 500 : imagWidth;
  imagWidth = matchDownMD ? 320 : imagWidth;

  let imagHight = 410;
  imagHight = matchDownLG ? 340 : imagHight;
  imagHight = matchDownMD ? 217 : imagHight;

  return (
    <MainCard
      sx={{
        position: 'relative',
        bgcolor: theme.palette.mode === ThemeMode.DARK ? 'grey.0' : 'grey.800',
        overflow: 'hidden',
        '&>*': {
          position: 'relative',
          zIndex: 5
        },
        '&:before': {
          content: '""',
          position: 'absolute',
          width: '100%',
          height: { xs: '100%', sm: 280, md: 380, lg: 480 },
          top: 0,
          left: 0,
          zIndex: 2,
          background:
            theme.direction === ThemeDirection.RTL
              ? {
                  xs: 'linear-gradient(-360.36deg, rgb(0, 0, 0) 14.79%, rgba(67, 67, 67, 0.28) 64.86%)',
                  md: 'linear-gradient(-329.36deg, rgb(0, 0, 0) 1.79%, rgba(67, 67, 67, 0.28) 64.86%)',
                  xl: 'linear-gradient(-329.36deg, rgb(0, 0, 0) 1.79%, rgba(67, 67, 67, 0.28) 64.86%)'
                }
              : 'linear-gradient(329.36deg, rgb(0, 0, 0) 14.79%, rgba(67, 67, 67, 0.28) 64.86%)'
        },
        border: 'transparent',
        borderRadius: 0,
        m: 0,
        height: { xs: '100%', sm: 280, md: 380, lg: 480 }
      }}
    >
      <Container maxWidth="lg" sx={{ px: { xs: 0, sm: 2 } }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-around" alignItems="center" spacing={{ xs: 0, sm: 3 }}>
          <Box sx={{ width: { xs: '100%', sm: 252, md: 360, lg: 436 }, pt: 6 }}>
            <Stack spacing={1}>
              <Typography
                align={matchDownSM ? 'center' : 'left'}
                variant="h2"
                color={theme.palette.mode === ThemeMode.DARK ? 'text.primary' : 'secondary.lighter'}
              >
                Talk to our{' '}
                <Typography variant="h2" component="span" color="primary" sx={{ cursor: 'pointer' }}>
                  Expert
                </Typography>
              </Typography>
              <Typography align={matchDownSM ? 'center' : 'left'} color="textSecondary">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
              </Typography>
            </Stack>
          </Box>
          <Image src={worldMap} alt="mantis" layout="fixed" width={imagWidth} height={imagHight} />
        </Stack>
      </Container>
    </MainCard>
  );
}

export default ContactHeader;
