## This script will link the energy codes to the DDX energy codes in the database

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE")
supabase: Client = create_client(supabase_url, supabase_key)

def get_enum_energy_codes() -> List[Dict]:
    """Fetch all rows from enum_energy_codes table"""
    response = supabase.table("enum_energy_codes").select("*").execute()
    return response.data

def get_ddx_energy_codes() -> List[Dict]:
    """Fetch all rows from ddx_energy_codes table"""
    response = supabase.table("ddx_energy_codes").select("*").execute()
    return response.data

def update_energy_code(id: int, ddx_energy_code_id: int | None):
    """Update an energy code with its corresponding DDX energy code ID"""
    supabase.table("enum_energy_codes").update(
        {"ddx_energy_code_id": ddx_energy_code_id}
    ).eq("id", id).execute()

def main():
    # Get all energy codes
    energy_codes = get_enum_energy_codes()
    
    # Get all DDX energy codes
    ddx_energy_codes = get_ddx_energy_codes()
    
    # Create a dictionary mapping DDX energy code names to their IDs
    ddx_energy_code_map = {code['ddx_energy_code']: code['id'] for code in ddx_energy_codes}
    
    # For each energy code, update with matching DDX energy code ID
    for code in energy_codes:
        name = code.get('name')
        energy_code_id = code.get('id')
        
        # Find matching DDX energy code ID or set to None if no match
        ddx_energy_code_id = ddx_energy_code_map.get(name)
        
        # Update the record
        update_energy_code(energy_code_id, ddx_energy_code_id)
        
        if ddx_energy_code_id:
            print(f"Updated {name} with DDX energy code ID: {ddx_energy_code_id}")
        else:
            print(f"No match found for {name}, setting DDX energy code ID to null")

if __name__ == "__main__":
    main() 