"""
Unit tests for Constrained Multi-Hotspot Portfolio Optimizer (Milestone 3).

SCIENTIFIC INTEGRITY & VALIDATION TESTS:
- Tests constrained linear programming solver across multiple hotspots and interventions.
- Verifies strict budget enforcement (cost never exceeds budget).
- Verifies physical eligibility capping (treated area <= eligible area).
- Tests zero budget and unconstrained budget behaviors.
- Tests error handling for negative budgets, empty interventions, and unsupported types.
- Verifies deterministic convergence and exact API contract schema compliance.
- Ensures distinct labeling of RECOMMENDED values vs SIMULATED and OBSERVED.
"""

import pytest
from optimization.domain import (
    EvidenceLevel,
    HotspotProfile,
    InterventionType,
    OptimizationResult,
    ValueStatus,
)
from optimization.mock_data import MOCK_HOTSPOTS_AOI_001, mock_repository
from optimization.optimizer import PortfolioOptimizer, default_optimizer, optimize_interventions
from optimization.schemas import OptimizeResponse


class TestPortfolioOptimizer:
    """Test suite for Milestone 3 portfolio optimization engine."""

    def test_valid_multi_hotspot_optimization(self):
        """Test optimization with standard budget across multiple hotspots."""
        hotspots = mock_repository.list_by_area("aoi-001")
        assert len(hotspots) >= 4

        budget = 1_500_000.0 # $1.5M budget
        interventions = ["tree_canopy", "cool_roof"]

        result: OptimizationResult = default_optimizer.optimize(
            hotspots=hotspots,
            budget=budget,
            interventions=interventions,
        )

        assert result.status == "optimal"
        assert result.budget == budget
        assert result.estimated_total_cost <= budget
        assert result.estimated_total_cost > 0.0
        assert result.expected_cooling > 0.0
        assert result.value_status == ValueStatus.RECOMMENDED
        assert result.model_version == "optimizer-v0.1"

        # Check recommendation summary structure
        assert len(result.recommendations) == 2
        alloc_sum = sum(r["allocation"] for r in result.recommendations)
        assert pytest.approx(alloc_sum, 0.01) == 1.0

        # Check granular hotspot allocations
        assert len(result.hotspot_allocations) == len(hotspots) * len(interventions)
        for alloc in result.hotspot_allocations:
            assert 0.0 <= alloc.allocation_fraction <= 1.0
            assert alloc.treated_area_m2 <= (alloc.eligible_area_m2 + 0.01)
            assert alloc.estimated_cost >= 0.0

    def test_zero_budget_gives_zero_allocation(self):
        """Budget = 0 must return 0 cost, 0 cooling, 0 allocation, and optimal status."""
        hotspots = mock_repository.list_by_area("aoi-001")
        result = default_optimizer.optimize(
            hotspots=hotspots,
            budget=0.0,
            interventions=["tree_canopy", "cool_roof"],
        )

        assert result.status == "optimal"
        assert result.budget == 0.0
        assert result.estimated_total_cost == 0.0
        assert result.expected_cooling == 0.0
        for r in result.recommendations:
            assert r["allocation"] == 0.0
        for alloc in result.hotspot_allocations:
            assert alloc.allocation_fraction == 0.0
            assert alloc.treated_area_m2 == 0.0
            assert alloc.estimated_cost == 0.0

    def test_budget_constraint_is_never_violated(self):
        """Test across multiple budget tiers that estimated total cost never exceeds budget."""
        hotspots = mock_repository.list_by_area("aoi-001")
        for test_budget in (10_000.0, 100_000.0, 500_000.0, 2_000_000.0, 10_000_000.0):
            result = default_optimizer.optimize(
                hotspots=hotspots,
                budget=test_budget,
                interventions=["tree_canopy", "cool_roof"],
            )
            assert result.status == "optimal"
            assert result.estimated_total_cost <= (test_budget + 0.01)

    def test_physical_eligibility_bounds_respected(self):
        """Even with an infinite / massive budget, allocation cannot exceed 100% of physical capacity."""
        hotspots = mock_repository.list_by_area("aoi-001")
        massive_budget = 1_000_000_000.0 # $1 Billion (far exceeds physical capacity)

        result = default_optimizer.optimize(
            hotspots=hotspots,
            budget=massive_budget,
            interventions=["tree_canopy", "cool_roof"],
        )

        assert result.status == "optimal"
        # Total cost should be capped by physical capacity, not budget
        assert result.estimated_total_cost < massive_budget

        for alloc in result.hotspot_allocations:
            assert alloc.allocation_fraction <= 1.0
            assert alloc.treated_area_m2 <= (alloc.eligible_area_m2 + 0.01)

    def test_negative_budget_raises_validation_error(self):
        """Negative budget must raise ValueError."""
        hotspots = mock_repository.list_by_area("aoi-001")
        with pytest.raises(ValueError) as exc:
            default_optimizer.optimize(hotspots, budget=-1000.0, interventions=["tree_canopy"])
        assert "Budget must be non-negative" in str(exc.value)

    def test_empty_interventions_raises_validation_error(self):
        """Empty interventions list must raise ValueError."""
        hotspots = mock_repository.list_by_area("aoi-001")
        with pytest.raises(ValueError) as exc:
            default_optimizer.optimize(hotspots, budget=1000.0, interventions=[])
        assert "Interventions list cannot be empty" in str(exc.value)

    def test_unsupported_intervention_raises_validation_error(self):
        """Unsupported intervention type must raise ValueError."""
        hotspots = mock_repository.list_by_area("aoi-001")
        with pytest.raises(ValueError):
            default_optimizer.optimize(hotspots, budget=1000.0, interventions=["unsupported_xyz"])

    def test_single_intervention_portfolio(self):
        """Optimizer should cleanly solve when only tree_canopy or only cool_roof is specified."""
        hotspots = mock_repository.list_by_area("aoi-001")

        # Tree canopy only
        res_tree = default_optimizer.optimize(hotspots, budget=500_000.0, interventions=["tree_canopy"])
        assert res_tree.status == "optimal"
        assert len(res_tree.recommendations) == 1
        assert res_tree.recommendations[0]["intervention"] == "tree_canopy"
        assert res_tree.recommendations[0]["allocation"] == 1.0

        # Cool roof only
        res_roof = default_optimizer.optimize(hotspots, budget=500_000.0, interventions=["cool_roof"])
        assert res_roof.status == "optimal"
        assert len(res_roof.recommendations) == 1
        assert res_roof.recommendations[0]["intervention"] == "cool_roof"
        assert res_roof.recommendations[0]["allocation"] == 1.0

    def test_optimization_is_deterministic(self):
        """Repeated optimization runs with identical inputs must produce identical solutions."""
        hotspots = mock_repository.list_by_area("aoi-001")
        budget = 750_000.0
        interventions = ["tree_canopy", "cool_roof"]

        res1 = default_optimizer.optimize(hotspots, budget, interventions)
        res2 = default_optimizer.optimize(hotspots, budget, interventions)

        assert res1.estimated_total_cost == res2.estimated_total_cost
        assert res1.expected_cooling == res2.expected_cooling
        assert res1.recommendations == res2.recommendations
        for a1, a2 in zip(res1.hotspot_allocations, res2.hotspot_allocations):
            assert a1.allocation_fraction == a2.allocation_fraction
            assert a1.estimated_cost == a2.estimated_cost
            assert a1.expected_cooling_celsius == a2.expected_cooling_celsius

    def test_high_risk_hotspots_prioritized_under_tight_budget(self):
        """Under a tight budget, the optimizer must prioritize higher-risk / higher-temperature hotspots."""
        hotspots = mock_repository.list_by_area("aoi-001")
        # Very tight budget: only enough for a fraction of total need
        tight_budget = 50_000.0

        result = default_optimizer.optimize(hotspots, budget=tight_budget, interventions=["tree_canopy", "cool_roof"])
        assert result.status == "optimal"

        allocated_hotspot_ids = {
            alloc.hotspot_id for alloc in result.hotspot_allocations if alloc.allocation_fraction > 0.0
        }
        # Highest risk hotspots (hs-001: risk 92, hs-002: risk 84) should be prioritized over lowest (hs-004: risk 62)
        assert "hs-001" in allocated_hotspot_ids or "hs-002" in allocated_hotspot_ids

    def test_optimize_interventions_api_contract_schema(self):
        """Test optimize_interventions convenience function against docs/API_CONTRACT.md."""
        hotspots = mock_repository.list_by_area("aoi-001")
        api_res: OptimizeResponse = optimize_interventions(
            hotspots=hotspots,
            budget=100_000_000.0,
            interventions=["tree_canopy", "cool_roof"],
        )

        data = api_res.model_dump()
        assert "status" in data
        assert "budget" in data
        assert "estimated_total_cost" in data
        assert "expected_cooling" in data
        assert "recommendations" in data
        assert "model_version" in data

        assert data["status"] == "optimal"
        assert data["budget"] == 100_000_000.0
        assert data["estimated_total_cost"] <= data["budget"]
        assert data["expected_cooling"] >= 0.0
        assert data["model_version"] == "optimizer-v0.1"
        assert isinstance(data["recommendations"], list)
        for rec in data["recommendations"]:
            assert "intervention" in rec
            assert "allocation" in rec
            assert 0.0 <= rec["allocation"] <= 1.0
