import pytest
import pandas as pd
import os
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from fastapi import Request

from utils import (
    encrypt_value, decrypt_value, return_enum_vals, get_enum_id, 
    add_event_history, sanitize_filename, get_field_name_from_use_type,
    fuel_category_override, verify_token, create_app
)

class TestEncryption:
    """Test encryption and decryption functions"""
    
    @patch('utils.os.getenv')
    def test_encrypt_decrypt_value(self, mock_getenv):
        """Test encryption and decryption of values"""
        mock_getenv.side_effect = lambda key: {
            'ENCRYPTION_KEY': 'test_key_123',
            'ENCRYPTION_SALT': 'test_salt_456'
        }.get(key)
        
        test_value = "sensitive_data"
        encrypted = encrypt_value(test_value)
        assert encrypted != test_value
        assert encrypted is not None
        
        decrypted = decrypt_value(encrypted)
        assert decrypted == test_value
    
    def test_encrypt_empty_value(self):
        """Test encryption of empty values"""
        assert encrypt_value("") == ""
        assert encrypt_value(None) is None
    
    def test_decrypt_empty_value(self):
        """Test decryption of empty values"""
        assert decrypt_value("") == ""
        assert decrypt_value(None) is None


class TestEnumFunctions:
    """Test enum-related utility functions"""
    
    @patch('utils.supabase')
    def test_return_enum_vals_success(self, mock_supabase):
        """Test successful enum value retrieval"""
        mock_data = [
            {'id': 1, 'name': 'Office', 'order': 1},
            {'id': 2, 'name': 'Retail', 'order': 2}
        ]
        # Supabase execute() returns (data, count) where data is (None, actual_results)
        mock_response = ((None, mock_data), None)  # (data, count) where data[1] = mock_data
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        result = return_enum_vals('project_use_types')
        assert result == mock_data
        mock_supabase.table.assert_called_with('enum_project_use_types')
    
    @patch('utils.supabase')
    def test_return_enum_vals_with_filter(self, mock_supabase):
        """Test enum value retrieval with use_type_id filter"""
        mock_data = [{'id': 1, 'name': 'Office', 'order': 1}]
        mock_query = mock_supabase.table.return_value.select.return_value.order.return_value
        mock_response = ((None, mock_data), None)  # (data, count) where data[1] = mock_data
        mock_query.eq.return_value.execute.return_value = mock_response
        
        result = return_enum_vals('project_use_types', use_type_id=1)
        assert result == mock_data
        mock_query.eq.assert_called_with('use_type_id', 1)
    
    @patch('utils.supabase')
    def test_return_enum_vals_no_results(self, mock_supabase):
        """Test enum value retrieval with no results"""
        mock_response = ((None, []), None)  # (data, count) where data[1] = []
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = mock_response
        
        result = return_enum_vals('project_use_types')
        assert result == "no results"
    
    @patch('utils.supabase')
    def test_return_enum_vals_error(self, mock_supabase):
        """Test enum value retrieval with database error"""
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.side_effect = Exception("DB Error")
        
        result = return_enum_vals('project_use_types')
        assert result == "error"
    
    def test_return_enum_vals_invalid_type(self):
        """Test enum value retrieval with invalid enum type"""
        result = return_enum_vals('invalid_enum_type')
        assert result == "error"
    
    @patch('utils.return_enum_vals')
    def test_get_enum_id_success(self, mock_return_enum_vals):
        """Test successful enum ID retrieval"""
        mock_return_enum_vals.return_value = [
            {'id': 1, 'name': 'Office'},
            {'id': 2, 'name': 'Retail'}
        ]
        
        result = get_enum_id('project_use_types', 'Office')
        assert result == 1
    
    @patch('utils.return_enum_vals')
    def test_get_enum_id_not_found(self, mock_return_enum_vals):
        """Test enum ID retrieval when value not found"""
        mock_return_enum_vals.return_value = [
            {'id': 1, 'name': 'Office'},
            {'id': 2, 'name': 'Retail'}
        ]
        
        result = get_enum_id('project_use_types', 'NonExistent')
        assert result is None


class TestEventHistory:
    """Test event history logging"""
    
    @patch('utils.supabase')
    def test_add_event_history_success(self, mock_supabase):
        """Test successful event history addition"""
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (None, [{'id': 1}])
        
        result = add_event_history('projects', 'project_name', '123', 'New Name', 'user_123', 'Old Name')
        assert result == "success"
        
        # Verify the correct data was inserted
        mock_supabase.table.assert_called_with('event_history')
        call_args = mock_supabase.table.return_value.insert.call_args[0][0][0]
        assert call_args['table_name'] == 'projects'
        assert call_args['field_name'] == 'project_name'
        assert call_args['ref_id'] == '123'
        assert call_args['new_value'] == 'New Name'
        assert call_args['updated_by'] == 'user_123'
        assert call_args['previous_value'] == 'Old Name'
    
    @patch('utils.supabase')
    def test_add_event_history_error(self, mock_supabase):
        """Test event history addition with database error"""
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        result = add_event_history('projects', 'project_name', '123', 'New Name', 'user_123', 'Old Name')
        assert result == "error"


class TestUtilityFunctions:
    """Test various utility functions"""
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        assert sanitize_filename('file name.txt') == 'file_name.txt'
        assert sanitize_filename('file*name?.txt') == 'filename.txt'
        assert sanitize_filename('file\\name/test.txt') == 'filenametest.txt'
        assert sanitize_filename('file:name<test>.txt') == 'filenametest.txt'
    
    @patch('utils.supabase')
    def test_get_field_name_from_use_type(self, mock_supabase):
        """Test field name retrieval from use type"""
        mock_data = [{'field_name': 'office_energy'}]
        mock_response = ((None, mock_data), None)  # (data, count) where data[1] = mock_data
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_response
        
        result = get_field_name_from_use_type('Office', 'Electricity')
        assert result == 'office_energy'
    
    def test_fuel_category_override(self):
        """Test fuel category override mappings"""
        assert fuel_category_override('Fossil_Fuels') == 'NaturalGas'
        assert fuel_category_override('District') == 'DistrictHeating'
        assert fuel_category_override('Onsite_Renewables') == 'On-SiteRenewables'
        assert fuel_category_override('onsite_renewables') == 'On-SiteRenewables'
        assert fuel_category_override('Electricity') == 'Electricity'


class TestAuthentication:
    """Test authentication and authorization"""
    
    @pytest.mark.asyncio
    @patch('utils.supabase')
    async def test_verify_token_success(self, mock_supabase):
        """Test successful token verification"""
        mock_request = Mock(spec=Request)
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        
        mock_user = Mock()
        mock_user.user_metadata = {
            'company_id': 'company_123',
            'role': 'admin'
        }
        mock_user.id = 'user_123'
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_supabase.auth.get_user.return_value = mock_auth_response
        
        result = await verify_token(mock_request)
        
        expected = {
            'is_authorized': True,
            'company_id': 'company_123',
            'role': 'admin',
            'user_id': 'user_123'
        }
        assert result == expected
    
    @pytest.mark.asyncio
    @patch('utils.supabase')
    async def test_verify_token_no_role(self, mock_supabase):
        """Test token verification with no role in metadata"""
        mock_request = Mock(spec=Request)
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        
        mock_user = Mock()
        mock_user.user_metadata = {'company_id': 'company_123'}
        mock_user.id = 'user_123'
        
        mock_auth_response = Mock()
        mock_auth_response.user = mock_user
        mock_supabase.auth.get_user.return_value = mock_auth_response
        
        result = await verify_token(mock_request)
        assert result['role'] == 'NA'
    
    @pytest.mark.asyncio
    async def test_verify_token_no_bearer(self):
        """Test token verification without Bearer prefix"""
        mock_request = Mock(spec=Request)
        mock_request.headers = {'Authorization': 'invalid_format'}
        
        result = await verify_token(mock_request)
        assert result == {'is_authorized': False}
    
    @pytest.mark.asyncio
    async def test_verify_token_no_header(self):
        """Test token verification without Authorization header"""
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        
        result = await verify_token(mock_request)
        assert result == {'is_authorized': False}
    
    @pytest.mark.asyncio
    @patch('utils.supabase')
    async def test_verify_token_auth_error(self, mock_supabase):
        """Test token verification with authentication error"""
        mock_request = Mock(spec=Request)
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        
        mock_supabase.auth.get_user.side_effect = Exception("Invalid token")
        
        result = await verify_token(mock_request)
        assert result == {'is_authorized': False}


class TestAppCreation:
    """Test FastAPI app creation and configuration"""
    
    @patch('utils.os.getenv')
    def test_create_app_with_cors(self, mock_getenv):
        """Test app creation with CORS configuration"""
        mock_getenv.return_value = 'http://localhost:3000,https://example.com'
        
        app = create_app()
        
        # Verify FastAPI app is created
        assert app is not None
        # Check that middleware was added (can't easily test the actual CORS config)
        assert hasattr(app, 'user_middleware')
    
    @patch('utils.os.getenv')
    def test_create_app_no_origins(self, mock_getenv):
        """Test app creation with no CORS origins"""
        mock_getenv.return_value = ''
        
        app = create_app()
        assert app is not None 