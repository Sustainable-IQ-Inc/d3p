"use client";

import { useState, useEffect } from "react";

// material-ui
import { Grid, Box, Chip, Button, Menu, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions, Select, FormControl, InputLabel } from "@mui/material";
import { MoreVert, Download, Refresh } from "@mui/icons-material";
import { message } from "antd";

// project import
import MainCard from "components/MainCard";
import ReactTable from "components/ReactTable";
import { getFailedUploads, downloadFailedFile, rerunFailedUpload } from "app/api/GetFailedUploads";
import { ColumnDef } from "@tanstack/react-table";

// assets

export type FailedUploadProps = {
  id: number;
  file_name: string;
  created_at: string;
  processing_error: string;
  upload_status_id: number;
  project_id: string | null;
  file_url: string;
  user_id: string;
  company_id: string;
  baseline_status: string | null;
  design_status: string | null;
  notified_admin: boolean;
  user_email?: string;
  profiles?: { email: string };
  companies?: { company_name: string };
};

// ==============================|| ADMIN FAILED UPLOADS PAGE ||============================== //

const AdminFailedUploadsPage = () => {
  const [data, setData] = useState<FailedUploadProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedUpload, setSelectedUpload] = useState<FailedUploadProps | null>(null);
  const [rerunDialogOpen, setRerunDialogOpen] = useState(false);
  const [rerunSide, setRerunSide] = useState<string>("");
  const [rerunning, setRerunning] = useState(false);
  const [menuPosition, setMenuPosition] = useState<{ top: number; left: number } | null>(null);

  const fetchFailedUploads = () => {
    setLoading(true);
    getFailedUploads()
      .then((uploads: FailedUploadProps[]) => {
        setData(uploads || []);
      })
      .catch((error) => {
        console.error("Error fetching failed uploads:", error);
        setData([]);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchFailedUploads();
  }, []);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, upload: FailedUploadProps) => {
    event.stopPropagation();
    event.preventDefault();
    const target = event.currentTarget;
    const rect = target.getBoundingClientRect();
    setMenuPosition({
      top: rect.bottom,
      left: rect.left,
    });
    setAnchorEl(target);
    setSelectedUpload(upload);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedUpload(null);
    setMenuPosition(null);
  };

  const handleDownload = async () => {
    if (!selectedUpload) return;
    
    try {
      const result = await downloadFailedFile(selectedUpload.id);
      if (result && result.signed_url) {
        window.open(result.signed_url, "_blank");
        message.success("Download started");
      } else {
        message.error("No file URL available for download");
      }
    } catch (error: any) {
      console.error("Download error:", error);
      const errorMessage = error?.message || error?.response?.data?.detail || "Failed to download file";
      message.error(`Failed to download file: ${errorMessage}`);
    }
    handleMenuClose();
  };

  const handleRerunClick = () => {
    if (!selectedUpload) return;
    
    // Determine which side to rerun
    const baselineFailed = selectedUpload.baseline_status === "failed";
    const designFailed = selectedUpload.design_status === "failed";
    
    if (baselineFailed && designFailed) {
      // Both failed, show dialog to choose
      setRerunDialogOpen(true);
    } else if (baselineFailed) {
      setRerunSide("baseline");
      handleRerun("baseline");
    } else if (designFailed) {
      setRerunSide("design");
      handleRerun("design");
    } else {
      // General failure, default to baseline
      setRerunSide("baseline");
      handleRerun("baseline");
    }
  };

  const handleRerun = async (side?: string) => {
    if (!selectedUpload) return;
    
    const sideToRerun = side || rerunSide;
    setRerunning(true);
    
    try {
      const result = await rerunFailedUpload(selectedUpload.id, sideToRerun);
      if (result && result.status === "success") {
        message.success(`${sideToRerun.charAt(0).toUpperCase() + sideToRerun.slice(1)} processing completed successfully`);
        fetchFailedUploads(); // Refresh list
      } else {
        const errorMsg = result?.message || result?.errors || result?.error || "Unknown error";
        message.error(`Rerun failed: ${errorMsg}`);
      }
    } catch (error: any) {
      console.error("Rerun error:", error);
      const errorMessage = error?.message || error?.response?.data?.detail || "Failed to rerun upload";
      message.error(`Failed to rerun upload: ${errorMessage}`);
    } finally {
      setRerunning(false);
      setRerunDialogOpen(false);
      handleMenuClose();
    }
  };

  const getStatusText = (upload: FailedUploadProps) => {
    if (upload.baseline_status === "failed" && upload.design_status === "failed") {
      return "Both Failed";
    } else if (upload.baseline_status === "failed") {
      return "Baseline Failed";
    } else if (upload.design_status === "failed") {
      return "Design Failed";
    }
    return "Failed";
  };

  const columns: ColumnDef<FailedUploadProps>[] = [
    {
      header: "File Name",
      accessorKey: "file_name",
    },
    {
      header: "User",
      accessorKey: "user_email",
      cell: ({ row }) => {
        return row.original.user_email || row.original.profiles?.email || "N/A";
      },
    },
    {
      header: "Company",
      accessorKey: "company_name",
      cell: ({ row }) => {
        return row.original.companies?.company_name || "Unknown";
      },
    },
    {
      header: "Upload Date",
      accessorKey: "created_at",
      cell: ({ row }) => {
        const date = new Date(row.original.created_at);
        return date.toLocaleDateString() + " " + date.toLocaleTimeString();
      },
    },
    {
      header: "Status",
      accessorKey: "status",
      cell: ({ row }) => {
        return <Chip label={getStatusText(row.original)} color="error" size="small" />;
      },
    },
    {
      header: "Error Message",
      accessorKey: "processing_error",
      cell: ({ row }) => {
        const error = row.original.processing_error;
        return error ? (
          <Box sx={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis" }}>
            {error}
          </Box>
        ) : (
          "-"
        );
      },
    },
    {
      header: "Actions",
      accessorKey: "actions",
      cell: ({ row }) => {
        return (
          <Button
            id="actions-button"
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              handleMenuOpen(e, row.original);
            }}
            startIcon={<MoreVert />}
            size="small"
          >
            Actions
          </Button>
        );
      },
    },
  ];

  return (
    <Grid container rowSpacing={4.5} columnSpacing={2.75}>
      <Grid item xs={12}>
        <MainCard sx={{ mt: 2 }} content={false}>
          <Box sx={{ p: 2 }}>
            <h2>Failed Uploads</h2>
            <p>Uploads that failed processing and require admin attention.</p>
          </Box>
          {loading ? (
            <Box sx={{ p: 2 }}>Loading...</Box>
          ) : data.length === 0 ? (
            <Box sx={{ p: 2 }}>No failed uploads found.</Box>
          ) : (
            <ReactTable
              id="failed-uploads-table"
              data={data}
              columns={columns}
              pagination={"server"}
              title={"Failed Uploads"}
            />
          )}
        </MainCard>
      </Grid>

      {/* Actions Menu */}
      <Menu 
        anchorEl={anchorEl} 
        open={Boolean(anchorEl)} 
        onClose={handleMenuClose}
        anchorReference="anchorPosition"
        anchorPosition={menuPosition ? { top: menuPosition.top, left: menuPosition.left } : undefined}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        disablePortal={false}
        style={{ zIndex: 1300 }}
        MenuListProps={{
          'aria-labelledby': 'actions-button',
        }}
        slotProps={{
          paper: {
            style: {
              maxHeight: '300px',
            },
          },
        }}
      >
        <MenuItem onClick={handleDownload}>
          <Download sx={{ mr: 1 }} /> Download File
        </MenuItem>
        <MenuItem onClick={handleRerunClick}>
          <Refresh sx={{ mr: 1 }} /> Rerun Processing
        </MenuItem>
      </Menu>

      {/* Rerun Dialog */}
      <Dialog open={rerunDialogOpen} onClose={() => setRerunDialogOpen(false)}>
        <DialogTitle>Select Side to Rerun</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Baseline or Design</InputLabel>
            <Select
              value={rerunSide}
              onChange={(e) => setRerunSide(e.target.value)}
              label="Baseline or Design"
            >
              <MenuItem value="baseline">Baseline</MenuItem>
              <MenuItem value="design">Design</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRerunDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => handleRerun()}
            variant="contained"
            disabled={!rerunSide || rerunning}
          >
            {rerunning ? "Rerunning..." : "Rerun"}
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
};

export default AdminFailedUploadsPage;

