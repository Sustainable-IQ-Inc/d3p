from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json
import re
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ValidationSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"

@dataclass
class ValidationRule:
    """Represents a single validation rule"""
    id: str
    name: str
    description: str
    severity: ValidationSeverity
    formula: str  # Python expression to evaluate
    field: Optional[str] = None  # Field this rule applies to
    enabled: bool = True
    category: str = "general"
    depends_on: List[str] = None  # Fields this rule depends on

@dataclass
class ValidationIssue:
    """Represents a validation issue found during validation"""
    rule_id: str
    rule_name: str
    severity: ValidationSeverity
    message: str
    field: Optional[str] = None
    current_value: Any = None
    suggested_value: Any = None
    category: str = "general"

@dataclass
class ValidationResult:
    """Contains the result of running all validations"""
    is_valid: bool
    can_submit: bool  # False if there are any errors
    warnings: List[ValidationIssue]
    errors: List[ValidationIssue]
    total_issues: int
    data_validated: Dict[str, Any]

class DDXPreValidator:
    """Main class for DDX pre-validation"""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.logger = logging.getLogger(__name__)
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default validation rules from the rules module"""
        from external.ddx_validation_rules import get_all_default_rules
        self.rules = get_all_default_rules()
    
    def add_rule(self, rule: ValidationRule):
        """Add a custom validation rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_id: str):
        """Remove a validation rule by ID"""
        self.rules = [r for r in self.rules if r.id != rule_id]
    
    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """Get a validation rule by ID"""
        return next((r for r in self.rules if r.id == rule_id), None)
    
    def enable_rule(self, rule_id: str):
        """Enable a validation rule"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
    
    def disable_rule(self, rule_id: str):
        """Disable a validation rule"""
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
    
    def _evaluate_formula(self, formula: str, data: Dict[str, Any], context: Dict[str, Any] = None) -> bool:
        """Safely evaluate a validation formula"""
        try:
            # Create a safe context for evaluation
            safe_context = {
                'data': data,
                'float': float,
                'int': int,
                'str': str,
                'len': len,
                'abs': abs,
                'min': min,
                'max': max,
                're': re,
                'datetime': datetime,
                '__builtins__': {}  # Remove access to built-in functions for security
            }
            print("DEBUG _evaluate_formula - formula:", formula)
            print("DEBUG _evaluate_formula - data keys:", list(data.keys()))
            
            # Add any additional context
            if context:
                safe_context.update(context)
            
            result = eval(formula, safe_context)
            print("DEBUG _evaluate_formula - result:", result)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Error evaluating formula '{formula}': {str(e)}")
            print(f"DEBUG _evaluate_formula - Exception: {str(e)}")
            return False
    
    def _create_validation_issue(self, rule: ValidationRule, data: Dict[str, Any], 
                               custom_message: str = None) -> ValidationIssue:
        """Create a ValidationIssue from a failed rule"""
        
        # Use the field specified in the rule, or fall back to heuristic
        field = rule.field
        current_value = None
        
        if field:
            current_value = data.get(field)
        else:
            # Fallback: Simple heuristic to determine the field from the formula
            formula_lower = rule.formula.lower()
            field_mappings = {
                'projectid': 'projectId',
                'projectname': 'projectName', 
                'usetype1area': 'useType1Area',
                'usetype1': 'useType1',
                'climatezone': 'climateZone',
                'baselineeui': 'baselineEUI',
                'predictedeui': 'predictedEUI',
                'reportingyear': 'reportingYear',
                'estimatedoccupancyyear': 'estimatedOccupancyYear',
                'zipcode': 'zipcode'
            }
            
            for key_variant, actual_key in field_mappings.items():
                if key_variant in formula_lower:
                    field = actual_key
                    current_value = data.get(actual_key)
                    break
        
        message = custom_message or rule.description
        
        return ValidationIssue(
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            message=message,
            field=field,
            current_value=current_value,
            category=rule.category
        )
    
    def validate(self, data: Dict[str, Any], enabled_rules_only: bool = True) -> ValidationResult:
        """Run all validation rules against the provided data"""
        
        print(f"DEBUG: Starting validation with data keys: {list(data.keys())}")
        print(f"DEBUG: reportingYear value: {data.get('reportingYear', 'NOT_FOUND')}")
        print(f"DEBUG: reportingYear type: {type(data.get('reportingYear', 'NOT_FOUND'))}")
        
        warnings = []
        errors = []
        
        # Filter rules based on enabled status
        rules_to_run = [r for r in self.rules if not enabled_rules_only or r.enabled]
        print(f"DEBUG: Running {len(rules_to_run)} rules")
        
        for rule in rules_to_run:
            try:
                # Check if rule dependencies are met
                if rule.depends_on:
                    missing_deps = [dep for dep in rule.depends_on if dep not in data]
                    if missing_deps:
                        self.logger.debug(f"Skipping rule {rule.id} due to missing dependencies: {missing_deps}")
                        continue
                
                # Special debug for past_year rule
                if rule.id == "past_year":
                    print(f"DEBUG: Evaluating past_year rule")
                    print(f"DEBUG: Formula: {rule.formula}")
                    print(f"DEBUG: Data contains reportingYear: {'reportingYear' in data}")
                    if 'reportingYear' in data:
                        print(f"DEBUG: reportingYear value: {data['reportingYear']}")
                        print(f"DEBUG: reportingYear == 2023: {data['reportingYear'] == 2023}")
                        print(f"DEBUG: int(reportingYear) == 2023: {int(data['reportingYear']) == 2023}")
                
                # Evaluate the rule
                is_valid = self._evaluate_formula(rule.formula, data)
                print(f"DEBUG: Rule {rule.id} result: {is_valid}")
                
                if not is_valid:
                    issue = self._create_validation_issue(rule, data)
                    
                    if rule.severity == ValidationSeverity.ERROR:
                        errors.append(issue)
                        print(f"DEBUG: Added ERROR for rule {rule.id}")
                    else:
                        warnings.append(issue)
                        print(f"DEBUG: Added WARNING for rule {rule.id}")
                        
            except Exception as e:
                self.logger.error(f"Error running validation rule {rule.id}: {str(e)}")
                print(f"DEBUG: Exception in rule {rule.id}: {str(e)}")
                print(f"DEBUG: Rule formula: {rule.formula}")
                print(f"DEBUG: Data keys: {list(data.keys())}")
                if rule.field and rule.field in data:
                    print(f"DEBUG: Field '{rule.field}' value: {data[rule.field]} (type: {type(data[rule.field])})")
                
                # Create an error for the failed validation with more context
                error_message = f"Validation rule failed to execute: {str(e)}"
                if rule.field and rule.field in data:
                    field_value = data[rule.field]
                    error_message += f" (Field '{rule.field}' has value: {field_value}, type: {type(field_value).__name__})"
                
                errors.append(ValidationIssue(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=ValidationSeverity.ERROR,
                    message=error_message,
                    field=rule.field,
                    current_value=data.get(rule.field) if rule.field else None,
                    category="system"
                ))
        
        print(f"DEBUG: Final validation result - warnings: {len(warnings)}, errors: {len(errors)}")
        
        # Determine overall validation status
        has_errors = len(errors) > 0
        is_valid = len(errors) == 0 and len(warnings) == 0
        can_submit = len(errors) == 0  # Can submit if no errors, warnings are OK
        
        return ValidationResult(
            is_valid=is_valid,
            can_submit=can_submit,
            warnings=warnings,
            errors=errors,
            total_issues=len(warnings) + len(errors),
            data_validated=data
        )
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Get a summary of all rules"""
        enabled_rules = [r for r in self.rules if r.enabled]
        disabled_rules = [r for r in self.rules if not r.enabled]
        
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len(enabled_rules),
            "disabled_rules": len(disabled_rules),
            "rules_by_category": {
                category: len([r for r in self.rules if r.category == category])
                for category in set(r.category for r in self.rules)
            },
            "rules_by_severity": {
                "errors": len([r for r in self.rules if r.severity == ValidationSeverity.ERROR]),
                "warnings": len([r for r in self.rules if r.severity == ValidationSeverity.WARNING])
            }
        }

# Convenience functions for API usage

def validate_ddx_data(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate DDX data with default rules
    
    Args:
        data: The DDX data to validate
        
    Returns:
        ValidationResult with all validation results
    """
    validator = DDXPreValidator()
    return validator.validate(data)

def create_validation_summary_response(validation_result: ValidationResult) -> Dict[str, Any]:
    """
    Create a response suitable for the frontend validation summary screen
    
    Args:
        validation_result: The validation result to format
        
    Returns:
        Dictionary formatted for frontend consumption
    """
    return {
        "status": "success" if validation_result.can_submit else "validation_required",
        "can_submit": validation_result.can_submit,
        "is_valid": validation_result.is_valid,
        "summary": {
            "total_issues": validation_result.total_issues,
            "warnings": len(validation_result.warnings),
            "errors": len(validation_result.errors)
        },
        "issues": {
            "warnings": [
                {
                    "id": w.rule_id,
                    "name": w.rule_name,
                    "message": w.message,
                    "field": w.field,
                    "current_value": w.current_value,
                    "suggested_value": w.suggested_value,
                    "category": w.category,
                    "severity": "warning"
                }
                for w in validation_result.warnings
            ],
            "errors": [
                {
                    "id": e.rule_id,
                    "name": e.rule_name,
                    "message": e.message,
                    "field": e.field,
                    "current_value": e.current_value,
                    "suggested_value": e.suggested_value,
                    "category": e.category,
                    "severity": "error"
                }
                for e in validation_result.errors
            ]
        },
        "data": validation_result.data_validated
    }


