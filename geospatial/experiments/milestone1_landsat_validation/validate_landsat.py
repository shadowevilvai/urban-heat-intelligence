import ee
import json
import sys
import os

def check_auth():
    """Check Earth Engine authentication and initialize."""
    try:
        project = os.environ.get('EE_PROJECT')
        if project:
            ee.Initialize(project=project)
        else:
            ee.Initialize()
        return True
    except Exception as e:
        print(f"Earth Engine authentication failed or not configured: {e}", file=sys.stderr)
        print("Please authenticate by running the following command in your terminal:", file=sys.stderr)
        print("    earthengine authenticate", file=sys.stderr)
        print("If your organization requires a specific Cloud Project, set the EE_PROJECT environment variable.", file=sys.stderr)
        return False

# Temporary Configurable Parameters (Require Team Confirmation)
# AOI: Temporary test AOI (Small part of Mumbai based on API_CONTRACT.md bounding box)
AOI_COORDS = [
    [72.80, 18.95],
    [72.95, 18.95],
    [72.95, 19.20],
    [72.80, 19.20],
    [72.80, 18.95]
]
TEMPORARY_START_DATE = '2023-03-01'
TEMPORARY_END_DATE = '2023-05-31'

# Dataset IDs as documented
L8_COLLECTION = 'LANDSAT/LC08/C02/T1_L2'
L9_COLLECTION = 'LANDSAT/LC09/C02/T1_L2'

def validate_landsat():
    print("Initializing Earth Engine...")
    if not check_auth():
        # Generate a warning validation result since we can't connect
        write_result("fail", 0, 0, 0, 0, [], ["Earth Engine authentication required. Run `earthengine authenticate`."])
        sys.exit(1)
        
    print("Earth Engine initialized. Querying datasets...")
    aoi = ee.Geometry.Polygon([AOI_COORDS])
    
    # Filter collections
    l8 = ee.ImageCollection(L8_COLLECTION).filterBounds(aoi).filterDate(TEMPORARY_START_DATE, TEMPORARY_END_DATE)
    l9 = ee.ImageCollection(L9_COLLECTION).filterBounds(aoi).filterDate(TEMPORARY_START_DATE, TEMPORARY_END_DATE)
    
    # Merge collections
    merged = l8.merge(l9)
    
    # Fetch counts
    try:
        l8_count = l8.size().getInfo()
        l9_count = l9.size().getInfo()
        total_count = merged.size().getInfo()
    except Exception as e:
        print(f"Error fetching data from Earth Engine: {e}", file=sys.stderr)
        write_result("fail", 0, 0, 0, 0, [], [f"Earth Engine query error: {e}"])
        sys.exit(1)
        
    print(f"Found {total_count} total scenes (L8: {l8_count}, L9: {l9_count}).")
    
    # Get metadata for up to 100 scenes to check acquisition dates and cloud cover
    scenes = merged.limit(100).getInfo().get('features', [])
    
    acquisition_dates = []
    usable_count = 0
    
    for scene in scenes:
        props = scene.get('properties', {})
        date = props.get('DATE_ACQUIRED')
        if date:
            acquisition_dates.append(date)
            
        cloud_cover = props.get('CLOUD_COVER', 100)
        # Temporary simplistic usable check: < 20% cloud cover
        if cloud_cover < 20:
            usable_count += 1
            
    status = "pass" if usable_count > 0 else "warning"
    if total_count == 0:
        status = "fail"
        
    write_result(status, total_count, l8_count, l9_count, usable_count, sorted(list(set(acquisition_dates))), [
        "Dataset IDs verified against Earth Engine catalog.",
        "AOI is a temporary test polygon (needs team confirmation).",
        "Time period is temporary (needs team confirmation).",
        "Usability defined as CLOUD_COVER < 20% for demonstration purposes."
    ])
    
def write_result(status, total_count, l8_count, l9_count, usable_count, acquisition_dates, notes):
    result = {
        "status": status,
        "dataset": f"{L8_COLLECTION}, {L9_COLLECTION}",
        "aoi": "Temporary Test AOI (Mumbai bounding box subset)",
        "start_date": TEMPORARY_START_DATE,
        "end_date": TEMPORARY_END_DATE,
        "scene_count": total_count,
        "landsat8_scene_count": l8_count,
        "landsat9_scene_count": l9_count,
        "usable_scene_count": usable_count,
        "cloud_filter": "< 20% (Temporary criteria for evaluation)",
        "acquisition_dates": acquisition_dates,
        "notes": notes
    }
    
    output_path = os.path.join(os.path.dirname(__file__), 'validation_result.json')
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
        
    print(f"Validation complete. Result saved to {output_path}")

if __name__ == "__main__":
    validate_landsat()
