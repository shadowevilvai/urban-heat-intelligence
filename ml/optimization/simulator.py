from typing import Dict, Any
from .domain import InterventionType, ValueStatus
from .schemas import SimulateRequest, SimulateResponse
from .config import default_config

class Simulator:
    def __init__(self):
        pass
        
    def simulate(self, request: SimulateRequest, p1_data: Dict[str, Any], suitability_factor: float) -> SimulateResponse:
        """
        Calculates planning-level scenario estimate for a 450m sampling point.
        """
        itype = InterventionType(request.intervention)
        spec = default_config.get(itype)
        
        observed_lst = p1_data.get("lst_c", 35.0)
        
        # Calculate expected cooling
        # We explicitly rely on the suitability_factor (0.0 - 1.0) to bound the theoretical max cooling
        # because physical treatment area is not observed.
        normalized_suitability = max(0.0, min(1.0, suitability_factor / 100.0))
        
        estimated_change = -1.0 * spec.cooling_coefficient_celsius * request.intensity * normalized_suitability
        scenario_lst = observed_lst + estimated_change
        
        uncertainty_vals = [
            -1.0 * spec.cooling_uncertainty_range[0] * request.intensity * normalized_suitability,
            -1.0 * spec.cooling_uncertainty_range[1] * request.intensity * normalized_suitability
        ]
        
        uncertainty = [min(uncertainty_vals), max(uncertainty_vals)]
        
        return SimulateResponse(
            observed_lst_celsius=round(observed_lst, 2),
            estimated_change_celsius=round(estimated_change, 2),
            scenario_lst_celsius=round(scenario_lst, 2),
            intervention_type=itype.value,
            intensity=request.intensity,
            suitability_factor=round(normalized_suitability, 2),
            cooling_coefficient=spec.cooling_coefficient_celsius,
            cooling_uncertainty_range=[round(u, 2) for u in uncertainty],
            evidence_level=spec.evidence_level,
            source_title=spec.source_title,
            source_year=spec.source_year,
            source_url_or_doi=spec.source_url_or_doi,
            applicability=spec.applicability,
            uncertainty=spec.uncertainty,
            assumptions=spec.assumptions,
            limitations=spec.limitations,
            status=ValueStatus.SIMULATED
        )

default_simulator = Simulator()
