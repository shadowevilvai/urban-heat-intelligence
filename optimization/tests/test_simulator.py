"""
Unit tests for Scenario Simulation Engine (Milestone 2).

SCIENTIFIC INTEGRITY & VALIDATION TESTS:
- Tests tree canopy and cool roof simulation logic.
- Verifies physical boundary constraints (intensity bounds, treated vs eligible area).
- Verifies explicit 'simulated' status labeling and distinction from baseline.
- Asserts presence of uncertainty intervals, literature evidence, assumptions, and limitations.
- Verifies deterministic reproducibility and resilience to missing optional environmental fields.
"""

import pytest
from optimization.domain import (
    EvidenceLevel,
    HotspotProfile,
    InterventionType,
    ValueStatus,
)
from optimization.mock_data import MOCK_HOTSPOTS_AOI_001, mock_repository
from optimization.schemas import SimulateResponse
from optimization.simulator import ScenarioSimulator, default_simulator, simulate_scenario


class TestScenarioSimulator:
    """Test suite for Milestone 2 simulation engine."""

    def test_valid_tree_canopy_simulation(self):
        """Test standard tree canopy simulation on a valid hotspot."""
        hs = mock_repository.get_by_id("hs-001") # Baseline LST = 43.5°C, Plantable = 5%
        assert hs is not None

        result = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.5)

        assert result.hotspot_id == hs.id
        assert result.intervention == InterventionType.TREE_CANOPY
        assert result.intensity == 0.5
        assert result.baseline_lst_celsius == hs.baseline_lst_celsius
        # Cooling must be strictly negative
        assert result.estimated_change_celsius < 0.0
        # Projected LST = Baseline LST + Delta LST
        assert pytest.approx(result.projected_lst_celsius, 0.01) == (
            result.baseline_lst_celsius + result.estimated_change_celsius
        )
        assert result.status == ValueStatus.SIMULATED
        assert result.evidence_level == EvidenceLevel.LITERATURE_SUPPORTED

    def test_valid_cool_roof_simulation(self):
        """Test standard cool roof simulation on a valid hotspot."""
        hs = mock_repository.get_by_id("hs-002") # Baseline LST = 45.2°C, Roof = 60%
        assert hs is not None

        result = default_simulator.simulate(hs, "cool_roof", intensity=0.7)

        assert result.hotspot_id == hs.id
        assert result.intervention == InterventionType.COOL_ROOF
        assert result.intensity == 0.7
        assert result.baseline_lst_celsius == hs.baseline_lst_celsius
        assert result.estimated_change_celsius < 0.0
        assert pytest.approx(result.projected_lst_celsius, 0.01) == (
            result.baseline_lst_celsius + result.estimated_change_celsius
        )
        assert result.status == ValueStatus.SIMULATED

    def test_intensity_zero_gives_zero_impact(self):
        """Intensity = 0.0 must yield 0 cooling, projected == baseline, 0 treated area, and 0 cost."""
        hs = mock_repository.get_by_id("hs-003")
        assert hs is not None

        for itype in (InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF):
            result = default_simulator.simulate(hs, itype, intensity=0.0)

            assert result.intensity == 0.0
            assert result.estimated_change_celsius == 0.0
            assert result.projected_lst_celsius == result.baseline_lst_celsius
            assert result.treated_area_m2 == 0.0
            assert result.treated_area_fraction == 0.0
            assert result.estimated_cost == 0.0
            assert result.cooling_uncertainty_range_celsius == (0.0, 0.0)
            assert result.status == ValueStatus.SIMULATED

    def test_intensity_one_respects_physical_eligibility_bounds(self):
        """At intensity = 1.0, treated area must equal total eligible area and not exceed it."""
        hs = mock_repository.get_by_id("hs-004")
        assert hs is not None

        # Tree canopy
        tree_res = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=1.0)
        assert pytest.approx(tree_res.treated_area_m2, 0.1) == tree_res.eligible_area_m2
        assert pytest.approx(tree_res.treated_area_m2, 0.1) == (hs.area_m2 * hs.max_plantable_fraction)
        assert tree_res.treated_area_m2 <= hs.area_m2

        # Cool roof
        roof_res = default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=1.0)
        assert pytest.approx(roof_res.treated_area_m2, 0.1) == roof_res.eligible_area_m2
        assert pytest.approx(roof_res.treated_area_m2, 0.1) == (hs.area_m2 * hs.max_roof_fraction)
        assert roof_res.treated_area_m2 <= hs.area_m2

    def test_invalid_intensity_negative_raises_error(self):
        """Intensity < 0.0 must raise ValueError."""
        hs = mock_repository.get_by_id("hs-001")
        with pytest.raises(ValueError) as exc:
            default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=-0.1)
        assert "Intensity must be between 0.0 and 1.0" in str(exc.value)

    def test_invalid_intensity_greater_than_one_raises_error(self):
        """Intensity > 1.0 must raise ValueError."""
        hs = mock_repository.get_by_id("hs-001")
        with pytest.raises(ValueError) as exc:
            default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=1.05)
        assert "Intensity must be between 0.0 and 1.0" in str(exc.value)

    def test_unsupported_intervention_raises_error(self):
        """Unrecognized intervention string must raise ValueError."""
        hs = mock_repository.get_by_id("hs-001")
        with pytest.raises(ValueError):
            default_simulator.simulate(hs, "non_existent_intervention", intensity=0.5)

    def test_projected_lst_strictly_derived_from_baseline_plus_change(self):
        """Projected LST must equal baseline_lst + estimated_change for all hotspots."""
        for hs in MOCK_HOTSPOTS_AOI_001:
            for itype in (InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF):
                for intensity in (0.2, 0.5, 0.8, 1.0):
                    res = default_simulator.simulate(hs, itype, intensity=intensity)
                    expected_proj = round(res.baseline_lst_celsius + res.estimated_change_celsius, 2)
                    assert pytest.approx(res.projected_lst_celsius, 0.02) == expected_proj

    def test_treated_area_never_exceeds_eligible_area(self):
        """For any intensity in [0, 1], treated area <= eligible area."""
        for hs in MOCK_HOTSPOTS_AOI_001:
            for itype in (InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF):
                for intensity in (0.0, 0.25, 0.5, 0.75, 1.0):
                    res = default_simulator.simulate(hs, itype, intensity=intensity)
                    assert res.treated_area_m2 <= (res.eligible_area_m2 + 0.01)

    def test_cost_scales_linearly_with_treated_area(self):
        """Cost must scale consistently with treated surface area."""
        hs = mock_repository.get_by_id("hs-003")
        assert hs is not None

        spec_tree = default_simulator.config.get(InterventionType.TREE_CANOPY)
        spec_roof = default_simulator.config.get(InterventionType.COOL_ROOF)

        res_tree_half = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.5)
        res_tree_full = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=1.0)

        assert pytest.approx(res_tree_half.estimated_cost * 2, 0.1) == res_tree_full.estimated_cost
        assert pytest.approx(res_tree_half.estimated_cost, 0.1) == (
            res_tree_half.treated_area_m2 * spec_tree.default_cost_per_m2
        )

        res_roof = default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=0.6)
        assert pytest.approx(res_roof.estimated_cost, 0.1) == (
            res_roof.treated_area_m2 * spec_roof.default_cost_per_m2
        )

    def test_simulated_output_explicitly_marked_status_simulated(self):
        """Verify that all simulation results have status == 'simulated' and never 'observed'."""
        hs = mock_repository.get_by_id("hs-005")
        res = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.4)

        assert res.status == ValueStatus.SIMULATED
        assert res.status.value == "simulated"
        assert res.status != ValueStatus.OBSERVED

    def test_assumptions_and_evidence_metadata_present(self):
        """Ensure evidence level, academic citations, assumptions, and limitations are returned."""
        hs = mock_repository.get_by_id("hs-001")
        for itype in (InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF):
            res = default_simulator.simulate(hs, itype, intensity=0.5)

            assert res.evidence_level == EvidenceLevel.LITERATURE_SUPPORTED
            assert len(res.assumptions) >= 2
            assert len(res.limitations) >= 2
            assert any("radiative surface skin temperature" in lim.lower() for lim in res.limitations)
            assert res.model_version == "simulation-v0.1"

    def test_uncertainty_range_exposed_and_ordered(self):
        """Uncertainty interval must contain [min_delta, max_delta] where min <= max."""
        hs = mock_repository.get_by_id("hs-002")
        for itype in (InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF):
            res = default_simulator.simulate(hs, itype, intensity=0.5)

            u_low, u_high = res.cooling_uncertainty_range_celsius
            # Both bounds should be negative or zero (cooling)
            assert u_low <= 0.0
            assert u_high <= 0.0
            assert u_low <= u_high
            # Estimated change should fall within or close to the bounds
            assert u_low <= res.estimated_change_celsius <= u_high

    def test_missing_optional_environmental_fields_do_not_crash(self):
        """Hotspot with all optional fields as None must simulate seamlessly."""
        minimal_hs = HotspotProfile(
            id="hs-minimal-01",
            latitude=19.10,
            longitude=72.88,
            area_m2=80000.0,
            baseline_lst_celsius=41.2,
            baseline_fvc=0.10,
            baseline_roof_fraction=0.30,
            baseline_impervious_fraction=0.50,
            max_plantable_fraction=0.20,
            max_roof_fraction=0.30,
            risk_score=75.0,
            # All optional fields omitted (None)
            lst_anomaly_c=None,
            ndvi_mean=None,
            ndbi_mean=None,
            ndwi_mean=None,
            land_cover_class=None,
        )

        res_tree = default_simulator.simulate(minimal_hs, InterventionType.TREE_CANOPY, intensity=0.3)
        res_roof = default_simulator.simulate(minimal_hs, InterventionType.COOL_ROOF, intensity=0.3)

        assert res_tree.estimated_change_celsius < 0.0
        assert res_roof.estimated_change_celsius < 0.0

    def test_simulation_deterministic(self):
        """Repeated simulations on the same hotspot must yield identical floating point results."""
        hs = mock_repository.get_by_id("hs-001")
        for itype in (InterventionType.TREE_CANOPY, InterventionType.COOL_ROOF):
            res1 = default_simulator.simulate(hs, itype, intensity=0.45)
            res2 = default_simulator.simulate(hs, itype, intensity=0.45)

            assert res1.estimated_change_celsius == res2.estimated_change_celsius
            assert res1.projected_lst_celsius == res2.projected_lst_celsius
            assert res1.treated_area_m2 == res2.treated_area_m2
            assert res1.estimated_cost == res2.estimated_cost
            assert res1.cooling_uncertainty_range_celsius == res2.cooling_uncertainty_range_celsius

    def test_simulate_scenario_matches_api_contract_schema(self):
        """Test simulate_scenario convenience function against docs/API_CONTRACT.md schema."""
        hs = mock_repository.get_by_id("hs-001")
        api_res: SimulateResponse = simulate_scenario(hs, "tree_canopy", 0.2)

        data = api_res.model_dump()
        assert "baseline_lst_celsius" in data
        assert "predicted_lst_celsius" in data
        assert "estimated_change_celsius" in data
        assert "evidence_level" in data
        assert "assumptions" in data
        assert "model_version" in data
        assert "status" in data

        assert data["status"] == "simulated"
        assert data["baseline_lst_celsius"] == hs.baseline_lst_celsius
        assert data["estimated_change_celsius"] < 0.0
        assert data["evidence_level"] == "literature_supported"
        assert data["model_version"] == "simulation-v0.1"


class TestParameterDrivenSimulation:
    """Test suite specifically validating P5 parameter-driven microclimatic and surface behavior."""

    def test_tree_canopy_density_scaling(self):
        """Higher crown leaf foliage density must yield proportionally greater cooling."""
        hs = mock_repository.get_by_id("hs-003")
        assert hs is not None

        from optimization.domain import TreeCanopyScenarioParams

        dense_params = TreeCanopyScenarioParams(canopy_density=0.95)
        sparse_params = TreeCanopyScenarioParams(canopy_density=0.50)

        res_dense = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.5, tree_params=dense_params)
        res_sparse = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.5, tree_params=sparse_params)

        # Dense foliage cooling should be strictly greater than sparse foliage (more negative change)
        assert res_dense.estimated_change_celsius < res_sparse.estimated_change_celsius
        assert abs(res_dense.estimated_change_celsius) > abs(res_sparse.estimated_change_celsius)
        assert res_dense.scenario_parameters["canopy_density"] == 0.95
        assert res_sparse.scenario_parameters["canopy_density"] == 0.50

    def test_tree_canopy_spatial_configuration_scaling(self):
        """Clustered park planting should yield greater microclimate cooling than dispersed planting."""
        hs = mock_repository.get_by_id("hs-004")
        assert hs is not None

        from optimization.domain import SpatialConfiguration, TreeCanopyScenarioParams

        clustered_params = TreeCanopyScenarioParams(spatial_configuration=SpatialConfiguration.CLUSTERED)
        dispersed_params = TreeCanopyScenarioParams(spatial_configuration=SpatialConfiguration.DISPERSED)

        res_clustered = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.5, tree_params=clustered_params)
        res_dispersed = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.5, tree_params=dispersed_params)

        assert abs(res_clustered.estimated_change_celsius) > abs(res_dispersed.estimated_change_celsius)
        assert res_clustered.scenario_parameters["spatial_configuration"] == "clustered"
        assert res_dispersed.scenario_parameters["spatial_configuration"] == "dispersed"

    def test_tree_canopy_height_maturity_scaling(self):
        """Mature trees (e.g. 12m) provide full crown spread vs young saplings (e.g. 2m)."""
        hs = mock_repository.get_by_id("hs-005")
        assert hs is not None

        from optimization.domain import TreeCanopyScenarioParams

        mature_params = TreeCanopyScenarioParams(tree_height_m=12.0)
        sapling_params = TreeCanopyScenarioParams(tree_height_m=2.0)

        res_mature = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.6, tree_params=mature_params)
        res_sapling = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.6, tree_params=sapling_params)

        assert abs(res_mature.estimated_change_celsius) > abs(res_sapling.estimated_change_celsius)
        assert res_mature.scenario_parameters["tree_height_m"] == 12.0
        assert res_sapling.scenario_parameters["tree_height_m"] == 2.0

    def test_cool_roof_albedo_delta_scaling(self):
        """Higher albedo increase (Δα) must yield proportionally greater cooling."""
        hs = mock_repository.get_by_id("hs-002")
        assert hs is not None

        from optimization.domain import CoolRoofScenarioParams

        # High performance coating: α=0.85 (Δα = 0.85 - 0.15 = 0.70)
        high_albedo_params = CoolRoofScenarioParams(baseline_albedo=0.15, intervention_albedo=0.85)
        # Moderate performance coating: α=0.50 (Δα = 0.50 - 0.15 = 0.35)
        mod_albedo_params = CoolRoofScenarioParams(baseline_albedo=0.15, intervention_albedo=0.50)

        res_high = default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=0.7, roof_params=high_albedo_params)
        res_mod = default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=0.7, roof_params=mod_albedo_params)

        assert abs(res_high.estimated_change_celsius) > abs(res_mod.estimated_change_celsius)
        assert res_high.scenario_parameters["delta_albedo"] == 0.70
        assert res_mod.scenario_parameters["delta_albedo"] == 0.35

    def test_cool_roof_emissivity_scaling(self):
        """Higher thermal emissivity must yield greater radiative cooling."""
        hs = mock_repository.get_by_id("hs-001")
        assert hs is not None

        from optimization.domain import CoolRoofScenarioParams

        high_emissivity = CoolRoofScenarioParams(thermal_emissivity=0.95)
        low_emissivity = CoolRoofScenarioParams(thermal_emissivity=0.60)

        res_high = default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=0.5, roof_params=high_emissivity)
        res_low = default_simulator.simulate(hs, InterventionType.COOL_ROOF, intensity=0.5, roof_params=low_emissivity)

        assert abs(res_high.estimated_change_celsius) > abs(res_low.estimated_change_celsius)
        assert res_high.scenario_parameters["thermal_emissivity"] == 0.95
        assert res_low.scenario_parameters["thermal_emissivity"] == 0.60

    def test_scenario_parameters_traceability_dictionary(self):
        """Verify that target area, eligible area, treated area, and optical parameters are in the result dictionary."""
        hs = mock_repository.get_by_id("hs-001")
        res = default_simulator.simulate(hs, InterventionType.TREE_CANOPY, intensity=0.4)

        params_dict = res.scenario_parameters
        assert "target_area_m2" in params_dict
        assert "eligible_plantable_area_m2" in params_dict
        assert "treated_area_m2" in params_dict
        assert "coverage_increase_fraction" in params_dict
        assert "canopy_density" in params_dict
        assert "spatial_configuration" in params_dict
        assert params_dict["target_area_m2"] == hs.area_m2

