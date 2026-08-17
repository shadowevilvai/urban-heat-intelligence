import numpy as np
from scipy.optimize import linprog
from typing import List, Dict, Any, Tuple
from .domain import InterventionType, ValueStatus
from .schemas import OptimizeRequest, OptimizeResponse, HotspotAllocationDetail
from .config import default_config
from .suitability import default_suitability_engine
from .simulator import default_simulator, SimulateRequest

class Optimizer:
    def __init__(self):
        pass

    def optimize(self, request: OptimizeRequest, hotspots_data: List[Tuple[str, Dict[str, Any], Dict[str, Any]]]) -> OptimizeResponse:
        """
        Executes deterministic resource-constrained optimization using SciPy HiGHS.
        hotspots_data is a list of tuples: (hotspot_id, p1_data, p2_data)
        """
        c_coeffs = []
        bounds = []
        cost_coeffs = []
        metadata = []
        
        # 1. Build the problem
        for hs_id, p1, p2 in hotspots_data:
            # Evaluate suitability
            suit_res = default_suitability_engine.evaluate(hs_id, p1, p2, request.interventions)
            
            for suit_item in suit_res.suitabilities:
                if suit_item.suitability_score <= 0.0:
                    continue # Skip unsuitable
                
                itype = InterventionType(suit_item.intervention)
                spec = default_config.get(itype)
                
                norm_suit = suit_item.suitability_score / 100.0
                expected_cooling_per_intensity = spec.cooling_coefficient_celsius * norm_suit
                
                # Objective coefficient (we minimize -benefit)
                # priority x suitability x expected_cooling x confidence
                # Confidence is treated as 1.0 for literature supported.
                priority = suit_item.heat_mitigation_need_score
                benefit = priority * suit_item.suitability_score * expected_cooling_per_intensity
                
                c_coeffs.append(-benefit)
                
                # Bounds: max intensity is 1.0
                bounds.append((0.0, 1.0))
                
                # Resource cost
                cost_coeffs.append(spec.unit_cost_resource_units)
                
                metadata.append({
                    "hs_id": hs_id,
                    "p1": p1,
                    "itype": itype,
                    "suit_factor": suit_item.suitability_score,
                    "spec": spec
                })
        
        # If no valid candidates, return zero allocation
        if not c_coeffs:
            return self._zero_result(request, hotspots_data)
            
        # 2. Solve LP
        A_ub = [cost_coeffs]
        b_ub = [request.resource_budget]
        
        res = linprog(
            c=c_coeffs,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method="highs"
        )
        
        status_msg = "optimal" if res.success else "infeasible"
        optimal_x = np.clip(res.x, 0.0, 1.0) if res.success else np.zeros(len(c_coeffs))
        
        # 3. Process results
        allocations = []
        total_resources_used = 0.0
        portfolio_objective_value = 0.0
        total_expected_cooling_celsius = 0.0
        cost_by_itype = {itype.value: 0.0 for itype in InterventionType}
        
        for idx, x_val in enumerate(optimal_x):
            if x_val < 0.001:
                continue
                
            meta = metadata[idx]
            used_resources = x_val * cost_coeffs[idx]
            total_resources_used += used_resources
            cost_by_itype[meta["itype"].value] += used_resources
            
            # The objective value contributed by this allocation
            portfolio_objective_value += (-c_coeffs[idx]) * x_val
            
            # Simulate exactly
            sim_req = SimulateRequest(
                hotspot_id=meta["hs_id"],
                intervention=meta["itype"].value,
                intensity=x_val
            )
            sim_res = default_simulator.simulate(sim_req, meta["p1"], meta["suit_factor"])
            
            expected_cooling = abs(sim_res.estimated_change_celsius)
            total_expected_cooling_celsius += expected_cooling
            
            allocations.append(HotspotAllocationDetail(
                hotspot_id=meta["hs_id"],
                intervention=meta["itype"].value,
                intensity_allocated=round(float(x_val), 4),
                resource_units_used=round(used_resources, 2),
                expected_cooling_celsius=round(expected_cooling, 2),
                scenario_lst_celsius=round(sim_res.scenario_lst_celsius, 2),
                limiting_constraints=["Budget constraint"] if total_resources_used >= request.resource_budget * 0.99 else ["Physical capacity constraint"]
            ))
            
        recommendations = []
        for k, v in cost_by_itype.items():
            if k in request.interventions:
                share = v / max(total_resources_used, 1.0)
                recommendations.append({k: round(share, 2)})
                
        return OptimizeResponse(
            status=status_msg,
            resource_budget=request.resource_budget,
            total_resources_used=round(total_resources_used, 2),
            portfolio_objective_value=round(portfolio_objective_value, 2),
            total_expected_cooling_celsius=round(total_expected_cooling_celsius, 2),
            recommendations=recommendations,
            hotspot_allocations=allocations,
            limiting_constraints=[f"Budget utilized: {total_resources_used:.1f} / {request.resource_budget:.1f}"],
            assumptions=["Optimization maximizes priority-weighted cooling subject to planning-unit resource constraints. Objective = Sum(Priority * Suitability * Expected Cooling)."]
        )

    def _zero_result(self, request: OptimizeRequest, hotspots_data: List[Any]) -> OptimizeResponse:
        recommendations = [{k: 0.0} for k in request.interventions]
        return OptimizeResponse(
            status="optimal",
            resource_budget=request.resource_budget,
            total_resources_used=0.0,
            portfolio_objective_value=0.0,
            total_expected_cooling_celsius=0.0,
            recommendations=recommendations,
            hotspot_allocations=[],
            limiting_constraints=["No valid candidates or zero budget."],
            assumptions=["Zero allocation generated."]
        )

default_optimizer = Optimizer()
