import {
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  SelectChangeEvent,
} from "@mui/material";
import { useEffect, useState } from "react";
import { getEnumList } from "./[enum_name]/page";

export default function EnumList({
  params,
  onChange,
}: {
  params: {
    enum_name: string;
    label: string;
    required: boolean;
    populateValue?: number;
    additional_fields?: string[];
    additional_filter_fields?: { [key: string]: any };
  };
  onChange: (value: string, additionalValues: { [key: string]: any }) => void;
}) {
  const [result, setResult] = useState<any[]>([]); // initialize state

  useEffect(() => {
    const fetchData = async () => {
      const data = await getEnumList(
        params.enum_name,
        params.additional_filter_fields &&
          Object.keys(params.additional_filter_fields).length > 0
          ? params.additional_filter_fields
          : undefined
      ); // Include additional_filter_fields in the request
      setResult(data); // set state
    };

    fetchData(); // call the async function
  }, [params.enum_name, params.additional_filter_fields]); // Add additional_filter_fields to the dependency array

  const handleChange = (event: SelectChangeEvent<string>) => {
    const selectedValue = event.target.value as string;
    let additionalValues: { [key: string]: any } = {};

    // If additional_fields is provided, find the corresponding values
    if (params.additional_fields) {
      const selectedItem = result.find((item) => item.id === selectedValue);
      if (selectedItem) {
        params.additional_fields.forEach((field) => {
          if (selectedItem.hasOwnProperty(field)) {
            additionalValues[field] = selectedItem[field];
          }
        });
      }
    }

    onChange(selectedValue, additionalValues);
  };

  return (
    <div>
      <FormControl sx={{ m: 1, minWidth: 250 }}>
        <InputLabel>
          {params.label}
          {params.required && " *"}
        </InputLabel>
        <Select
          id={"project-upload-" + params.enum_name}
          required={params.required}
          value={
            params.populateValue !== undefined
              ? params.populateValue.toString()
              : ""
          }
          placeholder="Select an option"
          label={params.label}
          onChange={handleChange}
        >
          {Array.isArray(result) && result.length > 0 ? (
            result.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.name}
              </MenuItem>
            ))
          ) : (
            <MenuItem disabled>No options available</MenuItem>
          )}
        </Select>
      </FormControl>
    </div>
  );
}
