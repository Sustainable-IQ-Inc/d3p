import { RadioGroup, FormControlLabel, Radio } from "@mui/material";
import { useState } from "react";
interface UploadTypeSelectorProps {
  setUploadType: (value: string) => void;
}

const UploadTypeSelector: React.FC<UploadTypeSelectorProps> = ({
  setUploadType,
}) => {
  const [selectedValue, setSelectedValue] = useState("single");
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedValue(event.target.value);
    setUploadType(event.target.value);
  };
  return (
    <RadioGroup
      aria-label="projectType"
      name="projectType"
      value={selectedValue}
      onChange={handleChange}
      row
    >
      <FormControlLabel
        value="single"
        control={<Radio />}
        label="Single Project Upload"
      />
      <FormControlLabel
        value="multi"
        control={<Radio />}
        label="Multi Project Upload"
      />
      <FormControlLabel
        value="multi-excel"
        control={<Radio />}
        label="Multi Project Excel Upload"
      />
    </RadioGroup>
  );
};

export default UploadTypeSelector;
