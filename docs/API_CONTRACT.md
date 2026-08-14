# API Contract

This is the integration contract between backend modules and frontend.

Endpoint paths may evolve, but semantics should remain stable.

## API Conventions

Responses should include, where applicable:

-   source
-   date/time
-   units
-   spatial resolution
-   model version
-   status
-   assumptions/limitations

Never make the frontend infer units or scientific meaning from field
names alone.

## 1. Areas

### GET /api/v1/areas

``` json
{
  "areas": [
    {
      "id": "aoi-001",
      "name": "Study Area",
      "bbox": [72.80, 18.95, 72.95, 19.20]
    }
  ]
}
```

## 2. Heat Layer

### GET /api/v1/heat

Parameters:

-   area_id
-   start_date
-   end_date

``` json
{
  "area_id": "aoi-001",
  "data_type": "land_surface_temperature",
  "date": "2026-01-15",
  "source": "Landsat Collection 2 Level 2",
  "unit": "celsius",
  "resolution_m": 30,
  "layer_url": "...",
  "min": 29.2,
  "max": 45.7,
  "status": "observed"
}
```

## 3. Hotspots

### GET /api/v1/hotspots

``` json
{
  "hotspots": [
    {
      "id": "hs-001",
      "latitude": 19.01,
      "longitude": 72.84,
      "lst_celsius": 42.7,
      "severity": "high",
      "status": "observed"
    }
  ]
}
```

## 4. Hotspot Analysis

### GET /api/v1/hotspots/{id}

``` json
{
  "id": "hs-001",
  "lst_celsius": 42.7,
  "lst_min_c": 40.1,
  "lst_max_c": 45.2,
  "lst_anomaly_c": 4.2,
  "ndvi_mean": 0.18,
  "ndbi_mean": 0.52,
  "ndwi_mean": 0.06,
  "land_cover_class": "built_up",
  "risk_score": 87,
  "risk_category": "high",
  "vulnerability_score": 74,
  "contributors": [
    {
      "name": "low vegetation",
      "value": 0.09,
      "importance": 0.31
    }
  ],
  "data_date": "2026-01-15",
  "model_version": "risk-v0.1",
  "status": "predicted"
}
```

## 5. Simulation

### POST /api/v1/simulate

``` json
{
  "hotspot_id": "hs-001",
  "intervention": "tree_canopy",
  "intensity": 0.2
}
```

Response:

``` json
{
  "baseline_lst_celsius": 42.7,
  "predicted_lst_celsius": 40.8,
  "estimated_change_celsius": -1.9,
  "evidence_level": "literature_supported",
  "assumptions": [
    "Scenario is based on validated model relationship"
  ],
  "model_version": "simulation-v0.1",
  "status": "simulated"
}
```

## 6. Optimization

### POST /api/v1/optimize

``` json
{
  "area_id": "aoi-001",
  "budget": 100000000,
  "interventions": [
    "tree_canopy",
    "cool_roof"
  ]
}
```

Response:

``` json
{
  "status": "optimal",
  "budget": 100000000,
  "estimated_total_cost": 98500000,
  "expected_cooling": 2.1,
  "recommendations": [
    {
      "intervention": "tree_canopy",
      "allocation": 0.42
    }
  ],
  "model_version": "optimizer-v0.1"
}
```

## Frontend Rules

Frontend must:

-   treat null scientific values as null
-   display units
-   display date/source
-   display model status/version where relevant
-   handle errors independently
-   handle partial service failures
-   never hard-code production scientific results

## Mock API

Frontend may use local mock responses while backend work is ongoing.

Mock data must be clearly isolated and never silently shipped as
production output.
