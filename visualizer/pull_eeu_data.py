import pandas as pd

def pull_eeu_data(supabase, **kwargs):
    company_id = kwargs.get('company_id',None)
    query = supabase.table('project_latest_upload_by_type5')\
            .select('*')
    
    if company_id is not None:
        query = query.eq('company_id', company_id)
        
    data, count = query.execute()
    
    if data[1] != []:
        df = pd.DataFrame(data[1])
        return df
    else:
        # Return empty DataFrame with expected columns to avoid errors
        expected_columns = ['project_id', 'proj_name', 'id', 'climate_zone', 'project_use_type', 
                           'company_id', 'project_phase', 'use_type_total_area', 'total_energy']
        return pd.DataFrame(columns=expected_columns)