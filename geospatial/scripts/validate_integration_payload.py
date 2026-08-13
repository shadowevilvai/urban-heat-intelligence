import json
import sys
from pathlib import Path

REQUIRED_PROPERTIES = {
    "schema_version": str,
    "feature_id": str,
    "city": str,
    "lst_c": (int, float),
    "lst_anomaly_c": (int, float, type(None)),
    "source": str,
    "satellite": str,
    "date_period_start": str,
    "date_period_end": str,
    "processing_date": str,
    "resolution_m_source": int,
    "resolution_m_sample": int,
    "coordinate_reference_system": str,
    "data_quality": str
}

OPTIONAL_PROPERTIES = {
    "valid_pixel_percent": (int, float, type(None)),
    "ndvi_mean": (int, float, type(None)),
    "ndbi_mean": (int, float, type(None)),
    "ndwi_mean": (int, float, type(None)),
    "land_cover_class": (str, type(None))
}

FORBIDDEN_PROPERTIES = ["hotspot_id", "hotspot_score", "confidence", "health_risk", "vulnerability"]

def validate_payload(filepath):
    print(f"\n--- Validating {filepath.name} ---")
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    assert data.get("type") == "FeatureCollection", "Not a FeatureCollection"
    features = data.get("features", [])
    
    for feat in features:
        assert feat.get("type") == "Feature", "Invalid Feature type"
        
        # Geometry checks
        geom = feat.get("geometry", {})
        assert geom.get("type") == "Point", "Geometry must be Point"
        coords = geom.get("coordinates", [])
        assert len(coords) == 2, "Coordinates must have exactly 2 elements"
        assert isinstance(coords[0], (int, float)) and isinstance(coords[1], (int, float)), "Coordinates must be numeric"
        
        # Properties checks
        props = feat.get("properties", {})
        
        # Check required
        for key, expected_type in REQUIRED_PROPERTIES.items():
            assert key in props, f"Missing required property: {key}"
            val = props[key]
            if val is not None:
                assert isinstance(val, expected_type), f"Property '{key}' has incorrect type. Expected {expected_type}, got {type(val)}"
            else:
                assert type(None) in (expected_type if isinstance(expected_type, tuple) else (expected_type,)), f"Property '{key}' cannot be null"
                
        # Value-specific checks
        assert props["schema_version"] == "1.0", "Invalid schema_version"
        assert props["coordinate_reference_system"] == "EPSG:4326", "Invalid CRS"
        assert props["feature_id"] == feat.get("id"), "Deterministic feature_id must match Feature root id"
        
        # Check optional
        for key, expected_type in OPTIONAL_PROPERTIES.items():
            if key in props:
                val = props[key]
                if val is not None:
                    assert isinstance(val, expected_type), f"Property '{key}' has incorrect type"
                    if key == "valid_pixel_percent":
                        assert 0 <= val <= 100, "valid_pixel_percent must be [0, 100]"
        
        # Check forbidden
        for key in FORBIDDEN_PROPERTIES:
            assert key not in props, f"Forbidden property found: '{key}'. P2 owns this field or it is scientifically invalid."
            
    print(f"Validation PASSED for {filepath.name}.")
    return True

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    
    payload1 = PROJECT_ROOT / "geospatial" / "outputs" / "integration" / "example_payload.json"
    payload2 = PROJECT_ROOT / "geospatial" / "outputs" / "integration" / "example_payload_missing_optional.json"
    
    try:
        validate_payload(payload1)
        validate_payload(payload2)
        print("\nAll integration payload validations PASSED.")
    except AssertionError as e:
        print(f"Validation FAILED: {e}")
        sys.exit(1)
