"use client";

import { useState, useEffect } from "react";
import { notFound, useRouter } from 'next/navigation';

// material-ui
import { Typography, Breadcrumbs, Link, Grid, Drawer, Button, Box } from "@mui/material";
import ProjectDetailSection from "components/ProjectDetailSection";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import ChangeHistory from "components/ProjectChangeHistory";
import AccessTimeIcon from '@mui/icons-material/AccessTime';

// project import

import { getProjectList } from "components/projects/project"; // Import your API function
import { getProjectDetails } from "app/api/ProjectDetails";
import ReactTable from "components/ReactTable";
import ReportCard from "components/cards/statistics/ReportCard";
import {  useDataReload } from "contexts/ProjectDataReload";
import ShareToDDXModal from 'components/ShareToDDXModal';
import { FetchDDXPreviewData } from 'app/api/ReturnDDXPreviewData';
import { getDDXIntegrationStatus } from 'app/api/apiKeyService';
import DDxShareButton from 'components/DDxShareButton';
import ExportProjectsButton from 'components/ExportProjectsButton';
import useUser from 'hooks/useUser';
import { apiRequest } from 'utils/apiClient';


// assets

export type TableDataProps = {
  user_email: string;
};

// ==============================|| DASHBOARD - DEFAULT ||============================== //

const ProjectDetailView = ({ params }: { params: { id: string } }) => {
  const router = useRouter();
  const { user } = useUser();
  const { reloadKey } = useDataReload();
  const [data, setData] = useState<any[]>([]);
  const [eeuDataEditDetails, setEeuDataEditDetails] = useState<any[]>([]);
  const [fuelTypes, setFuelTypes] = useState<string[]>([]);
  const [renewablesEditDetails, setRenewablesEditDetails] = useState<any[]>([]);
  const [selectedUnits, setSelectedUnits] = useState<string>('kbtu');
  const [isUnitsLoading, setIsUnitsLoading] = useState(false);

  const [isLoading, setIsLoading] = useState(true);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [ddxPreviewData, setDdxPreviewData] = useState<any>(null);
  const [ddxStatus, setDdxStatus] = useState<{
    has_been_shared: boolean;
    last_sync_date: string | null;
  } | null>(null);

  const toggleDrawer = (open: boolean) => () => {
    setIsDrawerOpen(open);
  };

  const toggleShareModal = async () => {
    if (!isShareModalOpen) {
      // Fetch DDX preview data when opening the modal
      try {
        const previewData = await FetchDDXPreviewData(params.id);
        setDdxPreviewData(previewData);
      } catch (error) {
        console.error('Error fetching DDX preview data:', error);
        setDdxPreviewData({ error: 'Failed to load DDX data' });
      }
    }
    setIsShareModalOpen(!isShareModalOpen);
  };

  const handleDDXSuccess = async () => {
    // Refresh both DDX status and preview data
    await fetchDDXStatus();
    try {
      const previewData = await FetchDDXPreviewData(params.id);
      setDdxPreviewData(previewData);
    } catch (error) {
      console.error('Error refreshing DDX preview data:', error);
    }
  };

  const fetchDDXStatus = async () => {
    try {
      const response = await getDDXIntegrationStatus(params.id);
      if (response.status === 'success') {
        setDdxStatus({
          has_been_shared: response.has_been_shared,
          last_sync_date: response.last_sync_date
        });
      }
    } catch (error) {
      console.error('Error fetching DDX status:', error);
    }
  };

  const formatLastSyncDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  const handleUnitsChange = async (newUnits: string) => {
    if (newUnits === selectedUnits) return;
    
    setIsUnitsLoading(true);
    setSelectedUnits(newUnits);
    
    // Small delay to ensure smooth transition
    setTimeout(() => {
      setIsUnitsLoading(false);
    }, 300);
  };

  useEffect(() => {
    console.log("Project detail useEffect triggered - reloadKey:", reloadKey);
    const fetchData = async () => {
      setIsLoading(true);
      try {
                          const [projectResponse, detailsResponse] = await Promise.all([
           getProjectList(undefined, false, "Imperial", params.id),
           getProjectDetails(params.id, undefined, selectedUnits)
         ]);
        
        if (!projectResponse || !Array.isArray(projectResponse) || projectResponse.length === 0 || !projectResponse[0]?.project_id) {
          notFound();
          return;
        }
        setData(projectResponse);
        
        if (detailsResponse.eeu_data?.length > 0) {
          setFuelTypes(detailsResponse.fuel_types);
          // Parse JSON strings if they are strings
          const eeuEditDetails = typeof detailsResponse.eeu_data_edit_details === 'string' 
            ? JSON.parse(detailsResponse.eeu_data_edit_details) 
            : detailsResponse.eeu_data_edit_details;
          setEeuDataEditDetails(eeuEditDetails);
          console.log('EEU Data Edit Details:', eeuEditDetails);
        } else {
          console.log('No EEU data found:', detailsResponse);
        }
        
        // Always process renewables data (even if empty) to ensure the table shows
        if (detailsResponse.renewables_edit_details) {
          // Parse JSON strings if they are strings
          const renewablesEditDetails = typeof detailsResponse.renewables_edit_details === 'string' 
            ? JSON.parse(detailsResponse.renewables_edit_details) 
            : detailsResponse.renewables_edit_details;
          setRenewablesEditDetails(renewablesEditDetails);
        } else {
          // Set empty array with default structure to ensure table still renders
          setRenewablesEditDetails([{
            'use_type': 'On-Site Renewables',
            'Solar PV_design': { value: 0, editable: true, edited: false },
            'Solar DHW_design': { value: 0, editable: true, edited: false },
            'Wind_On-SiteRenewables_design': { value: 0, editable: true, edited: false },
            'Other_On-SiteRenewables_design': { value: 0, editable: true, edited: false }
          }]);
        }
        
        await fetchDDXStatus();
        
      } catch (error) {
        console.error('Error fetching project data:', error);
        notFound();
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [params.id, reloadKey, selectedUnits]);

  const extractFuelTypes = (row: any) => {
    if (!row) {
      return;
    }

    const fuelTypesToSet = [
      ...new Set(
        Object.keys(row)
          .map((key) => {
            if (key === "use_type") {
              return null;
            }

            const lastUnderscoreIndex = key.lastIndexOf("_");
            return key.substring(0, lastUnderscoreIndex);
          })
          .filter(Boolean)
      ),
    ]; // remove null values

    return fuelTypesToSet.filter((fuelType) => fuelType !== null) as string[];
  };

  useEffect(() => {
    const fuelTypes = extractFuelTypes(eeuDataEditDetails && eeuDataEditDetails.length > 0 ? eeuDataEditDetails[0] : {});
    if (fuelTypes) {
      setFuelTypes(fuelTypes);
    }
  }, [eeuDataEditDetails]);

  const createColumns = (firstRow: any, isRenewables: boolean = false) => {
    return Object.keys(firstRow).map((key) => {
      // Skip the 'use_type' column
      if (key === "use_type") {
        return {
          header: "Use Type",
          accessorKey: "use_type",
          cell: (info: any) => {
            const value = info.getValue();
            if (value === 'Total') {
              const label = selectedUnits === 'kbtu/sf' ? 'Total: EUI' : 'Total: Gross Energy';
              return <div>{label}</div>;
            }
            return <div>{value}</div>;
          },
        };
      }

      // Determine the header based on the isRenewables flag
      let header;
      if (isRenewables) {
        header = key.replace(/_design$/, "").replace(/_/g, " ").toUpperCase();
      } else {
        header = key.substring(key.lastIndexOf("_") + 1).toUpperCase();
      }

      return {
        header,
        accessorKey: key,
        meta: {
          className: "cell-center",
        },
        cell: (info: any) => {
          const value = info.getValue();
          // Handle different value types
          if (value === null || value === undefined || value === '') {
            return <div>0</div>;
          }
          // If it's already a number, format it
          if (typeof value === 'number') {
            return (
              <div>
                {new Intl.NumberFormat("en-US", {
                  maximumFractionDigits: 1,
                }).format(value)}
              </div>
            );
          }
          // If it's a string that can be converted to a number
          const numValue = parseFloat(value);
          if (!isNaN(numValue)) {
            return (
              <div>
                {new Intl.NumberFormat("en-US", {
                  maximumFractionDigits: 1,
                }).format(numValue)}
              </div>
            );
          }
          // If it's a string that can't be converted, display as is
          return <div>{value}</div>;
        },
      };
    });
  };

  const firstRow = eeuDataEditDetails && eeuDataEditDetails.length > 0 ? eeuDataEditDetails[0] : {};
  const firstRowRewnewables = renewablesEditDetails && renewablesEditDetails.length > 0 ? renewablesEditDetails[0] : {
    'use_type': 'On-Site Renewables',
    'Solar PV_design': { value: 0, editable: true, edited: false },
    'Solar DHW_design': { value: 0, editable: true, edited: false },
    'Wind_On-SiteRenewables_design': { value: 0, editable: true, edited: false },
    'Other_On-SiteRenewables_design': { value: 0, editable: true, edited: false }
  };

  console.log('First row for EEU columns:', firstRow);
  console.log('EEU data for table:', eeuDataEditDetails);
  console.log('Renewables data for table:', renewablesEditDetails);
  console.log('First row for renewables columns:', firstRowRewnewables);

  const getUnitDisplayName = (unit: string) => {
    switch (unit) {
      case 'gj': return 'GJ';
      case 'kbtu': return 'kBtu';
      case 'kbtu/sf': return 'kBtu/SF';
      case 'mbtu': return 'MBtu';
      default: return unit;
    }
  };

  const columns = createColumns(firstRow);
  const columnsRenewables = createColumns(firstRowRewnewables, true);

  return (
    <div>
      <Drawer anchor="right" open={isDrawerOpen} onClose={toggleDrawer(false)}>
        <div
          role="presentation"
          onClick={toggleDrawer(false)}
          onKeyDown={toggleDrawer(false)}
          style={{ width: 450, padding: 20 }}
        >
          <Typography variant="h6" style={{ textAlign: "center", fontWeight: "bold" }}>Change History</Typography>
          <ChangeHistory project_id={params.id} />
        </div>
      </Drawer>

      <ShareToDDXModal
        open={isShareModalOpen}
        onClose={toggleShareModal}
        ddxPreviewData={ddxPreviewData}
        projectId={params.id}
        onSuccess={handleDDXSuccess}
      />

      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <div style={{ padding: '24px' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Breadcrumbs
            aria-label="breadcrumb"
            separator={<NavigateNextIcon fontSize="small" />}
          >
            <Link variant="h4" color="inherit" href="/dashboard/umbrella">
              Projects
            </Link>
            <Typography variant="h4">{data?.[0]?.project_name ?? 'Project'}</Typography>
          </Breadcrumbs>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <DDxShareButton
                onClick={toggleShareModal}
                eeuDataEditDetails={eeuDataEditDetails}
              />
              <ExportProjectsButton
                projectId={params.id}
                measurementSystem="Imperial"
              />
              {user.role === 'superadmin' && (
                <Button
                  variant="outlined"
                  color="error"
                  onClick={async () => {
                    if (!confirm('Delete this project and all related uploads/EEU data? This action cannot be undone.')) return;
                    try {
                      await apiRequest(`/projects/${params.id}/`, { method: 'DELETE' });
                      router.push('/dashboard/default');
                    } catch (e) {
                      alert('Failed to delete project');
                    }
                  }}
                >
                  Delete Project
                </Button>
              )}
              <Button
                variant="contained"
                color="primary"
                onClick={toggleDrawer(true)}
              >
                Change History
              </Button>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', mb: 3 }}>
            {ddxStatus?.has_been_shared ? (
              <>
                <AccessTimeIcon sx={{ color: 'success.dark', mr: 1, fontSize: 18 }} />
                <Typography variant="body2" color="success.dark">
                  Last DDx Share {formatLastSyncDate(ddxStatus.last_sync_date!)}
                </Typography>
              </>
            ) : (
              <>
                <AccessTimeIcon sx={{ color: 'primary.main', mr: 1, fontSize: 18 }} />
                <Typography variant="body2" color="primary.main">
                  Project has not been shared with the AIA 2030 DDx
                </Typography>
              </>
            )}
          </Box>

          <Grid container rowSpacing={4.5} columnSpacing={2.75} sx={{ paddingBottom: "10px" }}>
            <Grid item xs={12} lg={3} sm={6}>
              <ReportCard
                primary={data ? (data[0]?.conditioned_area ? `${Number(data[0].conditioned_area).toLocaleString()}` : "--") : "--"}
                secondary="Conditioned Area (GSF)"
              />
            </Grid>
            <Grid item xs={12} lg={3} sm={6}>
              <ReportCard
                primary={data ? (data[0]?.total_energy_per_unit_area_design ? Math.round(data[0].total_energy_per_unit_area_design) : "--") : "--"}
                secondary="Design Net PEUI (kBtu/SF)"
              />
            </Grid>
            <Grid item xs={12} lg={3} sm={6}>
              <ReportCard
                primary={data ? (data[0]?.total_energy_per_unit_area_baseline ? Math.round(data[0].total_energy_per_unit_area_baseline) : "--") : "--"}
                secondary="Baseline PEUI Energy (kBtu/SF)"
              />
            </Grid>
            <Grid item xs={12} lg={3} sm={6}>
              <ReportCard
                primary={data ? data[0]?.renewables : "--"}
                secondary="Renewables"
              />
            </Grid>
          </Grid>
          <Grid>
            <Grid style={{ paddingBottom: "10px" }}>
              <ProjectDetailSection
                data={data ? data[0] : null}
                detailPageView={true}
              />
            </Grid>
            <Grid>
              <div style={{ paddingBottom: "10px" }}>
                <ReactTable
                  id="renewables-table"
                  columns={columnsRenewables}
                  page_identifier={params.id}
                  data={renewablesEditDetails ? renewablesEditDetails : []}
                  pagination={"none"}
                  title={`Renewables Data (${getUnitDisplayName(selectedUnits)})`}
                  rowsPerPage={50}
                  showRowcount={false}
                  allowCellEdit={true}
                  editDetails={true}
                  showUnitsDropdown={true}
                  selectedUnits={selectedUnits}
                  onUnitsChange={handleUnitsChange}
                  isUnitsLoading={isUnitsLoading}
                  availableUnits={['gj', 'kbtu', 'mbtu']}
                />
              </div>
              <ReactTable
                id="eeu-table"
                columns={columns}
                data={eeuDataEditDetails ? eeuDataEditDetails : []}
                page_identifier={params.id}
                pagination={"none"}
                title={"EEU Data"}
                rowsPerPage={50}
                showColGroups={true}
                fuelTypes={fuelTypes}
                showRowcount={false}
                allowCellEdit={true}
                editDetails={true}
                showUnitsDropdown={true}
                selectedUnits={selectedUnits}
                onUnitsChange={handleUnitsChange}
                isUnitsLoading={isUnitsLoading}
              />
            </Grid>
          </Grid>
        </div>
      )}
    </div>
  );
};

export default ProjectDetailView;
