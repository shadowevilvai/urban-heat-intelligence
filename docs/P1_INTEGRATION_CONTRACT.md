# P1 Geospatial Integration Contract

This document defines the strictly normalized data structure provided by the P1 (Geospatial) module to downstream modules (like P2 ML/Risk layer). 

## Scientific Constraints & Limitations
Any downstream module consuming this data MUST abide by these constraints:
- **`lst_c` is Land Surface Temperature, not near-surface air temperature.**
- Do not use this data directly to infer human thermal comfort, health risk, or vulnerability.
- **The 450m value is a spatial sampling/visualization representation of the underlying 30m LST composite.** It must not be described as a 450m ground-truth temperature measurement.
- `null` means unavailable or not implemented. It must **never** be interpreted as zero. P2 must safely handle nullable fields.

## Schema Version
`schema_version: "1.0"`

## Field Definitions & Ownership

| Field | Required/Optional | Data Type | Units | Nullable | Owner | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `schema_version` | Required | String | N/A | No | P1 | Currently "1.0". Must be in properties. |
| `feature_id` | Required | String | N/A | No | P1 | Deterministic stable identifier. |
| `city` | Required | String | N/A | No | P1 | E.g., "mumbai". |
| `lst_c` | Required | Float | degrees Celsius | No | P1 | Point sample from median composite. |
| `lst_anomaly_c` | Required | Float | degrees Celsius | Yes | P1 | Pending baseline definition. |
| `source` | Required | String | N/A | No | P1 | E.g., "Landsat Collection 2 Level 2". |
| `satellite` | Required | String | N/A | No | P1 | E.g., "Landsat 8/9". |
| `date_period_start` | Required | String (YYYY-MM-DD) | N/A | No | P1 | |
| `date_period_end` | Required | String (YYYY-MM-DD) | N/A | No | P1 | |
| `processing_date` | Required | String (YYYY-MM-DD) | N/A | No | P1 | |
| `resolution_m_source`| Required | Integer | metres | No | P1 | Usually 30. |
| `resolution_m_sample`| Required | Integer | metres | No | P1 | Usually 450. |
| `coordinate_reference_system` | Required | String | N/A | No | P1 | Must be "EPSG:4326". |
| `data_quality` | Required | String | N/A | No | P1 | E.g., "validated". |
| `valid_pixel_percent`| Optional | Float | percentage [0,100]| Yes | P1 | If calculable per spatial cell. |
| `ndvi_mean` | Optional | Float | N/A | Yes | P1 | From Sentinel-2 (Pending). |
| `ndbi_mean` | Optional | Float | N/A | Yes | P1 | From Sentinel-2 (Pending). |
| `ndwi_mean` | Optional | Float | N/A | Yes | P1 | From Sentinel-2 (Pending). |
| `land_cover_class` | Optional | String | N/A | Yes | P1 | Source pending. |
| `hotspot_id` | N/A | N/A | N/A | N/A | P2 | P2 must calculate and assign. |
| `hotspot_score` | N/A | N/A | N/A | N/A | P2 | P2 must calculate and assign. |
| `confidence` | N/A | N/A | N/A | N/A | P2 | P2 must calculate and assign. |

## Payload Structure
The payload is a valid GeoJSON FeatureCollection where each Feature represents a discrete grid point and its associated properties.
See `geospatial/outputs/integration/example_payload.json` for a complete example.
