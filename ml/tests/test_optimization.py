import pytest
from ml.optimization.domain import InterventionType, ValueStatus, SuitabilityCategory
from ml.optimization.schemas import SuitabilityRequest, SimulateRequest, OptimizeRequest
from ml.optimization.suitability import default_suitability_engine
from ml.optimization.simulator import default_simulator
from ml.optimization.optimizer import default_optimizer
from ml.optimization.config import default_config

def get_mock_p1_p2(context="urban_heat", lst=40.0, ndvi=0.2, ndbi=0.2, lc="Built-up", risk=80.0):
    p1 = {
        "lst_c": lst,
        "lst_anomaly_c": 2.0,
        "ndvi_mean": ndvi,
        "ndbi_mean": ndbi,
        "ndwi_mean": -0.2,
        "land_cover_class": lc
    }
    p2 = {
        "risk_score": risk,
        "vulnerability_score": 60.0,
        "hotspot_context": context,
        "risk_category": "high"
    }
    return p1, p2

# ==========================================
# SUITABILITY TESTS
# ==========================================

def test_water_exclusion():
    p1, p2 = get_mock_p1_p2(context="water")
    res = default_suitability_engine.evaluate("hs-1", p1, p2)
    for s in res.suitabilities:
        assert s.suitability_score == 0.0
        assert s.category == SuitabilityCategory.UNSUITABLE
        assert "Water bodies strictly exclude" in s.limiting_factors[0]

def test_industrial_mining_handling():
    p1, p2 = get_mock_p1_p2(context="industrial_mining_candidate", ndbi=0.5, lc="Bare ground")
    res = default_suitability_engine.evaluate("hs-1", p1, p2)
    
    for s in res.suitabilities:
        if s.intervention == "tree_canopy":
            assert s.category == SuitabilityCategory.UNSUITABLE
            assert s.suitability_score == 0.0
        elif s.intervention == "cool_roof":
            assert s.category == SuitabilityCategory.UNSUITABLE
            assert s.suitability_score == 0.0
            assert "No verified built-up/roof evidence" in s.limiting_factors[0]

def test_industrial_mining_handling_with_builtup_evidence():
    p1, p2 = get_mock_p1_p2(context="industrial_mining_candidate", ndbi=0.2, lc="Built-up")
    res = default_suitability_engine.evaluate("hs-1", p1, p2, ["cool_roof"])
    s = res.suitabilities[0]
    # Should evaluate normally but cap/categorize based on score
    assert s.suitability_score > 0.0
    assert s.category in [SuitabilityCategory.MEDIUM, SuitabilityCategory.LOW]
    assert any("requires verification" in f for f in s.limiting_factors)

def test_urban_heat_suitability():
    p1, p2 = get_mock_p1_p2(context="urban_heat")
    res = default_suitability_engine.evaluate("hs-1", p1, p2)
    assert any(s.suitability_score > 0 for s in res.suitabilities)

def test_terrestrial_other_handling():
    p1, p2 = get_mock_p1_p2(context="terrestrial_other")
    res = default_suitability_engine.evaluate("hs-1", p1, p2)
    assert any(s.category != SuitabilityCategory.UNSUITABLE for s in res.suitabilities)

def test_high_ndvi_behavior():
    p1, p2 = get_mock_p1_p2(ndvi=0.6, ndbi=-0.1, lc="Vegetation")
    res = default_suitability_engine.evaluate("hs-1", p1, p2, ["tree_canopy"])
    assert any("High NDVI" in f for f in res.suitabilities[0].limiting_factors)

def test_high_ndbi_behavior():
    p1, p2 = get_mock_p1_p2(ndvi=0.1, ndbi=0.5, lc="Built-up")
    res = default_suitability_engine.evaluate("hs-1", p1, p2, ["tree_canopy"])
    assert any("High NDBI" in f for f in res.suitabilities[0].limiting_factors)
    
def test_missing_environmental_values():
    p1 = {}
    p2 = {"hotspot_context": "urban_heat"}
    res = default_suitability_engine.evaluate("hs-1", p1, p2)
    assert res.observed_lst_celsius == 0.0

# ==========================================
# SIMULATOR TESTS
# ==========================================

def test_simulator_intensity_zero():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=0.0)
    res = default_simulator.simulate(req, p1, suitability_factor=80.0)
    assert res.estimated_change_celsius == 0.0
    assert res.scenario_lst_celsius == 40.0

def test_simulator_intensity_one():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=1.0)
    res = default_simulator.simulate(req, p1, suitability_factor=100.0)
    assert res.estimated_change_celsius == -2.0 # tree_canopy max cooling is 2.0

def test_simulator_suitability_bounds():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=1.0)
    res_zero = default_simulator.simulate(req, p1, suitability_factor=0.0)
    assert res_zero.estimated_change_celsius == 0.0
    
    res_one = default_simulator.simulate(req, p1, suitability_factor=100.0)
    assert res_one.estimated_change_celsius == -2.0

def test_simulator_negative_cooling_direction():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=0.5)
    res = default_simulator.simulate(req, p1, suitability_factor=80.0)
    assert res.estimated_change_celsius < 0.0  # Cooling must be negative

def test_coefficient_provenance():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=0.5)
    res = default_simulator.simulate(req, p1, suitability_factor=80.0)
    assert res.source_title
    assert res.source_year > 0
    assert res.evidence_level

def test_uncertainty_ordering():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=0.5)
    res = default_simulator.simulate(req, p1, suitability_factor=80.0)
    # Ensure min <= max
    assert res.cooling_uncertainty_range[0] <= res.cooling_uncertainty_range[1]

def test_deterministic_simulator():
    p1, _ = get_mock_p1_p2(lst=40.0)
    req = SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=0.5)
    res1 = default_simulator.simulate(req, p1, suitability_factor=80.0)
    res2 = default_simulator.simulate(req, p1, suitability_factor=80.0)
    assert res1.estimated_change_celsius == res2.estimated_change_celsius

# ==========================================
# OPTIMIZER TESTS
# ==========================================

def test_optimizer_zero_budget():
    p1, p2 = get_mock_p1_p2()
    req = OptimizeRequest(hotspot_ids=["hs-1"], resource_budget=0.0, interventions=["tree_canopy"])
    res = default_optimizer.optimize(req, [("hs-1", p1, p2)])
    assert res.total_resources_used == 0.0
    for alloc in res.hotspot_allocations:
        assert alloc.intensity_allocated == 0.0

def test_optimizer_insufficient_budget():
    p1, p2 = get_mock_p1_p2()
    req = OptimizeRequest(hotspot_ids=["hs-1", "hs-2"], resource_budget=50.0, interventions=["tree_canopy"]) # tree needs 100
    res = default_optimizer.optimize(req, [("hs-1", p1, p2), ("hs-2", p1, p2)])
    assert res.total_resources_used <= 50.0 + 0.001
    allocations = [a.intensity_allocated for a in res.hotspot_allocations]
    assert sum(allocations) <= 0.501 # 50 / 100

def test_optimizer_budget_never_exceeded():
    p1, p2 = get_mock_p1_p2()
    req = OptimizeRequest(hotspot_ids=[f"hs-{i}" for i in range(10)], resource_budget=150.0, interventions=["tree_canopy"])
    hs_data = [(f"hs-{i}", p1, p2) for i in range(10)]
    res = default_optimizer.optimize(req, hs_data)
    assert res.total_resources_used <= 150.0 + 0.001

def test_optimizer_all_ineligible():
    p1, p2 = get_mock_p1_p2(context="water")
    req = OptimizeRequest(hotspot_ids=["hs-1"], resource_budget=150.0, interventions=["tree_canopy"])
    res = default_optimizer.optimize(req, [("hs-1", p1, p2)])
    assert res.total_resources_used == 0.0
    assert len(res.hotspot_allocations) == 0

def test_optimizer_water_hotspot():
    p1, p2 = get_mock_p1_p2(context="water")
    req = OptimizeRequest(hotspot_ids=["hs-1"], resource_budget=150.0, interventions=["tree_canopy"])
    res = default_optimizer.optimize(req, [("hs-1", p1, p2)])
    assert len(res.hotspot_allocations) == 0

def test_optimizer_objective_separate_from_celsius():
    p1, p2 = get_mock_p1_p2()
    req = OptimizeRequest(hotspot_ids=["hs-1"], resource_budget=100.0, interventions=["tree_canopy"])
    res = default_optimizer.optimize(req, [("hs-1", p1, p2)])
    
    assert res.portfolio_objective_value > 0.0
    assert res.total_expected_cooling_celsius > 0.0
    assert res.portfolio_objective_value != res.total_expected_cooling_celsius
    
    sum_cooling = sum([a.expected_cooling_celsius for a in res.hotspot_allocations])
    assert abs(res.total_expected_cooling_celsius - sum_cooling) < 0.01

# ==========================================
# VALUE STATUS TESTS
# ==========================================

def test_value_status():
    p1, p2 = get_mock_p1_p2()
    suit_res = default_suitability_engine.evaluate("hs-1", p1, p2)
    assert suit_res.status == ValueStatus.DERIVED
    
    sim_res = default_simulator.simulate(SimulateRequest(hotspot_id="hs-1", intervention="tree_canopy", intensity=0.5), p1, 80.0)
    assert sim_res.status == ValueStatus.SIMULATED
    
    opt_res = default_optimizer.optimize(OptimizeRequest(hotspot_ids=["hs-1"], resource_budget=100.0, interventions=["tree_canopy"]), [("hs-1", p1, p2)])
    assert opt_res.value_status == ValueStatus.RECOMMENDED
