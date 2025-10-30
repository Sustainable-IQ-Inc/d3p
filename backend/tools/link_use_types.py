## This script will link the use types to the DDX use types in the database

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

def get_enum_project_use_types() -> List[Dict]:
    """Fetch all rows from enum_project_use_types table"""
    response = supabase.table("enum_project_use_types").select("*").execute()
    return response.data

def get_ddx_use_types() -> List[Dict]:
    """Fetch all rows from ddx_use_types table"""
    response = supabase.table("ddx_use_types").select("*").execute()
    return response.data

def update_project_use_type(id: int, ddx_use_type_id: int | None):
    """Update a project use type with its corresponding DDX use type ID"""
    supabase.table("enum_project_use_types").update(
        {"ddx_use_type_id": ddx_use_type_id}
    ).eq("id", id).execute()

def main():
    # Get all project use types
    project_use_types = get_enum_project_use_types()
    
    # Get all DDX use types
    ddx_use_types = get_ddx_use_types()
    
    # Create a dictionary mapping DDX use type names to their IDs
    ddx_use_type_map = {use_type['ddx_use_type']: use_type['id'] for use_type in ddx_use_types}
    
    # For each project use type, update with matching DDX use type ID
    for use_type in project_use_types:
        name = use_type.get('name')
        project_use_type_id = use_type.get('id')
        
        # Find matching DDX use type ID or set to None if no match
        ddx_use_type_id = ddx_use_type_map.get(name)
        
        # Update the record
        update_project_use_type(project_use_type_id, ddx_use_type_id)
        
        if ddx_use_type_id:
            print(f"Updated {name} with DDX use type ID: {ddx_use_type_id}")
        else:
            print(f"No match found for {name}, setting DDX use type ID to null")

if __name__ == "__main__":
    main()

