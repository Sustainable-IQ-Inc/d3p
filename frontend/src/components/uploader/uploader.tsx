import React, { useState, useEffect } from "react";
import { InboxOutlined } from "@ant-design/icons";
import type { UploadProps } from "antd";
import { message, Upload } from "antd";
import { createClient } from "utils/supabase";
const { Dragger } = Upload;
import { RcFile, UploadChangeParam } from "antd/lib/upload";

type FileDropzoneProps = {
  disabledSetting?: boolean;
  reportType?: number;
  baseline_design?: string;
  onUploadStatusChange: (
    status: string | null,
    response: any,
    isUploading: any
  ) => void;
  companyId?: string;
  multiUpload?: boolean;
  width?: string;
  incrementUploadCount?: () => void;
  decrementUploadCount?: () => void;
};

const FileDropzone: React.FC<FileDropzoneProps> = ({
  onUploadStatusChange,
  disabledSetting,
  reportType,
  baseline_design,
  companyId,
  multiUpload = false,
  width = "300px",
  incrementUploadCount,
  decrementUploadCount,
}) => {
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [fileList, setFileList] = useState<RcFile[]>([]);
  const [isValidSize, setIsValidSize] = useState<boolean>(true);
  const [session, setSession] = useState<any>(null);
  const supabase = createClient();
  useEffect(() => {
    (async () => {
      const { data: session } = await supabase.auth.getSession();
      setSession(session);
    })();
  }, []);
  const FILE_SIZE_LIMIT_MB = 25; // You can change this value as needed
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const props: UploadProps = {
    name: "file",
    multiple: multiUpload,
    action: `${process.env.NEXT_PUBLIC_API_BASE_URL}/uploadfile/`,
    headers: {
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      Authorization: `Bearer ${session?.session?.access_token}`,
    },

    disabled: disabledSetting,
    showUploadList: {
      showRemoveIcon: true,
    },
    data: {
      //report_type: reportType ? reportType : undefined,
      company_id: companyId,
      baseline_design: baseline_design,
    },

    beforeUpload: (file: RcFile) => {
      const isSizeValid = file.size / 1024 / 1024 < FILE_SIZE_LIMIT_MB;
      
      if (!isSizeValid) {
        message.error(`File must be smaller than ${FILE_SIZE_LIMIT_MB}MB!`);
        setFileList((prevList) => [...prevList, { ...file, status: "error" }]);
        setIsValidSize(false);

        return false;
      }
      if (incrementUploadCount) {
        incrementUploadCount();
        
      }
      return isSizeValid;
    },

    onChange: (info: UploadChangeParam) => {
      const { status, response } = info.file;
      if (status === "done" || status === "error") {
        if (decrementUploadCount) {
          decrementUploadCount();
          
        }
      }
      if (status === "done") {
        // Check if the response contains an error status
        if (response && typeof response === 'object' && response.status === 'error') {
          // Extract error message from response
          let errorMessage = 'Upload failed';
          if (response.message) {
            try {
              // Try to parse the message if it's JSON
              const parsedMessage = JSON.parse(response.message);
              if (parsedMessage.error && typeof parsedMessage.error === 'object') {
                errorMessage = Object.entries(parsedMessage.error)
                  .map(([field, msg]) => `${field}: ${msg}`)
                  .join(', ');
              } else {
                errorMessage = response.message;
              }
            } catch (e) {
              // If parsing fails, use the raw message
              errorMessage = response.message;
            }
          }
          message.error(`${info.file.name} upload failed: ${errorMessage}`);
          setIsUploading(false);
          // Treat this as an error for status purposes
          setUploadStatus("error");
          onUploadStatusChange("error", response, isUploading);
        } else {
          // Actual success
          message.success(`${info.file.name} file uploaded successfully.`);
          setIsUploading(false);
          setUploadStatus(status || null);
          onUploadStatusChange(status || null, response, isUploading);
        }
      } else if (status === "error") {
        if (!isValidSize) {
          message.error(
            `${info.file.name} must be smaller than ${FILE_SIZE_LIMIT_MB}MB.`
          );
        } else {
          message.error(`${info.file.name} file upload failed.`);
        }
        setUploadStatus(status || null);
        onUploadStatusChange(status || null, response, isUploading);
      } else {
        // For uploading status
        if (!multiUpload) {
          setUploadStatus(status || null);
        }
        onUploadStatusChange(status || null, response, isUploading);
      }

      setFileList(info.fileList.map((file) => file as RcFile)); // Update the type of fileList
    },
    onDrop(e) {
      
    },
  };
  return (
    <Dragger
      {...props}
      fileList={fileList}
      style={{ width }}
      id={`file-upload-${baseline_design}`}
    >
      {disabledSetting ? (
        <p>Select a Report Type before uploading a file</p>
      ) : (
        uploadStatus !== "done" && (
          <>
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ fontSize: "24px" }} />
            </p>
            <p className="ant-upload-text">
              Click or drag file to this area to upload
            </p>
            <p className="ant-upload-hint">PDF, HTML and SIM files Supported</p>
          </>
        )
      )}
    </Dragger>
  );
};

export default FileDropzone;
