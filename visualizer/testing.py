import pandas as pd


import build_visualize as bv
from constants import *
from pull_eeu_data import pull_eeu_data

from supabase import create_client, Client
import plotly.express as px
import os

#### SUPABASE SETUP ####
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


excluded_projects = ['recjWz8X88wyCPqQz+Ex_P2_Office-wDC']

df = pull_eeu_data(supabase)
print(df)
selected_project = '1771 Stream'
company_id_use='775404f2-340a-4338-b8e3-05246eedea9e'
project_list = bv.generate_project_list(df,list_type='projects',company_name='775404f2-340a-4338-b8e3-05246eedea9e')
company_list = bv.generate_project_list(df,list_type='companies')
project_phases = bv.generate_project_list(df,list_type='project_phases',company_name='775404f2-340a-4338-b8e3-05246eedea9e')
gsf_ranges = []
df_compare_to_set_list  = bv.generate_compare_to_set(df,project_selector="775404f2-340a-4338-b8e3-05246eedea9e",
                                                     climate_zone_selector="All",
                                                     use_type_selector="All",
                                                     gsf_ranges=gsf_ranges,
                                                     excluded_projects=excluded_projects,
                                                     anonomyze=False,
                                                     company_name=company_id_use,
                                                     energy_units='kbtu/sf')
df_compare_to_set = df_compare_to_set_list[0]
df_selected_project = bv.generate_selected_project(df,selected_project=selected_project,company_name='775404f2-340a-4338-b8e3-05246eedea9e',baseline_design='design',energy_units='kbtu/sf')

eui_avg = bv.return_metric(metric_name='eui',set_name='compare_to',df_compare_to_set=df_compare_to_set,energy_units='kbtu/sf')
project_area = bv.return_metric(metric_name='area',set_name='project_list',project_list=project_list,selected_project=selected_project)
df_compare_to_set_full = df_compare_to_set_list[1]

prep_output = bv.prep_chart_data(df_compare_to_set_full,selected_project)
df_compare_to_set_full_plot = prep_output[0]
df_compare_to_set_full_plot_placeholder = prep_output[1]
df_compare_to_set_reordered = prep_output[2]
df_compare_to_set_full_plot = bv.truncate_project_ids(df_compare_to_set_full_plot)


chart_color_scheme = "px.colors.qualitative.T10"



fig3 = bv.create_multi_project_chart(df_compare_to_set_full_plot=df_compare_to_set_full_plot,
                                        selected_project=selected_project,
                                        empty_project=False,
                                        company_projects="HOK Projects",
                                        anonomyze = True,
                                        name = 'HOK',
                                        view_all_projects = True,
                                        units = "kBtu/SF",
                                        color_discrete_sequence = chart_color_scheme)
fig3.show()


fig3 = bv.create_multi_project_chart(df_compare_to_set_full_plot=df_compare_to_set_full_plot,
                                        selected_project="--Select a Project--",
                                        empty_project="--Select a Project--",
                                        company_projects="All Projects",
                                        anonomyze = False,
                                        name = 'Admin User',
                                        view_all_projects = True,
                                        units = "kBtu/SF",
                                        color_discrete_sequence = chart_color_scheme)
fig3.show()


df_combined = bv.generate_combined(df_compare_to_set,df_selected_project)
gsf_avg = bv.return_metric(metric_name='gsf',set_name='compare_to',df_compare_to_set=df_compare_to_set)
gsf_proj = bv.return_metric(metric_name='gsf',set_name='selected_project',df_selected_project=df_selected_project)
eui_proj = bv.return_metric(metric_name='eui',set_name='selected_project',df_selected_project=df_selected_project,energy_units='kBtu/SF')

climate_zone = bv.return_metric(metric_name='climate_zone',set_name='compare_to',df_compare_to_set=df_compare_to_set_full,selected_project=selected_project)
#se_type = bv.return_metric(metric_name='use_type',set_name='compare_to',df_compare_to_set=df_compare_to_set_full,selected_project=selected_project)
#area = bv.return_metric(metric_name='area',set_name='compare_to',df_compare_to_set=df_compare_to_set_full,selected_project=selected_project)
print('done')



