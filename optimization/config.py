"""
Configuration and literature parameter database for mitigation interventions.

SCIENTIFIC PRINCIPLES:
- No hardcoded universal constants; all coefficients are explicitly configurable and bounded.
- Every intervention links to literature citations and evidence classifications.
- Distinguishes MVP-required interventions (tree_canopy, cool_roof) from P1 candidates.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from optimization.domain import (
    CurrencyUnit,
    EvidenceLevel,
    InterventionSpecification,
    InterventionType,
)

# Model Version Constants
MODEL_VERSION_SIMULATION = "simulation-v0.1"
MODEL_VERSION_OPTIMIZER = "optimizer-v0.1"
MODEL_VERSION_SUITABILITY = "suitability-v0.1"

# Default Currency
DEFAULT_CURRENCY = CurrencyUnit.USD


# Default Intervention Registry with Literature Benchmarks
DEFAULT_INTERVENTIONS: Dict[InterventionType, InterventionSpecification] = {
    InterventionType.TREE_CANOPY: InterventionSpecification(
        intervention_type=InterventionType.TREE_CANOPY,
        name="Urban Tree Canopy",
        description="Planting and establishing urban shade trees on permeable ground and public rights-of-way.",
        cooling_mechanism="Solar radiation interception (shading) and latent heat flux through evapotranspiration.",
        unit_cost_currency=CurrencyUnit.USD,
        default_cost_per_m2=20.0,
        cost_range_per_m2=(12.0, 32.0),
        # Literature gradient: ~0.15°C to 0.25°C LST reduction per 10% FVC increase across pixel
        cooling_coefficient_celsius=2.0, # 2.0°C drop for 1.0 (100%) FVC conversion -> 0.20°C per 10%
        cooling_uncertainty_range=(1.5, 2.5),
        max_recommended_intensity=0.40,
        diminishing_returns_factor=0.50,
        evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
        citations=[
            "Oke, T. R. (1989). The micrometeorology of the urban forest. Phil. Trans. R. Soc. Lond. B, 324(1223), 335-349.",
            "Bowler, D. E., et al. (2010). Urban greening to cool towns and cities: A systematic review of the empirical evidence. Landscape and Urban Planning, 97(3), 147-155.",
            "Santamouris, M. (2014). Cooling the cities—a review of reflective and green roof mitigation technologies. Solar Energy, 103, 682-703.",
            "US EPA (2008). Reducing Urban Heat Islands: Compendium of Strategies - Trees and Vegetation.",
        ],
        assumptions=[
            "Trees require permeable soil and minimum rooting volume.",
            "Evapotranspiration cooling assumes adequate soil moisture availability.",
            "Full cooling benefits require tree canopy maturation (5-10 years post-planting).",
        ],
        is_mvp_ready=True,
    ),
    InterventionType.COOL_ROOF: InterventionSpecification(
        intervention_type=InterventionType.COOL_ROOF,
        name="Cool Roof Coating",
        description="Applying high-solar-reflectance (high-albedo) elastomeric or mineral coatings on building rooftops.",
        cooling_mechanism="Increases solar reflectance (albedo), reducing absorbed solar radiation and roof skin temperature.",
        unit_cost_currency=CurrencyUnit.USD,
        default_cost_per_m2=8.0,
        cost_range_per_m2=(5.0, 14.0),
        # Literature gradient: ~0.10°C to 0.20°C pixel LST reduction per 10% pixel-wide roof albedo conversion
        cooling_coefficient_celsius=1.5, # 1.5°C drop for 1.0 roof area conversion with delta_albedo=0.4 -> 0.15°C per 10%
        cooling_uncertainty_range=(1.0, 2.2),
        max_recommended_intensity=0.70,
        diminishing_returns_factor=0.30,
        evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
        citations=[
            "Akbari, H., et al. (2001). Cool surfaces and shade trees to reduce energy use and improve air quality in urban areas. Solar Energy, 70(3), 295-310.",
            "Sailor, D. J. (2008). A review of methods for estimating sensitivity of local heat island conditions to urban morphology and surface modifications. Environmental Research Letters, 3(4), 044008.",
            "Santamouris, M. (2014). Cooling the cities—a review of reflective and green roof mitigation technologies. Solar Energy, 103, 682-703.",
            "US EPA (2008). Reducing Urban Heat Islands: Compendium of Strategies - Cool Roofs.",
        ],
        assumptions=[
            "Roofs must be structurally intact and accessible for coating application.",
            "Albedo degradation over time (~10-20% loss over 3 years) requires periodic maintenance.",
            "Cooling effect is proportional to the fraction of total pixel area occupied by rooftops.",
        ],
        is_mvp_ready=True,
    ),
    # P1 Extension Candidate (Defined but marked is_mvp_ready=False)
    InterventionType.GREEN_ROOF: InterventionSpecification(
        intervention_type=InterventionType.GREEN_ROOF,
        name="Green Roof (Vegetated Roof)",
        description="Installing extensive vegetated sedum/shrub roof systems on reinforced building rooftops.",
        cooling_mechanism="Combines thermal mass insulation, albedo modification, and vegetative evapotranspiration.",
        unit_cost_currency=CurrencyUnit.USD,
        default_cost_per_m2=65.0,
        cost_range_per_m2=(45.0, 110.0),
        cooling_coefficient_celsius=1.8,
        cooling_uncertainty_range=(1.2, 2.4),
        max_recommended_intensity=0.50,
        diminishing_returns_factor=0.40,
        evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
        citations=[
            "Santamouris, M. (2014). Cooling the cities—a review of reflective and green roof mitigation technologies.",
        ],
        assumptions=[
            "Requires structural engineering verification of building roof load-bearing capacity.",
            "Irrigation infrastructure is required in arid climates.",
        ],
        is_mvp_ready=False,
    ),
}


class MitigationConfig:
    """
    Mutable configuration container that allows runtime calibration of intervention parameters.
    """
    def __init__(self, custom_interventions: Optional[Dict[InterventionType, InterventionSpecification]] = None):
        self._registry: Dict[InterventionType, InterventionSpecification] = {}
        if custom_interventions:
            self._registry.update(custom_interventions)
        else:
            # Deep copy defaults
            for k, v in DEFAULT_INTERVENTIONS.items():
                self._registry[k] = v.model_copy(deep=True)

    def get(self, intervention: InterventionType | str) -> InterventionSpecification:
        """Retrieve specification for an intervention type."""
        if isinstance(intervention, str):
            try:
                intervention = InterventionType(intervention)
            except ValueError:
                raise ValueError(
                    f"Unknown intervention type '{intervention}'. "
                    f"Supported types: {[t.value for t in InterventionType]}"
                )
        if intervention not in self._registry:
            raise KeyError(f"Intervention '{intervention}' not found in registry.")
        return self._registry[intervention]

    def list_interventions(self, mvp_only: bool = True) -> List[InterventionSpecification]:
        """List all available interventions."""
        if mvp_only:
            return [spec for spec in self._registry.values() if spec.is_mvp_ready]
        return list(self._registry.values())

    def update_parameter(
        self,
        intervention: InterventionType | str,
        cooling_coefficient_celsius: Optional[float] = None,
        default_cost_per_m2: Optional[float] = None,
        evidence_level: Optional[EvidenceLevel] = None,
    ) -> None:
        """Allows runtime scientific calibration of intervention parameters."""
        spec = self.get(intervention)
        update_dict = {}
        if cooling_coefficient_celsius is not None:
            if cooling_coefficient_celsius <= 0:
                raise ValueError("cooling_coefficient_celsius must be strictly positive.")
            update_dict["cooling_coefficient_celsius"] = cooling_coefficient_celsius
        if default_cost_per_m2 is not None:
            if default_cost_per_m2 <= 0:
                raise ValueError("default_cost_per_m2 must be strictly positive.")
            update_dict["default_cost_per_m2"] = default_cost_per_m2
        if evidence_level is not None:
            update_dict["evidence_level"] = evidence_level
        
        # Apply updates
        key = InterventionType(intervention) if isinstance(intervention, str) else intervention
        self._registry[key] = spec.model_copy(update=update_dict)


# Global default configuration instance
default_config = MitigationConfig()
