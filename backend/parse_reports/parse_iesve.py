from pathlib import Path
import pandas as pd
import requests
import pdfplumber
import io
##Script 1 Parsing for IESVE Report


#creates a function to parse the IESVE report
def parse_report_iesve(url):
 
  #sets the path to save the file to
  #filename = Path('temp/report.pdf')

  #takes URL from Airatble and stores that PDF to the path, above
  try:
    response = requests.get(url)
    pdf_file = io.BytesIO(response.content)


    pdf = pdfplumber.open(pdf_file)
    first_page = pdf.pages[0]

    #parameters for how to parse the PDF
    table_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "min_words_vertical": 5,
        
    }

    page1=pdf.pages[0]

    ##print details of words to find locations of tables to extract
    #print(page1.extract_words(x_tolerance=4, y_tolerance=3, keep_blank_chars=False, use_text_flow=False, horizontal_ltr=True, vertical_ttb=True, extra_attrs=[]))

    #set bounding box for EEU (main) table to extract

    eeu_table = page1.crop((43,140,400,350),relative=True)

    eeu_table=eeu_table.extract_table(table_settings)
    df = pd.DataFrame(eeu_table[1::],columns=eeu_table[0])
    nan_value = float("NaN")
    #cleans up the data table output
    df.replace("", nan_value, inplace=True)
    df.dropna(subset = ["Energy"], inplace=True)
    
    #renames columns
    df = df.rename(columns={'Energy End Use Site':'report_field', 'Energy':'energy_value', 'Source Energy CO2':'Source Energy', 'Em':'CO2 Emissions'})
    df['report_field']=df['report_field'].str.strip()

    df['energy_units']='mbtu'
    #df['co2_emissions_units']='kgco2/ft2/yr'

    #drop columns that aren't necessary for raw export
    df = df.drop(columns=['Source Energy','CO2 Emissions'], axis=1)
    df = df.reset_index(drop=True)

    #pulls the information that the conditioned space value is in
    conditioned_table = page1.crop((350,100,595,200),relative=True)
    conditioned_table=conditioned_table.extract_table()
    df_conditioned = pd.DataFrame(conditioned_table[0::],columns=['field','value'])
    df_conditioned.drop(columns=['field'])

    df['conditioned_area_sf']=df_conditioned.iloc[0, 1]

    
    df['energy_value']=pd.to_numeric(df["energy_value"], downcast="float")
    df['conditioned_area_sf']=pd.to_numeric(df["conditioned_area_sf"], downcast="float")

    df['energy_value']=df['energy_value']*df['conditioned_area_sf']/1000
    df['report']='iesve'

    project_table = page1.crop((30,77,500,150),relative=True)
    project_table=project_table.extract_table()
    print(project_table)
    df_project = pd.DataFrame(project_table,columns=['field','value'])
    df_project.drop(columns=['field'])

    df['project_name']=df_project.iloc[0, 1]
    df['weather_string']=df_project.iloc[2, 1]

    #save_to='/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/Script 1/raw/'+export_filename

    #df.to_csv(save_to)
  except Exception as e:
    print(e)
    return {'status':'error - could not process report'}

  return {'df':df,
                'warnings':[] ## warnings to be configured
                }