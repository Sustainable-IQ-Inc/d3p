#!/usr/bin/env python3
"""
Test script for DDX Pre-validation System
This script demonstrates how the validation system works with various data scenarios.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from external.ddx_pre_validation import (
    validate_ddx_data, 
    create_validation_summary_response,
    DDXPreValidator,
    ValidationRule,
    ValidationSeverity
)

# Test data scenarios
TEST_SCENARIOS = [
    {
        "name": "Valid Project Data",
        "data": {
            "projectId": "TEST-001",
            "projectName": "Sample Office Building",
            "useType1": "Office",
            "useType1Area": 25000,
            "climateZone": "4A - Mixed-Humid",
            "baselineEUI": 85.5,
            "predictedEUI": 65.2,
            "reportingYear": 2024,
            "zipcode": "20001",
            "designEnergyCode": "ASHRAE 90.1-2019"
        }
    },
    {
        "name": "Project with Warnings",
        "data": {
            "projectId": "TEST-002", 
            "projectName": "Large Warehouse",
            "useType1": "Warehouse",
            "useType1Area": 8500000,  # Very large area - will trigger warning
            "climateZone": "2A - Hot-Humid",
            "baselineEUI": 45.0,
            "predictedEUI": 42.0,  # Small savings - might trigger warning
            "reportingYear": 2024,
            "zipcode": "33101",
            "designEnergyCode": "IECC 2021"
        }
    },
    {
        "name": "Project with Errors",
        "data": {
            "projectId": "",  # Missing project ID - ERROR
            "projectName": "Problem Building",
            "useType1": "Office",
            "useType1Area": -1000,  # Negative area - ERROR
            "climateZone": "4A - Mixed-Humid",
            "baselineEUI": 1200,  # Exceeds DDX limit - ERROR
            "predictedEUI": 150,  # Much higher than baseline - ERROR
            "reportingYear": 2040,  # Invalid year - ERROR
            "zipcode": "invalid",  # Invalid zipcode format - WARNING
            "designEnergyCode": "ASHRAE 90.1-2019"
        }
    },
    {
        "name": "Minimal Data (Missing Fields)",
        "data": {
            "projectId": "TEST-003",
            "projectName": "Minimal Project"
            # Missing many required fields
        }
    }
]

def test_validation_scenario(scenario):
    """Test a single validation scenario"""
    print(f"\n{'='*50}")
    print(f"Testing: {scenario['name']}")
    print(f"{'='*50}")
    
    # Run validation
    validation_result = validate_ddx_data(scenario['data'])
    
    # Create response format
    response = create_validation_summary_response(validation_result)
    
    # Print summary
    print(f"Status: {response['status']}")
    print(f"Can Submit: {response['can_submit']}")
    print(f"Total Issues: {response['summary']['total_issues']}")
    print(f"Warnings: {response['summary']['warnings']}")
    print(f"Errors: {response['summary']['errors']}")
    
    # Print errors
    if response['issues']['errors']:
        print(f"\n🚨 ERRORS ({len(response['issues']['errors'])}):")
        for error in response['issues']['errors']:
            print(f"  • {error['name']}: {error['message']}")
            if error['field'] and error['current_value'] is not None:
                print(f"    Field: {error['field']} = {error['current_value']}")
    
    # Print warnings
    if response['issues']['warnings']:
        print(f"\n⚠️  WARNINGS ({len(response['issues']['warnings'])}):")
        for warning in response['issues']['warnings']:
            print(f"  • {warning['name']}: {warning['message']}")
            if warning['field'] and warning['current_value'] is not None:
                print(f"    Field: {warning['field']} = {warning['current_value']}")
    
    if not response['issues']['errors'] and not response['issues']['warnings']:
        print("\n✅ All validations passed!")
    
    return response

def test_custom_rules():
    """Test adding custom validation rules"""
    print(f"\n{'='*50}")
    print("Testing Custom Rules")
    print(f"{'='*50}")
    
    # Create validator with custom rules
    validator = DDXPreValidator()
    
    # Add a custom rule
    custom_rule = ValidationRule(
        id="custom_small_buildings",
        name="Small Building Check",
        description="Buildings under 5,000 SF should be reviewed for accuracy",
        severity=ValidationSeverity.WARNING,
        formula="float(data.get('useType1Area', 0)) >= 5000",
        category="custom_business_logic"
    )
    
    validator.add_rule(custom_rule)
    
    # Test data that will trigger the custom rule
    test_data = {
        "projectId": "SMALL-001",
        "projectName": "Small Office",
        "useType1": "Office", 
        "useType1Area": 3000,  # Small building - will trigger custom rule
        "climateZone": "4A - Mixed-Humid",
        "baselineEUI": 75.0,
        "predictedEUI": 60.0,
        "reportingYear": 2024,
        "zipcode": "20001",
        "designEnergyCode": "ASHRAE 90.1-2019"
    }
    
    validation_result = validator.validate(test_data)
    response = create_validation_summary_response(validation_result)
    
    print(f"Custom rule triggered: {len(response['issues']['warnings'])} warnings")
    for warning in response['issues']['warnings']:
        if warning['id'] == 'custom_small_buildings':
            print(f"✅ Custom rule fired: {warning['message']}")

def print_rules_summary():
    """Print summary of all validation rules"""
    print(f"\n{'='*50}")
    print("Validation Rules Summary")
    print(f"{'='*50}")
    
    validator = DDXPreValidator()
    summary = validator.get_rules_summary()
    
    print(f"Total Rules: {summary['total_rules']}")
    print(f"Enabled Rules: {summary['enabled_rules']}")
    print(f"Error Rules: {summary['rules_by_severity']['errors']}")
    print(f"Warning Rules: {summary['rules_by_severity']['warnings']}")
    
    print(f"\nRules by Category:")
    for category, count in summary['rules_by_category'].items():
        print(f"  {category}: {count}")
    
    print(f"\nAll Rules:")
    for rule in validator.rules:
        status = "✅" if rule.enabled else "❌"
        severity_icon = "🚨" if rule.severity == ValidationSeverity.ERROR else "⚠️"
        print(f"  {status} {severity_icon} {rule.name} ({rule.category})")

def main():
    """Main test function"""
    print("DDX Pre-validation System Test")
    print("=" * 50)
    
    # Print rules summary first
    print_rules_summary()
    
    # Test each scenario
    for scenario in TEST_SCENARIOS:
        test_validation_scenario(scenario)
    
    # Test custom rules
    test_custom_rules()
    
    print(f"\n{'='*50}")
    print("All tests completed!")
    print(f"{'='*50}")

if __name__ == "__main__":
    main() 