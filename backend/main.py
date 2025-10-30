from fastapi import FastAPI, File, UploadFile, Form, Depends, Request
from typing import Optional, Dict, Union
import os
from supabase import create_client, Client
from fastapi import HTTPException
from fastapi.security import HTTPBearer
import secrets

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


