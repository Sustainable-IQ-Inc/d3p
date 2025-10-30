import pytest
from pydantic import ValidationError
from typing import Optional, Dict, Union, List

from models import (
    MultiUpload, SubmitProject, CreateCompany, ExportProjectToDDX,
    ProjectIdsList, CreateProject, InviteUser, Project, ProjectUpdate,
    UploadUpdate, EEUUpdate, SimpleEnum, ZipUpdate, FlexibleModel,
    DDXImportProject
)


class TestMultiUpload:
    """Test MultiUpload model"""
    
    def test_valid_multi_upload(self):
        """Test valid MultiUpload creation"""
        data = {
            "design_files": ["file1.csv", "file2.csv"],
            "baseline_files": ["baseline1.csv"]
        }
        upload = MultiUpload(**data)
        assert upload.design_files == ["file1.csv", "file2.csv"]
        assert upload.baseline_files == ["baseline1.csv"]
    
    def test_multi_upload_optional_fields(self):
        """Test MultiUpload with optional fields"""
        # All fields are required in the actual model
        upload = MultiUpload(design_files=None, baseline_files=None)
        assert upload.design_files is None
        assert upload.baseline_files is None
    
    def test_multi_upload_empty_lists(self):
        """Test MultiUpload with empty lists"""
        data = {
            "design_files": [],
            "baseline_files": []
        }
        upload = MultiUpload(**data)
        assert upload.design_files == []
        assert upload.baseline_files == []


class TestSubmitProject:
    """Test SubmitProject model"""
    
    def test_valid_submit_project(self):
        """Test valid SubmitProject creation"""
        data = {
            "project_use_type_id": 1,
            "project_phase_id": 2,
            "project_construction_category_id": 3,
            "project_id": "TEST_001",
            "year": 2024,
            "reporting_year": 2024,
            "baseline_eeu_id": None,
            "design_eeu_id": None,
            "energy_code_id": None,
            "use_type_subtype_id": None
        }
        project = SubmitProject(**data)
        assert project.project_use_type_id == 1
        assert project.project_phase_id == 2
        assert project.project_construction_category_id == 3
        assert project.project_id == "TEST_001"
        assert project.year == 2024
        assert project.reporting_year == 2024
    
    def test_submit_project_with_optional_fields(self):
        """Test SubmitProject with optional fields"""
        data = {
            "project_use_type_id": 1,
            "project_phase_id": 2,
            "project_construction_category_id": 3,
            "project_id": "TEST_001",
            "year": 2024,
            "reporting_year": 2024,
            "baseline_eeu_id": 100,
            "design_eeu_id": 101,
            "energy_code_id": 5,
            "use_type_subtype_id": 10
        }
        project = SubmitProject(**data)
        assert project.baseline_eeu_id == 100
        assert project.design_eeu_id == 101
        assert project.energy_code_id == 5
        assert project.use_type_subtype_id == 10
        assert project.reporting_year == 2024
    
    def test_submit_project_missing_required_fields(self):
        """Test SubmitProject with missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            SubmitProject(project_use_type_id=1)
        
        errors = exc_info.value.errors()
        missing_fields = {error['loc'][0] for error in errors}
        expected_missing = {
            'project_phase_id', 
            'project_construction_category_id', 
            'project_id'
        }
        assert expected_missing.issubset(missing_fields)
    
    def test_submit_project_invalid_types(self):
        """Test SubmitProject with invalid field types"""
        with pytest.raises(ValidationError):
            SubmitProject(
                project_use_type_id="not_an_integer",
                project_phase_id=2,
                project_construction_category_id=3,
                project_id="TEST_001"
            )


class TestCreateCompany:
    """Test CreateCompany model"""
    
    def test_valid_create_company(self):
        """Test valid CreateCompany creation"""
        data = {"company_name": "Test Company Inc."}
        company = CreateCompany(**data)
        assert company.company_name == "Test Company Inc."
    
    def test_create_company_missing_name(self):
        """Test CreateCompany with missing company name"""
        with pytest.raises(ValidationError) as exc_info:
            CreateCompany()
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'company_name' for error in errors)
    
    def test_create_company_empty_string(self):
        """Test CreateCompany with empty string"""
        # Pydantic allows empty strings by default
        company = CreateCompany(company_name="")
        assert company.company_name == ""


class TestExportProjectToDDX:
    """Test ExportProjectToDDX model"""
    
    def test_valid_export_project(self):
        """Test valid ExportProjectToDDX creation"""
        data = {
            "project_id": "project_123",
            "edited_values": {
                "project_name": "Updated Project",
                "area": 5000,
                "energy_savings": 25.5
            }
        }
        export = ExportProjectToDDX(**data)
        assert export.project_id == "project_123"
        assert export.edited_values["project_name"] == "Updated Project"
        assert export.edited_values["area"] == 5000
        assert export.edited_values["energy_savings"] == 25.5
    
    def test_export_project_no_edited_values(self):
        """Test ExportProjectToDDX without edited values"""
        data = {"project_id": "project_123"}
        export = ExportProjectToDDX(**data)
        assert export.project_id == "project_123"
        assert export.edited_values is None
    
    def test_export_project_empty_edited_values(self):
        """Test ExportProjectToDDX with empty edited values"""
        data = {
            "project_id": "project_123",
            "edited_values": {}
        }
        export = ExportProjectToDDX(**data)
        assert export.edited_values == {}


class TestProjectIdsList:
    """Test ProjectIdsList model"""
    
    def test_valid_project_ids_list(self):
        """Test valid ProjectIdsList creation"""
        data = {
            "project_ids": ["project_1", "project_2", "project_3"]
        }
        project_list = ProjectIdsList(**data)
        assert len(project_list.project_ids) == 3
        assert "project_2" in project_list.project_ids
    
    def test_empty_project_ids_list(self):
        """Test ProjectIdsList with empty list"""
        data = {"project_ids": []}
        project_list = ProjectIdsList(**data)
        assert project_list.project_ids == []
    
    def test_project_ids_list_missing_field(self):
        """Test ProjectIdsList with missing field"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectIdsList()
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'project_ids' for error in errors)


class TestCreateProject:
    """Test CreateProject model"""
    
    def test_valid_create_project(self):
        """Test valid CreateProject creation"""
        data = {
            "company_id": "company_123",
            "project_name": "New Office Building"
        }
        project = CreateProject(**data)
        assert project.company_id == "company_123"
        assert project.project_name == "New Office Building"
    
    def test_create_project_missing_fields(self):
        """Test CreateProject with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            CreateProject(company_id="company_123")
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'project_name' for error in errors)


class TestInviteUser:
    """Test InviteUser model"""
    
    def test_valid_invite_user(self):
        """Test valid InviteUser creation"""
        data = {
            "user_email": "test@example.com",
            "company_id": "company_123"
        }
        invite = InviteUser(**data)
        assert invite.user_email == "test@example.com"
        assert invite.company_id == "company_123"
    
    def test_invite_user_missing_fields(self):
        """Test InviteUser with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            InviteUser(user_email="test@example.com")
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'company_id' for error in errors)


class TestProjectUpdate:
    """Test ProjectUpdate model"""
    
    def test_valid_project_update(self):
        """Test valid ProjectUpdate creation"""
        data = {
            "project_id": "project_123",
            "project_name": "Updated Project Name",
            "project_use_type_id": "2",
            "custom_project_id": "CUSTOM_001",
            "user_id": "user_456"
        }
        update = ProjectUpdate(**data)
        assert update.project_id == "project_123"
        assert update.project_name == "Updated Project Name"
        assert update.project_use_type_id == "2"
        assert update.custom_project_id == "CUSTOM_001"
        assert update.user_id == "user_456"
    
    def test_project_update_required_fields_only(self):
        """Test ProjectUpdate with only required fields"""
        data = {
            "project_id": "project_123",
            "user_id": "user_456"
        }
        update = ProjectUpdate(**data)
        assert update.project_id == "project_123"
        assert update.user_id == "user_456"
        assert update.project_name is None
        assert update.project_use_type_id is None
        assert update.custom_project_id is None


class TestUploadUpdate:
    """Test UploadUpdate model"""
    
    def test_valid_upload_update(self):
        """Test valid UploadUpdate creation"""
        data = {
            "project_id": "project_123",
            "project_use_type_id": 1,
            "energy_code_id": 5,
            "project_construction_category_id": 2,
            "project_phase_id": 3,
            "year": 2024,
            "climate_zone": 4,
            "custom_project_id": "CUSTOM_001",
            "ddx_override_use_type_total_area_sf": "5000"
        }
        update = UploadUpdate(**data)
        assert update.project_id == "project_123"
        assert update.project_use_type_id == 1
        assert update.year == 2024
        assert update.ddx_override_use_type_total_area_sf == "5000"
    
    def test_upload_update_required_only(self):
        """Test UploadUpdate with only required field"""
        data = {"project_id": "project_123"}
        update = UploadUpdate(**data)
        assert update.project_id == "project_123"
        assert update.project_use_type_id is None


class TestEEUUpdate:
    """Test EEUUpdate model"""
    
    def test_valid_eeu_update(self):
        """Test valid EEUUpdate creation"""
        data = {
            "project_id": "project_123",
            "use_type_total_area": "5000",
            "climate_zone": "4A",
            "zip_code": "10001",
            "city": "New York",
            "state": "NY",
            "new_value": "6000",
            "cell_key": "total_area",
            "eeu_id": 100,
            "current_units": "sf"
        }
        update = EEUUpdate(**data)
        assert update.project_id == "project_123"
        assert update.use_type_total_area == "5000"
        assert update.climate_zone == "4A"
        assert update.zip_code == "10001"
        assert update.eeu_id == 100
    
    def test_eeu_update_all_optional(self):
        """Test EEUUpdate with all optional fields"""
        update = EEUUpdate()
        assert update.project_id is None
        assert update.use_type_total_area is None
        assert update.eeu_id is None


class TestSimpleEnum:
    """Test SimpleEnum model"""
    
    def test_valid_simple_enum(self):
        """Test valid SimpleEnum creation"""
        data = {
            "id": 1,
            "name": "Office",
            "order": 10
        }
        enum = SimpleEnum(**data)
        assert enum.id == 1
        assert enum.name == "Office"
        assert enum.order == 10
    
    def test_simple_enum_missing_fields(self):
        """Test SimpleEnum with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            SimpleEnum(id=1, name="Office")
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'order' for error in errors)


class TestZipUpdate:
    """Test ZipUpdate model"""
    
    def test_valid_zip_update(self):
        """Test valid ZipUpdate creation"""
        data = {
            "zip_code": "10001",
            "project_id": "project_123"
        }
        update = ZipUpdate(**data)
        assert update.zip_code == "10001"
        assert update.project_id == "project_123"
    
    def test_zip_update_missing_fields(self):
        """Test ZipUpdate with missing fields"""
        with pytest.raises(ValidationError) as exc_info:
            ZipUpdate(zip_code="10001")
        
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'project_id' for error in errors)


class TestFlexibleModel:
    """Test FlexibleModel that allows extra fields"""
    
    def test_flexible_model_extra_fields(self):
        """Test FlexibleModel with extra fields"""
        data = {
            "standard_field": "value",
            "extra_field1": "extra_value1",
            "extra_field2": 123,
            "extra_field3": {"nested": "data"}
        }
        model = FlexibleModel(**data)
        assert model.standard_field == "value"
        assert model.extra_field1 == "extra_value1"
        assert model.extra_field2 == 123
        assert model.extra_field3 == {"nested": "data"}
    
    def test_flexible_model_empty(self):
        """Test FlexibleModel with no fields"""
        model = FlexibleModel()
        # Should not raise an error
        assert model is not None


class TestDDXImportProject:
    """Test DDXImportProject model with all required fields"""
    
    def test_valid_ddx_import_project(self):
        """Test valid DDXImportProject creation"""
        data = {
            "authToken": "auth123",
            "projectName": "Test Building",
            "projectId": "DDX_001",
            "projectPhase": "Design",
            "reportingYear": "2024",
            "estimatedOccupancyYear": "2025",
            "country": "USA",
            "state": "NY",
            "zipcode": "10001",
            "city": "New York",
            "climateZone": "4A",
            "useType1": "Office",
            "useType1Area": 25000.0,
            "designEnergyCode": "ASHRAE 90.1-2019",
            "baselineEUI": 85.5,
            "predictedEUI": 65.2,
            "energyModelingTool": "EnergyPlus",
            "districtChilledWater": 0.0,
            "districtHotWater": 0.0,
            "districtSteam": 0.0,
            "naturalGasCombustedOnSite": 450.5,
            "electricityProducedOffSite": 1200.8,
            "diesel": 0.0,
            "electricityFromRenewablesOnSite": 150.0
        }
        project = DDXImportProject(**data)
        assert project.authToken == "auth123"
        assert project.projectName == "Test Building"
        assert project.useType1Area == 25000.0
        assert project.baselineEUI == 85.5
        assert project.predictedEUI == 65.2
        assert project.estimatedOccupancyYear == "2025"
    
    def test_ddx_import_project_missing_required_fields(self):
        """Test DDXImportProject with missing required fields"""
        incomplete_data = {
            "authToken": "auth123",
            "projectName": "Test Building",
            # Missing many required fields
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DDXImportProject(**incomplete_data)
        
        errors = exc_info.value.errors()
        # Should have multiple missing field errors
        assert len(errors) > 5
        
        # Check for some expected missing fields
        missing_fields = {error['loc'][0] for error in errors}
        expected_missing = {
            'projectId', 'projectPhase', 'reportingYear',
            'estimatedOccupancyYear', 'country', 'state', 'zipcode'
        }
        assert expected_missing.issubset(missing_fields)
    
    def test_ddx_import_project_invalid_types(self):
        """Test DDXImportProject with invalid field types"""
        invalid_data = {
            "authToken": "auth123",
            "projectName": "Test Building",
            "projectId": "DDX_001",
            "projectPhase": "Design",
            "reportingYear": "2024",
            "estimatedOccupancyYear": "2025",
            "country": "USA",
            "state": "NY",
            "zipcode": "10001",
            "city": "New York",
            "climateZone": "4A",
            "useType1": "Office",
            "useType1Area": "not_a_number",  # Should be float
            "designEnergyCode": "ASHRAE 90.1-2019",
            "baselineEUI": "not_a_number",  # Should be float
            "predictedEUI": 65.2,
            "energyModelingTool": "EnergyPlus",
            "districtChilledWater": 0.0,
            "districtHotWater": 0.0,
            "districtSteam": 0.0,
            "naturalGasCombustedOnSite": 450.5,
            "electricityProducedOffSite": 1200.8,
            "diesel": 0.0,
            "electricityFromRenewablesOnSite": 150.0
        }
        
        with pytest.raises(ValidationError) as exc_info:
            DDXImportProject(**invalid_data)
        
        errors = exc_info.value.errors()
        # Should have validation errors for the non-numeric fields
        assert len(errors) >= 2 