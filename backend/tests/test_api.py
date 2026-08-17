import pytest
from fastapi.testclient import TestClient
import sys
import pathlib

root_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from backend.main import app
from backend.data_store import data_store
from ml.api_handler import process_hotspot_feature
from ml.optimization.schemas import ValueStatus

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def initialize_data_store():
    # Initialize the data store manually for testing since TestClient doesn't run startup events by default
    with TestClient(app):
        # Trigger lifespan
        pass
    data_store.initialize()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "mumbai" in data["loaded_cities"]
    assert "dhanbad" in data["loaded_cities"]
    assert data["dataset_loaded"] is True

def test_list_cities():
    response = client.get("/api/cities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    city_ids = [c["city_id"] for c in data]
    assert "mumbai" in city_ids
    assert "dhanbad" in city_ids
    
    # Real data counts check
    mumbai_city = next(c for c in data if c["city_id"] == "mumbai")
    dhanbad_city = next(c for c in data if c["city_id"] == "dhanbad")
    
    assert mumbai_city["feature_count"] == 2294
    assert dhanbad_city["feature_count"] == 2989

def test_city_map_mumbai():
    response = client.get("/api/cities/mumbai/map")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2294

    feature = data["features"][0]
    assert "feature_id" in feature["properties"]
    assert "lst_c" in feature["properties"]
    assert "risk_category" in feature["properties"]
    assert "hotspot_context" in feature["properties"]

def test_city_map_dhanbad():
    response = client.get("/api/cities/dhanbad/map")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2989

def test_invalid_city():
    response = client.get("/api/cities/invalid_city/map")
    assert response.status_code == 404

def test_hotspot_detail_and_p2_regression():
    # Fetch a detail
    # We will pick the first feature from Mumbai
    mumbai_map = client.get("/api/cities/mumbai/map").json()
    feature_id = mumbai_map["features"][0]["properties"]["feature_id"]
    
    response = client.get(f"/api/hotspots/mumbai/{feature_id}")
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "feature" in data
    assert "risk" in data
    
    feature = data["feature"]
    risk = data["risk"]
    
    # P1 Integrity Check
    props = feature["properties"]
    assert "lst_c" in props
    assert "ndvi_mean" in props
    assert "feature_id" in props
    assert "source" in props
    assert "valid_pixel_percent" in props
    
    # P2 Regression Check
    canonical_p2 = process_hotspot_feature(feature)
    
    assert risk["p2_analysis"]["risk_score"] == canonical_p2["p2_analysis"]["risk_score"]
    assert risk["p2_analysis"]["risk_category"] == canonical_p2["p2_analysis"]["risk_category"]
    assert risk["p2_analysis"]["vulnerability_score"] == canonical_p2["p2_analysis"]["vulnerability_score"]
    assert risk["p2_analysis"]["hotspot_context"] == canonical_p2["p2_analysis"]["hotspot_context"]
    assert risk["p2_analysis"]["model_version"] == canonical_p2["p2_analysis"]["model_version"]

def test_security_path_traversal():
    response = client.get("/api/hotspots/../../etc/passwd/123")
    assert response.status_code == 404
    
    response = client.get("/api/cities/../../etc/passwd/map")
    assert response.status_code == 404

def test_optimization():
    # Pick a few hotspots
    mumbai_map = client.get("/api/cities/mumbai/map").json()
    hotspot_ids = [f["properties"]["feature_id"] for f in mumbai_map["features"][:3]]
    
    request_data = {
        "city_id": "mumbai",
        "hotspot_ids": hotspot_ids,
        "resource_budget": 5.0,
        "interventions": ["COOL_ROOF", "TREE_CANOPY"]
    }
    
    response = client.post("/api/optimization/optimize", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Semantic verification
    assert "portfolio_objective_value" in data
    assert "total_expected_cooling_celsius" in data
    
    # Make sure we didn't silently rename or change semantics
    assert data["portfolio_objective_value"] != data["total_expected_cooling_celsius"]
    assert data["value_status"] == ValueStatus.RECOMMENDED.value
    
def test_optimization_limit():
    request_data = {
        "city_id": "mumbai",
        "hotspot_ids": ["test"] * 1001, # More than 1000
        "resource_budget": 5.0,
        "interventions": ["COOL_ROOF"]
    }
    
    response = client.post("/api/optimization/optimize", json=request_data)
    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "limit_exceeded"
