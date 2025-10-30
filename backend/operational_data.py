import pandas as pd
import os
from project_details import get_energy_end_uses_data
from weather_location import weather_check, process_weather_location

# Get the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the data
df_us_electricity = pd.read_csv(os.path.join(current_dir, 'dependencies/operational_carbon/carbon_emissions_electricity.csv'))
df_us_fuel_sources = pd.read_csv(os.path.join(current_dir, 'dependencies/operational_carbon/fuel_sources.csv'))
df_avoided_emissions = pd.read_csv(os.path.join(current_dir, 'dependencies/operational_carbon/avoided_emissions.csv'))
df_district_emissions = pd.read_csv(os.path.join(current_dir, 'dependencies/operational_carbon/district_emissions.csv'))




def return_emissions_factors(egrid_subregion, country):
    try:
        # Check if the subregion exists in the DataFrame
        if egrid_subregion not in df_us_electricity['egrid_acronym'].values:
            print(f"Warning: eGRID subregion {egrid_subregion} not found. Using national average.")
            # Use national average if subregion not found
            electricty = df_us_electricity['co2eq_per_kg_mbtu'].mean()
        else:
            electricty = df_us_electricity[df_us_electricity['egrid_acronym'] == egrid_subregion]['co2eq_per_kg_mbtu'].values[0]

        natural_gas = df_us_fuel_sources[df_us_fuel_sources['fuel_type'] == 'Natural Gas']['co2eq_per_kg_mbtu'].values[0]
        district_heating_elect = df_district_emissions[(df_district_emissions['country'] == country) & (df_district_emissions['fuel_type'] == 'District Steam')]['co2eq_per_kg_mbtu'].values[0]
        district_heating_fossil_fuels = df_district_emissions[(df_district_emissions['country'] == country) & (df_district_emissions['fuel_type'] == 'District Hot Water')]['co2eq_per_kg_mbtu'].values[0]
        district_cooling = df_district_emissions[(df_district_emissions['country'] == country) & (df_district_emissions['fuel_type'] == 'District Chilled Water - Electric Driven Chiller')]['co2eq_per_kg_mbtu'].values[0]
        building_fuel_other = df_us_fuel_sources[df_us_fuel_sources['fuel_type'] == 'Fuel Oil (No. 1)']['co2eq_per_kg_mbtu'].values[0]
        
        # For avoided emissions, use the same logic as electricity
        if egrid_subregion not in df_avoided_emissions['egrid_acronym'].values:
            avoided_emissions = df_avoided_emissions['co2eq_per_kg_mbtu'].mean()
        else:
            avoided_emissions = df_avoided_emissions[df_avoided_emissions['egrid_acronym'] == egrid_subregion]['co2eq_per_kg_mbtu'].values[0]

        return {
            'electricity': electricty, 
            'natural_gas': natural_gas, 
            'district_heating_elect': district_heating_elect, 
            'district_heating_fossil_fuels': district_heating_fossil_fuels, 
            'district_cooling': district_cooling, 
            'building_fuel_other': building_fuel_other,
            'avoided_emissions': avoided_emissions
        }
    except Exception as e:
        print(f"Error in return_emissions_factors: {str(e)}")
        # Return national averages as fallback
        return {
            'electricity': df_us_electricity['co2eq_per_kg_mbtu'].mean(),
            'natural_gas': df_us_fuel_sources[df_us_fuel_sources['fuel_type'] == 'Natural Gas']['co2eq_per_kg_mbtu'].mean(),
            'district_heating_elect': df_district_emissions[df_district_emissions['fuel_type'] == 'District Steam']['co2eq_per_kg_mbtu'].mean(),
            'district_heating_fossil_fuels': df_district_emissions[df_district_emissions['fuel_type'] == 'District Hot Water']['co2eq_per_kg_mbtu'].mean(),
            'district_cooling': df_district_emissions[df_district_emissions['fuel_type'] == 'District Chilled Water - Electric Driven Chiller']['co2eq_per_kg_mbtu'].mean(),
            'building_fuel_other': df_us_fuel_sources[df_us_fuel_sources['fuel_type'] == 'Fuel Oil (No. 1)']['co2eq_per_kg_mbtu'].mean(),
            'avoided_emissions': df_avoided_emissions['co2eq_per_kg_mbtu'].mean()
        }

def calc_operational_carbon_output(operational_energy_design,
                                   operational_energy_baseline,
                                   emissions_factors, 
                                   gsf):
    evaluations = ['baseline','design']

    if operational_energy_baseline['status'] != "success":
        evaluations.pop(0)
    if operational_energy_design['status'] != "success":
        evaluations.pop(1)
    operational_carbon_combined_output = {}
    for evaluation in evaluations:
        if evaluation == 'baseline':
            operational_energy = operational_energy_baseline
        else:
            operational_energy = operational_energy_design

        building_electricity = operational_energy['building_electricity'] * emissions_factors['electricity']/1000
        building_fossil_fuels = operational_energy['building_natural_gas'] * emissions_factors['natural_gas']/1000
        building_other = operational_energy['building_fuel_other'] * emissions_factors['building_fuel_other']/1000
        district_heating_fossil_fuels = operational_energy['district_heating_fossil_fuels'] * emissions_factors['district_heating_fossil_fuels']/1000
        avoided_emissions = operational_energy['avoided_emissions'] * emissions_factors['avoided_emissions']/1000
        net_operation_carbon = building_electricity + building_fossil_fuels + district_heating_fossil_fuels + building_other - avoided_emissions
        area_m2 = gsf * 0.092903
        if area_m2 and area_m2 > 0:
            net_operational_carbon_intensity = (net_operation_carbon * 1000) / area_m2
        else:
            net_operational_carbon_intensity = None

        operational_carbon_output = {'status':'success',
                                     'building_electricity': building_electricity,
                    'building_natural_gas': building_fossil_fuels,
                    'building_fuel_other': building_other,
                    'district_heating_fossil_fuels': district_heating_fossil_fuels,
                    'avoided_emissions': avoided_emissions,
                    'net_operational_carbon': net_operation_carbon,
                    'net_operational_carbon_intensity': net_operational_carbon_intensity,
                    }
        operational_carbon_combined_output[evaluation] = operational_carbon_output

    # Debugging: Print the combined output
    print("Operational Carbon Combined Output:", operational_carbon_combined_output)

    if operational_energy_baseline['status'] == "success" and operational_energy_design['status'] == "success":
        design_net_operational_carbon_intensity = operational_carbon_combined_output['design']['net_operational_carbon_intensity']
        baseline_net_operational_carbon_intensity = operational_carbon_combined_output['baseline']['net_operational_carbon_intensity']
        pct_savings = None
        if (
            baseline_net_operational_carbon_intensity is not None and
            design_net_operational_carbon_intensity is not None and
            baseline_net_operational_carbon_intensity != 0
        ):
            pct_savings = (
                baseline_net_operational_carbon_intensity - design_net_operational_carbon_intensity
            ) / baseline_net_operational_carbon_intensity

        operational_carbon_output = operational_carbon_combined_output['design']
        operational_carbon_output['pct_savings'] = pct_savings

    return {'status':'success',
            'operational_carbon_output_design': operational_carbon_output,
            'operational_carbon_output_baseline': operational_carbon_combined_output.get('baseline')}





def operational_energy_data(project_id,baseline_design):
    end_uses_output = get_energy_end_uses_data(project_id,baseline_design,output_units='mbtu')
    if end_uses_output['status'] != "success":
        return {"status":"no operational energy data found"}
    df_energy_end_uses = end_uses_output['eeu_data']
    df_renewables = end_uses_output['renewables']
 

    building_electricity = df_energy_end_uses['electricity'].sum()
    building_natural_gas = df_energy_end_uses['fossil_fuels'].sum()
    building_district = df_energy_end_uses['district'].sum()
    building_other = df_energy_end_uses['other'].sum()
    building_energy_total = building_electricity + building_natural_gas
    building_total_fossil_fuels = building_natural_gas + building_district + building_other

    total_renewables = df_renewables.loc[df_renewables.index == 'On-Site Renewables'].sum(numeric_only=True).sum()
    building_net_electricity = building_electricity - total_renewables
    building_net_energy_total = building_net_electricity + building_total_fossil_fuels
    operational_energy_output = {'status':'success',
                                 'project_id':project_id,
            'building_electricity':building_electricity,
            'building_natural_gas':building_natural_gas,
            'district_heating_fossil_fuels':building_district,
            'building_fuel_other':building_other,
            'avoided_emissions':total_renewables,
            'use_type_total_area':end_uses_output['use_type_total_area'],
            'zip_code':end_uses_output['zip_code'],
            'egrid_subregion':end_uses_output['egrid_subregion'],
            'eeu_id':int(end_uses_output['eeu_id']),
            'use_type_total_area':end_uses_output['use_type_total_area'],
            'building_total_fossil_fuels':building_total_fossil_fuels,
            'building_energy_total':building_energy_total,
            'building_net_electricity':building_net_electricity,
            'building_net_energy_total':building_net_energy_total,
            
            }
    if baseline_design == "baseline":
        operational_energy_output['pct_operational_energy_savings'] = 0
    else:
        operational_energy_output['pct_operational_energy_savings'] = 0
    return operational_energy_output

def operational_carbon_data(project_id):

    ## Get the operational energy data for the design file, if that doesn't exist, get the baseline data
    energy_output_data = {}
    energy_output_data['operational_energy_design'] = operational_energy_data(project_id, "design")
    energy_output_data['operational_energy_baseline'] = operational_energy_data(project_id, "baseline")

    for key in energy_output_data:
        operational_energy = energy_output_data[key]
        if operational_energy['status'] == 'success':
            if operational_energy['egrid_subregion'] is None or operational_energy['egrid_subregion'] == '':
                weather_response = process_weather_location(operational_energy['eeu_id'])
                if weather_response['egrid_subregion'] is not None:
                    operational_energy['egrid_subregion'] = weather_response['egrid_subregion']
                else:
                    operational_energy['status'] = "no location data found"
            emissions_factors = return_emissions_factors(operational_energy['egrid_subregion'],'us')
            use_type_total_area = operational_energy['use_type_total_area']
    
    output = calc_operational_carbon_output(energy_output_data['operational_energy_design'],energy_output_data['operational_energy_baseline'], 
                                            emissions_factors, 
                                            gsf=use_type_total_area)
    return {'status':'success',
            'operational_energy_data': {
                'design': energy_output_data['operational_energy_design'],
                'baseline': energy_output_data['operational_energy_baseline']
            },
            'operational_carbon_data': {
                'design': output['operational_carbon_output_design'],
                'baseline': output['operational_carbon_output_baseline']
            },
            'emissions_factors': emissions_factors}

print("done")
