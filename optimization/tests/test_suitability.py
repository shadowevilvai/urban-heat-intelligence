"""
Unit tests for multi-criteria suitability scoring engine.
"""

import pytest
from optimization.domain import (
    HotspotProfile,
    InterventionType,
    SuitabilityCategory,
    ValueStatus,
)
from optimization.mock_data import MOCK_HOTSPOTS_AOI_001, mock_repository
from optimization.suitability import SuitabilityScorer, default_scorer


class TestSuitabilityScoring:
    """Test multi-criteria suitability logic, physical bounds, and explainability."""

    def test_dharavi_dense_settlement_typology(self):
        """
        hs-001 has 55% roofs and only 5% plantable ground.
        Cool roofs should score significantly higher than tree canopy due to spatial constraints.
        """
        hs = mock_repository.get_by_id("hs-001")
        assert hs is not None

        assessments = default_scorer.evaluate_hotspot(hs)
        assert len(assessments) == 2 # Tree canopy and cool roof (MVP)

        # Cool roof should rank first
        assert assessments[0].intervention == InterventionType.COOL_ROOF
        assert assessments[0].suitability_score >= 70.0
        assert assessments[0].category == SuitabilityCategory.HIGH

        # Tree canopy should be severely limited by plantable space
        tree_eval = next(a for a in assessments if a.intervention == InterventionType.TREE_CANOPY)
        assert tree_eval.suitability_score < assessments[0].suitability_score
        assert any("permeable" in factor.lower() or "unbuilt" in factor.lower() for factor in tree_eval.limiting_factors)

    def test_industrial_estate_typology(self):
        """
        hs-002 has 62% roof fraction and only 3% plantable ground.
        Tree canopy should be deemed unsuitable/low, while cool roof should be HIGH.
        """
        hs = mock_repository.get_by_id("hs-002")
        assert hs is not None

        roof_eval = default_scorer.evaluate_intervention(hs, InterventionType.COOL_ROOF)
        tree_eval = default_scorer.evaluate_intervention(hs, InterventionType.TREE_CANOPY)

        assert roof_eval.category == SuitabilityCategory.HIGH
        assert roof_eval.suitability_score >= 75.0
        assert tree_eval.category in (SuitabilityCategory.LOW, SuitabilityCategory.UNSUITABLE)

    def test_residential_sector_typology(self):
        """
        hs-004 has balanced plantable ground (22%) and roof area (32%).
        Both interventions should be feasible with medium-to-high suitability.
        """
        hs = mock_repository.get_by_id("hs-004")
        assert hs is not None

        assessments = default_scorer.evaluate_hotspot(hs)
        for a in assessments:
            assert a.category in (SuitabilityCategory.MEDIUM, SuitabilityCategory.HIGH)
            assert a.suitability_score >= 40.0

    def test_zero_space_hard_infeasibility(self):
        """
        A hotspot with 0% plantable space must yield an UNSUITABLE classification with score 0.
        """
        zero_plant_hs = HotspotProfile(
            id="hs-zero-plant",
            latitude=19.05,
            longitude=72.85,
            area_m2=50000.0,
            baseline_lst_celsius=44.0,
            baseline_fvc=0.0,
            baseline_roof_fraction=0.70,
            baseline_impervious_fraction=0.30,
            max_plantable_fraction=0.0, # Zero plantable space
            max_roof_fraction=0.65,
            risk_score=90.0,
        )

        tree_eval = default_scorer.evaluate_intervention(zero_plant_hs, InterventionType.TREE_CANOPY)
        assert tree_eval.suitability_score == 0.0
        assert tree_eval.category == SuitabilityCategory.UNSUITABLE
        assert any("area constraint" in factor.lower() for factor in tree_eval.limiting_factors)

    def test_suitability_score_bounds_and_structure(self):
        """Verify that all scores lie within [0.0, 100.0] and metadata is populated."""
        for hs in MOCK_HOTSPOTS_AOI_001:
            assessments = default_scorer.evaluate_hotspot(hs)
            for a in assessments:
                assert 0.0 <= a.suitability_score <= 100.0
                assert 0.0 <= a.spatial_feasibility_score <= 100.0
                assert 0.0 <= a.heat_mitigation_need_score <= 100.0
                assert 0.0 <= a.cost_efficiency_score <= 100.0
                assert a.status == ValueStatus.SIMULATED
                assert a.model_version == "suitability-v0.1"
                assert len(a.assumptions) >= 1
