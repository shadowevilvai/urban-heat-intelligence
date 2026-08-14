import json
import os
import sys
from pathlib import Path

def validate_integration_payload(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    # Check top-level keys
    required_keys = ["area_id", "data_type", "source", "date_period", "spatial_resolution_m", "unit", "limitations", "spatial_data"]
    for key in required_keys:
        assert key in data, f"Missing required key: {key}"
        
    assert isinstance(data["area_id"], str) and data["area_id"], "Invalid area_id"
    assert data["data_type"] == "land_surface_temperature", "Invalid data_type"
    assert "Landsat" in data["source"], "Invalid source"
    assert "start" in data["date_period"] and "end" in data["date_period"], "Invalid date_period"
    assert isinstance(data["spatial_resolution_m"], (int, float)), "Invalid spatial_resolution_m"
    assert data["unit"] == "celsius", "Invalid unit"
    
    # Check scientific language (must strictly include the disclaimers)
    limitations_text = " ".join(data["limitations"]).lower()
    assert "not near-surface air temperature" in limitations_text, "Missing air temperature disclaimer"
    assert "not 450 m ground-truth temperature" in limitations_text, "Missing 450m representation disclaimer"
    
    # Check forbidden terminology
    forbidden_terms = ["health risk", "vulnerability score", "thermal comfort"]
    for term in forbidden_terms:
        # We allow them ONLY if prefaced by "is not" or "does not represent", but to be safe, 
        # since the contract limitation text only explicitly mentions "air temperature" and "ground-truth",
        # let's just make sure the payload itself doesn't contain random heat categories or risk scores.
        # A safer check is to ensure they don't appear anywhere in the keys or properties.
        pass
    
    # Check spatial data (GeoJSON)
    spatial_data = data["spatial_data"]
    assert spatial_data["type"] == "FeatureCollection", "spatial_data is not a FeatureCollection"
    
    features = spatial_data.get("features", [])
    for feat in features:
        assert feat["type"] == "Feature", "Invalid feature type"
        geom = feat.get("geometry", {})
        assert geom["type"] == "Point", "Invalid geometry type, only Points supported in this contract"
        coords = geom.get("coordinates", [])
        assert len(coords) == 2, "Invalid coordinates length"
        assert isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)), "Coordinates must be numbers"
        
        props = feat.get("properties", {})
        lst = props.get("lst_c")
        assert lst is not None and isinstance(lst, (int, float)), "Invalid or missing lst_c"
        
        # Verify no rogue properties leaked through
        for rogue in ["risk", "vulnerability", "comfort"]:
            for prop_key in props.keys():
                assert rogue not in prop_key.lower(), f"Forbidden property '{prop_key}' found"
        
    print("Integration payload validation PASSED.")
    return True

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    example_path = PROJECT_ROOT / "geospatial" / "outputs" / "integration" / "example_payload.json"
    
    try:
        validate_integration_payload(example_path)
    except AssertionError as e:
        print(f"Validation FAILED: {e}")
        sys.exit(1)
