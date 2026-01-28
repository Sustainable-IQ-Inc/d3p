from utils import supabase
import pandas as pd

def find_corrupted_deep():
    print("--- DEEP SEARCH FOR CORRUPTION ---")
    try:
        # Fetch all records from eeu_data (354 records is small enough)
        res = supabase.table('eeu_data').select('*').execute()
        
        if not res.data:
            print("No records found.")
            return
            
        df = pd.DataFrame(res.data)
        
        # Identify columns that are linked to energy end-uses
        # (usually have underscore or start with total_)
        energy_cols = [c for c in df.columns if '_' in c and c not in ['file_url', 'file_name', 'weather_string', 'is_ai_parsed', 'upload_id', 'created_at', 'updated_at']]
        
        def is_numeric(val):
            if val is None or val == '': return True
            try:
                float(str(val).replace(',', ''))
                return True
            except ValueError:
                return False

        all_corrupted_ids = set()
        
        for col in energy_cols:
            mask = df[col].apply(lambda x: not is_numeric(x))
            corrupted = df[mask]
            if not corrupted.empty:
                print(f"\nFOUND CORRUPTION IN COLUMN: {col}")
                for idx, row in corrupted.iterrows():
                    print(f"  ID: {row['id']} | Value: '{row[col]}' | File: {row['file_name']}")
                    all_corrupted_ids.add(row['id'])

        if all_corrupted_ids:
            print(f"\nTOTAL UNIQUE CORRUPTED RECORDS: {len(all_corrupted_ids)}")
            print(f"IDs to clean/delete: {list(all_corrupted_ids)}")
        else:
            print("No corruption found in energy columns.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    find_corrupted_deep()
