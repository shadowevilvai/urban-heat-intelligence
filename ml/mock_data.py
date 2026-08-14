MOCK_HOTSPOT_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            # 1. Complete feature
            "type": "Feature",
            "id": "mumbai_450m_1",
            "properties": {
                "schema_version": "1.0",
                "feature_id": "mumbai_450m_1",
                "city": "Mumbai",
                "lst_c": 50.0,
                "lst_anomaly_c": 8.0,
                "ndvi_mean": 0.18,
                "ndbi_mean": 0.52,
                "ndwi_mean": 0.06,
                "land_cover_class": "built_up",
                "source": "Landsat Collection 2 Level 2",
                "satellite": "Landsat 9",
                "date_period_start": "2026-03-01",
                "date_period_end": "2026-05-31",
                "processing_date": "2026-08-13",
                "resolution_m_source": 30,
                "resolution_m_sample": 450,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "validated",
                "valid_pixel_percent": 99.5
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8777, 19.0760]
            }
        },
        {
            # 2. Null anomaly
            "type": "Feature",
            "id": "mumbai_450m_2",
            "properties": {
                "schema_version": "1.0",
                "feature_id": "mumbai_450m_2",
                "city": "Mumbai",
                "lst_c": 40.5,
                "lst_anomaly_c": None,
                "ndvi_mean": 0.15,
                "ndbi_mean": 0.40,
                "ndwi_mean": -0.10,
                "land_cover_class": "urban",
                "source": "Landsat Collection 2 Level 2",
                "satellite": "Landsat 9",
                "date_period_start": "2026-03-01",
                "date_period_end": "2026-05-31",
                "processing_date": "2026-08-13",
                "resolution_m_source": 30,
                "resolution_m_sample": 450,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "validated",
                "valid_pixel_percent": 100.0
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8500, 19.0500]
            }
        },
        {
            # 3. Missing NDVI
            "type": "Feature",
            "id": "mumbai_450m_3",
            "properties": {
                "schema_version": "1.0",
                "feature_id": "mumbai_450m_3",
                "city": "Mumbai",
                "lst_c": 39.0,
                "lst_anomaly_c": 2.0,
                "ndvi_mean": None,
                "ndbi_mean": 0.30,
                "ndwi_mean": 0.05,
                "land_cover_class": "mixed",
                "source": "Landsat Collection 2 Level 2",
                "satellite": "Landsat 9",
                "date_period_start": "2026-03-01",
                "date_period_end": "2026-05-31",
                "processing_date": "2026-08-13",
                "resolution_m_source": 30,
                "resolution_m_sample": 450,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "validated",
                "valid_pixel_percent": 90.0
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8400, 19.0400]
            }
        },
        {
            # 4. Missing NDBI
            "type": "Feature",
            "id": "mumbai_450m_4",
            "properties": {
                "schema_version": "1.0",
                "feature_id": "mumbai_450m_4",
                "city": "Mumbai",
                "lst_c": 39.0,
                "lst_anomaly_c": 2.0,
                "ndvi_mean": 0.3,
                "ndbi_mean": None,
                "ndwi_mean": 0.05,
                "land_cover_class": "mixed",
                "source": "Landsat Collection 2 Level 2",
                "satellite": "Landsat 9",
                "date_period_start": "2026-03-01",
                "date_period_end": "2026-05-31",
                "processing_date": "2026-08-13",
                "resolution_m_source": 30,
                "resolution_m_sample": 450,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "validated",
                "valid_pixel_percent": 90.0
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8400, 19.0400]
            }
        },
        {
            # 5. Missing NDWI
            "type": "Feature",
            "id": "mumbai_450m_5",
            "properties": {
                "schema_version": "1.0",
                "feature_id": "mumbai_450m_5",
                "city": "Mumbai",
                "lst_c": 39.0,
                "lst_anomaly_c": 2.0,
                "ndvi_mean": 0.3,
                "ndbi_mean": 0.4,
                "ndwi_mean": None,
                "land_cover_class": "mixed",
                "source": "Landsat Collection 2 Level 2",
                "satellite": "Landsat 9",
                "date_period_start": "2026-03-01",
                "date_period_end": "2026-05-31",
                "processing_date": "2026-08-13",
                "resolution_m_source": 30,
                "resolution_m_sample": 450,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "validated",
                "valid_pixel_percent": 90.0
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8400, 19.0400]
            }
        },
        {
            # 6. All optional unavailable
            "type": "Feature",
            "id": "mumbai_450m_6",
            "properties": {
                "schema_version": "1.0",
                "feature_id": "mumbai_450m_6",
                "city": "Mumbai",
                "lst_c": 38.0,
                "lst_anomaly_c": 1.0,
                "ndvi_mean": None,
                "ndbi_mean": None,
                "ndwi_mean": None,
                "land_cover_class": None,
                "source": "Landsat Collection 2 Level 2",
                "satellite": "Landsat 9",
                "date_period_start": "2026-03-01",
                "date_period_end": "2026-05-31",
                "processing_date": "2026-08-13",
                "resolution_m_source": 30,
                "resolution_m_sample": 450,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "low",
                "valid_pixel_percent": None
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8300, 19.0300]
            }
        }
    ]
}
