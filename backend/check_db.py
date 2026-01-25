from utils import supabase
import pandas as pd

def check_db():
    print("--- Database Check ---")
    try:
        # Check projects count
        res_p = supabase.table('projects').select('id', count='exact').limit(1).execute()
        print(f"Total Projects in 'projects' table: {res_p.count}")
        
        # Check uploads count
        res_u = supabase.table('uploads').select('id', count='exact').limit(1).execute()
        print(f"Total Uploads in 'uploads' table: {res_u.count}")
        
        # Check eeu_data count
        res_e = supabase.table('eeu_data').select('id', count='exact').limit(1).execute()
        print(f"Total Records in 'eeu_data' table: {res_e.count}")
        
        # Check project_energy_summary view
        print("\nQuerying 'project_energy_summary' view...")
        res_v = supabase.table('project_energy_summary').select('*').limit(5).execute()
        
        if res_v.data:
            print(f"View is NOT empty. Found {len(res_v.data)} sample rows.")
            df = pd.DataFrame(res_v.data)
            print(df[['project_id', 'project_name', 'company_id']].to_string())
        else:
            print("View is EMPTY or query returned no data.")
            
        # Check for any corrupted records that might break the view
        # (e.g. invalid decimals in eeu_data)
        
    except Exception as e:
        print(f"ERROR querying database: {e}")

if __name__ == "__main__":
    check_db()
