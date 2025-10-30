"use client";
import { useState } from "react";
import MultiUploadDetails from "components/MultiUploadDetails";
import UploadTypeSelector from "components/UploadTypeSelector";
import MultiUploadFileUpload from "components/MultiUploadFileUpload";
import MultiProjectExcelUpload from "components/MultiProjectExcelUpload";

export default function MultiUpload() {
  const [uploadType, setUploadType] = useState<string>("single");
  const [hideUploadTypeSelector, setHideUploadTypeSelector] =
    useState<boolean>(false);

  const handleUploadTypeChange = (newUploadType: string) => {
    setUploadType(newUploadType);
  };

  const handleHideUploadSelector = (response: any) => {
    setHideUploadTypeSelector(true);
  };

  return (
    <div>
      {!hideUploadTypeSelector && (
        <UploadTypeSelector setUploadType={handleUploadTypeChange} />
      )}
      {uploadType === "single" ? <MultiUploadDetails /> : null}

      {uploadType === "multi" ? (
        <MultiUploadFileUpload onUploadDataChange={handleHideUploadSelector} />
      ) : null}

      {uploadType === "multi-excel" ? (
        <MultiProjectExcelUpload onUploadComplete={handleHideUploadSelector} />
      ) : null}
    </div>
  );
}
