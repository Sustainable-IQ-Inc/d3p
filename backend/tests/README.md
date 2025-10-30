# BEM Reports Backend Test Suite

This directory contains comprehensive unit tests for the BEM Reports backend system. The test suite covers API endpoints, business logic, data models, utility functions, and external integrations.

## Test Structure

```
backend/tests/
├── README.md                      # This file
├── __init__.py                    # Test package initialization
├── test_authorization_required.py # Existing authorization tests
├── test_weather_location.py       # Existing weather/location tests
├── test_utils.py                  # Utils module tests (NEW)
├── test_main_api.py              # Main API endpoints tests (NEW)
├── test_models.py                # Pydantic model validation tests (NEW)
└── test_conversions.py           # Unit conversion tests (NEW)
```

## Quick Start

### 1. Install Test Dependencies

```bash
# From the backend directory
python run_tests.py --install-deps
```

Or manually:
```bash
pip install pytest>=6.2.5 pytest-cov>=4.0.0 pytest-mock>=3.10.0 pytest-asyncio>=0.21.0
```

### 2. Run All Tests

```bash
# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose
```

### 3. Run Specific Test Categories

```bash
# Run only unit tests
python run_tests.py --type unit

# Run only API tests
python run_tests.py --type api

# Run fast tests only (exclude slow tests)
python run_tests.py --type fast
```

### 4. Run Specific Test Files

```bash
# Run a specific test file
python run_tests.py --file test_utils.py

# Run specific test with pattern matching
python run_tests.py --pattern "test_encrypt"
```

## Test Categories and Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual functions/methods
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.auth` - Authentication and authorization tests
- `@pytest.mark.conversion` - Unit conversion and calculation tests
- `@pytest.mark.model` - Pydantic model validation tests
- `@pytest.mark.utils` - Utility function tests
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.integration` - Integration tests (if any)

## Test Coverage

The test suite covers the following modules:

### 1. `test_utils.py` - Utility Functions
- ✅ Encryption/decryption functions
- ✅ Enum value retrieval and lookup
- ✅ Event history logging
- ✅ Authentication token verification
- ✅ Filename sanitization
- ✅ Fuel category mappings
- ✅ FastAPI app creation

### 2. `test_main_api.py` - API Endpoints
- ✅ Authentication middleware
- ✅ Project submission endpoints
- ✅ Company creation and management
- ✅ User invitation system
- ✅ Project creation
- ✅ Enum retrieval endpoints
- ✅ Request validation and error handling

### 3. `test_models.py` - Data Models
- ✅ All Pydantic model validation
- ✅ Required field validation
- ✅ Type checking and conversion
- ✅ Optional field handling
- ✅ Complex nested models (DDXImportProject)

### 4. `test_conversions.py` - Unit Conversions
- ✅ Basic unit conversion functions
- ✅ Energy unit conversions (MBtu, kBtu, GJ, kWh)
- ✅ Area conversions (ft² to m²)
- ✅ EUI conversions (kBtu/ft² to kWh/m²)
- ✅ Database-driven unit checking
- ✅ DataFrame conversion operations
- ✅ Edge cases and error handling

## Mocking Strategy

The test suite uses comprehensive mocking to isolate units under test:

### External Dependencies
- **Supabase**: All database operations are mocked
- **External APIs**: DDX API calls are mocked
- **File operations**: CSV reading and file uploads are mocked
- **Environment variables**: Configuration values are mocked

### Database Mocking
```python
@patch('module.supabase')
def test_function(mock_supabase):
    mock_supabase.table.return_value.select.return_value.execute.return_value = (None, test_data)
    # Test implementation
```

### Authentication Mocking
```python
@patch('main.verify_token')
def test_endpoint(mock_verify_token):
    mock_verify_token.return_value = {'is_authorized': True, 'company_id': 'test_company'}
    # Test implementation
```

## Running Tests in CI/CD

The test suite is designed to run in automated environments:

```bash
# For CI/CD environments
pytest tests/ --cov=. --cov-report=xml --cov-report=term-missing -v
```

## Writing New Tests

### Test File Naming
- Test files should start with `test_`
- Test classes should start with `Test`
- Test functions should start with `test_`

### Test Structure
```python
import pytest
from unittest.mock import patch, Mock

class TestYourModule:
    """Test class for your module"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        input_data = "test_input"
        expected = "expected_output"
        
        # Act
        result = your_function(input_data)
        
        # Assert
        assert result == expected
    
    @patch('your_module.external_dependency')
    def test_with_mocking(self, mock_dependency):
        """Test with external dependency mocked"""
        # Setup mock
        mock_dependency.return_value = "mock_response"
        
        # Test implementation
        result = your_function_with_dependency()
        
        # Verify mock was called
        mock_dependency.assert_called_once()
        assert result == "expected_result"
```

### Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Naming**: Test names should describe what is being tested
3. **Mock External Dependencies**: Don't make real API calls or database connections
4. **Test Edge Cases**: Include tests for error conditions and boundary values
5. **Use Fixtures**: For shared test data or setup
6. **Assert Clearly**: Use descriptive assertion messages

### Example Test Method
```python
def test_convert_mbtu_to_kwh_with_valid_input(self):
    """Test MBtu to kWh conversion with valid positive input"""
    # Test known conversion: 1 MBtu = 293.071 kWh
    input_mbtu = 5.0
    expected_kwh = 1465.355  # 5 * 293.071
    
    result = convert_mbtu_to_kwh(input_mbtu)
    
    assert abs(result - expected_kwh) < 0.001, f"Expected {expected_kwh}, got {result}"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are properly mocked before importing modules
2. **Mock Setup**: Mock external dependencies at the module level, not instance level
3. **Async Tests**: Use `@pytest.mark.asyncio` for testing async functions
4. **Environment Variables**: Mock `os.getenv` calls to avoid environment dependencies

### Debug Failed Tests
```bash
# Run with maximum verbosity and show local variables
pytest tests/test_specific.py::test_function -vv -s --tb=long

# Run and drop into debugger on failure
pytest tests/test_specific.py::test_function --pdb

# Run specific test with coverage
pytest tests/test_specific.py::test_function --cov=module_under_test --cov-report=term-missing
```

## Coverage Goals

Target coverage percentages:
- Overall: 85%+
- Critical modules (utils, main): 90%+
- Models: 95%+ (should be easy with validation tests)
- Conversions: 95%+ (mathematical functions should be thoroughly tested)

Generate coverage report:
```bash
python run_tests.py --coverage
# Open htmlcov/index.html in browser for detailed report
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add appropriate test markers
4. Update this README if adding new test categories
5. Aim for 90%+ coverage on new code

## Test Data

Create realistic test data that:
- Covers edge cases
- Uses representative values from the energy modeling domain
- Includes both valid and invalid data for validation testing
- Tests boundary conditions (very large/small values, empty data, etc.)

Example:
```python
SAMPLE_PROJECT_DATA = {
    "project_use_type_id": 1,  # Office
    "project_phase_id": 2,     # Design
    "project_construction_category_id": 3,  # New Construction
    "project_id": "TEST_OFFICE_001",
    "year": 2024,
    "baseline_eeu_id": 100,
    "design_eeu_id": 101
}
``` 