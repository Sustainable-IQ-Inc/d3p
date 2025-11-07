"use client";

import React, { useRef, useState, useEffect } from "react";
import { Grid, Typography, IconButton, CardContent, Button, TextField, InputAdornment, Tooltip } from "@mui/material";
import MainCard from "components/MainCard";
import EditIcon from "@mui/icons-material/Edit";
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { Field, Formik, Form } from "formik";
import EnumList from "components/enums/enum_list";
import DownloadFile from "./DownloadFile";
import YearField from "./YearField";
import ReportingYearField from "./ReportingYearField";
import submitUpload from "app/api/UpdateProjectDetails"; // Import the function
import submitUploadUpload from "app/api/UpdateUpload"; // Import the upload update function
import useUser from "hooks/useUser";
import { useDataReload } from "contexts/ProjectDataReload";
import { ProjectUpdate, UploadUpdate } from "types/updates";
import validateZip from "app/api/ValidateZip";
import { message } from "antd";
interface DetailsCardProps {
  editableData: any;
  isEditing: boolean;
  detailPageView?: boolean;
  handleEditClick: () => void;
  handleFieldChange: (field: string, value: string) => void;
  handleEnumChange: (field: string, value: number) => void;
  handleClose: () => void;
}



const DetailsCard: React.FC<DetailsCardProps> = ({
  editableData,
  isEditing,
  detailPageView,
  handleEditClick,
  handleFieldChange,
  handleEnumChange,
  handleClose,
}) => {

    const { user } = useUser();
    const { reloadData } = useDataReload();


    // Store initial form values - use state so Formik can react to changes
    const [initialFormValues, setInitialFormValues] = useState({
      project_id: editableData.project_id,
      energy_code_id: editableData.energy_code_id,
      project_construction_category_id: editableData.project_construction_category_id,
      project_phase_id: editableData.project_phase_id,
      year: editableData.year,
      reporting_year: editableData.reporting_year || editableData.year,
      user_id: editableData.user_id,
      project_use_type_id: editableData.project_use_type_id,
      custom_project_id: editableData.custom_project_id || editableData.project_id,
      use_type_total_area: editableData.use_type_total_area
    });

    // Also keep a ref for comparison in onSubmit (refs don't change during form editing)
    // This ref will be updated when editing starts to capture the baseline
    const initialFormValuesRef = useRef(initialFormValues);
    
    // Keep ref in sync with state when state changes (but only when editing starts, via useEffect)

    // Track previous isEditing state to detect when editing starts
    const prevIsEditingRef = useRef(isEditing);

    // Update the initial values ONLY when editing starts (transitions from false to true)
    // This ensures we capture the baseline values before any edits, not after data reloads
    useEffect(() => {
      const wasEditing = prevIsEditingRef.current;
      const isNowEditing = isEditing;
      
      // Only update when transitioning from not editing to editing
      if (!wasEditing && isNowEditing) {
        const newInitialValues = {
          project_id: editableData.project_id,
          energy_code_id: editableData.energy_code_id,
          project_construction_category_id: editableData.project_construction_category_id,
          project_phase_id: editableData.project_phase_id,
          year: editableData.year,
          reporting_year: editableData.reporting_year || editableData.year,
          user_id: editableData.user_id,
          project_use_type_id: editableData.project_use_type_id,
          custom_project_id: editableData.custom_project_id || editableData.project_id,
          use_type_total_area: editableData.use_type_total_area
        };
        setInitialFormValues(newInitialValues);
        initialFormValuesRef.current = newInitialValues;
        console.log("Captured initial form values for comparison:", newInitialValues);
      }
      
      prevIsEditingRef.current = isEditing;
    }, [isEditing, editableData]);

    const [zipCode, setZipCode] = useState<string>("");
    const [isZipValid, setIsZipValid] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const handleZipCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setZipCode(value);
      setIsZipValid(/^\d{5}$/.test(value)); // Check if the value is a 5-digit number
    };
    
    

    const handleZipCodeSubmit = async (zip_code: string, project_id: string) => { // Add parameters
      setLoading(true);
      setError(null);
      try {
        const response = await validateZip({zip_code: zip_code, project_id: project_id}); // Use the passed parameters
        if (response.data.status === "success") {
          //clear out the zip code field
          
          setZipCode("");
          reloadData();
          // add a toast notification
          message.success("Climate zone updated successfully");
        } else {
          setError("Failed to fetch climate zone. Please try again.");
        }
      } catch (error) {
        setError("Failed to fetch climate zone. Please try again.");
      } finally {
        setLoading(false);
      }
    };



    return (
      <Formik
      initialValues={initialFormValues}
      enableReinitialize={true}
      onSubmit={async (values, { resetForm }) => { // Removed initialFormValues from destructuring
        console.log("=== FORM SUBMISSION DEBUG ===");
        console.log("Current form values:", values);
        console.log("Initial values ref:", initialFormValuesRef.current);
        console.log("Initial values state:", initialFormValues);
        
        // Compare current values with initial values to find changed fields
        const updatedData = Object.keys(values).reduce((acc: Record<string, any>, key) => {
          const newValue = values[key as keyof typeof values];
          const oldValue = initialFormValuesRef.current[key as keyof typeof initialFormValuesRef.current];
          
          console.log(`Comparing ${key}:`, { 
            newValue, 
            oldValue, 
            newType: typeof newValue,
            oldType: typeof oldValue,
            equal: newValue === oldValue,
            looseEqual: newValue == oldValue
          });

          // Compare values, handling type coercion for numbers/strings
          // Convert both to strings for comparison to handle number/string mismatches
          const newValueStr = newValue != null ? String(newValue) : null;
          const oldValueStr = oldValue != null ? String(oldValue) : null;
          
          if (newValueStr !== oldValueStr) {
            console.log(`  -> Field ${key} changed: "${oldValueStr}" -> "${newValueStr}"`);
            acc[key] = newValue;
          }
          return acc;
        }, {});

        // Always include project_id and user_id
        updatedData.project_id = values.project_id;
        updatedData.user_id = user.id;

        console.log("Final updatedData:", updatedData);

        try {
          // Handle GSF updates through the upload update API
          if ('use_type_total_area' in updatedData) {
            // Use the upload update API for GSF changes
            const uploadUpdateData = {
              project_id: editableData.project_id,
              use_type_total_area: updatedData.use_type_total_area,
              user_id: user.id
            };
            
                         const uploadResult = await submitUploadUpload({ updateProps: uploadUpdateData as UploadUpdate });
            if (uploadResult !== "success") {
              message.error("Failed to update GSF");
              return;
            }
            
            delete updatedData.use_type_total_area; // Remove from project update
          }
          
          // Update other project fields if there are any
          if (Object.keys(updatedData).length > 0) {
            const result = await submitUpload({ updateProps: updatedData as ProjectUpdate });
            if (result === "success") {
              message.success("Project updated successfully");
            } else if (result === "custom_project_id_not_unique") {
              message.error("This Project ID already exists in your company. Please choose a unique Project ID.");
              return;
            } else {
              message.error("Failed to update project");
              return;
            }
          } else if ('use_type_total_area' in values) {
            message.success("GSF updated successfully");
          }
          
          reloadData();
          handleClose(); // Close modal on success
        } catch (error) {
          console.error("Error submitting form:", error);
          message.error("Failed to update project");
        }
      }}
    >
      {({ values, handleChange, handleSubmit, setFieldValue }) => (
        <Form>
          {loading && <div>Loading...</div>}
          <MainCard
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                <Typography variant="h6">Details</Typography>
                {detailPageView && (
                  <IconButton onClick={handleEditClick}>
                    <EditIcon />
                  </IconButton>
                )}
              </div>
            }
          >
            <CardContent>
              <Grid container spacing={1}>
                <Grid item xs={12}>
                  <table style={{ width: '100%' }}>
                    <tbody>
                      <tr>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Typography variant="h6">Project ID</Typography>
                          <Tooltip title="To associate this project with a project using the DDX API integration, this Project ID must match your DDX Project ID" placement="right">
                            <InfoOutlinedIcon sx={{ fontSize: 18, color: 'action.active', cursor: 'help' }} />
                          </Tooltip>
                        </div>
                      </td>
                      <td style={{ textAlign: "right" }}>
                        {isEditing ? (
                          <Field
                            name="custom_project_id"
                            type="text"
                            value={values.custom_project_id || values.project_id}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                              // Only update Formik - don't update editableData during editing
                              setFieldValue("custom_project_id", e.target.value);
                            }}
                            style={{
                              textAlign: "right",
                              padding: "8px",
                              border: "1px solid #ccc",
                              borderRadius: "4px",
                              width: "100%"
                            }}
                          />
                        ) : (
                          <Typography variant="body1" align="right" fontWeight={"bold"}>
                            {editableData.custom_project_id || editableData.project_id}
                          </Typography>
                        )}
                      </td>
                    </tr>
                      {detailPageView && (
                        <>
                                                
                      <tr>
                            <td><Typography variant="h6">Use Type</Typography></td>
                            <td style={{ textAlign: "right" }}>
                              {isEditing ? (
                                <Field
                                  component={EnumList}
                                  name="project_use_type_id"
                                  params={{
                                    enum_name: "project_use_types",
                                    label: "Use Type",
                                    required: true,
                                    populateValue: values.project_use_type_id || undefined,
                                  }}
                                  onChange={(value: number) => {
                                    // Only update Formik - don't update editableData during editing
                                    setFieldValue("project_use_type_id", value);
                                  }}
                                />
                              ) : (
                                <Typography variant="body1" align="right" fontWeight={"bold"}>
                                  {editableData.project_use_type ? editableData.project_use_type : "--"}
                                </Typography>
                              )}
                            </td>
                          </tr>
                          <tr>
                            <td><Typography variant="h6">City</Typography></td>
                            <td style={{ textAlign: "right" }}>
                              <Typography variant="body1" align="right" fontWeight={"bold"}>
                                {editableData.city ? editableData.city : "--"}
                              </Typography>
                            </td>
                          </tr>
                          <tr>
                            <td><Typography variant="h6">State</Typography></td>
                            <td style={{ textAlign: "right" }}>
                              <Typography variant="body1" align="right" fontWeight={"bold"}>
                                {editableData.state ? editableData.state : "--"}
                              </Typography>
                            </td>
                          </tr>
                          <tr>
                            <td><Typography variant="h6">Zip Code</Typography></td>
                            <td style={{ textAlign: "right" }}>
                              <Typography variant="body1" align="right" fontWeight={"bold"}>
                                {editableData.zip_code ? editableData.zip_code : "--"}
                              </Typography>
                            </td>
                          </tr>
                          <tr>
                            <td><Typography variant="h6">Climate Zone</Typography></td>
                            <td style={{ textAlign: "right" }}>
                              {isEditing ? (
                                <>
                                  <TextField
                                    variant="outlined"
                                    value={zipCode}
                                    onChange={handleZipCodeChange}
                                    placeholder="Enter Zip Code"
                                    style={{ marginRight: '8px', width: '250px' }}
                                    InputProps={{
                                      endAdornment: (
                                        <InputAdornment position="end">
                                        <Button
                                          variant="contained"
                                          color="primary"
                                          onClick={() => handleZipCodeSubmit(zipCode, editableData.project_id)} // Pass zipCode and project_id
                                          disabled={!isZipValid}
                                          size="small" // Added size property to make the button smaller
                                        >
                                          Validate
                                        </Button>
                                      </InputAdornment>
                                      ),
                                    }}
                                  />

                                  {error && <Typography color="error">{error}</Typography>}
                                  <Typography variant="body1" align="right" fontWeight={"bold"}>
                                    {editableData.climate_zone ? editableData.climate_zone : "--"}
                                  </Typography>
                                </>
                              ) : (
                                <Typography variant="body1" align="right" fontWeight={"bold"}>
                                  {editableData.climate_zone ? editableData.climate_zone : "--"}
                                </Typography>
                              )}
                            </td>
                          </tr>
                        </>
                      )}
                      <tr>
                        <td><Typography variant="h6">Occupancy Year</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          {isEditing ? (
                            <Field
                              component={YearField}
                              type="number"
                              name="year"
                              params={{
                                label: "Occupancy Year",
                                required: true,
                              }}
                              onChange={(value: number) => {
                                // Only update Formik - don't update editableData during editing
                                setFieldValue("year", value);
                              }}
                            />
                          ) : (
                            <Typography variant="body1" align="right" fontWeight={"bold"}>
                              {editableData.year ? editableData.year : "--"}
                            </Typography>
                          )}
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Reporting Year</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          {isEditing ? (
                            <Field
                              component={ReportingYearField}
                              type="number"
                              name="reporting_year"
                              params={{
                                label: "Reporting Year",
                                required: true,
                              }}
                              onChange={(value: number) => {
                                // Only update Formik - don't update editableData during editing
                                setFieldValue("reporting_year", value);
                              }}
                            />
                          ) : (
                            <Typography variant="body1" align="right" fontWeight={"bold"}>
                              {editableData.reporting_year ? editableData.reporting_year : "--"}
                            </Typography>
                          )}
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Project Phase</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          {isEditing ? (
                            <Field
                              component={EnumList}
                              name="project_phase_id"
                              params={{
                                enum_name: "project_phases",
                                label: "Project Phase",
                                required: true,
                                populateValue: values.project_phase_id || undefined,
                              }}
                              onChange={(value: number) => {
                                // Only update Formik - don't update editableData during editing
                                setFieldValue("project_phase_id", value);
                              }}
                            />
                          ) : (
                            <Typography variant="body1" align="right" fontWeight={"bold"}>
                              {editableData.project_phase}
                            </Typography>
                          )}
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Construction Category</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          {isEditing ? (
                            <Field
                              component={EnumList}
                              name="project_construction_category_id"
                              params={{
                                enum_name: "project_construction_categories",
                                label: "Construction Category",
                                required: true,
                                populateValue: values.project_construction_category_id || undefined,
                              }}
                              onChange={(value: number) => {
                                // Only update Formik - don't update editableData during editing
                                setFieldValue("project_construction_category_id", value);
                              }}
                            />
                          ) : (
                            <Typography variant="body1" align="right" fontWeight={"bold"}>
                              {editableData.project_construction_category_name ? editableData.project_construction_category_name : "--"}
                            </Typography>
                          )}
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Energy Code</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          {isEditing ? (
                            <Field
                              component={EnumList}
                              name="energy_code_id"
                              params={{
                                enum_name: "energy_codes",
                                label: "Energy Code",
                                required: true,
                                populateValue: values.energy_code_id || undefined,
                              }}
                              onChange={(value: number) => {
                                // Only update Formik - don't update editableData during editing
                                setFieldValue("energy_code_id", value);
                              }}
                            />
                          ) : (
                            <Typography variant="body1" align="right" fontWeight={"bold"}>
                              {editableData.energy_code_name ? editableData.energy_code_name : "--"}
                            </Typography>
                          )}
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Report Type</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          <Typography variant="body1" align="right" fontWeight={"bold"}>
                            {editableData.report_type_name ? editableData.report_type_name : "--"}
                          </Typography>
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Gross Square Footage (GSF)</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          {isEditing ? (
                            <TextField
                              type="number"
                              value={values.use_type_total_area || ''}
                              onChange={(e) => {
                                const value = e.target.value;
                                // Only update Formik - don't update editableData during editing
                                setFieldValue("use_type_total_area", value);
                              }}
                              style={{
                                textAlign: "right",
                                width: "100%"
                              }}
                              InputProps={{
                                endAdornment: <InputAdornment position="end">SF</InputAdornment>,
                              }}
                            />
                          ) : (
                            <Typography variant="body1" align="right" fontWeight={"bold"}>
                              {editableData.use_type_total_area ? `${Number(editableData.use_type_total_area).toLocaleString()} SF` : "--"}
                            </Typography>
                          )}
                        </td>
                      </tr>
                      <tr>
                        <td><Typography variant="h6">Last Update</Typography></td>
                        <td style={{ textAlign: "right" }}>
                          <Typography variant="body1" align="right" fontWeight={"bold"}>
                            {editableData.most_recent_updated_at ? new Date(editableData.most_recent_updated_at).toLocaleDateString("en-US", {
                              year: "numeric",
                              month: "long",
                              day: "numeric",
                            }) : "--"}
                          </Typography>
                        </td>
                      </tr>

                      {editableData.total_energy_baseline && detailPageView && (
                        <tr>
                          <td colSpan={2} style={{ textAlign: "right" }}>
                            <DownloadFile projectId={editableData.project_id} baselineDesign={"baseline"} />
                          </td>
                        </tr>
                      )}
                      {editableData.total_energy_design && detailPageView && (
                        <tr>
                          <td colSpan={2} style={{ textAlign: "right" }}>
                            <DownloadFile projectId={editableData.project_id} baselineDesign={"design"} />
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </Grid>
              </Grid>
              {isEditing && (
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
                  <Button variant="contained" color="secondary" onClick={() => handleClose()} style={{ marginRight: '8px' }}>
                    Cancel
                  </Button>
                  <Button variant="contained" color="primary" onClick={() => handleSubmit()}>
                    Save
                  </Button>
                </div>
              )}
            </CardContent>
          </MainCard>
        </Form>
      )}
    </Formik>
  );
};

export default DetailsCard;
