// theme.ts

import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
    components: {
        MuiSelect: {
            styleOverrides: {
                root: {
                    width: "250px", // or any other value
                    fontSize: "0.8rem",
                },
            },
        },

        MuiInputBase: {
            styleOverrides: {
              input: {
                fontSize: "0.8rem",
              },
            },
          },
        MuiInputLabel: {
            styleOverrides: {
                root: {
                    fontSize: "0.8rem",
                },
                outlined: {
                    // change background-color to 'transparent'
                    backgroundColor: "transparent",
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none', 
                },
            },
        },
    },
});