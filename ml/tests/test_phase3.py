import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mock_data import MOCK_HOTSPOT_GEOJSON
from api_handler import process_hotspot_feature, MODEL_VERSION
from schemas import HotspotFeatureCollection
from pydantic import ValidationError

def test_process_hotspot_feature_complete():
    raw_feature = MOCK_HOTSPOT_GEOJSON["features"][0]
    result = process_hotspot_feature(raw_feature)
    
    # Check exact API_CONTRACT.md format
    assert result["id"] == "MUM-HS-001"
    assert result["lst_celsius"] == 42.6
    assert result["lst_min_c"] == 40.1
    assert result["lst_max_c"] == 45.2
    assert result["lst_anomaly_c"] == 4.2
    assert result["ndvi_mean"] == 0.18
    assert result["ndbi_mean"] == 0.52
    assert result["ndwi_mean"] == 0.06
    assert result["land_cover_class"] == "built_up"
    assert isinstance(result["risk_score"], float)
    assert result["risk_score"] >= 0.0 and result["risk_score"] <= 100.0
    assert result["risk_category"] in ["low", "moderate", "high", "extreme"]
    assert isinstance(result["vulnerability_score"], float)
    assert isinstance(result["contributors"], list)
    assert len(result["contributors"]) > 0
    assert result["data_date"] == "2026-05-15"
    assert result["model_version"] == MODEL_VERSION
    assert result["status"] == "predicted"
    
    # Check contributors format
    c = result["contributors"][0]
    assert "name" in c
    assert "value" in c
    assert "importance" in c

def test_process_hotspot_feature_missing_optionals():
    raw_feature = MOCK_HOTSPOT_GEOJSON["features"][1]
    result = process_hotspot_feature(raw_feature)
    
    assert result["id"] == "MUM-HS-002"
    assert result["ndvi_mean"] is None
    assert result["ndbi_mean"] is None
    assert result["ndwi_mean"] is None
    assert result["land_cover_class"] is None
    assert result["vulnerability_score"] is None
    assert isinstance(result["risk_score"], float)

def test_invalid_input_raises_validation_error():
    invalid_feature = MOCK_HOTSPOT_GEOJSON["features"][0].copy()
    invalid_feature["properties"] = invalid_feature["properties"].copy()
    invalid_feature["properties"]["cloud_cover_percent"] = 500.0 # invalid percentage
    
    with pytest.raises(ValidationError):
        process_hotspot_feature(invalid_feature)
