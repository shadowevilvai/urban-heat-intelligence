import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.tests.test_fixtures import MOCK_HOTSPOT_GEOJSON
from ml.api_handler import process_hotspot_feature, MODEL_VERSION
from ml.schemas import P1FeatureCollection
from pydantic import ValidationError

def test_process_hotspot_feature_complete():
    raw_feature = MOCK_HOTSPOT_GEOJSON["features"][0]
    result = process_hotspot_feature(raw_feature)
    
    assert result["feature_id"] == "mumbai_450m_1"
    assert "hotspot_id" in result
    assert result["hotspot_id"] == "HS-mumbai_450m_1"
    
    assert "p1_location" in result
    assert result["p1_location"]["city"] == "Mumbai"
    assert result["p1_location"]["geometry"]["type"] == "Point"
    
    assert "p1_measurements" in result
    m = result["p1_measurements"]
    assert m["lst_c"] == 50.0
    assert m["lst_anomaly_c"] == 8.0
    assert m["ndvi_mean"] == 0.18
    assert m["ndbi_mean"] == 0.52
    assert m["ndwi_mean"] == 0.06
    assert m["land_cover_class"] == "built_up"
    
    assert "p1_provenance" in result
    p = result["p1_provenance"]
    assert p["schema_version"] == "1.0"
    assert p["date_period_start"] == "2026-03-01"
    
    assert "p2_analysis" in result
    a = result["p2_analysis"]
    assert isinstance(a["risk_score"], float)
    assert a["risk_category"] in ["low", "moderate", "high", "extreme"]
    assert isinstance(a["vulnerability_score"], float)
    assert isinstance(a["contributors"], list)
    assert len(a["contributors"]) > 0
    assert a["model_version"] == MODEL_VERSION
    
    # Check contributors format
    c = a["contributors"][0]
    assert "name" in c
    assert "value" in c
    assert "importance" in c

def test_process_hotspot_feature_missing_optionals():
    raw_feature = MOCK_HOTSPOT_GEOJSON["features"][5] # All optional unavailable
    result = process_hotspot_feature(raw_feature)
    
    assert result["feature_id"] == "mumbai_450m_6"
    
    m = result["p1_measurements"]
    assert m["ndvi_mean"] is None
    assert m["ndbi_mean"] is None
    assert m["ndwi_mean"] is None
    assert m["land_cover_class"] is None
    
    a = result["p2_analysis"]
    assert a["vulnerability_score"] is None
    assert isinstance(a["risk_score"], float)
    
    # Since risk score is low/moderate for 38.0 LST and 1.0 anomaly (without vuln), it might not have hotspot_id
    if a["risk_category"] not in ["high", "extreme"]:
        assert "hotspot_id" not in result

def test_invalid_input_raises_validation_error():
    invalid_feature = MOCK_HOTSPOT_GEOJSON["features"][0].copy()
    invalid_feature["properties"] = invalid_feature["properties"].copy()
    invalid_feature["properties"]["valid_pixel_percent"] = 500.0 # invalid percentage
    
    with pytest.raises(ValidationError):
        process_hotspot_feature(invalid_feature)
