# Product Requirements Document

## 1. Product

**Urban Heat Intelligence**

## 2. Problem

Urban areas can develop localized heat hotspots due to combinations of
built-up surfaces, vegetation loss, urban morphology, environmental
conditions and other factors.

Decision-makers need more than a temperature visualization. They need
decision support:

-   Where are the hotspots?
-   Which areas are most vulnerable?
-   What factors contribute?
-   What interventions are feasible?
-   Which strategy should be prioritized under constraints?

## 3. Vision

Transform validated geospatial and environmental data into:

**Heat intelligence → risk analysis → mitigation simulation → optimized
intervention plans.**

## 4. Users

Primary:

-   Urban planners
-   Municipal authorities
-   Climate/environment departments
-   Disaster-management stakeholders
-   Researchers

Secondary:

-   Smart-city teams
-   Academic institutions
-   Sustainability teams

## 5. Core Features

### P0 --- Heat Intelligence

-   Select AOI
-   Select observation period
-   Display validated heat/LST layer
-   Display real geographic base map
-   Detect/display hotspots
-   View source/date/unit

### P0 --- Risk & Vulnerability

-   Heat-risk score
-   Vulnerability/exposure indicators when supported
-   Explain contributing factors
-   Show model/version/limitations

### P0 --- Mitigation Simulation

-   Select hotspot
-   Select intervention
-   Change scenario parameters
-   Compare baseline vs simulated outcome
-   Display assumptions/evidence level

### P0 --- Optimization

-   Enter budget/constraints
-   Select available interventions
-   Run optimization
-   Display recommended strategy
-   Show cost, coverage, expected impact and trade-offs

### P1

-   Historical trends
-   Saved scenarios
-   Report export
-   Multi-city support
-   More intervention types

## 6. Non-Goals for MVP

-   Global coverage
-   Fully real-time satellite processing
-   Automatic legal/enforcement decisions
-   Exact cooling guarantees
-   Autonomous municipal decision-making
-   High-resolution human thermal-comfort prediction unless separately
    validated

## 7. User Stories

### Heat Map

As an urban planner, I want to view heat intensity on a real map so I
can identify hotspots.

### Hotspot Analysis

As a planner, I want to select a hotspot and understand its risk and
contributing factors.

### Simulation

As a planner, I want to simulate an intervention and compare it with the
baseline.

### Optimization

As a decision-maker, I want to provide constraints so the system can
recommend an intervention mix.

### Explainability

As a researcher, I want to understand why the model assigns a risk
score.

## 8. Success Metrics

### Product

-   Map load success
-   Hotspot selection success
-   Scenario completion
-   API error rate
-   Demo reliability

### ML

-   MAE
-   RMSE
-   R²
-   Spatial generalization
-   Temporal generalization where relevant

### Optimization

-   Objective improvement
-   Constraint satisfaction
-   Cost/impact trade-off

## 9. Scientific Integrity

Every scientific result should identify, where applicable:

-   source
-   observation/prediction date
-   spatial resolution
-   units
-   model version
-   assumptions
-   limitations

The UI must distinguish:

**Observed / Predicted / Simulated / Recommended**

## 10. MVP Acceptance

The MVP is complete when:

1.  One defined AOI loads.
2.  A real interactive base map is displayed.
3.  A validated heat/LST layer is displayed.
4.  Hotspots can be identified.
5.  A hotspot can be selected.
6.  Risk information can be retrieved.
7.  At least one mitigation scenario runs.
8.  A constrained optimization workflow runs.
9.  Results are traceable to documented data/methodology.
10. The demo works using a reproducible fallback if external services
    fail.
