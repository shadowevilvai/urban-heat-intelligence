"""
Scenario Simulation Engine for Urban Heat Mitigation Interventions.

P5 RESEARCH & SCIENTIFIC INTEGRITY PRINCIPLES:
- Parameter-driven cooling models instead of fixed universal cooling coefficients.
- Tree canopy cooling explicitly parameterized by: coverage increase, canopy foliage density,
  tree height/maturity, spatial configuration (dispersed/clustered/linear corridor), and eligible area.
- Cool roof cooling explicitly parameterized by: roof coverage, baseline albedo, intervention albedo,
  thermal emissivity, and eligible rooftop area.
- Never presents simulated cooling as observed sensor measurements (strictly status="simulated").
- Distinguishes radiative Land Surface Temperature (LST) from 2-m ambient air temperature.
- Exposes uncertainty bounds, explicit parameter breakdowns, evidence levels, assumptions, and limitations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from optimization.config import MitigationConfig, default_config, MODEL_VERSION_SIMULATION
from optimization.domain import (
    CoolRoofScenarioParams,
    CurrencyUnit,
    EvidenceLevel,
    HotspotProfile,
    InterventionSpecification,
    InterventionType,
    SimulationResult,
    SpatialConfiguration,
    TreeCanopyScenarioParams,
    ValueStatus,
)
from optimization.schemas import SimulateResponse


class ScenarioSimulator:
    """
    Evaluates parameter-driven what-if mitigation scenarios for candidate heat hotspots.
    """

    def __init__(self, config: Optional[MitigationConfig] = None):
        self.config = config or default_config

    def simulate(
        self,
        hotspot: HotspotProfile,
        intervention: Union[InterventionType, str],
        intensity: float,
        tree_params: Optional[TreeCanopyScenarioParams] = None,
        roof_params: Optional[CoolRoofScenarioParams] = None,
    ) -> SimulationResult:
        """
        Execute parameter-driven scenario simulation for a given hotspot and intervention.

        Args:
            hotspot: Validated HotspotProfile containing thermal, spatial, and morphology state.
            intervention: Target intervention type ('tree_canopy', 'cool_roof').
            intensity: Implementation intensity fraction in [0.0, 1.0].
            tree_params: Optional microclimate and morphological parameters for tree canopy.
            roof_params: Optional physical surface and optical parameters for cool roof.

        Returns:
            SimulationResult: Detailed structured simulation outcome.

        Raises:
            ValueError: If intensity is outside [0.0, 1.0] or intervention is unsupported.
        """
        # 1. Validate Input Intensity
        if not isinstance(intensity, (int, float)):
            raise ValueError(f"Intensity must be a numeric value, got {type(intensity).__name__}.")
        if intensity < 0.0 or intensity > 1.0:
            raise ValueError(f"Intensity must be between 0.0 and 1.0 (inclusive), got {intensity}.")

        # 2. Resolve Intervention Type
        if isinstance(intervention, str):
            try:
                itype = InterventionType(intervention.strip().lower())
            except ValueError:
                raise ValueError(
                    f"Unsupported intervention '{intervention}'. "
                    f"Supported types: {[t.value for t in InterventionType]}"
                )
        else:
            itype = intervention

        # 3. Route to Parameter-Driven Intervention Simulation Model
        if itype == InterventionType.TREE_CANOPY:
            return self._simulate_tree_canopy(hotspot, intensity, tree_params)
        elif itype == InterventionType.COOL_ROOF:
            return self._simulate_cool_roof(hotspot, intensity, roof_params)
        else:
            raise ValueError(
                f"Intervention '{itype.value}' is not supported in the MVP simulation engine. "
                f"MVP supports: {[InterventionType.TREE_CANOPY.value, InterventionType.COOL_ROOF.value]}"
            )

    def simulate_scenario(
        self,
        hotspot: HotspotProfile,
        intervention: Union[InterventionType, str],
        intensity: float,
        tree_params: Optional[TreeCanopyScenarioParams] = None,
        roof_params: Optional[CoolRoofScenarioParams] = None,
    ) -> SimulateResponse:
        """
        Execute simulation and return response matching docs/API_CONTRACT.md schema.
        """
        result = self.simulate(
            hotspot=hotspot,
            intervention=intervention,
            intensity=intensity,
            tree_params=tree_params,
            roof_params=roof_params,
        )
        return SimulateResponse(
            baseline_lst_celsius=round(result.baseline_lst_celsius, 2),
            predicted_lst_celsius=round(result.projected_lst_celsius, 2),
            estimated_change_celsius=round(result.estimated_change_celsius, 2),
            evidence_level=result.evidence_level.value,
            assumptions=list(result.assumptions),
            model_version=result.model_version,
            status=result.status.value,
        )

    # =========================================================================
    # Parameter-Driven Intervention Models
    # =========================================================================

    def _simulate_tree_canopy(
        self,
        hotspot: HotspotProfile,
        intensity: float,
        params: Optional[TreeCanopyScenarioParams] = None,
    ) -> SimulationResult:
        """
        Parameter-driven simulation of urban tree canopy expansion.

        Governing Variables:
        - Target Area ($A_{\\text{target}}$): Total hotspot surface area in $m^2$.
        - Eligible Area ($A_{\\text{eligible}}$): Permeable unbuilt ground ($A_{\\text{target}} \\times f_{\\text{plantable}}$).
        - Coverage Increase ($\\Delta \\text{coverage}$): $f_{\\text{plantable}} \\times \\text{intensity}$.
        - Canopy Foliage Density ($\\rho_{\\text{canopy}}$): Fractional crown leaf density factor [0.1 - 1.0].
        - Spatial Configuration ($\\mu_{\\text{spatial}}$): Dispersed (1.0x), Clustered (1.15x), Corridor (1.05x).
        - Tree Height / Maturity ($h$): Mature trees provide full crown spread; young trees are damped.
        """
        spec = self.config.get(InterventionType.TREE_CANOPY)
        p = params or TreeCanopyScenarioParams()

        baseline_lst = hotspot.baseline_lst_celsius
        area_m2 = hotspot.area_m2

        # 1. Spatial capacity & treated footprint
        eligible_fraction = hotspot.max_plantable_fraction
        eligible_area_m2 = area_m2 * eligible_fraction
        treated_fraction = eligible_fraction * intensity
        treated_area_m2 = area_m2 * treated_fraction

        if intensity == 0.0 or treated_area_m2 == 0.0:
            delta_lst = 0.0
            uncertainty_range = (0.0, 0.0)
            cost = 0.0
            spatial_mult = 1.0
            height_mult = 1.0
            effective_fvc_delta = 0.0
        else:
            # 2. Canopy density scaling (normalized relative to 0.80 reference benchmark)
            density_scaling = p.canopy_density / 0.80
            effective_fvc_delta = treated_fraction * density_scaling

            # 3. Spatial configuration microclimate multiplier
            if p.spatial_configuration == SpatialConfiguration.CLUSTERED:
                spatial_mult = 1.15 # Park cool island co-benefit
            elif p.spatial_configuration == SpatialConfiguration.LINEAR_CORRIDOR:
                spatial_mult = 1.05 # Street canyon shading effect
            else:
                spatial_mult = 1.00 # Dispersed baseline

            # 4. Tree height / maturity multiplier
            if p.tree_height_m is not None:
                if p.tree_height_m < 4.0:
                    height_mult = 0.70 + 0.30 * (p.tree_height_m / 4.0) # Young sapling reduced crown
                elif p.tree_height_m >= 8.0:
                    height_mult = 1.00 + 0.05 * min(2.0, (p.tree_height_m - 8.0) / 10.0) # Tall mature canopy
                else:
                    height_mult = 1.00
            else:
                height_mult = 1.00

            # 5. Baseline vegetation diminishing returns
            baseline_veg = hotspot.baseline_fvc
            saturation_factor = max(
                0.50,
                1.0 - (spec.diminishing_returns_factor * baseline_veg)
            )

            # 6. Parameterized Cooling Calculation
            base_cooling_coeff = spec.cooling_coefficient_celsius
            combined_multiplier = spatial_mult * height_mult * saturation_factor
            delta_lst = -(base_cooling_coeff * effective_fvc_delta * combined_multiplier)

            # 7. Uncertainty Bounds
            c_min, c_max = spec.cooling_uncertainty_range
            delta_lst_low = -(c_min * effective_fvc_delta * combined_multiplier)
            delta_lst_high = -(c_max * effective_fvc_delta * combined_multiplier)
            uncertainty_range = (
                round(min(delta_lst_high, delta_lst_low), 2),
                round(max(delta_lst_high, delta_lst_low), 2),
            )

            # 8. Cost Calculation
            cost = treated_area_m2 * spec.default_cost_per_m2

        projected_lst = baseline_lst + delta_lst

        # 9. Parameter Traceability & Metadata
        scenario_params_dict: Dict[str, Any] = {
            "target_area_m2": round(area_m2, 1),
            "eligible_plantable_area_m2": round(eligible_area_m2, 1),
            "eligible_plantable_fraction": round(eligible_fraction, 4),
            "treated_area_m2": round(treated_area_m2, 1),
            "coverage_increase_fraction": round(treated_fraction, 4),
            "canopy_density": p.canopy_density,
            "tree_height_m": p.tree_height_m,
            "spatial_configuration": p.spatial_configuration.value,
        }

        assumptions = list(spec.assumptions)
        assumptions.append(
            f"Scenario configured with {p.canopy_density:.0%} canopy density and "
            f"'{p.spatial_configuration.value}' spatial configuration."
        )
        assumptions.append(
            f"Treated area is constrained by physical permeable ground capacity "
            f"({eligible_fraction * 100:.1f}% maximum eligible area)."
        )
        if hotspot.is_mock:
            assumptions.append("Baseline hotspot thermal and spatial characteristics are derived from synthetic mock data.")

        limitations = [
            "LST represents radiative surface skin temperature and does not equal 2-m ambient air temperature or human thermal comfort.",
            "Cooling effectiveness depends on local tree species, canopy geometry, seasonal foliage, and soil water availability.",
            "Microclimatic wind advection and urban canyon shading interactions are not dynamically modeled in this scenario.",
        ]

        return SimulationResult(
            hotspot_id=hotspot.id,
            intervention=InterventionType.TREE_CANOPY,
            intensity=intensity,
            baseline_lst_celsius=round(baseline_lst, 2),
            projected_lst_celsius=round(projected_lst, 2),
            estimated_change_celsius=round(delta_lst, 2),
            cooling_uncertainty_range_celsius=uncertainty_range,
            eligible_area_m2=round(eligible_area_m2, 1),
            treated_area_m2=round(treated_area_m2, 1),
            treated_area_fraction=round(treated_fraction, 4),
            estimated_cost=round(cost, 2),
            currency=spec.unit_cost_currency,
            scenario_parameters=scenario_params_dict,
            evidence_level=spec.evidence_level,
            assumptions=assumptions,
            limitations=limitations,
            model_version=MODEL_VERSION_SIMULATION,
            status=ValueStatus.SIMULATED,
        )

    def _simulate_cool_roof(
        self,
        hotspot: HotspotProfile,
        intensity: float,
        params: Optional[CoolRoofScenarioParams] = None,
    ) -> SimulationResult:
        """
        Parameter-driven simulation of high-albedo cool roof deployment.

        Governing Variables:
        - Target Area ($A_{\\text{target}}$): Total hotspot surface area in $m^2$.
        - Eligible Roof Area ($A_{\\text{eligible}}$): Building rooftop footprint ($A_{\\text{target}} \\times f_{\\text{roof}}$).
        - Roof Coverage Converted ($f_{\\text{treated}}$): $f_{\\text{roof}} \\times \\text{intensity}$.
        - Baseline Albedo ($\\alpha_{\\text{base}}$): Solar reflectance of untreated roof (default 0.18).
        - Intervention Albedo ($\\alpha_{\\text{cool}}$): Solar reflectance of cool coating (default 0.68).
        - Net Albedo Increase ($\\Delta \\alpha$): $\\alpha_{\\text{cool}} - \\alpha_{\\text{base}}$.
        - Thermal Infrared Emissivity ($\\epsilon$): Surface emittance (default 0.90).
        """
        spec = self.config.get(InterventionType.COOL_ROOF)
        p = params or CoolRoofScenarioParams()

        baseline_lst = hotspot.baseline_lst_celsius
        area_m2 = hotspot.area_m2

        # 1. Spatial capacity & treated footprint
        eligible_fraction = hotspot.max_roof_fraction
        eligible_area_m2 = area_m2 * eligible_fraction
        treated_fraction = eligible_fraction * intensity
        treated_area_m2 = area_m2 * treated_fraction

        if intensity == 0.0 or treated_area_m2 == 0.0:
            delta_lst = 0.0
            uncertainty_range = (0.0, 0.0)
            cost = 0.0
            delta_albedo = 0.0
        else:
            # 2. Net albedo change
            delta_albedo = max(0.0, p.intervention_albedo - p.baseline_albedo)
            # Reference benchmark: delta_albedo = 0.50 corresponds to 1.0x baseline gradient
            albedo_scaling = delta_albedo / 0.50

            # 3. Thermal emissivity factor (reference: 0.90)
            emissivity_scaling = p.thermal_emissivity / 0.90

            # 4. Baseline roof density diminishing returns
            baseline_roof = hotspot.baseline_roof_fraction
            saturation_factor = max(
                0.60,
                1.0 - (spec.diminishing_returns_factor * baseline_roof)
            )

            # 5. Parameterized Cooling Calculation
            base_cooling_coeff = spec.cooling_coefficient_celsius
            combined_multiplier = albedo_scaling * emissivity_scaling * saturation_factor
            delta_lst = -(base_cooling_coeff * treated_fraction * combined_multiplier)

            # 6. Uncertainty Bounds
            c_min, c_max = spec.cooling_uncertainty_range
            delta_lst_low = -(c_min * treated_fraction * combined_multiplier)
            delta_lst_high = -(c_max * treated_fraction * combined_multiplier)
            uncertainty_range = (
                round(min(delta_lst_high, delta_lst_low), 2),
                round(max(delta_lst_high, delta_lst_low), 2),
            )

            # 7. Cost Calculation
            cost = treated_area_m2 * spec.default_cost_per_m2

        projected_lst = baseline_lst + delta_lst

        # 8. Parameter Traceability & Metadata
        scenario_params_dict: Dict[str, Any] = {
            "target_area_m2": round(area_m2, 1),
            "eligible_roof_area_m2": round(eligible_area_m2, 1),
            "eligible_roof_fraction": round(eligible_fraction, 4),
            "treated_roof_area_m2": round(treated_area_m2, 1),
            "treated_roof_fraction": round(treated_fraction, 4),
            "baseline_albedo": p.baseline_albedo,
            "intervention_albedo": p.intervention_albedo,
            "delta_albedo": round(delta_albedo, 3),
            "thermal_emissivity": p.thermal_emissivity,
        }

        assumptions = list(spec.assumptions)
        assumptions.append(
            f"Scenario configured with baseline albedo {p.baseline_albedo:.2f}, "
            f"cool roof albedo {p.intervention_albedo:.2f} (Δα = {delta_albedo:+.2f}), "
            f"and emissivity {p.thermal_emissivity:.2f}."
        )
        assumptions.append(
            f"Treated area is constrained by existing building rooftop coverage "
            f"({eligible_fraction * 100:.1f}% maximum eligible area)."
        )
        if hotspot.is_mock:
            assumptions.append("Baseline hotspot thermal and spatial characteristics are derived from synthetic mock data.")

        limitations = [
            "LST represents radiative surface skin temperature and does not equal 2-m ambient air temperature or human thermal comfort.",
            "Cooling effectiveness depends on roof slope, solar orientation, coating aging/soiling, and building insulation.",
            "Roof surface temperature reduction does not directly translate to identical 2-m air temperature cooling at pedestrian level.",
            "Building interior thermal comfort and air-conditioning energy reductions are not dynamically modeled in this scenario.",
        ]

        return SimulationResult(
            hotspot_id=hotspot.id,
            intervention=InterventionType.COOL_ROOF,
            intensity=intensity,
            baseline_lst_celsius=round(baseline_lst, 2),
            projected_lst_celsius=round(projected_lst, 2),
            estimated_change_celsius=round(delta_lst, 2),
            cooling_uncertainty_range_celsius=uncertainty_range,
            eligible_area_m2=round(eligible_area_m2, 1),
            treated_area_m2=round(treated_area_m2, 1),
            treated_area_fraction=round(treated_fraction, 4),
            estimated_cost=round(cost, 2),
            currency=spec.unit_cost_currency,
            scenario_parameters=scenario_params_dict,
            evidence_level=spec.evidence_level,
            assumptions=assumptions,
            limitations=limitations,
            model_version=MODEL_VERSION_SIMULATION,
            status=ValueStatus.SIMULATED,
        )


# Global default simulator instance
default_simulator = ScenarioSimulator()


def simulate_scenario(
    hotspot: HotspotProfile,
    intervention: Union[InterventionType, str],
    intensity: float,
    tree_params: Optional[TreeCanopyScenarioParams] = None,
    roof_params: Optional[CoolRoofScenarioParams] = None,
) -> SimulateResponse:
    """
    Convenience function for scenario simulation matching docs/API_CONTRACT.md.
    """
    return default_simulator.simulate_scenario(
        hotspot=hotspot,
        intervention=intervention,
        intensity=intensity,
        tree_params=tree_params,
        roof_params=roof_params,
    )
