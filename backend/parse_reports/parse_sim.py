import pandas as pd

from parse_reports.parse_equest_beps_for_sim import *

import requests

###parse SIM file
def parse_report_sim(url):
    #this_file_path='temp/8002 Base - Baseline Design.sim'

    #filename = Path('temp/report.sim')
    

    #takes URL from Airatble and stores that PDF to the path, above
    response = requests.get(url)
    text_file = io.BytesIO(response.content)

    #filename='temp/20220623-Baseline-IO.SIM.pdf'
    #filename='temp/Skycenter_Building-PRM-Report_approved.pdf'


    #read whole file to a string
    data = text_file.getvalue().decode()



    ##find the BEPS section
    beps_start=data.find('REPORT- BEPS Building Energy Performance')
    #find the ---- line
    beps_start1=data.find('---------',beps_start)
    beps_start2=data.find('\n',beps_start1)
    beps_start3=data.find('\n',beps_start2+1)
    beps_end=data.find('=======',beps_start1)
    beps_text=data[beps_start3+1:beps_end]


    filedata = beps_text

    filedata = filedata.replace('    MBTU', 'XXXXMBTU')

    # Write the file out again


    wf="WEATHER FILE- "
    wf_loc=data.find(wf)
    end_line=data.find("\n",wf_loc)
    wf_str=data[wf_loc+len(wf):end_line]




    ##find summary section

    summary_start=data.find('TOTAL SITE ENERGY',beps_start)
    summary_end=data.find('NET AREA',summary_start)

    summary_section=data[summary_start:summary_end]
    e_loc=summary_section.find("ENERGY")+6
    m_loc=summary_section.find("MBTU")
    mbtu=float(summary_section[e_loc:m_loc].strip())

    m_loc=m_loc+4
    k_loc=summary_section.find("KBTU")
    kbtu_p_sf=float(summary_section[m_loc:k_loc].strip())
    mbtu_p_sf=kbtu_p_sf/1000
    sf = round(mbtu/mbtu_p_sf,0)





    #find the word "task" in the first row after the --- line

    #find the bottom of the main table

    #find the summary section




    df = pd.read_fwf(io.StringIO(filedata), colspecs='infer', header=None, index_col=False)
    df = df.fillna("")

    df['LIGHTS']=''

    new_col=df.pop('LIGHTS')
    df.insert(1, 'LIGHTS', new_col)

    df.iloc[1,1]="LIGHTS"
    df.iloc[1,0]=""

    df.iloc[0] = (df.iloc[0]+" "+df.iloc[1])
    df=df.drop(df.index[1])
    ##remove the space in front of words
    df.iloc[0]=df.iloc[0].apply(lambda x: x.lstrip())



    print(len(df))

    check_row=True
    i=0

    while check_row:
        row_text=str(df.iloc[i,0])
        print(row_text)

        search_for_text='XXXXMBTU'
        print(row_text.find(search_for_text))


        if(row_text.find(search_for_text)==0):
            row_text=row_text[len(search_for_text):]
            lights_val=row_text.lstrip()
            df.iloc[i,1]=lights_val

            df.iloc[i,0]=df.iloc[i-1,0]

        i+=1

        if(i==len(df)):
            check_row=False
    check_row=True
    df.reset_index(drop=True)
    i=0
    while check_row:
        if(df.iloc[i,2]==''):
            df=df.drop(df.index[i])


        i+=1
        if(i==len(df)):
            check_row=False
        

    df=df.reset_index(drop=True)
    #make the first row the headers
    new_header = df.iloc[0]
    df = df[1:] 
    df.columns = new_header
    df=df.drop([1])

    #df = df.drop(df.tail(2).index)

    df.columns.values[0] = 'eeu'

    df['col1'] = df['eeu'].str.split().str[0]

    new_col=df.pop('col1')
    df.insert(0,'col1',new_col)
    df=df.drop(columns='eeu')

    export_filename=post_process_beps(df,sf,wf_str)

    return export_filename





    


