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
        
    # Process the feature
    result = process_hotspot_feature(payload)
    
    # Assertions
    assert result["feature_id"] == payload["properties"]["feature_id"]
    
    # Location was preserved
    assert "p1_location" in result
    assert result["p1_location"]["city"] == payload["properties"]["city"]
    assert result["p1_location"]["geometry"]["type"] == payload["geometry"]["type"]
    assert result["p1_location"]["geometry"]["coordinates"] == payload["geometry"]["coordinates"]
    
    # P1 properties preserved
    assert result["p1_measurements"]["lst_c"] == payload["properties"]["lst_c"]
    assert result["p1_measurements"]["lst_anomaly_c"] is None # Assuming the payload has null anomaly
    
    # P2 analysis generated correctly
    assert "p2_analysis" in result
    assert "risk_score" in result["p2_analysis"]
    assert "risk_category" in result["p2_analysis"]
    assert len(result["p2_analysis"]["contributors"]) > 0
