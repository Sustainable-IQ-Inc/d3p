
from pathlib import Path
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io

def parse_report_eplus(url):





  def get_braket_value(input_string):
    # Find the positions of the opening and closing brackets
    opening_bracket_index = input_string.find('[')
    closing_bracket_index = input_string.find(']')

    # Extract the value between the brackets using slicing
    if opening_bracket_index != -1 and closing_bracket_index != -1:
      value_within_brackets = input_string[opening_bracket_index + 1: closing_bracket_index]
    else:
      value_within_brackets = None
    return value_within_brackets

  # Get the HTML file
  response = requests.get(url)

  # Save the HTML data to a file-like object
  html_file = io.StringIO(response.text)

  # Parse the HTML file with BeautifulSoup
  soup = BeautifulSoup(html_file, "html.parser")

  tables = []
  for table in soup.find_all('table'):
    tables.extend(pd.read_html(table.prettify()))

  # Printing the first few:
  for df in tables[0:3]:
    print(df, '\n')
     
  all_text= soup.get_text()

  environment_text="Environment: "
  environment_loc=all_text.find(environment_text)
  end_line_loc=all_text.find("\n",environment_loc)

  weather_string=all_text[environment_loc+len(environment_text):end_line_loc]



  building_text="Building: "
  building_loc=all_text.find(building_text)
  end_line_loc1=all_text.find("\n",building_loc)

  building_str=all_text[building_loc+len(building_text):end_line_loc1]

  df_sf=tables[2]
  #get units for area
  input_string = df_sf.iloc[0,1]
  area_units = get_braket_value(input_string)

  if area_units == 'ft2':
    sf = float(df_sf.iloc[2,1])
  else:
    m2=float(df_sf.iloc[2,1])
    sf=round(m2*10.7639,2)
     


  #find main table
  df=tables[3]

  #check for units
  input_energy_units = df.iloc[0,1]
  energy_units_extract = get_braket_value(input_energy_units)


  #remove the water column
  df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True)


  cols=df.iloc[0]

  for i in range(1,len(cols)):

    col_name=cols[i]
    b1_loc=col_name.find('[')
    end_line=col_name.find("]",b1_loc)
    unit_str=col_name[b1_loc+1:end_line]

    if(b1_loc!=-1):
      col_str=col_name[:b1_loc-1]

      df.iloc[0,i]=col_str

  new_header = df.iloc[0] #grab the first row for the header
  df = df[1:] #take the data less the header row
  df.columns = new_header #set the header row as the df header
  df1=pd.DataFrame()
  for j in range(1,len(cols)):


    col_name=cols[j]

    if(col_name=='Electricity'):
      col_name='Electricity'
    elif(col_name=='Natural Gas'):
      col_name='NaturalGas'
    else:
      col_name='other'

    insert_list=df.iloc[:,[0,j]].values.tolist()
    df3=pd.DataFrame(insert_list)
    df3.iloc[:,0]=df3.iloc[:,0]+'_'+col_name

    insert_list=df3.values.tolist()
    #df2.reset_index(drop=True)
    df1=pd.concat([df1, pd.DataFrame(insert_list)], ignore_index=True)


  df1.columns=['report_field','energy_value']
  df1['energy_units']=energy_units_extract.lower()
  df1['conditioned_area_sf']=sf
  df1['report']='eplus'


  nan_value = float("NaN")
  #Convert NaN values to empty string

  df1.replace("", nan_value, inplace=True)

  df1.dropna(subset = ["report_field"], inplace=True)
  df1['weather_string']=weather_string
  df1['project_name']=building_str

  df1.reset_index(drop=True, inplace=True)


  #save_to='/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/Script 1/raw/'+export_filename

  #df.to_csv(save_to)
  return {'df':df1,
                'warnings':[] ## warnings to be configured
                }

print("done")



  
