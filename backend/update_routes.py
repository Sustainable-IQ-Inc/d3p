from fastapi import APIRouter, Depends
import models
from utils import verify_token, add_event_history, supabase
from typing import Optional, Dict, Union
from project_details import get_latest_upload_id, get_latest_eeu_data, get_eeu_fields_data
from weather_location import get_climate_zone_by_zip
from utils import get_enum_id, get_field_name_from_use_type, fuel_category_override
from conversions import check_units_eeu_field
router = APIRouter()

def check_custom_project_id_uniqueness(custom_project_id: str, project_id: str, company_id: str) -> bool:
    """
    Check if the custom_project_id is unique within the company.
    Checks both custom_project_id field and project_id field (in case user enters a UUID).
    Returns True if unique, False if already exists.
    """
    if not custom_project_id or not custom_project_id.strip():
        return True  # Empty custom_project_id is allowed
    
    try:
        # Check in project_energy_summary view for existing projects within the same company
        # Exclude the current project from the check
        projects_response = supabase.table('project_energy_summary')\
            .select('project_id, custom_project_id')\
            .eq('company_id', company_id)\
            .neq('project_id', project_id)\
            .execute()
        
        if projects_response.data:
            trimmed_input = custom_project_id.strip()
            
            for project in projects_response.data:
                # Check if the input matches the custom_project_id
                if project.get('custom_project_id') and project['custom_project_id'].strip() == trimmed_input:
                    return False  # Found duplicate custom_project_id in same company
                
                # Check if the input matches the project_id (UUID)
                if project.get('project_id') and project['project_id'] == trimmed_input:
                    return False  # Found duplicate project_id in same company
        
        return True  # No duplicates found
        
    except Exception as e:
        print(f"Error checking custom_project_id uniqueness: {e}")
        return False  # Assume not unique on error for safety

def update_project_record(item,user_id):
    item_data = item.model_dump(exclude_none=True)
    project_id = item_data.pop('project_id')
    
    # Remove user_id from item_data - it's not a column in projects table, only used for history
    item_data.pop('user_id', None)
    
    print(f"update_project_record called with item_data keys: {list(item_data.keys())}")
    print(f"item_data values: {item_data}")

    # Check custom_project_id uniqueness if it's being updated
    if 'custom_project_id' in item_data:
        try:
            # Get the company_id for this project
            project_response = supabase.table('projects')\
                .select('company_id')\
                .eq('id', project_id)\
                .execute()
            
            if project_response.data:
                company_id = project_response.data[0]['company_id']
                
                # Check if the custom_project_id is unique within the company
                if not check_custom_project_id_uniqueness(item_data['custom_project_id'], project_id, company_id):
                    return "custom_project_id_not_unique"
            else:
                return "project_not_found"
                
        except Exception as e:
            print(f"Error validating custom_project_id: {e}")
            return "validation_error"

    # Fields that need to be synced to uploads table (used by project_energy_summary view)
    # These fields don't exist in projects table, only in uploads table
    fields_to_sync_to_uploads = [
        'project_use_type_id',
        'project_construction_category_id',
        'energy_code_id',
        'project_phase_id',
        'year',
        'reporting_year'
    ]
    
    # Check if any fields that need to be synced to uploads are being updated
    upload_update_data = {k: v for k, v in item_data.items() if k in fields_to_sync_to_uploads}
    print(f"Fields to sync to uploads: {fields_to_sync_to_uploads}")
    print(f"Upload update data found: {upload_update_data}")
    
    # Remove fields that belong in uploads table from item_data (they don't exist in projects table)
    projects_table_data = {k: v for k, v in item_data.items() if k not in fields_to_sync_to_uploads}
    print(f"Projects table data: {projects_table_data}")
    
    # Only update projects table if there are fields that belong there
    if projects_table_data:
        try:
            data, count = supabase.table('projects')\
                .update(projects_table_data)\
                .eq('id', project_id)\
                .execute()
            try:
                for key, value in projects_table_data.items():
                    add_event_history('projects',key,project_id,value,user_id)
            except Exception as e:
                print(e)
                print("error logging history")
        except Exception as e:
            print(e)
            return "error"
    else:
        print("No fields to update in projects table")
    
    # If fields that appear in project_energy_summary view are being updated, also update uploads
    if upload_update_data:
        print(f"Syncing fields to uploads table: {upload_update_data}")
        try:
            # Values are already integers from ProjectUpdate model, pass them through
            print(f"Upload update data to sync: {upload_update_data}")
            
            # Use the baseline and design update function to update both uploads
            upload_update_item = models.UploadUpdate(project_id=project_id, **upload_update_data)
            upload_result = update_upload_record_baseline_and_design(upload_update_item, user_id)
            print(f"Upload update result: {upload_result}")
            if upload_result == "error":
                print(f"ERROR: Failed to update uploads table - no uploads found or all updates failed")
                return "error"
            elif upload_result == "partial":
                print(f"WARNING: Some upload updates failed")
                # Continue anyway, projects table was updated
        except Exception as e:
            print(f"EXCEPTION in updating uploads table: {e}")
            import traceback
            traceback.print_exc()
            return "error"
    
    return "success"
def update_eeu_record(item, user_id,**kwargs):
    item_data = item.model_dump(exclude_none=True)
    eeu_id = item_data.pop('eeu_id')
    energy_field = kwargs.get('energy_field')

    try:
        # Retrieve the current state of the record
        current_data_response = supabase.table('eeu_data')\
            .select('*')\
            .eq('id', eeu_id)\
            .execute()
        
        # Update the record
        update_response = supabase.table('eeu_data')\
            .update(item_data)\
            .eq('id', eeu_id)\
            .execute()
        
        try:
            for key, value in item_data.items():
                # Get the previous value
                previous_value = current_data_response.data[0].get(key) if current_data_response.data else None
                add_event_history('eeu_data', key, eeu_id, value, user_id, previous_value)
        except Exception as e:
            print("error logging history")

    except Exception as e:
        print(e)
        return "error"
    if energy_field is True:
        try:
            first_key_value = next(iter(item_data.keys()))
            run_calcs_eeu(first_key_value, eeu_id)
        except Exception as e:
            print(e)
            return "error"
    
    return "success"

def calculate_total_sum(fields_to_sum,eeu_id):
    try:
        sum_query = supabase.table('eeu_data')\
        .select(','.join(fields_to_sum))\
        .eq('id', eeu_id)\
        .execute()
    
        total_sum = 0
        for record in sum_query.data:
            total_sum += sum(float(record[field]) for field in fields_to_sum if record[field] is not None)
        return {'status': 'success', 'total_sum': total_sum}
    except Exception as e:
        print(e)
        return {'status': 'error'}
    

    
def update_total_value(eeu_id, new_value, **kwargs):
    # Ensure new_value is treated as a number
    new_value = float(new_value)
    fuel_category_value = kwargs.get('fuel_category_value')
    fuel_category_value = fuel_category_override(fuel_category_value)
    if fuel_category_value is not None:
        field_to_update = f'total_{fuel_category_value}'
    else:
        field_to_update = "total_energy"
    try:
        # Update the total for the fuel_category in the eeu_data table
        supabase.table('eeu_data')\
            .update({field_to_update: new_value})\
            .eq('id', eeu_id)\
            .execute()
        return {'status': 'success'}
    except Exception as e:
        print(f"Error updating total for fuel_category {fuel_category_value}: {e}")

def run_calcs_eeu(changed_field_name,eeu_id):
    df_fields = get_eeu_fields_data()
    fuel_category_value = df_fields.loc[df_fields['field_name'] == changed_field_name, 'fuel_category'].values[0].title()
    def update_eeu_data_total(df,eeu_id):
        # Filter fields that contain "total" but are not exactly "total"
        total_fields = ['total_Electricity','total_NaturalGas','total_DistrictHeating','total_Other','total_On-SiteRenewables']
        fields_to_sum = df.loc[df['field_name'].str.contains("total") & (df['field_name'] != "total_energy"), 'field_name'].values
        
        total_sum_result = calculate_total_sum(total_fields,eeu_id)
        if total_sum_result['status'] == 'success':
            # Handle the total sum as needed
            updated = update_total_value(eeu_id,total_sum_result['total_sum'])
            if updated['status'] == 'success':
                return {'status': 'success'}
            else:
                return {'status': 'error'}
        
    def update_eeu_data_fuel_category(fuel_category_value, df, eeu_id):
        
        fields_to_sum = df.loc[
            (df['fuel_category'] == fuel_category_value.lower()) & 
            (~df['field_name'].str.contains("total")), 
            'field_name'
        ].values
        total_sum_fuel_category_type = calculate_total_sum(fields_to_sum,eeu_id)
        if total_sum_fuel_category_type['status'] == 'success':
            total_value = total_sum_fuel_category_type['total_sum']
            
            fuel_category_value = fuel_category_override(fuel_category_value)
            updated = update_total_value(eeu_id,total_value,fuel_category_value=fuel_category_value)
            if updated['status'] == 'success':
                return {'status': 'success'}
            else:
                return {'status': 'error'}
    # Assuming you have the eeu_id available here
    
    update_eeu_data_fuel_category(fuel_category_value, df_fields, eeu_id)
    update_eeu_data_total(df_fields,eeu_id)

def update_upload_record_baseline_and_design(item, user_id):
    """Update ALL baseline and design upload records for the project when fields are edited"""
    item_data = item.model_dump(exclude_none=True)
    project_id = item_data.pop('project_id')
    
    print(f"=== update_upload_record_baseline_and_design called ===")
    print(f"Project ID: {project_id}")
    print(f"Data to update: {item_data}")
    print(f"User ID: {user_id}")
    
    # Get all upload IDs for both baseline and design (update all, not just latest)
    def get_upload_ids_by_type(project_id, baseline_design):
        try:
            print(f"  Searching for {baseline_design} uploads for project {project_id}")
            # First get all uploads for the project
            uploads_query = supabase.table('uploads')\
                .select('id, created_at')\
                .eq('project_id', project_id)\
                .order('created_at', desc=True)
            uploads_response = uploads_query.execute()
            
            print(f"  Total uploads found: {len(uploads_response.data) if uploads_response.data else 0}")
            
            if not uploads_response.data:
                print(f"  No uploads found for project {project_id}")
                return []
            
            upload_ids = []
            # For each upload, check if it has the corresponding baseline_design type
            for upload in uploads_response.data:
                upload_id = upload['id']
                eeu_query = supabase.table('eeu_data')\
                    .select('baseline_design')\
                    .eq('upload_id', upload_id)\
                    .eq('baseline_design', baseline_design)\
                    .limit(1)
                eeu_response = eeu_query.execute()
                
                print(f"    Upload {upload_id}: EEU data for {baseline_design}? {bool(eeu_response.data and len(eeu_response.data) > 0)}")
                
                if eeu_response.data and len(eeu_response.data) > 0:
                    upload_ids.append(upload_id)
            
            print(f"  Found {len(upload_ids)} {baseline_design} upload(s): {upload_ids}")
            return upload_ids
            
        except Exception as e:
            print(f"  ERROR finding {baseline_design} uploads: {e}")
            import traceback
            traceback.print_exc()
            return []

    baseline_upload_ids = get_upload_ids_by_type(project_id, 'baseline')
    design_upload_ids = get_upload_ids_by_type(project_id, 'design')
    
    print(f"Baseline upload IDs: {baseline_upload_ids}, Design upload IDs: {design_upload_ids}")
    
    success_count = 0
    total_attempts = 0
    
    # Update all baseline uploads
    for baseline_upload_id in baseline_upload_ids:
        total_attempts += 1
        try:
            # Retrieve current state
            current_data_response = supabase.table('uploads')\
                .select('*')\
                .eq('id', baseline_upload_id)\
                .execute()
            
            # Update the record
            update_response = supabase.table('uploads')\
                .update(item_data)\
                .eq('id', baseline_upload_id)\
                .execute()
            
            # Verify the update
            verify_data_response = supabase.table('uploads')\
                .select('project_construction_category_id, energy_code_id, updated_at')\
                .eq('id', baseline_upload_id)\
                .execute()
            print(f"Verified baseline upload {baseline_upload_id} after update: {verify_data_response.data[0] if verify_data_response.data else 'No data'}")
            
            # Log history
            try:
                for key, value in item_data.items():
                    previous_value = current_data_response.data[0].get(key) if current_data_response.data else None
                    add_event_history('uploads', key, baseline_upload_id, value, user_id, previous_value)
            except Exception as e:
                print(f"error logging history for baseline upload {baseline_upload_id}: {e}")
                
            success_count += 1
            print(f"Successfully updated baseline upload {baseline_upload_id}")
            
        except Exception as e:
            print(f"Error updating baseline upload {baseline_upload_id}: {e}")
            import traceback
            traceback.print_exc()
    
    # Update all design uploads
    for design_upload_id in design_upload_ids:
        total_attempts += 1
        try:
            # Retrieve current state
            current_data_response = supabase.table('uploads')\
                .select('*')\
                .eq('id', design_upload_id)\
                .execute()
            
            # Update the record
            update_response = supabase.table('uploads')\
                .update(item_data)\
                .eq('id', design_upload_id)\
                .execute()
            
            # Verify the update
            verify_data_response = supabase.table('uploads')\
                .select('project_construction_category_id, energy_code_id, updated_at')\
                .eq('id', design_upload_id)\
                .execute()
            print(f"Verified design upload {design_upload_id} after update: {verify_data_response.data[0] if verify_data_response.data else 'No data'}")
            
            # Log history
            try:
                for key, value in item_data.items():
                    previous_value = current_data_response.data[0].get(key) if current_data_response.data else None
                    add_event_history('uploads', key, design_upload_id, value, user_id, previous_value)
            except Exception as e:
                print(f"error logging history for design upload {design_upload_id}: {e}")
                
            success_count += 1
            print(f"Successfully updated design upload {design_upload_id}")
            
        except Exception as e:
            print(f"Error updating design upload {design_upload_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"Update results: {success_count}/{total_attempts} successful")
    
    if total_attempts == 0:
        return "error"  # No uploads found
    elif success_count == total_attempts:
        return "success"  # All updates successful
    else:
        return "partial"  # Some updates failed

def update_upload_record(item,user_id):
    item_data = item.model_dump(exclude_none=True)
    project_id = item_data.pop('project_id')
    upload_id = get_latest_upload_id(project_id)

    print("here is the send data", item_data)
    
    # Check custom_project_id uniqueness if it's being updated
    if 'custom_project_id' in item_data:
        try:
            # Get the company_id for this project
            project_response = supabase.table('projects')\
                .select('company_id')\
                .eq('id', project_id)\
                .execute()
            
            if project_response.data:
                company_id = project_response.data[0]['company_id']
                
                # Check if the custom_project_id is unique within the company
                if not check_custom_project_id_uniqueness(item_data['custom_project_id'], project_id, company_id):
                    return "custom_project_id_not_unique"
            else:
                return "project_not_found"
                
        except Exception as e:
            print(f"Error validating custom_project_id: {e}")
            return "validation_error"
    
    try:
        # Retrieve the current state of the record
        current_data_response = supabase.table('uploads')\
            .select('*')\
            .eq('id', upload_id)\
            .execute()
        
        # Update the record
        update_response = supabase.table('uploads')\
            .update(item_data)\
            .eq('id', upload_id)\
            .execute()
        
        try:
            for key, value in item_data.items():
                # Get the previous value
                previous_value = current_data_response.data[0].get(key) if current_data_response.data else None
                add_event_history('uploads', key, upload_id, value, user_id, previous_value)
        except Exception as e:
            print("error logging history")
    except Exception as e:
        print(e)
        return "error"
    
    # If GSF was updated, also update the EEU data
    if 'use_type_total_area' in item_data:
        try:
            gsf_value = item_data['use_type_total_area']
            latest_eeu_data = get_latest_eeu_data(project_id)
            if latest_eeu_data['status'] == 'success':
                # Update baseline if it exists
                if latest_eeu_data['latest_baseline'] is not None:
                    eeu_id = latest_eeu_data['latest_baseline']
                    eeu_update = models.EEUUpdate(eeu_id=eeu_id, use_type_total_area=gsf_value)
                    update_eeu_record(eeu_update, user_id)
                
                # Update design if it exists
                if latest_eeu_data['latest_design'] is not None:
                    eeu_id = latest_eeu_data['latest_design']
                    eeu_update = models.EEUUpdate(eeu_id=eeu_id, use_type_total_area=gsf_value)
                    update_eeu_record(eeu_update, user_id)
        except Exception as e:
            print(f"Error updating EEU data for GSF change: {e}")
    
    return "success"


def update_gsf_record(item, user_id):
    """
    Update the GSF (use_type_total_area) for a project and trigger recalculations
    """
    item_data = item.model_dump(exclude_none=True)
    project_id = item_data.pop('project_id')
    gsf_value = item_data.get('use_type_total_area')
    
    if not gsf_value:
        return "error"
    
    try:
        # Get the latest EEU data for this project
        latest_eeu_data = get_latest_eeu_data(project_id)
        if latest_eeu_data['status'] != 'success':
            return "error"
        
        status = "success"
        
        # Update baseline if it exists
        if latest_eeu_data['latest_baseline'] is not None:
            eeu_id = latest_eeu_data['latest_baseline']
            eeu_update = models.EEUUpdate(eeu_id=eeu_id, use_type_total_area=gsf_value)
            result = update_eeu_record(eeu_update, user_id)
            if result != 'success':
                status = 'error'
        
        # Update design if it exists
        if latest_eeu_data['latest_design'] is not None:
            eeu_id = latest_eeu_data['latest_design']
            eeu_update = models.EEUUpdate(eeu_id=eeu_id, use_type_total_area=gsf_value)
            result = update_eeu_record(eeu_update, user_id)
            if result != 'success':
                status = 'error'
        
        return status
        
    except Exception as e:
        print(f"Error updating GSF: {e}")
        return "error"


def process_eeu_update(item, user_id):
    item_data = item.model_dump(exclude_none=True)
    export_data = {}
    new_value = item_data['new_value']
    cell_key = item_data['cell_key']
    current_units = item_data.get('current_units')
    
    def extract_fuel_category(input_string):
        #find the position of the first _
        first_underscore_index = input_string.find('_')
        #take the string from the first character to the first underscore
        latter_portion = input_string[first_underscore_index:]
        #find the position of "baseline" or "design"
        baseline_design_index = latter_portion.find("baseline")
        if baseline_design_index == -1:
            baseline_design_index = latter_portion.find("design")
        #take the string from the first character to the baseline or design
        fuel_category = latter_portion[:baseline_design_index]
        #strip any leading or trailing "_"
        fuel_category = fuel_category.strip("_")

        return fuel_category
    
    def extract_type(input_string):
        # Split the string by the hyphen
        parts = input_string.split('-')
        
        type_portion = parts[0].split('_')[-1]
        
        return type_portion

    def extract_use_type(input_string):
        # Split the string by the hyphen
        parts = input_string.split('-')
        
        # The second part is the portion after the hyphen
        use_type = parts[1] if len(parts) > 1 else ''
        
        return use_type
    def extract_renewables_use_type(input_string):
        # Split the string by the _
        parts = input_string.split('_')
        use_type = parts[1]
        use_type = use_type+" On-Site Renewables"

        return use_type
    #if cell_key contains "renewables":
    if "Renewables" in cell_key:
        fuel_category = "onsite_renewables"
        baseline_design = "design"
        use_type = extract_renewables_use_type(cell_key)
    else:
        fuel_category = extract_fuel_category(cell_key)
        baseline_design = extract_type(cell_key)
        use_type = extract_use_type(cell_key)

    latest_eeu_data = get_latest_eeu_data(item_data['project_id'])
    if latest_eeu_data['status'] == 'success':
        eeu_id = latest_eeu_data.get(f'latest_{baseline_design}')
        if eeu_id is None:
            print(f"Warning: No EEU ID found for {baseline_design}")


    use_type = use_type.replace("_", " ")
    field_name = get_field_name_from_use_type(use_type,fuel_category)

    export_data['eeu_id'] = eeu_id
    new_value = check_units_eeu_field(eeu_id,supabase,new_value,current_units)
    export_data[field_name] = new_value

    
    
    if isinstance(export_data,dict):
        export_data = models.FlexibleModel(**export_data)       
    return export_data
@router.post("/update_project/")
async def create_upload_file(item: models.ProjectUpdate, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
        user_id = authorized['user_id']
        return update_project_record(item,user_id)

@router.post("/update_upload/")
async def create_upload_file(item: models.UploadUpdate, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    user_id = authorized['user_id']
    print("here is the uploaded data", item)
    
    item_data = item.model_dump(exclude_none=True)
    print(f"Item data keys: {list(item_data.keys())}, length: {len(item_data)}")
    
    # Fields that need to update ALL baseline and design uploads (not just latest)
    fields_requiring_all_uploads_update = [
        'project_use_type_id',
        'project_construction_category_id',
        'energy_code_id',
        'project_phase_id',
        'year',
        'reporting_year'
    ]
    
    # Check if any of these fields are being updated
    has_fields_for_all_uploads = any(field in item_data for field in fields_requiring_all_uploads_update)
    
    # If these fields are being updated, update all baseline and design uploads
    if has_fields_for_all_uploads:
        # Filter to only include fields that should update all uploads
        fields_to_update = {k: v for k, v in item_data.items() if k in fields_requiring_all_uploads_update}
        if len(fields_to_update) > 0:
            # Create a new item with only the fields that need to update all uploads
            # UploadUpdate model expects ints, which is what we're receiving
            all_uploads_item = models.UploadUpdate(project_id=item_data['project_id'], **fields_to_update)
            print(f"Using baseline and design update function for fields: {list(fields_to_update.keys())}")
            result = update_upload_record_baseline_and_design(all_uploads_item, user_id)
            
            # If there are other fields that don't need all-uploads update, handle them separately
            other_fields = {k: v for k, v in item_data.items() if k not in fields_requiring_all_uploads_update and k != 'project_id'}
            if other_fields:
                print(f"Also updating other fields with single upload: {list(other_fields.keys())}")
                # Use regular update for other fields (like use_type_total_area, custom_project_id, etc.)
                other_item = models.UploadUpdate(project_id=item_data['project_id'], **other_fields)
                update_upload_record(other_item, user_id)
            
            return result
    
    print("Using regular single upload update function")
    # Use the regular single upload update function
    return update_upload_record(item, user_id)

@router.post("/update_eeu_data/")
async def create_upload_file(item: models.EEUUpdate, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    user_id = authorized['user_id']

    # Check if this is a direct field update (has fields other than new_value and cell_key)
    item_data = item.model_dump(exclude_none=True)
    has_direct_fields = any(field in item_data for field in ['use_type_total_area', 'climate_zone', 'zip_code', 'city', 'state'])
    
    if has_direct_fields:
        # Handle direct field updates without processing through process_eeu_update
        # Get the EEU ID from the project_id
        project_id = item_data.get('project_id')
        if project_id:
            latest_eeu_data = get_latest_eeu_data(project_id)
            if latest_eeu_data['status'] == 'success':
                # Update both baseline and design if they exist
                status = "success"
                
                if latest_eeu_data['latest_baseline'] is not None:
                    eeu_id = latest_eeu_data['latest_baseline']
                    eeu_update = models.EEUUpdate(eeu_id=eeu_id, **{k: v for k, v in item_data.items() if k != 'project_id'})
                    result = update_eeu_record(eeu_update, user_id)
                    if result != 'success':
                        status = 'error'
                
                if latest_eeu_data['latest_design'] is not None:
                    eeu_id = latest_eeu_data['latest_design']
                    eeu_update = models.EEUUpdate(eeu_id=eeu_id, **{k: v for k, v in item_data.items() if k != 'project_id'})
                    result = update_eeu_record(eeu_update, user_id)
                    if result != 'success':
                        status = 'error'
                
                return status
            else:
                return "error"
        else:
            return "error"
    else:
        # Handle cell-based updates through the existing process
        item = process_eeu_update(item, user_id)
        return update_eeu_record(item, user_id, energy_field=True)

@router.post("/update_climate_zone_by_zip/")
async def get_climate_zone_by_zip_api(item: models.ZipUpdate,
                                      authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        zip_response = get_climate_zone_by_zip(item.zip_code)
        if zip_response['status'] == 'success':
            user_id = authorized['user_id']
            climate_zone = zip_response['climate_zone']

            latest_eeu_data = get_latest_eeu_data(item.project_id)
            def execute_update_eeu_record(eeu_id, climate_zone, user_id, zip_code):
                eeu_item = models.EEUUpdate(eeu_id=eeu_id, climate_zone=climate_zone, zip_code=item.zip_code)
                
                try:
                    update_eeu_record(eeu_item,user_id)
                    return {'status': 'success'}
                except Exception as e:
                    print(e)
                    return {"status": "error"}
            status = "success"
            if latest_eeu_data['status'] == 'success':
                if latest_eeu_data['latest_baseline'] is not None:
                    eeu_id = latest_eeu_data['latest_baseline']
                    update_baseline = execute_update_eeu_record(eeu_id, climate_zone, user_id, item.zip_code)
                    if update_baseline['status'] != 'success':
                        status = 'error'
                if latest_eeu_data['latest_design'] is not None:
                    eeu_id = latest_eeu_data['latest_design']
                    update_design = execute_update_eeu_record(eeu_id, climate_zone, user_id, item.zip_code)
                    if update_design['status'] != 'success':
                        status = 'error'
            
            return {'status': status}
        else:
            return "no climate zone found"
    else:
        return "not authorized"

@router.post("/update_gsf/")
async def update_gsf_api(item: models.GSFUpdate, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    user_id = authorized['user_id']
    return update_gsf_record(item, user_id)

