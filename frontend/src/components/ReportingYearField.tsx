import { FormControl, InputLabel, OutlinedInput } from "@mui/material";

export default function ReportingYearField({
  params,
  onChange,
}: {
  params: { 
    label: string; 
    required: boolean;
    populateValue?: number;
  };
  onChange: (value: number) => void;
}) {
  const currentYear = new Date().getFullYear();

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(event.target.value, 10);
    if (!isNaN(newValue)) {
      onChange(newValue);
    }
  };

  const displayValue = params.populateValue !== undefined && params.populateValue !== null 
    ? params.populateValue 
    : currentYear;

  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 250 }}>
        <InputLabel>
          {params.label}
          {params.required && " *"}
        </InputLabel>
        <OutlinedInput
          required={params.required}
          type="number"
          value={displayValue}
          label={params.label}
          onChange={handleChange}
          inputProps={{
            min: 1970,
            max: currentYear + 5,
          }}
        />
      </FormControl>
    </div>
  );
} 