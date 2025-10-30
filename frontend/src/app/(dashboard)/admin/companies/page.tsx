"use client";

import { useState, useEffect } from "react";

// material-ui
import { Grid, Box } from "@mui/material";

// project import
import MainCard from "components/MainCard";

import ReactTable from "components/ReactTable";
import { getCompanies } from "app/api/GetCompanies"; // Import your API function
import { ColumnDef } from "@tanstack/react-table";
import AddCompany from "components/AddCompany";
// assets

export type TableDataProps = {
  id: number;
  company_name: string;
  report_type: string;
  energy_code: string;
  baseline_area: number;
  baseline_total_energy: number;
};

// ==============================|| DASHBOARD - DEFAULT ||============================== //

const DashboardDefault = () => {
  const [data, setData] = useState<TableDataProps[]>([]);

  const fetchCompanies = () => {
    // Fetch data from your API

    getCompanies().then((companyList: TableDataProps[]) => {
      setData(companyList);
    });
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const columns: ColumnDef<TableDataProps>[] = [
    {
      header: "Company Name",
      accessorKey: "company_name",
    },
  ];

  return (
    <Grid container rowSpacing={4.5} columnSpacing={2.75}>
      <Grid
        item
        xs={12}
        style={{ display: "flex", justifyContent: "flex-end" }}
      ></Grid>

      <Grid
        item
        md={8}
        sx={{ display: { sm: "none", md: "block", lg: "none" } }}
      />

      {/* row 3 */}
      <Grid item xs={12} md={7} lg={8}>
        <Box textAlign="right">
          <AddCompany onCompanyCreated={fetchCompanies} />
        </Box>
        <Grid
          container
          alignItems="center"
          justifyContent="space-between"
        ></Grid>
        <MainCard sx={{ mt: 2 }} content={false}>
          <ReactTable
            id="companies-table"
            data={data}
            columns={columns}
            pagination={"none"}
            title={"Companies"}
            clickToPage="admin/company"
          />
        </MainCard>
      </Grid>
    </Grid>
  );
};

export default DashboardDefault;
