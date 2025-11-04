from fastapi import FastAPI, File, UploadFile, Form, Depends, Request
from typing import Optional, Dict, Union
import os
from supabase import create_client, Client
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.responses import StreamingResponse
import secrets
import io
from datetime import datetime

import uvicorn

import pandas as pd
import time
from conversions import convert_units_in_table
import models
from update_routes import router as update_router
from upload_routes import router as upload_router
from project_details import return_project_details, get_signed_url_from_project_id, get_energy_end_uses_chart_data, combine_end_uses_data, get_change_history
from operational_data import operational_carbon_data, operational_energy_data
from weather_location import get_climate_zone_by_zip
from external.ddx_api import get_data_for_ddx, clean_field_names, compile_data_for_ddx, update_user_keys, get_key_status, authenticate, get_keys
from external.ddx_pre_validation import validate_ddx_data, create_validation_summary_response, DDXPreValidator, ValidationRule, ValidationSeverity




from utils import return_enum_vals, get_enum_id, add_event_history, verify_token, supabase, create_app, url



app = create_app()
app.include_router(update_router)
app.include_router(upload_router)

security = HTTPBearer()

@app.get("/wake-up/")
async def submit_project(authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    return "success"

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()


    response = await call_next(request)
    return response

@app.post("/submit_project/")
async def submit_project(item: models.SubmitProject, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    

    if authorized['is_authorized']:
    
        # Convert the item to a dictionary
        item_data = item.model_dump()
        
        item_data.setdefault('design_eeu_id', None)
        item_data.setdefault('energy_code_id', None)

        extract_dict = {}

        if 'baseline_eeu_id' in item_data:
            extract_dict['baseline_eeu_id'] = item_data.pop('baseline_eeu_id')

        if 'design_eeu_id' in item_data:
            extract_dict['design_eeu_id'] = item_data.pop('design_eeu_id')
        def update_eeu_record(extract_dict, upload_id):
            
            try:
                data, count = supabase.table('eeu_data')\
                    .update(extract_dict)\
                    .eq('id', extract_dict['id'])\
                    .execute()
            except Exception as e:
                print(e)
                return "error eeu table"
            return "success"

        try:
            data, count = supabase.table('uploads')\
                .insert(item_data)\
                .execute()
        except Exception as e:
            print(e)
            return "error upload table"
        
        if extract_dict.get('baseline_eeu_id') is not None:
            eeu_data_dict  = dict()
            eeu_data_dict['id'] = extract_dict['baseline_eeu_id']
            eeu_data_dict['upload_id'] = data[1][0]['id']
            
            update_eeu_record(eeu_data_dict, eeu_data_dict['id'])
            
        if extract_dict.get('design_eeu_id') is not None:
            eeu_data_dict  = dict()
            eeu_data_dict['id'] = extract_dict['design_eeu_id']
            eeu_data_dict['upload_id'] = data[1][0]['id']
            update_eeu_record(eeu_data_dict, eeu_data_dict['id'])

        return "success"

    else:
        return "not authorized"
    
@app.post("/create_company/")
async def create_company(item: models.CreateCompany, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized'] and authorized['role'] == 'superadmin':
        # Convert the item to a dictionary
        item_data = item.model_dump()
        print(item_data)
        try:
            data, count = supabase.table('companies')\
                .insert(item_data)\
                .execute()
        except Exception as e:
            print(e)
            return "error"

        return "success"
    else:
        return "not authorized"
    
@app.post("/invite_user/")
async def invite_user(item: models.InviteUser,
                      authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        # Convert the item to a dictionary
        item_data = item.model_dump()
        print(item_data)
        company_id = item_data['company_id']
        query = supabase.table('companies')\
            .select('company_name')\
            .eq('id', company_id)
        
        data, count = query.execute()
        
        if data[1] != []:
            df = pd.DataFrame(data[1])
            print("company_name found:")
            company_name =  df.loc[0,'company_name']
        else:
            company_name =  ""
            #invite user to supabase
        try:
            key = os.getenv("SUPABASE_SERVICE_ROLE")
            supabase_admin = create_client(url, key)
            
            # Get the frontend URL from environment variable, fallback to production
            frontend_url = os.getenv("REDIRECT_URL")
            redirect_url = f"{frontend_url}/auth/confirm"
            
            print(f"Sending invite with redirect URL: {redirect_url}")

            data = supabase_admin.auth.admin.invite_user_by_email(item_data['user_email'],
                                                            options={"data":{"company_id":company_id,
                                                                             "company_name":company_name},
                                                                     'redirect_to': redirect_url})

        except Exception as e:
            print(e)

            if str(e) == "A user with this email address has already been registered":
                raise HTTPException(status_code=409, detail=str(e))
            
            
            if str(e) == "An email address is required":
                raise HTTPException(status_code=400, detail=str(e))
            return {"error": str(e)}
        
        return "success"
    else:
        return "not authorized"


@app.post("/create_project/")
async def create_project(item: models.CreateProject, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):

    if authorized['is_authorized']:
        item_data = item.model_dump()

        try:
            data, count = supabase.table('projects')\
                .insert(item_data)\
                .execute()
        except Exception as e:
            print(e)
            return "error"
        #return the id of the new project
        return {'status':'success','id':data[1][0]['id']}
    else:
        return "not authorized"


@app.get("/enums/{enum_name}/")
async def get_simple_enum(enum_name: str, 
                          use_type_id: Optional[int] = None, 
                          authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        print("additional_fields")
        #print(additional_fields)
        args = {'use_type_id': use_type_id} if use_type_id is not None else {}
        return return_enum_vals(enum_name, **args)
    
@app.get("/projects/")
async def get_projects(company_id: Optional[str] = None, 
                       project_id: Optional[str] = None, 
                       basic_info: Optional[bool] = False, 
                       measurement_system: Optional[str] = 'imperial',
                       authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        try:
            if basic_info:
                if authorized['role'] == 'superadmin':
                    company_id = company_id
                else:
                    company_id = authorized['company_id']


                query = supabase.table('projects').select('id,'\
                                                        'project_name')
                query = query.eq('company_id', company_id)
                
                data, count = query.execute()
                if data[1] != []:
                    return data[1]
                else:
                    return None
                
            else:
                query = supabase.table('project_energy_summary')\
                    .select('*')
            
            ## if the user is a superadmin, then the passed company_id is used
            if authorized['role'] == 'superadmin':
                company_id = company_id
            else:
                company_id = authorized['company_id']

            if company_id is not None:
                query = query.eq('company_id', company_id)
            
            if project_id is not None:
                query = query.eq('project_id', project_id)
            
            data, count = query.execute()
            
            if data[1] != []:
                if measurement_system == 'Imperial':
                    data_output = data[1]
                    #data_output = add_operational_carbon_calcs(data_output)
                else:
                    data_output = convert_units_in_table(data[1],'project_energy_summary','metric',supabase)
                data_with_id = [{'id': i, **d} for i, d in enumerate(data_output, start=1)]
                return data_with_id
            else:
                return None
        except Exception as e:
            print(e)
            return "error"
    else:
        return "not authorized"

@app.get("/project_details/")
async def get_projects(project_id: str = None, 
                       measurement_system: Optional[str] = 'imperial',
                       output_units: Optional[str] = 'kbtu/sf',
                       authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        return combine_end_uses_data(project_id, output_units)
    else:
        return "not authorized"

@app.get("/project_energy_end_uses/")
async def get_projects(project_id: str = None, measurement_system: Optional[str] = 'imperial',
                       baseline_design: str = None,
                       authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        chart_data = get_energy_end_uses_chart_data(project_id)
        return chart_data
    else:
        return "not authorized"
    

@app.get("/report_download_url/")
async def get_projects(project_id: str = None, 
                       baseline_design: str = None,
                       authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        return get_signed_url_from_project_id(project_id,baseline_design)
    else:
        return "not authorized"

    



@app.get("/uploads/")
async def get_uploads(project_id: int,authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        query = supabase.table('uploads')\
            .select('*,\
                    eeu_data(*)')\
            .eq('project_id', project_id)
        
        data, count = query.execute()
        
        if data[1] != []:
            return data[1]
        else:
            return "no results"
    else:
        return "not authorized" 
    

@app.get("/companies/")
async def get_companies(authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized'] and authorized['role'] == 'superadmin':
        query = supabase.table('companies')\
            .select('id,company_name')\
        
        data, count = query.execute()
        
        if data[1] != []:
            return data[1]
        else:
            return "no results"
    else:
        return "not authorized" 
    
@app.get("/companies/{company_id}")
async def get_company(company_id: str, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    print("=== GET COMPANY ENDPOINT DEBUG ===")
    print(f"Received company_id: {company_id}")
    print(f"Authorized: {authorized['is_authorized']}")
    print(f"Role: {authorized.get('role', 'N/A')}")
    
    if authorized['is_authorized'] and authorized['role'] == 'superadmin':
        query = supabase.table('companies')\
            .select('id,company_name')\
            .eq('id', company_id)
        
        data, count = query.execute()
        print(f"Query result: {data[1]}")
        
        if data[1] != []:
            print(f"Returning company: {data[1][0]}")
            return data[1][0]
        else:
            print(f"No results found for company_id: {company_id}")
            return {"error": "no results"}
    else:
        print("Not authorized to access this endpoint")
        return {"error": "not authorized"} 
    
@app.get("/company_users/")
async def get_uploads(company_id: str,authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized'] and authorized['role'] == 'superadmin':
        print(f"=== GET COMPANY USERS DEBUG ===")
        print(f"Requested company_id: {company_id}")
        
        query = supabase.table('profiles')\
            .select('email')\
            .eq('company_id', company_id)
        
        data, count = query.execute()
        
        print(f"Query result: {data[1]}")
        print(f"Number of users found: {len(data[1]) if data[1] else 0}")
        
        if data[1] != []:
            return data[1]
        else:
            return []  # Return empty array instead of "no results"
    else:
        return {"error": "not authorized"} 

@app.get("/operational_data/")
async def get_projects(project_id: str = None,
                       authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    
    if authorized['is_authorized']:
        operational_output = operational_carbon_data(project_id)
        if operational_output['status'] != "success":
            return {"status":"no operational data found"}

        

        return operational_output
    else:
        return "not authorized"



@app.get("/project_change_history/")
async def get_change_history_api(project_id: str, 
                                 authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        return get_change_history(project_id)
    else:
        return "not authorized"
    

@app.get("/ddx_data/")
async def get_ddx_data(project_id: str, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:

        response = get_data_for_ddx(project_id)
        if response['status'] == "success":
            clean_data = clean_field_names(response['data'])
            return clean_data
        else:
            return response
    else:
        return "not authorized"
    

@app.post("/export_project_to_ddx/")
async def export_project_to_ddx(item: models.ExportProjectToDDX, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        user_id = authorized['user_id']
        return compile_data_for_ddx(item.project_id, user_id, item.edited_values)
    else:
        return "not authorized"
    


@app.get("/ddx_keys/status/{user_id}")
async def get_key_status_endpoint(user_id: str, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        result = get_key_status(user_id)
        if "status" in result and result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return result
    else:
        raise HTTPException(status_code=401, detail="Not authorized")

@app.post("/ddx_keys/update/{user_id}")
async def update_keys(
    user_id: str, 
    keys: Dict[str, str], 
    authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token),
    request: Request = None
):
    if not authorized['is_authorized']:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    # Validate that the user is updating their own keys
    if authorized['user_id'] != user_id:
        raise HTTPException(status_code=403, detail="Cannot update keys for other users")

    # Basic server-side validation
    for key_name, key_value in keys.items():
        if key_value and len(key_value) < 8:
            raise HTTPException(status_code=400, detail=f"{key_name} must be at least 8 characters")

    result = update_user_keys(user_id, keys)
    if result["status"] == "success":
        return result
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.get("/ddx_keys/authenticate/{user_id}")
async def authenticate_ddx_user(user_id: str, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if not authorized['is_authorized'] or authorized['user_id'] != user_id:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    try:
        keys = get_keys(user_id)
        if not keys:
            return {"status": "error", "message": "DDX API keys not found. Please add them on the Settings Page"}
            
        auth_result = authenticate(keys['firm_key'], keys['user_key'])
        if 'authToken' in auth_result:
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Invalid DDX credentials", "keys": keys}
    except Exception as e:
        if repr(e) == "InvalidToken()":
            return {"status": "error", "message": "Invalid DDX credentials. Please update them on the Settings page."}
        return {"status": "error", "message": repr(e)}

@app.get("/ddx_integration_status/{project_id}")
async def get_ddx_integration_status(project_id: str, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        try:
            query = supabase.table('integrations_sync')\
                .select('created_at, response_code')\
                .eq('project_id', project_id)\
                .eq('response_code', '200')\
                .order('created_at', desc=True)\
                .limit(1)
            
            data, count = query.execute()
            
            if data[1] and len(data[1]) > 0:
                # Project has been successfully shared with DDX
                last_sync = data[1][0]['created_at']
                return {
                    "status": "success",
                    "has_been_shared": True,
                    "last_sync_date": last_sync
                }
            else:
                # Project has not been successfully shared with DDX
                return {
                    "status": "success", 
                    "has_been_shared": False,
                    "last_sync_date": None
                }
        except Exception as e:
            print(f"Error getting DDX integration status: {e}")
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "not authorized"}

@app.post("/ddx_integration_status_batch/")
async def get_ddx_integration_status_batch(
    project_ids: models.ProjectIdsList, 
    authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)
):
    if authorized['is_authorized']:
        try:
            # Get the latest successful sync for each project
            query = supabase.table('integrations_sync')\
                .select('project_id, created_at, response_code')\
                .in_('project_id', project_ids.project_ids)\
                .eq('response_code', '200')\
                .order('created_at', desc=True)
            
            data, count = query.execute()
            
            # Group by project_id and get the latest sync for each
            project_status = {}
            for project_id in project_ids.project_ids:
                project_status[project_id] = {
                    "has_been_shared": False,
                    "last_sync_date": None
                }
            
            if data[1]:
                # Create a dict to track the latest sync for each project
                latest_syncs = {}
                for record in data[1]:
                    project_id = record['project_id']
                    if project_id not in latest_syncs or record['created_at'] > latest_syncs[project_id]['created_at']:
                        latest_syncs[project_id] = record
                
                # Update status for projects that have been shared
                for project_id, record in latest_syncs.items():
                    project_status[project_id] = {
                        "has_been_shared": True,
                        "last_sync_date": record['created_at']
                    }
            
            return {
                "status": "success",
                "project_status": project_status
            }
        except Exception as e:
            print(f"Error getting batch DDX integration status: {e}")
            return {"status": "error", "message": str(e)}
    else:
        return {"status": "error", "message": "not authorized"}

@app.post("/ddx_pre_validation/")
async def run_ddx_pre_validation(
    item: models.ExportProjectToDDX, 
    authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)
):
    """
    Run pre-validation on DDX data before export.
    Returns validation results with warnings and errors.
    """
    if not authorized['is_authorized']:
        return {"status": "error", "message": "not authorized"}
    
    try:
        user_id = authorized['user_id']
        
        # Get the DDX data for the project
        ddx_response = get_data_for_ddx(item.project_id)
        if ddx_response['status'] != "success":
            return {"status": "error", "message": "Could not retrieve project data for validation"}
        
        data = ddx_response['data']
        print("DEBUG: Raw DDX data:", data)
        
        # Apply any edited values from the frontend
        if item.edited_values:
            print("DEBUG: Applying edited values:", item.edited_values)
            for key, value in item.edited_values.items():
                # Convert display names back to API field names if needed
                # (This mirrors the logic in compile_data_for_ddx)
                field_mappings = {
                    field.json_schema_extra.get('display_name', field_name): field_name
                    for field_name, field in models.DDXImportProject.model_fields.items()
                    if field_name != 'authToken'
                }
                
                api_field_name = field_mappings.get(key, key)
                if isinstance(value, str):
                    value = value.replace(',', '').replace('kBtu/SF', '').replace('ft2', '').strip()
                data[api_field_name] = value
        
        print("DEBUG: Data after applying edits:", data)
        print("DEBUG: reportingYear in data:", data.get('reportingYear', 'NOT_FOUND'))
        print("DEBUG: reportingYear type:", type(data.get('reportingYear', 'NOT_FOUND')))
        
        # Run validation with default rules only
        validation_result = validate_ddx_data(data)
        
        # Format response for frontend
        response = create_validation_summary_response(validation_result)
        
        return response
        
    except Exception as e:
        print(f"Error in DDX pre-validation: {str(e)}")
        return {
            "status": "error", 
            "message": f"Validation failed: {str(e)}"
        }


@app.post("/export_projects_csv/")
async def export_projects_csv(
    request_body: models.ExportProjectsCSVRequest,
    authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)
):
    """
    Export project data in the same format as the multi-project Excel template.
    Can export either a single project (project_id) or all projects for a company (company_id).
    Respects measurement system preference (Imperial/Metric).
    """
    if not authorized['is_authorized']:
        return "not authorized"
    
    try:
        # Extract parameters from request body
        company_id = request_body.company_id
        project_id = request_body.project_id
        search_term = request_body.search_term
        measurement_system = request_body.measurement_system or 'imperial'
        from project_details import get_latest_eeu_data, get_uploads_for_project, get_upload_data
        from weather_location import get_location_data
        from conversions import convert_sf_to_m2, convert_gj_to_mbtu
        from datetime import datetime
        
        # Define energy fields matching the template
        eeu_energy_fields = [
            'Heating_Electricity', 'Heating_NaturalGas', 'Heating_DistrictHeating', 'Heating_Other',
            'Cooling_Electricity', 'Cooling_DistrictHeating', 'Cooling_Other',
            'DHW_Electricity', 'DHW_NaturalGas', 'DHW_DistrictHeating', 'DHW_Other',
            'Interior Lighting_Electricity', 'Exterior Lighting_Electricity', 'Plug Loads_Electricity',
            'Process Refrigeration_Electricity', 'Fans_Electricity', 'Pumps_Electricity', 'Pumps_NaturalGas',
            'Heat Rejection_Electricity', 'Humidification_Electricity', 'HeatRecovery_Electricity', 'HeatRecovery_Other',
            'ExteriorUsage_Electricity', 'ExteriorUsage_NaturalGas', 'OtherEndUse_Electricity', 'OtherEndUse_NaturalGas', 'OtherEndUse_Other',
            'SolarDHW_On-SiteRenewables', 'SolarPV_On-SiteRenewables', 'Wind_On-SiteRenewables', 'Other_On-SiteRenewables'
        ]
        
        # Build query for project_energy_summary
        query = supabase.table('project_energy_summary').select('*')
        
        # Handle company_id authorization
        if authorized['role'] == 'superadmin':
            if company_id is not None:
                query = query.eq('company_id', company_id)
        else:
            company_id = authorized['company_id']
            query = query.eq('company_id', company_id)
        
        # Filter by project_id if provided (single project export)
        if project_id is not None:
            query = query.eq('project_id', project_id)
        # Filter by search_term if provided (search-based export from dashboard)
        elif search_term and search_term.strip():
            # Search across relevant text fields in project_energy_summary
            search_term_clean = f'%{search_term.strip()}%'
            # Use or_() with multiple conditions
            query = query.or_(f'project_name.ilike.{search_term_clean},project_use_type.ilike.{search_term_clean},project_phase.ilike.{search_term_clean},climate_zone.ilike.{search_term_clean}')
        
        data, count = query.execute()
        
        if not data[1] or len(data[1]) == 0:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Normalize measurement system for comparison
        measurement_system_lower = measurement_system.lower() if measurement_system else 'imperial'
        is_metric = measurement_system_lower == 'metric'
        
        # Process each project to match template format
        export_rows = []
        
        for project_summary in data[1]:
            try:
                proj_id = project_summary.get('project_id')
                if not proj_id:
                    continue
                
                # Get latest eeu_data for baseline and design
                try:
                    latest_eeu = get_latest_eeu_data(proj_id)
                    if not isinstance(latest_eeu, dict):
                        latest_eeu = {}
                    baseline_id = latest_eeu.get('latest_baseline')
                    design_id = latest_eeu.get('latest_design')
                except Exception as e:
                    print(f"Error getting latest eeu_data for project {proj_id}: {e}")
                    baseline_id = None
                    design_id = None
                
                # Fetch baseline and design eeu_data
                baseline_data = {}
                design_data = {}
                location_data = {}
                upload_data = {}
                
                if baseline_id:
                    try:
                        eeu_query = supabase.table('eeu_data').select('*').eq('id', baseline_id).limit(1)
                        eeu_resp, _ = eeu_query.execute()
                        if eeu_resp and len(eeu_resp) > 1 and eeu_resp[1]:
                            baseline_data = eeu_resp[1][0]
                    except Exception as e:
                        print(f"Error fetching baseline eeu_data for project {proj_id}: {e}")
                        baseline_data = {}
                
                if design_id:
                    try:
                        eeu_query = supabase.table('eeu_data').select('*').eq('id', design_id).limit(1)
                        eeu_resp, _ = eeu_query.execute()
                        if eeu_resp and len(eeu_resp) > 1 and eeu_resp[1]:
                            design_data = eeu_resp[1][0]
                    except Exception as e:
                        print(f"Error fetching design eeu_data for project {proj_id}: {e}")
                        design_data = {}
                
                # Get location data (prefer design, fallback to baseline)
                location_id = design_id or baseline_id
                if location_id:
                    try:
                        location_data = get_location_data(location_id)
                        if not isinstance(location_data, dict):
                            location_data = {}
                    except Exception as e:
                        print(f"Error getting location data for project {proj_id}: {e}")
                        location_data = {}
                
                # Get upload data for additional fields
                try:
                    uploads = get_uploads_for_project(proj_id)
                    if uploads and len(uploads) > 0:
                        upload_id = uploads[-1]['id']
                        upload_data = get_upload_data(upload_id)
                        if not isinstance(upload_data, dict):
                            upload_data = {}
                except Exception as e:
                    print(f"Error getting upload data for project {proj_id}: {e}")
                    upload_data = {}
                
                # Build row matching template format
                row = {}
                
                # Project ID - use custom_project_id if available, otherwise use project_id (same as DDX export)
                custom_id = upload_data.get('custom_project_id') if isinstance(upload_data, dict) else None
                row['project_id'] = str(custom_id) if custom_id else str(proj_id)
                
                # Shared fields (non-energy)
                row['project_name'] = project_summary.get('project_name', '')
                
                # Handle area - convert if metric
                conditioned_area = project_summary.get('conditioned_area')
                if conditioned_area is not None:
                    try:
                        if is_metric:
                            row['conditioned_area_sf'] = convert_sf_to_m2(float(conditioned_area))
                        else:
                            row['conditioned_area_sf'] = float(conditioned_area)
                    except (ValueError, TypeError):
                        row['conditioned_area_sf'] = ''
                else:
                    row['conditioned_area_sf'] = ''
                
                # Get zip_code, city, state from location_data (DDX-style)
                row['zip_code'] = str(location_data.get('zip_code', '')) if location_data.get('zip_code') else ''
                row['city'] = str(location_data.get('city', '')) if location_data.get('city') else ''
                row['state'] = str(location_data.get('state', '')) if location_data.get('state') else ''
                row['country'] = 'United States'  # Default as per DDX export
                
                row['project_use_type'] = project_summary.get('project_use_type', '')
                row['project_construction_category'] = project_summary.get('project_construction_category_name', '')
                row['project_phase'] = project_summary.get('project_phase', '')
                row['energy_code'] = project_summary.get('energy_code_name', '')
                row['report_type'] = project_summary.get('report_type_name', '')
                
                # Reporting year - from upload_data
                if upload_data.get('reporting_year'):
                    row['reporting_year'] = str(upload_data.get('reporting_year'))
                elif upload_data.get('year'):
                    row['reporting_year'] = str(upload_data.get('year'))
                else:
                    row['reporting_year'] = str(datetime.now().year)
                
                # Estimated occupancy year (DDX field)
                if upload_data.get('year'):
                    row['estimated_occupancy_year'] = str(upload_data.get('year'))
                else:
                    row['estimated_occupancy_year'] = str(datetime.now().year)
                
                # Area units
                row['area_units'] = 'sm' if is_metric else 'sf'
                
                # Climate zone - extract just the code (before ' - ')
                climate_zone_full = project_summary.get('climate_zone')
                if climate_zone_full and isinstance(climate_zone_full, str):
                    if ' - ' in climate_zone_full:
                        row['climate_zone'] = climate_zone_full.split(' - ')[0]
                    else:
                        row['climate_zone'] = climate_zone_full
                else:
                    row['climate_zone'] = ''
                
                # Energy units - from eeu_data, default to mbtu
                energy_units = 'mbtu'
                if isinstance(design_data, dict) and design_data.get('energy_units'):
                    energy_units = design_data.get('energy_units')
                elif isinstance(baseline_data, dict) and baseline_data.get('energy_units'):
                    energy_units = baseline_data.get('energy_units')
                row['energy_units'] = energy_units
                
                # DDX additional fields
                # Baseline EUI
                baseline_eui = project_summary.get('total_energy_per_unit_area_baseline')
                if baseline_eui is not None:
                    row['baseline_eui'] = float(baseline_eui)
                else:
                    row['baseline_eui'] = ''
                
                # Predicted/Design EUI
                design_eui = project_summary.get('total_energy_per_unit_area_design')
                if design_eui is not None:
                    row['predicted_eui'] = float(design_eui)
                else:
                    row['predicted_eui'] = ''
                
                # Add all energy fields with baseline and design suffixes
                for energy_field in eeu_energy_fields:
                    # Baseline value
                    baseline_value = baseline_data.get(energy_field) if isinstance(baseline_data, dict) else None
                    if baseline_value is not None:
                        try:
                            # Convert to MBTU if needed
                            if energy_units == 'gj':
                                row[f'{energy_field}_baseline'] = convert_gj_to_mbtu(float(baseline_value))
                            elif energy_units == 'kbtu' or energy_units == 'kbtu/sf':
                                row[f'{energy_field}_baseline'] = float(baseline_value) / 1000.0  # Convert kBtu to MBtu
                            else:
                                row[f'{energy_field}_baseline'] = float(baseline_value)
                        except (ValueError, TypeError):
                            row[f'{energy_field}_baseline'] = 0.0
                    else:
                        row[f'{energy_field}_baseline'] = 0.0
                    
                    # Design value
                    design_value = design_data.get(energy_field) if isinstance(design_data, dict) else None
                    if design_value is not None:
                        try:
                            # Convert to MBTU if needed
                            if energy_units == 'gj':
                                row[f'{energy_field}_design'] = convert_gj_to_mbtu(float(design_value))
                            elif energy_units == 'kbtu' or energy_units == 'kbtu/sf':
                                row[f'{energy_field}_design'] = float(design_value) / 1000.0  # Convert kBtu to MBtu
                            else:
                                row[f'{energy_field}_design'] = float(design_value)
                        except (ValueError, TypeError):
                            row[f'{energy_field}_design'] = 0.0
                    else:
                        row[f'{energy_field}_design'] = 0.0
                
                export_rows.append(row)
            except Exception as e:
                print(f"Error processing project {project_summary.get('project_id', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                # Continue with next project instead of failing entirely
                continue
        
        if not export_rows:
            raise HTTPException(status_code=404, detail="No project data could be exported")
        
        # Create DataFrame with proper column order matching template
        shared_fields = [
            'project_id', 'project_name', 'conditioned_area_sf', 'zip_code', 'city', 'state', 'country',
            'project_use_type', 'project_construction_category', 'project_phase', 'energy_code', 'report_type',
            'reporting_year', 'estimated_occupancy_year', 'area_units', 'climate_zone', 'energy_units',
            'baseline_eui', 'predicted_eui'
        ]
        
        # Build column order: shared fields, then baseline energy fields, then design energy fields
        column_order = shared_fields.copy()
        for field in eeu_energy_fields:
            column_order.append(f'{field}_baseline')
        for field in eeu_energy_fields:
            column_order.append(f'{field}_design')
        
        # Create DataFrame
        df = pd.DataFrame(export_rows)
        
        # Ensure all columns exist (fill missing with empty/0)
        for col in column_order:
            if col not in df.columns:
                df[col] = 0.0 if col.endswith('_baseline') or col.endswith('_design') else ''
        
        # Reorder columns to match template
        df = df[column_order]
        
        # Create CSV in memory
        output = io.StringIO()
        df.to_csv(output, index=False)
        csv_content = output.getvalue()
        
        # Determine filename
        if project_id:
            try:
                project_query = supabase.table('projects').select('project_name').eq('id', project_id).limit(1)
                project_data, _ = project_query.execute()
                project_name = project_data[1][0]['project_name'] if project_data[1] else 'project'
                project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '-')
                filename = f"d3p-project-{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
            except:
                filename = f"d3p-project-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        else:
            filename = f"d3p-portfolio-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"
        
        # Create StreamingResponse
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error exporting projects CSV: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@app.delete("/projects/{project_id}/")
async def delete_project(project_id: str, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if not authorized['is_authorized'] or authorized.get('role') != 'superadmin':
        return "not authorized"

    try:
        # 1) Gather uploads for the project
        uploads_resp, uploads_count = supabase.table('uploads')\
            .select('id')\
            .eq('project_id', project_id)\
            .execute()

        upload_ids = [row['id'] for row in (uploads_resp[1] or [])]

        # Helper to chunk lists for in() queries
        def chunk_list(values, size=1000):
            for i in range(0, len(values), size):
                yield values[i:i+size]

        # 2) Delete eeu_data by upload_id first (FK to uploads)
        if upload_ids:
            for chunk in chunk_list(upload_ids):
                try:
                    supabase.table('eeu_data')\
                        .delete()\
                        .in_('upload_id', chunk)\
                        .execute()
                except Exception as e:
                    print(f"Error deleting eeu_data for chunk: {e}")

        # 3) Delete uploads by id
        if upload_ids:
            for chunk in chunk_list(upload_ids):
                try:
                    supabase.table('uploads')\
                        .delete()\
                        .in_('id', chunk)\
                        .execute()
                except Exception as e:
                    print(f"Error deleting uploads for chunk: {e}")

        # 4) Finally delete the project row
        supabase.table('projects')\
            .delete()\
            .eq('id', project_id)\
            .execute()

        return { 'status': 'success' }
    except Exception as e:
        print(f"Error deleting project {project_id}: {e}")
        return { 'status': 'error', 'message': 'Failed to delete project and related data' }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        reload_dirs=["backend"]
    )


