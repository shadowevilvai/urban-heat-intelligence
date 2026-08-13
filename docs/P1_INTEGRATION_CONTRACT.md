# P1 Geospatial Integration Contract

This document defines the exact data structure provided by the P1 (Geospatial) module to downstream modules (like the ML/Risk layer). It is a minimal extension of the `Heat Layer` data structures in `API_CONTRACT.md` to support internal service-to-service data handoffs where point-based feature data is required.

## Scientific Constraints & Limitations

Any downstream module consuming this data MUST abide by these constraints:
- **LST is Land Surface Temperature and is not near-surface air temperature.**
- Do not use this data directly to infer human thermal comfort, health risk, or vulnerability without additional validated contextual features.
- **The current 450 m spatial representation is a visualization/sampling representation of the underlying LST composite and is not 450 m ground-truth temperature.**

## Payload Structure

The payload wraps the `Heat Layer` metadata semantics defined in `API_CONTRACT.md` around the actual GeoJSON feature collection used for downstream point-based analysis.

```json
{
  "area_id": "mumbai",
  "data_type": "land_surface_temperature",
  "source": "Landsat 8/9 Collection 2 Level 2",
  "date_period": {
    "start": "2023-03-01",
    "end": "2023-05-31"
  },
  "spatial_resolution_m": 450,
  "unit": "celsius",
  "limitations": [
    "LST is Land Surface Temperature and is not near-surface air temperature.",
    "The current 450 m spatial representation is a visualization/sampling representation of the underlying LST composite and is not 450 m ground-truth temperature."
  ],
  "spatial_data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [72.84, 19.01]
        },
        "properties": {
          "lst_c": 38.7
        }
      }
    ]
  }
}
```
