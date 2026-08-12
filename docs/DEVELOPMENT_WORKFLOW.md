# Development Workflow

## Goal

Allow six people to work in parallel without creating integration chaos.

## Phase 0 --- Research Lock

Before major coding:

-   finalize problem interpretation
-   choose study AOI
-   choose candidate datasets
-   define target variable
-   define risk concept
-   define initial interventions
-   define validation protocol

## Phase 1 --- Data Proof

Person 1:

-   obtain sample satellite data
-   produce LST
-   produce NDVI/NDBI/NDWI
-   generate first heat map
-   document data quality

Person 5:

-   validate data sources and methodology

Person 2:

-   prepare baseline ML approach

Person 3:

-   research intervention evidence and optimization formulation

Person 4:

-   build frontend using mock API

Person 6:

-   build product story and demo narrative

## Phase 2 --- Integration

Connect:

``` text
Geospatial
   ↓
ML
   ↓
Optimization
   ↓
API
   ↓
Frontend
```

Agree on API contracts before integration.

## Phase 3 --- Validation

Test:

-   spatial generalization
-   temporal generalization where feasible
-   missing data
-   edge cases
-   external API failure
-   model uncertainty

## Phase 4 --- Product Polish

Only after scientific pipeline works:

-   UI polish
-   animation
-   responsive design
-   charts
-   visual hierarchy
-   demo mode

## Git Workflow

Recommended:

``` text
main
  └── develop
       ├── feature/geospatial
       ├── feature/ml-risk
       ├── feature/optimization
       ├── feature/frontend
       └── feature/docs-validation
```

Use pull requests for merging substantial work.

## Frontend Parallel Development

Frontend can start before backend using:

``` text
Mock API
   ↓
React UI
   ↓
Real API later
```

The mock response must follow `API_CONTRACT.md` exactly.

## Definition of Done

A feature is not done when it "looks good."

It is done when:

-   implementation works
-   API contract is stable
-   error/loading states exist
-   scientific units/source/date are present
-   validation is documented where applicable
-   frontend and backend agree on schema

## Demo Freeze

Before SIH presentation:

-   freeze model version
-   freeze dataset/version
-   freeze optimization configuration
-   cache critical outputs
-   test without internet where possible
-   keep a documented fallback
-   run the entire demo end-to-end several times
