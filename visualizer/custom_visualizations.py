"""
Custom Visualization Module for D3P BEM Reports

This module handles all custom visualization functionality including:
- Scatter plots with interactive features
- Project details panels
- Color selector controls
- Performance metrics calculations
- Baseline data processing
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from streamlit_elements import elements, mui
import build_visualize as bv


class CustomVisualizationManager:
    """Manages custom visualizations and interactive features"""
    
    def __init__(self, chart_color_scheme, supabase_client):
        self.chart_color_scheme = chart_color_scheme
        self.supabase = supabase_client
    
    def render_custom_visualizations(self, df_compare_to_set_full_plot, df_compare_to_set_full, 
                                   project_list, project_list_names, df, company_id):
        """Main entry point for custom visualization section"""
        
        st.write("Custom Visualizations")
        
        # Render filter pills above the visualization
        self._render_filter_pills()
        
        # Get visualization options from Supabase
        viz_options = self.supabase.table('data_viz_chart_options').select(
            'visualization_name', 'x_axis_field', 'y_axis_field', 
            'x_axis_label', 'y_axis_label', 'x_axis_units', 'y_axis_units'
        ).execute()
        viz_options_df = pd.DataFrame(viz_options.data)
        
        # Create dropdown for visualization selection
        if not viz_options_df.empty:
            selected_viz = st.selectbox(
                'Select Visualization',
                viz_options_df['visualization_name'].tolist()
            )
            
            # Get the configuration for the selected visualization
            selected_viz_config = viz_options_df[
                viz_options_df['visualization_name'] == selected_viz
            ].iloc[0]
            
            # Render the scatter plot with interactive features
            self._render_scatter_plot_with_details(
                df_compare_to_set_full_plot, df_compare_to_set_full,
                selected_viz_config, project_list, 
                project_list_names, df, company_id
            )
        else:
            st.warning("No custom visualizations available")
    
    def _render_scatter_plot_with_details(self, df_compare_to_set_full_plot, df_compare_to_set_full,
                                        viz_config, project_list, 
                                        project_list_names, df, company_id):
        """Render scatter plot with interactive project details"""
        
        # Extract fields and labels from config
        x_field = viz_config['x_axis_field']
        y_field = viz_config['y_axis_field']
        x_label = viz_config.get('x_axis_label', x_field)
        y_label = viz_config.get('y_axis_label', y_field)
        x_units = viz_config.get('x_axis_units', '')
        y_units = viz_config.get('y_axis_units', '')
        selected_viz = viz_config['visualization_name']
        
        # Create formatted axis labels with units
        x_axis_label = f"{x_label} ({x_units})" if x_units else x_label
        y_axis_label = f"{y_label} ({y_units})" if y_units else y_label
        
        # Create side-by-side layout with scatter plot on left and project details on right
        if x_field in df_compare_to_set_full_plot.columns and y_field in df_compare_to_set_full_plot.columns:
            
            # Initialize color selector state if not exists
            if "scatter_color_by" not in st.session_state:
                st.session_state.scatter_color_by = "Use Type"
            
            # Determine color column and legend title based on current selection
            color_column, legend_title = self._get_color_mapping(st.session_state.scatter_color_by)
            
            # Create scatter plot
            fig_custom = self._create_scatter_plot(
                df_compare_to_set_full_plot, x_field, y_field, 
                color_column, legend_title, selected_viz,
                x_axis_label, y_axis_label
            )
            
            # Create two columns: chart on left (65%), details on right (35%)
            chart_col, details_col = st.columns([0.65, 0.35])
            
            with chart_col:
                # Display the scatter plot
                selected_point = st.plotly_chart(
                    fig_custom, use_container_width=True, 
                    key="custom_viz", on_select="rerun"
                )
                
                # Color selector for scatter plot (below the chart)
                self._render_color_selector()
            
            with details_col:
                # Render project details panel
                self._render_project_details_panel(
                    selected_point, df_compare_to_set_full_plot, df_compare_to_set_full,
                    project_list, project_list_names, df, company_id
                )
        else:
            st.warning(f"One or both of the selected fields ({x_field}, {y_field}) are not available in the dataset")
    
    def _get_color_mapping(self, selected_color_by):
        """Get color column and legend title based on selection"""
        if selected_color_by == "Climate Zone":
            return 'climate_zone', "Climate Zone"
        else:  # Use Type
            return 'project_use_type', "Building Type"
    
    def _create_scatter_plot(self, df_plot, x_field, y_field, color_column, legend_title, title, x_axis_label, y_axis_label):
        """Create the scatter plot with proper styling"""
        
        # Sort data by color column if it's climate zone for alphabetical ordering
        if color_column == 'climate_zone':
            df_plot = df_plot.sort_values(by='climate_zone')
        
        fig_custom = px.scatter(
            df_plot,
            x=x_field,
            y=y_field,
            color=color_column,
            title=f'{title}',
            labels={
                x_field: x_axis_label,
                y_field: y_axis_label
            },
            color_discrete_sequence=self.chart_color_scheme,
            custom_data=['proj_name', 'climate_zone', 'use_type_total_area', 
                       'total_energy', 'total_Electricity', 'total_NaturalGas',
                       'total_DistrictHeating', 'total_Other']
        )
        
        # Configure legend positioning
        fig_custom.update_layout(
            showlegend=True,
            legend=dict(
                title=legend_title,
                orientation="h",  # Horizontal legend
                yanchor="top",
                y=-0.35,  # Position further below the chart
                xanchor="center", 
                x=0.5,  # Center horizontally
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1
            ),
            margin=dict(b=150)  # Increased bottom margin for legend
        )
        
        # Update hover template
        fig_custom.update_traces(
            hovertemplate="<br>".join([
                "<b>%{customdata[0]}</b>",  # Project name
                f"{x_axis_label}: %{{x:,.1f}}",
                f"{y_axis_label}: %{{y:,.1f}}",
                "Building Area: %{customdata[2]:,.0f} SF",
                "Climate Zone: %{customdata[1]}",
                "Total Energy: %{customdata[3]:,.1f}",
                "<extra></extra>"  # Remove default trace box
            ])
        )
        
        return fig_custom
    
    def _render_color_selector(self):
        """Render the color selector below the chart"""
        color_by_options = ["Use Type", "Climate Zone"]
        selected_color_by = st.selectbox(
            "🎨 Color Projects by:",
            options=color_by_options,
            index=color_by_options.index(st.session_state.scatter_color_by),
            key="scatter_color_selector"
        )
        # Update session state and trigger rerun if selection changed
        if selected_color_by != st.session_state.scatter_color_by:
            st.session_state.scatter_color_by = selected_color_by
            st.rerun()
    
    def _render_project_details_panel(self, selected_point, df_compare_to_set_full_plot, 
                                    df_compare_to_set_full, project_list, project_list_names, 
                                    df, company_id):
        """Render the project details panel on the right side"""
        
        if selected_point and selected_point.selection and len(selected_point.selection.points) > 0:
            point_data = selected_point.selection.points[0]
            proj_name = point_data['customdata'][0]
            project_data = df_compare_to_set_full_plot[
                df_compare_to_set_full_plot['proj_name'] == proj_name
            ].iloc[0]
            
            # Create tabs for Performance and Opportunities
            tab1, tab2 = st.tabs(["Performance", "Opportunities"])
            
            with tab1:  # Performance Tab
                self._render_performance_tab(
                    proj_name, project_data, df_compare_to_set_full,
                    project_list, project_list_names, df, company_id
                )
            
            with tab2:  # Opportunities Tab
                self._render_opportunities_tab()
        
        else:
            # Show message when no point is selected
            with elements("no_selection"):
                with mui.Paper(sx={
                    "p": 3, "height": "200px", "display": "flex", 
                    "alignItems": "center", "justifyContent": "center", 
                    "elevation": 0, "boxShadow": "none"
                }):
                    mui.Typography(
                        "Click a point on the chart to see project details", 
                        variant="body1", sx={"color": "#666", "fontStyle": "italic"}
                    )
    
    def _render_performance_tab(self, proj_name, project_data, df_compare_to_set_full,
                              project_list, project_list_names, df, company_id):
        """Render the performance metrics tab"""
        
        with elements("baseline_details"):
            with mui.Paper(sx={
                "px": 0, "py": 2, "height": "700px", "overflow": "auto", 
                "backgroundColor": "#f8f9fa", "elevation": 0, "boxShadow": "none"
            }):
                # Project Details Section
                self._render_project_basic_info(proj_name, project_list, project_list_names)
                
                # Performance Metrics Section
                self._render_performance_metrics(
                    proj_name, project_data, df_compare_to_set_full, 
                    project_list, project_list_names, df, company_id
                )
    
    def _render_project_basic_info(self, proj_name, project_list, project_list_names):
        """Render basic project information"""
        
        with mui.Box(sx={"mb": 3}):
            # Project Name with link
            chart_project_id = None
            try:
                chart_project_id = project_list.loc[
                    project_list['proj_name'] == proj_name, 'project_id'
                ].iloc[0]
            except:
                chart_project_id = None
            
            mui.Typography(f"{proj_name}", variant="subtitle1", sx={"fontWeight": "bold", "mb": 1})
            
            # Use Type and Building Area
            self._render_project_details_grid(proj_name, project_list, project_list_names)
    
    def _render_project_details_grid(self, proj_name, project_list, project_list_names):
        """Render project details in a grid layout without headers"""
        
        with mui.Grid(container=True, spacing=1):
            with mui.Grid(item=True, xs=6):
                project_use_type_display = self._get_project_metric(
                    'use_type', proj_name, project_list, project_list_names
                )
                mui.Typography(project_use_type_display, variant="body2")
            
            with mui.Grid(item=True, xs=6):
                project_area_display = self._get_project_metric(
                    'area', proj_name, project_list, project_list_names
                )
                project_area_formatted = self._format_area(project_area_display)
                mui.Typography(project_area_formatted, variant="body2")
        
        # Location (without header)
        project_climate_zone_display = self._get_project_metric(
            'climate_zone', proj_name, project_list, project_list_names
        )
        location_display = f"Climate Zone {project_climate_zone_display}"
        mui.Typography(location_display, variant="body2", sx={"mt": 1})
    
    def _get_project_metric(self, metric_name, proj_name, project_list, project_list_names):
        """Get a specific metric for a project"""
        if proj_name in project_list_names['proj_name'].values:
            return bv.return_metric(
                metric_name=metric_name, set_name='project_list', 
                project_list=project_list, selected_project=proj_name
            )
        return "Unknown"
    
    def _format_area(self, area_value):
        """Format area value with proper formatting"""
        if area_value != "Unknown" and area_value != "--":
            try:
                return "{:,} ft²".format(float(area_value))
            except:
                return "Unknown"
        return "Unknown"
    
    def _render_kpi_section(self, project_data, df_compare_to_set_full, baseline_data, has_baseline_data):
        """Render Key Performance Indicators section"""
        
        # Show "--" if no baseline data, otherwise calculate savings
        if not has_baseline_data:
            energy_display = "--"
            carbon_display = "--"
        else:
            # Calculate energy savings percentage
            energy_savings = self._calculate_energy_savings(project_data, df_compare_to_set_full, baseline_data, has_baseline_data)
            # Calculate carbon savings percentage  
            carbon_savings = self._calculate_carbon_savings(project_data, df_compare_to_set_full, baseline_data, has_baseline_data)
            energy_display = f"{energy_savings:.1f}%"
            carbon_display = f"{carbon_savings:.1f}%"
        
        with mui.Box(sx={
            "display": "flex", "gap": 1, "mb": 1,
            "border": "1px solid #2e7d32", "borderRadius": 0.5,
            "backgroundColor": "#f8f9fa", "maxWidth": "300px"
        }):
            # Energy Savings KPI
            with mui.Box(sx={
                "flex": 1, "p": 1, "textAlign": "center",
                "backgroundColor": "#ffffff", "borderRadius": 0.5
            }):
                mui.Typography(energy_display, variant="body1", sx={
                    "fontWeight": "bold", "color": "#333", "mb": 0.25, "fontSize": "14px"
                })
                mui.Typography("% Energy Savings", variant="caption", sx={
                    "color": "#666", "fontSize": "10px"
                })
            
            # Carbon Savings KPI
            with mui.Box(sx={
                "flex": 1, "p": 1, "textAlign": "center",
                "backgroundColor": "#ffffff", "borderRadius": 0.5
            }):
                mui.Typography(carbon_display, variant="body1", sx={
                    "fontWeight": "bold", "color": "#333", "mb": 0.25, "fontSize": "14px"
                })
                mui.Typography("% Carbon Savings", variant="caption", sx={
                    "color": "#666", "fontSize": "10px"
                })
    
    def _calculate_energy_savings(self, project_data, df_compare_to_set_full, baseline_data, has_baseline_data):
        """Calculate energy savings percentage"""
        try:
            # Get total energy consumption for project
            project_total = self._get_total_energy_consumption(project_data)
            
            # Get baseline or comparison total
            if has_baseline_data and baseline_data is not None:
                baseline_total = self._get_total_energy_consumption(baseline_data)
                if baseline_total > 0:
                    return ((baseline_total - project_total) / baseline_total) * 100
            elif len(df_compare_to_set_full) > 0:
                comparison_total = self._get_total_energy_consumption(df_compare_to_set_full.select_dtypes(include=[np.number]).mean())
                if comparison_total > 0:
                    return ((comparison_total - project_total) / comparison_total) * 100
        except:
            pass
        return 0.0
    
    def _calculate_carbon_savings(self, project_data, df_compare_to_set_full, baseline_data, has_baseline_data):
        """Calculate carbon savings percentage"""
        try:
            # Get total carbon emissions for project
            project_total = self._get_total_carbon_emissions(project_data)
            
            # Get baseline or comparison total
            if has_baseline_data and baseline_data is not None:
                baseline_total = self._get_total_carbon_emissions(baseline_data)
                if baseline_total > 0:
                    return ((baseline_total - project_total) / baseline_total) * 100
            elif len(df_compare_to_set_full) > 0:
                comparison_total = self._get_total_carbon_emissions(df_compare_to_set_full.select_dtypes(include=[np.number]).mean())
                if comparison_total > 0:
                    return ((comparison_total - project_total) / comparison_total) * 100
        except:
            pass
        return 0.0
    
    def _get_total_energy_consumption(self, data):
        """Get total energy consumption from data"""
        try:
            # Sum all energy-related fields
            energy_fields = [col for col in data.index if 'Electricity' in col or 'NaturalGas' in col or 'DistrictHeating' in col]
            return sum(float(data[field]) for field in energy_fields if pd.notna(data[field]))
        except:
            return 0.0
    
    def _get_total_carbon_emissions(self, data):
        """Get total carbon emissions from data"""
        try:
            # For now, use energy consumption as proxy for carbon emissions
            # In a real implementation, you'd apply carbon factors
            return self._get_total_energy_consumption(data) * 0.5  # Simplified carbon factor
        except:
            return 0.0

    def _render_performance_metrics(self, proj_name, project_data, df_compare_to_set_full,
                                  project_list, project_list_names, df, company_id):
        """Render detailed performance metrics"""
        
        # Get baseline data for this specific project
        baseline_data, has_baseline_data = self._get_baseline_data(proj_name, df, company_id)
        
        with mui.Box(sx={"mb": 2}):
            mui.Typography("Performance Metrics Summary", variant="h6", sx={"mb": 1, "color": "#2e7d32"})
            
            # Details text with link icon
            # Get project ID for the link
            chart_project_id = None
            try:
                chart_project_id = project_list.loc[
                    project_list['proj_name'] == proj_name, 'project_id'
                ].iloc[0]
            except:
                chart_project_id = None
            
            with mui.Box(sx={
                "display": "flex", "alignItems": "center", 
                "gap": 0.5, "mb": 1
            }):
                mui.Typography("Full Details", variant="body2", sx={"color": "#666", "fontSize": "12px"})
                if chart_project_id:
                    project_url = f"http://localhost:8081/projects/{chart_project_id}"
                    mui.IconButton(
                        href=project_url,
                        target="_blank",
                        size="small",
                        sx={
                            "color": "#666", "padding": "2px",
                            "&:hover": {
                                "backgroundColor": "rgba(102, 102, 102, 0.1)",
                                "color": "#333"
                            }
                        },
                        children=mui.icon.OpenInNew(sx={"fontSize": "12px"})
                    )
            
            # Key Performance Indicators section (smaller, below Full Details)
            self._render_kpi_section(project_data, df_compare_to_set_full, baseline_data, has_baseline_data)
            
            # Get compare to set data (average from compare to set)
            comparison_data = df_compare_to_set_full.select_dtypes(include=[np.number]).mean() \
                if len(df_compare_to_set_full) > 0 else None
            
            # Store current data for EUI details expansion
            self.current_project_data = project_data
            self.current_comparison_data = comparison_data
            self.current_baseline_data = baseline_data if has_baseline_data else None
            
            # Create and display metrics
            metrics_data = self._create_metrics_data(
                project_data, baseline_data, has_baseline_data, comparison_data
            )
            
            self._render_metrics_table(metrics_data, has_baseline_data)
    
    def _get_baseline_data(self, proj_name, df, company_id):
        """Get baseline data for a specific project"""
        try:
            baseline_project_data = bv.generate_selected_project(
                df, proj_name, company_id, baseline_design='baseline', 
                energy_units=st.session_state['units']
            )
            
            if baseline_project_data is not None and len(baseline_project_data) > 0:
                if 'eeu' in baseline_project_data.columns and 'value' in baseline_project_data.columns:
                    # Convert from long format to wide format
                    baseline_data = baseline_project_data.set_index('eeu')['value']
                else:
                    baseline_data = baseline_project_data.iloc[0]
                
                return baseline_data, True
            else:
                return None, False
        except Exception as e:
            print(f"DEBUG: Exception getting baseline data: {str(e)}")
            return None, False
    
    def _create_metrics_data(self, project_data, baseline_data, has_baseline_data, comparison_data):
        """Create metrics data structure for display"""
        
        if project_data is not None and comparison_data is not None:
            # Load field list and create groupings
            field_list_df = self._load_field_list()
            
            # Group by higher_level_grouping and aggregate values
            grouped_categories, grouped_values, grouped_comparisons, grouped_baselines = \
                self._group_metrics_data(field_list_df, project_data, comparison_data, 
                                       baseline_data, has_baseline_data)
            
            # Create final metrics structure
            return self._build_final_metrics(
                grouped_categories, grouped_values, grouped_comparisons, grouped_baselines
            )
        else:
            # Fallback data structure
            return self._create_fallback_metrics()
    
    def _load_field_list(self):
        """Load field list CSV from multiple possible paths"""
        current_dir = os.path.dirname(__file__)
        
        field_list_paths = [
            os.path.join(current_dir, 'backend_dependencies', 'field_list.csv'),
            os.path.join(os.path.dirname(current_dir), 'backend', 'dependencies', 'field_list.csv'),
            os.path.join(current_dir, 'dependencies', 'field_list.csv')
        ]
        
        for path in field_list_paths:
            try:
                return pd.read_csv(path)
            except FileNotFoundError:
                continue
        
        # Ultimate fallback
        return self._create_fallback_field_list()
    
    def _create_fallback_field_list(self):
        """Create fallback field list if CSV not found"""
        field_list_data = {
            'field': [
                'Heating_Electricity', 'Heating_NaturalGas', 'Heating_DistrictHeating', 'Heating_Other',
                'Cooling_Electricity', 'Cooling_DistrictHeating', 'Cooling_Other',
                'DHW_Electricity', 'DHW_NaturalGas', 'DHW_DistrictHeating', 'DHW_Other',
                'Interior Lighting_Electricity', 'Exterior Lighting_Electricity',
                'Plug Loads_Electricity', 'Fans_Electricity', 'Pumps_Electricity', 'Pumps_NaturalGas',
                'Process Refrigeration_Electricity', 'OtherEndUse_Electricity', 'OtherEndUse_NaturalGas',
                'Heat Rejection_Electricity', 'Humidification_Electricity'
            ],
            'higher_level_grouping': [
                'Heating', 'Heating', 'Heating', 'Heating',
                'Cooling', 'Cooling', 'Cooling',
                'DHW', 'DHW', 'DHW', 'DHW',
                'Lighting', 'Lighting',
                'Other', 'Fans', 'Pumps', 'Pumps',
                'Other', 'Other', 'Other',
                'Other', 'Other'
            ]
        }
        return pd.DataFrame(field_list_data)
    
    def _group_metrics_data(self, field_list_df, project_data, comparison_data, 
                          baseline_data, has_baseline_data):
        """Group metrics data by higher level categories"""
        
        grouped_categories = {}
        grouped_values = {}
        grouped_comparisons = {}
        grouped_baselines = {}
        
        for _, row in field_list_df.iterrows():
            field_name = row['field']
            grouping = row['higher_level_grouping']
            
            if field_name in project_data.index and field_name in comparison_data.index:
                project_val = float(project_data[field_name]) if pd.notna(project_data[field_name]) else 0.0
                comparison_val = float(comparison_data[field_name]) if pd.notna(comparison_data[field_name]) else 0.0
                
                # Get baseline value if available
                baseline_val = 0.0
                if has_baseline_data and baseline_data is not None and field_name in baseline_data.index:
                    baseline_val = float(baseline_data[field_name]) if pd.notna(baseline_data[field_name]) else 0.0
                
                # Only include if there's non-zero values
                if project_val > 0 or comparison_val > 0 or baseline_val > 0:
                    if grouping not in grouped_categories:
                        grouped_categories[grouping] = grouping
                        grouped_values[grouping] = 0.0
                        grouped_comparisons[grouping] = 0.0
                        grouped_baselines[grouping] = 0.0
                    
                    grouped_values[grouping] += project_val
                    grouped_comparisons[grouping] += comparison_val
                    grouped_baselines[grouping] += baseline_val
        
        return grouped_categories, grouped_values, grouped_comparisons, grouped_baselines
    
    def _build_final_metrics(self, grouped_categories, grouped_values, grouped_comparisons, grouped_baselines):
        """Build final metrics data structure"""
        
        categories = []
        values = []
        baseline_values = []
        comparisons = []
        trends = []
        
        # Calculate totals for Whole Building row
        total_project_value = sum(grouped_values.values())
        total_comparison_value = sum(grouped_comparisons.values())
        total_baseline_value = sum(grouped_baselines.values())
        
        # Add Whole Building total as first row
        if total_project_value > 0 or total_comparison_value > 0:
            categories.append('Whole Building')
            values.append(total_project_value)
            baseline_values.append(total_baseline_value)
            comparisons.append(total_comparison_value)
            total_trend = '▲' if total_project_value > total_comparison_value else \
                         '▼' if total_project_value < total_comparison_value else '='
            trends.append(total_trend)
        
        # Sort categories for consistent display order
        category_order = ['Heating', 'Cooling', 'Lighting', 'DHW', 'Fans', 'Pumps', 'Other', 'Renewables']
        sorted_groupings = sorted(
            grouped_categories.keys(), 
            key=lambda x: category_order.index(x) if x in category_order else len(category_order)
        )
        
        # Add individual categories
        for grouping in sorted_groupings:
            if grouping in grouped_values and (grouped_values[grouping] > 0 or grouped_comparisons[grouping] > 0):
                categories.append(grouping)
                values.append(grouped_values[grouping])
                baseline_values.append(grouped_baselines[grouping])
                comparisons.append(grouped_comparisons[grouping])
                
                trend = '▲' if grouped_values[grouping] > grouped_comparisons[grouping] else \
                       '▼' if grouped_values[grouping] < grouped_comparisons[grouping] else '='
                trends.append(trend)
        
        return {
            'Category': categories,
            'Value': values,
            'Baseline': baseline_values,
            'Comparison': comparisons,
            'Trend': trends
        }
    
    def _create_fallback_metrics(self):
        """Create fallback metrics when no data is available"""
        all_categories = ['Whole Building', 'Heating', 'Cooling', 'Lighting', 'DHW', 'Fans', 'Pumps', 'Other']
        return {
            'Category': all_categories,
            'Value': [0.0] * len(all_categories),
            'Baseline': [0.0] * len(all_categories),
            'Comparison': [0.0] * len(all_categories),
            'Trend': ['='] * len(all_categories)
        }
    
    def _render_metrics_table(self, metrics_data, has_baseline_data):
        """Render the metrics table with proper formatting"""
        
        # Add column headers
        with mui.Box(sx={
            "display": "flex", "justifyContent": "space-between", 
            "alignItems": "center", "py": 1, "borderBottom": "2px solid #ddd", 
            "fontWeight": "bold", "mb": 1, "backgroundColor": "#f5f5f5"
        }):
            mui.Typography("Energy End Use Intensity", variant="body2", sx={"flex": 2, "fontWeight": "bold"})
            mui.Typography(f"Baseline ({st.session_state['units']})", variant="body2", sx={"flex": 1, "textAlign": "right", "fontWeight": "bold"})
            mui.Typography(f"Design ({st.session_state['units']})", variant="body2", sx={"flex": 1, "textAlign": "right", "fontWeight": "bold"})
            mui.Typography(f"Compare to Set ({st.session_state['units']})", variant="body2", sx={"flex": 1, "textAlign": "right", "fontWeight": "bold"})
        
        # Create metrics display
        for i, category in enumerate(metrics_data['Category']):
            trend_color = '#ff9800' if metrics_data['Trend'][i] == '▲' else \
                         '#4caf50' if metrics_data['Trend'][i] == '▼' else '#666'
            
            # Special styling for Whole Building row
            if category == 'Whole Building':
                self._render_whole_building_row(metrics_data, i, has_baseline_data, trend_color)
            else:
                self._render_category_row(metrics_data, i, category, has_baseline_data, trend_color)
    
    def _render_whole_building_row(self, metrics_data, i, has_baseline_data, trend_color):
        """Render the Whole Building row with special styling"""
        
        with mui.Box(sx={
            "display": "flex", "justifyContent": "space-between", 
            "alignItems": "center", "py": 0.75, "borderBottom": "2px solid #ddd", 
            "backgroundColor": "#f8f9fa", "fontWeight": "bold"
        }):
            mui.Typography("Whole Building", variant="body2", sx={"flex": 2, "fontWeight": "bold"})
            
            # Baseline column
            baseline_val = metrics_data['Baseline'][i]
            baseline_display = f"{baseline_val:.1f}" if has_baseline_data else "N/A"
            mui.Typography(baseline_display, variant="body2", sx={
                "flex": 1, "textAlign": "right", "color": "#666", "fontWeight": "bold"
            })
            
            # Design column with trend arrow
            with mui.Box(sx={
                "flex": 1, "display": "flex", "alignItems": "center", 
                "justifyContent": "flex-end", "gap": 0.5
            }):
                mui.Typography(f"{metrics_data['Value'][i]:.1f}", variant="body2", sx={"fontWeight": "bold"})
                mui.Typography(metrics_data['Trend'][i], variant="body2", sx={
                    "color": trend_color, "fontWeight": "bold"
                })
            
            # Compare to Set column
            mui.Typography(f"{metrics_data['Comparison'][i]:.1f}", variant="body2", sx={
                "flex": 1, "textAlign": "right", "color": "#666", "fontWeight": "bold"
            })
    
    def _render_category_row(self, metrics_data, i, category, has_baseline_data, trend_color):
        """Render a regular category row"""
        
        with mui.Box(sx={
            "display": "flex", "justifyContent": "space-between", 
            "alignItems": "center", "py": 0.5, "borderBottom": "1px solid #eee"
        }):
            # Category name
            mui.Typography(category, variant="body2", sx={"flex": 2})
            
            # Baseline column
            baseline_val = metrics_data['Baseline'][i]
            baseline_display = f"{baseline_val:.1f}" if has_baseline_data else "N/A"
            mui.Typography(baseline_display, variant="body2", sx={
                "flex": 1, "textAlign": "right", "color": "#666"
            })
            
            # Design column with trend arrow
            with mui.Box(sx={
                "flex": 1, "display": "flex", "alignItems": "center", 
                "justifyContent": "flex-end", "gap": 0.5
            }):
                mui.Typography(f"{metrics_data['Value'][i]:.1f}", variant="body2")
                mui.Typography(metrics_data['Trend'][i], variant="body2", sx={
                    "color": trend_color, "fontWeight": "bold"
                })
            
            # Compare to Set column
            mui.Typography(f"{metrics_data['Comparison'][i]:.1f}", variant="body2", sx={
                "flex": 1, "textAlign": "right", "color": "#666"
            })
    
    def _render_opportunities_tab(self):
        """Render the opportunities tab (placeholder for now)"""
        
        with elements("opportunities_details"):
            with mui.Paper(sx={
                "px": 0, "py": 2, "height": "700px", "overflow": "auto", 
                "backgroundColor": "#f8f9fa", "elevation": 0, "boxShadow": "none"
            }):
                with mui.Box(sx={
                    "display": "flex", "alignItems": "center", 
                    "justifyContent": "center", "height": "100%"
                }):
                    mui.Typography("Coming Soon", variant="h4", sx={
                        "color": "#666", "fontStyle": "italic"
                    })
    
    def _render_eui_details_inline(self, category, has_baseline_data):
        """Render individual EUI components inline as additional table rows"""
        
        # Get the field list to find EUI components for this category
        field_list_df = self._load_field_list()
        category_fields = field_list_df[field_list_df['higher_level_grouping'] == category]
        
        # Get project data for the selected point
        if hasattr(self, 'current_project_data') and self.current_project_data is not None:
            project_data = self.current_project_data
            comparison_data = self.current_comparison_data
            baseline_data = self.current_baseline_data if has_baseline_data else None
            
            # Render each EUI component as an indented row
            for _, field_row in category_fields.iterrows():
                field_name = field_row['field']
                
                if field_name in project_data.index:
                    project_val = float(project_data[field_name]) if pd.notna(project_data[field_name]) else 0.0
                    comparison_val = float(comparison_data[field_name]) if pd.notna(comparison_data[field_name]) else 0.0
                    baseline_val = 0.0
                    
                    if has_baseline_data and baseline_data is not None and field_name in baseline_data.index:
                        baseline_val = float(baseline_data[field_name]) if pd.notna(baseline_data[field_name]) else 0.0
                    
                    # Only show if there's a non-zero value
                    if project_val > 0 or comparison_val > 0 or baseline_val > 0:
                        # Calculate trend
                        trend = '▲' if project_val > comparison_val else '▼' if project_val < comparison_val else '='
                        trend_color = '#ff9800' if trend == '▲' else '#4caf50' if trend == '▼' else '#666'
                        
                        # Format field name for display
                        display_name = field_name.replace('_', ' ').replace('Electricity', 'Elec').replace('NaturalGas', 'NG')
                        
                        # Render as an indented row in the same table
                        with mui.Box(sx={
                            "display": "flex", "justifyContent": "space-between", 
                            "alignItems": "center", "py": 0.25, "borderBottom": "1px solid #f0f0f0",
                            "backgroundColor": "#fafafa"
                        }):
                            # EUI component name (indented)
                            mui.Typography(f"  {display_name}", variant="body2", sx={
                                "flex": 2, "fontSize": "11px", "color": "#555"
                            })
                            
                            # Baseline column
                            baseline_display = f"{baseline_val:.1f}" if has_baseline_data else "N/A"
                            mui.Typography(baseline_display, variant="body2", sx={
                                "flex": 1, "textAlign": "right", "color": "#666", "fontSize": "11px"
                            })
                            
                            # Design column with trend arrow
                            with mui.Box(sx={
                                "flex": 1, "display": "flex", "alignItems": "center", 
                                "justifyContent": "flex-end", "gap": 0.5
                            }):
                                mui.Typography(f"{project_val:.1f}", variant="body2", sx={"fontSize": "11px"})
                                mui.Typography(trend, variant="body2", sx={
                                    "color": trend_color, "fontWeight": "bold", "fontSize": "10px"
                                })
                            
                            # Compare to Set column
                            mui.Typography(f"{comparison_val:.1f}", variant="body2", sx={
                                "flex": 1, "textAlign": "right", "color": "#666", "fontSize": "11px"
                            })
    
    def _render_filter_pills(self):
        """Render filter pills above the chart showing active filters"""
        
        # Get current filter values from session state
        active_filters = self._get_active_filters()
        
        if active_filters:
            # Use a simple text element with help parameter
            st.text("Active Filters:", 
                   help="Add additional filters from the side panel, or remove them by clicking the ✕ on any pill below.")
            
            # Create a container for the pills with custom styling
            pills_container = st.container()
            
            with pills_container:
                # Create pills using streamlit columns for better layout
                pill_cols = st.columns([1] * len(active_filters) + [3])  # Last column for spacing
                
                for i, (filter_type, filter_value) in enumerate(active_filters):
                    with pill_cols[i]:
                                                 # Create custom styled button for each filter pill with smaller font and padding
                         button_style = """
                         <style>
                         div[data-testid="stButton"] > button {
                             background-color: #e3f2fd;
                             border: 1px solid #2196f3;
                             border-radius: 14px;
                             padding: 2px 6px;
                             font-size: 11px;
                             color: #1976d2;
                             width: 100%;
                             white-space: nowrap;
                             overflow: hidden;
                             text-overflow: ellipsis;
                             height: 22px;
                             line-height: 1.1;
                             margin: 0;
                         }
                         div[data-testid="stButton"] > button:hover {
                             background-color: #bbdefb;
                             border-color: #1976d2;
                         }
                         div[data-testid="stButton"] {
                             margin-bottom: 0;
                         }
                         </style>
                         """
                         st.markdown(button_style, unsafe_allow_html=True)
                         
                         # Truncate long filter values for display
                         display_value = filter_value if len(filter_value) <= 15 else filter_value[:12] + "..."
                         
                         if st.button(f"✕ {filter_type}: {display_value}", 
                                    key=f"remove_{filter_type}_{i}",
                                    help=f"Remove filter: {filter_type} = {filter_value}"):
                            self._remove_filter(filter_type)
                            st.rerun()
            
            # Reduced spacing separator
            st.markdown('<hr style="margin: 8px 0; border: none; height: 1px; background-color: #e0e0e0;">', 
                       unsafe_allow_html=True)
        else:
            # Show message when no filters are active with help
            st.text("All projects displayed - no filters are applied", 
                   help="Add filters from the side panel to narrow down the results.")
            
            # Add separator for consistency
            st.markdown('<hr style="margin: 8px 0; border: none; height: 1px; background-color: #e0e0e0;">', 
                       unsafe_allow_html=True)
    
    def _get_active_filters(self):
        """Get list of active filters from session state"""
        active_filters = []
        
        # Check climate zone filter
        if hasattr(st.session_state, 'climate_zone_selector') and st.session_state.get('climate_zone_selector', 'All') != 'All':
            active_filters.append(('Climate Zone', st.session_state.climate_zone_selector))
        
        # Check use type filter
        if hasattr(st.session_state, 'use_type_selector') and st.session_state.get('use_type_selector', 'All') != 'All':
            active_filters.append(('Use Type', st.session_state.use_type_selector))
        
        # Check GSF ranges filter
        if hasattr(st.session_state, 'gsf_ranges') and st.session_state.get('gsf_ranges'):
            gsf_list = st.session_state.gsf_ranges
            if gsf_list:
                active_filters.append(('GSF Range', ', '.join(gsf_list)))
        
        # Check project phase filter
        if hasattr(st.session_state, 'phase_selector') and st.session_state.get('phase_selector', 'All') != 'All':
            active_filters.append(('Project Phase', st.session_state.phase_selector))
        
        # Check project selector filter
        if hasattr(st.session_state, 'project_selector') and st.session_state.get('project_selector', 'All Projects') != 'All Projects':
            active_filters.append(('Projects', st.session_state.project_selector))
        
        return active_filters
    
    def _remove_filter(self, filter_type):
        """Remove a specific filter by setting it to 'All' option"""
        
        # Use a flag-based approach to avoid session state modification conflicts
        if filter_type == 'Climate Zone':
            st.session_state['reset_climate_zone'] = True
        elif filter_type == 'Use Type':
            st.session_state['reset_use_type'] = True
        elif filter_type == 'GSF Range':
            st.session_state['reset_gsf_ranges'] = True
        elif filter_type == 'Project Phase':
            st.session_state['reset_phase_selector'] = True
        elif filter_type == 'Projects':
            st.session_state['reset_project_selector'] = True
