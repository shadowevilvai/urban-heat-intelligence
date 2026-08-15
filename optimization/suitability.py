"""
Multi-Criteria Suitability Scoring Engine for Heat Mitigation Interventions.

SCIENTIFIC METHODOLOGY:
- Evaluates spatial feasibility, thermal mitigation deficit, and cost-effectiveness.
- Strictly enforces physical morphology constraints (e.g. tree canopy requires unbuilt permeable ground;
  cool roofs require existing roof structures).
- Produces transparent explainability breakdowns (limiting factors, advantages, citations).
- Categorizes suitability into HIGH, MEDIUM, LOW, or UNSUITABLE.
"""

from __future__ import annotations

from typing import List, Optional
from optimization.config import MitigationConfig, default_config, MODEL_VERSION_SUITABILITY
from optimization.domain import (
    EvidenceLevel,
    HotspotProfile,
    InterventionSpecification,
    InterventionType,
    SuitabilityAssessment,
    SuitabilityCategory,
    ValueStatus,
)


class SuitabilityScorer:
    """
    Evaluates physical and thermal suitability of mitigation interventions for given hotspots.
    """

    def __init__(self, config: Optional[MitigationConfig] = None):
        self.config = config or default_config

    def evaluate_intervention(
        self,
        hotspot: HotspotProfile,
        intervention_type: InterventionType | str,
    ) -> SuitabilityAssessment:
        """
        Evaluate suitability of a single intervention type on a specific hotspot.
        """
        spec = self.config.get(intervention_type)
        itype = spec.intervention_type

        # 1. Determine Physical Feasibility & Available Area
        available_fraction, max_area_m2 = self._calculate_physical_capacity(hotspot, itype)

        # 2. Compute Multi-Criteria Sub-Scores
        spatial_score, spatial_limits = self._compute_spatial_feasibility(hotspot, itype, available_fraction)
        need_score, need_advantages = self._compute_mitigation_need(hotspot)
        cost_score = self._compute_cost_efficiency(spec)

        # 3. Handle Hard Physical Infeasibility
        limiting_factors = list(spatial_limits)
        advantages = list(need_advantages)

        if available_fraction <= 0.01 or spatial_score < 5.0:
            composite_score = 0.0
            category = SuitabilityCategory.UNSUITABLE
            limiting_factors.append(
                f"Physical area constraint: insufficient suitable surface area ({available_fraction * 100:.1f}% available)."
            )
        else:
            # Weighted multi-criteria aggregation:
            # 50% Spatial Capacity + 35% Thermal/Risk Need + 15% Cost-Effectiveness
            w_spatial = 0.50
            w_need = 0.35
            w_cost = 0.15

            raw_score = (
                w_spatial * spatial_score +
                w_need * need_score +
                w_cost * cost_score
            )

            # Spatial feasibility gating: if spatial feasibility is low (< 25), clamp maximum composite score
            if spatial_score < 25.0:
                raw_score = min(raw_score, spatial_score * 1.5)

            # Apply saturation damping if baseline coverage is already high
            saturation_multiplier = self._compute_saturation_factor(hotspot, itype)
            composite_score = max(0.0, min(100.0, raw_score * saturation_multiplier))

            if composite_score >= 70.0:
                category = SuitabilityCategory.HIGH
            elif composite_score >= 40.0:
                category = SuitabilityCategory.MEDIUM
            elif composite_score >= 10.0:
                category = SuitabilityCategory.LOW
            else:
                category = SuitabilityCategory.UNSUITABLE

        # Compile specific advantages
        if available_fraction >= 0.25:
            advantages.append(f"Abundant physical surface capacity ({available_fraction * 100:.1f}% area available).")
        if hotspot.risk_score >= 75.0:
            advantages.append(f"High population risk score ({hotspot.risk_score:.0f}/100) maximizes public health impact.")

        # Assumptions & Citations
        assumptions = list(spec.assumptions)
        if hotspot.is_mock:
            assumptions.append("Assessment evaluated on synthetic/mock baseline hotspot profile.")

        return SuitabilityAssessment(
            hotspot_id=hotspot.id,
            intervention=itype,
            suitability_score=round(composite_score, 1),
            category=category,
            available_area_fraction=round(available_fraction, 4),
            max_feasible_area_m2=round(max_area_m2, 1),
            estimated_unit_cost=spec.default_cost_per_m2,
            spatial_feasibility_score=round(spatial_score, 1),
            heat_mitigation_need_score=round(need_score, 1),
            cost_efficiency_score=round(cost_score, 1),
            limiting_factors=limiting_factors,
            advantages=advantages,
            assumptions=assumptions,
            evidence_level=spec.evidence_level,
            model_version=MODEL_VERSION_SUITABILITY,
            status=ValueStatus.SIMULATED,
        )

    def evaluate_hotspot(
        self,
        hotspot: HotspotProfile,
        interventions: Optional[List[InterventionType | str]] = None,
    ) -> List[SuitabilityAssessment]:
        """
        Evaluate suitability of all requested (or all MVP) interventions on a hotspot.
        """
        if interventions is None:
            # Default to MVP interventions
            target_types = [spec.intervention_type for spec in self.config.list_interventions(mvp_only=True)]
        else:
            target_types = [
                InterventionType(i) if isinstance(i, str) else i
                for i in interventions
            ]

        results = [
            self.evaluate_intervention(hotspot, itype)
            for itype in target_types
        ]
        # Sort by suitability score descending
        results.sort(key=lambda x: x.suitability_score, reverse=True)
        return results

    # =========================================================================
    # Internal Evaluation Helpers
    # =========================================================================

    def _calculate_physical_capacity(
        self,
        hotspot: HotspotProfile,
        intervention_type: InterventionType,
    ) -> tuple[float, float]:
        """Determine available fraction and absolute surface area in m^2."""
        if intervention_type == InterventionType.TREE_CANOPY:
            frac = hotspot.max_plantable_fraction
        elif intervention_type in (InterventionType.COOL_ROOF, InterventionType.GREEN_ROOF):
            frac = hotspot.max_roof_fraction
        elif intervention_type == InterventionType.COOL_PAVEMENT:
            frac = hotspot.baseline_impervious_fraction * 0.50 # Road/pavement fraction estimate
        elif intervention_type == InterventionType.SHADE_STRUCTURE:
            frac = hotspot.baseline_impervious_fraction * 0.20 # Walkway/plaza fraction estimate
        else:
            frac = 0.0

        max_area_m2 = hotspot.area_m2 * frac
        return frac, max_area_m2

    def _compute_spatial_feasibility(
        self,
        hotspot: HotspotProfile,
        intervention_type: InterventionType,
        available_fraction: float,
    ) -> tuple[float, List[str]]:
        """Calculate spatial capacity score (0 - 100) and identify spatial limiting factors."""
        limiting_factors = []

        if intervention_type == InterventionType.TREE_CANOPY:
            # Threshold: 20% plantable ground yields 100 spatial score
            min_threshold = 0.03
            ideal_threshold = 0.25
            if available_fraction < min_threshold:
                score = 0.0
                limiting_factors.append(
                    f"Critically low permeable ground space ({available_fraction * 100:.1f}% vs minimum {min_threshold * 100:.0f}% required)."
                )
            else:
                score = min(100.0, (available_fraction / ideal_threshold) * 100.0)
                if available_fraction < 0.10:
                    limiting_factors.append(
                        f"Constrained unbuilt ground area ({available_fraction * 100:.1f}%) limits large-canopy tree deployment."
                    )

        elif intervention_type in (InterventionType.COOL_ROOF, InterventionType.GREEN_ROOF):
            # Threshold: 35% building roof area yields 100 spatial score
            min_threshold = 0.05
            ideal_threshold = 0.35
            if available_fraction < min_threshold:
                score = 0.0
                limiting_factors.append(
                    f"Low building rooftop coverage ({available_fraction * 100:.1f}% vs minimum {min_threshold * 100:.0f}% required)."
                )
            else:
                score = min(100.0, (available_fraction / ideal_threshold) * 100.0)

        else:
            score = min(100.0, (available_fraction / 0.20) * 100.0)

        return score, limiting_factors

    def _compute_mitigation_need(self, hotspot: HotspotProfile) -> tuple[float, List[str]]:
        """Calculate thermal deficit and vulnerability need score (0 - 100)."""
        advantages = []

        # Baseline LST component: 32°C reference baseline up to 48°C extreme hotspot
        t_ref = 32.0
        t_max = 48.0
        thermal_norm = max(0.0, min(1.0, (hotspot.baseline_lst_celsius - t_ref) / (t_max - t_ref)))
        thermal_score = thermal_norm * 100.0

        # Risk component (0 - 100)
        risk_score = hotspot.risk_score

        # Composite Need: 50% thermal intensity + 50% ML risk score
        composite_need = 0.50 * thermal_score + 0.50 * risk_score

        if hotspot.baseline_lst_celsius >= 40.0:
            advantages.append(
                f"Severe baseline thermal anomaly ({hotspot.baseline_lst_celsius:.1f}°C LST) indicates urgent cooling need."
            )

        return composite_need, advantages

    def _compute_cost_efficiency(self, spec: InterventionSpecification) -> float:
        """
        Compute cost efficiency rating (0 - 100) based on cooling gradient per unit cost.
        """
        # Baseline reference: $10/m^2 with 1.5°C cooling = 100 efficiency
        efficiency_ratio = spec.cooling_coefficient_celsius / max(1.0, spec.default_cost_per_m2)
        # Normalize: ratio of 0.15 -> 80 score, ratio of 0.20 -> 100 score
        score = min(100.0, (efficiency_ratio / 0.18) * 100.0)
        return max(20.0, score)

    def _compute_saturation_factor(
        self,
        hotspot: HotspotProfile,
        intervention_type: InterventionType,
    ) -> float:
        """
        Compute damping multiplier if hotspot already has high coverage of the same intervention type.
        """
        if intervention_type == InterventionType.TREE_CANOPY:
            # If baseline FVC is already > 40%, marginal benefit diminishes
            if hotspot.baseline_fvc > 0.40:
                return max(0.50, 1.0 - (hotspot.baseline_fvc - 0.40) * 1.2)
        return 1.0


# Global default scorer instance
default_scorer = SuitabilityScorer()
