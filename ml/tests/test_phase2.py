import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.risk_engine import calculate_risk, get_risk_category

def test_get_risk_category():
    assert get_risk_category(85.0) == "extreme"
    assert get_risk_category(70.0) == "high"
    assert get_risk_category(50.0) == "moderate"
    assert get_risk_category(20.0) == "low"
    assert get_risk_category(80.0) == "extreme"

def test_calculate_risk_complete():
    # Simulate completely populated normalized features
    features = {
        "norm_lst_c": 0.5,
        "norm_lst_anomaly": 0.8,
        "norm_inv_ndvi": 0.2,
        "norm_ndbi": 0.9,
        "norm_inv_ndwi": 0.5
    }
    
    result = calculate_risk(features)
    
    assert "risk_score" in result
    assert "vulnerability_score" in result
    assert result["vulnerability_score"] is not None
    assert "contributors" in result
    
    # Exposure Score = 0.5*0.4 + 0.8*0.6 = 0.2 + 0.48 = 0.68
    # Vuln Score = 0.2*0.4 + 0.9*0.4 + 0.5*0.2 = 0.08 + 0.36 + 0.10 = 0.54
    # Risk Score = (0.68*0.5 + 0.54*0.5) * 100 = (0.34 + 0.27) * 100 = 61.0
    
    assert abs(result["risk_score"] - 61.0) < 1e-4
    assert abs(result["vulnerability_score"] - 54.0) < 1e-4
    assert result["risk_category"] == "high"
    
    # Check contributors sum to 1.0 importance
    total_importance = sum(c["importance"] for c in result["contributors"])
    assert abs(total_importance - 1.0) < 1e-4
    
    # Ensure sorted by importance
    importances = [c["importance"] for c in result["contributors"]]
    assert importances == sorted(importances, reverse=True)

def test_calculate_risk_missing_vuln_features():
    # Simulate missing NDVI and NDWI
    features = {
        "norm_lst_c": 0.5,
        "norm_lst_anomaly": 0.8,
        "norm_ndbi": 0.9
        # norm_inv_ndvi and norm_inv_ndwi missing
    }
    
    result = calculate_risk(features)
    
    # Exposure Score = 0.68
    # Vuln Score (only NDBI available, so weight is 1.0) = 0.9 * 1.0 = 0.9
    # Risk Score = (0.68*0.5 + 0.9*0.5) * 100 = (0.34 + 0.45) * 100 = 79.0
    
    assert abs(result["risk_score"] - 79.0) < 1e-4
    assert abs(result["vulnerability_score"] - 90.0) < 1e-4
    assert result["risk_category"] == "high"

def test_calculate_risk_no_vuln_data():
    # Only exposure data
    features = {
        "norm_lst_c": 0.5,
        "norm_lst_anomaly": 0.8
    }
    
    result = calculate_risk(features)
    
    # Exposure Score = 0.68
    # Vuln Score = None
    # Risk Score = 0.68 * 100 = 68.0
    
    assert abs(result["risk_score"] - 68.0) < 1e-4
    assert result["vulnerability_score"] is None
    
    # Contributors should only be 2, summing to 1.0
    assert len(result["contributors"]) == 2
    total_importance = sum(c["importance"] for c in result["contributors"])
    assert abs(total_importance - 1.0) < 1e-4

def test_calculate_risk_null_anomaly():
    # Simulate missing anomaly
    features = {
        "norm_lst_c": 0.5,
        # norm_lst_anomaly missing
        "norm_inv_ndvi": 0.2,
        "norm_ndbi": 0.9,
        "norm_inv_ndwi": 0.5
    }
    
    result = calculate_risk(features)
    
    # Exposure Score (only LST available, so weight is 1.0) = 0.5 * 1.0 = 0.5
    # Vuln Score = 0.54
    # Risk Score = (0.5 * 0.5 + 0.54 * 0.5) * 100 = (0.25 + 0.27) * 100 = 52.0
    
    assert abs(result["risk_score"] - 52.0) < 1e-4
    assert abs(result["vulnerability_score"] - 54.0) < 1e-4
    assert result["risk_category"] == "moderate"
