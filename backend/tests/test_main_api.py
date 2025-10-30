import pytest
import json
from unittest.mock import patch, Mock, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# Import main without global mocking - use per-test mocking instead
from main import app
from utils import verify_token

client = TestClient(app)


class TestAuthentication:
    """Test authentication and basic endpoints"""

    def test_wake_up_authorized(self):
        """Test wake up endpoint with authorization"""
        # Override the dependency for this test
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            response = client.get("/wake-up/")
            assert response.status_code == 200
            assert response.json() == "success"
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_wake_up_unauthorized(self):
        """Test wake up endpoint without authorization"""
        def mock_verify_token():
            return {'is_authorized': False}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            response = client.get("/wake-up/")
            assert response.status_code == 200
            # The wake-up endpoint actually returns "success" regardless of auth
            assert response.json() == "success"
        finally:
            app.dependency_overrides.clear()


class TestProjectSubmission:
    """Test project submission endpoints"""

    def test_submit_project_unauthorized(self):
        """Test project submission without authorization"""
        def mock_verify_token():
            return {'is_authorized': False}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        project_data = {
            "project_use_type_id": 1,
            "project_phase_id": 2,
            "project_construction_category_id": 3,
            "project_id": "550e8400-e29b-41d4-a716-446655440002",  # Valid UUID format
            "baseline_eeu_id": 100,
            "design_eeu_id": 101,
            "energy_code_id": 5,
            "use_type_subtype_id": 10,
            "year": 2024,
            "reporting_year": 2024
        }
        
        try:
            response = client.post("/submit_project/", json=project_data)
            assert response.status_code == 200
            assert response.json() == "not authorized"
        finally:
            app.dependency_overrides.clear()

    @patch('main.supabase')
    def test_submit_project_db_error(self, mock_supabase):
        """Test project submission with database error"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        project_data = {
            "project_use_type_id": 1,
            "project_phase_id": 2,
            "project_construction_category_id": 3,
            "project_id": "550e8400-e29b-41d4-a716-446655440003",  # Valid UUID format
            "baseline_eeu_id": 100,
            "design_eeu_id": 101,
            "energy_code_id": 5,
            "use_type_subtype_id": 10,
            "year": 2024,
            "reporting_year": 2024
        }
        
        try:
            response = client.post("/submit_project/", json=project_data)
            assert response.status_code == 200
            assert response.json() == "error upload table"
        finally:
            app.dependency_overrides.clear()


class TestCompanyManagement:
    """Test company management endpoints"""

    @patch('main.supabase')
    def test_create_company_success(self, mock_supabase):
        """Test successful company creation"""
        def mock_verify_token():
            return {
                'is_authorized': True,
                'role': 'superadmin'
            }
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            (None, [{'id': 'company_123'}]), None
        )
        
        company_data = {"company_name": "Test Company"}
        
        try:
            response = client.post("/create_company/", json=company_data)
            assert response.status_code == 200
            assert response.json() == "success"
        finally:
            app.dependency_overrides.clear()

    def test_create_company_unauthorized_role(self):
        """Test company creation with wrong role"""
        def mock_verify_token():
            return {
                'is_authorized': True,
                'role': 'user'  # Not superadmin
            }
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        company_data = {"company_name": "Test Company"}
        
        try:
            response = client.post("/create_company/", json=company_data)
            assert response.status_code == 200
            assert response.json() == "not authorized"
        finally:
            app.dependency_overrides.clear()

    @patch('main.supabase')
    def test_create_company_db_error(self, mock_supabase):
        """Test company creation with database error"""
        def mock_verify_token():
            return {
                'is_authorized': True,
                'role': 'superadmin'
            }
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        company_data = {"company_name": "Test Company"}
        
        try:
            response = client.post("/create_company/", json=company_data)
            assert response.status_code == 200
            assert response.json() == "error"
        finally:
            app.dependency_overrides.clear()


class TestUserInvitation:
    """Test user invitation endpoints"""

    @patch('main.supabase')
    @patch('main.create_client')
    @patch('main.os.getenv')
    def test_invite_user_success(self, mock_getenv, mock_create_client, mock_supabase):
        """Test successful user invitation"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_getenv.return_value = "test_service_key"
        
        # Mock company lookup
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            (None, [{'company_name': 'Test Company'}]), None
        )
        
        # Mock admin client
        mock_admin_client = MagicMock()
        mock_create_client.return_value = mock_admin_client
        mock_admin_client.auth.admin.invite_user_by_email.return_value = {"user": {"id": "user_123"}}
        
        invitation_data = {
            "user_email": "test@example.com",
            "company_id": "company_123"
        }
        
        try:
            response = client.post("/invite_user/", json=invitation_data)
            assert response.status_code == 200
            assert response.json() == "success"
        finally:
            app.dependency_overrides.clear()

    def test_invite_user_unauthorized(self):
        """Test user invitation without authorization"""
        def mock_verify_token():
            return {'is_authorized': False}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        invitation_data = {
            "user_email": "test@example.com",
            "company_id": "company_123"
        }
        
        try:
            response = client.post("/invite_user/", json=invitation_data)
            assert response.status_code == 200
            assert response.json() == "not authorized"
        finally:
            app.dependency_overrides.clear()


class TestProjectCreation:
    """Test project creation endpoints"""

    @patch('main.supabase')
    def test_create_project_success(self, mock_supabase):
        """Test successful project creation"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            (None, [{'id': 'project_123'}]), None
        )
        
        project_data = {
            "company_id": "company_123",
            "project_name": "Test Project"
        }
        
        try:
            response = client.post("/create_project/", json=project_data)
            assert response.status_code == 200
            assert response.json() == {'status': 'success', 'id': 'project_123'}
        finally:
            app.dependency_overrides.clear()

    @patch('main.supabase')
    def test_create_project_db_error(self, mock_supabase):
        """Test project creation with database error"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        project_data = {
            "company_id": "company_123",
            "project_name": "Test Project"
        }
        
        try:
            response = client.post("/create_project/", json=project_data)
            assert response.status_code == 200
            assert response.json() == "error"
        finally:
            app.dependency_overrides.clear()


class TestEnumEndpoints:
    """Test enum retrieval endpoints"""

    @patch('main.return_enum_vals')
    def test_get_simple_enum_success(self, mock_return_enum_vals):
        """Test successful enum retrieval"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_return_enum_vals.return_value = [
            {'id': 1, 'name': 'Office', 'order': 1},
            {'id': 2, 'name': 'Retail', 'order': 2}
        ]
        
        try:
            response = client.get("/enums/project_use_types/")
            assert response.status_code == 200
            assert len(response.json()) == 2
            assert response.json()[0]['name'] == 'Office'
        finally:
            app.dependency_overrides.clear()

    @patch('main.return_enum_vals')
    def test_get_simple_enum_with_filter(self, mock_return_enum_vals):
        """Test enum retrieval with use_type_id filter"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_return_enum_vals.return_value = [
            {'id': 1, 'name': 'Office', 'order': 1}
        ]
        
        try:
            response = client.get("/enums/project_use_types/?use_type_id=1")
            assert response.status_code == 200
            mock_return_enum_vals.assert_called_with('project_use_types', use_type_id=1)
        finally:
            app.dependency_overrides.clear()

    def test_get_simple_enum_unauthorized(self):
        """Test enum retrieval without authorization"""
        def mock_verify_token():
            return {'is_authorized': False}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            response = client.get("/enums/project_use_types/")
            # When not authorized, the endpoint returns None (no response body)
            assert response.status_code == 200
            assert response.json() is None
        finally:
            app.dependency_overrides.clear()


class TestProjectEndpoints:
    """Test project detail endpoints"""

    @patch('main.combine_end_uses_data')
    def test_get_project_details_success(self, mock_combine_end_uses_data):
        """Test successful project details retrieval"""
        def mock_verify_token():
            return {'is_authorized': True}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        mock_combine_end_uses_data.return_value = {
            'project_id': 'project_123',
            'project_name': 'Test Project',
            'company_id': 'company_123'
        }
        
        try:
            response = client.get("/project_details/?project_id=project_123")
            assert response.status_code == 200
            # The endpoint returns the result of combine_end_uses_data
            project_details = response.json()
            assert project_details['project_id'] == 'project_123'
        finally:
            app.dependency_overrides.clear()

    def test_get_project_details_unauthorized(self):
        """Test project details retrieval without authorization"""
        def mock_verify_token():
            return {'is_authorized': False}
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            response = client.get("/project_details/?project_id=project_123")
            # When not authorized, endpoint returns "not authorized"
            assert response.status_code == 200
            assert response.json() == "not authorized"
        finally:
            app.dependency_overrides.clear()


class TestValidationHandling:
    """Test request validation and error handling"""

    def test_invalid_json_request(self):
        """Test handling of invalid JSON in request"""
        response = client.post("/submit_project/", data="invalid json")
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        incomplete_data = {
            "project_use_type_id": 1
            # Missing other required fields
        }
        
        response = client.post("/submit_project/", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_endpoint_with_missing_auth(self):
        """Test endpoint behavior when verify_token fails"""
        def mock_verify_token():
            raise Exception("Auth failed")
        
        app.dependency_overrides[verify_token] = mock_verify_token
        
        try:
            # This should raise an internal server error since dependency injection fails
            with pytest.raises(Exception):
                response = client.get("/enums/project_use_types/")
        finally:
            app.dependency_overrides.clear() 