# Urban Heat Intelligence: Geospatial Module (P1)

This module handles the ingestion, validation, and processing of raw geospatial data (satellite imagery, environmental parameters) to generate robust baseline observations for the Urban Heat Intelligence system.

## Data Sources & LST Methodology
- **Land Surface Temperature (LST)** is derived strictly from **Landsat 8 and Landsat 9 Collection 2 Level 2** data (`ST_B10` band). 
- QA_PIXEL bitmasking is rigidly applied to drop all cloudy, shadowed, snow, or invalid pixels.
- The pipeline generates a **median composite** over the specified observation period (e.g. pre-monsoon `2023-03-01` to `2023-05-31`).

## Study Areas
- `mumbai`: [72.80, 18.95, 72.95, 19.20]
- `dhanbad`: [86.30, 23.70, 86.55, 23.90]

## Scientific Limitations
- **`lst_c` represents Land Surface Temperature, not near-surface air temperature.** 
- Do not use this data directly to infer human thermal comfort, health risk, or vulnerability. 
- The exported GeoJSON represents a **450m spatial sampling/visualization representation** of the underlying 30m LST composite. It must not be described as a 450m ground-truth temperature measurement.

## P1 → P2 Integration Contract
P1 outputs a strictly normalized `GeoJSON FeatureCollection` designed to be consumed by P2 (ML/Risk). 
- **Real vs Example Data:** The pipeline exports real observations via `export_lst_spatial.py`. Example static schemas (complete and missing-optional) are kept in `outputs/integration/` purely for interface definition.
- **Field Ownership:** P1 owns raw geospatial observation fields (`lst_c`, `geometry`, `satellite`, `resolution_m_source`, etc.). P2 owns machine learning and downstream clustering fields (`hotspot_score`, `hotspot_id`, `confidence`). P1 explicitly *does not* output P2's fields.
- **Nullable Semantics:** A value of `null` indicates the feature is missing or pending project definition (e.g. `lst_anomaly_c`). Null must **never** be interpreted as zero.

See `docs/P1_INTEGRATION_CONTRACT.md` for the full schema details.

## Validation Command
To test integration payloads deterministically without requiring live Earth Engine authentication:
```bash
python geospatial/scripts/validate_integration_payload.py
```
