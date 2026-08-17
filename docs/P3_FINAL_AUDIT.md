# P3 FINAL IMPLEMENTATION AUDIT PACKAGE

## 1. Current Branch / Git State
- **Branch**: `feature/optimization-new`
- **Status**: Up to date with origin/feature/optimization-new. 
- **Diff/Modified files**: None (clean working tree except for new/untracked P3 files).
- **Deleted files**: None.
- **Untracked files**: 
  - `ml/optimization/` (Directory containing the entire P3 implementation)
  - `ml/tests/test_optimization.py` (Test suite for P3)
  - `scratch/` (Temporary scripts for audit execution)

These files belong to P3 as they implement the new optimization, suitability, and simulation pipelines strictly segregated from P1 and P2 components. No existing P1/P2 logic was modified.

## 2. Complete P3 File Inventory
* `ml/optimization/__init__.py`: Production - Exposes domain enums and status flags.
* `ml/optimization/domain.py`: Production - Defines core enums (`InterventionType`, `ValueStatus`, `SuitabilityCategory`, `EvidenceLevel`).
* `ml/optimization/schemas.py`: Production - Pydantic schemas enforcing input/output validation across Suitability, Simulation, and Optimization.
* `ml/optimization/config.py`: Production - Configuration holding literature-supported coefficients and provenance metadata.
* `ml/optimization/suitability.py`: Production - Context-aware suitability engine restricting inappropriate interventions based on P1/P2 indicators.
* `ml/optimization/simulator.py`: Production - Deterministic estimator of physical cooling and bounds.
* `ml/optimization/optimizer.py`: Production - HiGHS linear programming resource allocator based on priority, suitability, and physical constraints.
* `ml/tests/test_optimization.py`: Test Code - 43 assertions validating schema conformity, mathematical correctness, edge-case suitability, and optimizer deterministic semantics.

## 3. Actual P1 → P2 → P3 Contract Audit
P3 strictly consumes the exact outputs from P1 and P2 without modifying them.

**Mapping:**
- **P1 fields:** `feature_id`, `lst_c`, `lst_anomaly_c`, `ndvi_mean`, `ndbi_mean`, `ndwi_mean`, `land_cover_class` 
- **P2 fields:** `risk_score`, `risk_category`, `vulnerability_score`, `hotspot_context`, `contributors`, `model_version`
- **P3 fields (Inputs):** `hotspot_id`, P1 dict, P2 dict.
- **P3 consumption:**
  - `lst_c` is mapped to `observed_lst_celsius`.
  - `hotspot_context` determines base eligibility (e.g., `water` -> Unsuitable).
  - `risk_score` is used as `heat_mitigation_need_score`.
  - `ndvi_mean`, `ndbi_mean`, `land_cover_class` evaluate specific intervention feasibility (e.g., Cool Roof requires `Built-up` in industrial/mining zones).

*Note: P3 does NOT require or use `exposure_score`, `context_class`, `is_valid_target`, or `context_flags`.*

## 4. Actual P3 Schema
**Domain Enums:**
- `ValueStatus`: `OBSERVED`, `DERIVED`, `PROXY`, `SIMULATED`, `RECOMMENDED`.
- `SuitabilityCategory`: `HIGH`, `MEDIUM`, `LOW`, `UNSUITABLE`.
- `EvidenceLevel`: `LITERATURE_SUPPORTED`, `PLANNING_PROXY`.

**SimulateResponse:**
- `observed_lst_celsius` (float, required)
- `estimated_change_celsius` (float, required, must be negative or zero)
- `scenario_lst_celsius` (float, required, `observed_lst_celsius + estimated_change_celsius`)
- `cooling_uncertainty_range` (list[float], len 2, `[min, max]`)
- `status` (ValueStatus.SIMULATED)
- Provenance metadata (`source_title`, `source_year`, `evidence_level`, etc.)

**OptimizeResponse:**
- `portfolio_objective_value` (float, purely objective optimization score)
- `total_expected_cooling_celsius` (float, absolute celsius magnitude)
- `total_resources_used` (float) <= `resource_budget`
- `status` (ValueStatus.RECOMMENDED)

*These statuses are enforced via Pydantic schemas in `ml/optimization/schemas.py`.*

## 5. Suitability Engine — Mathematical Audit
**Tree Canopy**
- **Eligibility:** Unsuitable on `water` and `industrial_mining_candidate`.
- **Score:** Base feasibility evaluates `max(0, 100 - max(ndvi_mean*100, 0))` and subtracts penalties for `ndbi_mean > 0`.
- **Suitability:** `0.4 * priority_score + 0.6 * feasibility`.
- **Categories:** `>=70` (High), `>=40` (Medium), `<40` (Low).

**Cool Roof**
- **Eligibility:** Unsuitable on `water`. For `industrial_mining_candidate`, strictly requires `land_cover_class == "Built-up"`, else 0.
- **Score:** Penalized if `ndbi_mean <= 0`.
- **Suitability:** Same normalization logic. 

*Score Logic is deterministic, bounded [0, 100], and monotonic.*

## 6. Context-Specific Audit
**A. water**
- All conventional interventions (tree canopy, cool roof) explicitly score 0.0 (UNSUITABLE). Limiting factor explicitly states: "Water bodies strictly exclude conventional mitigation interventions."

**B. urban_heat**
- Normal eligibility evaluated via physical indicators (NDVI, NDBI). Optimizer proceeds to allocate.

**C. industrial_mining_candidate**
- `tree_canopy` strictly evaluated to 0.0 (UNSUITABLE).
- `cool_roof` requires explicit `land_cover_class == "Built-up"`. If no evidence -> 0.0 (UNSUITABLE) with reason "No verified built-up/roof evidence in current P1 data." If built-up evidence exists -> evaluated normally but categorized as LOW/MEDIUM.

**D. terrestrial_other**
- Normal evaluations base solely on P1 physical indicators (NDVI, NDBI).

## 7. Simulator — Complete Mathematical Audit
**Estimation Formula:**
`normalized_suitability = max(0.0, min(1.0, suitability_factor / 100.0))`
`estimated_change_celsius = -1.0 * spec.cooling_coefficient_celsius * request.intensity * normalized_suitability`
`scenario_lst_celsius = observed_lst_celsius + estimated_change_celsius`

**Uncertainty Calculation:**
`uncertainty_vals = [-1.0 * spec.cooling_uncertainty_range[0] * intensity * suit, -1.0 * spec.cooling_uncertainty_range[1] * intensity * suit]`
`uncertainty = [min(uncertainty_vals), max(uncertainty_vals)]`

**Verification:**
- Intensity bounded by `[0, 1]`, Suitability bounded by `[0, 1]`.
- Zero intensity guarantees zero estimated change.
- Cooling coefficient bounds guarantee negative (cooling) sign convention.
- Deterministic logic guarantees repeatable execution.

## 8. Cooling Coefficient Provenance
**Urban Tree Canopy**
- Coefficient: 2.0°C max potential drop
- Source: *Urban greening to cool towns and cities: A systematic review* (2010, DOI: 10.1016/j.landurbplan.2010.08.006)
- Applicability: "General urban areas with permeable ground"
- Evidence: `LITERATURE_SUPPORTED`

**Cool Roof Coating**
- Coefficient: 1.5°C max potential drop
- Source: *Cooling the cities—a review of reflective and green roof mitigation technologies* (2014, DOI: 10.1016/j.solener.2012.07.003)
- Applicability: "Built-up commercial/residential with low-albedo roofs"
- Evidence: `LITERATURE_SUPPORTED`

## 9. Uncertainty Audit
Enforced in `ml/optimization/simulator.py`:
`uncertainty = [min(uncertainty_vals), max(uncertainty_vals)]`
- Pydantic schema expects `list[float]`.
- Enforces correctly signed min/max where `min_change_celsius <= max_change_celsius`.

## 10. Optimizer — Complete Mathematical Audit
**Solver**: `scipy.optimize.linprog` (HiGHS method)

**Objective function (Minimization of negative benefit):**
`benefit = heat_mitigation_need_score (0-100) * suitability_score (0-100) * expected_cooling_per_intensity`
`c_coeffs.append(-benefit)`

**Constraints**:
- `A_ub = [cost_coeffs]` (Resource costs per intervention unit)
- `b_ub = [resource_budget]`
- `bounds = (0.0, 1.0)` (Intensity limit per intervention per hotspot)

**Mathematical Flow**:
Optimizes `c * x` subject to `A_ub * x <= b_ub` and `0 <= x <= 1`. 
Fully deterministic linear programming constraint satisfaction.

## 11. Objective Value vs Cooling Value
**Separation Verified:**
- `portfolio_objective_value`: Captures `sum(priority * suitability * cooling)`. 
- `total_expected_cooling_celsius`: Captures purely `sum(abs(estimated_change_celsius))`. 
- Optimization objective is not represented in Celsius.

## 12. Resource Unit Audit
**Proxy Definition:**
Resource units act as planning abstractions (e.g., 100 units for tree canopy, 40 units for cool roof) for a 450m point, rather than measured square footage or exact INR costs.
- The simulator explicitly defines assumption: `PROXY: Assumes physical unbuilt area exists near the 450m sampling point.`
- Constraint Verification: `total_resources_used` is explicitly capped by `resource_budget` in linear programming.
- P3 **NEVER** derives physical treatment area from `450m × 450m`. The geometry is explicitly treated as a sampling/planning reference point, not a measurable polygon. All "fractional limits" refer to scenario constraints (intensity `0.0 - 1.0`) on a hypothetical proxy resource, rather than physical square meters.

## 13. Real Data Integration
Ran `scratch/run_real_data.py` across `mumbai_lst_spatial.geojson` and `dhanbad_lst_spatial.geojson` using the actual `ml/api_handler.py` processing pipeline.

**Mumbai urban_heat**
- P1: `feature_id=unk, lst=41.79, anomaly=-0.21, ndbi=0.055, lc=Built-up`
- Canonical P2: `risk=36.18, risk_category=low, context=urban_heat`
- P3 Allocations: 
  - `tree_canopy` @ 0.6 => Scenario: 40.89°C (Expected cooling 0.9°C)
  - `cool_roof` @ 1.0 => Scenario: 40.66°C (Expected cooling 1.13°C)

**Mumbai water**
- P1: `feature_id=unk, lst=36.19, lc=Permanent water bodies`
- Canonical P2: `risk=33.85, risk_category=low, context=water`
- P3 Allocations: Total cooling 0.0, Resources used 0.0.

**Dhanbad industrial_mining_candidate**
- P1: `feature_id=unk, lst=52.25, anomaly=6.72, ndbi=0.208, lc=Bare / sparse vegetation`
- Canonical P2: `risk=65.37, risk_category=high, context=industrial_mining_candidate`
- P3 Allocations: Total cooling 0.0, Resources used 0.0. (`tree_canopy` and `cool_roof` automatically rejected due to lack of explicit "Built-up" evidence).

**Dhanbad terrestrial_other**
- P1: `feature_id=unk, lst=43.39, anomaly=0.32, ndbi=0.159, lc=Grassland`
- Canonical P2: `risk=38.49, risk_category=low, context=terrestrial_other`
- P3 Allocations: `tree_canopy` @ 0.6 => Scenario 42.51°C. `cool_roof` @ 1.0 => Scenario 42.42°C.

## 14. Real-Data Distribution Audit
- **Mumbai (2,294 Total):**
  - water: 590
  - urban_heat: 764
  - industrial_mining_candidate: 1
  - terrestrial_other: 939
  - eligible_tree_canopy: 1703
  - eligible_cool_roof: 1703
- **Dhanbad (2,989 Total):**
  - water: 17
  - urban_heat: 337
  - industrial_mining_candidate: 44
  - terrestrial_other: 2591
  - eligible_tree_canopy: 2928
  - eligible_cool_roof: 2928

## 15. Mock Data Audit
- All mock data exists purely in `ml/tests/test_optimization.py` via the function `get_mock_p1_p2()`.
- P3 uses zero mock data paths or fixtures in the production execution path.
- The `simulator.py` and `optimizer.py` are strictly stateless classes injected with real P1/P2 instances.

## 16. Test Suite Audit
`pytest ml/tests/`
- **Total Tests:** 43
- **Passed:** 43
- **Failed/Skipped/Warnings:** 0
- **Coverage:** Includes:
  - schema tests
  - suitability tests
  - simulator tests
  - optimizer tests
  - context tests
  - integration tests (P1 -> P2 -> P3 end-to-end)

*Tests prove:* Mathematical bounds, logic gating for industrial/water contexts, correct schema propagation, and deterministic resource allocation.
*Tests do NOT prove:* Real-world viability of physical intervention at exact locations (as geometry is merely a 450m sampling point).

## 17. Semantic Invariant Tests
Verified manually and via `pytest`:
- A. `total_expected_cooling_celsius == sum(selected allocation cooling)` (Verified)
- B. `total_resources_used <= resource_budget` (Verified via SciPy LP limits)
- C. `scenario_lst_celsius == observed_lst_celsius + estimated_change_celsius` (Verified in schemas)
- D. `uncertainty_min <= uncertainty_max` (Verified)
- E. `zero intervention == zero modeled cooling` (Verified in simulator)
- F. `water == no conventional mitigation allocation` (Verified in suitability logic)
- G. `industrial_mining_candidate == no conventional allocation unless explicit eligibility conditions are met` (Verified in suitability logic)
- H. `same input == same output` (Verified determinism tests)
- I. `P3 never fabricates physical treatment area` (Verified via review of `simulator.py` and `config.py`)

## 18. Scientific Limitations
- **450m point-based planning unit**: Geometry does not capture physical building outlines, street sizes, or exact unbuilt square footage.
- **Proxy resource units**: Cost definitions are abstracted resource capacities, not localized INR/m².
- **Missing population exposure**: Prioritizes general urban heat rather than specific vulnerable populations.
- **Intervention coefficients**: Assumes standardized effects and fails to capture local micro-climate impacts, localized advection, or actual structural loading capabilities.

## 19. Frontend/Backend Readiness
**Suitable for API Integration:**
- Strong Pydantic data schemas guarantee canonical JSON formats.
- Stable value statuses (`SIMULATED`, `RECOMMENDED`, `DERIVED`) structure deterministic UI rendering.
- Proper limitation and assumption string arrays guarantee explainable UI.
- No immediate backend modifications needed to consume the JSON endpoints.

## 20. Final Verdict
**P3 STATUS:** READY TO COMMIT
All integration checkpoints, architectural limits, invariant logic blocks, and provenance requirements are fully and independently addressed.
