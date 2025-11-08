import streamlit as st
import pandas as pd
import plotly.express as px

# Configure Streamlit to use wide mode
st.set_page_config(layout="wide", page_title="D3P BEM Reports Visualizer")
import build_visualize as bv
import numpy as np
import plotly.graph_objects as go
from constants import chart_types
from streamlit.components.v1 import html
from st_btn_select import st_btn_select
from streamlit_elements import elements, mui, html as elements_html
from pull_eeu_data import pull_eeu_data
import os

if os.environ.get('ENV', 'local').lower() == 'local':
    print("Loading .env file for visualizer...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"Looking for .env at: {env_path}")
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print("After loading .env file:")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_SERVICE_ROLE: {os.getenv('SUPABASE_SERVICE_ROLE')}")

import streamlit as st

from supabase import create_client, Client


#### SUPABASE SETUP ####
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_ROLE")
print(f"Final values:")
print(f"url: {url}")
print(f"key: {key}")
supabase: Client = create_client(url, key)

token = st.query_params.get('token')



print("token"+str(token))

st.markdown(
    """
    <style>
    .block-container {
        margin-top: 0;
        padding-top: 0;
        padding-left: 2rem;
        padding-right: 0;
        }
    .css-nahz7x.e16nr0p34 {
        padding-top: 0;
        margin-top: -75;
    }
    /* Additional margin for main content area */
    .main .block-container {
        padding-left: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

chart_color_scheme = px.colors.qualitative.T10


# Authentication is handled via token parameter in URL

name ="775404f2-340a-4338-b8e3-05246eedea9e"

def get_company_name(supabase, **kwargs):
    company_id = kwargs.get('company_id',None)
    query = supabase.table('companies')\
            .select('company_name')\
            .eq('id', company_id)
        
    data, count = query.execute()
    
    if data[1] != []:
        df = pd.DataFrame(data[1])
        print("company_name found:")
        return df.loc[0,'company_name']
    else:
        return "no company found"

if token:
    data = supabase.auth.get_user(token)
    company_id = data.user.user_metadata['company_id']

    if name:
        company_name = get_company_name(supabase, company_id=company_id)

    if data:
        
        if company_name == 'Admin User':
            company_projects = 'All Projects'
            df_pull_eeu_data = pull_eeu_data(supabase)
        else:

            company_projects = company_name + ' Projects'
        if 'project_selector' not in st.session_state:
            st.session_state['project_selector'] = company_projects

            print("sess_state_proj:"+str(st.session_state['project_selector']))

        if 'view_all_projects' not in st.session_state:
            st.session_state['view_all_projects'] = False
            print("view_allProj:"+str(st.session_state['view_all_projects']))

        if 'units' not in st.session_state:
            st.session_state['units'] = 'kbtu/sf'

  
        # Define company_projects early for both cases
        company_projects = company_name + ' Projects'
        
        if name == 'Admin User':
        
            #this is the full set of projects
            print(st.session_state['units'])
            
            df = df_pull_eeu_data  # Set df for Admin User case
            user_company_id = None  # Set user_company_id for Admin User case
            companies = bv.generate_project_list(df_pull_eeu_data,list_type='companies')

                
            project_types = ['All Projects']+companies
            project_list = bv.generate_project_list(df_pull_eeu_data,list_type='projects')
            project_list_names = bv.generate_project_list(df_pull_eeu_data,list_type='project_names')
        else:
            if st.session_state['project_selector'] == "All Projects":
                st.session_state['view_all_projects'] = True
                df = df_pull_eeu_data = pull_eeu_data(supabase)
                user_company_id=None
            if st.session_state['view_all_projects'] != True:
                
                ##TO DO - need to add company filter
                user_company_id = data.user.user_metadata['company_id']
                print("user_company_id"+user_company_id)
                df = df_pull_eeu_data = pull_eeu_data(supabase,company_id=user_company_id)
            
            # These lines are now inside the else block where df is defined
            project_list = bv.generate_project_list(df,list_type='projects',company_id=user_company_id)
            project_list_names = bv.generate_project_list(df,list_type='project_names',company_id=user_company_id)
            project_types = [company_projects] + ['All Projects']
        
        # Store company projects for filter reset functionality
        st.session_state['company_projects'] = company_projects

        if 'project_selector' not in st.session_state:
            st.session_state['project_selector'] = company_projects

        climate_zones = bv.generate_project_list(df,list_type='climate_zone')
        use_types = bv.generate_project_list(df,list_type='use_type')
        gsf_ranges = bv.generate_project_list(df,list_type='gsf_range')
        #project_phases = bv.generate_project_list(df,list_type='project_phases')

        # Ensure lists exist before inserting
        if not isinstance(climate_zones, list):
            climate_zones = []
        if not isinstance(use_types, list):
            use_types = []
        climate_zones.insert(0,"All")
        use_types.insert(0,"All")

        project_phases = bv.generate_project_list(df,list_type='project_phases',company_id=user_company_id)
        if not isinstance(project_phases, list):
            project_phases = []
        project_phases.insert(0,"All")
        gsf_ranges = bv.return_gsf_ranges()
        print(project_list)
        # Handle empty project_list_names DataFrame
        if project_list_names.empty or 'proj_name' not in project_list_names.columns:
            project_list_use = []
        else:
            project_list_use = project_list_names['proj_name'].tolist()
        empty_project_val="-- Select a Project --"
        project_list_use.insert(0,empty_project_val)
        anonomyze = True
        # Handle filter reset flags before creating widgets
        if st.session_state.get('reset_climate_zone', False):
            st.session_state.climate_zone_selector = 'All'
            st.session_state['reset_climate_zone'] = False
            
        if st.session_state.get('reset_use_type', False):
            st.session_state.use_type_selector = 'All'
            st.session_state['reset_use_type'] = False
            
        if st.session_state.get('reset_gsf_ranges', False):
            st.session_state.gsf_ranges = []
            st.session_state['reset_gsf_ranges'] = False
            
        if st.session_state.get('reset_phase_selector', False):
            st.session_state.phase_selector = 'All'
            st.session_state['reset_phase_selector'] = False
            
        if st.session_state.get('reset_project_selector', False):
            st.session_state.project_selector = 'All Projects'
            st.session_state['reset_project_selector'] = False

        with st.sidebar:
            st.write("**Selected Project:**")
            selected_project = st.selectbox(
                'Project',
                project_list_use)


            with st.expander("Project Details"):
                if(name == 'Admin User'):
                
                    project_company_placeholder = st.empty()
                    anonomyze = False
                climate_zone_placeholder = st.empty()
                

                use_type_placeholder = st.empty()


                area_placeholder = st.empty()
            st.divider()
            value_placeholder = st.empty()


            project_selector = st.selectbox(
                'Projects',
                project_types,key='project_selector')
            
            if project_selector == 'All Projects':
                st.session_state['view_all_projects'] = True

            climate_zone_selector = st.selectbox(
                'Climate Zone',
                climate_zones,
                key='climate_zone_selector')


            use_type_selector = st.selectbox(
                'Use Type',
                use_types,
                key='use_type_selector')
        

            gsf_ranges = st.multiselect(
                'GSF Range',
                options=gsf_ranges['Name'].tolist(),
                key='gsf_ranges'
                )


            phase_selector = st.selectbox(
            'Project Phase',
            project_phases,
            key='phase_selector')

            with st.expander("Customize Project List"):
                project_list_with_combined_id = project_list.copy()
                project_list['Include'] = True

                #move the include column to the front
                cols = project_list.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                project_list = project_list[cols]

                include_projects = st.data_editor(project_list)
                

                df_excluded_projects = include_projects[include_projects['Include'] == False]

                project_list_with_combined_id=project_list_with_combined_id['project_id']
                df_excluded_projects_ids = df_excluded_projects.join(project_list_with_combined_id,how='inner',rsuffix='_right')

                excluded_projects = df_excluded_projects_ids['project_id'].tolist()

        project_selector = project_selector.replace(" Projects","")
        print("project_selector:"+project_selector)
        print("climate_zone_selector:"+climate_zone_selector)
        print("use_type_selector:"+use_type_selector)
        print("gsf_ranges:"+str(gsf_ranges))
        print("phase_selector:"+phase_selector)
        print("excluded_projects:"+str(excluded_projects))
        print("anonomyze:"+str(anonomyze))
        print("company_id:"+str(user_company_id))
        df_compare_to_set_list  = bv.generate_compare_to_set(df,project_selector = project_selector,
                                                            climate_zone_selector = climate_zone_selector,
                                                            use_type_selector = use_type_selector,
                                                            gsf_ranges = gsf_ranges,
                                                            phase_selector=phase_selector,
                                                            excluded_projects = excluded_projects,
                                                            anonomyze = anonomyze,
                                                            company_id = company_id,
                                                            company_name = company_name,
                                                            energy_units = st.session_state['units'])
        print("UNITS NOW"+st.session_state['units'])
        df_compare_to_set = df_compare_to_set_list[0]

        df_compare_to_set_full = df_compare_to_set_list[1]
        
        # Prepare chart data for custom visualizations
        prep_output = bv.prep_chart_data(df_compare_to_set_full, selected_project)
        df_compare_to_set_full_plot = prep_output[0]
        df_compare_to_set_full_plot_placeholder = prep_output[1]
        df_compare_to_set_reordered = prep_output[2]
        
        # Custom visualizations section - at the very top
        from custom_visualizations import CustomVisualizationManager
        custom_viz_manager = CustomVisualizationManager(chart_color_scheme, supabase)
        custom_viz_manager.render_custom_visualizations(
            df_compare_to_set_full_plot, df_compare_to_set_full, 
            project_list, project_list_names, df, company_id
        )
        
        df_compare_to_set_list_bl  = bv.generate_compare_to_set(df,
                                                                project_selector = project_selector,
                                                                climate_zone_selector = climate_zone_selector,
                                                                use_type_selector = use_type_selector,
                                                                baseline_design = 'baseline', 
                                                                gsf_ranges = gsf_ranges,phase_selector=phase_selector,
                                                                excluded_projects = excluded_projects,
                                                                anonomyze = anonomyze,
                                                                company_id=user_company_id,
                                                                company_name = company_name,
                                                                energy_units = st.session_state['units'])
        df_compare_to_set_bl = df_compare_to_set_list_bl[0]
        num_projs = str(bv.return_num_projects_in_set(df_compare_to_set_full))
        if selected_project != empty_project_val:
            empty_project = False

            df_selected_project = bv.generate_selected_project(df,selected_project,company_id,baseline_design='design',energy_units = st.session_state['units'])
            df_main_selected_combined = bv.generate_combined(df_compare_to_set,df_selected_project)
            df_main_selected_combined_plot = df_main_selected_combined[df_main_selected_combined['eeu'] != 'use_type_total_area']
            project_climate_zone = bv.return_metric(metric_name='climate_zone',set_name='project_list',
                                        project_list=project_list,
                                        selected_project=selected_project)
            
            project_company = bv.return_metric(metric_name='project_company',set_name='project_list',
                                                project_list=project_list,
                                                selected_project=selected_project)
            project_use_type = bv.return_metric(metric_name='use_type',set_name='project_list',
                                        project_list=project_list,
                                        selected_project=selected_project)
            project_area = bv.return_metric(metric_name='area',set_name='project_list',project_list=project_list,selected_project=selected_project)
            #format the project_area to have commas and no decimals
            project_area = "{:,}".format(float(project_area))
            # Get project_id for the URL link
            try:
                project_id = project_list.loc[project_list['proj_name'] == selected_project, 'project_id'].iloc[0]
            except:
                project_id = None
        else:
            df_main_selected_combined_plot = df_compare_to_set.copy()
            df_main_selected_combined_plot = df_main_selected_combined_plot[df_main_selected_combined_plot['eeu'] != 'use_type_total_area']
            empty_project = True
            df_selected_project = pd.DataFrame()
            project_climate_zone = '--'
            project_company = '--'
            project_use_type = '--'
            project_area = '--'
            project_id = None

        if(name == 'Admin User'):
            project_company_placeholder.write("**Company:** "+project_company)


        climate_zone_placeholder.write("**Climate Zone:** "+project_climate_zone)
        use_type_placeholder.write("**Use Type:** "+project_use_type)


        area_placeholder.write("**Use Type Area (SF):** "+project_area)
        # Update the value of the placeholder
        value_placeholder.write(f"**Compare to Set** ({num_projs} Projects)")

        selected_unit = st.radio("Chart Units",('kbtu/sf','MBTU'),key='units',horizontal=True)
        #selected_unit = "MBTU"
        #selected_unit = st_btn_select("'kBtu/SF','MBTU'",key='units')

        if selected_unit != st.session_state['units']:
           st.session_state['units'] = selected_unit

        chart_placeholder = st.empty()

        #creates three columns to center the drop down
        col1, col2,col3 = st.columns([1,3,1])
        with col1:
            st.write('')
        with col2:
            chart_selector = st.selectbox("Chart Type",["Selected Project vs. Compare to Set",
                                                        "Multi Project",
                                                        "Energy Uses",
                                                        "Fuel Source + Stacked End Use"])
        with col3:
            def convert_df(df):

                return df.to_csv().encode('utf-8')


            if chart_selector == chart_types['multi_project_chart']:

                st.write('')
                st.write('')
                download_placeholder = st.empty()


        try:
            df_selected_project_bl = bv.generate_selected_project(df,selected_project,company_id,baseline_design='baseline',energy_units = st.session_state['units'])
        except Exception as err:
            df_selected_project_bl = pd.DataFrame()
        try:
            eui_proj_bl_int = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='selected_project',df_selected_project=df_selected_project_bl,format='int')
        except Exception as err:
            eui_proj_bl_int = 0
        try:
            eui_proj_bl = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='selected_project',df_selected_project=df_selected_project_bl)
        except Exception as err:
            eui_proj_bl = '--'
        eui_avg_bl = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='compare_to',df_compare_to_set=df_compare_to_set_bl,format='int') 
        
        col1, col2= st.columns(2)
        st.markdown(
                """
            <style>
            [data-testid="stMetricValue"] {
            font-size: 25px;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )
        with col1:
            if empty_project:
                gsf_proj = '--'
            else:
                gsf_proj = bv.return_metric(metric_name='gsf',set_name='selected_project',df_selected_project=df_selected_project)

            st.metric(label="This Project", value=gsf_proj)
        with col2:
            #return the average value for use_type_total_area within df
            gsf_set_avg = bv.return_metric(metric_name='gsf',set_name='compare_to',df_compare_to_set=df_compare_to_set)
            st.metric(label="Compare to Set ("+num_projs+" projects)", value=gsf_set_avg)

        # second row of data
        col1, col2= st.columns(2)
        with col1:
            try:
                eui_proj = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='selected_project',df_selected_project=df_selected_project)
            except:
                eui_proj = '--'
            try:
                eui_proj_int = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='selected_project',df_selected_project=df_selected_project,format='int')
            except:
                eui_proj_int = 0
            if(eui_proj_bl_int != 0):
                delta_eui = (eui_proj_int - eui_proj_bl_int)/eui_proj_bl_int
                #format delta_eui as a percentage with 2 decimal places
                delta_eui = "{:.2%}".format(delta_eui)
            else:
                delta_eui = ''
            st.metric(label="Energy This Project (Design)", value=eui_proj,delta=delta_eui,delta_color="inverse",help="Delta Value is Compared to Baseline Project File")

        with col2:
            eui_avg = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='compare_to',df_compare_to_set=df_compare_to_set)
            eui_avg_int = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='compare_to',df_compare_to_set=df_compare_to_set,format='int')
            try:
                delta_avg_eui = (eui_avg_int - eui_avg_bl)/eui_avg_bl
            except:
                delta_avg_eui = 0
            #format delta_avg_eui as a percentage with 2 decimal places
            delta_avg_eui = "{:.2%}".format(delta_avg_eui)
            st.metric(label="Energy Compare to Set (Design)", value=eui_avg,delta=delta_avg_eui,delta_color="inverse",help="Delta Value is Compared to Baseline Projects within the Compare to Set")
        
        col1, col2= st.columns(2)
        with col1:
            st.metric(label="Energy This Project (Baseline)", value=eui_proj_bl)

        with col2:
            eui_avg = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='compare_to',df_compare_to_set=df_compare_to_set)
            eui_avg_int = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='compare_to',df_compare_to_set=df_compare_to_set,format='int')
            eui_avg_bl = bv.return_metric(metric_name='eui',energy_units=st.session_state['units'],set_name='compare_to',df_compare_to_set=df_compare_to_set_bl) 
            st.metric(label="Energy Compare to Set (Baseline)", value=eui_avg_bl)
            
        with st.expander("See Details by EEU Type"):
            cols = bv.cols
            plot_selector=st.selectbox("EEU Detail View",cols)
            st.write("This view displays the distribution of the "+plot_selector+" EEU for the compare to set.")
            df_plot=df_compare_to_set_full[plot_selector].to_frame()
            print(type(df_plot))
            print("histogram plot df:")
            print(df_plot)
            df_plot=df_plot.loc[df_plot[plot_selector]!=0]
            fig2 = px.histogram(df_plot, x=plot_selector,marginal="rug")
            fig2.update_layout(xaxis_title=plot_selector+" "+st.session_state['units'])
            fig2.update_layout(yaxis_title="Number of Projects")
            fig2.update_layout(title_text=plot_selector+" Distribution for Compare to Set")
            st.plotly_chart(fig2, use_container_width=True)
        #st.dataframe(df3)
        
        st.write("Compare to Set View (ADMIN VIEW ONLY)")
        
        #create two tabs, one for "Chart View" and one for "Table View"
        tab1, tab2 = st.tabs(["Chart View", "Table View"])
        
        with tab1:
            

            fig3 = px.bar(df_compare_to_set_full_plot, x='total_energy', y='proj_name', orientation='h')
            #order the projects in descending order of total_energy\

            if st.session_state['units'] == 'kbtu/sf':
                chart_title = "Total Energy Use Intensity (kBtu/SF) for Compare to Set"
                fig3.update_traces(hovertemplate="<br>".join([
                    "Project ID: %{y}",
                    "Total Energy Use Intensity (kBtu/SF): %{x}",
                    "Climate Zone: %{customdata[0]}",
                    "Use Type Total Area (SF): %{customdata[1]}",
                    "Total Electricity (kBtu/SF): %{customdata[2]}",
                    "Total Natural Gas (kBtu/SF): %{customdata[3]}",
                    "Total District Heating (kBtu/SF): %{customdata[4]}",
                    "Total Other (kBtu/SF): %{customdata[5]}"
                    ]))
            else:
                chart_title = "Total Energy Use (MBTU) for Compare to Set"
                fig3.update_traces(hovertemplate="<br>".join([
                        "Project ID: %{y}",
                        "Total Energy Use (MBTU): %{x}",
                        "Climate Zone: %{customdata[0]}",
                        "Use Type Total Area (SF): %{customdata[1]}",
                        "Total Electricity (MBTU): %{customdata[2]}",
                        "Total Natural Gas (MBTU): %{customdata[3]}",
                        "Total District Heating (MBTU): %{customdata[4]}",
                        "Total Other (MBTU): %{customdata[5]}"
                        ]))
            fig3.update_layout(title_text=chart_title)
            #add a tool tip with data from the df_compare_to_set_full_plot dataframe  for the corresponding row climate zone, use_type_total_area, total_electricity, total_NaturalGas, total_DistrictHeating, total_other
            #format the tool tip to display numbers with commas and no decimal places


            fig3.update_traces(customdata=df_compare_to_set_full_plot[['climate_zone','use_type_total_area','total_Electricity','total_NaturalGas','total_DistrictHeating','total_Other']])

            st.plotly_chart(fig3, use_container_width=True)

        with tab2:
            
            st.dataframe(df_compare_to_set_reordered)



        # set the placeholder chart to display the chart selected in the drop down
        print(chart_selector)
        df_compare_to_set_full_plot = bv.truncate_project_ids(df_compare_to_set_full_plot)

        if(chart_selector == 'Multi Project'):
        
            
            if name == "Admin User":
                #create a chart where the x axis is the project ID and the y axis is the total_energy
                #create a column in df_compare_to_set_full_plot called Project ID Truncated that is the first 25 characters of the Project ID

                fig3 = px.bar(df_compare_to_set_full_plot, x='Project ID Truncated', y='total_energy')
                #set the labels for the x axis to be the Project ID Truncated
                fig3.update_layout(xaxis_title="Project ID")


                #set the labels for the x axis to be the Project ID Truncated

                #change the color of the bar where the project id is the same as selected_project to dark blue, rest of the bars light blue



                fig3.update_traces(marker_color=np.where(df_compare_to_set_full_plot['proj_name'] == selected_project, chart_color_scheme[0], chart_color_scheme[1]))
                #add hover text to display the Use Type, Climate Zone and Total Area for each project
                if st.session_state['units'] == 'kbtu/sf':
                    fig3.update_traces(hovertemplate="<br>".join([
                        "Project ID: %{customdata[2]}",
                        "Total Energy Use Intensity (kBtu/SF): %{y}",
                        "Climate Zone: %{customdata[0]}",
                        "Use Type Total Area (SF): %{customdata[1]}"
                        ]))
                else:
                    fig3.update_traces(hovertemplate="<br>".join([
                        "Project ID: %{customdata[2]}",
                        "Total Energy Use (MBTU): %{y}",
                        "Climate Zone: %{customdata[0]}",
                        "Use Type Total Area (SF): %{customdata[1]}"
                        ]))

                fig3.update_layout(yaxis_title=st.session_state['units'])

                #convert use_type_total_area to a string

                #add the custom data to the hover text
                fig3.update_traces(customdata=df_compare_to_set_full_plot[['climate_zone','use_type_total_area','proj_name']])
                

                
                #change the color of the bar where the project id is the same as selected_project to dark blue, rest of the bars light blue
                fig3.update_layout(title_text="EUI by Compare to Set Projects")


            else:
                fig3 = bv.create_multi_project_chart(df_compare_to_set_full_plot=df_compare_to_set_full_plot,
                                                    selected_project=selected_project,
                                                    empty_project=empty_project,
                                                    company_projects=company_projects,
                                                    anonomyze = anonomyze,
                                                    name = name,
                                                    view_all_projects = st.session_state['view_all_projects'],
                                                    units = st.session_state['units'],
                                                    color_discrete_sequence = chart_color_scheme,)

            df_export = bv.export_chart_data(chart_types['multi_project_chart'],df_compare_to_set_full_plot)
            csv = convert_df(df_export)
            download_placeholder.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name='d3p_multi_project.csv',
                    mime='text/csv',
                    )                               
            
            chart_placeholder.plotly_chart(fig3, use_container_width=True)
        elif(chart_selector == 'Energy Uses'):
            #create a chart with a stacked bar chart with the x axis as the project ID and the y axis as the total_energy, with the stacked bars being the different energy uses
            fig4 = px.bar(df_compare_to_set_full_plot, x='Project ID Truncated', y=['total_Electricity','total_NaturalGas','total_DistrictHeating','total_Other'],barmode='stack',
                        color_discrete_sequence = chart_color_scheme,)
            fig4.update_layout(title_text="Energy Uses by Compare to Set Projects")
            #make the selected project's label bold
            if st.session_state['units'] == 'kbtu/sf':
                fig4.update_layout(yaxis_title="EUI (kBtu/SF)")
            else:
                fig4.update_layout(yaxis_title="Energy Use (MBTU)")
            fig4.update_layout(xaxis_title="Projects")
            if st.session_state['units'] == 'kbtu/sf':
                fig4.update_traces(hovertemplate="<br>".join([
                    "Project ID: %{customdata[2]}",
                    "Total Energy Use Intensity (kBtu/SF): %{y}",
                    "Climate Zone: %{customdata[0]}",
                    "Use Type Total Area (SF): %{customdata[1]}"
                    ]))
            else:
                fig4.update_traces(hovertemplate="<br>".join([
                    "Project ID: %{customdata[2]}",

                    "Total Energy Use (MBTU): %{y}",
                    "Climate Zone: %{customdata[0]}",
                    "Use Type Total Area (SF): %{customdata[1]}"
                    ]))
            fig4.update_traces(customdata=df_compare_to_set_full_plot[['climate_zone','use_type_total_area','proj_name']])
            chart_placeholder.plotly_chart(fig4, use_container_width=True)
            

        elif(chart_selector == 'Fuel Source + Stacked End Use'):
            
            if empty_project:
                
                chart_placeholder.write("**Please select a project to view this chart.**")
            else:
                #create a chart for the df_selected_project df with a stacked bar chart with the x axis as energy type and the y axis as the total_energy, with the stacked bars being the different eeu types
                df_selected_project_energy_types = bv.add_energy_types_selected_table(df_selected_project)
                
                
                #add a title to chart with the project id in it

                #remove rows where value is 0
                df_selected_project_energy_types = df_selected_project_energy_types[df_selected_project_energy_types['value'] != 0]
                fig5 = px.bar(df_selected_project_energy_types, y='value', x='fuel_source',color='eeu',barmode='stack',color_discrete_sequence = chart_color_scheme)
                #add a title of Project ID of selected project - EUI by Energy Type


                if st.session_state['units'] == 'kbtu/sf':
                    fig5.update_layout(title_text=selected_project+" - EUI by Energy Type")
                    fig5.update_layout(yaxis_title="EUI (kBtu/SF)")
                else:
                    fig5.update_layout(title_text=selected_project+" - Energy Use by Energy Type")
                    fig5.update_layout(yaxis_title="Energy Use (MBTU)")
                fig5.update_layout(xaxis_title="Energy Type")
                chart_placeholder.plotly_chart(fig5, use_container_width=True)
        elif(chart_selector == 'Selected Project vs. Compare to Set'):
            #remove rows where value is 0
            df_main_selected_combined_plot = df_main_selected_combined_plot[df_main_selected_combined_plot['value'] != 0]
            #remove rows where eeu starts with total_ 
            df_main_selected_combined_plot = df_main_selected_combined_plot[~df_main_selected_combined_plot['eeu'].str.startswith('total_')]
            #reorder the bars so that the selected project is first

            def custom_sort(item):
                # The selected project is a special case.
                if item == selected_project:
                    return 0  # Always sort this first.
                else:
                    # Otherwise, sort alphabetically (or numerically, or however you like).
                    return 1

            # Then, apply this function to sort your DataFrame.

            df_main_selected_combined_plot['SortColumn'] = df_main_selected_combined_plot['project_name'].apply(custom_sort)
            df_main_selected_combined_plot = df_main_selected_combined_plot.sort_values('SortColumn')
            df_main_selected_combined_plot = df_main_selected_combined_plot.drop('SortColumn', axis=1)
            
            fig = px.histogram(df_main_selected_combined_plot, x="eeu", y="value",
                        color='project_name', barmode='group',
                        labels={
                                "eeu": "EEU Type",
                                "value": st.session_state['units'],
                                "project_name": "Legend"
                            },

                            
                            color_discrete_sequence = chart_color_scheme,
            )
            #add a title EUI by EEU Type for Selected Project vs. Compare to Set
            if st.session_state['units'] == 'kbtu/sf':
                text_title_type = "EUI"
            else:
                text_title_type = "Energy Use"
            if empty_project:
                title_text_use = text_title_type + " by EEU Type for Compare to Set"
            else:
                title_text_use = text_title_type + " by EEU Type for "+selected_project+" vs. Compare to Set"
            fig.update_layout(title_text=title_text_use)
            #add a yaxis title of EUI (kBtu/SF) or Energy Use (MBTU)
            fig.update_layout(yaxis_title=st.session_state['units'])
            #put the legend on the bottom
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))

            chart_placeholder.plotly_chart(fig, use_container_width=True)
            #st.plotly_chart(fig, use_container_width=True)
    
else:
    st.error('You could not be authenticated')

