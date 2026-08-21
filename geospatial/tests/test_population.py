import os
import pytest
import rasterio
import json
from geospatial.scripts.population_loader import PopulationLoader

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "population")

def test_population_rasters_exist():
    mumbai_path = os.path.join(BASE_DIR, "mumbai_population_2023.tif")
    dhanbad_path = os.path.join(BASE_DIR, "dhanbad_population_2023.tif")
    assert os.path.exists(mumbai_path), "Mumbai raster missing"
    assert os.path.exists(dhanbad_path), "Dhanbad raster missing"

def test_raster_properties():
    mumbai_path = os.path.join(BASE_DIR, "mumbai_population_2023.tif")
    with rasterio.open(mumbai_path) as src:
        assert src.crs.to_string() == "EPSG:4326"
        # 3 arc seconds is approx 0.0008333 degrees
        assert abs(src.res[0] - 0.0008333) < 0.0001
        
        # Check values are numeric and non-negative
        data = src.read(1)
        valid_data = data[data >= 0]
        assert len(valid_data) > 0, "No valid data found"
        assert valid_data.min() >= 0, "Negative population found"

def test_metadata_exists():
    meta_path = os.path.join(BASE_DIR, "metadata.json")
    assert os.path.exists(meta_path)
    with open(meta_path, 'r') as f:
        meta = json.load(f)
        assert meta["year"] == 2023
        assert "WorldPop" in meta["source"]

def test_population_loader():
    loader = PopulationLoader(base_dir=BASE_DIR)
    
    # Test a point roughly in Mumbai center
    geom_mumbai = {
        "type": "Point",
        "coordinates": [72.85, 19.05]
    }
    
    pop_mumbai = loader.get_population_for_feature("mumbai", geom_mumbai)
    assert pop_mumbai >= 0
    assert type(pop_mumbai) is float

    loader.close()
