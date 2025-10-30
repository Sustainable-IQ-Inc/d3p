import pandas as pd 
from constants import *
import plotly.graph_objects as go
import random
import os

# Get the directory where this file is located and go up one level to the root
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cols =  ['Heating_Electricity','Heating_NaturalGas', 'Heating_DistrictHeating', 'Heating_Other',
       'Cooling_Electricity', 'Cooling_DistrictHeating', 'Cooling_Other',
       'DHW_Electricity', 'DHW_NaturalGas', 'DHW_DistrictHeating', 'DHW_Other',
       'Interior Lighting_Electricity', 'Exterior Lighting_Electricity',
       'Plug Loads_Electricity', 'Fans_Electricity', 'Pumps_Electricity',
       'Pumps_NaturalGas', 'Process Refrigeration_Electricity',
       'ExteriorUsage_Electricity', 'ExteriorUsage_NaturalGas',
       'OtherEndUse_Electricity', 'OtherEndUse_NaturalGas',
       'OtherEndUse_Other', 'Heat Rejection_Electricity',
       'Humidification_Electricity', 'HeatRecovery_Electricity',
       'HeatRecovery_Other', 'SolarDHW_On-SiteRenewables',
       'SolarPV_On-SiteRenewables', 'Wind_On-SiteRenewables',
       'Other_On-SiteRenewables', 'total_Electricity', 'total_NaturalGas',
       'total_DistrictHeating', 'total_Other', 'total_On-SiteRenewables','total_energy',
       'use_type_total_area'
         ]




def generate_project_list(df,list_type,**kwargs):

    # list of columns to create lists for
    company_id = kwargs.get('company_id',None)

    df_lists=df[['project_id','proj_name','id','climate_zone','project_use_type','company_id','project_phase','use_type_total_area','total_energy']]
    
    #convert use type column to string
    if(list_type=='use_type'):
        
        use_types_list = df_lists['project_use_type'].unique().tolist()
        return use_types_list
    
    if(list_type=='climate_zone'):
        cz_list = df_lists['climate_zone'].unique().tolist()
        return cz_list
  
    if(list_type=='project_phases'):
        project_phases_list = df_lists['project_phase'].unique().tolist()
        return project_phases_list
    
    
    if(list_type=='projects'):

        if(company_id!="All" and company_id is not None):
            project_list = df_lists[df_lists['company_id']==company_id]
        else:
            project_list = df_lists

        project_list = project_list.rename(columns={'company_id':'Company Name','climate_zone': 'Climate Zone','project_phase':"Project Phase",'use_type':'project_use_type','use_type_total_area':'Use Type Area (SF)'})


        cols = ['project_id','proj_name','Company Name','total_energy','project_use_type','Use Type Area (SF)','Climate Zone','Project Phase']
        project_list = project_list[cols]
        project_list = project_list.reset_index(drop=True)
        #project_list = project_list['project_id'].unique().tolist()
      
        
        return project_list
    
    if(list_type=='project_names'):

        if(company_id!="All" and company_id is not None):
            project_list = df_lists[df_lists['company_id']==company_id]
        else:
            project_list = df_lists



        cols = ['proj_name']
        project__names_list = project_list[cols]
        #remove duplicates
        project__names_list = project__names_list.drop_duplicates(subset=['proj_name'],keep='last')
        project__names_list = project__names_list.reset_index(drop=True)
        #project_list = project_list['project_id'].unique().tolist()
      
        
        return project__names_list
    if(list_type=='companies'):

        company_list = df_lists.drop_duplicates(subset=['company_id'],keep='last')
        company_list = company_list['company_id'].tolist()
        return company_list
    

def convert_to_kbtu_sf(df):
    cols_to_divide = cols.copy()
    try:
        cols_to_divide.remove('use_type_total_area')
    except:
        print("error removing use_type_total_area")
    df[cols_to_divide] = df[cols_to_divide].div(df['use_type_total_area'], axis=0).multiply(1000)
    
    return df
    
def generate_compare_to_set(df,anonomyze,**kwargs):
    climate_zone_selector = kwargs.get('climate_zone_selector',None)
    use_type_selector = kwargs.get('use_type_selector',None)
    project_selector = kwargs.get('project_selector',None)
    phase_selector = kwargs.get('phase_selector',None)
    baseline_design = kwargs.get('baseline_design',None)
    gsf_ranges = kwargs.get('gsf_ranges',None)
    excluded_projects = kwargs.get('excluded_projects',None)
    anonomyze = kwargs.get('anonomyze',True)
    view_all_projects = kwargs.get('view_all_projects',None)
    company_id = kwargs.get('company_id',None)
    energy_units = kwargs.get('energy_units',None)  
    company_name = kwargs.get('company_name',None)

    if(baseline_design is None):
        baseline_design = 'design'

    df_compare_to_set = df.copy()
    df_compare_to_set = df_compare_to_set[df_compare_to_set['baseline_design']==baseline_design]

    if(excluded_projects is not None):
        df_compare_to_set = df_compare_to_set[~df_compare_to_set['project_id'].isin(excluded_projects)]
        print(df_compare_to_set)



    if(climate_zone_selector!="All" and climate_zone_selector is not None):
        df_compare_to_set=df_compare_to_set.loc[df_compare_to_set['climate_zone']==climate_zone_selector]
    if(use_type_selector != "All" and use_type_selector is not None):
        df_compare_to_set = df_compare_to_set.loc[df_compare_to_set['project_use_type']==use_type_selector]
    if(project_selector != "All" and project_selector is not None):
        df_compare_to_set = df_compare_to_set.loc[df_compare_to_set['company_id']==company_id]
    if(phase_selector != "All" and phase_selector is not None):
        df_compare_to_set = df_compare_to_set.loc[df_compare_to_set['project_phase']==phase_selector]

    if(gsf_ranges != []):
        df_gsf_ranges = return_gsf_ranges()

        df_gsf_ranges = df_gsf_ranges[df_gsf_ranges['Name'].isin(gsf_ranges)]
        '''
        for i in range(len(gsf_ranges)):
            check_gsf = gsf_ranges[i]
            low_val = df_gsf_ranges.loc[df_gsf_ranges['Name']==check_gsf].iloc[0,df_gsf_ranges.columns.get_loc('Lower Value')]
            
            upper_val = df_gsf_ranges.loc[df_gsf_ranges['Name']==check_gsf].iloc[0,df_gsf_ranges.columns.get_loc('Upper Value')]

            df_compare_to_set = df_compare_to_set.loc[df_compare_to_set['use_type_total_area'] > low_val]
            df_compare_to_set = df_compare_to_set.loc[df_compare_to_set['use_type_total_area'] <= upper_val]'''
        filtered_df = pd.DataFrame()
        df_compare_to_set['use_type_total_area'] = df_compare_to_set['use_type_total_area'].astype(float)
        for index, row in df_gsf_ranges.iterrows():
            lower_value = row['Lower Value']
            upper_value = row['Upper Value']
            filtered_rows = df_compare_to_set[(df_compare_to_set['use_type_total_area'] >= lower_value) & (df_compare_to_set['use_type_total_area'] <= upper_value)]
            filtered_df = pd.concat([filtered_df,filtered_rows])

        # Drop duplicates and reset index
        df_compare_to_set = filtered_df


    df_compare_to_set[cols] = df_compare_to_set[cols].apply(pd.to_numeric, errors='ignore', downcast='float')
    df_compare_to_set_full = df_compare_to_set.copy()

    df_compare_to_set_full['pct_total_area'] = 1
    df_compare_to_set_full['legend_val'] = ''
    if(anonomyze):
        print("anonomyzing")

        #if the company id does not match the company id of the user, then replace the Project ID with the project_id_combined_hashed
        df_compare_to_set_full['project_id_combined_hashed']=df_compare_to_set_full['project_id'].apply(lambda x: str(hash(x))[1:7])
        #add a "P" to the front of the hashed project_id_combined_hashed
        df_compare_to_set_full['project_id_combined_hashed']='P'+df_compare_to_set_full['project_id_combined_hashed']
        df_compare_to_set_full.loc[df_compare_to_set_full['company_id']!=company_id,'proj_name'] =  df_compare_to_set_full['project_id_combined_hashed']
        df_compare_to_set_full.loc[df_compare_to_set_full['company_id']==company_id,'legend_val'] = company_name + " Projects"
        df_compare_to_set_full.loc[df_compare_to_set_full['company_id']!=company_id,'legend_val'] = "Anonomous Company Projects"
        #df_compare_to_set_full['project_id'] =  df_compare_to_set_full['project_id_combined_hashed']
        df_compare_to_set_full['proj_name'] = df_compare_to_set_full['proj_name'].astype(str)
        



    #df_compare_to_set_full['weighted_eui'] = df_compare_to_set_full['value'] * df_compare_to_set_full['pct_total_area']
    #take the list cols and replace the value of the column with the value * the pct_total_area
    #from the list cols, remove the value legend_val




    
    df_compare_to_set = df_compare_to_set_full[cols].multiply(df_compare_to_set_full['pct_total_area'],axis="index")


    df_compare_to_set = df_compare_to_set[cols].mean()
    if(energy_units == "kbtu/sf"):
        df_compare_to_set = convert_to_kbtu_sf(df_compare_to_set)
        df_compare_to_set_full = convert_to_kbtu_sf(df_compare_to_set_full)
        df_compare_to_set_full['energy_units'] = 'kbtu/sf'


    df_compare_to_set = df_compare_to_set.reset_index()
    df_compare_to_set = df_compare_to_set.rename(columns={"index": "eeu",0:"value"})

    #divide the use type total area by the total area to get the percentage of the total area

    df_compare_to_set['project_name']='Compare to Set'

    return [df_compare_to_set,df_compare_to_set_full]

def generate_selected_project(df,selected_project,company_id,baseline_design,**kwargs):
    energy_units = kwargs.get('energy_units',None)
    df[cols] = df[cols].apply(pd.to_numeric, errors='ignore', downcast='float')
    df_selected_project = df.loc[df['company_id']==company_id]
    df_selected_project = df.loc[df['proj_name']==selected_project]

    

    df_selected_project = df_selected_project[df_selected_project['baseline_design']==baseline_design]

    #remove duplicates of project id combined and keep only the most recent version

    df_selected_project = df_selected_project[cols]
    df_selected_project=df_selected_project.T
    df_selected_project=df_selected_project.reset_index()
    df_selected_project=df_selected_project.rename(columns={"index": "eeu"})
    print(df_selected_project)
    df_selected_project.rename(columns={ df_selected_project.columns[0]: "eeu", df_selected_project.columns[1]: "value"}, inplace = True)
    #rename the second column to "value"
    #df_selected_project = df_selected_project.rename(columns={df_selected_project.columns[1]: 'value'})
    
    if(energy_units == "kbtu/sf"):
        #convert df_selected_project to a series
        df_selected_project = df_selected_project.set_index('eeu').T
        df_seleceted_project = convert_to_kbtu_sf(df_selected_project)
        df_selected_project = df_selected_project.T
        df_selected_project=df_selected_project.reset_index()
        df_selected_project=df_selected_project.rename(columns={"index": "eeu"})
    df_selected_project['project_name']=selected_project
    return df_selected_project

def generate_combined(df_compare_to_set,df_selected_project):
    df_main_selected_combined = pd.concat([df_compare_to_set,df_selected_project])
    return df_main_selected_combined

def return_num_projects_in_set(df_compare_to_set_full):
    num_projs = len(df_compare_to_set_full)
    return num_projs

def return_metric(metric_name,set_name,**kwargs):
    df_compare_to_set = kwargs.get('df_compare_to_set',None)
    df_selected_project = kwargs.get('df_selected_project',None)
    selected_project = kwargs.get('selected_project',None)
    project_list = kwargs.get('project_list',None)
    energy_units = kwargs.get('energy_units',None)

    format = kwargs.get('format',None)
    
    if(metric_name=='gsf'):
        if(set_name=="compare_to"):
            ##
            gsf = float(df_compare_to_set.loc[df_compare_to_set['eeu'] == 'use_type_total_area', 'value'].iloc[0])
            
        elif(set_name=="selected_project"):
            #gsf=df_selected_project['use_type_total_area'].iloc[-1]
            gsf = float(df_selected_project.loc[df_selected_project['eeu'] == 'use_type_total_area', 'value'].iloc[0])
            
        #round to 0 decimals
        gsf = round(gsf,0)
        if(format=="int"):
            return gsf
        else:
            gsf = "{:,}".format(gsf)
            gsf = gsf + " SF"

            return gsf
    if(metric_name=='eui'):
        if(set_name=="compare_to"):
            eui = float(df_compare_to_set.loc[df_compare_to_set['eeu'] == 'total_energy', 'value'].iloc[0])
        elif(set_name=="selected_project"): 
            eui = float(df_selected_project.loc[df_selected_project['eeu'] == 'total_energy', 'value'].iloc[0])
        eui = round(eui,0)
        if(format=="int"):
            return eui
        else:
            try:
                eui = "{:,}".format(eui)
            except:
                print("error formatting eui")
                eui = ''
            eui = eui + " " + energy_units
            return eui
    if(metric_name=='climate_zone'):
        #select 
        try:
            climate_zone = project_list.loc[project_list['proj_name'] == selected_project].iloc[0,project_list.columns.get_loc('Climate Zone')]
        except:
            climate_zone = 'Unknown'
        return climate_zone
    if(metric_name=='use_type'):
        #select 
        use_type = project_list.loc[project_list['proj_name'] == selected_project].iloc[0,project_list.columns.get_loc('project_use_type')]

        return use_type
    if(metric_name=='area'):
        #select 
        area = project_list.loc[project_list['proj_name'] == selected_project].iloc[0,project_list.columns.get_loc('Use Type Area (SF)')]

        return area
    if(metric_name=='project_company'):
        #select 
        project_company = project_list.loc[project_list['proj_name'] == selected_project].iloc[0,project_list.columns.get_loc('Company Name')]

        return project_company
    
def reformat_output_table(df):
    cols = ['Heating_NaturalGas', 'Heating_DistrictHeating', 'Heating_Other',
    'Cooling_Electricity', 'Cooling_DistrictHeating', 'Cooling_Other',
    'DHW_Electricity', 'DHW_NaturalGas', 'DHW_DistrictHeating', 'DHW_Other',
    'Interior Lighting_Electricity', 'Exterior Lighting_Electricity',
    'Plug Loads_Electricity', 'Fans_Electricity', 'Pumps_Electricity',
    'Pumps_NaturalGas', 'Process Refrigeration_Electricity',
    'ExteriorUsage_Electricity', 'ExteriorUsage_NaturalGas',
    'OtherEndUse_Electricity', 'OtherEndUse_NaturalGas',
    'OtherEndUse_Other', 'Heat Rejection_Electricity',
    'Humidification_Electricity', 'HeatRecovery_Electricity',
    'HeatRecovery_Other', 'SolarDHW_On-SiteRenewables',
    'SolarPV_On-SiteRenewables', 'Wind_On-SiteRenewables',
    'Other_On-SiteRenewables', 'total_Electricity', 'total_NaturalGas',
    'total_DistrictHeating', 'total_Other', 'total_On-SiteRenewables',
    'use_type_total_area', 'report_type', 'project_name', 'area_units',
    'energy_units',  'baseline_design', 'weather_string',
    'climate_zone', 'Heating_Electricity', 'weather_station',
    'total_energy', 'id',
    'project_id', 'project_use_type', 'project_phase',
    'company_id','pct_total_area','legend_val','proj_name']
    
    cols.insert(0, cols.pop(cols.index('project_id')))
    cols.insert(1, cols.pop(cols.index('company_id')))
    cols.insert(2, cols.pop(cols.index('energy_units')))
    cols.insert(3, cols.pop(cols.index('total_energy')))
    #remove 'active (from record_id)', project_id_combined, output_status, filename,  from cols
    cols.remove('project_name')

    df = df[cols]

    #rename company_id to "Company Name"
    df = df.rename(columns={'company_id': 'Company Name'})
    return df
    
def add_energy_types_selected_table(df):
    # Get the directory where this file is located (visualizer directory)
    visualizer_dir = os.path.dirname(os.path.abspath(__file__))
    field_list = pd.read_csv(os.path.join(visualizer_dir, 'dependencies/field_list.csv'))

    df = pd.merge(df, field_list, left_on='eeu',right_on='field', how='left')

    #remove row for 'use_type_total_area'
    df = df[df.eeu != 'use_type_total_area']
    #remove columns that start with total_
    df = df[~df.eeu.str.startswith('total_')]
    return df

def return_gsf_ranges():
    # Get the directory where this file is located (visualizer directory)
    visualizer_dir = os.path.dirname(os.path.abspath(__file__))
    df_ranges = pd.read_csv(os.path.join(visualizer_dir, 'dependencies/gsf_ranges.csv'))
    df_ranges = df_ranges.sort_values(by='Lower Value')
    return df_ranges

def export_chart_data(chart_type,df):
        if chart_type == chart_types['multi_project_chart']:
            export_cols=['project_id',
                         'energy_units',
                        'total_energy',
                        'use_type_total_area',
                        'area_units',
                        'climate_zone',
                        'project_use_type',
                        'project_phase']
            df_export = df[export_cols]
            return df_export
def prep_chart_data(df_compare_to_set_full,selected_project):
        #convert df_compare_to_set_full_plot['total_energy'] to float
        
        df_compare_to_set_reordered = reformat_output_table(df_compare_to_set_full)
        df_compare_to_set_full_plot = df_compare_to_set_reordered.copy()
        df_compare_to_set_full_plot['total_energy'] = df_compare_to_set_full_plot['total_energy'].astype(float) 
        #df_compare_to_set_full_plot = df_compare_to_set_full_plot[df_compare_to_set_full_plot['total_energy'] < 10000]
        df_compare_to_set_full_plot = df_compare_to_set_full_plot.sort_values(by=['total_energy'],ascending=True)
        df_compare_to_set_full_plot = df_compare_to_set_full_plot.reset_index(drop=True)
        print("selected project"+selected_project)
        print(df_compare_to_set_full_plot)
        try:
            df_compare_to_set_full_plot.loc[df_compare_to_set_full_plot['proj_name'] == selected_project,'legend_val'] = selected_project + ' (Selected Project)'
        except:
            print("error setting legend val")
            
        ### This was the old approach of bringing the selected project to the front, but with the new legend addition, this may not be necessary

        #mask = df_compare_to_set_full_plot['project_id'] == selected_project

        # Now use the mask to separate the DataFrame into two
        #df_mask = df_compare_to_set_full_plot[mask]
        #df_mask['legend_val'] = selected_project + ' (Selected Project)'
        #df_no_mask = df_compare_to_set_full_plot[~mask]

        # Finally, concatenate the two DataFrames back together with the desired row at the top
        #df_compare_to_set_full_plot = pd.concat([df_mask, df_no_mask])

        ###

        df_compare_to_set_full_plot_placeholder = df_compare_to_set_full_plot.copy()

        return [df_compare_to_set_full_plot,df_compare_to_set_full_plot_placeholder,df_compare_to_set_reordered]

def truncate_project_ids(df_compare_to_set_full_plot):
    def add_dots(string):
        truncate_characters = 25
        if len(string) > truncate_characters:
            string = string[:truncate_characters] + '...'
        return string
    df_compare_to_set_full_plot['Project ID Truncated']=df_compare_to_set_full_plot['proj_name'].apply(add_dots)
    return df_compare_to_set_full_plot 

def create_multi_project_chart(df_compare_to_set_full_plot,
                               selected_project,
                               empty_project,
                               company_projects,
                               anonomyze,
                               name,
                               view_all_projects,
                               units,
                               color_discrete_sequence):
    fig3 = go.Figure()

    added_to_legend = set()

    color_mapping = {}
    if anonomyze == True:    
        color_mapping = {company_projects: color_discrete_sequence[0], 'Anonomous Company Projects': color_discrete_sequence[1]}

    
    if selected_project != empty_project:
        #add the selected project to the legend
        color_mapping[selected_project + ' (Selected Project)'] = color_discrete_sequence[2]

    

    for index, row in df_compare_to_set_full_plot.iterrows():
        show_legend = row['legend_val'] not in added_to_legend
        added_to_legend.add(row['legend_val'])

        if anonomyze == False and selected_project == empty_project:
            color_row = color_discrete_sequence[0]
        else:
            color_row = color_mapping[row['legend_val']]

        if units == 'kbtu/sf':
            hover_template_text = f"<b>Project ID: </b>{row['Project ID Truncated']}<br>" + f"<b>Total EUI (kBtu/SF): </b>{round(row['total_energy'],2)}<br>" + f"<b>Climate Zone: </b> {row['climate_zone']}<br>" + f"<b>Use Type Total Area (SF): </b> {round(row['use_type_total_area'],0)}<extra></extra>"

        else:
            hover_template_text = f"<b>Project ID: </b>{row['Project ID Truncated']}<br>" + f"<b>Total Energy Use (MBTU): </b>{round(row['total_energy'],0)}<br>" + f"<b>Climate Zone: </b> {row['climate_zone']}<br>" + f"<b>Use Type Total Area (SF): </b> {round(row['use_type_total_area'],0)}<extra></extra>"

        fig3.add_trace(go.Bar(x=[row['Project ID Truncated']], 
                            y=[row['total_energy']], 
                            name=row['legend_val'],
                            marker_color = color_row,
                            legendgroup=row['legend_val'],  # This groups legend items together
                            showlegend=show_legend,
                            hovertemplate=hover_template_text))
    
    #fig3 = px.bar(df_compare_to_set_full_plot, x='Project ID Truncated', y='total_energy', color='legend_val')
    #set the labels for the x axis to be the Project ID Truncated
    fig3.update_layout(xaxis_title = "Project ID")
    #set the labels for the x axis to be the Project ID Truncated

    #change the color of the bar where the project id is the same as selected_project to dark blue, rest of the bars light blue

    #fig3.update_traces(marker_color=np.where(df_compare_to_set_full_plot['project_id'] == selected_project, 'rgb(173, 216, 230)', 'rgb(0, 0, 255)'))
    if name != 'Admin User' and anonomyze == True and view_all_projects == True:

        #fig3.update_traces(marker_color=np.where(df_compare_to_set_full_plot['Company Name'] == company_name, 'rgb(0, 0, 255)', 'rgb(178, 172, 136)'))

        #add a legend to the chart showing the color of the selected project, the company's projects and the other projects
        fig3.update_layout(legend_title_text='Legend', legend=dict(
            yanchor = "top",
            y = 0.99,
            xanchor = "left",
            x = 0.01
        ))

    #add hover text to display the Use Type, Climate Zone and Total Area for each project
    

    fig3.update_layout(yaxis_title = units)

    #convert use_type_total_area to a string

    #add the custom data to the hover text
    fig3.update_traces(customdata = df_compare_to_set_full_plot[['climate_zone','use_type_total_area','project_id']])
    

    
    #change the color of the bar where the project id is the same as selected_project to dark blue, rest of the bars light blue
    fig3.update_layout(title_text = "EUI by Compare to Set Projects")

    return fig3


