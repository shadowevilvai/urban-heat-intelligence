import os
import json
import sys
from pathlib import Path
import ee

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.src.earth_engine import initialize_earth_engine
from geospatial.src.lst_processor import get_lst_composite
from geospatial.src.landsat import get_aoi
from geospatial.Config.study_areas import DEFAULT_DATE_RANGE

def export_spatial_lst(city_key, scale=450):
    """
    Exports a coarse sample of the LST composite as GeoJSON points.
    
    Explanation on Points vs Polygons:
    While a polygon grid is sometimes preferred for continuous surfaces to
    indicate spatial coverage explicitly, generating thousands of polygon
    geometries adds significant overhead to the GeoJSON size for a web prototype.
    Point sampling using `ee.Image.sample()` perfectly extracts the aggregated 
    temperature at the center of the downsampled grid cells (e.g., 300m) while 
    keeping the payload extremely lightweight and fast to parse on the frontend.
    """
    composite, _ = get_lst_composite(city_key)
    aoi = get_aoi(city_key)
    
    # Sample the image at a coarser scale (e.g., 300m) to reduce output size.
    # dropNulls is true by default, so masked pixels are automatically excluded.
    samples = composite.sample(
        region=aoi,
        scale=scale,
        projection='EPSG:4326',
        geometries=True,
        dropNulls=True
    )
    
    # Extract features from Earth Engine
    features_ee = samples.getInfo().get('features', [])
    
    geojson_features = []
    lst_values = []
    
    for feat in features_ee:
        coords = feat['geometry']['coordinates']
        lst = feat['properties'].get('LST_Celsius')
        
        import datetime
        
        if lst is not None:
            lst_values.append(lst)
            feature_id = f"{city_key}_{scale}m_{round(coords[0], 5)}_{round(coords[1], 5)}"
            geojson_features.append({
                "type": "Feature",
                "id": feature_id,
                "geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "properties": {
                    "schema_version": "1.0",
                    "feature_id": feature_id,
                    "city": city_key,
                    "lst_c": round(lst, 2),
                    "lst_anomaly_c": None,
                    "source": "Landsat Collection 2 Level 2",
                    "satellite": "Landsat 8/9",
                    "date_period_start": DEFAULT_DATE_RANGE["start"],
                    "date_period_end": DEFAULT_DATE_RANGE["end"],
                    "processing_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "resolution_m_source": 30,
                    "resolution_m_sample": scale,
                    "coordinate_reference_system": "EPSG:4326",
                    "data_quality": "validated",
                    "valid_pixel_percent": None,
                    "ndvi_mean": None,
                    "ndbi_mean": None,
                    "ndwi_mean": None,
                    "land_cover_class": None
                }
            })
            
    # Calculate stats
    feature_count = len(geojson_features)
    if feature_count > 0:
        min_c = min(lst_values)
        max_c = max(lst_values)
        mean_c = sum(lst_values) / feature_count
    else:
        min_c = max_c = mean_c = None
        
    geojson = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    
    validation_stats = {
        "city": city_key,
        "feature_count": feature_count,
        "min_lst_c": round(min_c, 2) if min_c is not None else None,
        "max_lst_c": round(max_c, 2) if max_c is not None else None,
        "mean_lst_c": round(mean_c, 2) if mean_c is not None else None,
        "source": "Landsat 8/9 Collection 2 Level 2",
        "resolution_m": scale,
        "period": DEFAULT_DATE_RANGE
    }
    
    return geojson, validation_stats

def main():
    try:
        initialize_earth_engine()
    except Exception as e:
        print(f"Failed to initialize Earth Engine: {e}")
        sys.exit(1)
        
    output_dir = PROJECT_ROOT / "geospatial" / "outputs" / "lst"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 450 meters is an appropriate coarse visualization resolution to keep
    # the feature count < 5,000 for manageable GeoJSON outputs and to avoid
    # Earth Engine's getInfo() limits.
    scale = 450 
    
    for city in ["mumbai", "dhanbad"]:
        print(f"\nExporting spatial LST for {city} at {scale}m scale...")
        try:
            geojson, stats = export_spatial_lst(city, scale=scale)
            
            if stats['feature_count'] == 0:
                print(f"Warning: No features exported for {city}. Check AOI and mask.")
                
            # Save GeoJSON
            geojson_path = output_dir / f"{city}_lst_spatial.geojson"
            with open(geojson_path, 'w') as f:
                json.dump(geojson, f)
            print(f"Saved {geojson_path}")
            
            # Save Validation stats
            val_path = output_dir / f"{city}_lst_spatial_validation.json"
            with open(val_path, 'w') as f:
                json.dump(stats, f, indent=2)
            print(f"Saved {val_path}")
            
            print("Validation Results:")
            print(f"  Feature Count: {stats['feature_count']}")
            print(f"  Min LST (C): {stats['min_lst_c']}")
            print(f"  Max LST (C): {stats['max_lst_c']}")
            print(f"  Mean LST (C): {stats['mean_lst_c']}")
            
        except Exception as e:
            print(f"Error processing {city}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
