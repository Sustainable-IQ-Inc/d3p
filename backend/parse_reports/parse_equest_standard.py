from pathlib import Path
import pandas as pd
import requests
import tabula
import logging_start
import post_processing 
import io
from tabula.io import read_pdf


def parse_report_equest_standard(url,area,zip_code):


  conditioned_space = area

  # Get the PDF file
  response = requests.get(url)
  pdf_file = io.BytesIO(response.content)

  try:
    # Read the PDF file into a DataFrame
    df_list = read_pdf(pdf_file, pages='all', output_format='dataframe')
    if df_list:
      df = pd.concat(df_list)
    else:
      raise ValueError("No data found in PDF")
  except Exception as err:
    print("tabula error:"+ str(err))
    logging_start.logger.info("tabula error:"+str(err))

  # Create new columns for Jan and Feb
  df['Jan'] = df['Jan Feb']
  df['Feb'] = df['Jan Feb']

  #take the value before the space and set it in the Jan col
  for i in range(df.shape[0]):
    if((type(df.iloc[i]['Jan Feb'])==str)):
      jan_num = df.iloc[i]['Jan Feb'].find(" ")
      jan_val = df.iloc[i]['Jan Feb'][:jan_num]
      df.iloc[i,df.columns.get_loc('Jan')]=jan_val

  #take the value after the space and set it in the Feb col
  for i in range(df.shape[0]):
    if((type(df.iloc[i]['Jan Feb'])==str)):
      feb_num = df.iloc[i]['Jan Feb'].find(" ")+1
      feb_val = df.iloc[i]['Jan Feb'][feb_num:]
      df.iloc[i,df.columns.get_loc('Feb')]=feb_val

  #get rid of unnecessary columns

  df = df.drop(columns=['Jan Feb','Unnamed: 2'], axis=1)

  #move the jan and feb columns to the proper order
  jan_col=df.pop('Jan')
  feb_col=df.pop('Feb')
  df.insert(1, 'Jan', jan_col)
  df.insert(2, 'Feb', feb_col)

  #rename first column
  df = df.rename(columns={'Unnamed: 0': 'report_field'})
  df = df.rename(columns={'Total': 'energy_value'})

  #get rid of any hyphens in dataframe
  df = df.replace(['-'],0)



  #get a list of the column names
  cols = list(df.columns.values)

  #create a list of columns with number type values by removing the first column from list
  num_cols = cols[1:]

  df[num_cols]=df[num_cols].apply(pd.to_numeric, errors='coerce')


  #this finds the first row with the value Total. Above this is electric, below is Gas
  first_total_row = df[df['report_field'] == 'Total'].index[0]
  #df_electric=df[:first_total_row+1]
  df_electric=df.iloc[:first_total_row+1].copy()

  df_electric['report_field']=df_electric['report_field'] + '_elec'
  df_electric['energy_units']='mwh'
  df_electric.to_csv('temp/electric.csv')


  #this finds where the gas part of the table starts and adds 2 rows, which is where first value is
  gas_start_row = df[df['report_field'] == 'Gas Consumption (Btu x000,000)'].index[0]
  #df_gas=df[gas_start_row+2:]
  df_gas=df.iloc[gas_start_row+2:].copy()

  df_gas['report_field']=df_gas['report_field'] + '_gas'
  df_gas['energy_units']='mbtu'

  df_gas.to_csv('temp/gas.csv')

  df_combined=pd.concat([df_electric,df_gas])
  df_combined['conditioned_area_sf']=conditioned_space
  df_combined['report']='equest_standard'
  df_combined['weather_string']=str(zip_code)


  df_combined.to_csv('combined.csv')

  df_export=pd.DataFrame(df_combined,columns=['report_field','energy_value','energy_units','report','conditioned_area_sf','weather_string'])
  #total_row = df.col1.ne('Total').idxmin()



  #save_to='/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/Script 1/raw/'+export_filename

  #df.to_csv(save_to)
  return {'df':df,
        'warnings':[] ## warnings to be configured
                }