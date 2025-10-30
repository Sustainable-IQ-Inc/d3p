import { useState, useCallback } from "react";
import submitMultiUpload from "app/api/SubmitMultiUpload";

import FileDropzone from "components/uploader/uploader";
import MainCard from "components/MainCard";
import { Button } from "@mui/material";
import Tooltip from "@mui/material/Tooltip";
import MultiUploadDetails from "./MultiUploadDetails";
import StepperComponent from "./MultiUploadStepper";

interface MultiUploadFileUploadProps {
  onUploadDataChange: (uploadData: any) => void;
}

export default function MultiUploadFileUpload({
  onUploadDataChange,
}: MultiUploadFileUploadProps) {
  const [activeStep] = useState(0);
  const [errorIndex] = useState<number | null>(null);
  const [designFiles, setDesignFiles] = useState<any>([]);
  const [baselineFiles, setBaselineFiles] = useState<any>([]);
  const [uploadData, setUploadData] = useState(null);
  const [uploadCount, setUploadCount] = useState(0);
  const steps = [
    "Upload Multiple Files",
    "Match Files and Add Project Details",
  ];
  const incrementUploadCount = useCallback(() => {
    setUploadCount((count) => count + 1);
  }, []);

  const decrementUploadCount = useCallback(() => {
    setUploadCount((count) => count - 1);
  }, []);

  const isUploading = uploadCount > 0;

  const handleNextClick = async () => {
    const uploadProps = {
      design_files: designFiles,
      baseline_files: baselineFiles,
    };

    try {
      const response = await submitMultiUpload({ uploadProps });
      
      setUploadData(response);
      onUploadDataChange(response);
    } catch (error) {
      console.error("An error occurred while submitting the files:", error);
    }
  };
  const handleUploadStatusChange = (
    status: string | null,
    response: any,
    source: string,
    isUploading: boolean
  ) => {
    
    
    if (response && status === "done") {
      // Check if this is a PRM report (report_type 8)
      if (response.report_type === 8) {
        // For PRM reports, we get both baseline and design data
        const baselineData = response.baseline;
        const designData = response.design;
        
        // Add both baseline and design IDs regardless of source
        // since PRM contains both
        setDesignFiles((prevDesignFiles: any) => [
          ...prevDesignFiles,
          designData.eeu_id,
        ]);
        setBaselineFiles((prevBaselineFiles: any) => [
          ...prevBaselineFiles,
          baselineData.eeu_id,
        ]);
      } else {
        // Handle regular reports (non-PRM)
        if (source === "design") {
          setDesignFiles((prevDesignFiles: any) => [
            ...prevDesignFiles,
            response.eeu_id,
          ]);
        } else if (source === "baseline") {
          setBaselineFiles((prevBaselineFiles: any) => [
            ...prevBaselineFiles,
            response.eeu_id,
          ]);
        }
      }
    }
  };
  
  
  return (
    <div>
      {!uploadData && (
        <div>
          <MainCard style={{ width: "1010px" }}>
            <StepperComponent
              activeStep={activeStep}
              steps={steps}
              errorIndex={errorIndex}
            />
            <div
              style={{
                display: "flex",
                justifyContent: "flex-start",
                gap: "5px",
              }}
            >
              <MainCard title="Design Files" style={{ width: "500px" }}>
                <FileDropzone
                  incrementUploadCount={incrementUploadCount}
                  decrementUploadCount={decrementUploadCount}
                  onUploadStatusChange={(status, response, isUploading) =>
                    handleUploadStatusChange(
                      status,
                      response,
                      "design",
                      isUploading
                    )
                  }
                  baseline_design="design"
                  companyId="1"
                  multiUpload={true}
                  width="95%"
                />
              </MainCard>
              <MainCard title="Baseline Files" style={{ width: "500px" }}>
                <FileDropzone
                  incrementUploadCount={incrementUploadCount}
                  decrementUploadCount={decrementUploadCount}
                  onUploadStatusChange={(status, response, isUploading) =>
                    handleUploadStatusChange(
                      status,
                      response,
                      "baseline",
                      isUploading
                    )
                  }
                  baseline_design="baseline"
                  companyId="1"
                  multiUpload={true}
                  width="95%"
                />
              </MainCard>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Tooltip
                title={
                  isUploading
                    ? "Please wait for all files to finish uploading"
                    : designFiles.length === 0
                    ? "Please upload at least one Design file"
                    : ""
                }
              >
                <span>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNextClick}
                    disabled={isUploading || designFiles.length === 0}
                  >
                    Next
                  </Button>
                </span>
              </Tooltip>
            </div>
          </MainCard>
        </div>
      )}
      {uploadData && <MultiUploadDetails data={uploadData} />}{" "}
      {/* conditionally render the component */}
    </div>
  );
}
