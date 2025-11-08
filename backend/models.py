from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List
from dataclasses import dataclass
from fastapi import Form, UploadFile

class MultiUpload(BaseModel):
    design_files: Optional[list]
    baseline_files: Optional[list]

class SubmitProject(BaseModel):
    #conditioned_area: float
    #climate_zone: int
    project_use_type_id: int
    project_phase_id: int
    project_construction_category_id: int
    baseline_eeu_id: Optional[int]
    design_eeu_id: Optional[int]
    project_id: str
    energy_code_id: Optional[int]
    use_type_subtype_id: Optional[int]
    #other_energy_code: Optional[str]
    year: Optional[int]  # occupancy_year
    reporting_year: Optional[int]

class CreateCompany(BaseModel):
    company_name: str

class ExportProjectToDDX(BaseModel):
    project_id: str
    edited_values: Optional[Dict[str, Union[str, int, float]]] = None

class ProjectIdsList(BaseModel):
    project_ids: List[str]

class ExportProjectsCSVRequest(BaseModel):
    company_id: Optional[str] = None
    project_id: Optional[str] = None
    search_term: Optional[str] = None
    measurement_system: Optional[str] = 'imperial'

@dataclass
class ReportUpload:
    #report_type: Optional[int] = Form(...)
    baseline_design: str = Form(...)
    conditioned_area: Optional[float] = Form(None)
    area_units: Optional[str] = Form(None)
    file: UploadFile = Form(...)
    company_id: str = Form(...)

class CreateProject(BaseModel):
    company_id: str
    project_name: str

class InviteUser(BaseModel):
    user_email: str
    company_id: str

class Project(BaseModel):
    CreateProject: CreateProject
    project_id: str
class ProjectUpdate(BaseModel):
    project_id: str
    project_name: Optional[str] = None
    project_use_type_id: Optional[int] = None
    energy_code_id: Optional[int] = None
    project_construction_category_id: Optional[int] = None
    project_phase_id: Optional[int] = None
    year: Optional[int] = None
    reporting_year: Optional[int] = None
    custom_project_id: Optional[str] = None
    user_id: str
    use_type_total_area: Optional[str] = None


class UploadUpdate(BaseModel):
    project_id: str
    project_use_type_id: Optional[int] = None
    energy_code_id: Optional[int] = None
    project_construction_category_id: Optional[int] = None
    project_phase_id: Optional[int] = None
    year: Optional[int] = None  # occupancy_year
    reporting_year: Optional[int] = None
    climate_zone: Optional[int] = None
    custom_project_id: Optional[str] = None
    ddx_override_use_type_total_area_sf: Optional[str] = None
    use_type_total_area: Optional[str] = None

class EEUUpdate(BaseModel):
    project_id: Optional[str] = None
    use_type_total_area: Optional[str] = None
    climate_zone: Optional[str] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    new_value: Optional[str] = None
    cell_key: Optional[str] = None
    eeu_id: Optional[int] = None
    current_units: Optional[str] = None

class GSFUpdate(BaseModel):
    project_id: str
    use_type_total_area: str

#create classes for enums from supabase

class SimpleEnum(BaseModel):
    id: int
    name: str 
    order: int

class ZipUpdate(BaseModel):
    zip_code: str
    project_id: str

class FlexibleModel(BaseModel):
    class Config:
        extra = 'allow'  # Allow extra fields not explicitly defined


class MultiProjectExcelUpload(BaseModel):
    file_url: str
    company_id: str

class MultiProjectResult(BaseModel):
    status: str
    total_projects: int
    successful_projects: int
    failed_projects: int
    validation_errors: List[str]
    created_project_ids: List[str]
    created_projects: List[Dict[str, str]]

class DDXImportProject(BaseModel):
    authToken: str = Field(..., display_name="Authentication Token")
    projectName: str = Field(..., display_name="Project Name")
    projectId: str = Field(..., display_name="Project ID")
    projectPhase: str = Field(..., display_name="Project Phase")
    reportingYear: str = Field(..., display_name="Reporting Year")
    estimatedOccupancyYear: str = Field(..., display_name="Occupancy Year")
    country: str = Field(..., display_name="Country")
    state: str = Field(..., display_name="State")
    zipcode: str = Field(..., display_name="Zip Code")
    city: str = Field(..., display_name="City")
    climateZone: str = Field(..., display_name="Climate Zone")
    useType1: str = Field(..., display_name="Use Type")
    useType1Area: float = Field(..., display_name="Use Type Area")
    designEnergyCode: str = Field(..., display_name="Design Energy Code")
    baselineEUI: float = Field(..., display_name="Baseline EUI")
    predictedEUI: float = Field(..., display_name="Predicted EUI")
    energyModelingTool: str = Field(..., display_name="Energy Modeling Tool")
    districtChilledWater: float = Field(..., display_name="District Chilled Water")
    districtHotWater: float = Field(..., display_name="District Hot Water")
    districtSteam: float = Field(..., display_name="District Steam")
    naturalGasCombustedOnSite: float = Field(..., display_name="Natural Gas Combusted On-Site")
    electricityProducedOffSite: float = Field(..., display_name="Electricity Produced Off-Site")
    diesel: float = Field(..., display_name="Diesel")
    electricityFromRenewablesOnSite: float = Field(..., display_name="Electricity from Renewables On-Site")

