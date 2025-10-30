"""
DDX Validation Rules

This module contains all the default validation rules for DDX data submission.
Rules are organized by category for easier maintenance and understanding.
"""

from typing import List
import sys
import os
from datetime import datetime
import re

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external.ddx_pre_validation import ValidationRule, ValidationSeverity


def get_all_default_rules() -> List[ValidationRule]:
    """Get all default validation rules"""
    current_year = datetime.now().year
    return [
        # Required fields
        ValidationRule(
            id="required_project_id",
            name="Project ID Required",
            description="Project ID must be provided and not empty",
            severity=ValidationSeverity.ERROR,
            formula="data.get('projectId', '').strip() != ''",
            field="projectId",
            category="completeness"
        ),
        ValidationRule(
            id="required_project_name",
            name="Project Name Required", 
            description="Project name must be provided and not empty",
            severity=ValidationSeverity.ERROR,
            formula="data.get('projectName', '').strip() != ''",
            field="projectName",
            category="completeness"
        ),
        ValidationRule(
            id="required_use_type",
            name="Use Type Required",
            description="Use type must be specified",
            severity=ValidationSeverity.ERROR,
            formula="data.get('useType1', '').strip() != ''",
            field="useType1",
            category="completeness"
        ),
        ValidationRule(
            id="required_climate_zone",
            name="Climate Zone Required",
            description="Climate zone must be specified",
            severity=ValidationSeverity.ERROR,
            formula="data.get('climateZone', '').strip() != ''",
            field="climateZone",
            category="completeness"
        ),
        ValidationRule(
            id="required_city",
            name="City Required",
            description="City must be provided and not empty",
            severity=ValidationSeverity.ERROR,
            formula="data.get('city', '').strip() != ''",
            field="city",
            category="completeness"
        ),
        ValidationRule(
            id="required_state",
            name="State Required",
            description="State must be provided and not empty",
            severity=ValidationSeverity.ERROR,
            formula="data.get('state', '').strip() != ''",
            field="state",
            category="completeness"
        ),
        
        # Data quality
        ValidationRule(
            id="positive_area",
            name="Valid Project Area Range",
            description="Project area must be between 100 and 5,000,000 GSF",
            severity=ValidationSeverity.ERROR,
            formula="100 <= float(data.get('useType1Area', 0)) <= 5000000",
            field="useType1Area",
            category="data_quality"
        ),
        ValidationRule(
            id="positive_baseline_eui",
            name="Valid Baseline EUI Range",
            description="Baseline EUI must be between 4 and 1,000 kBtu/GSF",
            severity=ValidationSeverity.ERROR,
            formula="4 <= float(data.get('baselineEUI', 0)) <= 1000",
            field="baselineEUI",
            category="data_quality"
        ),
        ValidationRule(
            id="positive_predicted_eui",
            name="Positive Predicted EUI", 
            description="Predicted EUI must be greater than 0",
            severity=ValidationSeverity.ERROR,
            formula="float(data.get('predictedEUI', 0)) > 0",
            field="predictedEUI",
            category="data_quality"
        ),
        ValidationRule(
            id="predicted_eui_savings_range",
            name="Valid EUI Savings Range",
            description="Predicted EUI savings must be between -200% and 200% compared to baseline EUI",
            severity=ValidationSeverity.ERROR,
            formula="float(data.get('baselineEUI', 0)) > 0 and float(data.get('predictedEUI', 0)) > 0 and -200 <= ((float(data.get('baselineEUI', 0)) - float(data.get('predictedEUI', 0))) / float(data.get('baselineEUI', 0))) * 100 <= 200",
            field="predictedEUI",
            category="data_quality"
        ),
        ValidationRule(
            id="valid_reporting_year",
            name="Valid Reporting Year",
            description="Reporting year must be a valid year between 2000 and 2050",
            severity=ValidationSeverity.ERROR,
            formula="'reportingYear' in data and data['reportingYear'] and str(data['reportingYear']).strip() not in ['', 'None', 'null'] and 2000 <= int(data['reportingYear']) <= 2050",
            field="reportingYear",
            category="data_quality"
        ),
        ValidationRule(
            id="valid_occupancy_year",
            name="Valid Occupancy Year",
            description="Occupancy year must be a valid year between 2000 and 2050",
            severity=ValidationSeverity.ERROR,
            formula="'estimatedOccupancyYear' in data and data['estimatedOccupancyYear'] and str(data['estimatedOccupancyYear']).strip() not in ['', 'None', 'null'] and 2000 <= int(data['estimatedOccupancyYear']) <= 2050",
            field="estimatedOccupancyYear",
            category="data_quality"
        ),
        ValidationRule(
            id="past_year",
            name="Past Year Data", 
            description="Just checking, you're submitting data for a past year",
            severity=ValidationSeverity.WARNING,
            formula=f"'reportingYear' in data and data['reportingYear'] and str(data['reportingYear']).strip() not in ['', 'None', 'null'] and int(data['reportingYear']) >= {current_year}",
            field="reportingYear",
            category="data_quality"
        ),
        ValidationRule(
            id="past_occupancy_year",
            name="Past Occupancy Year Data", 
            description="Just checking, you're submitting occupancy data for a past year",
            severity=ValidationSeverity.WARNING,
            formula=f"'estimatedOccupancyYear' in data and data['estimatedOccupancyYear'] and str(data['estimatedOccupancyYear']).strip() not in ['', 'None', 'null'] and int(data['estimatedOccupancyYear']) >= {current_year}",
            field="estimatedOccupancyYear",
            category="data_quality"
        ),
        # Business logic
        ValidationRule(
            id="predicted_vs_baseline_eui",
            name="EUI Improvement Check",
            description="Predicted EUI should be less than baseline EUI for energy savings",
            severity=ValidationSeverity.WARNING,
            formula="float(data.get('predictedEUI', 0)) < float(data.get('baselineEUI', 0))",
            field="predictedEUI",
            category="business_logic"
        ),
        
        # Format validation
        ValidationRule(
            id="valid_zipcode_format",
            name="Zip Code Required and Valid Format",
            description="Zip code is required and must be in valid US format (5 digits or 5+4 digits)",
            severity=ValidationSeverity.ERROR,
            formula="data.get('zipcode', '').strip() != '' and re.match(r'^\\d{5}(-\\d{4})?$', str(data.get('zipcode', '')).strip())",
            field="zipcode",
            category="data_quality"
        ),
    ]


 