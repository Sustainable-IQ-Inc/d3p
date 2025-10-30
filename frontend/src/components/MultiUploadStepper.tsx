import React, { ReactNode } from "react";
import { Stepper, Step, StepLabel, Typography } from "@mui/material";

interface StepperComponentProps {
  activeStep: number;
  steps: string[];
  errorIndex: number | null;
}

const StepperComponent: React.FC<StepperComponentProps> = ({
  activeStep,
  steps,
  errorIndex,
}) => {
  return (
    <Stepper activeStep={activeStep} sx={{ pt: 3, pb: 5 }}>
      {steps.map((label, index) => {
        const labelProps: { error?: boolean; optional?: ReactNode } = {};

        if (index === errorIndex) {
          labelProps.optional = (
            <Typography variant="caption" color="error">
              Error
            </Typography>
          );

          labelProps.error = true;
        }

        return (
          <Step key={label}>
            <StepLabel {...labelProps} style={{ fontSize: "20px" }}>
              {label}
            </StepLabel>
          </Step>
        );
      })}
    </Stepper>
  );
};

export default StepperComponent;
