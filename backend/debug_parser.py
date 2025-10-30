#!/usr/bin/env python3
"""
Debug script to test the multi-project parser with the new column structure
"""
import sys
import os
sys.path.append('.')

from parse_reports.parse_multi_project_xlsx import MultiProjectExcelParser

def test_parser_with_new_structure():
    """Test the parser with the new baseline/design column structure"""
    
    # Create a test project data structure that mimics the new format
    test_project_data = {
        'project_name': 'Test Project',
        'conditioned_area_sf': 50000,
        'area_units': 'sf',
        'zip_code': '94102',
        'climate_zone': '3C',
        'project_use_type': 'Office',
        'project_construction_category': 'New',
        'project_phase': 'Design Development',
        'energy_code': 'ASHRAE 90.1-2019',
        'report_type': 'EnergyPlus Report',
        'year': 2024,
        'reporting_year': 2024,
        'energy_units': 'mbtu',
        'baseline_energy_data': {
            'Heating_Electricity': 100.0,
            'Heating_NaturalGas': 150.0,
            'Cooling_Electricity': 200.0
        },
        'design_energy_data': {
            'Heating_Electricity': 80.0,
            'Heating_NaturalGas': 120.0,
            'Cooling_Electricity': 160.0
        }
    }
    
    print("Testing parser with new structure...")
    print(f"Project data: {test_project_data}")
    
    # Test the energy field extraction
    parser = MultiProjectExcelParser()
    
    # Test baseline energy extraction
    baseline_energy = {}
    if 'baseline_energy_data' in test_project_data:
        for field_name, value in test_project_data['baseline_energy_data'].items():
            if value is not None:
                try:
                    baseline_energy[field_name] = float(value)
                except (ValueError, TypeError):
                    continue
    
    print(f"Baseline energy fields: {baseline_energy}")
    
    # Test design energy extraction
    design_energy = {}
    if 'design_energy_data' in test_project_data:
        for field_name, value in test_project_data['design_energy_data'].items():
            if value is not None:
                try:
                    design_energy[field_name] = float(value)
                except (ValueError, TypeError):
                    continue
    
    print(f"Design energy fields: {design_energy}")
    
    return len(baseline_energy) > 0 and len(design_energy) > 0

if __name__ == "__main__":
    success = test_parser_with_new_structure()
    print(f"Parser test {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
