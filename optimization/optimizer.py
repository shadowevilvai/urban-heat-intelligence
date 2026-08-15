"""
Constrained Multi-Hotspot Portfolio Optimization Engine.

SCIENTIFIC & MATHEMATICAL FORMULATION:
- Models heat mitigation resource allocation as a Linear Program (LP) solved via SciPy HiGHS.
- Objective: Maximize total risk-weighted, area-weighted cooling impact across multiple hotspots.
- Decision Variables: x_{ij} in [0.0, 1.0] representing the fraction of physically eligible area
  allocated to intervention j on hotspot i.
- Constraints:
  1. Total Budget: sum_{i, j} (Area_{i, eligible, j} * Cost_j) * x_{ij} <= Budget
  2. Physical Eligibility: 0.0 <= x_{ij} <= 1.0 for all (i, j)
  3. Non-negativity: x_{ij} >= 0.0
- Re-evaluates final scenario cooling using the validated ScenarioSimulator to ensure exact
  consistency with non-linear diminishing returns and physical morphology.
- Produces deterministic, explainable recommendations strictly distinguishing RECOMMENDED
  decisions from SIMULATED scenario projections and OBSERVED sensor data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import numpy as np
from scipy.optimize import linprog

from optimization.config import MitigationConfig, default_config, MODEL_VERSION_OPTIMIZER
from optimization.domain import (
    EvidenceLevel,
    HotspotAllocationDetail,
    HotspotProfile,
    InterventionSpecification,
    InterventionType,
    OptimizationResult,
    ValueStatus,
)
from optimization.schemas import InterventionAllocation, OptimizeResponse
from optimization.simulator import ScenarioSimulator, default_simulator


class PortfolioOptimizer:
    """
    Constrained optimization solver allocating mitigation interventions across multiple hotspots.
    """

    def __init__(
        self,
        config: Optional[MitigationConfig] = None,
        simulator: Optional[ScenarioSimulator] = None,
    ):
        self.config = config or default_config
        self.simulator = simulator or default_simulator

    def optimize(
        self,
        hotspots: List[HotspotProfile],
        budget: float,
        interventions: List[Union[InterventionType, str]],
    ) -> OptimizationResult:
        """
        Solve constrained portfolio optimization across candidate hotspots.

        Args:
            hotspots: List of validated HotspotProfile instances.
            budget: Total available municipal/project budget (must be >= 0.0).
            interventions: List of allowed intervention types (e.g. ['tree_canopy', 'cool_roof']).

        Returns:
            OptimizationResult: Structured optimization outcome with portfolio summary and
                               granular per-hotspot allocation details.

        Raises:
            ValueError: If budget is negative, interventions list is empty, or an intervention is unsupported.
        """
        # 1. Validate Input Budget
        if not isinstance(budget, (int, float)):
            raise ValueError(f"Budget must be a numeric value, got {type(budget).__name__}.")
        if budget < 0.0:
            raise ValueError(f"Budget must be non-negative, got {budget}.")

        # 2. Validate & Resolve Interventions List
        if not interventions:
            raise ValueError("Interventions list cannot be empty.")

        resolved_interventions: List[InterventionType] = []
        for item in interventions:
            if isinstance(item, str):
                try:
                    itype = InterventionType(item.strip().lower())
                except ValueError:
                    raise ValueError(
                        f"Unsupported intervention '{item}'. "
                        f"Supported types: {[t.value for t in InterventionType]}"
                    )
            else:
                itype = item
            if itype not in resolved_interventions:
                resolved_interventions.append(itype)

        # 3. Handle Edge Cases: Zero Budget or Empty Hotspot List
        if budget == 0.0 or not hotspots:
            return self._create_zero_budget_result(hotspots, budget, resolved_interventions)

        # 4. Build Decision Variables & Linear Programming Matrices
        # Variables x_{ij} indexed by k = i * M + j
        N = len(hotspots)
        M = len(resolved_interventions)
        num_vars = N * M

        c_vector = np.zeros(num_vars, dtype=float)
        cost_coefficients = np.zeros(num_vars, dtype=float)
        bounds = []

        var_metadata = [] # Stores (hotspot, itype, eligible_area_m2, unit_cost, max_cooling)

        for i, hs in enumerate(hotspots):
            for j, itype in enumerate(resolved_interventions):
                k = i * M + j
                spec = self.config.get(itype)

                # Determine eligible area for this intervention
                if itype == InterventionType.TREE_CANOPY:
                    eligible_fraction = hs.max_plantable_fraction
                elif itype == InterventionType.COOL_ROOF:
                    eligible_fraction = hs.max_roof_fraction
                else:
                    eligible_fraction = 0.0

                eligible_area_m2 = hs.area_m2 * eligible_fraction
                unit_cost = spec.default_cost_per_m2
                var_cost = eligible_area_m2 * unit_cost

                cost_coefficients[k] = var_cost
                bounds.append((0.0, 1.0)) # Physical eligibility: x_{ij} in [0.0, 1.0]

                if eligible_area_m2 > 0.0:
                    # Simulate marginal cooling at full deployment (x = 1.0)
                    sim_full = self.simulator.simulate(hs, itype, intensity=1.0)
                    delta_lst_full = abs(sim_full.estimated_change_celsius)

                    # Risk & Thermal Need Weight:
                    # Prioritizes high-risk, high-temperature hotspots
                    risk_weight = (hs.risk_score / 100.0) * max(0.5, hs.baseline_lst_celsius / 40.0)
                    
                    # Benefit metric: risk_weight * area_m2 * delta_lst
                    marginal_benefit = risk_weight * hs.area_m2 * delta_lst_full
                else:
                    delta_lst_full = 0.0
                    marginal_benefit = 0.0

                # Linprog minimizes c^T x, so we negate benefit to maximize impact
                c_vector[k] = -marginal_benefit

                var_metadata.append({
                    "hotspot": hs,
                    "itype": itype,
                    "spec": spec,
                    "eligible_area_m2": eligible_area_m2,
                    "eligible_fraction": eligible_fraction,
                    "unit_cost": unit_cost,
                    "var_cost": var_cost,
                    "delta_lst_full": delta_lst_full,
                })

        # 5. Solve Constrained Linear Program via SciPy HiGHS
        A_ub = np.array([cost_coefficients]) # 1 x num_vars
        b_ub = np.array([budget])            # Budget upper bound

        total_potential_cost = float(np.sum(cost_coefficients))

        # If total potential cost is zero (no eligible areas on any hotspot)
        if total_potential_cost == 0.0:
            return self._create_zero_budget_result(hotspots, budget, resolved_interventions)

        solver_res = linprog(
            c=c_vector,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method="highs",
        )

        if not solver_res.success:
            # Fallback if solver encounters an issue
            return OptimizationResult(
                status="infeasible",
                budget=float(budget),
                estimated_total_cost=0.0,
                expected_cooling=0.0,
                recommendations=[{"intervention": t.value, "allocation": 0.0} for t in resolved_interventions],
                hotspot_allocations=[],
                limiting_constraints=["Optimization solver could not find a feasible solution."],
                evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
                assumptions=["Solver failed to converge on the constraint set."],
                model_version=MODEL_VERSION_OPTIMIZER,
                value_status=ValueStatus.RECOMMENDED,
            )

        optimal_x = np.clip(solver_res.x, 0.0, 1.0)

        # 6. Post-Process Allocations & Exact Scenario Simulation
        hotspot_allocations: List[HotspotAllocationDetail] = []
        cost_by_intervention: Dict[InterventionType, float] = {t: 0.0 for t in resolved_interventions}
        total_estimated_cost = 0.0
        total_area_weighted_cooling = 0.0
        total_aoi_area = sum(h.area_m2 for h in hotspots)

        binding_constraints = []
        budget_utilized_fraction = float(np.dot(cost_coefficients, optimal_x)) / max(1.0, budget)

        if budget_utilized_fraction >= 0.999:
            binding_constraints.append(
                f"Budget constraint binding: {budget_utilized_fraction * 100:.1f}% of budget allocated."
            )
        else:
            binding_constraints.append(
                f"Budget unconstrained: all physically eligible intervention opportunities fully satisfied "
                f"({budget_utilized_fraction * 100:.1f}% budget required)."
            )

        for k, meta in enumerate(var_metadata):
            alloc_frac = float(optimal_x[k])
            hs = meta["hotspot"]
            itype = meta["itype"]
            spec = meta["spec"]
            eligible_area_m2 = meta["eligible_area_m2"]
            unit_cost = meta["unit_cost"]

            treated_area_m2 = eligible_area_m2 * alloc_frac
            item_cost = treated_area_m2 * unit_cost

            total_estimated_cost += item_cost
            cost_by_intervention[itype] += item_cost

            # Exact simulation of final allocation
            if alloc_frac > 0.0 and treated_area_m2 > 0.0:
                sim_res = self.simulator.simulate(hs, itype, intensity=alloc_frac)
                exp_cooling = abs(sim_res.estimated_change_celsius)
                proj_lst = sim_res.projected_lst_celsius
            else:
                exp_cooling = 0.0
                proj_lst = hs.baseline_lst_celsius

            total_area_weighted_cooling += hs.area_m2 * exp_cooling

            # Limiting constraints per allocation
            alloc_constraints = []
            if eligible_area_m2 == 0.0:
                alloc_constraints.append("Zero physical eligibility on this hotspot.")
            elif alloc_frac >= 0.999:
                alloc_constraints.append("Physical capacity fully saturated (100% of eligible area treated).")
            elif alloc_frac > 0.0:
                alloc_constraints.append("Budget-limited partial allocation.")
            else:
                alloc_constraints.append("Deprioritized relative to higher-impact hotspots.")

            hotspot_allocations.append(
                HotspotAllocationDetail(
                    hotspot_id=hs.id,
                    hotspot_name=hs.name,
                    intervention=itype,
                    allocation_fraction=round(alloc_frac, 4),
                    treated_area_m2=round(treated_area_m2, 1),
                    eligible_area_m2=round(eligible_area_m2, 1),
                    estimated_cost=round(item_cost, 2),
                    expected_cooling_celsius=round(exp_cooling, 2),
                    projected_lst_celsius=round(proj_lst, 2),
                    risk_score=hs.risk_score,
                    limiting_constraints=alloc_constraints,
                )
            )

        # 7. Portfolio-Level Recommendations (Matches docs/API_CONTRACT.md schema)
        recommendations: List[Dict[str, Any]] = []
        for itype in resolved_interventions:
            itype_cost = cost_by_intervention[itype]
            if total_estimated_cost > 0.0:
                share = itype_cost / total_estimated_cost
            else:
                share = 0.0
            recommendations.append({
                "intervention": itype.value,
                "allocation": round(share, 2),
            })

        area_weighted_avg_cooling = (
            total_area_weighted_cooling / max(1.0, total_aoi_area)
            if total_aoi_area > 0 else 0.0
        )

        assumptions = [
            "Portfolio optimization solved via exact Linear Programming (SciPy HiGHS solver).",
            "Objective maximizes risk-weighted, area-weighted Land Surface Temperature mitigation.",
            "Decision variables represent recommended investment fractions subject to budget and physical area limits.",
            "All cooling values are simulated projections derived from parameterized literature response models.",
        ]

        return OptimizationResult(
            status="optimal",
            budget=float(budget),
            estimated_total_cost=round(total_estimated_cost, 2),
            expected_cooling=round(area_weighted_avg_cooling, 2),
            recommendations=recommendations,
            hotspot_allocations=hotspot_allocations,
            limiting_constraints=binding_constraints,
            evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
            assumptions=assumptions,
            model_version=MODEL_VERSION_OPTIMIZER,
            value_status=ValueStatus.RECOMMENDED,
        )

    def optimize_area(
        self,
        hotspots: List[HotspotProfile],
        budget: float,
        interventions: List[Union[InterventionType, str]],
    ) -> OptimizeResponse:
        """
        Execute optimization and return response matching docs/API_CONTRACT.md schema.
        """
        result = self.optimize(hotspots, budget, interventions)
        return OptimizeResponse(
            status=result.status,
            budget=result.budget,
            estimated_total_cost=round(result.estimated_total_cost, 2),
            expected_cooling=round(result.expected_cooling, 2),
            recommendations=[
                InterventionAllocation(
                    intervention=r["intervention"],
                    allocation=r["allocation"],
                )
                for r in result.recommendations
            ],
            model_version=result.model_version,
        )

    def _create_zero_budget_result(
        self,
        hotspots: List[HotspotProfile],
        budget: float,
        interventions: List[InterventionType],
    ) -> OptimizationResult:
        """Create empty/zero allocation result when budget is 0 or hotspots list is empty."""
        recommendations = [{"intervention": t.value, "allocation": 0.0} for t in interventions]
        hotspot_allocations = []

        for hs in hotspots:
            for itype in interventions:
                hotspot_allocations.append(
                    HotspotAllocationDetail(
                        hotspot_id=hs.id,
                        hotspot_name=hs.name,
                        intervention=itype,
                        allocation_fraction=0.0,
                        treated_area_m2=0.0,
                        eligible_area_m2=0.0,
                        estimated_cost=0.0,
                        expected_cooling_celsius=0.0,
                        projected_lst_celsius=hs.baseline_lst_celsius,
                        risk_score=hs.risk_score,
                        limiting_constraints=["Zero budget allocated."],
                    )
                )

        return OptimizationResult(
            status="optimal",
            budget=float(budget),
            estimated_total_cost=0.0,
            expected_cooling=0.0,
            recommendations=recommendations,
            hotspot_allocations=hotspot_allocations,
            limiting_constraints=["Zero budget: no interventions funded."],
            evidence_level=EvidenceLevel.LITERATURE_SUPPORTED,
            assumptions=["No financial resources allocated to mitigation."],
            model_version=MODEL_VERSION_OPTIMIZER,
            value_status=ValueStatus.RECOMMENDED,
        )


# Global default optimizer instance
default_optimizer = PortfolioOptimizer()


def optimize_interventions(
    hotspots: List[HotspotProfile],
    budget: float,
    interventions: List[Union[InterventionType, str]],
) -> OptimizeResponse:
    """
    Convenience function for portfolio optimization matching docs/API_CONTRACT.md.
    """
    return default_optimizer.optimize_area(hotspots, budget, interventions)
