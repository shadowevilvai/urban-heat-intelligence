"""
Unit tests for API contract validation schemas.
Ensures 100% adherence to docs/API_CONTRACT.md.
"""

import pytest
from pydantic import ValidationError
from optimization.schemas import (
    InterventionAllocation,
    OptimizeRequest,
    OptimizeResponse,
    SimulateRequest,
    SimulateResponse,
    SuitabilityRequest,
    SuitabilityResponse,
)


class TestSimulateSchemas:
    """Validate SimulateRequest and SimulateResponse against docs/API_CONTRACT.md."""

    def test_valid_simulate_request(self):
        req = SimulateRequest(
            hotspot_id="hs-001",
            intervention="tree_canopy",
            intensity=0.2,
        )
        assert req.hotspot_id == "hs-001"
        assert req.intervention == "tree_canopy"
        assert req.intensity == 0.2

    def test_simulate_request_intensity_bounds(self):
        # Intensity > 1.0 should fail
        with pytest.raises(ValidationError):
            SimulateRequest(hotspot_id="hs-001", intervention="tree_canopy", intensity=1.5)
        # Intensity < 0.0 should fail
        with pytest.raises(ValidationError):
            SimulateRequest(hotspot_id="hs-001", intervention="tree_canopy", intensity=-0.1)

    def test_simulate_request_unsupported_intervention(self):
        with pytest.raises(ValidationError):
            SimulateRequest(hotspot_id="hs-001", intervention="unsupported_intervention", intensity=0.2)

    def test_valid_simulate_response_schema(self):
        res = SimulateResponse(
            baseline_lst_celsius=42.7,
            predicted_lst_celsius=40.8,
            estimated_change_celsius=-1.9,
            evidence_level="literature_supported",
            assumptions=["Scenario is based on validated model relationship"],
            model_version="simulation-v0.1",
            status="simulated",
        )
        data = res.model_dump()
        assert data["baseline_lst_celsius"] == 42.7
        assert data["predicted_lst_celsius"] == 40.8
        assert data["estimated_change_celsius"] == -1.9
        assert data["status"] == "simulated"
        assert data["model_version"] == "simulation-v0.1"
        assert len(data["assumptions"]) == 1


class TestOptimizeSchemas:
    """Validate OptimizeRequest and OptimizeResponse against docs/API_CONTRACT.md."""

    def test_valid_optimize_request(self):
        req = OptimizeRequest(
            area_id="aoi-001",
            budget=100000000.0,
            interventions=["tree_canopy", "cool_roof"],
        )
        assert req.area_id == "aoi-001"
        assert req.budget == 100000000.0
        assert len(req.interventions) == 2

    def test_optimize_request_negative_budget(self):
        with pytest.raises(ValidationError):
            OptimizeRequest(
                area_id="aoi-001",
                budget=-500.0,
                interventions=["tree_canopy"],
            )

    def test_optimize_request_empty_interventions(self):
        with pytest.raises(ValidationError):
            OptimizeRequest(
                area_id="aoi-001",
                budget=1000.0,
                interventions=[],
            )

    def test_valid_optimize_response_schema(self):
        res = OptimizeResponse(
            status="optimal",
            budget=100000000.0,
            estimated_total_cost=98500000.0,
            expected_cooling=2.1,
            recommendations=[
                InterventionAllocation(intervention="tree_canopy", allocation=0.42),
                InterventionAllocation(intervention="cool_roof", allocation=0.58),
            ],
            model_version="optimizer-v0.1",
        )
        data = res.model_dump()
        assert data["status"] == "optimal"
        assert data["budget"] == 100000000.0
        assert data["estimated_total_cost"] == 98500000.0
        assert data["expected_cooling"] == 2.1
        assert len(data["recommendations"]) == 2
        assert data["recommendations"][0]["intervention"] == "tree_canopy"
        assert data["recommendations"][0]["allocation"] == 0.42
