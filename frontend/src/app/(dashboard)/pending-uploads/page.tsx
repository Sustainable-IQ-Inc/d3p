"use client";

import { useState, useEffect } from "react";

// material-ui
import { Grid, Box, Chip } from "@mui/material";
import { Link } from "@mui/material";

// project import
import MainCard from "components/MainCard";
import ReactTable from "components/ReactTable";
import { getPendingUploads } from "app/api/GetPendingUploads";
import { ColumnDef } from "@tanstack/react-table";

// assets

export type PendingUploadProps = {
  id: number;
  file_name: string;
  created_at: string;
  processing_error: string;
  upload_status_id: number;
  project_id: string | null;
  file_url: string;
  baseline_status: string | null;
  design_status: string | null;
};

// ==============================|| PENDING UPLOADS PAGE ||============================== //

const PendingUploadsPage = () => {
  const [data, setData] = useState<PendingUploadProps[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPendingUploads = () => {
    setLoading(true);
    getPendingUploads()
      .then((uploads: PendingUploadProps[]) => {
        setData(uploads || []);
      })
      .catch((error) => {
        console.error("Error fetching pending uploads:", error);
        setData([]);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchPendingUploads();
  }, []);

  const getStatusChip = (upload: PendingUploadProps) => {
    if (upload.baseline_status === "failed" || upload.design_status === "failed") {
      return <Chip label="Failed" color="error" size="small" />;
    }
    return <Chip label="Pending" color="warning" size="small" />;
  };

  const columns: ColumnDef<PendingUploadProps>[] = [
    {
      header: "File Name",
      accessorKey: "file_name",
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
      cell: ({ row }) => getStatusChip(row.original),
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
      header: "Project",
      accessorKey: "project_id",
      cell: ({ row }) => {
        const projectId = row.original.project_id;
        return projectId ? (
          <Link href={`/projects/${projectId}`}>View Project</Link>
        ) : (
          "Not linked"
        );
      },
    },
  ];

  return (
    <Grid container rowSpacing={4.5} columnSpacing={2.75}>
      <Grid item xs={12}>
        <MainCard sx={{ mt: 2 }} content={false}>
          <Box sx={{ p: 2 }}>
            <h2>Pending Uploads</h2>
            <p>
              Files that could not be processed automatically. You can still complete
              the form for these uploads. We'll notify you when processing is complete.
            </p>
          </Box>
          {loading ? (
            <Box sx={{ p: 2 }}>Loading...</Box>
          ) : data.length === 0 ? (
            <Box sx={{ p: 2 }}>No pending uploads found.</Box>
          ) : (
            <ReactTable
              id="pending-uploads-table"
              data={data}
              columns={columns}
              pagination={"server"}
              title={"Pending Uploads"}
            />
          )}
        </MainCard>
      </Grid>
    </Grid>
  );
};

export default PendingUploadsPage;


