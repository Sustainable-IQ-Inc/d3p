import pandas as pd
import requests
import io
import logging
from typing import Dict, List, Any, Optional, Tuple

# Create a simple printer function to avoid circular import
def printer(message: str):
    print(message)
    logging.info(message)


class MultiProjectExcelParser:
    """Parser for multi-project Excel files"""
    
    def __init__(self):
        # Define the required columns for multi-project Excel
        self.required_columns = [
            'project_name',
            'conditioned_area_sf', 
            'zip_code',
            'project_use_type',
            'project_construction_category',
            'project_phase',
            'energy_code',
            'report_type',
            'reporting_year'
        ]
        
        # Define optional columns with defaults
        self.optional_columns = {
            'area_units': 'sf',
            'climate_zone': None,
            'year': None,
            'energy_units': 'mbtu'
        }
        
        # Define valid enum values (these should match database values)
        self.valid_enums = {
            'project_construction_category': ['New', 'Existing'],
            'project_phase': ['Design', 'Concept', 'Construction Documents', 'Design Development', 'Final Design', 'Schematic Design', 'Unknown'],
            'climate_zone': ['1A', '1B', '2A', '2B', '3A', '3B', '3C', '4A', '4B', '4C', '5A', '5B', '6A', '6B', '7', '8'],
            'area_units': ['sf', 'sm'],
            # Restrict allowed energy units at parse-time; server will also enforce
            'energy_units': ['mbtu', 'gj'],
            'report_type': ['IESVE', 'EnergyPlus Report', 'EQuest - SIM Report', 'Generic .XLSX', 'EQuest - BEPS Report', 'EQuest - Standard Report', 'Other', 'IESVE PRM']
        }

    def parse_multi_project_excel(self, url: str) -> Dict[str, Any]:
        """
        Parse multi-project Excel file from URL
        
        Args:
            url: URL to the Excel file
            
        Returns:
            Dictionary containing parsed projects and validation results
        """
        try:
            # Download and read Excel file
            if url.startswith('http'):
                response = requests.get(url)
                excel_file = io.BytesIO(response.content)
            else:
                excel_file = url
            
            # Try reading with different header positions to handle instruction rows
            df = None
            for header_row in [0, 1, 2, 3]:
                try:
                    df_test = pd.read_excel(excel_file, sheet_name=0, header=header_row)
                    # Check if this looks like the right header row
                    if ('project_name' in df_test.columns and 
                        'conditioned_area_sf' in df_test.columns and 
                        'project_use_type' in df_test.columns):
                        df = df_test
                        break
                except:
                    continue
            
            if df is None:
                return {
                    'status': 'error',
                    'message': 'Could not find valid project data in Excel file',
                    'projects': [],
                    'validation_errors': []
                }
            
            # Remove any completely empty rows
            df = df.dropna(how='all').reset_index(drop=True)
            
            if len(df) == 0:
                return {
                    'status': 'error',
                    'message': 'No valid project data found in Excel file',
                    'projects': [],
                    'validation_errors': []
                }
            
            # Parse and validate each project
            parsed_projects = []
            validation_errors = []
            
            for index, row in df.iterrows():
                project_result = self._parse_project_row(row, index + 1)
                
                if project_result['status'] == 'valid':
                    parsed_projects.append(project_result['project'])
                elif project_result['status'] == 'warning':
                    parsed_projects.append(project_result['project'])
                    validation_errors.extend(project_result['warnings'])
                else:
                    validation_errors.extend(project_result['errors'])
            
            return {
                'status': 'success' if len(parsed_projects) > 0 else 'error',
                'projects': parsed_projects,
                'validation_errors': validation_errors,
                'total_projects': len(parsed_projects),
                'total_errors': len(validation_errors)
            }
            
        except Exception as e:
            printer(f"Error parsing multi-project Excel: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to parse Excel file: {str(e)}',
                'projects': [],
                'validation_errors': []
            }

    def _parse_project_row(self, row: pd.Series, row_number: int) -> Dict[str, Any]:
        """
        Parse a single project row
        
        Args:
            row: Pandas Series representing the row
            row_number: Row number for error reporting
            
        Returns:
            Dictionary with parsing results
        """
        project = {}
        errors = []
        warnings = []
        
        # Check required columns
        for col in self.required_columns:
            if col not in row.index or pd.isna(row[col]) or str(row[col]).strip() == '':
                errors.append(f"Row {row_number}: Missing required field '{col}'")
            else:
                project[col] = str(row[col]).strip()
        
        # Add optional columns with defaults
        for col, default in self.optional_columns.items():
            if col in row.index and not pd.isna(row[col]) and str(row[col]).strip() != '':
                project[col] = str(row[col]).strip()
            else:
                project[col] = default
        
        # Add energy data columns (all other numeric columns)
        energy_columns = []
        baseline_energy_data = {}
        design_energy_data = {}
        
        for col in row.index:
            if col not in self.required_columns and col not in self.optional_columns:
                if pd.notna(row[col]) and str(row[col]).strip() != '':
                    try:
                        # Try to convert to float for energy data
                        energy_value = float(row[col])
                        
                        # Check if this is a baseline or design energy field
                        if col.endswith('_baseline'):
                            # Extract the base field name (remove _baseline suffix)
                            base_field = col[:-9]  # Remove '_baseline'
                            baseline_energy_data[base_field] = energy_value
                            energy_columns.append(col)
                        elif col.endswith('_design'):
                            # Extract the base field name (remove _design suffix)
                            base_field = col[:-7]  # Remove '_design'
                            design_energy_data[base_field] = energy_value
                            energy_columns.append(col)
                        else:
                            # Legacy format - store as is
                            project[col] = energy_value
                            energy_columns.append(col)
                            
                    except (ValueError, TypeError):
                        # If not numeric, store as string
                        project[col] = str(row[col]).strip()
        
        # Store baseline and design energy data separately
        if baseline_energy_data:
            project['baseline_energy_data'] = baseline_energy_data
        if design_energy_data:
            project['design_energy_data'] = design_energy_data
        
        # Note: Skip local enum validation to avoid duplicate messages.
        # Enum validation is performed against database values later in the flow.
        
        # Validate numeric fields
        numeric_fields = ['conditioned_area_sf', 'year', 'reporting_year']
        for field in numeric_fields:
            if field in project and project[field] is not None:
                try:
                    if field in ['year', 'reporting_year']:
                        project[field] = int(float(project[field]))
                    else:
                        project[field] = float(project[field])
                except (ValueError, TypeError):
                    errors.append(f"Row {row_number}: Invalid numeric value for field '{field}': {project[field]}")
        
        # Determine status
        if errors:
            return {'status': 'error', 'errors': errors, 'project': None}
        elif warnings:
            return {'status': 'warning', 'warnings': warnings, 'project': project}
        else:
            return {'status': 'valid', 'project': project}

    def validate_against_database_enums(self, projects: List[Dict], supabase_client) -> Tuple[List[Dict], List[str]]:
        """
        Validate project enum values against actual database values
        
        Args:
            projects: List of parsed projects
            supabase_client: Supabase client for database queries
            
        Returns:
            Tuple of (validated_projects, validation_errors)
        """
        validation_errors = []
        validated_projects = []
        
        try:
            # Fetch enum values from database
            db_enums = self._fetch_database_enums(supabase_client)
            
            for i, project in enumerate(projects):
                project_errors = []
                
                # Validate each enum field
                enum_mappings = {
                    'project_use_type': ('enum_project_use_types', 'name'),
                    'project_construction_category': ('enum_project_construction_categories', 'name'),
                    'project_phase': ('enum_project_phases', 'name'),
                    'energy_code': ('enum_energy_codes', 'name'),
                    'report_type': ('enum_report_types', 'name'),
                    'climate_zone': ('enum_climate_zones', 'name')
                }
                
                for field, (table, column) in enum_mappings.items():
                    if field in project and project[field]:
                        valid_values = db_enums.get(table, [])
                        if project[field] not in valid_values:
                            project_errors.append(f"Invalid {field}: '{project[field]}'. Valid options: {', '.join(valid_values[:10])}{'...' if len(valid_values) > 10 else ''}")
                
                if project_errors:
                    validation_errors.extend([f"Project '{project.get('project_name', f'Row {i+1}')}': {error}" for error in project_errors])
                else:
                    validated_projects.append(project)
            
        except Exception as e:
            printer(f"Error validating against database: {str(e)}")
            validation_errors.append(f"Database validation error: {str(e)}")
            validated_projects = projects  # Return original projects if validation fails
        
        return validated_projects, validation_errors

    def _fetch_database_enums(self, supabase_client) -> Dict[str, List[str]]:
        """Fetch enum values from database"""
        enums = {}
        
        enum_tables = [
            'enum_project_use_types',
            'enum_project_construction_categories', 
            'enum_project_phases',
            'enum_energy_codes',
            'enum_report_types',
            'enum_climate_zones'
        ]
        
        for table in enum_tables:
            try:
                response = supabase_client.table(table).select('name').execute()
                enums[table] = [row['name'] for row in response.data]
            except Exception as e:
                printer(f"Error fetching {table}: {str(e)}")
                enums[table] = []
        
        return enums


def is_multi_project_excel(url: str) -> bool:
    """
    Check if an Excel file is a multi-project file by looking for multiple project rows
    
    Args:
        url: URL to the Excel file
        
    Returns:
        True if it's a multi-project Excel file, False otherwise
    """
    try:
        if url.startswith('http'):
            response = requests.get(url)
            excel_file = io.BytesIO(response.content)
        else:
            # Handle local file paths
            excel_file = url
            
        # Try reading with different header positions to handle instruction rows
        df = None
        for header_row in [0, 1, 2, 3]:
            try:
                df_test = pd.read_excel(excel_file, sheet_name=0, header=header_row)
                # Check if this looks like the right header row
                if ('project_name' in df_test.columns and 
                    'conditioned_area_sf' in df_test.columns and 
                    'project_use_type' in df_test.columns):
                    df = df_test
                    break
            except:
                continue
        
        if df is None:
            return False
        
        # Remove any completely empty rows
        df = df.dropna(how='all').reset_index(drop=True)
        
        # Check if we have the required multi-project columns
        required_columns = ['project_name', 'conditioned_area_sf', 'project_use_type']
        has_required_columns = all(col in df.columns for col in required_columns)
        
        # Check if we have multiple rows with project data
        has_multiple_projects = len(df) > 1
        
        # Check if we have project_name column with multiple non-empty values
        if 'project_name' in df.columns:
            non_empty_projects = df['project_name'].dropna().astype(str).str.strip()
            non_empty_projects = non_empty_projects[non_empty_projects != '']
            has_multiple_named_projects = len(non_empty_projects) > 1
        else:
            has_multiple_named_projects = False
        
        return has_required_columns and (has_multiple_projects or has_multiple_named_projects)
        
    except Exception as e:
        printer(f"Error checking if multi-project Excel: {str(e)}")
        return False


def parse_multi_project_excel_report(url: str) -> Dict[str, Any]:
    """
    Main function to parse multi-project Excel report
    
    Args:
        url: URL to the Excel file
        
    Returns:
        Dictionary containing parsing results
    """
    # First check if this is actually a multi-project Excel file
    if not is_multi_project_excel(url):
        # Raise exception to let the system try other parsers
        raise Exception("Not a multi-project Excel file")
    
    parser = MultiProjectExcelParser()
    result = parser.parse_multi_project_excel(url)
    
    # For multi-project Excel, we need to return a format that won't be processed by post_processing
    # Instead, we'll return a special format that signals to the upload handler to use multi-project service
    if result['status'] == 'success' and result['projects']:
        # Create a minimal df that indicates this is a multi-project file
        df = pd.DataFrame([{
            'report': 'generic_xlsx',  # Use existing report type for weather processing
            'report_field': 'multi_project_indicator',
            'energy_value': len(result['projects']),  # Number of projects
            'energy_units': 'mbtu',  # Use standard units
            'conditioned_area_sf': result['projects'][0].get('conditioned_area_sf', 0) if result['projects'] else 0,
            'weather_string': result['projects'][0].get('zip_code', '') if result['projects'] else '',
        }])
        
        return {
            'df': df,
            'status': 'success',
            'projects': result['projects'],
            'validation_errors': result['validation_errors'],
            'warnings': result.get('validation_errors', []),
            'report_type': 9  # Use numeric report type
        }
    else:
        # If parsing failed, raise exception to let system try other parsers
        raise Exception(f"Multi-project parsing failed: {result.get('message', 'Unknown error')}")
