import pytest
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_handler import process_hotspot_feature

def test_p1_integration_payload():
    payload_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures/p1/example_payload.json'))
    
    if not os.path.exists(payload_path):
        pytest.skip(f"Integration payload not found at {payload_path}")
        
    with open(payload_path, 'r') as f:
        payload = json.load(f)
        
    # Assert it is a FeatureCollection
    assert payload.get("type") == "FeatureCollection"
    assert "features" in payload
    assert len(payload["features"]) > 0
    
    # Obtain the Feature from payload["features"][0]
    p1_feature = payload["features"][0]
    
    # Process the feature
    result = process_hotspot_feature(p1_feature)
    
    # Assertions
    assert result["feature_id"] == p1_feature["properties"]["feature_id"]
    
    # Assert canonical feature_id
    assert result["feature_id"] == "mumbai_450m_72.84_19.01"
    
    # Location was preserved
    assert "p1_location" in result
    assert result["p1_location"]["city"] == p1_feature["properties"]["city"]
    assert result["p1_location"]["geometry"]["type"] == p1_feature["geometry"]["type"]
    assert result["p1_location"]["geometry"]["coordinates"] == p1_feature["geometry"]["coordinates"]
    
    # P1 properties preserved
    assert result["p1_measurements"]["lst_c"] == p1_feature["properties"]["lst_c"]
    assert result["p1_measurements"]["lst_anomaly_c"] is None 
    
    # P2 analysis generated correctly
    assert "p2_analysis" in result
    assert "risk_score" in result["p2_analysis"]
    assert "risk_category" in result["p2_analysis"]
    assert len(result["p2_analysis"]["contributors"]) > 0
