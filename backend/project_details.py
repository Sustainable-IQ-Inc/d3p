from utils import supabase
import pandas as pd
from functools import lru_cache
from pandas import json_normalize
from gcs_upload import get_signed_url_from_url
from utils import sanitize_filename, enum_list, return_enum_value
from conversions import convert_units_in_table, convert_mbtu_to_kbtu_per_sf, convert_mbtu_to_kbtu_df, convert_mbtu_to_gj_df, convert_gj_to_mbtu
import json
import uuid

list_energy_types = ['electricity', 'fossil_fuels', 'district','other']
list_onsite_renewables = ['SolarPV_On-SiteRenewables','SolarDHW_On-SiteRenewables','Wind_On-SiteRenewables','Other_On-SiteRenewables']
def get_uploads_for_project(project_id):
    query = supabase.table('uploads')\
                        .select('id')\
                        .eq('project_id', project_id)
    data, count = query.execute()
    return data[1]

def get_upload_data(upload_id):
    query = supabase.table('uploads')\
                        .select('enum_project_phases(name),enum_energy_codes(name),year,reporting_year,enum_project_use_types(name),project_use_type_id,custom_project_id,project_phase_id,energy_code_id')\
                        .eq('id', upload_id)
    data, count = query.execute()
    return data[1][0]

def get_eeu_data_ids_for_uploads(upload_ids):
    if not isinstance(upload_ids, list):
        upload_ids = [upload_ids]  # Ensure it's a list

    all_data = []
    for upload_id in upload_ids:
        query = supabase.table('eeu_data')\
                            .select('id')\
                            .eq('upload_id', upload_id)
        data, count = query.execute()
        # Extract 'id' from each entry and add to all_data
        all_data.extend([entry['id'] for entry in data[1]])

    return all_data

def get_latest_upload_id(project_id):
    query = supabase.table('uploads')\
                        .select('id')\
                        .eq('project_id', project_id)\
                        .order('created_at', desc=True)\
                        .limit(1)
    data, count = query.execute()
    return data[1][0]['id']  # Return just the value of the id
def get_latest_eeu_data(project_id, **kwargs):
    def default_response(project_name: str = ""):
        return {
            "status": "success",
            "latest_eeu_data": [],
            "latest_baseline": None,
            "latest_design": None,
            "project_name": project_name
        }

    # Validate project_id to avoid sending invalid UUIDs to PostgREST
    if project_id is None or str(project_id).strip().lower() in ("", "none"):
        return default_response()
    try:
        uuid.UUID(str(project_id))
    except Exception:
        return default_response()

    query = supabase.table('uploads')\
                        .select('id,project_id,eeu_data(id,created_at,baseline_design),projects(project_name)')\
                        .eq('project_id', project_id)

    data, count = query.execute()

    # Short-circuit if no rows
    if count == 0 or not data[1]:
        return default_response()

    # Extract project_name safely
    project_name = ""
    try:
        for row in data[1]:
            proj = row.get('projects') if isinstance(row, dict) else None
            if proj and isinstance(proj, dict) and proj.get('project_name'):
                project_name = proj.get('project_name')
                break
    except Exception:
        project_name = ""

    # Normalize the JSON data with a prefix for the metadata
    df = pd.json_normalize(data[1], 'eeu_data', ['id', 'project_id'], meta_prefix='parent_')

    # Fallback path: if nested relationship returns no eeu_data, fetch via separate queries
    if df.empty:
        try:
            # Fetch upload ids for this project
            uploads_resp, uploads_count = supabase.table('uploads')\
                                                .select('id')\
                                                .eq('project_id', project_id)\
                                                .execute()

            upload_ids = [row['id'] for row in (uploads_resp[1] or [])]

            if not upload_ids:
                return default_response(project_name=project_name)

            # Fetch eeu_data rows for those uploads
            eeu_resp, eeu_count = supabase.table('eeu_data')\
                                        .select('id,created_at,baseline_design,upload_id')\
                                        .in_('upload_id', upload_ids)\
                                        .execute()

            if eeu_count == 0 or not eeu_resp[1]:
                return default_response(project_name=project_name)

            df = pd.DataFrame(eeu_resp[1])
            # Align with expected column names
            df = df.rename(columns={'id': 'eeu_id'})
            df['created_at'] = pd.to_datetime(df['created_at'])
        except Exception:
            return default_response(project_name=project_name)

    # Rename the 'id' column to 'eeu_id'
    df = df.rename(columns={'id': 'eeu_id'})

    # Convert 'created_at' to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    latest_baseline = None
    latest_design = None

    baseline_data = df[df['baseline_design'] == 'baseline']
    design_data = df[df['baseline_design'] == 'design']

    if not baseline_data.empty:
        latest_baseline = baseline_data.loc[baseline_data['created_at'].idxmax()]

    if not design_data.empty:
        latest_design = design_data.loc[design_data['created_at'].idxmax()]
    latest_eeu_data = []
    if latest_baseline is not None:
        latest_eeu_data.append(latest_baseline['eeu_id'])
    if latest_design is not None:
        latest_eeu_data.append(latest_design['eeu_id'])
    return {
        "status": "success",
        "latest_eeu_data": latest_eeu_data,
        "latest_baseline": latest_baseline['eeu_id'] if latest_baseline is not None else None,
        "latest_design": latest_design['eeu_id'] if latest_design is not None else None,
        "project_name": project_name
    }

def return_project_details(project_id):
    latest_eeu_data = get_latest_eeu_data(project_id)
    latest_eeu_data = latest_eeu_data['latest_eeu_data']

    eeu_data_full = []
    df_eeu_data = pd.DataFrame()
    for eeu_id in latest_eeu_data:
        try:
            eeu_query = supabase.table('eeu_data')\
                                .select('*')\
                                .eq('id', eeu_id)
            eeu_data, eeu_count = eeu_query.execute()
            eeu_data_full.append(eeu_data[1])

            df_eeu_data = pd.concat([df_eeu_data,pd.json_normalize(eeu_data[1])])
            
        except:
            print('No EEU data found for this ID.')

    '''df_eeu_data = df_eeu_data.T
    df_eeu_data = df_eeu_data.reset_index()
    df_eeu_data.columns = range(df_eeu_data.shape[1])
    df_eeu_data = df_eeu_data.rename(columns={0: 'field_name',1: 'baseline', 2: 'design'})'''
    cols_to_drop=['id','report_type','use_type_total_area','area_units',
                  'project_name','weather_string',
                  'weather_station','climate_zone','upload_id',
                  'file_url','created_at','updated_at','upload_warnings','energy_units','upload_errors','file_type']
    df_eeu_data = df_eeu_data.drop(columns=cols_to_drop)
    df_eeu_data = df_eeu_data.T

    # Rename the columns based on the 'baseline_design' row
    col_names = ['field_name']
    col_names.extend(list(df_eeu_data.loc['baseline_design']))
    #delete the baseline_design row
    df_eeu_data = df_eeu_data.drop('baseline_design')
    df_eeu_data = df_eeu_data.reset_index()
    df_eeu_data.columns = range(df_eeu_data.shape[1])
    df_eeu_data.columns = col_names


    json_output = df_eeu_data.to_json(orient='records')

    return json_output

def get_signed_url_from_project_id(project_id, baseline_design):
    latest_eeu_data = get_latest_eeu_data(project_id)
    latest_baseline = latest_eeu_data['latest_baseline']
    latest_design = latest_eeu_data['latest_design']
    project_name = latest_eeu_data['project_name']

    if baseline_design == 'baseline' and latest_baseline is None:
        return "No latest baseline data available"
    elif baseline_design == 'design' and latest_design is None:
        return "No latest design data available"
    
    if baseline_design == 'baseline':
        latest_id = latest_baseline
    else:
        latest_id = latest_design
    query = supabase.table('eeu_data')\
                        .select('id,file_url,file_type')\
                        .eq('id', latest_id)
    data, count = query.execute()
    file_url =  data[1][0]['file_url']
    file_type = data[1][0]['file_type']
    project_name = sanitize_filename(project_name)
    file_name = project_name + '_' + baseline_design + file_type
    return get_signed_url_from_url(file_url, download_as = file_name)

@lru_cache(maxsize=128)
def get_eeu_fields_data():
    query = supabase.table('eeu_fields')\
                        .select('*')
    data, count = query.execute()
    df = pd.DataFrame(data[1])
    
    return df


@lru_cache(maxsize=128)
def get_use_types():
    query = supabase.table('eeu_fields')\
                        .select('use_type')
    # where fuel_category is in the list_energy_types
    query = query.in_('fuel_category', list_energy_types)
    data, count = query.execute()
    df = pd.DataFrame(data[1])
    #remove duplicates
    df = df.drop_duplicates()
    #remove the row "Total"
    df = df.loc[df['use_type'] != 'Total']
    
    return df


def get_energy_end_uses_data(project_id, baseline_design, **kwargs):
    
    output_units = kwargs.get('output_units', 'kbtu/sf')
    
    #find the most recently updated eeu_data for design/baseline based on passed parameter
    latest_eeu_data = get_latest_eeu_data(project_id)
    
    baseline_design_key = f'latest_{baseline_design}'
    latest_eeu_data = latest_eeu_data[baseline_design_key]
    
    status = "success"

    if latest_eeu_data is None:
        status = "No latest project available"
        return {"status":status,"baseline_design":baseline_design}
    
    eeu_query = supabase.table('eeu_data')\
                        .select('*')\
                        .eq('id', latest_eeu_data)
    eeu_data, eeu_count = eeu_query.execute()
    
    if eeu_count == 0 or not eeu_data[1]:
        return {"status": "No EEU data found", "baseline_design": baseline_design}

    eeu_data = eeu_data[1][0]
    
    df_eeu = pd.DataFrame(eeu_data, index=[0])
    #df_eeu = df_eeu.T
    energy_units = df_eeu['energy_units'][0]
    
    # Check for required location data fields
    location_fields = ['zip_code', 'egrid_subregion']
    for field in location_fields:
        if field not in df_eeu.columns or pd.isna(df_eeu[field].iloc[0]):
            pass
    
    zip_code = df_eeu['zip_code'][0] if 'zip_code' in df_eeu.columns else None
    egrid_subregion = df_eeu['egrid_subregion'][0] if 'egrid_subregion' in df_eeu.columns else None
    eeu_id = df_eeu['id'][0]
    
    if energy_units == 'gj':
        df_eeu = convert_gj_to_mbtu(df_eeu,supabase,'eeu_data')
        
    use_type_total_area = float(df_eeu['use_type_total_area'][0])
    
    if output_units == 'kbtu/sf':
        df_eeu = convert_mbtu_to_kbtu_per_sf(df_eeu, use_type_total_area, supabase)
    elif output_units == 'kbtu':
        df_eeu = convert_mbtu_to_kbtu_df(df_eeu, supabase)
    elif output_units == 'gj':
        df_eeu = convert_mbtu_to_gj_df(df_eeu, supabase)
    elif output_units != 'mbtu':
        return {"status":"error","error":"Invalid output units"}
        
    df_eeu = df_eeu.T
    df_eeu = df_eeu.reset_index()
    
    df_fields = get_eeu_fields_data()

    # Merge the EEU data with the EEU fields data
    df = pd.merge(df_eeu, df_fields, left_on='index', right_on='field_name')
    
    #rename column named 0 to 'energy_value'
    df = df.rename(columns={0: 'energy_value'})
    #set column energy_value to numeric
    df['energy_value'] = pd.to_numeric(df['energy_value'], errors='coerce')
    
    # Check for NaN values after conversion
    nan_count = df['energy_value'].isna().sum()
    if nan_count > 0:
        pass

    df = df.loc[df['use_type'] != 'Total']
    
    # Check if we have any data left
    non_zero_count = (df['energy_value'] != 0).sum()
    if df.empty:
        return {"status": "No data after processing", "baseline_design": baseline_design}

    def export_pivot(df,export_type):
        #group by use type and fuel_type return sums 
        if export_type == 'end_uses':
            energy_type_cols = list_energy_types
                #drop rows for fuel_category of onsite_renewables
            
            cols_to_pivot='fuel_category'
        elif export_type == 'renewables':
            energy_type_cols = list_onsite_renewables
            cols_to_pivot='field_name'

        df_grouped = df.groupby(['use_type',cols_to_pivot]).sum().reset_index()
        if export_type == 'end_uses':
            df_grouped = df_grouped.loc[df_grouped['fuel_category'] != 'onsite_renewables']


        # Pivot the DataFrame
        df_pivot = df_grouped.pivot(index='use_type', columns=cols_to_pivot, values='energy_value').fillna(0)
        df_pivot_vals = None
        if export_type == 'end_uses':
            df_pivot_vals = pd.DataFrame(index=df_pivot.index, columns=df_pivot.columns)

            for row in df_pivot.index:
                for col in df_pivot.columns:
                    value = df_pivot.at[row, col]
                    # Filter df_grouped to ensure lengths match
                    matches = df_grouped[
                        (df_grouped['fuel_category'] == col) & 
                        (df_grouped['use_type'] == row)
                    ]
                    editable = not matches.empty  # Check if there are any matches
                    df_pivot_vals.at[row, col] = {'value': value, 'editable': editable, 'edited': False}
        else:
            df_pivot_vals = pd.DataFrame(index=df_pivot.index, columns=df_pivot.columns)

            for row in df_pivot.index:
                for col in df_pivot.columns:
                    value = df_pivot.at[row, col]
                    # Filter df_grouped to ensure lengths match

 
                    df_pivot_vals.at[row, col] = {'value': value, 'editable': True, 'edited': False}
        # Ensure all columns are present, even if they are empty
        for energy_type in energy_type_cols:
            if energy_type not in df_pivot.columns:
                df_pivot[energy_type] = 0

        # Fill NA values with 0
        df_pivot = df_pivot.fillna(0)

        # Order the columns
        df_pivot = df_pivot[energy_type_cols]

        return {"pivot_table":df_pivot, "pivot_details":df_pivot_vals}
    

    df_renewables = df.loc[df['fuel_category'] == 'onsite_renewables']
    #set the value of all "use_type" to "On-Site Renewables"
    df_renewables['use_type'] = 'On-Site Renewables'
    df_renewables = export_pivot(df_renewables,'renewables')
    df_pivot = export_pivot(df,'end_uses')

    


    return {"status":status,
            "eeu_data":df_pivot['pivot_table'],
            "eeu_data_edit_details":df_pivot['pivot_details'],
            "renewables":df_renewables['pivot_table'],
            "renewables_edit_details":df_renewables['pivot_details'],
            "use_type_total_area":use_type_total_area,
            "zip_code":zip_code,
            "egrid_subregion":egrid_subregion,
            "eeu_id":eeu_id}

def combine_end_uses_data(project_id, output_units):
    df_baseline_empty = False
    df_design_empty = False
    
    # Get location data from the latest EEU data
    from weather_location import get_location_data
    location_data = None
    try:
        latest_eeu_data = get_latest_eeu_data(project_id)
        if latest_eeu_data['status'] == 'success' and latest_eeu_data['latest_design']:
            location_data = get_location_data(latest_eeu_data['latest_design'])
    except Exception as e:
        print(f"Error getting location data: {e}")
        location_data = None
    def append_col_name_baseline_design(df, baseline_design):  
        df.columns = [f'{col}_{baseline_design}' for col in df.columns]
        return df
    
    def add_total_row(df, edit_details=False):
        if edit_details:
            total = df.applymap(lambda x: x['value'] if isinstance(x, dict) else x).sum(numeric_only=True)
            total = total.apply(lambda x: {'value': x, 'editable': False, 'edited': False})
        else:
            total = df.sum(numeric_only=True)
        
        total[df.columns[0]] = 'Total'
        df_total = pd.DataFrame(total).T
        df = pd.concat([df, df_total], ignore_index=True)
        return df
    def check_energy_type_cols(df, energy_type, edit_details):
        energy_type_cols = [f'{energy_type}_baseline', f'{energy_type}_design']
        energy_type_cols = [col for col in energy_type_cols if col in df.columns]
        
        if edit_details:
            total_sum = df[energy_type_cols].applymap(lambda x: x['value'] if isinstance(x, dict) else x).sum().sum()
        else:
            total_sum = df[energy_type_cols].sum().sum()

        if total_sum == 0:
            return True
        else:
            return False

    def create_empty_df(baseline_design,export_type):
        if export_type == 'end_uses':
            col_energy_types = list_energy_types
            df_use_types = get_use_types()
        elif export_type == 'renewables':
            col_energy_types = list_onsite_renewables

        
        cols = [f'{col}_{baseline_design}' for col in col_energy_types]
        cols.insert(0, 'use_type')  # add "use_type" column as first column

        df_blank = pd.DataFrame(columns=cols)
        if export_type == 'end_uses':
            df_blank['use_type'] = df_use_types['use_type']  # make 'use_type' the first column of df_blank
        elif export_type == 'renewables':
            df_blank['use_type'] = ['On-Site Renewables']

        # fill all other columns with zero
        for col in cols[1:]:
            df_blank[col] = 0

        return df_blank


    def process_eeu_data(df_baseline,df_design,export_type, edit_details=False):

        if export_type == 'end_uses':
            energy_type_cols  = list_energy_types
        elif export_type == 'renewables':
            energy_type_cols = list_onsite_renewables
        
        def process_df(df, df_type):
            if isinstance(df, pd.DataFrame):
                df = append_col_name_baseline_design(df, df_type)
                df = df.reset_index()
            else:
                df = create_empty_df(df_type,export_type)
            return df
        
        df_baseline = process_df(df_baseline, 'baseline')
        df_design = process_df(df_design, 'design')


        df_combined = pd.merge(df_baseline, df_design, on='use_type', how='outer')
        df_output = df_combined
        if export_type == 'end_uses':
            df_output = add_total_row(df_output, edit_details=edit_details)
        
        col_order = [f'{energy_type}_{suffix}' for energy_type in energy_type_cols for suffix in ['design', 'baseline']]
        col_order.insert(0, 'use_type')

        # Filter col_order to only include columns that exist in df_output
        col_order = [col for col in col_order if col in df_output.columns]

        # Reorder df_output based on the filtered col_order
        df_output = df_output[col_order]

        if export_type == 'end_uses':
            # Iterate over each energy type in the list of energy types
            for energy_type in energy_type_cols:
                # Check if the columns for the current energy type are empty (sum to zero)
                if check_energy_type_cols(df_output, energy_type, edit_details):
                    # Create a list of column names to drop for the current energy type
                    cols_to_drop = [f'{energy_type}_baseline', f'{energy_type}_design']
                    # Filter the list to only include columns that actually exist in the DataFrame
                    cols_to_drop = [col for col in cols_to_drop if col in df_output.columns]
                    # Drop the specified columns from the DataFrame
                    df_output = df_output.drop(columns=cols_to_drop)
        elif export_type == 'renewables':
            #rename 'SolarPV_On-SiteRenewables','SolarDHW_On-SiteRenewables', columns to Solar PV and Solar DHW
            #renewables only have design data, drop baseline data
            cols_to_drop = [col for col in df_output.columns if col.endswith('_baseline')]
            df_output = df_output.drop(columns=cols_to_drop)
            df_output = df_output.rename(columns={'SolarPV_On-SiteRenewables_design':'Solar PV_design',
                                                    'SolarDHW_On-SiteRenewables_design':'Solar DHW_design'})
            

        json_output = df_output.to_json(orient='records')

        return json_output
        

    
    baseline = get_energy_end_uses_data(project_id, 'baseline', output_units=output_units)

    if baseline['status'] != "success":
        df_baseline_renewables = baseline['status']
        df_baseline = baseline['status']
        df_baseline_edit_details = baseline['status']
    else:
        df_baseline_renewables = baseline['renewables']
        df_baseline = baseline['eeu_data']
        df_baseline_edit_details = baseline['eeu_data_edit_details']

    design = get_energy_end_uses_data(project_id, 'design', output_units=output_units)
    df_design_renewables_edit_details = None
    if design['status'] != "success":
        df_design_renewables = design['status']
        df_design = design['status']
        df_design_edit_details = design['status']
    else:
        df_design_renewables = design['renewables']
        df_design = design['eeu_data']
        df_design_edit_details = design['eeu_data_edit_details']
        df_design_renewables_edit_details = design['renewables_edit_details']




    eeu_data_output = process_eeu_data(df_baseline,df_design,'end_uses')
    renewables_output = process_eeu_data(df_baseline_renewables,df_design_renewables,'renewables')
    eeu_data_edit_details = process_eeu_data(df_baseline_edit_details,df_design_edit_details,'end_uses', edit_details=True)
    renewables_edit_details = process_eeu_data(df_baseline_renewables,df_design_renewables_edit_details,'renewables', edit_details=True)
    
    # Prepare response with location data
    response = {
        "eeu_data": eeu_data_output,
        "eeu_data_edit_details": eeu_data_edit_details,
        "renewables": renewables_output,
        "renewables_edit_details": renewables_edit_details
    }
    
    # Add location data if available
    if location_data:
        response.update({
            "city": location_data.get('city', ''),
            "state": location_data.get('state', ''),
            "zip_code": location_data.get('zip_code', ''),
            "egrid_subregion": location_data.get('egrid_subregion', '')
        })
    
    return response
    
    




def get_energy_end_uses_chart_data(project_id):
    def remove_empty_energy_types(df):
        # Remove any columns that sum to zero
        filtered_df = df.loc[:, (df.sum() != 0)]
        return filtered_df
    
    def process_data(output, data_type):
        if output['status'] == "success":
            df_pivot = output['eeu_data']
            
            df_pivot = remove_empty_energy_types(df_pivot)
            
            if df_pivot.empty:
                series = []
                categories = []
            else:
                series = [{'name': index, 'data': row.tolist()} for index, row in df_pivot.iterrows()]
                categories = df_pivot.columns.tolist()
        else:
            series = []
            categories = []
        
        result = {"series": series, "categories": categories}
        return result

    baseline = get_energy_end_uses_data(project_id, 'baseline')
    design = get_energy_end_uses_data(project_id, 'design')
    
    baseline_result = process_data(baseline, "baseline")
    design_result = process_data(design, "design")
    
    final_response = {
        "baseline": baseline_result,
        "design": design_result
    }
    
    return final_response

    
def get_change_history(project_id):
    uploads = get_uploads_for_project(project_id)
    upload_ids = [upload['id'] for upload in uploads]
    eeu_data_ids = get_eeu_data_ids_for_uploads(upload_ids)
    

    @lru_cache(maxsize=128)
    def fetch_user_email(id):
        query = supabase.from_('profiles')\
                            .select('email')\
                            .eq('id', id)
        data, count = query.execute()
        return data[1][0]['email']
    
    def return_enum_field_clean(field_name):
        #from enum_list, find the display_name for the field_name
        for item in enum_list:
            if item['id'] == field_name:
                return item['display_name']
        return field_name
    
    def return_enum_list_name(field_name):
        for item in enum_list:
            if item['id'] == field_name:
                return item['list_name']
        return field_name

    def fetch_event_history(table_name, ref_ids):
        query = supabase.table('event_history')\
                            .select('field_name,previous_value,new_value,updated_at,updated_by')\
                            .eq('table_name', table_name)\
                            .in_('ref_id', ref_ids)
        data, count = query.execute()
        df = pd.DataFrame(data[1])

        # Map updated_by to email
        try:
            df['updated_by'] = df['updated_by'].apply(fetch_user_email)
        except:
            print("Error fetching user email")
        try:
            df['enum_list_name'] = df['field_name'].apply(return_enum_list_name)
            df['field_name'] = df['field_name'].apply(return_enum_field_clean)
           
        except:
            print("Error cleaning field name")
        try:
            if table_name == 'uploads':
                df['previous_value'] = df.apply(lambda row: return_enum_value(row['enum_list_name'], enum_id=row['previous_value']), axis=1)
            else:
                df['previous_value'] = df['previous_value'].astype(str)
        except:
            print("Error cleaning previous value")
        try:
            if table_name == 'uploads':
                df['new_value'] = df.apply(lambda row: return_enum_value(row['enum_list_name'], enum_id=row['new_value']), axis=1)
            else:
                df['new_value'] = df['new_value'].astype(str)
        except:
            print("Error cleaning new value")
        
        return df
    # Fetch event history for each table
    uploads_history = fetch_event_history('uploads', upload_ids)
    eeu_data_history = fetch_event_history('eeu_data', eeu_data_ids)
    projects_history = fetch_event_history('projects', [project_id])

    # Combine all dataframes
    combined_history = pd.concat([uploads_history, eeu_data_history, projects_history])

    # Check if combined_history is empty or 'updated_at' column is missing
    if combined_history.empty or 'updated_at' not in combined_history.columns:
        return json.dumps([])  # Return an empty JSON array

    # Sort by 'updated_at' in descending order
    combined_history = combined_history.sort_values(by='updated_at', ascending=False)

    # Convert the DataFrame to a list of dictionaries
    history_list = combined_history.to_dict(orient='records')

    # Convert the list of dictionaries to JSON
    history_json = json.dumps(history_list)

    return history_json

def get_project_energy_summary_data(project_id):
    query = supabase.table('project_energy_summary')\
                        .select('*')\
                        .eq('project_id', project_id)
    data, count = query.execute()
    return data[1][0]














