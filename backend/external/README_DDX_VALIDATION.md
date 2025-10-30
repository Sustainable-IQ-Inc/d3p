# DDX Pre-validation System

A flexible, configurable validation system that checks DDX data before submission to identify warnings and errors that could prevent successful DDX integration.

## Overview

The DDX Pre-validation System provides:

- **Formula-based validation rules** that can be easily configured and modified
- **Two severity levels**: Warnings (allow submission) and Errors (block submission)
- **Categorized validation rules** for better organization and reporting
- **Custom user rules** that can be added via the API
- **Comprehensive validation results** with detailed issue descriptions
- **Frontend integration** with a validation summary modal

## Architecture

### Core Components

1. **`DDXPreValidator`** - Main validation engine
2. **`ValidationRule`** - Individual validation rule definition
3. **`ValidationResult`** - Results container with warnings and errors
4. **Database integration** - Custom rules storage in Supabase
5. **API endpoints** - RESTful API for validation operations
6. **Frontend components** - React modal for validation results

### Data Flow

```
Project Data → DDX Pre-validation → Validation Results → Frontend Display → User Decision
```

## Default Validation Rules

### Data Completeness
- **Project ID Required**: Ensures project ID is provided
- **Project Name Required**: Ensures project name is provided  
- **Use Type Required**: Ensures use type is specified
- **Climate Zone Required**: Ensures climate zone is specified

### Data Quality
- **Positive Use Type Area**: Area must be > 0
- **Reasonable Area Size**: Area should be 100-10M sq ft (warning)
- **Positive Baseline EUI**: Baseline EUI must be > 0
- **Positive Predicted EUI**: Predicted EUI must be > 0
- **Reasonable EUI Ranges**: EUIs should be within typical ranges (warnings)

### Business Logic
- **EUI Improvement Check**: Predicted EUI should be less than baseline (warning)
- **Excessive Savings Check**: Savings over 90% flagged for review (warning)
- **Negative Savings Check**: Predicted EUI much higher than baseline (error)

### Format Validation
- **Valid Reporting Year**: Year must be 2020-2030
- **Valid Zipcode Format**: US zipcode format validation (warning)

### DDX Requirements
- **DDX Baseline EUI Limit**: Baseline EUI must be < 1,000 kBtu/SF
- **DDX Area Limit**: Large area projects flagged for review (warning)

## API Endpoints

### Run Pre-validation
```http
POST /ddx_pre_validation/
Content-Type: application/json

{
  "project_id": "project-uuid",
  "edited_values": {
    "Use Type Area": 25000,
    "Project ID": "CUSTOM-001"
  }
}
```

**Response:**
```json
{
  "status": "validation_required",
  "can_submit": false,
  "is_valid": false,
  "summary": {
    "total_issues": 3,
    "warnings": 1,
    "errors": 2
  },
  "issues": {
    "warnings": [...],
    "errors": [...]
  },
  "data": {...}
}
```



## Frontend Integration

### DDXPreValidationModal Component

Shows validation results in a user-friendly interface:

```tsx
<DDXPreValidationModal
  open={showValidation}
  onClose={() => setShowValidation(false)}
  projectId={projectId}
  editedValues={editedValues}
  onValidationComplete={(canSubmit, result) => {
    if (canSubmit) {
      // Proceed with DDX submission
    }
  }}
/>
```

### Features
- **Visual summary** with warning/error counts
- **Categorized issue lists** with expand/collapse
- **Field-specific feedback** showing current values
- **Blocking behavior** for errors vs warnings
- **Integration** with existing DDX submission flow

## Writing Validation Rules

### Rule Structure

```python
ValidationRule(
    id="unique_rule_id",
    name="Human Readable Name",
    description="What this rule validates",
    severity=ValidationSeverity.WARNING,  # or ERROR
    formula="python_expression_returning_bool",
    category="rule_category",
    enabled=True,
    depends_on=["field1", "field2"]  # Optional
)
```

### Formula Syntax

Formulas are Python expressions evaluated in a safe context with access to:

- `data` - Dictionary of DDX field values
- `float()`, `int()`, `str()` - Type conversion functions
- `len()`, `abs()`, `min()`, `max()` - Utility functions
- `re` - Regular expression module
- `datetime` - Date/time utilities

### Formula Examples

```python
# Check if area is positive
"float(data.get('useType1Area', 0)) > 0"

# Check if EUI is within range
"10 <= float(data.get('baselineEUI', 0)) <= 500"

# Check if predicted EUI is less than baseline
"float(data.get('predictedEUI', 0)) < float(data.get('baselineEUI', 0))"

# Check zipcode format
"re.match(r'^\\d{5}(-\\d{4})?$', str(data.get('zipcode', '')))"

# Check for required field
"data.get('projectId', '').strip() != ''"

# Complex business logic
"(float(data.get('baselineEUI', 0)) - float(data.get('predictedEUI', 0))) / float(data.get('baselineEUI', 1)) <= 0.9"
```

### Best Practices

1. **Use descriptive IDs**: `company_specific_area_check` vs `rule1`
2. **Handle missing data**: Always use `data.get(field, default)`
3. **Type conversion**: Wrap values in `float()`, `int()`, `str()` as needed
4. **Clear descriptions**: Explain what the rule checks and why
5. **Appropriate severity**: Use ERROR only for submission-blocking issues
6. **Test formulas**: Use the test script to verify rule behavior



## Testing

Run the test script to see the validation system in action:

```bash
cd backend
python test_validation.py
```

This will:
- Show all default validation rules
- Test various data scenarios
- Demonstrate custom rule creation
- Display validation results for each scenario

## Security Considerations

1. **Safe evaluation**: Formulas run in restricted Python context
2. **Input validation**: Rule structure is validated before use
3. **Error handling**: Failed rule evaluation logged, doesn't crash system

## Extension Points

### Adding New Default Rules

1. Add rule to `get_all_default_rules()` in `ddx_validation_rules.py`
2. Test with various data scenarios
3. Update documentation

### Rule Categories

Rules are organized into categories:
- `completeness` - Required field validation
- `data_quality` - Data accuracy and format validation
- `business_logic` - Domain-specific business rules
- `system` - System-level validation errors

### Integration with Other Systems

The validation system can be extended to:
- Validate data from other sources
- Integrate with external validation services
- Send notifications for critical validation failures
- Generate validation reports

## Troubleshooting

### Common Issues

1. **Formula evaluation errors**: Check formula syntax and data access patterns
2. **Missing dependencies**: Ensure required fields exist in data
3. **Performance issues**: Optimize rule formulas for better performance

### Debugging

Enable detailed logging to see formula evaluation:

```python
import logging
logging.getLogger('ddx_pre_validation').setLevel(logging.DEBUG)
```

### Support

For questions or issues:
1. Check the test script for examples
2. Review validation rule formulas
3. Test with sample data scenarios
4. Check backend logs for detailed error messages 