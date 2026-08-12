# Urban Heat Intelligence --- SIH Project

## Project Overview

**Working title:** Urban Heat Intelligence\
**Problem Statement:** Optimizing Urban Heat Mitigation and Cooling
Strategies via AI/ML

Urban Heat Intelligence is an AI/ML-powered geospatial decision-support
platform that helps users:

1.  Observe urban heat patterns from validated geospatial data.
2.  Identify and rank heat hotspots.
3.  Analyze heat-risk/vulnerability factors.
4.  Simulate evidence-supported mitigation interventions.
5.  Optimize intervention choices under constraints such as budget and
    available area.
6.  Present the results on a real interactive geographic map.

## Core Product Question

The product must answer:

> **Where is the heat problem, why is the area vulnerable, and what
> intervention should be prioritized?**

The product is **not just a heatmap**.

## Core Flow

``` text
Satellite + Environmental + Urban Data
                    ↓
          Geospatial Processing
                    ↓
       Heat / LST Intelligence
                    ↓
             Hotspot Detection
                    ↓
       Risk & Vulnerability Engine
                    ↓
          Mitigation Simulation
                    ↓
             Optimization
                    ↓
          Interactive GIS Dashboard
```

## Important Scientific Distinctions

The UI and APIs must distinguish:

-   **Observed:** measured/derived from a source dataset.
-   **Predicted:** produced by an ML model.
-   **Simulated:** estimated under a hypothetical intervention.
-   **Recommended:** selected by an optimization procedure.

Do not label all four simply as "AI result."

## Team Modules

  -----------------------------------------------------------------------
  Module                  Owner                   Primary Output
  ----------------------- ----------------------- -----------------------
  Geospatial Data & Heat  Person 1                Heat/LST layers +
  Intelligence                                    geospatial features +
                                                  hotspots

  AI Heat-Risk &          Person 2                Risk prediction +
  Vulnerability Engine                            explanation

  Mitigation Simulation & Person 3                Scenario simulation +
  Optimization                                    optimal strategy

  Product Engineering     Person 4                Integrated dashboard

  Research & Validation   Person 5                Scientific evidence +
                                                  validation

  Product & Presentation  Person 6                Product story + pitch +
                                                  demo
  -----------------------------------------------------------------------

## Frontend Owner

The frontend owner turns the outputs of the other modules into a
coherent decision-support product.

Responsibilities:

-   Real interactive geographic map
-   Heat/LST visualization
-   Hotspot selection
-   Risk/vulnerability panels
-   Explainability
-   Mitigation scenario controls
-   Optimization results
-   Data source/date/model status
-   Loading/error/empty/stale states
-   Responsive design
-   API integration

## Development Philosophy

-   Prove the scientific pipeline before polishing the UI.
-   Start with one well-defined Area of Interest (AOI).
-   Keep geospatial, ML, optimization and frontend modules decoupled.
-   Use mock API responses during parallel frontend development.
-   Never fabricate scientific results.
-   Document assumptions and uncertainty.
-   Prefer reproducibility over "live demo magic."
-   Do not claim real-time satellite analysis unless the pipeline
    actually supports it.

## Repository Structure

``` text
/
├── README.md
├── docs/
│   ├── DESIGN.md
│   ├── TECHSTACK.md
│   ├── PRD.md
│   ├── MVP.md
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACT.md
│   ├── FRONTEND_GUIDE.md
│   ├── RESEARCH_VALIDATION.md
│   ├── DATA_SOURCES.md
│   └── DEVELOPMENT_WORKFLOW.md
├── frontend/
├── backend/
├── ml/
├── geospatial/
├── optimization/
└── data/
```

## Current Scope

Start with one small urban AOI.

Recommended progression:

``` text
Single AOI
  ↓
Reliable heat/LST layer
  ↓
Hotspots
  ↓
Risk model
  ↓
1–2 evidence-supported interventions
  ↓
Simple optimization
  ↓
Dashboard
  ↓
Validation
  ↓
Scale
```
