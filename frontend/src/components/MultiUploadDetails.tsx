import React, { useState, useEffect } from "react";
import { Formik, Field, Form, FieldArray } from "formik";
import axios from "axios";
import { createClient } from "utils/supabase";
import ProjectCard from "./ProjectDetailCard";
import ProjectCardHorizontal from "./ProjectDetailCardHorizontal";
import { Button, Typography, IconButton, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid } from "@mui/material";
import Popover from "@mui/material/Popover";
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';

import ListProjects from "components/projects/ListProjects";
import { getProjectList } from "components/projects/project";
import useUser from "hooks/useUser";

import EnumList from "components/enums/enum_list";
import YearField from "components/YearField";
import ReportingYearField from "components/ReportingYearField";
import DeleteIcon from "@mui/icons-material/Delete";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import Tooltip from "@mui/material/Tooltip";
import { message } from "antd";
import Link from "next/link";

import submitUpload from "app/api/SubmitUpload";
import FileDropzone from "components/uploader/uploader";
import { SubmitUploadProps } from "types/file-submission";
import "./App.css";

import { ThemeProvider } from "@mui/material/styles";
import { theme } from "themes/FieldTheme";
import { UUID } from "crypto";

import StepperComponent from "./MultiUploadStepper";
interface MultiUploadDetailsProps {
  data?: any;
}
interface KeyMetricFields {
  use_type_total_area: number;
  total_energy: number;
  climate_zone: string;
  file_name: string;
  file_url?: string;
}
interface FileData extends KeyMetricFields {
  id: number;
  upload_id: number;
  visible?: boolean;
  baseline_file_data?: FileData;
  upload_attempted?: boolean;
}
export type PrepopulatedDataProps = {
  project_use_type_id: number;
  project_phase_id: number;
  project_construction_category_id: number;
  energy_code_id: number;
  year: number;
  reporting_year: number;
};

interface RecordData extends KeyMetricFields {
  id: number;
  project_use_type_id: number;
  project_phase_id: number;
  project_construction_category_id: number;
  has_subtypes: boolean;
  use_type_subtype_id?: number;
  energy_code_id: number;
  baseline_file_data?: FileData | null;
  project_id: UUID;
  year: number;
  reporting_year: number;
  upload_attempted?: boolean;
}

const MultiUploadDetails: React.FC<MultiUploadDetailsProps> = ({ data }) => {
  const { user } = useUser();
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(
    null
  );
  const [selectedRecordIndex, setSelectedRecordIndex] = useState<number | null>(
    null
  );

  const handleSubmitRow = (
    rowData: RecordData,
    index: number,
    remove: (index: number) => void,
    setFieldValue: Function
  ) => {
    // Submit the data
    console.log("Submitting row data:", rowData);
    console.log("Year value:", rowData.year);
    console.log("Reporting year value:", rowData.reporting_year);

    const submitData: SubmitUploadProps = {
      project_use_type_id: rowData.project_use_type_id,
      project_phase_id: rowData.project_phase_id,
      project_construction_category_id:
        rowData.project_construction_category_id,

      project_id: rowData.project_id,
      energy_code_id: rowData.energy_code_id,
      baseline_eeu_id:
        rowData.baseline_file_data &&
          rowData.baseline_file_data.id !== undefined
          ? rowData.baseline_file_data.id
          : null,
      design_eeu_id: rowData.id !== undefined ? rowData.id : null,
      year: rowData.year,
      reporting_year: rowData.reporting_year,
      use_type_subtype_id:
        rowData.use_type_subtype_id !== undefined
          ? rowData.use_type_subtype_id
          : null,
      // Include file_url and file_name for failed uploads so admins can download them
      file_url: rowData.file_url,
      file_name: rowData.file_name,
    };

    (async () => {
      try {
        const status = await submitUpload({ uploadProps: submitData });

        if (status === "success") {
          message.success(
            <Typography>
              Project submitted successfully.
              <br />
              <Link
                href={`/projects/${submitData.project_id}`}
                rel="noopener noreferrer"
                target="_blank"
              >
                View Details
              </Link>
            </Typography>
          );

          remove(index); // remove the row from the array
        } else {
          message.error("Failed to submit project. Please try again.");
        }
      } catch (error: any) {
        console.error("Error submitting project:", error);
        const errorMessage = error?.message || error?.response?.data?.error || "An error occurred while submitting the project. Please check the console for details.";
        message.error(errorMessage);
      }
    })();
    // This is just a placeholder. Replace it with your actual submit logic.
  };

  const handleSelectBaselineClick = (
    event: React.MouseEvent<HTMLButtonElement>,
    index: number
  ) => {
    setAnchorEl(event.currentTarget);
    setSelectedRecordIndex(index);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "simple-popover" : undefined;
  const userCompanyId = user.companyId;

  const [uploads, setUploads] = useState<FileData[]>([]);
  console.log("uploads", uploads);
  const [baselineFiles, setBaselineFiles] = useState<FileData[]>([]);
  const steps = [
    "Upload Multiple Files",
    "Match Files and Add Project Details",
  ];

  const [errorIndex] = useState<number | null>(null);
  const [activeStep] = useState(1);

  const [initialValues, setInitialValues] = useState<{ records: RecordData[] }>(
    {
      records: [],
    }
  ); // Provide a type for the initialValues state variable

  // Dynamic Parsing State
  const [dynamicProcessing, setDynamicProcessing] = useState<boolean>(false);
  const [reviewData, setReviewData] = useState<any>(null);
  const [reviewIndex, setReviewIndex] = useState<number | null>(null);
  const [reviewType, setReviewType] = useState<'design' | 'baseline'>('design');
  const [showReviewDialog, setShowReviewDialog] = useState<boolean>(false);

  const handleTriggerDynamicParsing = async (
    fileUrl: string,
    fileName: string,
    index: number,
    type: 'design' | 'baseline',
    setFieldValue: Function,
    values: any
  ) => {
    console.log("Button Clicked!", { fileUrl, fileName, index, type });
    if (!fileUrl) {
      console.error("Missing fileUrl");
      return;
    }

    setDynamicProcessing(true);
    setReviewIndex(index);
    setReviewType(type);

    try {
      const supabase = createClient();
      const { data: session } = await supabase.auth.getSession();

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/trigger_dynamic_parsing/`,
        {
          file_url: fileUrl,
          file_name: fileName,
          baseline_design: type
        },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session?.session?.access_token}`,
          },
        }
      );

      if (response.data.status === "success") {
        const result = response.data.data;
        let datasetToUse = null;

        // Handle new response structure with formatted_datasets
        if (result.formatted_datasets && Array.isArray(result.formatted_datasets)) {
          // Find the matching dataset (design or baseline)
          datasetToUse = result.formatted_datasets.find((ds: any) =>
            ds.baseline_design_type && ds.baseline_design_type.toLowerCase() === type.toLowerCase()
          );

          // If match not found, fallback to the first one (or 'unknown' if applicable)
          if (!datasetToUse && result.formatted_datasets.length > 0) {
            datasetToUse = result.formatted_datasets[0];
          }
        }
        // Fallback to legacy single-dataset structure if formatted_datasets is missing
        else if (result.formatted_data) {
          datasetToUse = result;
        }

        if (datasetToUse) {
          // Flatten the data for the UI (extract values from metadata objects)
          const rawData = datasetToUse.formatted_data || datasetToUse;
          const flattenedData: any = {};

          Object.keys(rawData).forEach(key => {
            const val = rawData[key];
            if (val && typeof val === 'object' && val.hasOwnProperty('value')) {
              flattenedData[key] = val.value;
            } else {
              flattenedData[key] = val;
            }
          });

          const finalExtractedData = {
            ...flattenedData,
            _raw_data: rawData
          };

          console.log("AI data extracted successfully, applying automatically...");
          await saveAndApplyAIParsedData(finalExtractedData, index, type, values.records[index], setFieldValue);
        } else {
          message.warning("No data found for this file type in the extraction result.");
        }
      } else {
        message.error(`Dynamic parsing failed: ${response.data.message}`);
      }
    } catch (error: any) {
      console.error("Error triggering dynamic parsing:", error);
      message.error("Failed to trigger dynamic parsing");
    } finally {
      setDynamicProcessing(false);
    }
  };

  const saveAndApplyAIParsedData = async (
    extractedData: any,
    index: number,
    type: 'design' | 'baseline',
    record: any,
    setFieldValue: Function
  ) => {
    const prefix = type === 'design' ? `records.${index}` : `records.${index}.baseline_file_data`;

    try {
      const supabase = createClient();
      const { data: session } = await supabase.auth.getSession();

      const payload = {
        ...extractedData,
        file_url: type === 'design' ? record.file_url : record.baseline_file_data?.file_url,
        file_name: extractedData.file_name || (type === 'design' ? record.file_name : record.baseline_file_data?.file_name),
        baseline_design: type,
        total_energy: Number(extractedData.total_energy),
        use_type_total_area: Number(extractedData.use_type_total_area || record.use_type_total_area),
        climate_zone: String(extractedData.climate_zone || ''),
        energy_units: extractedData.energy_units || 'mbtu',
        user_id: user.id || null,
        company_id: user.companyId || null
      };

      // Clean up internal keys before sending
      delete (payload as any)._raw_data;
      delete (payload as any).total_Electricity;
      delete (payload as any).total_NaturalGas;
      delete (payload as any).total_DistrictHeating;
      delete (payload as any).total_Other;
      delete (payload as any).total_On_SiteRenewables;

      if (isNaN(payload.total_energy) || isNaN(payload.use_type_total_area)) {
        console.warn("Invalid data returned from AI, dropping to review modal", payload);
        setReviewData(extractedData);
        setReviewIndex(index);
        setReviewType(type);
        setShowReviewDialog(true);
        return;
      }

      const saveResponse = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/save_ai_parsed_data/`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${session?.session?.access_token}`,
          },
        }
      );

      if (saveResponse.data.status === "success") {
        const newEeuId = saveResponse.data.eeu_id;
        setFieldValue(`${prefix}.id`, newEeuId);
        setFieldValue(`${prefix}.use_type_total_area`, extractedData.use_type_total_area);
        setFieldValue(`${prefix}.total_energy`, extractedData.total_energy);
        setFieldValue(`${prefix}.climate_zone`, extractedData.climate_zone);
        setFieldValue(`${prefix}.is_ai_parsed`, true);

        if (type === 'design') {
          setFieldValue(`records.${index}.upload_attempted`, false);
        } else {
          setFieldValue(`records.${index}.baseline_file_data.upload_attempted`, false);
        }

        message.success("AI parsed data applied automatically!");
      } else {
        throw new Error(saveResponse.data.message);
      }
    } catch (error) {
      console.error("Error auto-applying AI data, falling back to modal:", error);
      setReviewData(extractedData);
      setReviewIndex(index);
      setReviewType(type);
      setShowReviewDialog(true);
    }
  };

  const handleApplyDynamicData = async (setFieldValue: Function, values: any) => {
    if (reviewIndex === null || !reviewData) return;
    const record = values.records[reviewIndex];
    await saveAndApplyAIParsedData(reviewData, reviewIndex, reviewType, record, setFieldValue);
    setShowReviewDialog(false);
    setReviewData(null);
  };


  useEffect(() => {
    if (data) {
      const currentYear = new Date().getFullYear();
      const updatedUploads = data.uploads.map((upload: any) => ({
        ...upload,
        baseline_file_data: null,
        // Mark upload as attempted if there's an id OR if it's a failed upload
        upload_attempted: upload.id !== undefined || upload.upload_attempted === true,
        // Ensure year and reporting_year are properly initialized
        year: upload.year || currentYear,
        reporting_year: upload.reporting_year || currentYear,
        // Ensure all required fields have default values
        project_use_type_id: upload.project_use_type_id || 0,
        project_phase_id: upload.project_phase_id || 0,
        project_construction_category_id: upload.project_construction_category_id || 0,
        energy_code_id: upload.energy_code_id || 0,
        has_subtypes: upload.has_subtypes || false,
        project_id: upload.project_id || "00000000-0000-0000-0000-000000000000",
      }));

      // Add failed uploads as records with upload_attempted = true but no id
      const failedUploadRecords = (data.failed_uploads || []).map((failedUpload: any) => ({
        id: undefined,
        upload_attempted: true,
        file_name: failedUpload.file_name || failedUpload.response?.file_name || 'Unknown file',
        file_url: failedUpload.file_url || failedUpload.response?.url,  // Include file URL for download
        baseline_file_data: null,
        year: currentYear,
        reporting_year: currentYear,
        project_use_type_id: 0,
        project_phase_id: 0,
        project_construction_category_id: 0,
        energy_code_id: 0,
        has_subtypes: false,
        project_id: "00000000-0000-0000-0000-000000000000",
        use_type_total_area: 0,
        total_energy: 0,
        climate_zone: '',
      }));

      console.log("Updated uploads with proper year initialization:", updatedUploads);
      console.log("Failed upload records:", failedUploadRecords);

      const allRecords = [...updatedUploads, ...failedUploadRecords];
      setUploads(allRecords);

      const updatedBaselineFiles = Array.isArray(data.unmatched_baseline_files)
        ? data.unmatched_baseline_files.map((file: any) => ({
          ...file,
          visible: true,
        }))
        : [];
      setBaselineFiles([...updatedBaselineFiles]);
      setInitialValues({ records: allRecords });
    } else {
      setUploads([]);
      setBaselineFiles([]);
      const currentYear = new Date().getFullYear();
      setInitialValues({
        records: [
          {
            id: 0,
            project_use_type_id: 0,
            project_phase_id: 0,
            project_construction_category_id: 0,
            has_subtypes: false,
            energy_code_id: 0,
            year: currentYear,
            reporting_year: currentYear,
            use_type_total_area: 0,
            total_energy: 0,
            climate_zone: "",
            file_name: "",
            file_url: undefined,
            project_id: "00000000-0000-0000-0000-000000000000",
            baseline_file_data: null,
          },
        ],
      });
    }
  }, [data]);

  // Add these styles at the top of your file
  const fetchProjects = async (projectId?: string) => {
    const company_id: string = user.companyId;

    const projectList = await getProjectList(
      company_id,
      false,
      "Imperial",
      projectId
    );

    //setPrepopulatedData(projectList);
    return projectList;
  };


  const handleFileClick = (
    index_sub: number,
    file: FileData,
    setFieldValue: Function
  ) => {
    setFieldValue(`records.${selectedRecordIndex}.baseline_file_data`, file);

    //hides the selected file from the list of baseline file options that user can choose
    setBaselineFiles(
      baselineFiles.map((file, i) =>
        i === index_sub ? { ...file, visible: false } : file
      )
    );
    handleClose();


  };

  const handleOnChange = (
    index: number,
    value: number,
    additionalValues: { [key: string]: any },
    setFieldValue: Function
  ) => {
    setFieldValue(`records.${index}.project_use_type_id`, value);

    if (additionalValues.has_subtypes) {
      setFieldValue(`records.${index}.has_subtypes`, true);
    }
  };

  return (
    <div>
      {data && (
        <StepperComponent
          activeStep={activeStep}
          steps={steps}
          errorIndex={errorIndex}
        />
      )}
      <Formik
        initialValues={initialValues}
        enableReinitialize
        onSubmit={(values, { setSubmitting, resetForm }) => {

          setSubmitting(false);
          resetForm();
        }}
      >
        {({ values, handleSubmit, isSubmitting, setFieldValue }) => (
          <Form>
            <table className="table">
              <thead>
                <tr>
                  <th>Project Name</th>
                  <th>Files</th>
                  <th>Details</th>
                  <th>Actions</th>
                </tr>
                <tr
                  className="detailsRow"
                  style={{ backgroundColor: "transparent" }}
                >
                  <th>Step 1: Select project or create a new one</th>
                  <th>Step 2: Select the matching baseline file for the project</th>
                  <th>Step 3: Complete the required Detail Inputs</th>
                  <th>Step 4: Submit or Delete</th>
                </tr>
              </thead>
              <FieldArray name="records">
                {({ push, remove, form: { setFieldValue } }) => (
                  <tbody>
                    {values.records.map((record: RecordData, index) => (
                      <tr key={index}>
                        <td style={{ width: "20%", verticalAlign: "top" }}>
                          <ListProjects
                            companyId={userCompanyId}
                            onProjectSelect={(projectId) => {
                              setFieldValue(
                                `records.${index}.project_id`,
                                projectId
                              );
                              fetchProjects(projectId).then((projectList) => {
                                if (projectList && projectList.length > 0) {
                                  const project =
                                    projectList[0] as PrepopulatedDataProps;
                                  setFieldValue(
                                    `records.${index}.project_use_type_id`,
                                    project.project_use_type_id
                                  );
                                  setFieldValue(
                                    `records.${index}.project_construction_category_id`,
                                    project.project_construction_category_id
                                  );
                                  setFieldValue(
                                    `records.${index}.energy_code_id`,
                                    project.energy_code_id
                                  );
                                  setFieldValue(
                                    `records.${index}.project_phase_id`,
                                    project.project_phase_id
                                  );
                                  setFieldValue(
                                    `records.${index}.year`,
                                    project.year
                                  );
                                  setFieldValue(
                                    `records.${index}.reporting_year`,
                                    project.reporting_year || project.year
                                  );
                                }
                              });
                            }}
                            value={values.records[index].project_id}
                          />
                        </td>
                        <td style={{ width: "30%", verticalAlign: "top" }}>
                          <b>Design File *</b>
                          {values.records[index].id ? (
                            <ProjectCard
                              total_energy={record.total_energy}
                              use_type_total_area={record.use_type_total_area}
                              climate_zone={record.climate_zone}
                              file_name={record.file_name}
                              is_ai_parsed={(record as any).is_ai_parsed}
                            />
                          ) : values.records[index].upload_attempted && values.records[index].file_name ? (
                            <div style={{
                              padding: "16px",
                              border: "1px solid #ff9800",
                              borderRadius: "4px",
                              backgroundColor: "#fff3e0",
                              marginTop: "8px"
                            }}>
                              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <Tooltip title="File upload failed. The file could not be automatically processed. Please ensure it's a valid energy modeling report. Admin will review this upload.">
                                  <WarningAmberIcon style={{ color: "#ff9800", fontSize: "24px" }} />
                                </Tooltip>
                                <Typography variant="body1" style={{ color: "#e65100", fontWeight: 500 }}>
                                  {values.records[index].file_name}
                                </Typography>
                              </div>
                              <Typography variant="caption" style={{ color: "#bf360c", marginTop: "4px", display: "block" }}>
                                File uploaded but not processed Automatically. You can still complete the form and we will update you once it is processed.
                              </Typography>

                              {dynamicProcessing && reviewIndex === index && reviewType === 'design' ? (
                                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "8px" }}>
                                  <CircularProgress size={20} />
                                  <Typography variant="caption">AI Parsing in progress (~1 min)...</Typography>
                                </div>
                              ) : (values.records[index] as any).can_dynamic_parse ? (
                                <Button
                                  variant="outlined"
                                  size="small"
                                  startIcon={<AutoFixHighIcon />}
                                  style={{ marginTop: "8px", borderColor: "#ff9800", color: "#e65100" }}
                                  onClick={() => handleTriggerDynamicParsing(
                                    (values.records[index] as any).file_url,
                                    values.records[index].file_name,
                                    index,
                                    'design',
                                    setFieldValue,
                                    values
                                  )}
                                >
                                  Use AI Parser?
                                </Button>
                              ) : null}
                            </div>
                          ) : (

                            <FileDropzone
                              onUploadStatusChange={(status, response) => {
                                console.log("Upload Status Change:", status, response);
                                if (status === "done" || status === "warning") {
                                  // Check if this is a failed upload that allows form completion
                                  if (status === "warning" && response && response.status === 'error' && response.allow_form_completion) {
                                    // Failed upload - mark as attempted but don't set id
                                    setFieldValue(
                                      `records.${index}.upload_attempted`,
                                      true
                                    );
                                    if (response.file_name) {
                                      setFieldValue(
                                        `records.${index}.file_name`,
                                        response.file_name
                                      );
                                    }
                                    // Capture file_url so admin can download it later
                                    if (response.url) {
                                      setFieldValue(
                                        `records.${index}.file_url`,
                                        response.url
                                      );
                                    }

                                    // Capture dynamic parsing eligibility
                                    if (response.can_dynamic_parse) {
                                      setFieldValue(`records.${index}.can_dynamic_parse`, true);
                                      setFieldValue(`records.${index}.file_url`, response.file_url);
                                    }

                                    return;
                                  }


                                  // Capture dynamic parsing eligibility
                                  if (response.can_dynamic_parse) {
                                    setFieldValue(`records.${index}.can_dynamic_parse`, true);
                                    setFieldValue(`records.${index}.file_url`, response.file_url); // Ensure we have the URL
                                  }


                                  // Check if this is a PRM report (report_type 8)
                                  if (response.report_type === 8) {
                                    // For PRM reports, we get both baseline and design data
                                    // Set design data
                                    const designData = response.design;
                                    setFieldValue(
                                      `records.${index}.id`,
                                      designData.eeu_id
                                    );
                                    setFieldValue(
                                      `records.${index}.total_energy`,
                                      designData.total_energy
                                    );
                                    setFieldValue(
                                      `records.${index}.use_type_total_area`,
                                      designData.conditioned_area
                                    );
                                    setFieldValue(
                                      `records.${index}.climate_zone`,
                                      designData.climate_zone
                                    );
                                    setFieldValue(
                                      `records.${index}.file_name`,
                                      designData.file_name
                                    );
                                    // Capture file_url for future downloads
                                    if (response.url) {
                                      setFieldValue(
                                        `records.${index}.file_url`,
                                        response.url
                                      );
                                    }

                                    // Set baseline data automatically
                                    const baselineData = response.baseline;
                                    setFieldValue(
                                      `records.${index}.baseline_file_data`,
                                      {
                                        id: baselineData.eeu_id,
                                        total_energy: baselineData.total_energy,
                                        use_type_total_area: baselineData.conditioned_area,
                                        climate_zone: baselineData.climate_zone,
                                        file_name: baselineData.file_name,
                                        file_url: response.url,  // Include URL for baseline too
                                        visible: false
                                      }
                                    );
                                  } else {
                                    // Handle regular reports (non-PRM)
                                    setFieldValue(
                                      `records.${index}.id`,
                                      response.eeu_id
                                    );
                                    setFieldValue(
                                      `records.${index}.total_energy`,
                                      response.total_energy
                                    );
                                    setFieldValue(
                                      `records.${index}.use_type_total_area`,
                                      response.conditioned_area
                                    );
                                    setFieldValue(
                                      `records.${index}.climate_zone`,
                                      response.climate_zone
                                    );
                                    setFieldValue(
                                      `records.${index}.file_name`,
                                      response.file_name
                                    );
                                    // Capture file_url for future downloads
                                    if (response.url) {
                                      setFieldValue(
                                        `records.${index}.file_url`,
                                        response.url
                                      );
                                    }
                                  }
                                }
                              }}
                              baseline_design="design"
                              companyId={userCompanyId}
                              width="100%"
                            />
                          )}
                          {values.records[index].baseline_file_data === null ? (
                            <>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "center",
                                  paddingTop: "5px",
                                }}
                              >
                                <Button
                                  type="button"
                                  variant="contained"
                                  id={`select-uploaded-baseline-${index}`}
                                  onClick={(event) =>
                                    handleSelectBaselineClick(event, index)
                                  }
                                >
                                  Select Baseline File
                                </Button>
                              </div>

                              <Popover
                                id={id}
                                open={open}
                                anchorEl={anchorEl}
                                onClose={handleClose}
                                anchorOrigin={{
                                  vertical: "top",
                                  horizontal: "right",
                                }}
                                transformOrigin={{
                                  vertical: "top",
                                  horizontal: "left",
                                }}
                              >
                                <div
                                  style={{
                                    overflow: "auto",
                                    maxHeight: "600px",
                                    width: "500px",
                                    padding: "1em",
                                  }}
                                >
                                  <Typography
                                    variant="h5"
                                    style={{
                                      textAlign: "center",
                                      fontWeight: "bold",
                                    }}
                                  >
                                    Select or Upload a Baseline File for this
                                    Project
                                  </Typography>

                                  {baselineFiles.map((file, index_sub) => {
                                    if (file.visible) {
                                      return (
                                        <div
                                          style={{ marginBottom: "5px" }}
                                          key={index_sub}
                                          onClick={() =>
                                            handleFileClick(
                                              index_sub,
                                              file,
                                              setFieldValue
                                            )
                                          }
                                        >
                                          <ProjectCardHorizontal
                                            total_energy={file.total_energy}
                                            use_type_total_area={
                                              file.use_type_total_area
                                            }
                                            climate_zone={file.climate_zone}
                                            file_name={file.file_name}
                                          />
                                        </div>
                                      );
                                    }
                                    return null;
                                  })}
                                  <FileDropzone
                                    onUploadStatusChange={(
                                      status,
                                      response
                                    ) => {
                                      if (selectedRecordIndex === null) {
                                        return;
                                      }

                                      if (status === "done" || status === "warning") {
                                        // Check if this is a failed upload that allows form completion
                                        if (status === "warning" && response && response.status === 'error' && response.allow_form_completion) {
                                          // Failed upload - mark baseline as attempted but don't set id
                                          const currentBaseline = values.records[selectedRecordIndex].baseline_file_data;
                                          setFieldValue(
                                            `records.${selectedRecordIndex}.baseline_file_data`,
                                            {
                                              ...(currentBaseline || {}),
                                              upload_attempted: true,
                                              file_name: response.file_name || currentBaseline?.file_name,
                                              file_url: response.url || currentBaseline?.file_url  // Capture URL
                                            }
                                          );
                                          handleClose();
                                          return;
                                        }

                                        // Check if this is a PRM report (report_type 8)
                                        if (response.report_type === 8) {
                                          // For PRM reports, use baseline data for baseline field
                                          const baselineData = response.baseline;
                                          setFieldValue(
                                            `records.${selectedRecordIndex}.baseline_file_data`,
                                            {
                                              id: baselineData.eeu_id,
                                              total_energy: baselineData.total_energy,
                                              use_type_total_area: baselineData.conditioned_area,
                                              climate_zone: baselineData.climate_zone,
                                              file_name: baselineData.file_name,
                                              file_url: response.url,  // Capture URL
                                              visible: false
                                            }
                                          );
                                        } else {
                                          // Handle regular reports (non-PRM)
                                          setFieldValue(
                                            `records.${selectedRecordIndex}.baseline_file_data`,
                                            {
                                              id: response.eeu_id,
                                              total_energy: response.total_energy,
                                              use_type_total_area: response.conditioned_area,
                                              climate_zone: response.climate_zone,
                                              file_name: response.file_name,
                                              file_url: response.url,  // Capture URL
                                              visible: false
                                            }
                                          );
                                        }
                                        handleClose();
                                      }
                                    }}
                                    baseline_design="baseline"
                                    companyId={userCompanyId}
                                    width="100%"
                                  />
                                </div>
                              </Popover>
                            </>
                          ) : (
                            <div>
                              <b>Baseline File</b>

                              {values.records[index].baseline_file_data &&
                                values.records[index].baseline_file_data?.id ? (
                                <ProjectCard
                                  total_energy={
                                    values.records[index]?.baseline_file_data
                                      ?.total_energy
                                  }
                                  use_type_total_area={
                                    values.records[index].baseline_file_data
                                      ?.use_type_total_area
                                  }
                                  climate_zone={
                                    values.records[index].baseline_file_data
                                      ?.climate_zone
                                  }
                                  file_name={
                                    values.records[index].baseline_file_data
                                      ?.file_name
                                  }
                                  is_ai_parsed={(values.records[index].baseline_file_data as any)?.is_ai_parsed}
                                  showCloseIcon={true}
                                  onClose={() => {
                                    setFieldValue(
                                      `records.${index}.baseline_file_data`,
                                      null
                                    );

                                    setBaselineFiles((prevFiles) =>
                                      prevFiles.map((file) =>
                                        file.file_name ===
                                          values.records[index].baseline_file_data
                                            ?.file_name
                                          ? { ...file, visible: true }
                                          : file
                                      )
                                    );
                                    handleClose();
                                  }}
                                />
                              ) : values.records[index].baseline_file_data?.upload_attempted &&
                                values.records[index].baseline_file_data?.file_name ? (
                                <div style={{
                                  padding: "16px",
                                  border: "1px solid #ff9800",
                                  borderRadius: "4px",
                                  backgroundColor: "#fff3e0",
                                  marginTop: "8px"
                                }}>
                                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                    <Tooltip title="File upload failed. The file could not be automatically processed. Please ensure it's a valid energy modeling report. Admin will review this upload.">
                                      <WarningAmberIcon style={{ color: "#ff9800", fontSize: "24px" }} />
                                    </Tooltip>
                                    <Typography variant="body1" style={{ color: "#e65100", fontWeight: 500 }}>
                                      {values.records[index].baseline_file_data?.file_name}
                                    </Typography>
                                  </div>
                                  <Typography variant="caption" style={{ color: "#bf360c", marginTop: "4px", display: "block" }}>
                                    File uploaded but not processed. You can still complete the form.
                                  </Typography>

                                  {dynamicProcessing && reviewIndex === index && reviewType === 'baseline' ? (
                                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "8px" }}>
                                      <CircularProgress size={20} />
                                      <Typography variant="caption">AI Parsing in progress (~1 min)...</Typography>
                                    </div>
                                  ) : (values.records[index].baseline_file_data as any)?.can_dynamic_parse ? (
                                    <Button
                                      variant="outlined"
                                      size="small"
                                      startIcon={<AutoFixHighIcon />}
                                      style={{ marginTop: "8px", borderColor: "#ff9800", color: "#e65100" }}
                                      onClick={() => {
                                        const baselineData = values.records[index].baseline_file_data;
                                        if (baselineData && (baselineData as any).file_url) {
                                          handleTriggerDynamicParsing(
                                            (baselineData as any).file_url,
                                            baselineData.file_name,
                                            index,
                                            'baseline',
                                            setFieldValue,
                                            values
                                          );
                                        }
                                      }}
                                    >
                                      Use AI Parser?
                                    </Button>
                                  ) : null}
                                </div>
                              ) : null}

                            </div>
                          )}
                        </td>
                        <td style={{ width: "40%", verticalAlign: "top" }}>
                          <ThemeProvider theme={theme}>
                            <div
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                gap: "10px",
                              }}
                            >
                              <div style={{ width: "250px" }}>
                                <Field
                                  component={EnumList}
                                  id="project_use_type_id"
                                  params={{
                                    enum_name: "project_use_types",
                                    label: "Project Use Type",
                                    required: true,
                                    populateValue:
                                      values.records[index]
                                        .project_use_type_id || undefined,
                                    additional_fields: ["has_subtypes"],
                                  }}
                                  onChange={(
                                    value: number,
                                    additionalValues: { [key: string]: any }
                                  ) =>
                                    handleOnChange(
                                      index,
                                      value,
                                      additionalValues,
                                      setFieldValue
                                    )
                                  }
                                />
                                {(values.records[index].has_subtypes ||
                                  values.records[index]
                                    .use_type_subtype_id) && (
                                    <Field
                                      component={EnumList}
                                      name="use_type_subtype_id"
                                      params={{
                                        enum_name: "use_type_subtypes",
                                        label: "Use Type Subtype",
                                        required: false,
                                        populateValue:
                                          values.records[index]
                                            .use_type_subtype_id || undefined,
                                        additional_filter_fields: {
                                          use_type_id:
                                            values.records[index]
                                              .project_use_type_id,
                                        },
                                      }}
                                      onChange={(value: number) =>
                                        setFieldValue(
                                          `records.${index}.use_type_subtype_id`,
                                          value
                                        )
                                      }
                                    />
                                  )}

                                <div className="max-width-250">
                                  <YearField
                                    params={{
                                      label: "Occupancy Year",
                                      required: true,
                                      populateValue: values.records[index]?.year,
                                    }}
                                    onChange={(value: number) => {
                                      console.log(`Setting year for record ${index} to:`, value);
                                      setFieldValue(
                                        `records.${index}.year`,
                                        value
                                      );
                                    }}
                                  />
                                </div>

                                <div className="max-width-250">
                                  <ReportingYearField
                                    params={{
                                      label: "Reporting Year",
                                      required: true,
                                      populateValue: values.records[index]?.reporting_year,
                                    }}
                                    onChange={(value: number) => {
                                      console.log(`Setting reporting_year for record ${index} to:`, value);
                                      setFieldValue(
                                        `records.${index}.reporting_year`,
                                        value
                                      );
                                    }}
                                  />
                                </div>

                                <Field
                                  component={EnumList}
                                  name={`records.${index}.project_phase_id`}
                                  params={{
                                    enum_name: "project_phases",
                                    label: "Project Phase",
                                    required: true,
                                    populateValue:
                                      values.records[index].project_phase_id ||
                                      undefined,
                                  }}
                                  onChange={(value: number) => {
                                    setFieldValue(
                                      `records.${index}.project_phase_id`,
                                      value
                                    );
                                  }}
                                />
                              </div>
                              <div style={{ width: "55%" }}>
                                <Field
                                  component={EnumList}
                                  name="project_construction_category_id"
                                  params={{
                                    enum_name:
                                      "project_construction_categories",
                                    label: "Construction Category",
                                    required: true,
                                    populateValue:
                                      values.records[index]
                                        .project_construction_category_id ||
                                      undefined,
                                  }}
                                  onChange={(value: number) =>
                                    setFieldValue(
                                      `records.${index}.project_construction_category_id`,
                                      value
                                    )
                                  }
                                />
                                <Field
                                  component={EnumList}
                                  name="energy_code_id"
                                  params={{
                                    enum_name: "energy_codes",
                                    label: "Energy Code",
                                    required: true,
                                    populateValue:
                                      values.records[index].energy_code_id ||
                                      undefined,
                                  }}
                                  onChange={(value: number) =>
                                    setFieldValue(
                                      `records.${index}.energy_code_id`,
                                      value
                                    )
                                  }
                                />
                              </div>
                            </div>
                          </ThemeProvider>
                        </td>
                        <td>
                          <Button
                            variant="contained"
                            id={`submit-${index}`}
                            onClick={() =>
                              handleSubmitRow(
                                values.records[index],
                                index,
                                remove,
                                setFieldValue
                              )
                            }
                            disabled={
                              !values.records[index].project_id ||
                              !values.records[index].project_use_type_id ||
                              !values.records[index].project_phase_id ||
                              !values.records[index]
                                .project_construction_category_id ||
                              !values.records[index].energy_code_id ||
                              (!values.records[index].id && !values.records[index].upload_attempted && !values.records[index].baseline_file_data?.upload_attempted)
                            }
                          >
                            Submit
                          </Button>
                          <IconButton
                            onClick={() => {
                              setFieldValue(
                                `records.${index}.project_id`,
                                null
                              );
                              remove(index);
                            }}
                          >
                            <DeleteIcon id={`delete-icon-${index}`} />
                          </IconButton>
                        </td>
                      </tr>
                    ))}
                    <tr>
                      <td colSpan={4}>
                        <div
                          style={{
                            display: "flex",
                            justifyContent:
                              values.records.length === 0
                                ? "center"
                                : "flex-start",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                            }}
                          >
                            <Button
                              type="button"
                              variant="contained"
                              style={{
                                marginBottom: "20px",
                                marginTop: "20px",
                              }}
                              onClick={() => {
                                const currentYear = new Date().getFullYear();
                                push({
                                  id: 0,
                                  project_use_type_id: 0,
                                  project_phase_id: 0,
                                  project_construction_category_id: 0,
                                  has_subtypes: false,
                                  energy_code_id: 0,
                                  year: currentYear,
                                  reporting_year: currentYear,
                                  use_type_total_area: 0,
                                  total_energy: 0,
                                  climate_zone: "",
                                  file_name: "",
                                  file_url: undefined,
                                  project_id: "00000000-0000-0000-0000-000000000000",
                                  baseline_file_data: null,
                                });
                              }}
                            >
                              Add New Project
                            </Button>
                            {values.records.length === 0 && (
                              <Link href={`/dashboard/default`}>
                                <Button
                                  type="button"
                                  variant="contained"
                                  style={{ marginBottom: "10px" }}
                                >
                                  Return to All Projects
                                </Button>
                              </Link>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                )}
              </FieldArray>
            </table>
            <Dialog open={showReviewDialog} onClose={() => setShowReviewDialog(false)} maxWidth="md" fullWidth>
              <DialogTitle>Review AI Extracted Data</DialogTitle>
              <DialogContent>
                <Typography variant="body2" gutterBottom>
                  Please review and edit the values extracted by the AI parser. These values will be applied to your project.
                </Typography>

                {reviewData && (
                  <Grid container spacing={2} style={{ marginTop: "10px" }}>
                    <Grid item xs={12}>
                      <Typography variant="h6">Project Specs</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Conditioned Area (sq ft)"
                        type="number"
                        fullWidth
                        value={reviewData.use_type_total_area || ''}
                        onChange={(e) => setReviewData({ ...reviewData, use_type_total_area: parseFloat(e.target.value) })}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Climate Zone"
                        fullWidth
                        value={reviewData.climate_zone || ''}
                        onChange={(e) => setReviewData({ ...reviewData, climate_zone: e.target.value })}
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Typography variant="h6" style={{ marginTop: "10px" }}>Energy End-Uses ({reviewData.energy_units || 'mbtu'})</Typography>
                    </Grid>

                    {Object.keys(reviewData)
                      .filter(key => key.includes('_') && !key.startsWith('total_') && !['_raw_data', 'project_name'].includes(key))
                      .map(key => (
                        <Grid item xs={6} key={key}>
                          <TextField
                            label={key.replace('_', ' ')}
                            type="number"
                            fullWidth
                            size="small"
                            value={reviewData[key] ?? 0}
                            onChange={(e) => setReviewData({ ...reviewData, [key]: parseFloat(e.target.value) || 0 })}
                          />
                        </Grid>
                      ))}

                    <Grid item xs={12}>
                      <Typography variant="h6" style={{ marginTop: "10px", color: '#1976d2' }}>Total Energy: {reviewData.total_energy || '0'} {reviewData.energy_units || 'mbtu'}</Typography>
                    </Grid>
                  </Grid>
                )}
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setShowReviewDialog(false)}>Cancel</Button>
                <Button
                  onClick={() => handleApplyDynamicData(setFieldValue, values)}
                  variant="contained" color="primary"
                >
                  Apply Values
                </Button>
              </DialogActions>
            </Dialog>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default MultiUploadDetails;