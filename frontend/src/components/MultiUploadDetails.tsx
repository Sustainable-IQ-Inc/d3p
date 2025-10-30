import React, { useState, useEffect } from "react";
import { Formik, Field, Form, FieldArray } from "formik";
import ProjectCard from "./ProjectDetailCard";
import ProjectCardHorizontal from "./ProjectDetailCardHorizontal";
import { Button, Typography, IconButton } from "@mui/material";
import Popover from "@mui/material/Popover";

import ListProjects from "components/projects/ListProjects";
import { getProjectList } from "components/projects/project";
import useUser from "hooks/useUser";

import EnumList from "components/enums/enum_list";
import YearField from "components/YearField";
import ReportingYearField from "components/ReportingYearField";
import DeleteIcon from "@mui/icons-material/Delete";
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
}
interface FileData extends KeyMetricFields {
  id: number;
  upload_id: number;
  visible?: boolean;
  baseline_file_data?: FileData;
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
      design_eeu_id: rowData.id,
      year: rowData.year,
      reporting_year: rowData.reporting_year,
      use_type_subtype_id:
        rowData.use_type_subtype_id !== undefined
          ? rowData.use_type_subtype_id
          : null,
    };

    (async () => {
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

  useEffect(() => {
    if (data) {
      const currentYear = new Date().getFullYear();
      const updatedUploads = data.uploads.map((upload: any) => ({
        ...upload,
        baseline_file_data: null,
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

      console.log("Updated uploads with proper year initialization:", updatedUploads);

      setUploads([...updatedUploads]);

      const updatedBaselineFiles = Array.isArray(data.unmatched_baseline_files)
        ? data.unmatched_baseline_files.map((file: any) => ({
            ...file,
            visible: true,
          }))
        : [];
      setBaselineFiles([...updatedBaselineFiles]);
      setInitialValues({ records: [...updatedUploads] });
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
        {({ values, handleSubmit, isSubmitting }) => (
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
                            />
                          ) : (
                            <FileDropzone
                              onUploadStatusChange={(status, response) => {
                                if (status === "done") {
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
                                      if (status === "done") {
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

                              {values.records[index].baseline_file_data && (
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
                              )}
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
                              !values.records[index].id
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
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default MultiUploadDetails;