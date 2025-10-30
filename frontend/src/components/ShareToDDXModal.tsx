import React from 'react';
import { Modal, Box, Typography, Button, Grid, TextField, IconButton, Tooltip, FormControl, Select, MenuItem } from '@mui/material';
import { message } from 'antd';
import { authenticateDDX } from 'app/api/apiKeyService';
import useUser from 'hooks/useUser';
import EditIcon from '@mui/icons-material/Edit';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import WarningIcon from '@mui/icons-material/Warning';
import submitUpload from 'app/api/UpdateProjectDetails';
import { useDataReload } from 'contexts/ProjectDataReload';
import { ProjectUpdate } from 'types/updates';
import EnumList from 'components/enums/enum_list';
import DDXPreValidationModal from './DDXPreValidationModal';
import ReactTable from 'components/ReactTable';

interface DDXPreviewField {
  value: string | number;
  editable: boolean;
}

interface DDXPreviewData {
  [key: string]: DDXPreviewField;
}

interface ShareToDDXModalProps {
  open: boolean;
  onClose: () => void;
  ddxPreviewData: DDXPreviewData | { error: string } | null;
  projectId: string;
  onSuccess?: () => void; // Optional callback for successful upload
}

const modalStyle = {
  position: 'absolute' as const,
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '80%',
  maxWidth: 800,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
  maxHeight: '90vh',
  overflow: 'auto',
  borderRadius: 2,
};

const formatValue = (key: string, value: string | number): string => {
  if (key.includes('EUI') || key.includes('Energy Use Intensity')) {
    return `${value} kBtu/SF`;
  }
  if (key === 'Use Type Area') {
    // Format the number with commas and add ft2 unit
    const numValue = typeof value === 'string' ? parseFloat(value.replace(/,/g, '')) : value;
    return `${numValue.toLocaleString()} ft2`;
  }
  return value.toString();
};

const ShareToDDXModal: React.FC<ShareToDDXModalProps> = ({ open, onClose, ddxPreviewData, projectId, onSuccess }) => {
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = React.useState(true);
  const [editedValues, setEditedValues] = React.useState<Record<string, string | number>>({});
  const [editingFields, setEditingFields] = React.useState<Record<string, boolean>>({});
  const [showPreValidation, setShowPreValidation] = React.useState(false);
  const [canSubmitToDDX, setCanSubmitToDDX] = React.useState(false);
  const [validationResult, setValidationResult] = React.useState<any>(null);
  const [hasEditedValues, setHasEditedValues] = React.useState(false);
  const { user } = useUser();
  const { reloadData } = useDataReload();

  // Add state for custom project ID
  const [customProjectId, setCustomProjectId] = React.useState<string>('');
  const [previousCustomProjectId, setPreviousCustomProjectId] = React.useState<string>('');

  // Add state for Use Type
  const [selectedUseTypeId, setSelectedUseTypeId] = React.useState<number | null>(null);
  const [originalUseTypeId, setOriginalUseTypeId] = React.useState<number | null>(null);

  // Add state for Energy Code
  const [selectedEnergyCodeId, setSelectedEnergyCodeId] = React.useState<number | null>(null);
  const [originalEnergyCodeId, setOriginalEnergyCodeId] = React.useState<number | null>(null);

  // Helper function to determine if a field should be editable
  const isFieldEditable = (key: string, data: DDXPreviewField): boolean => {
    const alwaysEditableFields = ['Use Type Area', 'Energy Code', 'Use Type', 'Design Energy Code', 'Reporting Year', 'Occupancy Year'];
    return data.editable || alwaysEditableFields.includes(key);
  };

  // Helper function to check if a field is a fuel subtotal
  const isFuelSubtotal = (key: string): boolean => {
    const fuelSubtotalFields = [
      'Electricity Produced Off-Site (MBtu)',
      'Natural Gas Combusted On-Site (MBtu)',
      'District Steam (MBtu)',
      'District Hot Water (MBtu)',
      'District Chilled Water (MBtu)',
      'Diesel (MBtu)',
      'Electricity from Renewables On-Site (MBtu)'
    ];
    return fuelSubtotalFields.includes(key);
  };

  React.useEffect(() => {
    const checkAuth = async () => {
      if (open) {
        try {
          const result = await authenticateDDX(user.id);
          setIsAuthenticated(result.status === 'success')
          if (result.status === 'error') {
            setError(result.message);
            console.error('Error authenticating with DDX:', result.message);
          }
        } catch (err) {
          setIsAuthenticated(false);
          setError('Failed to authenticate with DDX. Please check your API credentials in Settings.');
        }
      }
    };
    checkAuth();
  }, [open, user.id]);

  React.useEffect(() => {
    if (ddxPreviewData && !('error' in ddxPreviewData)) {
      const projectIdField = Object.entries(ddxPreviewData).find(([key]) => key === 'Project ID');
      if (projectIdField) {
        const projectIdValue = String(projectIdField[1].value);
        setCustomProjectId(projectIdValue);
        setPreviousCustomProjectId(projectIdValue);
      }
      
      // Try to extract Use Type ID from DDX preview data
      const fetchCurrentUseType = async () => {
        
        // Look for the original Use Type ID in the DDX preview data
        const originalUseTypeIdField = Object.entries(ddxPreviewData).find(([key]) => key === '_original_useType1_id');
        if (originalUseTypeIdField && typeof originalUseTypeIdField[1] === 'object' && 'value' in originalUseTypeIdField[1]) {
          const rawValue = originalUseTypeIdField[1].value;
          
          // Try to convert to number, but check if it's valid
          const originalUseTypeId = Number(rawValue);
          
          // Only set if we have a valid number
          if (!isNaN(originalUseTypeId) && originalUseTypeId > 0) {
            setSelectedUseTypeId(originalUseTypeId);
            setOriginalUseTypeId(originalUseTypeId);
          } else if (isNaN(originalUseTypeId)) {
            console.log('Invalid Use Type ID from DDX preview data, skipping');
          }
        } else {
          
          // Fallback: try the old _original_Use Type field (though this contains name, not ID)
          const originalUseTypeField = Object.entries(ddxPreviewData).find(([key]) => key === '_original_Use Type');
          if (originalUseTypeField && typeof originalUseTypeField[1] === 'object' && 'value' in originalUseTypeField[1]) {

           }
         }
         
         // Extract Energy Code ID from DDX preview data
         const originalEnergyCodeIdField = Object.entries(ddxPreviewData).find(([key]) => key === '_original_designEnergyCode_id');
         if (originalEnergyCodeIdField && typeof originalEnergyCodeIdField[1] === 'object' && 'value' in originalEnergyCodeIdField[1]) {
           const rawValue = originalEnergyCodeIdField[1].value;
           
           // Try to convert to number, but check if it's valid
           const originalEnergyCodeId = Number(rawValue);
           
           // Only set if we have a valid number
           if (!isNaN(originalEnergyCodeId) && originalEnergyCodeId > 0) {
             setSelectedEnergyCodeId(originalEnergyCodeId);
             setOriginalEnergyCodeId(originalEnergyCodeId);
           } else if (isNaN(originalEnergyCodeId)) {
             console.log('Invalid Energy Code ID from DDX preview data, skipping');
           }
         } else {
           console.log('No _original_designEnergyCode_id found in DDX preview data');
         }
       };
      
      fetchCurrentUseType();
    }
  }, [ddxPreviewData, projectId]);



  const handleValueChange = (key: string, value: string) => {
    const isStringField = ['Project ID', 'Energy Code', 'Design Energy Code', 'Use Type Area', 'Use Type', 'City', 'State', 'Zip Code', 'Country', 'Reporting Year', 'Occupancy Year'].includes(key);
    const finalValue = isStringField ? value : Number(value);
    
    setEditedValues(prev => ({
      ...prev,
      [key]: finalValue
    }));
    setHasEditedValues(true);
  };

  // New function to handle location updates
  const handleLocationUpdate = async () => {
    const locationFields = ['City', 'State', 'Zip Code'];
    
    // Check if there are actual changes by comparing with original values
    const hasActualChanges = locationFields.some(field => {
      const editedValue = editedValues[field];
      if (editedValue === undefined) return false;
      
      // Get original value from DDX preview data
      const originalData = ddxPreviewData && !('error' in ddxPreviewData) ? ddxPreviewData[field] : null;
      const originalValue = originalData && typeof originalData === 'object' && 'value' in originalData 
        ? String(originalData.value) 
        : '';
      

      
      return editedValue !== originalValue;
    });
    

    
    if (!hasActualChanges) {
      console.log('No actual changes detected, skipping save');
      return;
    }

    try {
      const submitEEUUpdate = (await import('app/api/UpdateEnergyFields')).default;
      
      const updateProps: any = {
        project_id: projectId,
      };

      // Add only the changed location fields (mapping from display names to API field names)
      if (editedValues['City'] !== undefined) updateProps.city = editedValues['City'];
      if (editedValues['State'] !== undefined) updateProps.state = editedValues['State'];
      if (editedValues['Zip Code'] !== undefined) updateProps.zip_code = editedValues['Zip Code'];



      const result = await submitEEUUpdate({ updateProps });
      

      
      if (result === 'success') {
        message.success('Location updated successfully');
        
        // If zip code was changed, trigger climate zone validation
        if (editedValues['Zip Code'] !== undefined) {
          await triggerClimateZoneValidation(String(editedValues['Zip Code']));
        }
        
        reloadData(); // Reload the data to reflect changes
      } else {
        console.error('handleLocationUpdate - API returned non-success result:', result);
        message.error('Failed to update location');
      }
    } catch (error) {
      console.error('Error updating location:', error);
      console.error('Error details:', JSON.stringify(error, null, 2));
      message.error('Failed to update location');
    }
  };

  // Function to trigger climate zone validation
  const triggerClimateZoneValidation = async (zipCode: string) => {
    try {
      const validateZip = (await import('app/api/ValidateZip')).default;
      const response = await validateZip({ zip_code: zipCode, project_id: projectId });
      
      if (response.data.status === "success") {
        message.success("Climate zone updated successfully based on new zip code");
        
        // Trigger refresh of DDX preview data in parent component
        if (onSuccess) {
          onSuccess();
        }
      } else {
        message.warning("Failed to update climate zone. Please verify the zip code.");
      }
    } catch (error) {
      console.error('Error validating climate zone:', error);
      message.warning("Failed to update climate zone. Please verify the zip code.");
    }
  };

  const [lastToggleCall, setLastToggleCall] = React.useState<number>(0);

  const toggleEditing = async (key: string) => {
    // Prevent rapid double-calls
    const now = Date.now();
    if (now - lastToggleCall < 100) {
      return;
    }
    setLastToggleCall(now);
    
    const isProjectId = key === 'Project ID';
    const isLocationField = ['City', 'State', 'Zip Code'].includes(key);
    const isYearField = ['Reporting Year', 'Occupancy Year'].includes(key);
    const wasEditing = editingFields[key];
    const isAnyLocationFieldEditing = ['City', 'State', 'Zip Code'].some(field => editingFields[field]);
    
    // For location fields, enable/disable editing for all location fields together
    if (isLocationField) {
      const shouldEnableEditing = !isAnyLocationFieldEditing;
      
      setEditingFields(prev => ({
        ...prev,
        'City': shouldEnableEditing,
        'State': shouldEnableEditing,
        'Zip Code': shouldEnableEditing
      }));

      // If we're turning off editing (exiting edit mode), save any changes
      if (isAnyLocationFieldEditing && !shouldEnableEditing) {
        await handleLocationUpdate();
      }
    } else {
      setEditingFields(prev => ({
        ...prev,
        [key]: !prev[key]
      }));
    }
    
    // If we're turning off editing for Project ID and the value has changed
    if (isProjectId && wasEditing && customProjectId !== previousCustomProjectId) {
      try {
        const updateProps: ProjectUpdate = {
          project_id: projectId, // Already a string, don't convert to number
          custom_project_id: customProjectId,
          user_id: user.id
        };
        
        const result = await submitUpload({ updateProps });
        
        if (result === 'success') {
          message.success('Project ID updated successfully');
          setPreviousCustomProjectId(customProjectId);
          reloadData(); // Reload the data to reflect changes
        } else if (result === 'custom_project_id_not_unique') {
          message.error('This Project ID already exists in your company. Please choose a unique Project ID.');
          setCustomProjectId(previousCustomProjectId); // Revert on failure
        } else {
          message.error('Failed to update Project ID');
          setCustomProjectId(previousCustomProjectId); // Revert on failure
        }
      } catch (error) {
        console.error('Error updating Project ID:', error);
        message.error('Failed to update Project ID');
        setCustomProjectId(previousCustomProjectId); // Revert on failure
      }
    }
    
    // Handle year field updates
    if (isYearField && wasEditing && editedValues[key] !== undefined) {
      const originalData = ddxPreviewData && !('error' in ddxPreviewData) ? ddxPreviewData[key] : null;
      const originalValue = originalData && typeof originalData === 'object' && 'value' in originalData 
        ? String(originalData.value) 
        : '';

      if (String(editedValues[key]) !== originalValue) {
        try {
          const fieldMapping = key === 'Reporting Year' ? 'reporting_year' : 'year';
          const updateProps: ProjectUpdate = {
            project_id: projectId,
            [fieldMapping]: Number(editedValues[key]),
            user_id: user.id
          };
          
          const result = await submitUpload({ updateProps });
          
          if (result === 'success') {
            message.success(`${key} updated successfully`);
            reloadData(); // Reload the data to reflect changes
          } else if (result === 'custom_project_id_not_unique') {
            message.error('This Project ID already exists in your company. Please choose a unique Project ID.');
          } else {
            message.error(`Failed to update ${key}`);
          }
        } catch (error) {
          console.error(`Error updating ${key}:`, error);
          message.error(`Failed to update ${key}`);
        }
      }
    }
    
    // Handle other fields - initialize edited values for editing but don't save to database
    if (!isProjectId && !isLocationField && !isYearField && !editingFields[key] && !editedValues[key] && ddxPreviewData && !('error' in ddxPreviewData)) {
      const rawValue = String(ddxPreviewData[key].value).replace(/,/g, '').replace('kBtu/SF', '').replace('ft2', '').trim();
      setEditedValues(prev => ({
        ...prev,
        [key]: (key === 'Energy Code' || key === 'Design Energy Code' || key === 'Use Type Area' || key === 'Use Type') ? rawValue : Number(rawValue)
      }));
      
      // Special handling for Use Type - ensure selectedUseTypeId is set when entering edit mode
      if (key === 'Use Type' && selectedUseTypeId === null && originalUseTypeId !== null) {
        setSelectedUseTypeId(originalUseTypeId);
      }
      
      // Special handling for Energy Code - ensure selectedEnergyCodeId is set when entering edit mode
      if ((key === 'Energy Code' || key === 'Design Energy Code') && selectedEnergyCodeId === null && originalEnergyCodeId !== null) {
        setSelectedEnergyCodeId(originalEnergyCodeId);
      }
    }

    // Initialize year fields when entering edit mode
    if (isYearField && !editingFields[key] && !editedValues[key] && ddxPreviewData && !('error' in ddxPreviewData)) {
      const currentValue = typeof ddxPreviewData[key] === 'object' && 'value' in ddxPreviewData[key] 
        ? String(ddxPreviewData[key].value) 
        : '';
      setEditedValues(prev => ({
        ...prev,
        [key]: currentValue
      }));
    }

    // Handle location fields - initialize edited values when entering edit mode
    if (isLocationField && !isAnyLocationFieldEditing && ddxPreviewData && !('error' in ddxPreviewData)) {
      const locationFields = ['City', 'State', 'Zip Code'];
      setEditedValues(prev => {
        const newValues = { ...prev };
        locationFields.forEach(field => {
          if (ddxPreviewData[field] && !newValues[field]) {
            const currentValue = typeof ddxPreviewData[field] === 'object' && 'value' in ddxPreviewData[field] 
              ? ddxPreviewData[field].value 
              : ddxPreviewData[field];
            newValues[field] = String(currentValue);
          }
        });
        return newValues;
      });
    }
  };

  const handleSubmit = async () => {
    try {
      setError(null);
      setIsSubmitting(true);
      const requestBody = { 
        project_id: projectId,
        edited_values: {
          ...editedValues,
          'Project ID': customProjectId // Add the custom project ID to the edited values
        }
      };
      

      
      // Use direct fetch instead of apiRequest to handle 422 errors properly
      const supabase = (await import('utils/supabase')).createClient();
      const { data: session } = await supabase.auth.getSession();
      
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/export_project_to_ddx/`;
      const fetchResponse = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.session?.access_token}`,
        },
        body: JSON.stringify(requestBody),
      });


      
      const responseData = await fetchResponse.json();


      // Check for HTTP errors OR response body errors
      if (!fetchResponse.ok || (responseData && responseData.status === 'error')) {
        // Handle 422 and other error responses, or response body errors
        let errorMessage = 'Unknown error occurred';
        
        if (responseData && typeof responseData === 'object') {
          if ('message' in responseData) {
            // Try to parse the message if it's JSON
            try {
              const parsedMessage = JSON.parse(responseData.message);
              if (parsedMessage.error && typeof parsedMessage.error === 'object') {
                errorMessage = Object.entries(parsedMessage.error)
                  .map(([field, msg]) => `${field}: ${msg}`)
                  .join('\n');
              } else {
                errorMessage = String(responseData.message);
              }
            } catch (e) {
              // If parsing fails, use the raw message
              errorMessage = String(responseData.message);
            }
          } else if ('error' in responseData) {
            // Handle validation errors
            if (typeof responseData.error === 'object') {
              errorMessage = Object.entries(responseData.error)
                .map(([field, msg]) => `${field}: ${msg}`)
                .join('\n');
            } else {
              errorMessage = String(responseData.error);
            }
          } else if ('detail' in responseData) {
            // Handle FastAPI validation errors (array format)
            if (Array.isArray(responseData.detail)) {
              errorMessage = responseData.detail
                .map((err: any) => `${err.loc?.join('.')} : ${err.msg}`)
                .join('\n');
            } else {
              errorMessage = String(responseData.detail);
            }
          }
        }
        

        setError(errorMessage);
        return;
      }
      
      message.success('Successfully exported to DDX');
      onClose();
      
      // Call the success callback to update DDx status
      if (onSuccess) {
        onSuccess();
      }

      // After successful DDX export, store the DDX override Use Type Area value in the uploads table
      const useTypeArea = editedValues['Use Type Area'];
      if (useTypeArea) {
        try {
          const updateProps: ProjectUpdate = {
            project_id: projectId, // Already a string
            ddx_override_use_type_total_area_sf: String(useTypeArea),
            user_id: user.id
          };
          
          void await submitUpload({ updateProps });
          

        } catch (error) {
          console.error('Error updating DDX override Use Type Area in database:', error);
        }
      }
      
      // After successful DDX export, update the Use Type in the database
      if (selectedUseTypeId && selectedUseTypeId !== originalUseTypeId) {
        try {
          const updateProps: ProjectUpdate = {
            project_id: projectId, // Already a string
            project_use_type_id: String(selectedUseTypeId), // Convert to string
            user_id: user.id
          };
          
          void await submitUpload({ updateProps });
          

        } catch (error) {
          console.error('Error updating Use Type in database:', error);
        }
      }
      
      // After successful DDX export, update the Energy Code in the database
      if (selectedEnergyCodeId && selectedEnergyCodeId !== originalEnergyCodeId) {
        try {
          const updateProps: ProjectUpdate = {
            project_id: projectId, // Already a string
            energy_code_id: String(selectedEnergyCodeId), // Convert to string
            user_id: user.id
          };
          
          void await submitUpload({ updateProps });

        } catch (error) {
          console.error('Error updating Energy Code in database:', error);
        }
      }
      
      // Reload data after all updates
      reloadData();
    } catch (error) {
      console.error('Error exporting to DDX:', error);
      console.error('Error details:', JSON.stringify(error, null, 2));
      
      // Try to extract more details from the error
      if (error instanceof Error) {

        setError(`Failed to export to DDX: ${error.message}`);
      } else {
        setError('Failed to export to DDX. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleValidationComplete = (canSubmit: boolean, result?: any) => {
    setCanSubmitToDDX(canSubmit);
    setValidationResult(result);
    setShowPreValidation(false);
    setHasEditedValues(false); // Reset the edited flag after validation
  };

  const handleValidationClose = () => {
    setShowPreValidation(false);
  };

  // Helper function to get validation issues for a specific field
  // Map display field names to API field names
  const fieldNameMapping: { [key: string]: string } = {
    'Project ID': 'projectId',
    'projectId': 'projectId',
    'Project Name': 'projectName', 
    'Project Phase': 'phase',
    'Reporting Year': 'reportingYear',
    'Occupancy Year': 'estimatedOccupancyYear',
    'Country': 'country',
    'State': 'state',
    'Zip Code': 'zipcode',
    'City': 'city',
    'Use Type': 'useType1',
    'Use Type Area': 'useType1Area',
    'Design Energy Code': 'designEnergyCode',
    'Baseline EUI': 'baselineEUI',
    'Predicted EUI': 'predictedEUI',
    'Energy Modeling Tool': 'energyModelingTool',
    'Climate Zone': 'climateZone'
  };

  const getFieldValidationIssues = (fieldName: string) => {
    if (!validationResult?.issues) {
      return [];
    }
    
    // Map display name to API field name
    const apiFieldName = fieldNameMapping[fieldName] || fieldName;
    
    const allIssues = [...(validationResult.issues.warnings || []), ...(validationResult.issues.errors || [])];
    const fieldIssues = allIssues.filter(issue => issue.field === apiFieldName);
    
    return fieldIssues;
  };

  // Helper function to render validation messages for a field
  const renderFieldValidation = (fieldName: string) => {
    const issues = getFieldValidationIssues(fieldName);
    if (issues.length === 0) return null;

    return (
      <Box>
        {issues.map((issue, index) => {
          // Use dark blue for warnings, red for errors
          const color = issue.severity === 'error' ? '#d32f2f' : '#1565c0';
          const isError = issue.severity === 'error';

          return (
            <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', mb: 0.5 }}>
              <WarningIcon sx={{ 
                fontSize: 16, 
                color: isError ? '#d32f2f' : '#f57c00',
                mr: 0.5,
                mt: 0.1
              }} />
              <Typography
                variant="body2"
                sx={{
                  color: color,
                  fontSize: '0.875rem',
                  lineHeight: 1.4
                }}
              >
                {issue.message}
              </Typography>
            </Box>
          );
        })}
      </Box>
    );
  };

  return (
    <>
      <DDXPreValidationModal
        open={showPreValidation}
        onClose={handleValidationClose}
        projectId={projectId}
        editedValues={{
          ...editedValues,
          'Project ID': customProjectId
        }}
        onValidationComplete={handleValidationComplete}
      />
      
      <Modal open={open} onClose={onClose}>
      <Box sx={modalStyle}>
        <Typography variant="h6" component="h2" gutterBottom>
          {!ddxPreviewData ? 'Loading...' : 
           (typeof ddxPreviewData === 'string' || (typeof ddxPreviewData === 'object' && 'error' in ddxPreviewData)) ? 
           'Error Loading DDX Data' : 
           'Please review the project inputs displayed. Return to project details screen to edit any fields that need to be updated.'}
        </Typography>

        {!ddxPreviewData ? (
          <Typography>Loading DDX data...</Typography>
        ) : typeof ddxPreviewData === 'string' ? (
          <Typography color="error" sx={{ mt: 2, mb: 2 }}>
            {ddxPreviewData}
          </Typography>
        ) : 'error' in ddxPreviewData ? (
          <Typography color="error" sx={{ mt: 2, mb: 2 }}>
            {typeof ddxPreviewData.error === 'string' ? ddxPreviewData.error : JSON.stringify(ddxPreviewData.error)}
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {/* Project Data Section */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 1, mb: 2, fontWeight: 'bold', color: 'primary.main' }}>
                Project Data
              </Typography>
            </Grid>

            {/* Project ID - moved into Project Data section */}
            <Grid item xs={4}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography sx={{ fontWeight: 'bold' }}>
                  Project ID:
                </Typography>
                <Tooltip title="To associate this project with a project using the DDX API integration, this Project ID must match your DDX Project ID" placement="right">
                  <InfoOutlinedIcon sx={{ fontSize: 18, color: 'action.active', cursor: 'help', ml: 1, verticalAlign: 'text-bottom' }} />
                </Tooltip>
              </Box>
            </Grid>
            <Grid item xs={3}>
              {renderFieldValidation('projectId')}
            </Grid>
            <Grid item xs={4}>
              {editingFields['Project ID'] ? (
                <TextField
                  fullWidth
                  size="small"
                  value={customProjectId}
                  onChange={(e) => {
                    setCustomProjectId(e.target.value);
                    setHasEditedValues(true);
                  }}
                  onBlur={() => toggleEditing('Project ID')}
                  autoFocus
                  sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'white' } }}
                />
              ) : (
                <Typography>
                  {customProjectId}
                </Typography>
              )}
            </Grid>
            <Grid item xs={1}>
              <IconButton 
                size="small" 
                onClick={() => toggleEditing('Project ID')}
                sx={{ ml: -1 }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Grid>



            {/* Rest of the fields */}
            {Object.entries(ddxPreviewData).map(([key, data]) => {
              // Skip Project ID (handled above), location fields (handled above), _original_ fields, and fuel subtotals (handled below)
              if (key === 'Project ID' || 
                  ['City', 'State', 'Country', 'Zip Code', 'Climate Zone'].includes(key) || 
                  key.startsWith('_original_') || 
                  isFuelSubtotal(key)) {
                return null;
              }

              // Check if this field has a corresponding original value
              const originalKey = `_original_${key}`;
              const originalValue = ddxPreviewData[originalKey];
              const currentValue = typeof data === 'object' && 'value' in data ? data.value : data;
              const hasMapping = originalValue && 
                                typeof originalValue === 'object' && 
                                'value' in originalValue &&
                                originalValue.value !== currentValue;

              return (
                <React.Fragment key={key}>
                  <Grid item xs={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography sx={{ fontWeight: 'bold' }}>
                        {key}:
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={3}>
                    {renderFieldValidation(key)}
                  </Grid>
                  <Grid item xs={hasMapping ? 3 : 4}>
                    {isFieldEditable(key, data) && editingFields[key] ? (
                      key === 'Use Type' ? (
                        <Box sx={{ 
                          '& .MuiFormControl-root': { 
                            m: 0, 
                            minWidth: 'auto', 
                            width: '100%' 
                          },
                          '& .MuiInputLabel-root': {
                            display: 'none' // Hide the label completely
                          },
                          '& .MuiSelect-select': {
                            py: 1, // Match TextField padding
                            fontSize: '0.875rem' // Match TextField font size
                          }
                        }}>
                          <EnumList
                            params={{
                              enum_name: "project_use_types",
                              label: "",
                              required: false,
                              populateValue: (() => {
                                // Only use valid, non-NaN numbers
                                const validSelectedId = selectedUseTypeId !== null && !isNaN(selectedUseTypeId) && selectedUseTypeId > 0 ? selectedUseTypeId : null;
                                const validOriginalId = originalUseTypeId !== null && !isNaN(originalUseTypeId) && originalUseTypeId > 0 ? originalUseTypeId : null;
                                const value = validSelectedId || validOriginalId || undefined;
                                return value;
                              })(),
                            }}
                            onChange={(value: string) => {
                              const numValue = Number(value);
                              setSelectedUseTypeId(numValue);
                              setEditedValues(prev => ({
                                ...prev,
                                [key]: String(value) // Explicitly convert to string for DDX export
                              }));
                              setHasEditedValues(true);
                            }}
                          />
                        </Box>
                      ) : (key === 'Energy Code' || key === 'Design Energy Code') ? (
                        <Box sx={{ 
                          '& .MuiFormControl-root': { 
                            m: 0, 
                            minWidth: 'auto', 
                            width: '100%' 
                          },
                          '& .MuiInputLabel-root': {
                            display: 'none' // Hide the label completely
                          },
                          '& .MuiSelect-select': {
                            py: 1, // Match TextField padding
                            fontSize: '0.875rem' // Match TextField font size
                          }
                        }}>
                          <EnumList
                            params={{
                              enum_name: "energy_codes",
                              label: "",
                              required: false,
                              populateValue: (() => {
                                // Only use valid, non-NaN numbers
                                const validSelectedId = selectedEnergyCodeId !== null && !isNaN(selectedEnergyCodeId) && selectedEnergyCodeId > 0 ? selectedEnergyCodeId : null;
                                const validOriginalId = originalEnergyCodeId !== null && !isNaN(originalEnergyCodeId) && originalEnergyCodeId > 0 ? originalEnergyCodeId : null;
                                const value = validSelectedId || validOriginalId || undefined;
                                return value;
                              })(),
                            }}
                            onChange={(value: string) => {
                              const numValue = Number(value);
                              setSelectedEnergyCodeId(numValue);
                              setEditedValues(prev => ({
                                ...prev,
                                [key]: String(value) // Explicitly convert to string for DDX export
                              }));
                              setHasEditedValues(true);
                            }}
                          />
                        </Box>
                      ) : (
                        <TextField
                          fullWidth
                          size="small"
                          type={(key === 'Energy Code' || key === 'Design Energy Code' || key === 'Reporting Year' || key === 'Occupancy Year') ? 'text' : 'number'}
                          value={editedValues[key] ?? String(data.value).replace(/,/g, '').replace('kBtu/SF', '').replace('ft2', '').trim()}
                          onChange={(e) => handleValueChange(key, e.target.value)}
                          onBlur={() => toggleEditing(key)}
                          autoFocus
                          sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'white' } }}
                        />
                      )
                    ) : (
                      <Typography>
                          {formatValue(key, editedValues[key] ?? (typeof data === 'object' && 'value' in data ? String(data.value) : String(data)))}
                      </Typography>
                    )}
                  </Grid>
                  {hasMapping && (
                    <Grid item xs={1}>
                      <Tooltip 
                        title={`Original: ${originalValue.value} → Mapped: ${typeof data === 'object' && 'value' in data ? data.value : data}`} 
                        placement="right"
                      >
                        <InfoOutlinedIcon sx={{ fontSize: 18, color: 'info.main', cursor: 'help', verticalAlign: 'text-bottom' }} />
                      </Tooltip>
                    </Grid>
                  )}
                  {isFieldEditable(key, data) && (
                    <Grid item xs={1}>
                      <IconButton 
                        size="small" 
                        onClick={() => toggleEditing(key)}
                        sx={{ ml: -1 }}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Grid>
                  )}
                </React.Fragment>
              );
            })}
          </Grid>
        )}

        {/* Location Section */}
        {ddxPreviewData && !('error' in ddxPreviewData) && (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold', color: 'primary.main' }}>
                Location
              </Typography>
            </Grid>

            {/* Location fields - render City, State, Zip Code, Country, Climate Zone in this section */}
            {(() => {
              // Check if any location field is being edited
              const isAnyLocationFieldEditing = ['City', 'State', 'Zip Code'].some(field => editingFields[field]);
              
              return (
                <>
                  {['City', 'State', 'Zip Code', 'Country', 'Climate Zone'].map((locationField) => {
                    const data = ddxPreviewData[locationField];
                    
                    if (!data) return null;

                    // Check if this field has a corresponding original value
                    const originalKey = `_original_${locationField}`;
                    const originalValue = ddxPreviewData[originalKey];
                    const currentValue = typeof data === 'object' && 'value' in data ? data.value : data;
                    const hasMapping = originalValue && 
                                      typeof originalValue === 'object' && 
                                      'value' in originalValue &&
                                      originalValue.value !== currentValue;

                    // Climate zone and country should not be editable
                    const isLocationFieldEditable = locationField !== 'Climate Zone' && locationField !== 'Country';

                    return (
                      <React.Fragment key={locationField}>
                        <Grid item xs={4}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography sx={{ fontWeight: 'bold' }}>
                              {locationField}:
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={3}>
                          {renderFieldValidation(locationField)}
                        </Grid>
                        <Grid item xs={hasMapping ? 3 : 4}>
                          {isLocationFieldEditable && editingFields[locationField] ? (
                            locationField === 'State' ? (
                              <FormControl fullWidth size="small">
                                <Select
                                  value={editedValues[locationField] ?? String(currentValue)}
                                  onChange={(e) => handleValueChange(locationField, String(e.target.value))}
                                  sx={{ 
                                    '& .MuiOutlinedInput-root': { bgcolor: 'white' },
                                    '& .MuiSelect-select': { py: 1 }
                                  }}
                                >
                                  <MenuItem value="Alabama">Alabama</MenuItem>
                                  <MenuItem value="Alaska">Alaska</MenuItem>
                                  <MenuItem value="Arizona">Arizona</MenuItem>
                                  <MenuItem value="Arkansas">Arkansas</MenuItem>
                                  <MenuItem value="California">California</MenuItem>
                                  <MenuItem value="Colorado">Colorado</MenuItem>
                                  <MenuItem value="Connecticut">Connecticut</MenuItem>
                                  <MenuItem value="Delaware">Delaware</MenuItem>
                                  <MenuItem value="District of Columbia">District of Columbia</MenuItem>
                                  <MenuItem value="Florida">Florida</MenuItem>
                                  <MenuItem value="Georgia">Georgia</MenuItem>
                                  <MenuItem value="Hawaii">Hawaii</MenuItem>
                                  <MenuItem value="Idaho">Idaho</MenuItem>
                                  <MenuItem value="Illinois">Illinois</MenuItem>
                                  <MenuItem value="Indiana">Indiana</MenuItem>
                                  <MenuItem value="Iowa">Iowa</MenuItem>
                                  <MenuItem value="Kansas">Kansas</MenuItem>
                                  <MenuItem value="Kentucky">Kentucky</MenuItem>
                                  <MenuItem value="Louisiana">Louisiana</MenuItem>
                                  <MenuItem value="Maine">Maine</MenuItem>
                                  <MenuItem value="Maryland">Maryland</MenuItem>
                                  <MenuItem value="Massachusetts">Massachusetts</MenuItem>
                                  <MenuItem value="Michigan">Michigan</MenuItem>
                                  <MenuItem value="Minnesota">Minnesota</MenuItem>
                                  <MenuItem value="Mississippi">Mississippi</MenuItem>
                                  <MenuItem value="Missouri">Missouri</MenuItem>
                                  <MenuItem value="Montana">Montana</MenuItem>
                                  <MenuItem value="Nebraska">Nebraska</MenuItem>
                                  <MenuItem value="Nevada">Nevada</MenuItem>
                                  <MenuItem value="New Hampshire">New Hampshire</MenuItem>
                                  <MenuItem value="New Jersey">New Jersey</MenuItem>
                                  <MenuItem value="New Mexico">New Mexico</MenuItem>
                                  <MenuItem value="New York">New York</MenuItem>
                                  <MenuItem value="North Carolina">North Carolina</MenuItem>
                                  <MenuItem value="North Dakota">North Dakota</MenuItem>
                                  <MenuItem value="Ohio">Ohio</MenuItem>
                                  <MenuItem value="Oklahoma">Oklahoma</MenuItem>
                                  <MenuItem value="Oregon">Oregon</MenuItem>
                                  <MenuItem value="Pennsylvania">Pennsylvania</MenuItem>
                                  <MenuItem value="Rhode Island">Rhode Island</MenuItem>
                                  <MenuItem value="South Carolina">South Carolina</MenuItem>
                                  <MenuItem value="South Dakota">South Dakota</MenuItem>
                                  <MenuItem value="Tennessee">Tennessee</MenuItem>
                                  <MenuItem value="Texas">Texas</MenuItem>
                                  <MenuItem value="Utah">Utah</MenuItem>
                                  <MenuItem value="Vermont">Vermont</MenuItem>
                                  <MenuItem value="Virginia">Virginia</MenuItem>
                                  <MenuItem value="Washington">Washington</MenuItem>
                                  <MenuItem value="West Virginia">West Virginia</MenuItem>
                                  <MenuItem value="Wisconsin">Wisconsin</MenuItem>
                                  <MenuItem value="Wyoming">Wyoming</MenuItem>
                                </Select>
                              </FormControl>
                            ) : (
                              <TextField
                                fullWidth
                                size="small"
                                value={editedValues[locationField] ?? String(currentValue)}
                                onChange={(e) => handleValueChange(locationField, e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    toggleEditing(locationField);
                                  }
                                }}
                                sx={{ '& .MuiOutlinedInput-root': { bgcolor: 'white' } }}
                              />
                            )
                          ) : (
                            <Typography>
                              {editedValues[locationField] ?? String(currentValue)}
                            </Typography>
                          )}
                        </Grid>
                        {hasMapping && (
                          <Grid item xs={1}>
                            <Tooltip 
                              title={`Original: ${originalValue.value} → Mapped: ${currentValue}`} 
                              placement="right"
                            >
                              <InfoOutlinedIcon sx={{ fontSize: 18, color: 'info.main', cursor: 'help', verticalAlign: 'text-bottom' }} />
                            </Tooltip>
                          </Grid>
                        )}
                        {/* Only show edit icon if not in editing mode and field is editable */}
                        {isLocationFieldEditable && !isAnyLocationFieldEditing && (
                          <Grid item xs={1}>
                            <IconButton 
                              size="small" 
                              onClick={() => toggleEditing(locationField)}
                              sx={{ ml: -1 }}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Grid>
                        )}
                        
                        {/* Save Location button - show right after Zip Code when editing */}
                        {locationField === 'Zip Code' && isAnyLocationFieldEditing && (
                          <Grid item xs={12}>
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                              <Button
                                variant="contained"
                                size="small"
                                onClick={async () => {
               
                                  
                                  // Save location fields and exit edit mode
                                  await handleLocationUpdate();
                                  
                                  // Turn off editing for all location fields
                                  setEditingFields(prev => ({
                                    ...prev,
                                    'City': false,
                                    'State': false,
                                    'Zip Code': false
                                  }));
                                }}
                              >
                                Save Location
                              </Button>
                            </Box>
                          </Grid>
                        )}
                      </React.Fragment>
                    );
                  })}
                </>
              );
            })()}
          </Grid>
        )}

        {/* Fuel Subtotals Table Section */}
        {ddxPreviewData && !('error' in ddxPreviewData) && (
          <Box sx={{ mt: 4 }}>
            {(() => {
              // Prepare fuel subtotals data
              const fuelSubtotalsData = Object.entries(ddxPreviewData)
                .filter(([key]) => isFuelSubtotal(key))
                .map(([key, data]) => {
                  const cleanFieldName = key.replace(' (MBtu)', '');
                  const numericValue = typeof data === 'object' && 'value' in data ? Number(data.value) : 0;
                  let displayValue = numericValue;
                  let unit = 'MBtu';
                  let tooltip;

                  // Use original MBtu values for electricity and gas
                  if (cleanFieldName === 'Electricity Produced Off-Site' && ddxPreviewData['_original_electricityProducedOffSite_mbtu']) {
                    displayValue = numericValue; // Already in kWh
                    unit = 'kWh';
                    tooltip = `Value in Original Units: ${Number(ddxPreviewData['_original_electricityProducedOffSite_mbtu'].value).toFixed(1)} MBtu`;
                  } else if (cleanFieldName === 'Natural Gas Combusted On-Site' && ddxPreviewData['_original_naturalGasCombustedOnSite_mbtu']) {
                    displayValue = numericValue; // Already in therms
                    unit = 'Therms';
                    tooltip = `Value in Original Units: ${Number(ddxPreviewData['_original_naturalGasCombustedOnSite_mbtu'].value).toFixed(1)} MBtu`;
                  }
                  //if district steam, district hot water, or district chilled water, convert to kBtu
                  if (cleanFieldName === 'District Steam' || cleanFieldName === 'District Hot Water' || cleanFieldName === 'District Chilled Water') {
                    displayValue = numericValue
                    unit = 'kBtu';
                    
                  }

                  return {
                    fuelSource: cleanFieldName,
                    value: displayValue,
                    formattedValue: new Intl.NumberFormat('en-US', {
                      minimumFractionDigits: 1,
                      maximumFractionDigits: 1
                    }).format(displayValue) + ` ${unit}`,
                    tooltip
                  };
                });

              // Define columns
              const fuelSubtotalsColumns = [
                {
                  header: 'Fuel Source',
                  accessorKey: 'fuelSource',
                  cell: (info: any) => {
                    const row = info.row.original;
                    const showTooltip = ['Electricity Produced Off-Site', 'Natural Gas Combusted On-Site'].includes(row.fuelSource);
                    return (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography 
                          variant="body2" 
                          sx={{ fontWeight: 'medium' }}
                        >
                          {info.getValue()}
                        </Typography>
                        {showTooltip && row.tooltip && (
                          <Tooltip 
                            title={row.tooltip} 
                            placement="right"
                            arrow
                          >
                            <InfoOutlinedIcon 
                              sx={{ 
                                fontSize: 18, 
                                color: 'info.main',
                                cursor: 'help',
                                ml: 1
                              }} 
                            />
                          </Tooltip>
                        )}
                      </Box>
                    );
                  }
                },
                {
                  header: 'Value',
                  accessorKey: 'formattedValue',
                  meta: {
                    className: 'cell-center',
                  },
                  cell: (info: any) => {
                    return (
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontWeight: 'medium',
                          textAlign: 'right'
                        }}
                      >
                        {info.getValue()}
                      </Typography>
                    );
                  }
                }
              ];

              return (
                <>
                  <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold', color: 'primary.main' }}>
                    Fuel Source Subtotals
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary', fontStyle: 'italic' }}>
                    Energy values can be edited from the project details screen by closing this modal.
                  </Typography>
                  <ReactTable
                    id="fuel-subtotals-table"
                    columns={fuelSubtotalsColumns}
                    data={fuelSubtotalsData}
                    pagination="none"
                    title=""
                    rowsPerPage={50}
                    showRowcount={false}
                    allowCellEdit={false}
                  />
                </>
              );
            })()}
          </Box>
        )}

        {error && (
          <Typography 
            color="error.main" 
            sx={{ 
              mt: 3,
              p: 3,
              bgcolor: 'error.contrastText',
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'error.main'
            }}
          >
            {error}
          </Typography>
        )}

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button onClick={onClose} variant="outlined">
            Cancel
          </Button>
          {validationResult ? (
            <>
              <Button 
                onClick={() => setShowPreValidation(true)} 
                variant="outlined"
                disabled={isSubmitting}
              >
                Run Validation Again
              </Button>
              <Button 
                onClick={handleSubmit} 
                variant="contained" 
                disabled={isSubmitting || !canSubmitToDDX || !ddxPreviewData || ('error' in ddxPreviewData) || !isAuthenticated || hasEditedValues}
                sx={{
                  backgroundColor: (canSubmitToDDX && !hasEditedValues) ? 'primary.main' : 'grey.400'
                }}
              >
                {isSubmitting ? 'Submitting...' : 
                 hasEditedValues ? 'Re-run Validation Required' :
                 canSubmitToDDX ? 'Submit to DDX' : 'Cannot Submit - Fix Errors'}
              </Button>
            </>
          ) : (
            <Button 
              onClick={() => setShowPreValidation(true)} 
              variant="contained" 
              disabled={isSubmitting || !ddxPreviewData || ('error' in ddxPreviewData) || !isAuthenticated}
            >
              {isSubmitting ? 'Submitting...' : 'Validate & Submit to DDX'}
            </Button>
          )}
        </Box>
      </Box>
    </Modal>
    </>
  );
};

export default ShareToDDXModal; 