import React, { useState } from "react";
import { Box, Typography, Button, Alert, List, ListItem, ListItemText, Chip, Card, CardContent, Link } from "@mui/material";
import { Download as DownloadIcon } from "@mui/icons-material";
import FileDropzone from "components/uploader/uploader";
import useUser from "hooks/useUser";

interface MultiProjectExcelUploadProps {
  onUploadComplete?: (result: any) => void;
}

const MultiProjectExcelUpload: React.FC<MultiProjectExcelUploadProps> = ({ onUploadComplete }) => {
  const { user } = useUser();
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleDownloadTemplate = () => {
    // Download the multi-project Excel template
    const link = document.createElement('a');
    link.href = `${process.env.NEXT_PUBLIC_API_BASE_URL}/download-multi-project-template/`;
    link.download = 'd3p-multi-project-template.xlsx';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleUploadStatusChange = async (status: string | null, response: any, isUploading: boolean) => {
    setIsUploading(isUploading);
    
    if (status === "done" && response) {
      // Check if this is a multi-project Excel file that needs special processing
      if (response.is_multi_project && response.report_type === 9) {
        console.log('Multi-project Excel detected, processing with multi-project service...');
        
        try {
          // Call the multi-project service endpoint
          const multiProjectResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/submit_multi_project_excel/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${await (await import('utils/supabase')).createClient().auth.getSession().then(s => s.data.session?.access_token)}`
            },
            body: JSON.stringify({
              file_url: response.url || response.file_url,
              company_id: user?.companyId
            })
          });
          
          const result = await multiProjectResponse.json();
          console.log('Multi-project service result:', result);
          
          setUploadResult(result);
          if (onUploadComplete) {
            onUploadComplete(result);
          }
        } catch (error) {
          console.error('Error processing multi-project file:', error);
          setUploadResult({
            status: 'error',
            message: `Failed to process multi-project file: ${error}`,
            total_projects: 0,
            successful_projects: 0,
            failed_projects: 0,
            validation_errors: [`Processing error: ${error}`],
            created_project_ids: []
          });
        }
      } else {
        // Regular single-file upload response
        setUploadResult(response);
        if (onUploadComplete) {
          onUploadComplete(response);
        }
      }
    }
  };

  const renderResults = () => {
    if (!uploadResult) return null;

    const { total_projects, successful_projects, failed_projects, validation_errors, created_project_ids, created_projects } = uploadResult;

    return (
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Upload Results
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Chip 
              label={`${successful_projects} Successful`} 
              color="success" 
              sx={{ mr: 1 }} 
            />
            <Chip 
              label={`${failed_projects} Failed`} 
              color={failed_projects > 0 ? "error" : "default"} 
              sx={{ mr: 1 }} 
            />
            <Chip 
              label={`${total_projects} Total`} 
              color="info" 
            />
          </Box>

          {validation_errors && validation_errors.length > 0 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Validation Issues:
              </Typography>
              <List dense>
                {validation_errors.map((error: string, index: number) => (
                  <ListItem key={index} sx={{ py: 0 }}>
                    <ListItemText primary={error} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          )}

          {successful_projects > 0 && (
            <Alert severity="success">
              <Typography variant="subtitle2" gutterBottom>
                Successfully created {successful_projects} project{successful_projects > 1 ? 's' : ''}!
              </Typography>
              
              {(created_projects && created_projects.length > 0) || (created_project_ids && created_project_ids.length > 0) ? (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    Individual Project Links:
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    {created_projects && created_projects.length > 0
                      ? created_projects.map((proj: { project_id: string; project_name: string }, index: number) => (
                          <Box key={proj.project_id || index} sx={{ mb: 1 }}>
                            <Link
                              href={`/projects/${proj.project_id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              color="primary"
                              underline="hover"
                              sx={{ fontWeight: 'medium' }}
                            >
                              View {proj.project_name || `Project ${index + 1}`} Details
                            </Link>
                            {proj.project_id && (
                              <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                (ID: {proj.project_id.substring(0, 8)}...)
                              </Typography>
                            )}
                          </Box>
                        ))
                      : created_project_ids.map((projectId: string, index: number) => (
                          <Box key={projectId || index} sx={{ mb: 1 }}>
                            <Link
                              href={`/projects/${projectId}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              color="primary"
                              underline="hover"
                              sx={{ fontWeight: 'medium' }}
                            >
                              View Project {index + 1} Details
                            </Link>
                            <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                              (ID: {projectId.substring(0, 8)}...)
                            </Typography>
                          </Box>
                        ))}
                  </Box>
                  
                  <Button
                    variant="contained"
                    color="primary"
                    href="/dashboard/default"
                    size="medium"
                    sx={{ mt: 1 }}
                  >
                    View All Projects
                  </Button>
                </Box>
              ) : null}
            </Alert>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Multi-Project Excel Upload
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 2 }}>
        Upload an Excel file containing multiple projects. Each row will create a separate project with its energy data.
      </Typography>

      <Button
        variant="outlined"
        startIcon={<DownloadIcon />}
        onClick={handleDownloadTemplate}
        sx={{ mb: 3 }}
      >
        Download Excel Template
      </Button>

      <Box sx={{ mb: 3 }}>
        <FileDropzone
          onUploadStatusChange={handleUploadStatusChange}
          companyId={user?.companyId}
          multiUpload={false}
          baseline_design="design"
          reportType={9} // We'll add this as a new report type for multi-project Excel
        />
      </Box>

      {isUploading && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="body2">
            Processing multi-project file... This may take a moment.
          </Typography>
        </Alert>
      )}

      {renderResults()}
    </Box>
  );
};

export default MultiProjectExcelUpload;
