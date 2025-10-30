from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_wake_up():
    # wake-up endpoint always returns success regardless of auth status
    response = client.get("/wake-up/")
    assert response.status_code == 200
    assert response.json() == "success"

def test_submit_project():
    # Provide valid data structure to bypass validation and test auth
    valid_data = {
        "project_use_type_id": 1,
        "project_phase_id": 2,
        "project_construction_category_id": 3,
        "project_id": "550e8400-e29b-41d4-a716-446655440010",  # Valid UUID format
        "baseline_eeu_id": None,
        "design_eeu_id": None,
        "energy_code_id": None,
        "use_type_subtype_id": None,
        "year": 2024,
        "reporting_year": 2024
    }
    response = client.post("/submit_project/", json=valid_data)
    assert response.status_code == 200
    assert response.json() == "not authorized"

def test_create_company():
    # Provide valid data structure to bypass validation and test auth
    valid_data = {"company_name": "Test Company"}
    response = client.post("/create_company/", json=valid_data)
    assert response.status_code == 200
    assert response.json() == "not authorized"
