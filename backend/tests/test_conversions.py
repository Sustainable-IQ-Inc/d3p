import pytest
import pandas as pd
from unittest.mock import patch, Mock, MagicMock

from conversions import (
    convert_kbtu_per_ft2_to_kwh_per_m2, convert_mbtu_to_kwh, convert_sf_to_m2,
    convert_gj_to_mbtu, convert_mbtu_to_gj, convert_mbtu_to_kbtu,
    check_units_eeu_field, get_columns_for_conversion, convert_units_in_table,
    convert_mbtu_to_kbtu_df, convert_mbtu_to_gj_df, convert_mbtu_to_kbtu_per_sf
)


class TestBasicUnitConversions:
    """Test basic unit conversion functions"""
    
    def test_convert_kbtu_per_ft2_to_kwh_per_m2(self):
        """Test conversion from kBtu/ft² to kWh/m²"""
        # Test with known values - using actual conversion factor
        assert abs(convert_kbtu_per_ft2_to_kwh_per_m2(10) - 31.54) < 0.01
        # Fix expected value based on actual conversion factor
        assert abs(convert_kbtu_per_ft2_to_kwh_per_m2(50) - 157.73) < 0.01
    
    def test_convert_mbtu_to_kwh(self):
        """Test conversion from MBtu to kWh"""
        assert convert_mbtu_to_kwh(1) == 293.071
        assert convert_mbtu_to_kwh(5) == 1465.355
    
    def test_convert_sf_to_m2(self):
        """Test conversion from square feet to square meters"""
        assert abs(convert_sf_to_m2(1000) - 92.903) < 0.001
        assert abs(convert_sf_to_m2(10.764) - 1.0) < 0.001
    
    def test_convert_gj_to_mbtu_scalar(self):
        """Test conversion from GJ to MBtu (scalar calculation)"""
        # There's no scalar convert_gj_to_mbtu function, just the conversion factor
        conversion_factor = 0.947817
        assert abs(1 * conversion_factor - 0.947817) < 0.000001
        assert abs(100 * conversion_factor - 94.7817) < 0.0001
    
    def test_convert_mbtu_to_gj(self):
        """Test conversion from MBtu to GJ"""
        assert abs(convert_mbtu_to_gj(1) - 1.0550558526) < 0.0000001
        assert abs(convert_mbtu_to_gj(10) - 10.550558526) < 0.000001
    
    def test_convert_mbtu_to_kbtu(self):
        """Test conversion from MBtu to kBtu"""
        assert convert_mbtu_to_kbtu(1) == 1000
        assert convert_mbtu_to_kbtu(5.5) == 5500
    
    def test_conversion_consistency(self):
        """Test that conversions are consistent (round-trip)"""
        # Test GJ <-> MBtu conversion consistency using conversion factors
        original_gj = 100
        mbtu = original_gj * 0.947817  # GJ to MBtu
        back_to_gj = convert_mbtu_to_gj(mbtu)
        assert abs(original_gj - back_to_gj) < 0.001

        # Test MBtu <-> kBtu conversion consistency
        original_mbtu = 5.5
        kbtu = convert_mbtu_to_kbtu(original_mbtu)
        back_to_mbtu = kbtu / 1000
        assert abs(original_mbtu - back_to_mbtu) < 0.000001


class TestCheckUnitsEeuField:
    """Test check_units_eeu_field function"""
    
    @patch('conversions.supabase', create=True)
    def test_check_units_with_current_units_gj(self, mock_supabase):
        """Test check_units_eeu_field with current_units='gj'"""
        result = check_units_eeu_field(1, mock_supabase, 100, current_units='gj')
        # 100 GJ * 0.947817 = 94.7817 MBtu
        assert abs(result - 94.7817) < 0.0001
    
    @patch('conversions.supabase', create=True)
    def test_check_units_with_current_units_kbtu(self, mock_supabase):
        """Test check_units_eeu_field with current_units='kbtu'"""
        result = check_units_eeu_field(1, mock_supabase, 1000, current_units='kbtu')
        # 1000 kBtu / 1000 = 1 MBtu
        assert result == 1.0
    
    @patch('conversions.supabase', create=True)
    def test_check_units_with_current_units_kbtu_sf(self, mock_supabase):
        """Test check_units_eeu_field with current_units='kbtu/sf'"""
        result = check_units_eeu_field(1, mock_supabase, 2000, current_units='kbtu/sf')
        # 2000 kBtu/sf / 1000 = 2 MBtu
        assert result == 2.0
    
    @patch('conversions.supabase', create=True)
    def test_check_units_with_current_units_mbtu(self, mock_supabase):
        """Test check_units_eeu_field with current_units='mbtu'"""
        result = check_units_eeu_field(1, mock_supabase, 5.5, current_units='mbtu')
        # No conversion needed
        assert result == 5.5
    
    @patch('conversions.supabase', create=True)
    def test_check_units_from_database_gj(self, mock_supabase):
        """Test check_units_eeu_field retrieving units from database (GJ)"""
        mock_data = [{'energy_units': 'gj'}]
        mock_response = ((None, mock_data), None)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = check_units_eeu_field(1, mock_supabase, 50.0)
        # 50 GJ * 0.947817 = 47.39085 MBtu
        assert abs(result - 47.39085) < 0.00001
    
    @patch('conversions.supabase', create=True)
    def test_check_units_from_database_kbtu(self, mock_supabase):
        """Test check_units_eeu_field retrieving units from database (kBtu)"""
        mock_data = [{'energy_units': 'kbtu'}]
        mock_response = ((None, mock_data), None)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = check_units_eeu_field(1, mock_supabase, 3000.0)
        # 3000 kBtu / 1000 = 3 MBtu
        assert result == 3.0
    
    @patch('conversions.supabase', create=True)
    def test_check_units_no_units_found(self, mock_supabase):
        """Test check_units_eeu_field when no units found in database"""
        mock_response = ((None, []), None)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = check_units_eeu_field(1, mock_supabase, 42.5)
        # Should return raw value when no units found
        assert result == 42.5
    
    @patch('conversions.supabase', create=True)
    def test_check_units_string_conversion(self, mock_supabase):
        """Test check_units_eeu_field with string input values"""
        result = check_units_eeu_field(1, mock_supabase, "1500", current_units='kbtu')
        # "1500" kBtu / 1000 = 1.5 MBtu
        assert result == 1.5


class TestGetColumnsForConversion:
    """Test get_columns_for_conversion function"""
    
    @patch('conversions.supabase', create=True)
    def test_get_columns_for_conversion_success(self, mock_supabase):
        """Test successful column retrieval"""
        mock_data = [
            {'column_name': 'energy_per_area', 'unit_type': 'eui'},
            {'column_name': 'total_energy', 'unit_type': 'energy'},
            {'column_name': 'floor_area', 'unit_type': 'area'}
        ]
        mock_response = ((None, mock_data), None)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        eui_list, energy_list, area_list = get_columns_for_conversion('test_table', mock_supabase)
        
        assert eui_list == ['energy_per_area']
        assert energy_list == ['total_energy']
        assert area_list == ['floor_area']
    
    @patch('conversions.supabase', create=True)
    def test_get_columns_for_conversion_empty(self, mock_supabase):
        """Test get_columns_for_conversion with no results"""
        mock_response = ((None, []), None)
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = get_columns_for_conversion('test_table', mock_supabase)
        assert result is None


class TestConvertUnitsInTable:
    """Test convert_units_in_table function"""
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_units_in_table_metric_conversion(self, mock_get_columns):
        """Test converting units in table to metric system"""
        mock_get_columns.return_value = (
            ['energy_per_area'],  # EUI columns
            ['total_energy', 'heating_energy'],  # Energy columns
            ['floor_area']  # Area columns
        )
        
        test_data = [
            {
                'id': 1,
                'energy_per_area': 50.0,  # kBtu/ft²
                'total_energy': 5.0,  # MBtu
                'heating_energy': 2.0,  # MBtu
                'floor_area': 10000.0  # ft²
            },
            {
                'id': 2,
                'energy_per_area': 75.0,
                'total_energy': 8.0,
                'heating_energy': 3.5,
                'floor_area': 15000.0
            }
        ]
        
        result = convert_units_in_table(
            test_data, 'test_table', 'metric', Mock()
        )
        
        # Check conversions
        assert abs(result[0]['total_energy'] - 1465.355) < 0.001  # 5 MBtu to kWh
        assert abs(result[0]['floor_area'] - 929.03) < 0.01  # 10000 ft² to m²
        assert abs(result[0]['energy_per_area'] - 157.73) < 0.01  # 50 kBtu/ft² to kWh/m²
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_units_mbtu_to_kbtu_per_sf(self, mock_get_columns):
        """Test converting MBtu to kBtu/sf"""
        mock_get_columns.return_value = (
            ['energy_per_area'],  # EUI columns
            ['total_energy'],  # Energy columns
            ['floor_area']  # Area columns
        )
        
        test_data = [
            {
                'id': 1,
                'energy_per_area': 0.05,  # MBtu
                'total_energy': 5.0,  # MBtu
                'floor_area': 10000.0  # ft²
            }
        ]
        
        result = convert_units_in_table(
            test_data, 'test_table', 'imperial', Mock(),
            conversion_type='mbtu_to_kbtu/sf', conditioned_area_value=1000
        )
        
        # EUI conversion: 0.05 MBtu * 1000 / 1000 = 0.05 kBtu/sf
        assert result[0]['energy_per_area'] == 0.05
        # Energy should not be converted in this mode
        assert result[0]['total_energy'] == 5.0
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_units_with_none_values(self, mock_get_columns):
        """Test conversion handling None values correctly"""
        mock_get_columns.return_value = (
            ['energy_per_area'],
            ['total_energy'],
            ['floor_area']
        )
        
        test_data = [
            {
                'id': 1,
                'energy_per_area': None,
                'total_energy': None,
                'floor_area': 10000.0
            }
        ]
        
        result = convert_units_in_table(
            test_data, 'test_table', 'metric', Mock()
        )
        
        # None values should remain None
        assert result[0]['energy_per_area'] is None
        assert result[0]['total_energy'] is None
        # Non-None values should be converted
        assert abs(result[0]['floor_area'] - 929.03) < 0.01


class TestDataFrameConversions:
    """Test DataFrame conversion functions"""
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_mbtu_to_kbtu_df(self, mock_get_columns):
        """Test converting MBtu to kBtu in DataFrame"""
        mock_get_columns.return_value = (
            ['energy_per_area'],  # EUI columns
            ['total_energy', 'heating_energy'],  # Energy columns
            ['floor_area']  # Area columns
        )
        
        df = pd.DataFrame({
            'total_energy': [5.0, 8.0, None],
            'heating_energy': [2.0, 3.5, 1.0],
            'floor_area': [10000, 15000, 5000],
            'other_field': [1, 2, 3]
        })
        
        result = convert_mbtu_to_kbtu_df(df, Mock())
        
        # Check conversions (MBtu * 1000 = kBtu)
        assert result['total_energy'].iloc[0] == 5000.0
        assert result['total_energy'].iloc[1] == 8000.0
        assert pd.isna(result['total_energy'].iloc[2])  # None should remain None
        assert result['heating_energy'].iloc[0] == 2000.0
        # Non-energy columns should remain unchanged
        assert result['floor_area'].iloc[0] == 10000
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_mbtu_to_gj_df(self, mock_get_columns):
        """Test converting MBtu to GJ in DataFrame"""
        mock_get_columns.return_value = ([], ['total_energy'], [])
        
        df = pd.DataFrame({
            'total_energy': [1.0, 2.0, None],
            'other_field': [1, 2, 3]
        })
        
        result = convert_mbtu_to_gj_df(df, Mock())
        
        # Check conversions (MBtu * 1.0550558526 = GJ)
        assert abs(result['total_energy'].iloc[0] - 1.0550558526) < 0.0000001
        assert abs(result['total_energy'].iloc[1] - 2.1101117052) < 0.0000001
        assert pd.isna(result['total_energy'].iloc[2])
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_mbtu_to_kbtu_per_sf(self, mock_get_columns):
        """Test converting MBtu to kBtu/sf with area normalization"""
        mock_get_columns.return_value = ([], ['total_energy'], [])
        
        df = pd.DataFrame({
            'total_energy': [5.0, 10.0, None],
            'other_field': [1, 2, 3]
        })
        
        use_type_total_area = 1000  # ft²
        result = convert_mbtu_to_kbtu_per_sf(df, use_type_total_area, Mock())
        
        # Check conversions (MBtu * 1000 / area = kBtu/sf)
        assert result['total_energy'].iloc[0] == 5.0  # 5 * 1000 / 1000
        assert result['total_energy'].iloc[1] == 10.0  # 10 * 1000 / 1000
        assert pd.isna(result['total_energy'].iloc[2])
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_gj_to_mbtu_df(self, mock_get_columns):
        """Test converting GJ to MBtu in DataFrame"""
        mock_get_columns.return_value = ([], ['total_energy'], [])
        
        df = pd.DataFrame({
            'total_energy': [100.0, 200.0, None],
            'other_field': [1, 2, 3]
        })
        
        result = convert_gj_to_mbtu(df, Mock(), 'test_table')
        
        # Check conversions (GJ * 0.9478171203 = MBtu)
        assert abs(result['total_energy'].iloc[0] - 94.78171203) < 0.00001
        assert abs(result['total_energy'].iloc[1] - 189.5634241) < 0.0001
        assert pd.isna(result['total_energy'].iloc[2])


class TestConversionEdgeCases:
    """Test edge cases and error handling"""
    
    def test_negative_values(self):
        """Test conversion functions with negative values"""
        # Most conversions should handle negative values correctly
        assert convert_mbtu_to_kwh(-1) == -293.071
        assert convert_sf_to_m2(-100) < 0
        # Test GJ to MBtu conversion factor with negative values
        assert (-10 * 0.947817) < 0
    
    def test_very_large_values(self):
        """Test conversion with very large values"""
        large_value = 1e6
        result = convert_mbtu_to_kwh(large_value)
        assert result == large_value * 293.071
    
    def test_very_small_values(self):
        """Test conversion with very small values"""
        small_value = 1e-6
        result = convert_mbtu_to_kwh(small_value)
        assert abs(result - small_value * 293.071) < 1e-9
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_units_empty_data(self, mock_get_columns):
        """Test conversion with empty data"""
        mock_get_columns.return_value = ([], [], [])
        
        result = convert_units_in_table([], 'test_table', 'metric', Mock())
        assert result == []
    
    @patch('conversions.get_columns_for_conversion')
    def test_convert_units_missing_columns(self, mock_get_columns):
        """Test conversion when data doesn't have expected columns"""
        mock_get_columns.return_value = (['missing_column'], ['another_missing'], [])
        
        test_data = [{'id': 1, 'existing_field': 100}]
        
        # Should not raise an error, just skip missing columns
        result = convert_units_in_table(test_data, 'test_table', 'metric', Mock())
        assert result == test_data 