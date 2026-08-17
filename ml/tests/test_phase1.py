import pytest
from pydantic import ValidationError
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schemas import P1Feature, P1FeatureCollection, P1FeatureProperties
from test_fixtures import MOCK_HOTSPOT_GEOJSON
from preprocessing import preprocess_features, clip_and_scale
from adapter import adapt_p1_to_p2

def test_clip_and_scale():
    assert clip_and_scale(30.0, 25.0, 55.0) == 5.0 / 30.0
    assert clip_and_scale(10.0, 25.0, 55.0) == 0.0
    assert clip_and_scale(60.0, 25.0, 55.0) == 1.0

def test_schema_valid_complete():
    collection = P1FeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    assert len(collection.features) == 6
    
    feature1 = collection.features[0]
    assert feature1.properties.feature_id == "mumbai_450m_1"
    assert feature1.properties.ndvi_mean == 0.18
    assert feature1.geometry.type == "Point"

def test_schema_valid_missing_optional():
    collection = P1FeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    feature6 = collection.features[5] # All optional unavailable
    assert feature6.properties.ndvi_mean is None
    assert feature6.properties.ndbi_mean is None
    assert feature6.properties.ndwi_mean is None
    assert feature6.properties.valid_pixel_percent is None

def test_schema_invalid_percentages():
    props = MOCK_HOTSPOT_GEOJSON["features"][0]["properties"].copy()
    props["valid_pixel_percent"] = 150.0 # invalid
    with pytest.raises(ValidationError):
        P1FeatureProperties(**props)

def test_preprocessing_complete():
    collection = P1FeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    props = collection.features[0].properties
    p2_props = adapt_p1_to_p2(props)
    norm = preprocess_features(p2_props)
    
    assert "norm_lst_c" in norm
    assert "norm_lst_anomaly" in norm
    assert "norm_inv_ndvi" in norm
    assert "norm_ndbi" in norm
    assert "norm_inv_ndwi" in norm
    
    # 0.18 -> clip(-1,1) = 0.18 -> scale(0,2)=1.18/2=0.59 -> inv = 1 - 0.59 = 0.41
    assert abs(norm["norm_inv_ndvi"] - 0.41) < 1e-5
    
    # 0.52 -> clip(-1,1) = 0.52 -> scale(0,2) = 1.52/2 = 0.76
    assert abs(norm["norm_ndbi"] - 0.76) < 1e-5

def test_preprocessing_missing_optional():
    collection = P1FeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    # feature index 5 has all optional missing
    props = collection.features[5].properties
    p2_props = adapt_p1_to_p2(props)
    norm = preprocess_features(p2_props)
    
    assert "norm_lst_c" in norm
    assert "norm_lst_anomaly" in norm
    
    assert "norm_inv_ndvi" not in norm
    assert "norm_ndbi" not in norm
    assert "norm_inv_ndwi" not in norm

def test_preprocessing_null_anomaly():
    collection = P1FeatureCollection(**MOCK_HOTSPOT_GEOJSON)
    # feature index 1 has null anomaly
    props = collection.features[1].properties
    p2_props = adapt_p1_to_p2(props)
    norm = preprocess_features(p2_props)
    
    assert "norm_lst_c" in norm
    assert "norm_lst_anomaly" not in norm
