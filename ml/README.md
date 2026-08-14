# P2 - AI Heat-Risk & Vulnerability Engine

This module implements the deterministic composite risk index for the Urban Heat Intelligence project.

## Scoring Formula & Weights

Since the `hotspot_score` from the geospatial layer is for spatial prioritization (not a ground-truth health risk label), this engine uses a transparent, rule-based statistical composite index.

The overall risk score (0-100) is a weighted combination of two components:
1. **Heat Exposure (50%)**
2. **Environmental Vulnerability (50%)**

### Heat Exposure (Always required)
Derived from thermal satellite imagery (e.g., Landsat LST):
- `norm_lst_mean` (40% of Exposure) — LST mean normalized over a theoretical 25°C - 55°C range.
- `norm_lst_anomaly` (60% of Exposure) — LST anomaly normalized over a 0°C - 10°C range.

### Environmental Vulnerability (Optional, gracefully degrades)
Derived from environmental proxy indices:
- `norm_inv_ndvi` (40% of Vulnerability) — Inverted NDVI (-1 to 1 mapped to 1.0 to 0.0). Lack of vegetation increases vulnerability.
- `norm_ndbi` (40% of Vulnerability) — NDBI (-1 to 1). High built-up area increases vulnerability.
- `norm_inv_ndwi` (20% of Vulnerability) — Inverted NDWI (-1 to 1 mapped to 1.0 to 0.0). Lack of water increases vulnerability.

### Missing Data Handling
If any environmental vulnerability features are missing from the input GeoJSON, the engine **dynamically renormalizes** the weights of the available features within the Vulnerability group so they sum to 100%.

If *no* environmental vulnerability features are available, the overall Risk Score falls back to 100% Heat Exposure, and the Vulnerability Score is returned as `null`. We do not fabricate missing data.

## Contributors
The `contributors` output is a calculated list of feature impacts, where the `importance` directly reflects the final absolute weight of that feature in the overall risk score (summing to 1.0).

## Running Tests
To run the test suite:
```bash
python -m pytest tests/ -v
```
