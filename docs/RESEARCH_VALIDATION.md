# Research & Validation Framework

## Purpose

The system is an applied AI/ML research prototype. Scientific
credibility is a core product requirement.

## Research Questions

1.  Can validated geospatial/environmental variables explain or predict
    urban heat patterns?
2.  Which factors are most associated with heat intensity/risk?
3.  Does the model generalize to unseen spatial areas?
4.  Can evidence-supported intervention relationships support scenario
    simulation?
5.  Can constrained optimization improve expected impact for a defined
    budget/area?

## Data Validation

For every dataset document:

-   source
-   product name
-   acquisition/observation date
-   spatial resolution
-   temporal resolution
-   CRS
-   units
-   missing-data handling
-   cloud/quality filtering
-   known limitations
-   licensing/usage requirements

## ML Validation

Do not rely only on random splits.

Evaluate where feasible:

### Random split

Useful for initial debugging.

### Spatial split

Train on some locations and test on unseen locations.

### Temporal split

Train on earlier dates and test on later dates.

This is important because the problem is spatial and temporal.

## Regression Metrics

For LST/temperature prediction:

-   MAE
-   RMSE
-   R²

Interpret metrics in target units.

## Hotspot Metrics

Where labels exist:

-   Precision
-   Recall
-   F1
-   IoU for segmentation

## Explainability

Potential:

-   Feature importance
-   SHAP
-   Sensitivity analysis

The explanation must correspond to the actual model.

## Intervention Evidence

Do not hard-code claims such as:

> "20% more trees always gives exactly 2.5°C cooling."

Instead classify evidence:

### Level A --- Directly validated

Supported by measurements/experiments relevant to the study.

### Level B --- Literature-supported

Supported by published research but not directly validated in the study
area.

### Level C --- Scenario assumption

Used only for exploratory simulation and clearly labelled.

## LST vs Air Temperature

Land Surface Temperature is not automatically equivalent to:

-   near-surface air temperature
-   human thermal comfort
-   heat-health risk

If the product makes a health/vulnerability claim, the target variable
and evidence must be explicitly defined.

## Reproducibility

Record:

-   dataset version
-   preprocessing version
-   feature definitions
-   model version
-   training date
-   configuration
-   random seed where relevant
-   evaluation split

## Deliverables

Person 5 maintains:

1.  Literature matrix
2.  Dataset registry
3.  Methodology
4.  Validation protocol
5.  Model evaluation
6.  Assumption registry
7.  Limitations
8.  References

## Review Gate

No major scientific claim should enter the final pitch/UI until Person 5
has checked:

``` text
Claim
 ↓
Evidence
 ↓
Method
 ↓
Uncertainty
 ↓
Approved wording
```
