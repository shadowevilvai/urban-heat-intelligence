# Technical Stack

## Frontend

Recommended:

-   React
-   TypeScript
-   Vite or equivalent modern build tooling
-   Tailwind CSS
-   shadcn/ui or equivalent component system
-   TanStack Query for server state
-   Recharts or equivalent for charts
-   MapLibre GL JS for the interactive map

MapLibre GL JS is an open-source TypeScript/WebGL library for
interactive browser maps and supports vector tiles, heatmaps, custom
layers and other geospatial visualization capabilities.
citeturn0search0turn0search3

### Important

MapLibre is the **map renderer**, not the source of geographic basemap
data.

A compliant basemap/tile provider must be selected and configured
separately. If OpenStreetMap data/tiles are used, follow the applicable
attribution and tile-usage policies. citeturn1search12

## Backend

-   Python
-   FastAPI
-   Pydantic
-   PostgreSQL
-   PostGIS

## Geospatial / Data

-   Google Earth Engine
-   Rasterio
-   GeoPandas
-   Shapely
-   NumPy
-   Pandas
-   GDAL where required

Google Earth Engine is primarily a **data-processing/analysis layer**,
not something the frontend should call for every user interaction.

## Machine Learning

Start with interpretable baselines:

-   scikit-learn
-   Random Forest
-   XGBoost

Evaluate advanced deep learning only if justified by data and
validation:

-   PyTorch
-   CNN/spatial models
-   temporal/spatiotemporal models

## Optimization

Possible:

-   OR-Tools
-   SciPy Optimize
-   Pyomo if required

The optimization problem must explicitly define:

-   objective
-   decision variables
-   constraints
-   assumptions

## Data

Potential sources:

-   Landsat thermal/multispectral
-   Sentinel-2 multispectral
-   ERA5/ERA5-Land or other validated weather/reanalysis data
-   DEM/elevation
-   Building/road data
-   Population/exposure data
-   Land-use/land-cover

## Architecture

``` text
React
  ↓
FastAPI
  ↓
┌───────────┬───────────┬──────────────┐
│ Geo       │ ML        │ Optimization │
│ Service   │ Service   │ Service      │
└───────────┴───────────┴──────────────┘
  ↓
PostgreSQL + PostGIS
```

## Engineering Rules

1.  Frontend contains no ML logic.
2.  Frontend does not process raw satellite datasets.
3.  GEE processing belongs in the geospatial/data pipeline.
4.  ML models are accessed through services/APIs.
5.  Scientific calculations must be reproducible.
6.  API responses include units and dates where relevant.
7.  Do not silently mix datasets with incompatible spatial/temporal
    resolutions.
8.  Do not use arbitrary interpolation to make datasets look
    higher-resolution without documenting it.
9.  Do not commit API keys or credentials.
10. Cache expensive operations where appropriate.
