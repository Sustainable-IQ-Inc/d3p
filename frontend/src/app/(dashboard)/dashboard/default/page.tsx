"use client";

import { useState, useEffect } from "react";

// material-ui
import {
  Grid,
  Skeleton,
  CircularProgress,
  Typography,
  Box,
} from "@mui/material";

// project import
import MainCard from "components/MainCard";
import dynamic from "next/dynamic";

const UmbrellaTable = dynamic(() => import("components/Umbrella"), {
  ssr: false,
});
import { getProjectList } from "components/projects/project"; // Import your API function
import { ColumnDef } from "@tanstack/react-table";
import useUser from "hooks/useUser";
import UnitSelector from "components/UnitSelector";
import CompanyDropdown from "components/CompanySelector";
import {  useDataReload } from "contexts/ProjectDataReload";

// assets

export type TableDataProps = {
  project_name: string;
  report_type: string;
  energy_code: string;
  baseline_area: number;
  baseline_total_energy: number;
  project_id: string;
};

// ==============================|| DASHBOARD - DEFAULT ||============================== //

const DashboardDefault = () => {
  const { user } = useUser();
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState<TableDataProps[]>([]);
  const { reloadData } = useDataReload();
  const [measurementSystem, setMeasurementSystem] = useState("Imperial");
  const [companyView, setCompanyView] = useState(user.companyId);

  const fetchProjects = (measurementSystem: string) => {
    setIsLoading(true);
    
    getProjectList(companyView, false, measurementSystem).then(
      (projectList: TableDataProps[]) => {
        setData(projectList);
        setIsLoading(false);
      }
    );
  };

  const handleCompanyChange = (companyId: string) => {
    setCompanyView(companyId);
  };

  useEffect(() => {
    fetchProjects(measurementSystem); // Modify this line
  }, [measurementSystem, companyView,reloadData]); // Modify this line

  const columns: ColumnDef<TableDataProps>[] = [
    {
      id: "id",
      accessorKey: "id",
      enableResizing: false,
      size: 0,
      enableSorting: true,
      sortingFn: "alphanumeric",
      cell: (info) => <div>{info.getValue() as any}</div>,
    },
    {
      id: "project_name",
      header: "Project Name",
      accessorKey: "project_name",
      enableResizing: false,
      size: 400,
      enableSorting: true,
      sortingFn: "alphanumeric",
      cell: (info) => <div>{info.getValue() as any}</div>,
    },
    {
      id: "project_use_type",
      header: "Use Type",
      accessorKey: "project_use_type",
      sortingFn: "alphanumeric",
      cell: (info) => <div>{info.getValue() as any}</div>,
    },

    {
      id: "conditioned_area",
      header: `Total Area (${measurementSystem === "Imperial" ? "GSF" : "M2"})`,
      accessorKey: "conditioned_area",
      cell: (info) => (
        <div>
          {new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(
            info.getValue() as number
          )}
        </div>
      ),
      sortingFn: "alphanumeric",
      enableColumnFilter: false,
    },

    {
      id: "total_energy_per_unit_area_design",
      header: `Design Net PEUI (${
        measurementSystem === "Imperial" ? "kBtu/ft2" : "kWh/M2"
      })`,
      accessorKey: "total_energy_per_unit_area_design",
      cell: (info) => (
        <div>
          {new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(
            info.getValue() as number
          )}
        </div>
      ),
      sortingFn: "alphanumeric",
      enableColumnFilter: false,
    },

    {
      id: "total_energy_per_unit_area_baseline",
      header: `Baseline PEUI Energy (${
        measurementSystem === "Imperial" ? "kBtu/ft2" : "kWh/M2"
      })`,

      accessorKey: "total_energy_per_unit_area_baseline",
      cell: (info) => (
        <div>
          {new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(
            info.getValue() as number
          )}
        </div>
      ),
      sortingFn: "alphanumeric",
      enableColumnFilter: false,
    },
    {
      id: "project_phase",
      header: "Project Phase",
      accessorKey: "project_phase",
      cell: (info) => <div>{info.getValue() as any}</div>,
      sortingFn: "alphanumeric",
    },
    {
      id: "climate_zone",
      header: "Climate Zone",
      accessorKey: "climate_zone",
      cell: (info) => <div>{info.getValue() as any}</div>,
      sortingFn: "alphanumeric",
    },
    {
      id: "renewables",
      header: "Renewables",
      accessorKey: "renewables",
      cell: (info) => <div>{info.getValue() as any}</div>,
      sortingFn: "alphanumeric",
    },
  ];

  return (
    <>
      <Box display="flex" justifyContent="flex-end">
        {user.role === "superadmin" && (
          <CompanyDropdown
            userRole={user.role}
            onCompanyChange={handleCompanyChange}
            label="Admin Only: View As Company"
          />
        )}
      </Box>
      <Grid container rowSpacing={4.5} columnSpacing={2.75}>
        <Grid
          item
          md={8}
          sx={{ display: { sm: "none", md: "block", lg: "none" } }}
        />

        {/* row 3 */}
        <Grid item xs={12} sm={12} md={12} lg={12} xl={12}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid item />
            <Grid item>
              <UnitSelector
                measurementSystem={measurementSystem}
                setMeasurementSystem={setMeasurementSystem}
              />
            </Grid>
          </Grid>
          <MainCard sx={{ mt: 2, width: "100%" }} content={false}>
            {isLoading ? (
              <div style={{ position: "relative" }}>
                <Skeleton variant="rectangular" width="100%" height={400} />
                <div
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: "50%",
                    transform: "translate(-50%, -50%)",
                    textAlign: "center",
                  }}
                >
                  <Typography
                    variant="h6"
                    style={{ color: "darkgrey", fontWeight: "bold" }}
                  >
                    Loading...
                  </Typography>
                  <CircularProgress />
                </div>
              </div>
            ) : data === null ? (
              <Typography
                variant="h6"
                style={{
                  textAlign: "center",
                  marginTop: "20px",
                  marginBottom: "20px",
                }}
              >
                No projects have been uploaded for your company.
              </Typography>
            ) : (
              <UmbrellaTable
                data={data}
                columnsNew={columns}
                pagination={"bottom"}
                title={"Projects"}
              />
            )}
          </MainCard>
        </Grid>
      </Grid>
      </>
  );
};

export default DashboardDefault;
