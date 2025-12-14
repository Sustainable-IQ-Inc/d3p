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
  const [failedUploads, setFailedUploads] = useState<any>([]);
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
    // Extract just the IDs for the backend API (it expects array of numbers)
    const design_ids = designFiles.map((file: any) => 
      typeof file === 'object' && file.id ? file.id : file
    );
    const baseline_ids = baselineFiles.map((file: any) => 
      typeof file === 'object' && file.id ? file.id : file
    );
    
    const uploadProps = {
      design_files: design_ids,
      baseline_files: baseline_ids,
    };

    try {
      const response = await submitMultiUpload({ uploadProps });
      
      // Enhance the response uploads with file_url from our local designFiles
      if (response && response.uploads) {
        response.uploads = response.uploads.map((upload: any) => {
          // Find the matching design file from our local state
          const matchingDesignFile = designFiles.find((file: any) => 
            (typeof file === 'object' ? file.id : file) === upload.id
          );
          
          // If we have a matching file with file_url, add it to the upload
          if (matchingDesignFile && typeof matchingDesignFile === 'object') {
            return {
              ...upload,
              file_url: matchingDesignFile.file_url || matchingDesignFile.url,
              ...matchingDesignFile  // Preserve all other fields too
            };
          }
          return upload;
        });
      }
      
      // Add failed uploads info to the response
      if (failedUploads.length > 0) {
        response.failed_uploads = failedUploads;
      }
      
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
    
    
    if (response && (status === "done" || status === "warning")) {
      // Check if this is a PRM report (report_type 8)
      if (response.report_type === 8) {
        // For PRM reports, we get both baseline and design data
        const baselineData = response.baseline;
        const designData = response.design;
        
        // Add IDs if successful - store full response to preserve file_url
        if (designData.eeu_id) {
          setDesignFiles((prevDesignFiles: any) => [
            ...prevDesignFiles,
            { ...designData, file_url: response.url },  // Store full response with file_url
          ]);
        } else if (designData.status === 'error') {
          // Track failed upload
          setFailedUploads((prev: any) => [...prev, { source: 'design', response: designData }]);
        }
        
        if (baselineData.eeu_id) {
          setBaselineFiles((prevBaselineFiles: any) => [
            ...prevBaselineFiles,
            { ...baselineData, file_url: response.url },  // Store full response with file_url
          ]);
        } else if (baselineData.status === 'error') {
          // Track failed upload
          setFailedUploads((prev: any) => [...prev, { source: 'baseline', response: baselineData }]);
        }
      } else {
        // Handle regular reports (non-PRM)
        if (response.eeu_id) {
          // Successful upload - store full response to preserve file_url
          if (source === "design") {
            setDesignFiles((prevDesignFiles: any) => [
              ...prevDesignFiles,
              { ...response, id: response.eeu_id },  // Store full response with file_url
            ]);
          } else if (source === "baseline") {
            setBaselineFiles((prevBaselineFiles: any) => [
              ...prevBaselineFiles,
              { ...response, id: response.eeu_id },  // Store full response with file_url
            ]);
          }
        } else if (response.status === 'error' && response.allow_form_completion) {
          // Failed upload that allows form completion - include file_url for admin downloads
          setFailedUploads((prev: any) => [...prev, { 
            source, 
            response, 
            file_name: response.file_name,
            file_url: response.url  // Include file URL so admin can download failed files
          }]);
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
