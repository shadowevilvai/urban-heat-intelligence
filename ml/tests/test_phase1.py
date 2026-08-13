import pytest
from pydantic import ValidationError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas import HotspotFeature, HotspotFeatureCollection, HotspotProperties
from mock_data import MOCK_HOTSPOT_GEOJSON
from preprocessing import preprocess_features, clip_and_scale

def test_clip_and_scale():
    assert clip_and_scale(30.0, 25.0, 55.0) == 5.0 / 30.0
    assert clip_and_scale(10.0, 25.0, 55.0) == 0.0
    assert clip_and_scale(60.0, 25.0, 55.0) == 1.0

def test_schema_valid_complete():
    # MOCK_HOTSPOT_GEOJSON has two features, the first is complete
    collection = HotspotFeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    assert len(collection.features) == 2
    
    feature1 = collection.features[0]
    assert feature1.properties.hotspot_id == "MUM-HS-001"
    assert feature1.properties.ndvi_mean == 0.18
    assert feature1.geometry.type == "Point"

def test_schema_valid_missing_optional():
    # The second feature has missing optional indicators
    collection = HotspotFeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    feature2 = collection.features[1]
    assert feature2.properties.ndvi_mean is None
    assert feature2.properties.ndbi_mean is None
    assert feature2.properties.ndwi_mean is None

def test_schema_invalid_percentages():
    props = MOCK_HOTSPOT_GEOJSON["features"][0]["properties"].copy()
    props["cloud_cover_percent"] = 150.0 # invalid
    with pytest.raises(ValidationError):
        HotspotProperties(**props)

def test_preprocessing_complete():
    collection = HotspotFeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    props = collection.features[0].properties
    norm = preprocess_features(props)
    
    assert "norm_lst_mean" in norm
    assert "norm_lst_anomaly" in norm
    assert "norm_inv_ndvi" in norm
    assert "norm_ndbi" in norm
    assert "norm_inv_ndwi" in norm
    
    # 0.18 -> clip(-1,1) = 0.18 -> scale(0,2)=1.18/2=0.59 -> inv = 1 - 0.59 = 0.41
    assert abs(norm["norm_inv_ndvi"] - 0.41) < 1e-5
    
    # 0.52 -> clip(-1,1) = 0.52 -> scale(0,2) = 1.52/2 = 0.76
    assert abs(norm["norm_ndbi"] - 0.76) < 1e-5

def test_preprocessing_missing_optional():
    collection = HotspotFeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    props = collection.features[1].properties
    norm = preprocess_features(props)
    
    assert "norm_lst_mean" in norm
    assert "norm_lst_anomaly" in norm
    
    assert "norm_inv_ndvi" not in norm
    assert "norm_ndbi" not in norm
    assert "norm_inv_ndwi" not in norm
