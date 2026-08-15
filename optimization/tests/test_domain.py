"""
Unit tests for domain models, scientific classifications, and validation invariants.
"""

import pytest
from pydantic import ValidationError
from optimization.domain import (
    EvidenceLevel,
    HotspotProfile,
    InterventionSpecification,
    InterventionType,
    SuitabilityCategory,
    ValueStatus,
)


class TestScientificClassifications:
    """Verify explicit value status and evidence level definitions."""

    def test_value_status_values(self):
        assert ValueStatus.OBSERVED.value == "observed"
        assert ValueStatus.PREDICTED.value == "predicted"
        assert ValueStatus.SIMULATED.value == "simulated"
        assert ValueStatus.RECOMMENDED.value == "recommended"

    def test_evidence_levels(self):
        assert EvidenceLevel.DIRECTLY_VALIDATED.value == "directly_validated"
        assert EvidenceLevel.LITERATURE_SUPPORTED.value == "literature_supported"
        assert EvidenceLevel.SCENARIO_ASSUMPTION.value == "scenario_assumption"

    def test_mvp_interventions_exist(self):
        assert InterventionType.TREE_CANOPY.value == "tree_canopy"
        assert InterventionType.COOL_ROOF.value == "cool_roof"


class TestHotspotProfileValidation:
    """Test validation and physical invariants on HotspotProfile."""

    def test_valid_hotspot_profile(self):
        hp = HotspotProfile(
            id="hs-test-01",
            latitude=19.05,
            longitude=72.85,
            area_m2=100000.0,
            baseline_lst_celsius=42.5,
            baseline_fvc=0.10,
            baseline_roof_fraction=0.40,
            baseline_impervious_fraction=0.45,
            max_plantable_fraction=0.20,
            max_roof_fraction=0.35,
            risk_score=85.0,
            risk_category="high",
            vulnerability_score=70.0,
            status=ValueStatus.OBSERVED,
            is_mock=True,
        )
        assert hp.id == "hs-test-01"
        assert hp.baseline_lst_celsius == 42.5
        assert hp.status == ValueStatus.OBSERVED
        assert hp.is_mock is True

    def test_invalid_plantable_fraction_exceeds_unbuilt_space(self):
        """Plantable space cannot exceed unbuilt area (1 - roof_fraction)."""
        with pytest.raises(ValidationError) as exc:
            HotspotProfile(
                id="hs-invalid-01",
                latitude=19.05,
                longitude=72.85,
                area_m2=100000.0,
                baseline_lst_celsius=42.5,
                baseline_fvc=0.05,
                baseline_roof_fraction=0.80, # Only 20% unbuilt space left
                max_plantable_fraction=0.50, # Trying to claim 50% plantable space
                max_roof_fraction=0.80,
                risk_score=85.0,
            )
        assert "max_plantable_fraction" in str(exc.value)

    def test_invalid_roof_fraction_exceeds_existing_roofs(self):
        """Convertible roof space cannot exceed actual building roof fraction."""
        with pytest.raises(ValidationError) as exc:
            HotspotProfile(
                id="hs-invalid-02",
                latitude=19.05,
                longitude=72.85,
                area_m2=100000.0,
                baseline_lst_celsius=42.5,
                baseline_fvc=0.10,
                baseline_roof_fraction=0.20, # Only 20% building roofs
                max_plantable_fraction=0.40,
                max_roof_fraction=0.50, # Trying to claim 50% convertible roofs
                risk_score=85.0,
            )
        assert "max_roof_fraction" in str(exc.value)

    def test_invalid_coordinates(self):
        with pytest.raises(ValidationError):
            HotspotProfile(
                id="hs-invalid-03",
                latitude=95.0, # Latitude > 90
                longitude=72.85,
                area_m2=100000.0,
                baseline_lst_celsius=42.5,
                risk_score=85.0,
            )

    def test_invalid_negative_area(self):
        with pytest.raises(ValidationError):
            HotspotProfile(
                id="hs-invalid-04",
                latitude=19.05,
                longitude=72.85,
                area_m2=-500.0, # Negative area
                baseline_lst_celsius=42.5,
                risk_score=85.0,
            )
