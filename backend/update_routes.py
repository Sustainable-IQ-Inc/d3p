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
        data, count = supabase.table('projects')\
            .update(item_data)\
            .eq('id', project_id)\
            .execute()
        try:
            for key, value in item_data.items():
                add_event_history('projects',key,project_id,value,user_id)
        except Exception as e:
            print(e)
            print("error logging history")
    except Exception as e:
        print(e)
        return "error"
    
    return "success"
def update_eeu_record(item, user_id,**kwargs):
    item_data = item.model_dump(exclude_none=True)
    eeu_id = item_data.pop('eeu_id')
    energy_field = kwargs.get('energy_field')

    try:
        # Retrieve the current state of the record
        current_data, _ = supabase.table('eeu_data')\
            .select('*')\
            .eq('id', eeu_id)\
            .execute()
        
        # Update the record
        data, count = supabase.table('eeu_data')\
            .update(item_data)\
            .eq('id', eeu_id)\
            .execute()
        
        try:
            for key, value in item_data.items():
                # Get the previous value
                previous_value = current_data[1][0].get(key)
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
    """Update both baseline and design upload records for project_use_type_id changes"""
    item_data = item.model_dump(exclude_none=True)
    project_id = item_data.pop('project_id')
    
    print(f"Updating both baseline and design for project {project_id} with data: {item_data}")
    
    # Get the latest upload IDs for both baseline and design
    def get_latest_upload_id_by_type(project_id, baseline_design):
        try:
            # First get all uploads for the project
            uploads_query = supabase.table('uploads')\
                .select('id, created_at')\
                .eq('project_id', project_id)\
                .order('created_at', desc=True)
            uploads_data, _ = uploads_query.execute()
            
            if not uploads_data[1]:
                print(f"No uploads found for project {project_id}")
                return None
            
            # For each upload, check if it has the corresponding baseline_design type
            for upload in uploads_data[1]:
                upload_id = upload['id']
                eeu_query = supabase.table('eeu_data')\
                    .select('baseline_design')\
                    .eq('upload_id', upload_id)\
                    .eq('baseline_design', baseline_design)\
                    .limit(1)
                eeu_data, _ = eeu_query.execute()
                
                if eeu_data[1] and len(eeu_data[1]) > 0:
                    print(f"Found {baseline_design} upload: {upload_id}")
                    return upload_id
            
            print(f"No {baseline_design} upload found for project {project_id}")
            return None
            
        except Exception as e:
            print(f"Error finding {baseline_design} upload: {e}")
            return None

    baseline_upload_id = get_latest_upload_id_by_type(project_id, 'baseline')
    design_upload_id = get_latest_upload_id_by_type(project_id, 'design')
    
    print(f"Baseline upload ID: {baseline_upload_id}, Design upload ID: {design_upload_id}")
    
    success_count = 0
    total_attempts = 0
    
    # Update baseline upload if it exists
    if baseline_upload_id:
        total_attempts += 1
        try:
            # Retrieve current state
            current_data, _ = supabase.table('uploads')\
                .select('*')\
                .eq('id', baseline_upload_id)\
                .execute()
            
            # Update the record
            data, count = supabase.table('uploads')\
                .update(item_data)\
                .eq('id', baseline_upload_id)\
                .execute()
            
            # Log history
            try:
                for key, value in item_data.items():
                    previous_value = current_data[1][0].get(key)
                    add_event_history('uploads', key, baseline_upload_id, value, user_id, previous_value)
            except Exception as e:
                print("error logging history for baseline")
                
            success_count += 1
            print(f"Successfully updated baseline upload {baseline_upload_id}")
            
        except Exception as e:
            print(f"Error updating baseline upload: {e}")
    
    # Update design upload if it exists
    if design_upload_id:
        total_attempts += 1
        try:
            # Retrieve current state
            current_data, _ = supabase.table('uploads')\
                .select('*')\
                .eq('id', design_upload_id)\
                .execute()
            
            # Update the record
            data, count = supabase.table('uploads')\
                .update(item_data)\
                .eq('id', design_upload_id)\
                .execute()
            
            # Log history
            try:
                for key, value in item_data.items():
                    previous_value = current_data[1][0].get(key)
                    add_event_history('uploads', key, design_upload_id, value, user_id, previous_value)
            except Exception as e:
                print("error logging history for design")
                
            success_count += 1
            print(f"Successfully updated design upload {design_upload_id}")
            
        except Exception as e:
            print(f"Error updating design upload: {e}")
    
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
        current_data, _ = supabase.table('uploads')\
            .select('*')\
            .eq('id', upload_id)\
            .execute()
        
        # Update the record
        data, count = supabase.table('uploads')\
            .update(item_data)\
            .eq('id', upload_id)\
            .execute()
        
        try:
            for key, value in item_data.items():
                # Get the previous value
                previous_value = current_data[1][0].get(key)
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
    
    # Check if this is a project_use_type_id update that should affect both baseline and design
    item_data = item.model_dump(exclude_none=True)
    print(f"Item data keys: {list(item_data.keys())}, length: {len(item_data)}")
    print(f"Has project_use_type_id: {'project_use_type_id' in item_data}")
    
    if 'project_use_type_id' in item_data and len(item_data) <= 3:  # project_id, user_id, project_use_type_id
        print("Using baseline and design update function")
        # Use the baseline and design update function
        return update_upload_record_baseline_and_design(item, user_id)
    else:
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

