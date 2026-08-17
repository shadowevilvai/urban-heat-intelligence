from typing import Dict
from .domain import InterventionType, InterventionSpecification, EvidenceLevel

DEFAULT_INTERVENTIONS: Dict[InterventionType, InterventionSpecification] = {
    InterventionType.TREE_CANOPY: InterventionSpecification(
        intervention_type=InterventionType.TREE_CANOPY,
        name="Urban Tree Canopy",
        description="Planting and establishing urban shade trees on unbuilt, permeable ground near the sampling point.",
        cooling_coefficient_celsius=2.0,  # max potential drop
        cooling_uncertainty_range=(1.5, 2.5),
        unit_cost_resource_units=100.0,
        evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
        source_title="Urban greening to cool towns and cities: A systematic review",
        source_year=2010,
        source_url_or_doi="10.1016/j.landurbplan.2010.08.006",
        applicability="General urban areas with permeable ground.",
        uncertainty="High dependence on tree maturity, species, and soil moisture.",
        assumptions=[
            "PROXY: Assumes physical unbuilt area exists near the 450m sampling point.",
            "Cooling coefficient represents maximum localized scenario drop, not guaranteed ambient air temperature reduction.",
            "Evapotranspiration cooling assumes adequate soil moisture availability."
        ],
        limitations=[
            "Does not account for exact tree species, maturity, or localized wind flow.",
            "True plantable physical geometry is not observed; resource units and intensity are proxy measures."
        ]
    ),
    InterventionType.COOL_ROOF: InterventionSpecification(
        intervention_type=InterventionType.COOL_ROOF,
        name="Cool Roof Coating",
        description="Applying high-albedo coatings to structurally sound roofs near the sampling point.",
        cooling_coefficient_celsius=1.5,
        cooling_uncertainty_range=(1.0, 2.2),
        unit_cost_resource_units=40.0,
        evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
        source_title="Cooling the cities—a review of reflective and green roof mitigation technologies",
        source_year=2014,
        source_url_or_doi="10.1016/j.solener.2012.07.003",
        applicability="Built-up commercial/residential with low-albedo roofs.",
        uncertainty="Albedo degrades over time due to dust and weathering.",
        assumptions=[
            "PROXY: Assumes adequate built-up roof area exists near the 450m sampling point.",
            "Baseline roof albedo is assumed to be low (standard urban material).",
            "Cooling effect is highly localized to the surface radiative budget."
        ],
        limitations=[
            "Does not have verified roof polygons or structural load assessments.",
            "Albedo degradation over time is not dynamically modeled."
        ]
    )
}

class MitigationConfig:
    def __init__(self):
        self._registry = {k: v.model_copy() for k, v in DEFAULT_INTERVENTIONS.items()}
        
    def get(self, intervention: InterventionType) -> InterventionSpecification:
        if intervention not in self._registry:
            raise KeyError(f"Intervention '{intervention}' not found.")
        return self._registry[intervention]

default_config = MitigationConfig()
