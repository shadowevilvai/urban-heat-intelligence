"""
Unit tests for mitigation configuration and literature parameter registry.
"""

import pytest
from optimization.config import (
    DEFAULT_INTERVENTIONS,
    MitigationConfig,
    default_config,
)
from optimization.domain import EvidenceLevel, InterventionType


class TestInterventionConfig:
    """Test configuration registry and literature metadata."""

    def test_default_interventions_contain_mvp(self):
        assert InterventionType.TREE_CANOPY in DEFAULT_INTERVENTIONS
        assert InterventionType.COOL_ROOF in DEFAULT_INTERVENTIONS
        tree_spec = DEFAULT_INTERVENTIONS[InterventionType.TREE_CANOPY]
        roof_spec = DEFAULT_INTERVENTIONS[InterventionType.COOL_ROOF]

        assert tree_spec.is_mvp_ready is True
        assert roof_spec.is_mvp_ready is True

    def test_literature_citations_present(self):
        tree_spec = default_config.get(InterventionType.TREE_CANOPY)
        roof_spec = default_config.get(InterventionType.COOL_ROOF)

        assert len(tree_spec.citations) >= 2
        assert any("Oke" in c for c in tree_spec.citations)
        assert len(roof_spec.citations) >= 2
        assert any("Akbari" in c for c in roof_spec.citations)

    def test_cooling_gradients_and_costs_are_positive(self):
        for spec in default_config.list_interventions(mvp_only=True):
            assert spec.cooling_coefficient_celsius > 0.0
            assert spec.default_cost_per_m2 > 0.0
            assert spec.cost_range_per_m2[0] < spec.cost_range_per_m2[1]
            assert spec.cooling_uncertainty_range[0] < spec.cooling_uncertainty_range[1]

    def test_update_parameter_calibration(self):
        cfg = MitigationConfig()
        cfg.update_parameter(
            InterventionType.TREE_CANOPY,
            cooling_coefficient_celsius=2.3,
            default_cost_per_m2=25.0,
            evidence_level=EvidenceLevel.DIRECTLY_VALIDATED,
        )
        updated = cfg.get(InterventionType.TREE_CANOPY)
        assert updated.cooling_coefficient_celsius == 2.3
        assert updated.default_cost_per_m2 == 25.0
        assert updated.evidence_level == EvidenceLevel.DIRECTLY_VALIDATED

    def test_invalid_parameter_update_raises_error(self):
        cfg = MitigationConfig()
        with pytest.raises(ValueError):
            cfg.update_parameter(InterventionType.TREE_CANOPY, cooling_coefficient_celsius=-1.0)
        with pytest.raises(ValueError):
            cfg.update_parameter(InterventionType.TREE_CANOPY, default_cost_per_m2=0.0)

    def test_unknown_intervention_lookup_raises_error(self):
        cfg = MitigationConfig()
        with pytest.raises(ValueError):
            cfg.get("unknown_intervention_xyz")
