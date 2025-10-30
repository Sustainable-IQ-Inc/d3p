import pandas as pd
from functools import lru_cache
from supabase import create_client, Client
import os
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import re
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# Only load .env file in local development
env = os.environ.get('ENV', 'local').lower()
print(f"ENV value: {env}")
if env == 'local':
    print("Loading .env file...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"Looking for .env at: {env_path}")
    load_dotenv(env_path)

#### SUPABASE SETUP ####
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE")
print(f"Final values:")
print(f"url: {url}")
print(f"key: {key}")
supabase: Client = create_client(url, key)

#### ENCRYPTION SETUP ####
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
SALT = os.getenv('ENCRYPTION_SALT')

def get_encryption_key():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT if isinstance(SALT, bytes) else SALT.encode(),
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode()))
    return Fernet(key)

def encrypt_value(value: str) -> str:
    if not value:
        return value
    f = get_encryption_key()
    return f.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value: str) -> str:
    if not encrypted_value:
        return encrypted_value
    f = get_encryption_key()
    return f.decrypt(encrypted_value.encode()).decode()

enum_list = [
    {'id': 'project_use_type_id', 'list_name': 'project_use_types', 'display_name': 'Project Use Type'},
    {'id': 'project_phase_id', 'list_name': 'project_phases', 'display_name': 'Project Phase'},
    {'id': 'project_construction_category_id', 'list_name': 'project_construction_categories', 'display_name': 'Project Construction Category'},
    {'id': 'report_type_id', 'list_name': 'report_types', 'display_name': 'Report Type'},
    {'id': 'energy_code_id', 'list_name': 'energy_codes', 'display_name': 'Energy Code'},
    {'id': 'use_type_subtype_id', 'list_name': 'use_type_subtypes', 'display_name': 'Use Type Subtype'},
    {'id': 'climate_zone_id', 'list_name': 'climate_zones', 'display_name': 'Climate Zone'}
]

def create_app():
    app = FastAPI()

    # Get CORS origins from environment variable
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '').split(',')
    # Filter out empty strings
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    return app

async def verify_token(req: Request):
    access_token = req.headers.get('Authorization')
    print(req)

    if access_token and access_token.startswith('Bearer '):
        access_token = access_token.split('Bearer ')[1]  # Extract the token part after 'Bearer '
    
    else:
        # Handle cases where the token format is incorrect or missing
        return {'is_authorized': False}     # Or raise an error or return an appropriate response

    try:
        data = supabase.auth.get_user(access_token)
        

        user_company_id = data.user.user_metadata['company_id']
        user_role = data.user.user_metadata.get('role', 'NA')
        user_id = data.user.id
        return {'is_authorized': True, 
                'company_id': user_company_id, 
                'role': user_role, 
                'user_id': user_id}
    except:
        print ("error with authentication")
        return {'is_authorized': False}   

#@lru_cache(maxsize=128)
def return_enum_vals(enum_type, **args):
    use_type_id = args.get('use_type_id', None)
    id_value = args.get('id_value', None)
    
    # Extract list names from the enum_list dictionary
    enum_list_names = [enum['list_name'] for enum in enum_list]
    
    if enum_type in enum_list_names:
        enum_table_name = "enum_" + enum_type
        try:
            query = supabase.table(enum_table_name)\
                .select('*')\
                .order('order')
            if use_type_id:
                query = query.eq('use_type_id', use_type_id)
            if id_value:
                query = query.eq('id', id_value)
            data, count = query.execute()

            if data[1] != []:
                return data[1]
            else:
                return "no results"
        except Exception as e:
            print(e)
            return "error"
    else:
        return "error"
def return_enum_value(enum_type,enum_id):
    output = return_enum_vals(enum_type, id_value=enum_id)
    return output[0]['name']


def get_enum_id(enum_type, enum_value):


    enum_vals = return_enum_vals(enum_type)
    df = pd.DataFrame(enum_vals)
    try:
        return df[df['name'] == enum_value]['id'].values[0]
    except Exception as e:
        return None
    

def add_event_history(table_name,field_name,ref_id,new_value,user_id,previous_value):
    try:
        data, count = supabase.table('event_history')\
            .insert([{
                'table_name': table_name,
                'field_name': field_name,
                'ref_id': str(ref_id),
                'new_value': str(new_value),
                'updated_by': user_id,
                'previous_value': previous_value
            }])\
            .execute()
        return "success"
    except Exception as e:
        print(e)
        return "error"
    
def sanitize_filename(filename):
    # Remove invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    return filename

def get_field_name_from_use_type(use_type, fuel_category):
    query = supabase.table('eeu_fields')\
        .select('field_name')\
        .eq('use_type', use_type)\
        .eq('fuel_category', fuel_category)
    data, count = query.execute()
    return data[1][0]['field_name']


def fuel_category_override(fuel_category):
    if fuel_category == 'Fossil_Fuels':
        return 'NaturalGas'
    elif fuel_category == 'District':
        return "DistrictHeating"
    elif fuel_category == 'Onsite_Renewables' or fuel_category == 'onsite_renewables':
        return "On-SiteRenewables"
    else:
        return fuel_category

