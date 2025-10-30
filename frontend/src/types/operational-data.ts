export interface OperationalEnergyDataProps {
    building_electricity: number;
    building_natural_gas: number;
    district_heating_fossil_fuels: number;
    building_fuel_other: number;
    avoided_emissions: number;
    use_type_total_area: number;
    status: string;
    building_total_fossil_fuels: number;
    building_energy_total: number;
    building_net_electricity: number;
    building_net_energy_total: number;
  }

  export interface OperationalEnergyDataCombinedProps {
    design: OperationalEnergyDataProps;
    baseline: OperationalEnergyDataProps;
  }

  export interface OperationalCarbonDataProps {
    building_electricity: number;
    building_natural_gas: number;
    district_heating_fossil_fuels: number;
    building_fuel_other: number;
    avoided_emissions: number;
    net_operational_carbon: number;
    net_operational_carbon_intensity: number;
    pct_savings: number;
    status: string;
  }

  export interface OperationalCarbonDataCombinedProps {
    design: OperationalCarbonDataProps;
    baseline: OperationalCarbonDataProps;
  }

  export interface EmissionsFactorsProps {
    electricity: number;
    natural_gas: number;
    district_heating_elect: number;
    district_heating_fossil_fuels: number;
    district_cooling: number;
    building_fuel_other: number;
    avoided_emissions: number;
  }

  
  
  export interface OperationalDataProps {
    operational_energy_data: OperationalEnergyDataCombinedProps;
    operational_carbon_data: OperationalCarbonDataCombinedProps;
    emissions_factors: EmissionsFactorsProps;
  }
