"use client";
import React, { useState, useEffect } from "react";
import { getFileDownloadUrl } from "app/api/FileDownloadUrl";
import { Button } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";

const DownloadFile = ({
  projectId,
  baselineDesign,
}: {
  projectId: string;
  baselineDesign: string;
}) => {
  const [signedUrl, setSignedUrl] = useState("");

  useEffect(() => {
    if (signedUrl) {
      window.open(signedUrl);
      setSignedUrl(""); // Reset the signedUrl state
    }
  }, [signedUrl]);

  const handleDownload = async () => {
    const response = await getFileDownloadUrl(projectId, baselineDesign);
    
    setSignedUrl(response);
  };

  const toTitleCase = (str: string) => {
    return str.replace(/\w\S*/g, (txt: string) => {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  };

  return (
    <Button onClick={handleDownload} endIcon={<DownloadIcon />}>
      {toTitleCase(baselineDesign)} File
    </Button>
  );
};

export default DownloadFile;
