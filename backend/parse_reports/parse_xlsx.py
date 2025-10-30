import pandas as pd
from post_processing import printer


def parse_xlsx_report(url):
    #attachment_url='temp/generic_upload_test.xlsx'
    df=pd.read_excel(url)

    report_type='generic_xlsx'
    conditioned_area=df.iloc[0,df.columns.get_loc('conditioned_area')]
    area_units=df.iloc[0,df.columns.get_loc('area_units')]
    energy_units=df.iloc[0,df.columns.get_loc('energy_units')]
    weather_string=df.iloc[0,df.columns.get_loc('zip_code')]

    cols_to_drop=['conditioned_area','area_units','energy_units','zip_code']


    for col in cols_to_drop:
        try:
            df.pop(col)
        except Exception as err:
            printer(err)

    df=df.T

    df=df.rename_axis('report_field')
    df=df.rename(columns={0:'energy_value'})
    df = df.reset_index()
    df['energy_units']=energy_units
    df['conditioned_area_sf']=conditioned_area
    df['weather_string']=weather_string
    df['report']=report_type
    
    return {'df':df,
                'warnings':[]## warnings to be configured
                }


