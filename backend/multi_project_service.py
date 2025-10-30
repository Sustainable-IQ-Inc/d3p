import uuid
from typing import Dict, List, Any, Tuple, Optional
from supabase import Client
from parse_reports.parse_multi_project_xlsx import MultiProjectExcelParser
import logging_start
from conversions import convert_mbtu_to_kbtu, convert_mbtu_to_gj

class MultiProjectService:
    """Service for handling multi-project Excel uploads"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.parser = MultiProjectExcelParser()
    
    def process_multi_project_excel(self, file_url: str, company_id: str) -> Dict[str, Any]:
        """
        Process multi-project Excel file and create projects/uploads
        
        Args:
            file_url: URL to the Excel file
            company_id: ID of the company
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Parse the Excel file
            parse_result = self.parser.parse_multi_project_excel(file_url)
            
            if parse_result['status'] == 'error':
                return {
                    'status': 'error',
                    'message': parse_result.get('message', 'Failed to parse Excel file'),
                    'total_projects': 0,
                    'successful_projects': 0,
                    'failed_projects': 0,
                    'validation_errors': parse_result.get('validation_errors', []),
                    'created_project_ids': []
                }
            
            projects = parse_result['projects']
            validation_errors = parse_result['validation_errors'].copy()
            
            # Validate against database enums
            validated_projects, db_validation_errors = self.parser.validate_against_database_enums(
                projects, self.supabase
            )
            validation_errors.extend(db_validation_errors)
            
            # Validate allowed energy_units for each project before creation
            allowed_units = {'mbtu', 'gj'}
            projects_after_unit_validation = []
            for project in validated_projects:
                raw_units = project.get('energy_units')
                input_units = (raw_units if raw_units is not None else 'mbtu')
                input_units_lower = str(input_units).lower().strip()
                if input_units_lower not in allowed_units:
                    project_name = project.get('project_name', 'Unknown')
                    validation_errors.append(
                        f"Project '{project_name}': Invalid energy_units: '{input_units}'. Allowed: mbtu, gj"
                    )
                    continue
                projects_after_unit_validation.append(project)
            validated_projects = projects_after_unit_validation
            
            # Process each validated project
            created_project_ids = []
            created_projects = []
            failed_projects = []
            
            for project in validated_projects:
                try:
                    project_id = self._create_project_and_upload(project, company_id, file_url)
                    if project_id:
                        created_project_ids.append(project_id)
                        created_projects.append({
                            'project_id': project_id,
                            'project_name': project.get('project_name', 'Unknown')
                        })
                    else:
                        failed_projects.append(project.get('project_name', 'Unknown'))
                except Exception as e:
                    error_msg = f"Failed to create project {project.get('project_name', 'Unknown')}: {str(e)}"
                    logging_start.logger.error(error_msg)
                    failed_projects.append(project.get('project_name', 'Unknown'))
                    validation_errors.append(error_msg)
            
            # Calculate failed projects: projects that failed validation + projects that failed creation
            total_failed = len(projects) - len(validated_projects) + len(failed_projects)
            
            return {
                'status': 'success' if len(created_project_ids) > 0 else 'error',
                'total_projects': len(projects),
                'successful_projects': len(created_project_ids),
                'failed_projects': total_failed,
                'validation_errors': validation_errors,
                'created_project_ids': created_project_ids,
                'created_projects': created_projects
            }
            
        except Exception as e:
            logging_start.logger.error(f"Error processing multi-project Excel: {str(e)}")
            return {
                'status': 'error',
                'message': f'Processing failed: {str(e)}',
                'total_projects': 0,
                'successful_projects': 0,
                'failed_projects': 0,
                'validation_errors': [str(e)],
                'created_project_ids': []
            }
    
    def _create_project_and_upload(self, project_data: Dict[str, Any], company_id: str, file_url: str) -> Optional[str]:
        """
        Create a project and associated upload record
        
        Args:
            project_data: Parsed project data
            company_id: Company ID
            file_url: Original file URL
            
        Returns:
            Created project ID or None if failed
        """
        try:
            # Map enum values to IDs
            enum_mappings = self._get_enum_mappings(project_data)

            # Determine if a project already exists for this company with this name
            existing_project = None
            try:
                existing_query = (
                    self.supabase
                        .table('projects')
                        .select('id, project_name')
                        .eq('company_id', company_id)
                        .eq('project_name', project_data.get('project_name'))
                        .order('created_at', desc=True)
                        .limit(1)
                        .execute()
                )
                if existing_query and getattr(existing_query, 'data', None):
                    existing_project = existing_query.data[0]
            except Exception as e:
                logging_start.logger.warning(f"Error checking for existing project: {str(e)}")

            if existing_project:
                # Update existing project with provided non-null fields
                project_id = existing_project['id']
                update_fields = {
                    'conditioned_area_sf': project_data.get('conditioned_area_sf'),
                    'climate_zone_id': enum_mappings.get('climate_zone_id'),
                    'project_construction_category_id': enum_mappings.get('project_construction_category_id'),
                    'project_use_type_id': enum_mappings.get('project_use_type_id')
                }
                update_fields = {k: v for k, v in update_fields.items() if v is not None}
                if update_fields:
                    update_result = self.supabase.table('projects').update(update_fields).eq('id', project_id).execute()
                    if not update_result or not getattr(update_result, 'data', None):
                        logging_start.logger.warning(f"No data returned when updating project {project_id}. Fields: {update_fields}")
            else:
                # Create new project
                project_id = str(uuid.uuid4())
                project_record = {
                    'id': project_id,
                    'project_name': project_data.get('project_name'),
                    'conditioned_area_sf': project_data.get('conditioned_area_sf'),
                    'company_id': company_id,
                    'climate_zone_id': enum_mappings.get('climate_zone_id'),
                    'project_construction_category_id': enum_mappings.get('project_construction_category_id'),
                    'project_use_type_id': enum_mappings.get('project_use_type_id')
                }
                project_record = {k: v for k, v in project_record.items() if v is not None}
                project_result = self.supabase.table('projects').insert(project_record).execute()
                if not project_result or not getattr(project_result, 'data', None):
                    logging_start.logger.error(f"Failed to create project: {project_record}")
                    return None
            
            # Create upload record with energy data
            upload_record = self._create_upload_record(
                project_data, project_id, company_id, enum_mappings, file_url
            )
            
            upload_result = self.supabase.table('uploads').insert(upload_record).execute()
            
            if not upload_result.data:
                logging_start.logger.error(f"Failed to create upload: {upload_record}")
                # Clean up project if upload fails
                # Only delete if we just created this project in this call
                if not existing_project:
                    self.supabase.table('projects').delete().eq('id', project_id).execute()
                return None
            
            # Create EEU data records for both baseline and design if we have energy data
            baseline_energy_fields = self._extract_energy_fields(project_data, 'baseline')
            design_energy_fields = self._extract_energy_fields(project_data, 'design')
            
            if baseline_energy_fields:
                baseline_eeu_record = self._create_eeu_record(project_data, upload_result.data[0]['id'], baseline_energy_fields, 'baseline')
                baseline_eeu_result = self.supabase.table('eeu_data').insert(baseline_eeu_record).execute()
                
                if not baseline_eeu_result.data:
                    logging_start.logger.warning(f"Failed to create baseline EEU data for project {project_id}")
            
            if design_energy_fields:
                design_eeu_record = self._create_eeu_record(project_data, upload_result.data[0]['id'], design_energy_fields, 'design')
                design_eeu_result = self.supabase.table('eeu_data').insert(design_eeu_record).execute()
                
                if not design_eeu_result.data:
                    logging_start.logger.warning(f"Failed to create design EEU data for project {project_id}")
            
            return project_id
            
        except Exception as e:
            error_msg = f"Error creating project and upload: {str(e)}"
            logging_start.logger.error(error_msg)
            print(f"DEBUG: {error_msg}")  # Add debug output
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            return None
    
    def _get_enum_mappings(self, project_data: Dict[str, Any]) -> Dict[str, Optional[int]]:
        """Get enum ID mappings for project data"""
        mappings = {}
        
        enum_queries = {
            'climate_zone_id': ('enum_climate_zones', project_data.get('climate_zone')),
            'project_construction_category_id': ('enum_project_construction_categories', project_data.get('project_construction_category')),
            'project_use_type_id': ('enum_project_use_types', project_data.get('project_use_type')),
            'project_phase_id': ('enum_project_phases', project_data.get('project_phase')),
            'energy_code_id': ('enum_energy_codes', project_data.get('energy_code')),
            'report_type_id': ('enum_report_types', project_data.get('report_type'))
        }
        
        for field, (table, value) in enum_queries.items():
            if value:
                try:
                    result = self.supabase.table(table).select('id').eq('name', value).execute()
                    if result.data:
                        mappings[field] = result.data[0]['id']
                    else:
                        logging_start.logger.warning(f"No ID found for {field}: {value}")
                        mappings[field] = None
                except Exception as e:
                    logging_start.logger.error(f"Error getting ID for {field}: {str(e)}")
                    mappings[field] = None
            else:
                mappings[field] = None
        
        return mappings
    
    def _create_upload_record(self, project_data: Dict[str, Any], project_id: str, 
                            company_id: str, enum_mappings: Dict[str, Optional[int]], 
                            file_url: str) -> Dict[str, Any]:
        """Create upload record"""
        upload_record = {
            'project_id': project_id,
            'company_id': company_id,
            'area': project_data.get('conditioned_area_sf'),
            'area_units': project_data.get('area_units', 'sf'),
            'climate_zone_str': project_data.get('climate_zone'),
            'climate_zone_id': enum_mappings.get('climate_zone_id'),
            'project_phase_id': enum_mappings.get('project_phase_id'),
            'report_type_id': enum_mappings.get('report_type_id'),
            'energy_code_id': enum_mappings.get('energy_code_id'),
            'project_construction_category_id': enum_mappings.get('project_construction_category_id'),
            'project_use_type_id': enum_mappings.get('project_use_type_id'),
            'year': project_data.get('year'),
            'id_uuid': str(uuid.uuid4())
            # Note: upload_status_id removed since enum_upload_statuses table is empty
        }
        
        # Remove None values
        return {k: v for k, v in upload_record.items() if v is not None}
    
    def _extract_energy_fields(self, project_data: Dict[str, Any], baseline_design: str = None) -> Dict[str, float]:
        """Extract energy fields from project data for baseline or design"""
        energy_fields = {}
        
        if baseline_design:
            # New format: extract from baseline_energy_data or design_energy_data
            energy_data_key = f'{baseline_design}_energy_data'
            if energy_data_key in project_data:
                for field_name, value in project_data[energy_data_key].items():
                    if value is not None:
                        try:
                            energy_fields[field_name] = float(value)
                        except (ValueError, TypeError):
                            # Skip invalid values
                            continue
        else:
            # Legacy format: extract directly from project_data
            energy_field_patterns = [
                'Heating_', 'Cooling_', 'DHW_', 'Interior Lighting_', 'Exterior Lighting_',
                'Plug Loads_', 'Fans_', 'Pumps_', 'Process Refrigeration_', 'ExteriorUsage_',
                'OtherEndUse_', 'Heat Rejection_', 'Humidification_', 'HeatRecovery_',
                'total_', 'SolarDHW_', 'SolarPV_', 'Wind_', 'Other_'
            ]
            
            for field, value in project_data.items():
                if any(field.startswith(pattern) for pattern in energy_field_patterns):
                    try:
                        energy_fields[field] = float(value)
                    except (ValueError, TypeError):
                        pass
        
        return energy_fields
    
    def _create_eeu_record(self, project_data: Dict[str, Any], upload_id: int, 
                          energy_fields: Dict[str, float], baseline_design: str = 'design') -> Dict[str, Any]:
        """Create EEU data record with calculated totals"""
        # Get weather information for location data
        weather_info = self._get_weather_info(project_data)
        
        # Map provided report type name to its identifier_name from enum_report_types
        report_type_identifier = self._get_report_type_identifier(project_data.get('report_type'))

        # Validate and normalize energy units to MBtu; convert fields accordingly
        input_units = (project_data.get('energy_units') or 'mbtu').lower()
        allowed_units = {'mbtu', 'gj'}
        if input_units not in allowed_units:
            raise ValueError(f"Invalid energy_units '{input_units}'. Allowed: mbtu, gj")

        # If input is GJ, convert to MBtu
        if input_units == 'gj':
            # Multiply all energy fields by GJ->MBtu factor
            energy_fields = {k: float(v) * 0.947817 for k, v in energy_fields.items()}
            normalized_units = 'mbtu'
        
        else:
            normalized_units = 'mbtu'
        
        eeu_record = {
            'upload_id': upload_id,
            # Store identifier_name on eeu_data.report_type
            'report_type': report_type_identifier if report_type_identifier is not None else None,
            'use_type_total_area': project_data.get('conditioned_area_sf'),
            'area_units': project_data.get('area_units', 'sf'),
            'energy_units': normalized_units,
            'project_name': project_data.get('project_name'),
            'weather_string': project_data.get('zip_code', ''),
            'weather_station': weather_info.get('city_name', ''),
            'climate_zone': weather_info.get('climate_zone', project_data.get('climate_zone', '')),
            'zip_code': weather_info.get('zip_code', project_data.get('zip_code', '')),
            'city': weather_info.get('city', ''),
            'state': weather_info.get('state', ''),
            'egrid_subregion': weather_info.get('egrid_subregion', ''),
            'baseline_design': baseline_design
        }
        
        # Add energy fields
        eeu_record.update(energy_fields)
        
        # Calculate totals by fuel type
        totals = self._calculate_energy_totals(energy_fields)
        eeu_record.update(totals)
        
        return eeu_record

    def _get_report_type_identifier(self, report_type_name: Optional[str]) -> Optional[str]:
        """Given a report type display name, return its identifier_name from enum_report_types."""
        if not report_type_name:
            return None
        try:
            result = self.supabase.table('enum_report_types').select('identifier_name').eq('name', report_type_name).execute()
            if result and getattr(result, 'data', None):
                identifier = result.data[0].get('identifier_name')
                return identifier
        except Exception as e:
            # Log and fall back to None so caller can decide default behavior
            import logging_start
            logging_start.logger.warning(f"Error looking up identifier_name for report type '{report_type_name}': {str(e)}")
        return None
    
    def _calculate_energy_totals(self, energy_fields: Dict[str, float]) -> Dict[str, float]:
        """Calculate total energy values by fuel type"""
        totals = {
            'total_Electricity': 0.0,
            'total_NaturalGas': 0.0,
            'total_DistrictHeating': 0.0,
            'total_Other': 0.0,
            'total_On-SiteRenewables': 0.0,
            'total_energy': 0.0
        }
        
        # Sum up electricity fields
        electricity_fields = [field for field in energy_fields.keys() if field.endswith('_Electricity')]
        totals['total_Electricity'] = sum(energy_fields.get(field, 0.0) for field in electricity_fields)
        
        # Sum up natural gas fields
        natural_gas_fields = [field for field in energy_fields.keys() if field.endswith('_NaturalGas')]
        totals['total_NaturalGas'] = sum(energy_fields.get(field, 0.0) for field in natural_gas_fields)
        
        # Sum up district heating fields
        district_fields = [field for field in energy_fields.keys() if field.endswith('_DistrictHeating')]
        totals['total_DistrictHeating'] = sum(energy_fields.get(field, 0.0) for field in district_fields)
        
        # Sum up other fuel fields
        other_fields = [field for field in energy_fields.keys() if field.endswith('_Other')]
        totals['total_Other'] = sum(energy_fields.get(field, 0.0) for field in other_fields)
        
        # Sum up on-site renewables
        renewable_fields = [field for field in energy_fields.keys() if field.endswith('_On-SiteRenewables')]
        totals['total_On-SiteRenewables'] = sum(energy_fields.get(field, 0.0) for field in renewable_fields)
        
        # Calculate overall total energy (sum of all fuel types minus renewables since they offset)
        totals['total_energy'] = (
            totals['total_Electricity'] + 
            totals['total_NaturalGas'] + 
            totals['total_DistrictHeating'] + 
            totals['total_Other'] - 
            totals['total_On-SiteRenewables']
        )
        
        # Ensure total energy is not negative
        totals['total_energy'] = max(totals['total_energy'], 0.0)
        
        return totals
    
    def _get_weather_info(self, project_data: Dict[str, Any]) -> Dict[str, str]:
        """Get weather information for a project based on zip code"""
        try:
            # Import weather_check function
            from weather_location import weather_check
            
            zip_code = project_data.get('zip_code', '')
            report_type = 'generic_xlsx'  # Use generic xlsx for multi-project files
            
            if not zip_code:
                # Return empty weather info if no zip code
                return {
                    'city_name': '',
                    'ratio_match': '',
                    'climate_zone': '',
                    'zip_code': '',
                    'egrid_subregion': '',
                    'city': '',
                    'state': ''
                }
            
            # Call weather check to get location data
            weather_info = weather_check(zip_code, report_type)
            return weather_info
            
        except Exception as e:
            logging_start.logger.error(f"Error getting weather info for project {project_data.get('project_name', 'Unknown')}: {str(e)}")
            # Return empty weather info on error
            return {
                'city_name': '',
                'ratio_match': '',
                'climate_zone': '',
                'zip_code': project_data.get('zip_code', ''),
                'egrid_subregion': '',
                'city': '',
                'state': ''
            }


def create_multi_project_service() -> MultiProjectService:
    """Create MultiProjectService instance with Supabase client"""
    # Import the already configured supabase client from utils
    from utils import supabase
    return MultiProjectService(supabase)
