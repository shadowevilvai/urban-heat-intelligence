MOCK_HOTSPOT_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "hotspot_id": "MUM-HS-001",
                "city": "Mumbai",
                "lst_mean_c": 42.6,
                "lst_min_c": 40.1,
                "lst_max_c": 45.2,
                "lst_anomaly_c": 4.2,
                "heat_class": "very_high",
                "hotspot_score": 87.4,
                "ndvi_mean": 0.18,
                "ndbi_mean": 0.52,
                "ndwi_mean": 0.06,
                "land_cover_class": "built_up",
                "source": "Landsat 9",
                "satellite": "L9",
                "acquisition_date": "2026-05-15",
                "processing_date": "2026-05-16",
                "cloud_cover_percent": 1.2,
                "resolution_m": 30.0,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "high",
                "valid_pixel_percent": 99.5,
                "confidence": 0.91
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8777, 19.0760]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "hotspot_id": "MUM-HS-002",
                "city": "Mumbai",
                "lst_mean_c": 39.5,
                "lst_min_c": 38.0,
                "lst_max_c": 41.0,
                "lst_anomaly_c": 1.5,
                "heat_class": "moderate",
                "hotspot_score": 60.0,
                # Missing optional environmental indicators
                "ndvi_mean": None,
                "ndbi_mean": None,
                "ndwi_mean": None,
                "land_cover_class": None,
                "source": "Landsat 9",
                "satellite": "L9",
                "acquisition_date": "2026-05-15",
                "processing_date": "2026-05-16",
                "cloud_cover_percent": 5.0,
                "resolution_m": 30.0,
                "coordinate_reference_system": "EPSG:4326",
                "data_quality": "medium",
                "valid_pixel_percent": 85.0,
                "confidence": 0.75
            },
            "geometry": {
                "type": "Point",
                "coordinates": [72.8500, 19.0500]
            }
        }
    ]
}
