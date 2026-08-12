# Data Sources & Data Strategy

## Purpose

This document prevents the team from choosing datasets ad hoc.

The exact final dataset combination must be validated during research.

## Recommended Initial Stack

### 1. Landsat 8/9 Collection 2 Level 2

Primary candidate for **Land Surface Temperature (LST)**.

The Earth Engine catalog provides atmospherically corrected surface
reflectance and land-surface-temperature data for Landsat 8/9 Level 2
products, including thermal information and QA bands.
citeturn0search2turn0search5

Use for:

-   LST target/observed heat layer
-   multispectral features
-   historical analysis

Important:

-   LST is surface temperature, not automatically air temperature.
-   Apply QA/cloud filtering.
-   Document acquisition time and spatial resolution.
-   Do not treat missing ST pixels as valid observations.

### 2. Sentinel-2 Harmonized Surface Reflectance

Candidate for higher-resolution multispectral features.

The harmonized Sentinel-2 L2A collection provides surface reflectance,
has a nominal 5-day revisit, and includes bands at 10 m, 20 m and 60 m
spatial resolutions depending on band. citeturn1search2turn1search3

Use for:

-   NDVI
-   NDWI
-   built/land-cover features
-   vegetation characterization
-   land-cover context

Important:

Sentinel-2 does **not** provide the thermal LST backbone used by the
initial architecture.

### 3. ERA5 / ERA5-Land

Candidate for atmospheric/environmental context.

ERA5 provides hourly reanalysis at roughly 31 km grid spacing, while
ERA5-Land provides land-focused hourly reanalysis at approximately 11 km
pixel size. citeturn1search0turn1search1

Possible features:

-   air temperature
-   wind
-   humidity/dew point
-   radiation
-   soil/land variables

Important:

These are much coarser than Landsat/Sentinel imagery.

Do not pretend they provide 10--30 m weather information.

### 4. DEM / Elevation

Use a validated DEM for:

-   elevation
-   slope
-   terrain context

### 5. Urban Data

Potential:

-   building footprints
-   road networks
-   land-use/land-cover
-   population/exposure

Each dataset must be evaluated for:

-   geographic coverage
-   date
-   resolution
-   license
-   completeness

## Spatial Alignment

Different datasets have different resolutions and projections.

Example:

``` text
Sentinel-2       ≈ 10–20 m for relevant bands
Landsat LST      ≈ 30 m product scale
ERA5-Land        ≈ 11 km
```

Do not simply resample everything to 10 m and claim that all variables
have 10 m information.

Earth Engine documents explicit resampling/reduction methods for
combining datasets at different scales. citeturn1search11

The research team must define a **common analysis grid** appropriate to
the target variable.

## Data Registry

Maintain a table:

  --------------------------------------------------------------------------------------------------------
  Dataset      Role         Resolution Date/Cadence   CRS      Source             License      Status
  ------------ ---------- ------------ -------------- -------- ------------------ ------------ -----------
  Landsat L2   LST               \~30m TBD            TBD      USGS/EE            Public       Candidate

  Sentinel-2   Features        10--20m 5-day nominal  TBD      Copernicus/EE      Copernicus   Candidate
  SR                                   revisit                                    terms        

  ERA5-Land    Weather          \~11km Hourly         TBD      ECMWF/Copernicus   C3S terms    Candidate
               context                                                                         
  --------------------------------------------------------------------------------------------------------

## Data Priority

Start small:

``` text
Landsat LST
   +
Sentinel-2 NDVI/NDBI/NDWI
   +
One validated weather/context source
   +
Basic urban features
```

Only add more datasets if they improve the research question/model.

## Data Quality Rules

-   Cloud mask
-   QA filtering
-   Missing-data handling
-   Temporal matching
-   CRS consistency
-   Resolution policy
-   Outlier handling
-   Source/date tracking

## Demo Reliability

Precompute/cache the validated study-area outputs for the SIH demo.

The UI should not depend on a live satellite query completing during the
presentation.
