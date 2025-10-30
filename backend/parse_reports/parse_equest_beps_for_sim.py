
from pathlib import Path

import pandas as pd

import pathlib
import requests
from bs4 import BeautifulSoup
import pdfplumber
import re
import tabula
import xlsxwriter
import os
from datetime import datetime, timedelta
import time
from math import radians, cos, sin, asin, sqrt
import logging_start
import post_processing 
import io


def post_process_beps(df,sf,wf_str):
    energy_type_codes=[['e-Me','elec'],['EM1','elec'],['FM','gas'],['FM1','gas'],['Stea','other'],['Chil','other'],['Hot','other'],['DHW','other'],['HW','other'],['CHW','other']]
    for i in range(df.shape[0]):
        for j in range(len(energy_type_codes)):
        
            if(df.iloc[i,0].find(energy_type_codes[j][0]) != -1):
                df.iloc[i,0]=energy_type_codes[j][1]
                print('found it'+energy_type_codes[j][1])
        
            
    

    df = df.T

    #make the first row the headers
    new_header = df.iloc[0]
    df = df[1:] 
    df.columns = new_header

    df['conditioned_area_sf']=sf
    df = df.reset_index()
    df.columns.values[0] = "report_field"
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




    #df.to_csv(save_to)
    return {'df':df_beps,
                'warnings':[] ##warnings need to be configured for this file type
                }


def parse_equest_beps_for_sim(url):

  try:   
        response = requests.get(url)

        # Save the PDF data to a file-like object
        pdf_file = io.BytesIO(response.content)

        # Open the PDF file
        with pdfplumber.open(pdf_file) as pdf:
            pages = pdf.pages
            for i, pg in enumerate(pages):
                txt = pages[i].extract_text()
                # look for REPORT- BEPS Building Energy Performance  text
                found_text = txt.find("REPORT- BEPS Building Energy Performance")
                if found_text != -1:
                    page_no_to_use = i
                    print("page" + str(i))
                    

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
        beps_text= main_table.search('REFRIG')
        top=beps_text[0].get('top')
        page_width=page_to_use.width
        total_text= main_table.search('TOTAL')
        right=page_width


        main_table = main_table.crop((0,top,right,table1_botton),relative=True)
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
        m_loc=s.find("MBTU")
        mbtu=float(s[e_loc:m_loc].strip())

        m_loc=m_loc+4
        k_loc=s.find("KBTU")
        kbtu_p_sf=float(s[m_loc:k_loc].strip())
        mbtu_p_sf=kbtu_p_sf/1000
        sf = round(mbtu/mbtu_p_sf,0)



        table=main_table.extract_table(table_settings)

        df = pd.DataFrame(table)

        #df = df.drop([0,1])

        df.iloc[0] = df.iloc[0]+" "+df.iloc[1]
        df.iloc[0,0]='col1'
        df.iloc[0]=df.iloc[0].apply(lambda x: x.lstrip())

        #df.to_csv('df_priorT1.csv')
        #df = df.drop([0,2,3,4,5,7,8,10,11])
        #df.to_csv('df_priorT2.csv')
        '''df.iloc[0,0]='fuel type'
        df.iloc[1,0]='electric mbtu'
        df.iloc[2,0]='gas mbtu'
        df.iloc[3,0]='total mbtu'
        '''

        cols = list(df.iloc[0])



        df.columns=cols

        df = df.drop([0])

        nan_value = float("NaN")
        df.replace("", nan_value, inplace=True)




        for i in range(df.shape[0]):
            if(df.iloc[i,1]=="MBTU"):
                df.iloc[i,1]=df.iloc[i-1,1]+" "+df.iloc[i,1]
                df.iloc[i,0]=df.iloc[i-1,0]


        #df.dropna(subset = ['col1'], inplace=True)
        df.dropna(subset = ['TOTAL'], inplace=True)

        df=df.drop(df.columns[1], axis=1)
        df = df.reset_index(drop=True)
        df = df.drop([0,1])


        
        ''' if(' TOTAL' in df.columns):
            df=df.rename(columns={' TOTAL': 'TOTAL'})'''



        output_beps_sim = post_process_beps(df,sf,wf_str)
        
        return {'df':output_beps_sim,
                'warnings':[]#warnings have not been configured yet
                }
        #transpose dataframe


        
  except ValueError as err:
    print("error")
