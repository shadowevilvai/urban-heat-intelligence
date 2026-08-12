# Product & UI Design Specification

## Design Goal

The product should feel like a professional **urban climate intelligence
and decision-support system**, not a generic analytics dashboard or
landing page.

The map is the primary interaction surface.

## Primary User Journey

``` text
Open Dashboard
      ↓
Select Area / Date
      ↓
View Real Geographic Map + Heat Layer
      ↓
Select Hotspot
      ↓
Inspect Heat + Risk + Vulnerability
      ↓
Understand Contributing Factors
      ↓
Run Mitigation Scenario
      ↓
Compare Baseline vs Scenario
      ↓
Optimize Strategy
```

## Real Map Requirement

The dashboard must contain a **real interactive geographic map**.

The map has two distinct concepts:

### Base map

Provides geographic context:

-   roads
-   places
-   boundaries
-   water
-   geographic labels

The base map provider is separate from the AI heat data.

### Analytical overlays

Generated/served by our system:

-   LST/heat layer
-   hotspots
-   vegetation
-   built-up intensity
-   administrative boundaries
-   intervention/simulation layers

Do not present the base map itself as our AI output.

## Main Screens

### 1. Overview

-   Map
-   Current selected AOI
-   Heat summary
-   Number of hotspots
-   Highest-risk areas
-   Date/source status

### 2. Heat Intelligence Map

Map controls:

-   Layer toggle
-   Opacity
-   Legend
-   Date selector
-   AOI selector
-   Search
-   Zoom to hotspot

Possible layers:

-   Base map
-   Heat/LST
-   Hotspots
-   Vegetation
-   Built-up
-   Water
-   Boundaries

### 3. Hotspot Detail

Show:

-   Hotspot ID
-   Coordinates/area
-   LST with unit
-   Heat-risk score
-   Vulnerability/exposure score where available
-   Contributing factors
-   Model confidence/limitations
-   Recommended interventions

### 4. Explainability

Avoid:

``` text
Risk = 87
```

Prefer:

``` text
Heat Risk
87 / 100
HIGH

Main contributing factors
• High surface temperature
• Low vegetation
• High built-up intensity
• Exposure/vulnerability indicators
```

Only display factors actually supported by the model.

### 5. Mitigation Simulator

Controls:

-   Intervention type
-   Intensity/coverage
-   Area
-   Optional budget

Output:

-   Baseline
-   Simulated scenario
-   Expected change
-   Cost if available
-   Assumptions
-   Evidence level
-   Uncertainty where available

### 6. Optimization

Inputs:

-   Budget
-   Area/coverage constraints
-   Available interventions
-   Priority areas

Output:

-   Recommended intervention mix
-   Expected impact
-   Estimated cost
-   Coverage
-   Constraint status
-   Trade-offs

## Visual Language

Use a restrained, professional climate-tech visual language.

Principles:

-   Map-first composition
-   Strong information hierarchy
-   Moderate visual density
-   Low-to-moderate motion
-   Heat colors reserved for heat/risk semantics
-   Avoid excessive gradients
-   Avoid generic "AI dashboard" card grids
-   Keep the map visually dominant

## Taste Skill

The `design-taste-frontend` skill is a **supplementary design-quality
layer** for Antigravity.

It must not override this document.

Priority:

``` text
PRD / scientific requirements
        ↓
DESIGN.md
        ↓
FRONTEND_GUIDE.md
        ↓
design-taste-frontend skill
        ↓
implementation
```

Use the skill to improve composition, typography, hierarchy, motion,
density and polish while preserving project-specific UX requirements.

## Responsive Design

Desktop:

-   Large map
-   Analysis side panel
-   Floating map controls

Tablet:

-   Map + collapsible analysis panel

Mobile:

-   Map-first
-   Bottom-sheet hotspot details
-   Compact controls

## Required UX States

Every data-driven component must support:

-   Loading
-   Empty
-   Error
-   Partial data
-   Stale data
-   Successful state

## Accessibility

-   Do not use color alone to communicate risk.
-   Include text/labels for risk states.
-   Maintain readable contrast over maps.
-   Keyboard-accessible non-map controls.
-   Provide clear legends.
