"use client";

import React, { useState } from "react";
import { Button, CircularProgress, Tooltip } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { exportProjectsCSV } from "app/api/ExportProjects";

interface ExportProjectsButtonProps {
  projectId?: string;
  companyId?: string;
  measurementSystem: string;
  filename?: string;
  variant?: "contained" | "outlined" | "text";
  color?: "primary" | "secondary" | "inherit";
  size?: "small" | "medium" | "large";
  searchTerm?: string;
}

const ExportProjectsButton: React.FC<ExportProjectsButtonProps> = ({
  projectId,
  companyId,
  measurementSystem,
  searchTerm,
  variant = "outlined",
  color = "primary",
  size = "medium",
}) => {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      console.log("Exporting with params:", { projectId, companyId, measurementSystem, searchTerm });
      await exportProjectsCSV(projectId, companyId, measurementSystem, searchTerm);
    } catch (error: any) {
      console.error("Export failed:", error);
      const errorMessage = error?.message || "Unknown error occurred";
      alert(`Failed to export data: ${errorMessage}. Please check the console for more details.`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <Tooltip title={projectId ? "Export Project Data" : "Export Portfolio Data"}>
      <span>
        <Button
          variant={variant}
          color={color}
          size={size}
          onClick={handleExport}
          disabled={isExporting}
          startIcon={isExporting ? <CircularProgress size={16} /> : <DownloadIcon />}
        >
          {isExporting ? "Exporting..." : projectId ? "Export Project" : "Export Portfolio"}
        </Button>
      </span>
    </Tooltip>
  );
};

export default ExportProjectsButton;

