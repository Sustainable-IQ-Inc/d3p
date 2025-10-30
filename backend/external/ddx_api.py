import requests
import sys
import os
import json
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from utils import encrypt_value, decrypt_value


# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging_start
import models
from project_details import get_latest_eeu_data, get_uploads_for_project, get_upload_data, get_project_energy_summary_data
from utils import return_enum_vals, supabase
ddx_api_base_url = os.getenv("DDX_API_BASE_URL")
from weather_location import get_location_data

def authenticate(firm_key,user_key):
    url = f"{ddx_api_base_url}/api/v1/authenticate"
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "firm_key": firm_key,
        "user_key": user_key
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def import_project(project: models.DDXImportProject):
    url = f"{ddx_api_base_url}/api/v1/import_project"
    headers = {
        'Content-Type': 'application/json'
    }
    data = project.model_dump()


    response = requests.post(url, json=data, headers=headers)



    try:
        if response.status_code == 200:
            return {"status": "success","response": response.json()}  # Try to parse and return JSON response regardless of status code
        else:
            return {"status": "error","response_code": response.status_code,"message": response.text}  # Return raw text if JSON parsing fails
    except requests.exceptions.JSONDecodeError:
        return {"status": "error","response_code": response.status_code,"message": response.text}  # Return raw text if JSON parsing fails

# Example usage

def get_ddx_value_by_id(ddx_id: int, ddx_table: str, value_column: str) -> str | None:
    """Get the DDX value from a DDX table using the ID.
    
    Args:
        ddx_id: The ID from the DDX table
        ddx_table: The name of the DDX table (e.g., 'ddx_use_types')
        value_column: The name of the value column (e.g., 'ddx_use_type')
        
    Returns:
        The DDX value or None if not found
    """
    if not ddx_id:
        return None
        
    try:
        
        query = supabase.table(ddx_table)\
            .select(value_column)\
            .eq('id', ddx_id)\
            .single()
        data, count = query.execute()
        
        
        result = data[1].get(value_column) if data[1] else None
        
        return result
    except Exception as e:
        return None

def get_ddx_mapping_from_enum_id(enum_table: str, enum_id: int, ddx_id_column: str, ddx_table: str, ddx_value_column: str) -> str | None:
    """Get DDX value by first getting the DDX ID from an enum table, then looking up the value.
    
    Args:
        enum_table: The enum table name (e.g., 'enum_project_use_types')
        enum_id: The ID in the enum table
        ddx_id_column: The column name containing the DDX table ID (e.g., 'ddx_use_type_id')
        ddx_table: The DDX table name (e.g., 'ddx_use_types')
        ddx_value_column: The column with the DDX value (e.g., 'ddx_use_type')
        
    Returns:
        The DDX value or None if not found
    """
    if not enum_id:
        return None
        
    try:
        
        # First get the DDX ID from the enum table
        query = supabase.table(enum_table)\
            .select(ddx_id_column)\
            .eq('id', enum_id)\
            .single()
        data, count = query.execute()
        
        
        if not data[1] or not data[1].get(ddx_id_column):
            return None
            
        ddx_id = data[1][ddx_id_column]
        
        # Then get the DDX value using the DDX ID
        ddx_value = get_ddx_value_by_id(ddx_id, ddx_table, ddx_value_column)
        
        return ddx_value
        
    except Exception as e:
        return None

def map_enum_to_ddx_value(value, enum_list_name, ddx_field_name, **kwargs):
    d3p_field_name = kwargs.get('d3p_field_name', 'name')
    
    # Special handling for project phases
    if enum_list_name == 'project_phases':
        # Query to get the phase with its DDX type
        query = supabase.table('enum_project_phases')\
            .select('*, ddx_phase_types(ddx_phase_type)')\
            .eq('name', value)\
            .single()
        try:
            data, count = query.execute()
            if data[1] and data[1].get('ddx_phase_types'):
                return data[1]['ddx_phase_types']['ddx_phase_type']
            return None
        except Exception as e:
            return None
    
    # Regular handling for other enums
    try:
        # Create a mapping dictionary from the enum values
        ddx_field_mapping = {rt[d3p_field_name]: rt[ddx_field_name] for rt in return_enum_vals(enum_list_name)}
        # Direct dictionary lookup
        return ddx_field_mapping.get(value)
    except Exception as e:
        return None


def map_climate_zone_to_ddx_value(value):
    climate_zones = return_enum_vals('climate_zones')
    # Create a new list with modified names
    climate_zones = [
        {**zone, 'name': f"{zone['name']} - {zone['description']}"} 
        for zone in climate_zones
    ]
    # Create a mapping dictionary
    ddx_field_mapping = {rt['name']: rt['ddx_climate_zone'] for rt in climate_zones}
    # Direct dictionary lookup
    return ddx_field_mapping.get(value)

def calculate_baseline_eui(use_type_id: int) -> float:
    """Calculate the baseline EUI by getting the baseline_eui from ddx_use_types.
    
    Args:
        use_type_id: ID from enum_project_use_types
        
    Returns:
        float: The calculated baseline EUI or 0 if not found
    """
    try:
        query = supabase.table('enum_project_use_types')\
            .select('ddx_use_types(baseline_eui)')\
            .eq('id', use_type_id)\
            .single()\
            .execute()
        
        baseline_eui = query.data.get('ddx_use_types', {}).get('baseline_eui', 0)
        return round(baseline_eui)
    except Exception as e:
        return 0  # Return 0 as a fallback value

def convert_mbtu_to_kwh(mbtu_value: float) -> float:
    """Convert MBtu to kWh"""
    return mbtu_value * 1000 * 0.29307107017

def convert_mbtu_to_kbtu(mbtu_value: float) -> float:
    """Convert MBtu to kBTU"""
    return mbtu_value * 1000

def convert_mbtu_to_therms(mbtu_value: float) -> float:
    """Convert MBtu to therms"""
    return mbtu_value * 1000 * 0.01000238767

def get_data_for_ddx(project_id):
    latest_eeu_data = get_latest_eeu_data(project_id)
    
    if latest_eeu_data['latest_design']:
        latest_eeu_id = latest_eeu_data['latest_design']
    else:
        return {"status": "error", "message": "No design EEU data found. Project must have a design EEU to export to DDX."}
        
    location_data = get_location_data(latest_eeu_id)                   
    uploads = get_uploads_for_project(project_id)
    upload_id = uploads[-1]['id']
    upload_data = get_upload_data(upload_id)
    
    project_upload_data = {}
    project_energy_summary_data = get_project_energy_summary_data(project_id)
    project_upload_data['projectName'] = project_energy_summary_data['project_name']
    
    # Use custom_project_id if available, otherwise use project_id
    project_upload_data['projectId'] = upload_data['custom_project_id'] if upload_data['custom_project_id'] else project_id
   
    # Get DDX phase type using ID mapping
    ddx_phase = get_ddx_mapping_from_enum_id(
        'enum_project_phases', 
        upload_data['project_phase_id'], 
        'ddx_phase_type_id', 
        'ddx_phase_types', 
        'ddx_phase_type'
    )
    if not ddx_phase:
        project_upload_data['projectPhase'] = "ERROR: Missing phase mapping"
    else:
        project_upload_data['projectPhase'] = ddx_phase
    # Store original value for helper text
    project_upload_data['_original_projectPhase'] = upload_data['enum_project_phases']['name']

    # Handle null year values properly
    if upload_data['reporting_year'] is not None:
        project_upload_data['reportingYear'] = str(upload_data['reporting_year'])
    elif upload_data['year'] is not None:
        # Fallback to occupancy year if reporting year is not set
        project_upload_data['reportingYear'] = str(upload_data['year'])
    else:
        # Default to current year if no year is specified
        from datetime import datetime
        current_year = datetime.now().year
        project_upload_data['reportingYear'] = str(current_year)
    
    # Add occupancy year as a separate field
    if upload_data['year'] is not None:
        project_upload_data['estimatedOccupancyYear'] = str(upload_data['year'])
    else:
        # Default to current year if no occupancy year is specified
        from datetime import datetime
        current_year = datetime.now().year
        project_upload_data['estimatedOccupancyYear'] = str(current_year)
        
    project_upload_data['country'] = 'United States'
    project_upload_data['state'] = location_data['state']
    project_upload_data['zipcode'] = location_data['zip_code']
    project_upload_data['city'] = location_data['city']

    # Get DDX use type using ID mapping
    ddx_use_type = get_ddx_mapping_from_enum_id(
        'enum_project_use_types', 
        upload_data['project_use_type_id'], 
        'ddx_use_type_id', 
        'ddx_use_types', 
        'ddx_use_type'
    )
    if not ddx_use_type:
        project_upload_data['useType1'] = "ERROR: Missing use type mapping"
    else:
        project_upload_data['useType1'] = ddx_use_type
    # Store original value for helper text
    project_upload_data['_original_useType1'] = upload_data['enum_project_use_types']['name']
    # Store original ID for frontend dropdown population
    project_upload_data['_original_useType1_id'] = upload_data['project_use_type_id']

    project_upload_data['useType1Area'] = project_energy_summary_data['conditioned_area']

    # Get DDX energy code using ID mapping
    ddx_energy_code = get_ddx_mapping_from_enum_id(
        'enum_energy_codes', 
        upload_data['energy_code_id'], 
        'ddx_energy_code_id', 
        'ddx_energy_codes', 
        'ddx_energy_code'
    )
    if not ddx_energy_code:
        project_upload_data['designEnergyCode'] = "ERROR: Missing energy code mapping"
    else:
        project_upload_data['designEnergyCode'] = ddx_energy_code
    # Store original value for helper text
    project_upload_data['_original_designEnergyCode'] = upload_data['enum_energy_codes']['name']
    # Store original ID for frontend dropdown population
    project_upload_data['_original_designEnergyCode_id'] = upload_data['energy_code_id']

    try:
        # Calculate baselineEUI using the utility function
        baseline_eui = calculate_baseline_eui(upload_data['project_use_type_id'])
        project_upload_data['baselineEUI'] = str(baseline_eui)
    except Exception as e:
        project_upload_data['baselineEUI'] = "0"  # Set a default value
    
    project_upload_data['predictedEUI'] = round(project_energy_summary_data['total_energy_per_unit_area_design'], 2)
    project_upload_data['energyModelingTool'] = map_enum_to_ddx_value(
        project_energy_summary_data.get('report_type'),
        'report_types',
        'ddx_report_type_name',
        d3p_field_name='identifier_name'
    )
    # Fallback to a safe string if mapping failed or source is missing
    if not project_upload_data['energyModelingTool']:
        raw_report_type = project_energy_summary_data.get('report_type')
        project_upload_data['energyModelingTool'] = str(raw_report_type) if raw_report_type is not None else 'Other'

    project_upload_data['climateZone'] = map_climate_zone_to_ddx_value(project_energy_summary_data['climate_zone'])

    # Calculate fuel subtotals
    try:
        from project_details import get_energy_end_uses_data
        energy_data = get_energy_end_uses_data(project_id, 'design', output_units='mbtu')
        
        if energy_data['status'] == 'success':
            eeu_df = energy_data['eeu_data']
            renewables_df = energy_data['renewables']
            
            # Calculate electricity produced off-site (total electricity minus on-site renewables)
            total_electricity = eeu_df['electricity'].sum() if 'electricity' in eeu_df.columns else 0
            total_renewables = renewables_df.sum(numeric_only=True).sum() if len(renewables_df) > 0 else 0
            electricity_produced_off_site = max(0, total_electricity - total_renewables)
            
            # Natural gas combusted on-site
            natural_gas_combusted_on_site = eeu_df['fossil_fuels'].sum() if 'fossil_fuels' in eeu_df.columns else 0
            
            # Get district totals
            district_total = eeu_df['district'].sum() if 'district' in eeu_df.columns else 0
            
            # Calculate district cooling from cooling use types with district fuel
            district_cooling = 0
            district_hot_water = district_total  # Start with full district total
            
            if len(eeu_df) > 0:
                # Look for cooling use types in the data
                cooling_use_types = eeu_df[eeu_df.index.str.contains('Cooling', case=False, na=False)]
                if len(cooling_use_types) > 0:
                    district_cooling = cooling_use_types['district'].sum() if 'district' in cooling_use_types.columns else 0
                    # Subtract cooling from hot water (remainder goes to hot water)
                    district_hot_water = max(0, district_total - district_cooling)
            
            # Other fuel types
            diesel = 0  # Not currently tracked separately in the system
            other_fuels = eeu_df['other'].sum() if 'other' in eeu_df.columns else 0
            
            # District steam (part of district total, but separated for DDX)
            district_steam = 0  # Not currently tracked separately
            
            # Electricity from renewables on-site
            electricity_from_renewables_on_site = total_renewables
            
            # Convert electricity to kWh and gas to therms
            electricity_produced_off_site_kwh = convert_mbtu_to_kwh(electricity_produced_off_site)
            natural_gas_combusted_on_site_therms = convert_mbtu_to_therms(natural_gas_combusted_on_site)
            district_hot_water_kbtu = convert_mbtu_to_kbtu(district_hot_water)
            district_chilled_water_kbtu = convert_mbtu_to_kbtu(district_cooling)
            district_steam_kbtu = convert_mbtu_to_kbtu(district_steam)
            
            # Add fuel subtotals to the data (read-only)
            project_upload_data['electricityProducedOffSite'] = round(electricity_produced_off_site_kwh, 2)
            project_upload_data['_original_electricityProducedOffSite_mbtu'] = round(electricity_produced_off_site, 2)
            project_upload_data['naturalGasCombustedOnSite'] = round(natural_gas_combusted_on_site_therms, 2)
            project_upload_data['_original_naturalGasCombustedOnSite_mbtu'] = round(natural_gas_combusted_on_site, 2)
            project_upload_data['districtSteam'] = round(district_steam_kbtu, 2)
            project_upload_data['districtHotWater'] = round(district_hot_water_kbtu, 2)
            project_upload_data['districtChilledWater'] = round(district_chilled_water_kbtu, 2)
            project_upload_data['diesel'] = round(other_fuels, 2)
            project_upload_data['electricityFromRenewablesOnSite'] = round(electricity_from_renewables_on_site, 2)
            
            
    except Exception as e:
        # Set default values if calculation fails
        project_upload_data['electricityProducedOffSite'] = 0
        project_upload_data['_original_electricityProducedOffSite_mbtu'] = 0
        project_upload_data['naturalGasCombustedOnSite'] = 0
        project_upload_data['_original_naturalGasCombustedOnSite_mbtu'] = 0
        project_upload_data['districtSteam'] = 0
        project_upload_data['districtHotWater'] = 0
        project_upload_data['districtChilledWater'] = 0
        project_upload_data['diesel'] = 0
        project_upload_data['electricityFromRenewablesOnSite'] = 0

    return {"status": "success", "data": project_upload_data}

def insert_api_call_db(project_id, response_code, response, outbound_request=None):

    def ddx_id_extract(response):
            try:
                return response.id
            except:
                return None
    
    insert_data = {
        'project_id': project_id,
        'response_code': response_code,
        'response': response
    }
    
    # Add outbound_request if provided (serialize as JSON string)
    if outbound_request:
        insert_data['outbound_request'] = json.dumps(outbound_request)
            
    query = supabase.table('integrations_sync').insert([insert_data])
    data, count = query.execute()
    return data
 
    
def clean_field_names(data):
    # Get the schema from our Pydantic model
    field_mappings = {
        field_name: {
            'display_name': field.json_schema_extra.get('display_name', field_name),
            'editable': field_name in ['baselineEUI', 'city', 'state', 'zipcode', 'reportingYear', 'estimatedOccupancyYear']  # Add more editable fields here as needed
        }
        for field_name, field in models.DDXImportProject.model_fields.items()
        if field_name != 'authToken'  # Exclude authToken as it's not part of the data
    }
    
    # Add fuel subtotal fields as read-only
    fuel_subtotal_fields = {
        'electricityProducedOffSite': {
            'display_name': 'Electricity Produced Off-Site (MBtu)',
            'editable': False
        },
        'naturalGasCombustedOnSite': {
            'display_name': 'Natural Gas Combusted On-Site (MBtu)', 
            'editable': False
        },
        'districtSteam': {
            'display_name': 'District Steam (MBtu)',
            'editable': False
        },
        'districtHotWater': {
            'display_name': 'District Hot Water (MBtu)',
            'editable': False
        },
        'districtChilledWater': {
            'display_name': 'District Chilled Water (MBtu)',
            'editable': False
        },
        'diesel': {
            'display_name': 'Diesel (MBtu)',
            'editable': False
        },
        'electricityFromRenewablesOnSite': {
            'display_name': 'Electricity from Renewables On-Site (MBtu)',
            'editable': False
        }
    }
    
    # Merge fuel subtotal fields with existing field mappings
    field_mappings.update(fuel_subtotal_fields)
    
    # Create a new dictionary with renamed keys and editable information
    clean_data = {
        field_mappings[key]['display_name']: {
            'value': value,
            'editable': field_mappings[key]['editable']
        }
        for key, value in data.items()
        if key in field_mappings
    }
    
    # Add _original_ fields for helper tooltips (preserve them as-is)
    for key, value in data.items():
        if key.startswith('_original_'):
            # Map the original field name to the display name equivalent
            base_field = key.replace('_original_', '')
            if base_field in field_mappings:
                display_name = field_mappings[base_field]['display_name']
                clean_data[f'_original_{display_name}'] = {
                    'value': value,
                    'editable': False
                }
            else:
                # Preserve other _original_ fields (like IDs) as-is
                clean_data[key] = {
                    'value': value,
                    'editable': False
                }
    
    return {"status": "success", "clean_data": clean_data}

def get_keys(user_id: str) -> dict:
    query = supabase.table('ddx_keys').select('*').eq('user_id', user_id)
    data, count = query.execute()
    
    if len(data) > 0 and data[1]:
        encrypted_user_key = data[1][0].get('user_key')
        encrypted_firm_key = data[1][0].get('firm_key')
        if encrypted_user_key and encrypted_firm_key:
            return {
                "user_key": decrypt_value(encrypted_user_key),
                "firm_key": decrypt_value(encrypted_firm_key)
            }
    
    logging_start.logger.error("Keys not found for user_id: %s", user_id)
    return None

def compile_data_for_ddx(project_id, user_id, edited_values=None):
    response = get_data_for_ddx(project_id)

    try:
        # Convert numeric fields to strings
        data = response['data']
        
        # Apply any edited values from the frontend
        if edited_values:
            # Convert display names back to API field names
            field_mappings = {
                field.json_schema_extra.get('display_name', field_name): field_name
                for field_name, field in models.DDXImportProject.model_fields.items()
                if field_name != 'authToken'
            }
            
            # Update data with edited values, converting display names back to API field names
            for display_name, value in edited_values.items():
                api_field_name = field_mappings.get(display_name)
                if api_field_name:
                    # Special handling for Use Type - map ID to DDX text value
                    if api_field_name == 'useType1' and isinstance(value, (str, int)):
                        try:
                            use_type_id = int(value)

                            ddx_use_type = get_ddx_mapping_from_enum_id(
                                'enum_project_use_types', 
                                use_type_id, 
                                'ddx_use_type_id', 
                                'ddx_use_types', 
                                'ddx_use_type'
                            )
                            if ddx_use_type:
                                data[api_field_name] = ddx_use_type
                   
                            else:
                                print(f"ERROR: Failed to map use type ID {use_type_id}, keeping original value")
                        except (ValueError, TypeError):
                            print(f"ERROR: Invalid use type ID value: {value}, keeping original value")
                    # Special handling for Energy Code - map ID to DDX text value  
                    elif api_field_name == 'designEnergyCode' and isinstance(value, (str, int)):
                        try:
                            energy_code_id = int(value)
                            ddx_energy_code = get_ddx_mapping_from_enum_id(
                                'enum_energy_codes', 
                                energy_code_id, 
                                'ddx_energy_code_id', 
                                'ddx_energy_codes', 
                                'ddx_energy_code'
                            )
                            if ddx_energy_code:
                                data[api_field_name] = ddx_energy_code
                                
                            else:
                                print(f"ERROR: Failed to map energy code ID {energy_code_id}, keeping original value")
                        except (ValueError, TypeError):
                            print(f"ERROR: Invalid energy code ID value: {value}, keeping original value")
                    # Special handling for Reporting Year and Occupancy Year
                    elif api_field_name in ['reportingYear', 'estimatedOccupancyYear'] and isinstance(value, (str, int)):
                        try:
                            year_value = int(value)
                            data[api_field_name] = str(year_value)
                        except (ValueError, TypeError):
                            print(f"ERROR: Invalid year value: {value}, keeping original value")
                    else:
                        # Remove any formatting (commas and units) before saving
                        if isinstance(value, str):
                            value = value.replace(',', '').replace('kBtu/SF', '').strip()
                        data[api_field_name] = value

        # Convert numeric fields to strings after applying edits
        for field in ['useType1Area', 'baselineEUI', 'predictedEUI', 'reportingYear', 'estimatedOccupancyYear']:
            data[field] = str(data[field])
        
        
        # Call get_keys once and store the result
        keys = get_keys(user_id)
        auth_token = authenticate(keys['firm_key'], keys['user_key'])

        project = models.DDXImportProject(
            authToken=auth_token['authToken'],
            **data
        )
        
        # Convert the complete project object to dict for logging (excluding auth token)
        outbound_request_data = project.model_dump()
        # Remove the auth token before storing
        outbound_request_data.pop('authToken', None)
        
        project_response = import_project(project)
        if project_response['status'] == 'success':
            # Insert successful upload into integrations_sync table with complete outbound request
            insert_api_call_db(project_id, "200", project_response['response'], outbound_request_data)
            logging_start.logger.info(f"Project imported successfully: {project_response['response']['id']}")
            return {"status": "success", "message": "Project imported successfully","ddx_project_id": project_response['response']['id']}
        else:
            insert_api_call_db(project_id, project_response['response_code'], project_response['message'], outbound_request_data)
            logging_start.logger.error(f"Error importing project: {project_response}")
            return {"status": "error", "message": project_response['message']}
    except requests.exceptions.RequestException as e:
        logging_start.logger.error(f"An error occurred: {e}")
        return {"status": "error", "message": f"An error occurred: {e}"}

def update_user_keys(user_id: str, keys: dict) -> dict:
    try:
        query = supabase.table('ddx_keys').select('*').eq('user_id', user_id)
        data, count = query.execute()
        
        if data[1]:
            existing_record = data[1][0]
            update_data = {}
            
            # Update only if the key is provided
            if 'userKey' in keys:
                update_data['user_key'] = encrypt_value(keys['userKey'])
            else:
                update_data['user_key'] = existing_record.get('user_key', '')
            
            if 'firmKey' in keys:
                update_data['firm_key'] = encrypt_value(keys['firmKey'])
            else:
                update_data['firm_key'] = existing_record.get('firm_key', '')
            
            data, count = supabase.table('ddx_keys')\
                .update(update_data)\
                .eq('user_id', user_id)\
                .execute()
        else:
            update_data = {
                'user_id': user_id,
                'user_key': encrypt_value(keys.get('userKey', '')),
                'firm_key': encrypt_value(keys.get('firmKey', ''))
            }
            
            data, count = supabase.table('ddx_keys')\
                .insert(update_data)\
                .execute()
        
        return {"status": "success"}
    except Exception as e:
        logging_start.logger.error(f"Error updating keys: {str(e)}")
        return {"status": "error", "message": str(e)}

def get_key_status(user_id: str) -> dict:
    try:
        query = supabase.table('ddx_keys').select('id,'\
                                                'user_key,'\
                                                'firm_key')
        query = query.eq('user_id', user_id)
        
        data, count = query.execute()
        if data[1]:
            result = data[1][0]
            return {
                'user_id': user_id,
                'user_key': bool(result.get('user_key')),
                'firm_key': bool(result.get('firm_key'))
            }
        else:
            return {
                'user_id': user_id,
                'user_key': False,
                'firm_key': False
            }
    except Exception as e:
        logging_start.logger.error(f"Error getting key status: {str(e)}")
        return {"status": "error", "message": str(e)}
