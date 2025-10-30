'use client';


// material-ui
import {  FormHelperText, Grid, Stack } from '@mui/material';

// project imports
import MainCard from 'components/MainCard';
import UploadSingleFile from 'components/third-party/dropzone/SingleFile';

// third-party
import { Formik } from 'formik';
import * as yup from 'yup';

// assets

// ==============================|| PLUGINS - DROPZONE ||============================== //

const DropzoneSingle = ({title}: {title: string}) => {

  return (
    <Grid container spacing={3}>
      
      <Grid item xs={12}>
      <MainCard title={title}>
          <Formik
            initialValues={{ files: null }}
            onSubmit={(values: any) => {
              // submit form
            }}
            validationSchema={yup.object().shape({
              files: yup.mixed().required('Avatar is a required.')
            })}
          >
            {({ values, handleSubmit, setFieldValue, touched, errors }) => (
              <form onSubmit={handleSubmit}>
                <Grid container spacing={3}>
                  <Grid item xs={10}>
                    <Stack spacing={1.5} alignItems="center" height={100}>
                      <UploadSingleFile setFieldValue={setFieldValue} file={values.files} error={touched.files && !!errors.files} />
                      {touched.files && errors.files && (
                        <FormHelperText error id="standard-weight-helper-text-password-login">
                          {errors.files as string}
                        </FormHelperText>
                      )}
                    </Stack>
                  </Grid>
                </Grid>
              </form>
            )}
          </Formik>
        </MainCard>
      </Grid>
    </Grid>
  );
};

export default DropzoneSingle;
