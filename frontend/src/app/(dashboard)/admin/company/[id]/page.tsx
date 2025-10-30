"use client";

import { useState, useEffect } from "react";

// material-ui
import { Grid, Box, Typography } from "@mui/material";

// project import
import MainCard from "components/MainCard";

import ReactTable from "components/ReactTable";
import { getCompanyUsers } from "app/api/CompanyUsers"; // Import your API function
import { getCompany } from "app/api/GetCompany"; // Import company API function
import { ColumnDef } from "@tanstack/react-table";
import InviteUser from "components/AddUser";
// assets

export type TableDataProps = {
  user_email: string;
};

// ==============================|| DASHBOARD - DEFAULT ||============================== //

const DashboardDefault = ({ params }: { params: { id: string } }) => {
  const [data, setData] = useState<TableDataProps[]>([]);
  const [companyName, setCompanyName] = useState<string>("");

  console.log("=== COMPANY PAGE DEBUG ===");
  console.log("Component rendered with params:", params);
  console.log("Company ID from URL:", params.id);
  console.log("Current companyName state:", companyName);

  const fetchCompanyUsers = () => {
    console.log("Fetching company users for ID:", params.id);

    getCompanyUsers(params.id as string).then(
      (companyUsers: any) => {
        console.log("Company users fetched:", companyUsers);
        console.log("Type of response:", typeof companyUsers);
        console.log("Is array:", Array.isArray(companyUsers));
        
        // Ensure we always set an array
        if (Array.isArray(companyUsers)) {
          setData(companyUsers);
        } else {
          console.warn("Response is not an array, setting empty array");
          setData([]);
        }
      }
    ).catch((error: any) => {
      console.error("Error fetching company users:", error);
      setData([]);
    });
  };

  const fetchCompany = () => {
    console.log("Fetching company details for ID:", params.id);
    
    getCompany(params.id as string).then((company: any) => {
      console.log("API Response - Company data:", company);
      console.log("Company ID in response:", company?.id);
      console.log("Company name in response:", company?.company_name);
      
      if (company && company.company_name) {
        console.log("Setting company name to:", company.company_name);
        setCompanyName(company.company_name);
      } else {
        console.error("No company name found in response:", company);
      }
    }).catch((error: any) => {
      console.error("Error fetching company:", error);
    });
  };

  useEffect(() => {
    console.log("useEffect triggered - fetching data");
    fetchCompanyUsers();
    fetchCompany();
  }, [params.id]);

  const columns: ColumnDef<TableDataProps>[] = [
    {
      header: "Email",
      accessorKey: "email",
    },
  ];

  return (
    <Grid container rowSpacing={4.5} columnSpacing={2.75}>
      <Grid
        item
        md={8}
        sx={{ display: { sm: "none", md: "block", lg: "none" } }}
      />

      {/* row 3 */}

      <Grid item xs={12} md={7} lg={8}>
        {companyName && (
          <Typography variant="h3" sx={{ mb: 2 }}>
            {companyName}
          </Typography>
        )}
        <Box textAlign="right">
          <InviteUser onInviteUser={fetchCompanyUsers} companyId={params.id} />
        </Box>
        <Grid
          container
          alignItems="center"
          justifyContent="space-between"
        ></Grid>
        <MainCard sx={{ mt: 2 }} content={false}>
          {data.length === 0 ? (
            <Box sx={{ p: 3, textAlign: "center" }}>
              <Typography variant="body1" color="text.secondary">
                No users found for this company. Click "Invite User" to add users.
              </Typography>
            </Box>
          ) : (
            <ReactTable
              id="users-table"
              data={data}
              columns={columns}
              pagination={"bottom"}
              title={"Users"}
            />
          )}
        </MainCard>
      </Grid>
    </Grid>
  );
};

export default DashboardDefault;
