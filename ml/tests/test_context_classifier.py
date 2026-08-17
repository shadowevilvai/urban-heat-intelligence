import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from context_classifier import classify_context
from schemas import P1FeatureProperties

def create_mock_props(
    lst_c=30.0,
    lst_anomaly_c=0.0,
    ndvi_mean=0.5,
    ndbi_mean=-0.2,
    land_cover_class="Tree cover",
    city="mumbai"
):
    return P1FeatureProperties(
        schema_version="1.0",
        feature_id="test_id",
        city=city,
        lst_c=lst_c,
        lst_anomaly_c=lst_anomaly_c,
        ndvi_mean=ndvi_mean,
        ndbi_mean=ndbi_mean,
        land_cover_class=land_cover_class,
        source="test",
        satellite="test",
        date_period_start="2023-01-01",
        date_period_end="2023-12-31",
        processing_date="2024-01-01",
        resolution_m_source=30,
        resolution_m_sample=30,
        coordinate_reference_system="EPSG:4326",
        data_quality="good"
    )

def test_water_context():
    props = create_mock_props(land_cover_class="Permanent water bodies")
    assert classify_context(props) == "water"

def test_terrestrial_other_context():
    props = create_mock_props(
        land_cover_class="Tree cover",
        lst_c=30.0,
        lst_anomaly_c=0.0,
        ndbi_mean=-0.2
    )
    assert classify_context(props) == "terrestrial_other"

def test_urban_heat_candidate_context():
    # Built-up, NDBI > 0, anomalous heat
    props = create_mock_props(
        land_cover_class="Built-up",
        lst_c=41.0,
        lst_anomaly_c=1.5,
        ndbi_mean=0.1
    )
    assert classify_context(props) == "urban_heat"

    # Not 'Built-up' land cover but has strong built-up signature (ndbi > 0)
    props2 = create_mock_props(
        land_cover_class="Cropland",
        lst_c=41.0,
        lst_anomaly_c=1.5,
        ndbi_mean=0.1
    )
    assert classify_context(props2) == "terrestrial_other"

def test_industrial_mining_candidate_context():
    props = create_mock_props(
        land_cover_class="Bare / sparse vegetation",
        lst_c=46.0,
        lst_anomaly_c=4.5,
        ndbi_mean=0.1
    )
    assert classify_context(props) == "industrial_mining_candidate"

def test_city_independence():
    # Identical properties should yield identical context regardless of city
    props_mumbai = create_mock_props(
        city="mumbai",
        land_cover_class="Bare / sparse vegetation",
        lst_c=46.0,
        lst_anomaly_c=4.5,
        ndbi_mean=0.1
    )
    props_dhanbad = create_mock_props(
        city="dhanbad",
        land_cover_class="Bare / sparse vegetation",
        lst_c=46.0,
        lst_anomaly_c=4.5,
        ndbi_mean=0.1
    )
    assert classify_context(props_mumbai) == "industrial_mining_candidate"
    assert classify_context(props_dhanbad) == "industrial_mining_candidate"
