import pandas as pd
import re
import os
from geopy.geocoders import Nominatim
import logging_start
from math import radians, cos, sin, asin, sqrt
from utils import supabase
from rapidfuzz import process, fuzz


# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

df_zips = pd.read_csv(os.path.join(current_dir, 'dependencies/operational_carbon/zip_to_subregion.csv'), dtype={'zip': str})


def format_as_zip_code(zip_code):
    if not zip_code or not str(zip_code).strip():
        return ''
    try:
        return "{:05}".format(int(str(zip_code).strip()))
    except (ValueError, TypeError):
        return ''



def get_subregion_by_zip(zip_code):
    zip_code = format_as_zip_code(zip_code)

    # Filter the DataFrame by the formatted zip_code
    filtered_df = df_zips[df_zips['zip'] == zip_code]

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return "no zip code found"
    else:
        return filtered_df['subregion'].values[0]
    
def get_climate_zone_by_zip(zip_code):
    df_cities = pd.read_csv(os.path.join(current_dir, 'dependencies/uscities.csv'))
    best_match = process.extractOne(zip_code, df_cities['zips'], scorer=fuzz.token_sort_ratio)
    this_city = df_cities.loc[df_cities['zips'] == best_match[0]]
    this_city_state_clean = this_city.iloc[0, this_city.columns.get_loc('city_ascii')] + ", " + this_city.iloc[0, this_city.columns.get_loc('state_id')]
    this_city_selected = this_city.iloc[0, this_city.columns.get_loc('city_ascii')]
    this_state_selected = this_city.iloc[0, this_city.columns.get_loc('state_name')]
    lat1 = this_city.iloc[0, this_city.columns.get_loc('lat')]
    long1 = this_city.iloc[0, this_city.columns.get_loc('lng')]

    df_weather_locs = pd.read_csv(os.path.join(current_dir, 'dependencies/weather_output_new.csv'))
    df_weather_locs['distance'] = [haversine(long1, lat1, df_weather_locs.long[j], df_weather_locs.lat[j]) for j in range(len(df_weather_locs))]
    df_weather_locs.reset_index()
    min_dist_id = df_weather_locs['distance'].idxmin()

    closest_city = df_weather_locs.loc[min_dist_id]
    weather_info = {
        'status': 'success',
        'city_name': this_city_state_clean,
        'ratio_match': best_match[1],
        'climate_zone': closest_city['climate_zone'],
        'zip_code': zip_code,
        'city': this_city_selected,
        'state': this_state_selected
    }
    return weather_info

def latlong_to_zip(lat, lon):
    geolocator = Nominatim(user_agent="d3p-bem-reports",timeout=20)
    location = geolocator.reverse((lat, lon), exactly_one=True)
    
    if location and 'postcode' in location.raw['address']:
        return location.raw['address']['postcode']
    else:
        return None
    
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km
    
def _get_empty_weather_info():
    """Return empty weather information structure"""
    return {
        'city_name': '',
        'ratio_match': '',
        'climate_zone': '',
        'zip_code': '',
        'egrid_subregion': '',
        'city': '',
        'state': ''
    }

def _process_iesve_weather(weather_string):
    """Process weather data for IESVE, IESVE_PRM, and EPLUS report types"""
    try:
        # Extract WMO code from weather string
        wmo_code = int(re.findall(r'.(\d{6})', weather_string)[0])
        
        # Load and filter weather data
        df_weather = pd.read_csv(os.path.join(current_dir, 'dependencies/weather_output_new.csv'))
        df_weather_new = df_weather.loc[df_weather['wmo_code'] == wmo_code]
        
        if df_weather_new.empty:
            return None
            
        # Extract location data
        climate_zone = df_weather_new.iloc[0]['climate_zone']
        lat = df_weather_new.iloc[0]['lat']
        long = df_weather_new.iloc[0]['long']
        
        # Get zip code and state
        zip_code = latlong_to_zip(lat, long)
        df_cities = pd.read_csv(os.path.join(current_dir, 'dependencies/uscities.csv'))
        state = df_cities.loc[df_cities['zips'].str.contains(str(zip_code), na=False), 'state_name'].iloc[0]
        
        return {
            'city_name': weather_string,
            'ratio_match': 0,
            'climate_zone': climate_zone,
            'zip_code': zip_code,
            'city': '',  # Add missing city field
            'state': state
        }
    except Exception as e:
        logging_start.logger.error(f"IESVE weather processing failed: {str(e)}")
        return None

def _process_equest_beps_weather(weather_string):
    """Process weather data for EQUEST_BEPS report type"""
    try:
        # Load city data and find best match
        df_cities = pd.read_csv(os.path.join(current_dir, 'dependencies/uscities.csv'))
        df_cities['city_state'] = df_cities['city_ascii'] + " " + df_cities['state_id']
        best_match = process.extractOne(weather_string, df_cities['city_state'], scorer=fuzz.token_sort_ratio)
        
        if not best_match:
            return None
            
        # Get city details
        this_city = df_cities.loc[df_cities['city_state'] == best_match[0]].iloc[0]
        this_city_state_clean = f"{this_city['city_ascii']}, {this_city['state_id']}"
        
        # Get location data
        df_weather = pd.read_csv(os.path.join(current_dir, 'dependencies/weather_output_new.csv'))
        df_weather['distance'] = [haversine(this_city['lng'], this_city['lat'], 
                                          df_weather.long[j], df_weather.lat[j]) 
                                for j in range(len(df_weather))]
        
        closest_city = df_weather.loc[df_weather['distance'].idxmin()]
        
        return {
            'city_name': this_city_state_clean,
            'ratio_match': best_match[1],
            'climate_zone': closest_city['climate_zone'],
            'zip_code': this_city['zips'].split()[0],
            'city': this_city['city_ascii'],
            'state': this_city['state_name']
        }
    except Exception as e:
        logging_start.logger.error(f"EQUEST BEPS weather processing failed: {str(e)}")
        return None

def _process_equest_standard_weather(weather_string):
    """Process weather data for EQUEST_STANDARD and GENERIC_XLSX report types"""
    try:
        zip_code = format_as_zip_code(str(weather_string))
        weather_info = get_climate_zone_by_zip(zip_code)
        
        if not weather_info:
            return None
            
        # Get state and city from zip code
        df_cities = pd.read_csv(os.path.join(current_dir, 'dependencies/uscities.csv'))
        matching_cities = df_cities.loc[df_cities['zips'].str.contains(str(zip_code), na=False)]
        if not matching_cities.empty:
            weather_info['state'] = matching_cities.iloc[0]['state_name']
            weather_info['city'] = matching_cities.iloc[0].get('city_ascii', '')
        else:
            weather_info['state'] = ''
            weather_info['city'] = ''
        
        return weather_info
    except Exception as e:
        logging_start.logger.error(f"EQUEST standard weather processing failed: {str(e)}")
        return None

def weather_check(weather_string, report_type):
    """
    Process weather data based on report type and return weather information.
    
    Args:
        weather_string: Input weather string to process
        report_type: Type of report ('iesve', 'iesve_prm', 'eplus', 'equest_beps', 'equest_standard', 'generic_xlsx')
        
    Returns:
        dict: Weather information including city, climate zone, zip code, and state
    """
    try:
        # Process based on report type
        if report_type in ['iesve', 'iesve_prm', 'eplus']:
            weather_info = _process_iesve_weather(weather_string)
        elif report_type == 'equest_beps':
            weather_info = _process_equest_beps_weather(weather_string)
        elif report_type in ['equest_standard', 'generic_xlsx']:
            weather_info = _process_equest_standard_weather(weather_string)
        else:
            logging_start.logger.error(f"Unknown report type: {report_type}")
            return _get_empty_weather_info()
            
        if not weather_info:
            return _get_empty_weather_info()
            
        # Add eGRID subregion
        if 'zip_code' in weather_info:
            weather_info['egrid_subregion'] = get_subregion_by_zip(weather_info['zip_code'])
        else:
            weather_info['egrid_subregion'] = ''
            
        return weather_info
        
    except Exception as e:
        logging_start.logger.error(f"Weather check failed: {str(e)}")
        return _get_empty_weather_info()

def process_weather_location(eeu_id):
  weather_checker_cache = {}

  # Fetch the row from the eeu_data table where id equals eeu_id
  data, count = supabase.table('eeu_data').select('weather_string,report_type').eq('id', eeu_id).execute()

  # If no data is returned, return None or handle accordingly
  if count == 0:
    return None

  weather_string = data[1][0]['weather_string']
  report_type = data[1][0]['report_type']
  
  # Check if the weather_string is in the cache
  if weather_string in weather_checker_cache:
    response = weather_checker_cache[weather_string]
  else:
    # Call the weather_checker function and cache the response
    response = weather_check(weather_string,report_type)
    weather_checker_cache[weather_string] = response
    zip_code = format_as_zip_code(response['zip_code'])


  # Update the zip_code and egrid_subregion for the current row
  update_data = {
    'zip_code': zip_code,
    'egrid_subregion': response['egrid_subregion'],
    'city': response.get('city', ''),
    'state': response.get('state', '')

  }
  supabase.table('eeu_data').update(update_data).eq('id', eeu_id).execute()

  return {'eeu_id': eeu_id,
          'zip_code': zip_code,
          'egrid_subregion': response['egrid_subregion'],
          'city': response.get('city', ''),
          'state': response.get('state', '')}


def get_location_data(eeu_id):
    query = supabase.table('eeu_data')\
                    .select('zip_code,egrid_subregion,city,state')\
                    .eq('id', eeu_id)
    data, count = query.execute()

    # Check if data is empty or if any required fields are None
    if (data[1] == [] or 
        data[1][0]['zip_code'] is None or 
        data[1][0]['city'] is None or 
        data[1][0]['state'] is None):
        location_data = process_weather_location(eeu_id)
        return location_data

    return {'eeu_id':eeu_id,
            'zip_code':data[1][0]['zip_code'],
            'egrid_subregion':data[1][0]['egrid_subregion'],
            'city':data[1][0]['city'],
            'state':data[1][0]['state']}