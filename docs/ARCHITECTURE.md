# System Architecture

## High-Level

``` text
                 ┌─────────────────────┐
                 │   React Frontend    │
                 │ Map + Decision UI   │
                 └──────────┬──────────┘
                            │
                         REST/JSON
                            │
                 ┌──────────▼──────────┐
                 │      FastAPI        │
                 │ API / Orchestrator  │
                 └──────────┬──────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Geospatial   │    │ Heat Risk ML │    │ Optimization │
│ Service      │    │ Service      │    │ Service      │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                   PostgreSQL/PostGIS
```

## Data Flow

``` text
Satellite / Environmental / Urban Data
                  ↓
            Preprocessing
                  ↓
         Feature Engineering
                  ↓
         Heat/LST Intelligence
                  ↓
            Hotspot Engine
                  ↓
        Risk/Vulnerability Model
                  ↓
        Mitigation Simulation
                  ↓
             Optimization
                  ↓
               API
                  ↓
             Frontend
```

## Important Separation

### Geospatial layer

Produces:

-   imagery-derived features
-   LST/heat layer
-   spatial boundaries
-   hotspot candidates

### ML layer

Consumes validated features and produces:

-   risk predictions
-   vulnerability/exposure scores
-   explanations

### Optimization layer

Consumes validated simulation outputs and produces:

-   strategy recommendations
-   cost/impact trade-offs

### Frontend

Consumes APIs and visualizes results.

It should not:

-   calculate LST
-   run ML
-   call GEE for heavy processing
-   implement optimization logic

## Real Map Architecture

``` text
MapLibre GL JS
      ↓
Basemap provider
      +
Our analytical tile/GeoJSON layers
      ↓
Interactive map
```

The basemap and AI overlays must remain conceptually separate.

## Fallback

``` text
Primary service
      ↓
Available?
  ┌───┴────┐
 YES       NO
  ↓         ↓
Live      Cached validated
result    result
```

Fallback data must be clearly identified in development/demo tooling.

## Module Ownership

### Person 1

Geospatial/data pipeline.

### Person 2

Risk/vulnerability ML.

### Person 3

Simulation/optimization.

### Person 4

Frontend/product integration.

### Person 5

Research/validation.

### Person 6

Product/presentation.
