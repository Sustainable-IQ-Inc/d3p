from pint import UnitRegistry
ureg = UnitRegistry()


def convert_kbtu_per_ft2_to_kwh_per_m2(value):
    return value * (0.293071 / 0.092903)

def convert_mbtu_to_kwh(value):
    #convert mbtu to kwh
    return value * 293.071

def convert_sf_to_m2(value):
    return value * 0.092903

def convert_gj_to_mbtu(value):
    return value * 0.947817

def convert_mbtu_to_gj(value):
    return value * 1.0550558526

def convert_mbtu_to_kbtu(value):
    #convert mbtu to kbtu
    return value * 1000

def check_units_eeu_field(eeu_id,supabase,value,current_units=None):
    # If current_units is provided, use it; otherwise fall back to project's stored units
    if current_units:
        energy_units = current_units
        print(f"Using current display units: {energy_units}, input value: {value}")
    else:
        query = supabase.table('eeu_data')\
                        .select('energy_units')\
                        .eq('id', eeu_id)
        data, count = query.execute()
        if data[1]:
            energy_units = data[1][0]['energy_units']
            print(f"Using project stored units: {energy_units}, input value: {value}")
        else:
            # Fallback if no energy units found
            value = float(value)
            print(f"No energy units found, using raw value: {value}")
            return value
    
    # Convert input value to MBtu for database storage
    if energy_units == 'gj':
        # Convert from GJ to MBtu for storage
        value = float(value) * 0.947817
        print(f"Converted GJ to MBtu: {value}")
    elif energy_units == 'kbtu' or energy_units == 'kbtu/sf':
        # Convert from kBtu to MBtu for storage (divide by 1000)
        value = float(value) / 1000
        print(f"Converted kBtu to MBtu: {value}")
    else:
        # Already in MBtu, no conversion needed
        value = float(value)
        print(f"No conversion needed (MBtu): {value}")

    return value



def get_columns_for_conversion(table_name,supabase):
    query = supabase.table('column_metadata')\
                .select('column_name','unit_type')\
                .eq('table_name', table_name)\
                .eq('has_units', True)\
                .eq('conversion_needed', True)
    data, count = query.execute()

    if data[1] != []:
        # Initialize empty lists for each unit type
        energy_list = []
        area_list = []
        eui_list = []

        # Iterate over the response data
        for item in data[1]:
            # Append the column name to the appropriate list based on the unit type
            if item['unit_type'] == 'eui':
                eui_list.append(item['column_name'])
            elif item['unit_type'] == 'energy':
                energy_list.append(item['column_name'])
            elif item['unit_type'] == 'area':
                area_list.append(item['column_name'])

        return eui_list, energy_list, area_list
    else:
        return None




def convert_units_in_table(data,table_name,output_measurement_system,supabase,**kwargs):
    conversion_type = kwargs.get('conversion_type', None)
    conditioned_area_value = kwargs.get('conditioned_area_value', None)

    eui_list, energy_list,area_list = get_columns_for_conversion(table_name,supabase)
    
    for record in data:
        for field in energy_list:
            if conversion_type != 'mbtu_to_kbtu/sf' and field in record and record[field] is not None :
                record[field] = convert_mbtu_to_kwh(float(record[field]))
        for field in area_list:
            if field in record and record[field] is not None and conversion_type != 'mbtu_to_kbtu/sf':
                record[field] = convert_sf_to_m2(float(record[field]))
        for field in eui_list:
            if field in record and record[field] is not None:
                if conversion_type == 'mbtu_to_kbtu/sf':
                    record[field] = float(record[field]) * 1000 / conditioned_area_value
                else:
                    record[field] = convert_kbtu_per_ft2_to_kwh_per_m2(float(record[field]))
    return data

def convert_mbtu_to_kbtu_per_sf(df, use_type_total_area, supabase):
    eui_list, energy_list, area_list = get_columns_for_conversion('eeu_data', supabase)
    for column_label, series in df.items():
        for field in energy_list:
            if field == column_label:
                df[column_label] = df[column_label].apply(lambda x: float(x) * 1000 / use_type_total_area if x is not None else x)
    return df

def convert_mbtu_to_kbtu_df(df, supabase):
    eui_list, energy_list, area_list = get_columns_for_conversion('eeu_data', supabase)
    for column_label, series in df.items():
        for field in energy_list:
            if field == column_label:
                df[column_label] = df[column_label].apply(lambda x: float(x) * 1000 if x is not None else x)
    return df

def convert_mbtu_to_gj_df(df, supabase):
    eui_list, energy_list, area_list = get_columns_for_conversion('eeu_data', supabase)
    for column_label, series in df.items():
        for field in energy_list:
            if field == column_label:
                df[column_label] = df[column_label].apply(lambda x: float(x) * 1.0550558526 if x is not None else x)
    return df

def convert_gj_to_mbtu(df,supabase,table_name):
    eui_list, energy_list, area_list = get_columns_for_conversion(table_name,supabase)
    for column_label, series in df.items():
        for field in energy_list:
            if field == column_label:
                df[column_label] = df[column_label].apply(lambda x: float(x) * 0.9478171203 if x is not None else x)
    return df


