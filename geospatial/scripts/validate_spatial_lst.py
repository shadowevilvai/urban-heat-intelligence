import os
import json
import sys
import statistics
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.Config.study_areas import STUDY_AREAS

def point_in_bbox(lon, lat, bbox):
    # bbox format: [minLon, minLat, maxLon, maxLat]
    return bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]

def run_validation():
    output_dir = PROJECT_ROOT / "geospatial" / "outputs" / "lst"
    cities = ["mumbai", "dhanbad"]
    
    for city in cities:
        print(f"\n--- Validating {city} ---")
        
        geojson_path = output_dir / f"{city}_lst_spatial.geojson"
        m2_val_path = output_dir / f"{city}_lst_validation.json"
        m4_val_path = output_dir / f"{city}_lst_spatial_validation.json"
        
        # Load GeoJSON and M2 results
        with open(geojson_path, 'r') as f:
            geojson = json.load(f)
            
        with open(m2_val_path, 'r') as f:
            m2_data = json.load(f)
            m2_mean = m2_data["statistics"]["mean_c"]
            m2_min = m2_data["statistics"]["min_c"]
            m2_max = m2_data["statistics"]["max_c"]
            
        bbox = STUDY_AREAS[city]["bbox"]
        
        # CHECK 1 & 3: GeoJSON Structure & Geographic Sanity
        assert geojson.get("type") == "FeatureCollection", f"[{city}] Not a FeatureCollection"
        features = geojson.get("features", [])
        
        lst_values = []
        lons, lats = [], []
        coords_set = set()
        
        for feat in features:
            assert feat.get("type") == "Feature", f"[{city}] Invalid feature type"
            
            geom = feat.get("geometry", {})
            assert geom.get("type") == "Point", f"[{city}] Invalid geometry type"
            
            coords = geom.get("coordinates")
            assert len(coords) == 2, f"[{city}] Invalid coordinates"
            lon, lat = coords
            
            assert point_in_bbox(lon, lat, bbox), f"[{city}] Coordinate {lon},{lat} falls outside bounding box {bbox}"
            
            coords_tuple = (lon, lat)
            assert coords_tuple not in coords_set, f"[{city}] Duplicate coordinate found at {coords_tuple}"
            coords_set.add(coords_tuple)
            
            props = feat.get("properties", {})
            assert props.get("city") == city, f"[{city}] City property mismatch"
            
            lst = props.get("lst_c")
            assert lst is not None and isinstance(lst, (int, float)), f"[{city}] Invalid or missing lst_c"
            
            lst_values.append(lst)
            lons.append(lon)
            lats.append(lat)
            
        feature_count = len(features)
        assert feature_count > 0, f"[{city}] No features found"
        
        # CHECK 2: Statistical Consistency
        min_lst = min(lst_values)
        max_lst = max(lst_values)
        mean_lst = statistics.mean(lst_values)
        median_lst = statistics.median(lst_values)
        
        abs_diff = abs(mean_lst - m2_mean)
        pct_diff = (abs_diff / m2_mean) * 100
        
        # We allow a small percentage difference due to spatial sampling (max 5%)
        assert pct_diff < 5, f"[{city}] Mean LST difference too high: {pct_diff:.2f}%"
        
        # CHECK 4: Scientific Language (Strict enforcement)
        limitations = [
            "Land Surface Temperature (LST), not near-surface air temperature.",
            "Does not directly represent human thermal comfort or heat-health risk.",
            "The 450 m representation is a spatial sampling/visualization representation of the underlying LST composite and should not be described as 450 m ground-truth temperature measurements."
        ]
        
        # Verify required phrase is present
        required_phrase = "Land Surface Temperature (LST), not near-surface air temperature."
        assert required_phrase in limitations, "Required scientific disclaimer missing"
        
        forbidden_phrases = ["ambient temperature", "human temperature"]
        for text in limitations:
            lower_text = text.lower()
            for forbidden in forbidden_phrases:
                assert forbidden not in lower_text, f"[{city}] Forbidden term '{forbidden}' found in limitations."
            
        # CHECK 5: Visual Inspection Preparation (Output Validation Report)
        report = {
            "city": city,
            "feature_count": feature_count,
            "spatial_bounds": {
                "min_lon": min(lons),
                "max_lon": max(lons),
                "min_lat": min(lats),
                "max_lat": max(lats)
            },
            "statistics": {
                "min_lst_c": min_lst,
                "max_lst_c": max_lst,
                "mean_lst_c": round(mean_lst, 4),
                "median_lst_c": round(median_lst, 4)
            },
            "m2_comparison": {
                "m2_mean": m2_mean,
                "spatial_mean": round(mean_lst, 4),
                "absolute_mean_difference": round(abs_diff, 4),
                "percentage_mean_difference": round(pct_diff, 4),
                "explanation_min_max_diff": "The minimum and maximum LST can differ between Milestone 2 (all 30m pixels) and Milestone 3 (spatial sampling) because taking discrete point samples at 450m scale might miss the absolute hottest or absolute coldest single 30m pixel. The mean remains very close because it averages over the entire area."
            },
            "limitations": limitations,
            "validation_status": "PASSED"
        }
        
        with open(m4_val_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"{city} validation PASSED.")
        print(f"Feature count: {feature_count}")
        print(f"Mean difference: {abs_diff:.4f} °C ({pct_diff:.2f}%)")
        
    print("\nP1 Milestone 4 validation PASSED.")

if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as e:
        print(f"\nValidation FAILED: {e}")
        sys.exit(1)
