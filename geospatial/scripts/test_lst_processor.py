import os
import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from geospatial.src.earth_engine import initialize_earth_engine
from geospatial.src.lst_processor import get_lst_composite, compute_statistics
from geospatial.Config.study_areas import DEFAULT_DATE_RANGE

def main():
    try:
        initialize_earth_engine()
    except Exception as e:
        print(f"Failed to initialize Earth Engine: {e}")
        sys.exit(1)
        
    output_dir = PROJECT_ROOT / "geospatial" / "outputs" / "lst"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for city in ["mumbai", "dhanbad"]:
        print(f"\nProcessing LST for {city}...")
        
        try:
            composite, scene_count = get_lst_composite(city)
            print(f"Input scenes (L8+L9): {scene_count}")
            
            if scene_count == 0:
                print(f"No Landsat scenes found for {city}.")
                sys.exit(1)
                
            stats = compute_statistics(composite, city)
            
            valid_pixels = stats.get("valid_pixel_count")
            
            print(f"Images after masking: (median composite contains {valid_pixels} valid pixels)")
            print(f"Valid pixel count: {valid_pixels}")
            print(f"Min LST (C): {stats.get('min_c')}")
            print(f"Max LST (C): {stats.get('max_c')}")
            print(f"Mean LST (C): {stats.get('mean_c')}")
            print(f"Median LST (C): {stats.get('median_c')}")
            
            if not valid_pixels or valid_pixels == 0:
                print(f"Resulting image has no valid pixels for {city}.")
                sys.exit(1)
                
            if stats.get('min_c') is None:
                print(f"Statistics could not be calculated correctly for {city}.")
                sys.exit(1)
                
            result = {
                "area_id": city,
                "data_type": "land_surface_temperature",
                "period": {
                    "start": DEFAULT_DATE_RANGE["start"],
                    "end": DEFAULT_DATE_RANGE["end"]
                },
                "source": "Landsat 8/9 Collection 2 Level 2",
                "band": "ST_B10",
                "unit": "celsius",
                "resolution_m": 30,
                "composite": "median",
                "statistics": {
                    "min_c": stats.get('min_c'),
                    "max_c": stats.get('max_c'),
                    "mean_c": stats.get('mean_c'),
                    "median_c": stats.get('median_c')
                },
                "valid_pixel_count": valid_pixels,
                "status": "success",
                "limitations": [
                    "Represents Land Surface Temperature, not near-surface air temperature.",
                    "Does not directly represent human thermal comfort or heat-health risk.",
                    "Cloud, shadow, snow and fill pixels are masked.",
                    "Null/masked pixels represent unavailable valid observations."
                ]
            }
            
            output_file = output_dir / f"{city}_lst_validation.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
                
            print(f"Saved {output_file}")
            
        except Exception as e:
            print(f"Error processing {city}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
