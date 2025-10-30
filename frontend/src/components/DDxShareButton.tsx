import React from 'react';
import { Button, Tooltip } from '@mui/material';

interface DDxShareButtonProps {
  onClick: () => void;
  operationalEnergyData?: any;
  eeuDataEditDetails?: any[];
  variant?: 'contained' | 'outlined' | 'text';
  color?: 'primary' | 'secondary' | 'inherit';
  disabled?: boolean;
}

const DDxShareButton: React.FC<DDxShareButtonProps> = ({
  onClick,
  operationalEnergyData,
  eeuDataEditDetails,
  variant = 'contained',
  color = 'primary',
  disabled = false
}) => {
  // Use the same mechanism as the operational energy widget to check for design data
  const hasDesignData = () => {
    // If we have operational energy data, use the same check as the operational energy widget
    if (operationalEnergyData) {
      return operationalEnergyData.design && operationalEnergyData.design.status === 'success';
    }
    
    // If we have EEU data (project details page), check for design columns with actual data
    if (eeuDataEditDetails && eeuDataEditDetails.length > 0) {
      // Check all rows for any non-zero design values
      for (const row of eeuDataEditDetails) {
        if (!row) continue;
        
        // Check if there are any design columns with non-zero values
        const designColumns = Object.keys(row).filter(key => key.endsWith('_design'));
        
        for (const designColumn of designColumns) {
          const value = row[designColumn];
          
          // Check if value is a non-zero number
          // Handle both direct values and object values with .value property
          let numValue: number;
          if (typeof value === 'object' && value !== null && 'value' in value) {
            numValue = typeof value.value === 'number' ? value.value : parseFloat(value.value);
          } else {
            numValue = typeof value === 'number' ? value : parseFloat(value);
          }
          
          if (!isNaN(numValue) && numValue > 0) {
            return true; // Found actual design data
          }
        }
      }
      
      return false; // No non-zero design data found
    }
    
    return false; // No data available
  };

  const hasDesign = hasDesignData();
  const isDisabled = disabled || !hasDesign;
  const tooltipText = isDisabled ? 'Design data required for DDx sharing' : '';

  return (
    <Tooltip title={tooltipText}>
      <span>
        <Button
          variant={variant}
          color={color}
          onClick={onClick}
          disabled={isDisabled}
        >
          DDx Share
        </Button>
      </span>
    </Tooltip>
  );
};

export default DDxShareButton; 