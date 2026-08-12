# Frontend Implementation Guide

## Role

The frontend is the product layer that connects geospatial, ML and
optimization services.

Its job is to make scientific output understandable and actionable.

## Primary Stack

-   React
-   TypeScript
-   Tailwind CSS
-   MapLibre GL JS
-   TanStack Query
-   Recharts where required

## Component Structure

``` text
App
├── AppShell
│   ├── Header
│   ├── Sidebar
│   └── MainContent
│
├── Dashboard
│   ├── MapView
│   │   ├── BaseMap
│   │   ├── HeatLayer
│   │   ├── HotspotLayer
│   │   ├── BoundaryLayer
│   │   └── MapControls
│   ├── Summary
│   └── RecentHotspots
│
├── HotspotPanel
│   ├── RiskScore
│   ├── Metrics
│   ├── Contributors
│   └── Recommendations
│
├── SimulationPanel
│   ├── InterventionSelector
│   ├── ParameterControls
│   ├── Comparison
│   └── Results
│
└── OptimizationPanel
    ├── ConstraintInputs
    ├── RunOptimization
    └── StrategyResults
```

## Map Architecture

The map should contain:

``` text
MapLibre
   ↓
Base geographic map
   +
Heat/LST raster or tile layer
   +
Hotspot GeoJSON/vector layer
   +
Optional analytical layers
```

The map is the primary product surface.

## State

### Server state

Use TanStack Query for:

-   areas
-   heat layer metadata
-   hotspots
-   hotspot analysis
-   simulations
-   optimization

### UI state

Manage:

-   selected hotspot
-   selected layer
-   opacity
-   map position
-   open panel
-   scenario controls
-   filters

## Scientific Display Rules

Every scientific value should have context.

Bad:

``` text
42.7
```

Good:

``` text
42.7 °C
Land Surface Temperature
Observed: 15 Jan 2026
```

Bad:

``` text
Risk: 87
```

Good:

``` text
Heat Risk
87 / 100
HIGH
Model: risk-v0.1
```

Distinguish:

-   Observed
-   Predicted
-   Simulated
-   Recommended

## Map Interaction

Judge/user should be able to:

1.  Pan/zoom.
2.  Toggle layers.
3.  Click hotspot.
4.  Open details.
5.  Inspect contributing factors.
6.  Run simulation.
7.  Compare scenarios.
8.  Open optimization.

## Mock Data

Store mock responses under:

``` text
frontend/src/mocks/
```

Use an environment/config switch.

Example:

``` text
VITE_USE_MOCK_API=true
```

Never silently mix mock and production responses.

## Error Handling

One service failing should not crash the entire dashboard.

Examples:

``` text
Heat layer unavailable
→ Show cached layer if valid
```

``` text
Risk model unavailable
→ Heat map remains usable
```

``` text
Optimization failed
→ Show validation error / retry
```

## Loading

Use meaningful progress states:

-   Loading heat layer...
-   Loading hotspot analysis...
-   Running simulation...
-   Optimizing intervention plan...

## Responsive

Desktop:

-   large map
-   side panel

Tablet:

-   map + collapsible panel

Mobile:

-   map-first
-   bottom sheet
-   compact controls

## Taste Skill Instruction

Use `design-taste-frontend` for visual quality and anti-generic design.

However:

-   Do not turn the dashboard into a landing page.
-   Do not sacrifice map usability for aesthetics.
-   Do not add animations that interfere with scientific analysis.
-   Do not override API/data requirements.
-   Do not invent UI metrics.

## Frontend Acceptance

-   responsive
-   no console errors
-   no broken states
-   typed API responses
-   loading/error handling
-   real map
-   analytical overlays
-   clear legends
-   visible units
-   visible data dates
-   visible source/model status
-   no production fake data
