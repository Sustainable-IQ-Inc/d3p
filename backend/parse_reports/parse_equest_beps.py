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
import post_processing 
import io
import os

# Get the directory where this file is located and go up one level to backend
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_report_equest_beps(url):
  warnings = []

  try:   
        #filename = Path('temp/report.pdf')

        #takes URL from Airatble and stores that PDF to the path, above
        response = requests.get(url)
        pdf_file = io.BytesIO(response.content)
        with pdfplumber.open(pdf_file) as pdf:
            pages = pdf.pages
            for i,pg in enumerate(pages):
                txt = pages[i].extract_text()
                #look for REPORT- BEPS Building Energy Performance  text
                found_text = txt.find("REPORT- BEPS Building Energy Performance")
                if(found_text!=-1):
                
                    page_no_to_use=i
                    print("page"+str(i))

        page_to_use = pdf.pages[page_no_to_use]

        #im=first_page.to_image()
        #im.reset().debug_tablefinder()

        #im.debug_tablefinder()
        all_text = page_to_use.extract_text()



        table_settings = {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "min_words_vertical": 3,
        }
        table_settings2 = {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "min_words_vertical": 0,
        }


        main_table=pdf.pages[page_no_to_use]

        box2 = main_table.search('TOTAL SITE ENERGY')

        #[{'text': 'TOTAL SITE ENERGY', 'groups': (), 'x0': 108.88134247482824, 'top': 202.43642850000003, 'x1': 174.08041956786948, 'bottom': 208.7843835, 'chars': [{'matrix': (0.75, 0.0, 0.0, 0.75, 108.88134247482824, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 108.88134247482824, 'y0': 583.2156165, 'x1': 112.69011547482825, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'T', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 112.69073539072173, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 112.69073539072173, 'y0': 583.2156165, 'x1': 116.49950839072173, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'O', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 116.56298794072171, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 116.56298794072171, 'y0': 583.2156165, 'x1': 120.37176094072171, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'T', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 120.3723808566152, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 120.3723808566152, 'y0': 583.2156165, 'x1': 124.1811538566152, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'A', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 124.24463340661518, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 124.24463340661518, 'y0': 583.2156165, 'x1': 128.05340640661518, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'L', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 131.92627887250865, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 131.92627887250865, 'y0': 583.2156165, 'x1': 135.73505187250865, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'S', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 135.73567178840213, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 135.73567178840213, 'y0': 583.2156165, 'x1': 139.54444478840213, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'I', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 139.5450647042956, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 139.5450647042956, 'y0': 583.2156165, 'x1': 143.35383770429561, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'T', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 143.4173172542956, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 143.4173172542956, 'y0': 583.2156165, 'x1': 147.2260902542956, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'E', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 151.09896272018906, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 151.09896272018906, 'y0': 583.2156165, 'x1': 154.90773572018907, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'E', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 154.90835563608255, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 154.90835563608255, 'y0': 583.2156165, 'x1': 158.71712863608255, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'N', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 158.78060818608253, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 158.78060818608253, 'y0': 583.2156165, 'x1': 162.58938118608253, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'E', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 162.59000110197601, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 162.59000110197601, 'y0': 583.2156165, 'x1': 166.39877410197602, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'R', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 166.3993940178695, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 166.3993940178695, 'y0': 583.2156165, 'x1': 170.2081670178695, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'G', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}, {'matrix': (0.75, 0.0, 0.0, 0.75, 170.27164656786948, 585.120003), 'fontname': 'CIDFont+F2', 'adv': 5.078364, 'upright': True, 'x0': 170.27164656786948, 'y0': 583.2156165, 'x1': 174.08041956786948, 'y1': 589.5635715, 'width': 3.808773000000002, 'height': 6.347954999999956, 'size': 6.347954999999956, 'object_type': 'char', 'page_number': 1, 'text': 'Y', 'stroking_color': None, 'non_stroking_color': (0.0, 0.0, 0.0), 'top': 202.43642850000003, 'bottom': 208.7843835, 'doctop': 202.43642850000003}]}]

        total_site_energy_x0 = box2[0].get('x0')
        total_site_energy_x1 = box2[0].get('x1')
        total_site_energy_top = box2[0].get('top')
        total_site_energy_bottom = box2[0].get('bottom')

        box1=main_table.search("=======")
        table1_botton=box1[0].get('top')


        #use the bottom location of text BEPS Building Energy Performance to create the upper bounds for the main table
        beps_text= main_table.search('BEPS Building Energy Performance')
        top=beps_text[0].get('bottom')
        page_width=page_to_use.width
        total_text= main_table.search('TOTAL')
        right=page_width


        main_table = main_table.crop((0,top,right,table1_botton+20),relative=True)
        #print(main_table.extract_words(x_tolerance=4, y_tolerance=3, keep_blank_chars=False, use_text_flow=False, horizontal_ltr=True, vertical_ttb=True, extra_attrs=[]))

        #find table with summar value to derive building size
        #'SITE', 'x0': 131.92627887250865, 'x1': 147.2260902542956, 'top': 180.83642625000005
        summary_section=pdf.pages[page_no_to_use]
        summary_section=summary_section.crop((total_site_energy_x0,total_site_energy_top,612,total_site_energy_bottom),relative=True)
        s=summary_section.extract_text(x_tolerance=3, y_tolerance=3, layout=False, x_density=7.25, y_density=13)


        #find weather file data
        wf="WEATHER FILE- "
        wf_loc=all_text.find(wf)
        end_line=all_text.find("\n",wf_loc)
        wf_str=all_text[wf_loc+len(wf):end_line]

        e_loc=s.find("ENERGY")+6
        energy_units = "MBTU"
        m_loc=s.find(energy_units)
        mbtu=float(s[e_loc:m_loc].strip())

        m_loc=m_loc+4
        k_loc=s.find("KBTU")
        kbtu_p_sf=float(s[m_loc:k_loc].strip())
        mbtu_p_sf=kbtu_p_sf/1000
        sf = round(mbtu/mbtu_p_sf,0)



        table=main_table.extract_table(table_settings)
        df = pd.DataFrame(table[1::],columns=table[0])
        #df.to_csv('temp/raw_table.csv')

        #df = df.drop([0,1])

        df.iloc[1] = df.iloc[1]+" "+df.iloc[2]
        df.iloc[1,0]='col1'

        cols = list(df.iloc[1])


        
        df.columns=cols
        df = df.drop([1])
        nan_value = float("NaN")
        df.replace("", nan_value, inplace=True)

        df.dropna(subset = ['col1'], inplace=True)
        #df.to_csv('df_priorT3.csv')    
        df = df.reset_index(drop=True)
        #df.to_csv('df_priorT.csv')

        for i in range(df.shape[0]):
            if(df.iloc[i,0]==energy_units):
                if i == df.shape[0] - 1:  # Check if it's the last row
                    df.iloc[i,0] = "total"
                else:
                    df.iloc[i,0]=df.iloc[i-1,0]+" "+df.iloc[i,0]
        df.replace("", nan_value, inplace=True)

        df.dropna(subset = [' TOTAL'], inplace=True)

        #transpose dataframe
        
        df_energy_type_codes = pd.read_csv(os.path.join(current_dir, 'dependencies/energy_codes.csv'))

        
        for i in range(df.shape[0]-1):
    

            def characters_before_space(s):
                return s.split(' ', 1)[0]

            
            #check if energy code from row is in the set

            if(characters_before_space(df.iloc[i,0]) in df_energy_type_codes['code'].values):
                df.iloc[i,0]=df_energy_type_codes.loc[df_energy_type_codes['code'] == characters_before_space(df.iloc[i,0]), 'energy_type'].iloc[0]
            else:
                print('didnt find it'+df.iloc[i,0])
                warnings.append('Did not find energy code for '+characters_before_space(df.iloc[i,0]))
            
                
        #df.to_csv('df_priorT4.csv')

        # Fetch the last column
        last_column = df.iloc[:, -1]

        #convert last column to numeric
        last_column = pd.to_numeric(last_column, errors='coerce')

        # Calculate sum of all rows except the last one in the last column
        sum_except_last = last_column.iloc[:-1].sum()

        # Get the value in the last row of the last column
        last_row_value = last_column.iloc[-1]

        # Check if they are equal
        if sum_except_last != last_row_value:
            print("The sum of the rows ("+ str(sum_except_last) +") does not match the total row's value ("+ str(last_row_value) +")")
            warnings.append("The sum of the rows ("+ str(sum_except_last) +") does not match the total row's value ("+ str(last_row_value) +")")




        df = df.T

        #make the first row the header
        new_header = df.iloc[0]
        df = df[1:] 
        df.columns = new_header

        df['conditioned_area_sf']=sf
        df = df.reset_index()
        df.columns.values[0] = "report_field"
        #df.to_csv('df_postT.csv')
        cols=['report_field','energy_value']
        df_beps=pd.DataFrame(columns=cols)


        for i in range(1,len(df.columns)-1):
            for j in range(df.shape[0]):
                col_vals=df.columns.values.tolist()

                this_add={'report_field':df.iloc[j,0]+"_"+col_vals[i],'energy_value':df.iloc[j,i]}
                
                df_beps=pd.concat([df_beps,pd.DataFrame([this_add])])

        df_elec=df.iloc[:,:1]
        df = df.reset_index()
        df_elec = df_elec.reset_index()

        df_elec.columns.values[0] = "report_field"
        df_beps['report_field'] = df_beps['report_field'].str.strip()
        df_beps['report']='equest_beps'
        df_beps['energy_units']='mbtu'
        df_beps['conditioned_area_sf']=sf
        df_beps['weather_string']=wf_str

        #df_beps.to_csv('export_equest_beps.csv')


        #df.to_csv('/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/export_equest_beps.csv')



        #save_to='/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/Script 1/raw/'+export_filename

        #df.to_csv(save_to)


        return {'df':df_beps,
                'warnings':warnings}
  except ValueError as err:
    print("error")