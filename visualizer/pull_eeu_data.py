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
        return "no results"