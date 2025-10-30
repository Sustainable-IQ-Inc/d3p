import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Box, 
  Typography, 
  Button, 
  Alert,
  AlertTitle,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

interface ValidationIssue {
  id: string;
  name: string;
  message: string;
  field?: string;
  current_value?: any;
  suggested_value?: any;
  category: string;
  severity: 'warning' | 'error';
}

interface ValidationResult {
  status: string;
  can_submit: boolean;
  is_valid: boolean;
  summary: {
    total_issues: number;
    warnings: number;
    errors: number;
  };
  issues: {
    warnings: ValidationIssue[];
    errors: ValidationIssue[];
  };
  data: any;
}

interface DDXPreValidationModalProps {
  open: boolean;
  onClose: () => void;
  projectId: string;
  editedValues?: Record<string, string | number>;
  onValidationComplete: (canSubmit: boolean, validationResult?: ValidationResult) => void;
}

const modalStyle = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '90%',
  maxWidth: 800,
  maxHeight: '90vh',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
  overflow: 'auto',
};

const DDXPreValidationModal: React.FC<DDXPreValidationModalProps> = ({
  open,
  onClose,
  projectId,
  editedValues,
  onValidationComplete
}) => {
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && projectId) {
      runValidation();
    }
  }, [open, projectId, editedValues]);

  const runValidation = async () => {
    setLoading(true);
    setError(null);
    setValidationResult(null); // Reset validation result before running new validation
    
    try {
      const requestBody = {
        project_id: projectId,
        edited_values: editedValues || {}
      };
      
      // Use direct fetch with supabase authentication
      const supabase = (await import('utils/supabase')).createClient();
      const { data: session } = await supabase.auth.getSession();
      
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/ddx_pre_validation/`;
      const fetchResponse = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session?.session?.access_token}`,
        },
        body: JSON.stringify(requestBody),
      });

      const response = await fetchResponse.json();



      if (response.status === 'success' || response.status === 'validation_required') {
        setValidationResult(response);
      } else {
        setError(response.message || 'Validation failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to run validation');
    } finally {
      setLoading(false);
    }
  };

  const handleProceed = () => {
    if (validationResult) {
      onValidationComplete(validationResult.can_submit, validationResult);
    }
    onClose();
  };



  

  const renderValidationSummary = () => {
    if (!validationResult) return null;

    // Calculate counts from actual issues arrays to ensure accuracy
    const warningCount = validationResult.issues?.warnings?.length || 0;
    const errorCount = validationResult.issues?.errors?.length || 0;
    const totalIssues = warningCount + errorCount;
    const hasIssues = totalIssues > 0;

    return (
      <Box>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            DDx Share Pre-validation Summary
          </Typography>
          <Typography variant="body1" color="text.secondary">
            The project data being shared with the DDx was run through a set of pre-validation checks to assess if there are warnings and/or errors with any values that should be reviewed and/or revised.
          </Typography>
        </Box>

        {/* Summary Cards */}
        <Box sx={{ display: 'flex', gap: 3, mb: 4, justifyContent: 'center' }}>
          <Card sx={{ minWidth: 120, textAlign: 'center' }}>
            <CardContent>
              <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
              <Typography variant="h4" component="div">
                {warningCount}
              </Typography>
              <Typography color="text.secondary">
                Warnings
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ minWidth: 120, textAlign: 'center' }}>
            <CardContent>
              <ErrorIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
              <Typography variant="h4" component="div">
                {errorCount}
              </Typography>
              <Typography color="text.secondary">
                Errors
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Status Message */}
        {hasIssues ? (
          <Alert 
            severity={errorCount > 0 ? "error" : "warning"} 
            sx={{ mb: 3, textAlign: 'center' }}
          >
            <AlertTitle>
              {errorCount > 0 ? "Hold on! There are some things you need to take a look at. Errors must be resolved before submission." : "Please review the warnings."}
            </AlertTitle>
 
          </Alert>
        ) : (
          <Alert severity="success" sx={{ mb: 3, textAlign: 'center' }}>
            <AlertTitle>All validations passed!</AlertTitle>
            Your project data is ready for DDx submission.
          </Alert>
        )}
      </Box>
    );
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Box sx={modalStyle}>
        {loading ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
            <CircularProgress size={40} />
            <Typography sx={{ mt: 2 }}>Running validation checks...</Typography>
          </Box>
        ) : error ? (
          <Box>
            <Typography variant="h6" component="h2" gutterBottom>
              Validation Error
            </Typography>
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button onClick={onClose} variant="outlined">
                Close
              </Button>
              <Button onClick={runValidation} variant="contained">
                Retry
              </Button>
            </Box>
          </Box>
        ) : (
          <Box>
            {renderValidationSummary()}
            
            {/* Action Buttons */}
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 4 }}>
              <Button 
                onClick={onClose} 
                variant="outlined"
                size="large"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleProceed}
                variant="contained"
                size="large"
                sx={{ 
                  minWidth: 120,
                  backgroundColor: 'primary.main'
                }}
              >
                Review
              </Button>
            </Box>
          </Box>
        )}
      </Box>
    </Modal>
  );
};

export default DDXPreValidationModal; 