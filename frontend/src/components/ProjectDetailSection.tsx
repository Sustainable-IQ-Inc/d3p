"use client";
import React, { useState, useEffect } from "react";
import { CardContent, Grid, Typography, Button, Box, Skeleton, SelectChangeEvent, Dialog, DialogContent, DialogTitle } from "@mui/material";
import MainCard from "components/MainCard";
import OperationalEnergyTable from "./OperationalEnergySection";
import OperationalCarbonTable from "./OperationalCarbonSection";
import Link from "next/link";
import EnergyUseChart from "./EnergyUseChart";
import { getProjectOperationalData } from "app/api/ProjectOperationalData";
import {
  OperationalDataProps,
  OperationalCarbonDataCombinedProps,
  OperationalEnergyDataCombinedProps,
  EmissionsFactorsProps,
} from "types/operational-data";
import { FormControl, Select, MenuItem } from "@mui/material";
import DetailsCard from "./DetailsCard";
import ShareToDDXModal from './ShareToDDXModal';
import { FetchDDXPreviewData } from 'app/api/ReturnDDXPreviewData';
import { getDDXIntegrationStatus } from 'app/api/apiKeyService';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import DDxShareButton from './DDxShareButton';

interface ProjectDetailSectionProps {
  data: any;
  detailPageView?: boolean;
}

const ProjectDetailSection: React.FC<ProjectDetailSectionProps> = ({
  data,
  detailPageView,
}) => {
  
  const [operationalEnergyData, setOperationalEnergyData] =
    useState<OperationalEnergyDataCombinedProps>();
  const [operationalCarbonData, setOperationalCarbonData] =
    useState<OperationalCarbonDataCombinedProps>();
    const [emissionsFactors, setEmissionsFactors] =
    useState<EmissionsFactorsProps>();
  const [selectedEnergyOption, setSelectedEnergyOption] = useState<string>('');
  const [isEditing, setIsEditing] = useState(false);
  const [editableData, setEditableData] = useState(data);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [ddxPreviewData, setDdxPreviewData] = useState<any>(null);
  const [ddxStatus, setDdxStatus] = useState<{
    has_been_shared: boolean;
    last_sync_date: string | null;
  } | null>(null);

  const fetchOperationalData = () => {
    // Fetch data from your API
    getProjectOperationalData(data.project_id)
      .then((operational_data: OperationalDataProps) => {
        
        // Transform data to the required format for react-select
        setOperationalEnergyData(operational_data.operational_energy_data);
        setOperationalCarbonData(operational_data.operational_carbon_data);
        setEmissionsFactors(operational_data.emissions_factors);
      })
      .catch((error: Error) => {
        // Handle the error here
        console.error(
          "Error fetching operational energy and carbon data:",
          error
        );
      });
  };

  const fetchDDXStatus = async () => {
    try {
      const response = await getDDXIntegrationStatus(data.project_id);
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

  const handleEnergyOptionChange = (event: SelectChangeEvent<string>) => {
    setSelectedEnergyOption(event.target.value);
  };

  const energyOptions = [
    { value: 'design', label: 'Design', available: operationalEnergyData?.design.status === 'success' },
    { value: 'baseline', label: 'Baseline', available: operationalEnergyData?.baseline.status === 'success' },
  ].filter(option => option.available);

  // Ensure we always have a valid selectedEnergyOption
  const validSelectedOption = energyOptions.find(option => option.value === selectedEnergyOption)?.value || energyOptions[0]?.value || 'design';

  const toggleShareModal = async () => {
    if (!isShareModalOpen) {
      // Fetch DDX preview data when opening the modal
      try {
        const previewData = await FetchDDXPreviewData(data.project_id);
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
      const previewData = await FetchDDXPreviewData(data.project_id);
      setDdxPreviewData(previewData);
    } catch (error) {
      console.error('Error refreshing DDX preview data:', error);
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

  useEffect(() => {
    if (energyOptions.length > 0) {
      setSelectedEnergyOption(energyOptions[0].value);
    }
  }, [operationalEnergyData]);

  useEffect(() => {
    fetchOperationalData();
    fetchDDXStatus();
 
  }, [data]);
  // Remove the local handleDataRefresh function
  // const handleDataRefresh = () => {
  //   fetchOperationalData();
  // };

  const handleEditClick = () => {
    setIsEditing(!isEditing);
  };
  useEffect(() => {
    if (data) {
      // Map conditioned_area to use_type_total_area for the DetailsCard
      const mappedData = {
        ...data,
        use_type_total_area: data.conditioned_area
      };
      setEditableData(mappedData);
    } else {
      setEditableData(data);
    }
  }, [data]);
  const handleFieldChange = (field: string, value: string) => {
    if (field === 'use_type_total_area') {
      // When GSF is updated, also update the conditioned_area field
      setEditableData({ 
        ...editableData, 
        [field]: value,
        conditioned_area: value 
      });
    } else {
      setEditableData({ ...editableData, [field]: value });
    }
  };
  const handleClose = () => {
    setIsEditing(false);
  };
  return (
    <>
      <ShareToDDXModal
        open={isShareModalOpen}
        onClose={toggleShareModal}
        ddxPreviewData={ddxPreviewData}
        projectId={data.project_id}
        onSuccess={handleDDXSuccess}
      />
      
      <Grid container spacing={3}>
        <Grid item xs={3}>
          {!isEditing && (
            <DetailsCard
              editableData={editableData}
              isEditing={isEditing}
              detailPageView={detailPageView}
              handleEditClick={handleEditClick}
              handleFieldChange={handleFieldChange}
              handleEnumChange={(field, value) => {
                setEditableData({ ...editableData, [field]: value });
              }}
              handleClose={handleClose} 
            />
          )}
        </Grid>

        <Dialog open={isEditing} onClose={handleEditClick} fullWidth maxWidth="md">
          <DialogTitle>Edit Details</DialogTitle>
          <DialogContent>
            <DetailsCard
              editableData={editableData}
              isEditing={isEditing}
              detailPageView={detailPageView}
              handleEditClick={handleEditClick}
              handleFieldChange={handleFieldChange}
              handleEnumChange={(field, value) => {
                setEditableData({ ...editableData, [field]: value });
              }}
              handleClose={handleClose} 
            />
          </DialogContent>
        </Dialog>

        <Grid item xs={5}>
          <Box mb={1.2}>
            {operationalEnergyData && (
              <OperationalEnergyTable data={operationalEnergyData} />
            )}
          </Box>
          {operationalCarbonData && emissionsFactors && operationalEnergyData ? (
            <OperationalCarbonTable carbonData={operationalCarbonData} 
            energyData={operationalEnergyData} 
            emissionsFactors={emissionsFactors} />
          ) : (
            <MainCard>
              <CardContent>
                <Skeleton variant="rectangular" height={200} />
              </CardContent>
            </MainCard>
          )}
        </Grid>
        <Grid item xs={4}>
          <MainCard 
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                <Typography variant="h6" fontWeight="bold">Energy End Uses</Typography>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  {energyOptions.length > 1 ? (
                    <FormControl variant="outlined" size="small" style={{ minWidth: 120, marginRight: '10px' }}>
                      <Select
                        value={validSelectedOption}
                        onChange={handleEnergyOptionChange}
                      >
                        {energyOptions.map((option) => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  ) : (
                    <Typography variant="body2" style={{ marginRight: '10px' }}>
                      {energyOptions[0]?.label || 'No options available'}
                    </Typography>
                  )}
                </div>
              </div>
            }
          >
            <CardContent>
              {operationalEnergyData ? (
                <EnergyUseChart 
                  projectId={data.project_id} 
                  baseline_design={validSelectedOption}
                />
              ) : (
                <Skeleton variant="rectangular" width={300} height={300} />
              )}
            </CardContent>
          </MainCard>
        </Grid>
        {!detailPageView && (
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Link href={`/projects/${data.project_id}`}>
                <Button variant="contained" color="primary">
                  Go to Project
                </Button>
              </Link>
              <DDxShareButton
                onClick={toggleShareModal}
                operationalEnergyData={operationalEnergyData}
              />
              
              <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
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
            </Box>
          </Grid>
        )}
      </Grid>
    </>
  );
};

export default ProjectDetailSection;
