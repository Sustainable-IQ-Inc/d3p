
from pathlib import Path

import pandas as pd

import pathlib
import requests
from bs4 import BeautifulSoup
import pdfplumber

from datetime import datetime, timedelta
import time
from math import radians, cos, sin, asin, sqrt
import logging_start
import io


def printer(str):
  print(str)
  logging_start.logger.info(str)


def process_prm_table(df,prm_baseline_design):

    df = df.loc[df['check_row_type']=="Energy use kBtu"]
    
    # Validate that we have data after filtering
    if df.empty or len(df) == 0:
        printer("Error: No rows found with 'Energy use kBtu' in check_row_type column")
        raise ValueError("No energy use data found in PRM table")

    for i in range(len(df)):
        if(df.iloc[i,df.columns.get_loc('energy_type')].find("Gas")!=-1):
            fuel_type="gas"
        else:
            fuel_type="electricity"

        # Clean the energy_use value by removing all types of newline and whitespace characters
        energy_use_clean = str(df.iloc[i,df.columns.get_loc('energy_use')])
        energy_use_clean = energy_use_clean.replace('\\n', ' ')  # literal \n strings
        energy_use_clean = energy_use_clean.replace('\n', ' ')   # actual newlines
        energy_use_clean = energy_use_clean.replace('\\r', ' ')  # literal \r strings
        energy_use_clean = energy_use_clean.replace('\r', ' ')   # actual carriage returns
        energy_use_clean = energy_use_clean.replace('\t', ' ')   # tabs
        energy_use_clean = ' '.join(energy_use_clean.split())    # normalize whitespace
        
        df.iloc[i,df.columns.get_loc('report_field')]= energy_use_clean+"_"+fuel_type
    std_cols=['report_field','energy_units','conditioned_area_sf','weather_string','report']
    des_col=['design_value']

    des_cols=std_cols+des_col

    bl_col=['baseline_value']

    bl_cols=std_cols+bl_col

    all_cols=std_cols+bl_col+des_col
    
    # Validate all required columns exist
    missing_cols = [col for col in all_cols if col not in df.columns]
    if missing_cols:
        printer(f"Error: Missing required columns in PRM table: {missing_cols}")
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    df=df[all_cols]
    for i in range(len(df)):
        try:
            design_val = str(df.iloc[i,df.columns.get_loc('design_value')])
            baseline_val = str(df.iloc[i,df.columns.get_loc('baseline_value')])
            
            # Handle NaN or empty values
            if pd.isna(design_val) or design_val == 'nan' or design_val.strip() == '':
                printer(f"Warning: Empty design_value at row {i}, setting to 0")
                design_val = '0'
            if pd.isna(baseline_val) or baseline_val == 'nan' or baseline_val.strip() == '':
                printer(f"Warning: Empty baseline_value at row {i}, setting to 0")
                baseline_val = '0'
            
            df.iloc[i,df.columns.get_loc('design_value')]=float(design_val.replace(',',''))/1000
            df.iloc[i,df.columns.get_loc('baseline_value')]=float(baseline_val.replace(',',''))/1000
        except (ValueError, IndexError) as e:
            printer(f"Error processing row {i}: {e}")
            raise ValueError(f"Error processing energy values at row {i}: {str(e)}")

    df_des=df[des_cols]
    output_filenames=[]

    
    df_des=df_des.rename(columns={des_col[0]:'energy_value'})

    


    df_bl=df[bl_cols]


    df_bl=df_bl.rename(columns={bl_col[0]:'energy_value'})


    #save_to='/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/Script 1/raw/'+export_filename

    #df.to_csv(save_to)
    if prm_baseline_design == 'design':
        df = df_des
    else:
        df = df_bl

    return {'df':df,
            'warnings':[] #warnings have not been configured for this report yet
            }

def parse_report_iesve_prm(url,baseline_design):

 
    # Get the PDF file
    response = requests.get(url)

    # Save the PDF data to a file-like object
    pdf_file = io.BytesIO(response.content)

    # Open the PDF file
    with pdfplumber.open(pdf_file) as pdf:
        pages = pdf.pages

    
    


        page_no_to_use_sf=-999
        page_no_to_use_main_table=-999
        page_no_to_use_weather=-999
        double_page_table=False  # Initialize to False




        for i,pg in enumerate(pages):
            txt = pages[i].extract_text()
            ## find the page with the square footage values
            found_text_1= txt.find("Space Summary")
            found_text_2= txt.find("Building Use")
            if(page_no_to_use_sf==-999 and found_text_1!=-1 and found_text_2!=-1):
                page_no_to_use_sf=i

            ##Find page with the table that contains the Design and Baseline values
            found_text_3 = txt.find("Performance Rating Table - PRM Compliance")
            #found_text_4 = txt.find("Total Annual Energy Use")

            if(found_text_3!=-1):
                page_no_to_use_main_table=i
                ##  look in the page after the main table for the next section header, if it's not there, then it's a two page table
                
                # Check if there's a next page before accessing it
                if i+1 < len(pages):
                    txt_next_page = pages[i+1].extract_text()
                    found_text_6 = txt_next_page.find("Energy Cost & Consumption by energy Type")
                    if(found_text_6!=-1):
                        double_page_table=False
                    else:
                        page_no_to_use_main_table_2=i+1
                        double_page_table=True
                        page_to_use_main_table_2=pdf.pages[page_no_to_use_main_table_2]
                else:
                    # Last page, so it's not a double page table
                    double_page_table=False 


            ##Find page with the table that contains the weather locaiton data
            found_text_5 = txt.find("Weather file")
            if(page_no_to_use_weather==-999 and found_text_5!=-1):
                page_no_to_use_weather=i




            

            ## if all of the values have been found, break
            if(page_no_to_use_sf!=-999 and page_no_to_use_main_table!=-999 and page_no_to_use_weather!=-999):
                break

            ## if all of the values have been found, including
                

            


        # Validate that all required pages were found
        if page_no_to_use_sf == -999:
            error_msg = "Could not find 'Space Summary' page in PDF"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        if page_no_to_use_main_table == -999:
            error_msg = "Could not find 'Performance Rating Table - PRM Compliance' page in PDF"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        if page_no_to_use_weather == -999:
            error_msg = "Could not find 'Weather file' page in PDF"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)

        #im=first_page.to_image()
        #im.reset().debug_tablefinder()

        #im.debug_tablefinder()
        #all_text = page_to_use_main_table.extract_text()



        table_settings_main_table = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "min_words_vertical": 4,
        }

        table_settings_sf = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "min_words_vertical": 4,
        }

        table_settings_weather = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "min_words_vertical": 4,
        }
        ##Find page width and ehight to determine if it is landscape or portrait

        page_to_use_sf = pdf.pages[page_no_to_use_sf] 
        try:
            totals_text= page_to_use_sf.search('Totals')
            if not totals_text or len(totals_text) == 0:
                error_msg = "Could not locate square footage table - missing 'Totals' marker"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)
            left_sf=totals_text[0].get('x0')-5
            left_sf=0
            top_sf=totals_text[0].get('top')
            bottom_sf=totals_text[0].get('bottom')
        except Exception as e:
            error_msg = f"Could not locate square footage table: {str(e)}"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg) from e
    
        page_width_sf=page_to_use_sf.width
        right_sf=page_width_sf 

        sf_table = page_to_use_sf.crop((left_sf,top_sf,right_sf,bottom_sf),relative=True)
        data_sf=sf_table.extract_table(table_settings_sf)

        # Validate that we extracted table data
        if not data_sf or len(data_sf) == 0:
            error_msg = "Could not extract square footage table from PDF"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        #remove any columns from data_sf that are empty
        data_sf = [x.strip() for x in data_sf[0] if x.strip()]

        # Validate that we have data after cleaning
        if not data_sf or len(data_sf) == 0:
            error_msg = "Square footage table is empty after cleaning"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)

        if(data_sf[0]=="Totals"):
            if len(data_sf) < 2:
                error_msg = "Square footage table format is incorrect - missing value after 'Totals'"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)
            conditioned_space = data_sf[1]
        else:
            conditioned_space = data_sf[0]
        
        conditioned_space=float(conditioned_space.replace(',',''))



        page_to_use_weather=pdf.pages[page_no_to_use_weather]
        try:
            weather_loc_text="Weather file"
            weather_loc= page_to_use_weather.search(weather_loc_text)
            if not weather_loc or len(weather_loc) == 0:
                error_msg = "Could not locate weather data - missing 'Weather file' marker"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)
            
            all_weather_text=page_to_use_weather.extract_text()
            # Try multiple variations of the bottom marker
            weather_bottom_loc = None
            weather_bottom_text = None
            for bottom_text in ["zone:", "Climate zone:"]:
                weather_bottom_loc = page_to_use_weather.search(bottom_text, x_tolerance=3, y_tolerance=3, case=False)
                if weather_bottom_loc and len(weather_bottom_loc) > 0:
                    weather_bottom_text = bottom_text
                    break
            
            if not weather_bottom_loc or len(weather_bottom_loc) == 0:
                error_msg = "Could not locate weather data - missing 'zone:' or 'Climate zone:' marker"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)

            left_weather=weather_loc[0].get('x0')
            top_weather=weather_loc[0].get('top')
            bottom_weather=weather_bottom_loc[0].get('top')
        except Exception as e:
            error_msg = f"Could not locate weather data: {str(e)}"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg) from e
        page_width_weather=page_to_use_weather.width
        page_height_weather=page_to_use_weather.height
        right_weather=page_width_weather 
        weather_table = page_to_use_weather.crop((left_weather,top_weather,right_weather,bottom_weather),relative=True)
        data_weather=weather_table.extract_table(table_settings_weather)
        
        # If table extraction fails, try extracting text directly
        weather_string = None
        if not data_weather or len(data_weather) == 0 or (len(data_weather) > 0 and len(data_weather[0]) == 0):
            # Fall back to text extraction
            weather_text = weather_table.extract_text()
            if weather_text:
                # Remove the "Weather file" prefix and any trailing "Climate zone:" text
                weather_text_clean = weather_text.replace(weather_loc_text, "").strip()
                # Remove any trailing "Climate zone:" or "zone:" text
                for suffix in ["Climate zone:", "zone:"]:
                    if weather_text_clean.endswith(suffix):
                        weather_text_clean = weather_text_clean[:-len(suffix)].strip()
                weather_string = weather_text_clean
        else:
            # Use table extraction method (original behavior)
            data_weather=data_weather[0][0]
            weather_string = data_weather[len(weather_loc_text):]
        
        # Validate that we extracted weather string
        if not weather_string or weather_string.strip() == "":
            error_msg = "Could not extract weather string from PDF"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        # Clean up the weather string (remove extra whitespace, newlines, etc.)
        weather_string = ' '.join(weather_string.split())





            #page_no_to_use_main_table=11
        page_to_use_main_table = pdf.pages[page_no_to_use_main_table]  

        if(double_page_table):
            offset=-5
        else:
            offset=0
        try:
            set_left= page_to_use_main_table.search('Combined Heat and Power')
            if not set_left or len(set_left) == 0:
                error_msg = "Could not locate main energy table - missing 'Combined Heat and Power' marker"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)
            left=set_left[0].get('x0')+offset
            
            set_top= page_to_use_main_table.search('%')
            if not set_top or len(set_top) == 0:
                error_msg = "Could not locate main energy table - missing '%' marker"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)

            top=set_top[0].get('bottom')
        except Exception as e:
            error_msg = f"Could not locate main energy table: {str(e)}"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg) from e
    
        page_width=page_to_use_main_table.width
        page_height=page_to_use_main_table.height
        right=page_width


        
        main_table = page_to_use_main_table.crop((left,top,right,page_height),relative=True)
        eeu_table=main_table.extract_table(table_settings_main_table)
        
        # Validate that we extracted the main energy table
        if not eeu_table or len(eeu_table) == 0:
            error_msg = "Could not extract main energy table from PDF"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        ##if it's a double page report, extract second page and add it to same dataframe
        df=pd.DataFrame(eeu_table)
        if(double_page_table):
            set_top= page_to_use_main_table_2.search('%')
            if not set_top or len(set_top) == 0:
                error_msg = "Could not extract second page of energy table - missing '%' marker"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)
            top=set_top[0].get('bottom')
            
            main_table2=page_to_use_main_table_2.crop((left,top,right,page_height),relative=True)
            eeu_table2=main_table2.extract_table(table_settings_main_table)
            
            if not eeu_table2 or len(eeu_table2) == 0:
                error_msg = "Could not extract second page of main energy table from PDF"
                printer(f"Error: {error_msg}")
                raise ValueError(error_msg)
        
            df_2=pd.DataFrame(eeu_table2)

            df=pd.concat([df,df_2])
        
        # Validate dataframe has required columns
        if df.shape[1] < 7:
            error_msg = f"Energy table format is incorrect - has only {df.shape[1]} columns, expected at least 7"
            printer(f"Error: {error_msg}")
            raise ValueError(error_msg)
        
        df=df[[0,2,3,4,6,]]

        df = df.rename(columns={0:'energy_use',2:'energy_type',3:'check_row_type',4:'design_value',6:'baseline_value'})
        df['report_field']=''
        df['energy_units']='mbtu'
        df['conditioned_area_sf']=conditioned_space
        df['weather_string']=weather_string
        df['report']='iesve_prm'
        
        try:
            output_prm = process_prm_table(df,baseline_design)
        except Exception as err:
            printer(err)
            printer("There was an error parsing PRM table")
            return "error parsing PRM table"

        return output_prm

#parse_report_iesve_prm("1234","1234A")