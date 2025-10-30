import React, { useEffect, useState } from "react";
import { getCompanies } from "app/api/GetCompanies";
import {
  Select,
  MenuItem,
  SelectChangeEvent,
  InputLabel,
  FormControl,
} from "@mui/material";
import { createTheme, ThemeProvider } from "@mui/material/styles";

interface Company {
  id: string;
  company_name: string;
}

interface CompanyDropdownProps {
  userRole: string;
  defaultCompany?: string;
  label: string;
  onCompanyChange: (companyId: string) => void;
}

const CompanyDropdown: React.FC<CompanyDropdownProps> = ({
  userRole,
  defaultCompany,
  label,
  onCompanyChange,
}) => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>(
    defaultCompany || ""
  ); // Use the prop here

  

  const fetchCompanies = () => {
    // Fetch data from your API

    getCompanies().then((companyList: Company[]) => {
      if (Array.isArray(companyList)) {
        setCompanies(companyList);
        
      } else {
        console.error("companyList is not an array:", companyList);
      }
    });
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  if (userRole !== "superadmin") {
    return null; // Don't render the dropdown for non-superadmin users
  }

  const handleChange = (event: SelectChangeEvent<string>) => {
    const newValue = event.target.value as string;
    setSelectedCompany(newValue);
    onCompanyChange(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <FormControl variant="outlined" fullWidth>
        <InputLabel id="company-select-label">{label}:</InputLabel>
        <Select value={selectedCompany} onChange={handleChange} label={label}>
          {companies.map((company) => (
            <MenuItem key={company.id} value={company.id}>
              {company.company_name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </ThemeProvider>
  );
};

const theme = createTheme({
  components: {
    MuiSelect: {
      styleOverrides: {
        root: {
          width: "20%", // or any other value
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
  },
});
export default CompanyDropdown;
