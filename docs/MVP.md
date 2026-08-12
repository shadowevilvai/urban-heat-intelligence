# Minimum Viable Product

## Goal

Demonstrate a complete, reproducible end-to-end workflow for one limited
urban Area of Interest.

## MVP Scope

### 1. AOI

Start with one selected urban region.

Do not start with all of India.

### 2. Real Geographic Map

Display a real interactive base map.

The base map is separate from analytical overlays.

### 3. Heat/LST Layer

Use a validated LST/heat product.

Display:

-   temperature
-   unit
-   date
-   source
-   resolution where relevant
-   legend

### 4. Hotspots

Detect a limited number of hotspots.

Each hotspot:

-   ID
-   geometry/coordinates
-   LST
-   severity
-   date/source

### 5. Risk Engine

For selected hotspot:

-   risk score
-   vulnerability/exposure score if supported
-   contributing factors
-   model version
-   uncertainty/limitations

### 6. Mitigation Simulator

Support at least two evidence-supported interventions.

The first candidates may be:

-   vegetation/tree canopy
-   cool roofs

Final choices depend on available data and literature.

### 7. Optimization

Simple constrained optimization:

Input:

-   budget
-   available interventions
-   target areas

Output:

-   recommended mix
-   estimated cost
-   expected impact
-   constraint status

### 8. Dashboard

Minimum product areas:

1.  Overview
2.  Heat Map
3.  Hotspot Details
4.  Mitigation Simulator
5.  Optimization

## MVP Demo

``` text
Open dashboard
      ↓
Select AOI
      ↓
Real map + heat layer
      ↓
Click hotspot
      ↓
View risk
      ↓
View contributing factors
      ↓
Run mitigation scenario
      ↓
Compare baseline vs scenario
      ↓
Enter constraints
      ↓
Run optimization
      ↓
View recommended strategy
```

## Data Strategy

Use a reproducible validated dataset first.

``` text
Validated/cached data
        ↓
Repeatable pipeline
        ↓
API integration
        ↓
Live/near-real-time enhancement if feasible
```

Do not make live external services a single point of failure for the SIH
demo.

## MVP Must Not

-   fabricate scientific values
-   imply LST equals air temperature or human thermal comfort
-   claim exact intervention cooling without evidence
-   process huge raw satellite datasets on every UI click
-   depend on a single external API
-   hide uncertainty/assumptions
