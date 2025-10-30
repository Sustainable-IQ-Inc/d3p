import pytest
import pandas as pd
import os
from unittest.mock import patch, Mock, MagicMock
import logging_start

from weather_location import weather_check, format_as_zip_code, get_subregion_by_zip, latlong_to_zip

# Mock data for testing
MOCK_WEATHER_OUTPUT = pd.DataFrame({
    'wmo_code': [123456],
    'climate_zone': ['4A'],
    'lat': [40.7128],
    'long': [-74.0060]
})

MOCK_CITIES = pd.DataFrame({
    'city_ascii': ['New York'],
    'state_id': ['NY'],
    'state_name': ['New York'],
    'zips': ['10001 10002'],
    'lat': [40.7128],
    'lng': [-74.0060]
})

@pytest.fixture(autouse=True)
def mock_logger():
    with patch.object(logging_start, 'logger') as mock:
        mock.info = MagicMock()
        mock.error = MagicMock()
        yield mock

@pytest.fixture(autouse=True)
def mock_rapidfuzz():
    with patch('weather_location.process') as mock_process:
        mock_process.extractOne.return_value = ('New York NY', 100)
        yield mock_process

@pytest.fixture
def mock_csv_reads(monkeypatch):
    def mock_read_csv(path):
        if 'weather_output_new.csv' in path:
            return MOCK_WEATHER_OUTPUT
        elif 'uscities.csv' in path:
            return MOCK_CITIES
        raise ValueError(f"Unexpected path: {path}")
    
    monkeypatch.setattr(pd, "read_csv", mock_read_csv)

@pytest.fixture
def mock_latlong_to_zip():
    with patch('weather_location.latlong_to_zip') as mock:
        mock.return_value = '10001'
        yield mock

@pytest.fixture
def mock_get_subregion():
    with patch('weather_location.get_subregion_by_zip') as mock:
        mock.return_value = 'NYCW'
        yield mock

def test_weather_check_iesve(mock_csv_reads, mock_latlong_to_zip, mock_get_subregion):
    """Test weather_check with IESVE report type"""
    result = weather_check('USA_NY_123456', 'iesve')
    
    assert result['climate_zone'] == '4A'
    assert result['zip_code'] == '10001'
    assert result['state'] == 'New York'
    assert result['egrid_subregion'] == 'NYCW'

def test_weather_check_equest_beps(mock_csv_reads, mock_get_subregion):
    """Test weather_check with equest_beps report type"""
    result = weather_check('New York NY', 'equest_beps')
    
    assert result['city_name'] == 'New York, NY'
    assert result['zip_code'] == '10001'
    assert result['state'] == 'New York'
    assert result['egrid_subregion'] == 'NYCW'

def test_weather_check_equest_standard(mock_csv_reads, mock_get_subregion):
    """Test weather_check with equest_standard report type"""
    with patch('weather_location.get_climate_zone_by_zip') as mock_climate:
        mock_climate.return_value = {
            'climate_zone': '4A',
            'zip_code': '10001',
            'city': 'New York',
            'state': 'NY'
        }
        
        result = weather_check('10001', 'equest_standard')
        
        assert result['climate_zone'] == '4A'
        assert result['zip_code'] == '10001'
        assert result['state'] == 'New York'
        assert result['egrid_subregion'] == 'NYCW'

def test_weather_check_invalid_report_type(mock_csv_reads):
    """Test weather_check with invalid report type"""
    result = weather_check('test', 'invalid_type')
    
    assert result['city_name'] == ''
    assert result['zip_code'] == ''
    assert result['state'] == ''

def test_weather_check_invalid_weather_string(mock_csv_reads):
    """Test weather_check with invalid weather string"""
    result = weather_check('invalid_string', 'iesve')
    
    assert result['city_name'] == ''
    assert result['zip_code'] == ''
    assert result['state'] == ''

def test_weather_check_missing_data(mock_csv_reads):
    """Test weather_check with missing data"""
    # Override mock data to simulate missing data
    empty_df = pd.DataFrame(columns=['wmo_code', 'climate_zone', 'lat', 'long'])
    with patch('pandas.read_csv', return_value=empty_df):
        result = weather_check('USA_NY_123456', 'iesve')
        
        assert result['city_name'] == ''
        assert result['zip_code'] == ''
        assert result['state'] == '' 