#### INSTALL PACKAGES ####

import os
import pandas as pd
import re
import os
import time

import logging_start
from parse_reports.parse_eplus import *
from parse_reports.parse_equest_beps import *
from parse_reports.parse_iesve_prm import *
from parse_reports.parse_xlsx import *
from parse_reports.parse_sim import *
from parse_reports.parse_iesve import *
from parse_reports.parse_equest_standard import *
from parse_reports.parse_multi_project_xlsx import parse_multi_project_excel_report
import traceback
from weather_location import weather_check

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

BUCKET_NAME = os.getenv('BUCKET_NAME')





def printer(str):
  print(str)
  logging_start.logger.info(str)

def post_process(df_output):
  #imports the list of standard fields
  df_fields = pd.read_csv(os.path.join(current_dir, 'dependencies/field_list.csv'))

  column_fields=[]
  df_cf=pd.Series(column_fields,dtype=object)

  for i in range(df_fields.shape[0]):

    df_cf = pd.concat([df_cf,pd.Series([df_fields.iloc[i,0]])])

  df_2_full=pd.DataFrame()
  df_output = df_output.reset_index(drop=True)
  report_type = df_output.loc[0]['report']

  conditioned_sf = df_output.loc[0]['conditioned_area_sf'].astype('float')
  
  energy_units_in = df_output.loc[0]['energy_units']
  df_output['energy_value']=df_output['energy_value'].astype(float)

  try:
    project_name = df_output.loc[0]['project_name']
  except KeyError as err:
    project_name=''
  uncommon_units=False
  if(energy_units_in=="mbtu"):
    df_output['energy_value_report']=df_output['energy_value']
    df_output['energy_units_report']="mbtu"
    df_output['energy_value']=df_output['energy_value']
    df_output['energy_units']='mbtu'
    uncommon_units=False
  elif(energy_units_in=='gj'):
    df_output['energy_value_report']=df_output['energy_value']
    df_output['energy_value']=df_output['energy_value']*947.8171203/1000
    df_output['energy_units']='mbtu' 
    df_output['energy_units_report']="gj"
    uncommon_units=True
  elif(energy_units_in=='mwh'):
    df_output['energy_value_report']=df_output['energy_value']
    df_output['energy_value']=df_output['energy_value']*3414.4259497
    df_output['energy_units']='kbtu' 

    df_output['energy_units_report']="mwh"
    uncommon_units=True
  elif(energy_units_in=='kbtu'):
    df_output['energy_value_report']=df_output['energy_value']
    df_output['energy_value']=df_output['energy_value']/1000
    df_output['energy_units']='mbtu' 
    df_output['energy_units_report']="kbtu"
    uncommon_units=True
  energy_units = df_output.loc[0]['energy_units']+'/sf'
  df_cm = pd.read_csv(os.path.join(current_dir, 'dependencies/column_mapping.csv'))
  
  try:
    weather_string = str(df_output.loc[0]['weather_string'])

    logging_start.logger.info(str(weather_string))
  except KeyError as err:
    weather_string=''
  
  try:
    logging_start.logger.info('trying weather:'+str(weather_string)+" type:"+report_type)
    weather_info = weather_check(weather_string, report_type)
  except Exception as e:
    logging_start.logger.error(f"Weather check failed: {str(e)}")
    weather_info = {
        'city_name': '',
        'ratio_match': '',
        'climate_zone': '',
        'zip_code': '',
        'egrid_subregion': '',
        'city': '',
        'state': ''
    }

  df_cm = df_cm[df_cm['report'] == report_type] 
  df_cm_output = pd.merge(df_output,df_cm,on="report_field",how='outer')

  ##figure out number of rows per output per report
  if(uncommon_units==True):
    report_rows=['report_values','mbtu','kbtu/sf']

  else:
    report_rows=['mbtu','kbtu/sf']
  #creates a list of output records that is used to mark multiple records as invalid if an error comes up
  output_records=[]
  for k in range(len(report_rows)):
    if(report_rows[k]=='report_values'):
      energy_units = df_cm_output.loc[0]['energy_units_report']
      energy_value_to_use='energy_value_report'
      energy_multiplier=1
      divide_by_val=1
    elif(report_rows[k]=='mbtu'):
      energy_units = 'mbtu'
      energy_value_to_use='energy_value'
      energy_multiplier=1
      divide_by_val=1
    elif(report_rows[k]=='kbtu/sf'):
      energy_units = 'kbtu/sf'
      energy_value_to_use='energy_value'
      energy_multiplier=1000
      divide_by_val=conditioned_sf
    df_fields_list= pd.read_csv(os.path.join(current_dir, 'dependencies/field_list.csv'))

    df_fields_list['total_val']=0
    df_fields_list['units']=energy_units
    column_fields=[]
    df_cf=pd.DataFrame(column_fields,dtype=object)
    for i in range(df_fields_list.shape[0]):
      fieldname=df_fields_list.iloc[i, 0]

      df_fields_list.iloc[i,df_fields_list.columns.get_loc('total_val')] = df_cm_output.loc[df_cm_output['eeu_name'] == fieldname, energy_value_to_use].sum()*energy_multiplier/divide_by_val

      df_cf = pd.concat([df_cf,pd.Series([df_fields_list.iloc[i,0]])])
      
    df_cf = df_cf.reset_index(drop=True)

    #create a list of the fuel sources within df_fields
    fuel_sources=df_fields_list['fuel_source'].unique().tolist()
    num_fuel_sources=len(fuel_sources)
    total_energy=0

    #run look for each of the fuel sources
    for j in range(num_fuel_sources):
      this_fuel_source = fuel_sources[j]

      #sum up the total energy for each fuel source
      fuel_source_total = df_fields_list.loc[df_fields_list['fuel_source'] == this_fuel_source, 'total_val'].sum()
      total_energy=total_energy+fuel_source_total

      #create a new row for the fuel source total which will be added to the main df
      df_row_total_energy_fuel_source = {'field':'total_'+this_fuel_source,'fuel_source' : this_fuel_source,'total_val': fuel_source_total,'units': energy_units}

      #add the new row to the main df
      df_fields_list = pd.concat([df_fields_list,pd.DataFrame([df_row_total_energy_fuel_source])],ignore_index=True)

    #create a row for the use_type_total_area
    df_row_use_type_total_area={'field':'use_type_total_area','fuel_source' : 'na','total_val': conditioned_sf,'units': 'sf'}
  
    #add the new row to the main df
    df_fields_list = pd.concat([df_fields_list,pd.DataFrame([df_row_use_type_total_area])])

    #create a row for the total energy
    df_row_total_energy={'field':'total_energy','fuel_source' : 'na','total_val': total_energy,'units': 'na'}

    #add the new row to the main df
    df_fields_list = pd.concat([df_fields_list,pd.DataFrame([df_row_total_energy])])

    #create a new row to show the report type
    df_row_report_type={'field':'report_type','fuel_source' : 'na','total_val': report_type,'units': 'na'}
    #add the new row to the main df
    df_fields_list = pd.concat([df_fields_list,pd.DataFrame([df_row_report_type])])

    #create a new row to show the project name
    df_row_project_name={'field':'project_name','fuel_source' : 'na','total_val': project_name,'units': 'na'}
    #add the new row to the main df
    df_fields_list = pd.concat([df_fields_list,pd.DataFrame([df_row_project_name])])

    df_new = df_fields_list.T
    df_new['energy_units']=df_new.iloc[3,0]
    df_new.drop(labels=['fuel_source','units'],axis=0,inplace=True)
    df_new.reset_index(inplace=True,drop=True)
    new_header = df_new.iloc[0] #grab the first row for the header
    df_new = df_new[1:] #take the data less the header row
    df_new.columns = new_header #set the header row as the df header
    df_new["area_units"]='sf'
    df_new["weather_station"]=weather_info['city_name']
    df_new["climate_zone"]=weather_info['climate_zone']
    df_new['weather_string']=weather_string
    df_new['zip_code']=weather_info['zip_code']
    df_new['egrid_subregion']=weather_info['egrid_subregion']
    df_new = df_new.rename(columns={energy_units:'energy_units'})

    return df_new



def run_script_master(url, **kwargs):
  report_type = kwargs.get('report_type', None)
  area = kwargs.get('conditioned_area', None)
  baseline_design = kwargs.get('baseline_design', None)
  errors=[]
  warnings=[]
  
  report_parsers = {
    5: parse_report_equest_beps,
    1: parse_report_iesve,
    2: parse_report_eplus,
    3: parse_report_sim,
    4: parse_xlsx_report,
    
    6: parse_report_equest_standard,
    7: None,
    8: parse_report_iesve_prm,
    9: parse_multi_project_excel_report,
   
  }

  warnings = []
  df_output = None

  if report_type is None:
    report_types_to_try = report_parsers.keys()
  else:
    report_types_to_try = [report_type]

  total_start_time = time.time()
  for report_type in report_types_to_try:
    start_time = time.time()
    parser_function = report_parsers.get(report_type)
    print(f"Trying to parse {report_type}...")
    if parser_function is not None:
      try:
        if parser_function.__name__ == 'parse_report_iesve_prm':
          output = parser_function(url, baseline_design)
        else:
          output = parser_function(url)
        df_output = output['df']
        warnings_new = output['warnings']
        warnings.append(warnings_new)
        
        # Check if this is a multi-project Excel file (report type 9)
        if report_type == 9 and 'projects' in output:
          # Return the raw multi-project result without post-processing
          return {
            "status": "success",
            "df": df_output,
            "errors": errors,
            "warnings": warnings,
            "report_type": 9,
            "projects": output['projects'],
            "validation_errors": output.get('validation_errors', [])
          }
        
        break
      except Exception as err:
        print(f"Error parsing {report_type}: {err}")
        logging_start.logger.info(f"Error parsing {report_type}: {err}")
    end_time = time.time()
    print(f"Time taken for {report_type}: {end_time - start_time} seconds")

  total_end_time = time.time()
  print(f"Total time taken: {total_end_time - total_start_time} seconds")

  if df_output is None:
    errors = ['Unsupported file type.']
    return ["pending", errors, warnings]

  try:
    post_process_result = post_process(df_output)
  except ValueError as err:
    post_process_error = "error attachment url:"+url+"error text:"+str(err)
    printer(post_process_error)
    errors.append("There was an error processing your file.")
    traceback.print_exc()
    return ["ERROR",errors,warnings]
  
  return {"status":"success",
      "df":post_process_result,
      "errors":errors,
      "warnings":warnings,
      "report_type":report_type}