"use client";
import React from "react";
import {
  Box,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Typography,
} from "@mui/material";

interface UnitSelectorProps {
  measurementSystem: string;
  setMeasurementSystem: (measurementSystem: string) => void;
}

export default function UnitSelector({
  measurementSystem,
  setMeasurementSystem,
}: UnitSelectorProps) {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMeasurementSystem(event.target.value as string);
  };

  return (
    <Box display="flex" alignItems="center">
      <Typography component="legend" style={{ marginRight: "10px" }}>
        Units:
      </Typography>
      <FormControl component="fieldset">
        <RadioGroup
          aria-label="units"
          name="units"
          value={measurementSystem}
          onChange={handleChange}
          row
        >
          <FormControlLabel
            value="Imperial"
            control={<Radio />}
            label="Imperial"
          />
          <FormControlLabel value="Metric" control={<Radio />} label="Metric" />
        </RadioGroup>
      </FormControl>
    </Box>
  );
}
