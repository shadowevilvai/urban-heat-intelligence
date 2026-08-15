"""
Synthetic / Mock Hotspot Profile Generator and Registry.

SCIENTIFIC PRINCIPLES:
- Explicitly flags all data as synthetic/mock (`is_mock=True`).
- Provides physically realistic urban morphology typologies (dense core, industrial, suburban, etc.).
- Allows offline testing and decoupled frontend/backend development while real Earth Engine / ML
  pipelines are under development.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from optimization.domain import HotspotProfile, ValueStatus


# Synthetic Hotspots Database for Default AOI (aoi-001: Mumbai Suburban Study Zone)
MOCK_HOTSPOTS_AOI_001: List[HotspotProfile] = [
    HotspotProfile(
        id="hs-001",
        name="Dharavi Transit Corridor",
        latitude=19.0410,
        longitude=72.8530,
        area_m2=250000.0, # 25 hectares
        baseline_lst_celsius=43.5, # Severe thermal anomaly
        baseline_fvc=0.04, # Very low vegetation
        baseline_roof_fraction=0.55, # Dense corrugated metal / tin roofs
        baseline_impervious_fraction=0.38, # Narrow paved alleys / paths
        max_plantable_fraction=0.05, # Severely constrained permeable soil
        max_roof_fraction=0.50, # High cool roof potential
        risk_score=92.0, # Critical risk
        risk_category="high",
        vulnerability_score=88.0, # High social vulnerability & exposure
        data_date="2026-01-15",
        data_source="Landsat Collection 2 Level 2 (Synthetic Mock)",
        status=ValueStatus.OBSERVED,
        is_mock=True,
    ),
    HotspotProfile(
        id="hs-002",
        name="Kurla Industrial Estate",
        latitude=19.0680,
        longitude=72.8890,
        area_m2=420000.0, # 42 hectares
        baseline_lst_celsius=45.2, # Extreme thermal hotspot
        baseline_fvc=0.02, # Minimal vegetation
        baseline_roof_fraction=0.62, # Massive warehouse & industrial flat roofs
        baseline_impervious_fraction=0.34, # Concrete loading yards & parking
        max_plantable_fraction=0.03, # Negligible open soil
        max_roof_fraction=0.60, # Massive flat roof albedo enhancement opportunity
        risk_score=84.0,
        risk_category="high",
        vulnerability_score=65.0,
        data_date="2026-01-15",
        data_source="Landsat Collection 2 Level 2 (Synthetic Mock)",
        status=ValueStatus.OBSERVED,
        is_mock=True,
    ),
    HotspotProfile(
        id="hs-003",
        name="Bandra Kurla Complex Fringe",
        latitude=19.0590,
        longitude=72.8650,
        area_m2=310000.0, # 31 hectares
        baseline_lst_celsius=41.8, # Significant hotspot
        baseline_fvc=0.12, # Some roadside shrubs/grass
        baseline_roof_fraction=0.35, # Commercial mid-rise buildings
        baseline_impervious_fraction=0.45, # Wide roads and plazas
        max_plantable_fraction=0.18, # Viable roadside and median planting strips
        max_roof_fraction=0.30, # Commercial reflective roof candidate
        risk_score=76.0,
        risk_category="high",
        vulnerability_score=52.0,
        data_date="2026-01-15",
        data_source="Landsat Collection 2 Level 2 (Synthetic Mock)",
        status=ValueStatus.OBSERVED,
        is_mock=True,
    ),
    HotspotProfile(
        id="hs-004",
        name="Chembur Residential Sector",
        latitude=19.0520,
        longitude=72.9010,
        area_m2=180000.0, # 18 hectares
        baseline_lst_celsius=38.9, # Moderate hotspot
        baseline_fvc=0.18, # Moderate existing tree cover
        baseline_roof_fraction=0.32, # Residential apartment blocks
        baseline_impervious_fraction=0.40,
        max_plantable_fraction=0.22, # Ample open space in residential compounds
        max_roof_fraction=0.28,
        risk_score=62.0,
        risk_category="medium",
        vulnerability_score=48.0,
        data_date="2026-01-15",
        data_source="Landsat Collection 2 Level 2 (Synthetic Mock)",
        status=ValueStatus.OBSERVED,
        is_mock=True,
    ),
    HotspotProfile(
        id="hs-005",
        name="Sion Rail Yard Buffer",
        latitude=19.0380,
        longitude=72.8620,
        area_m2=150000.0, # 15 hectares
        baseline_lst_celsius=42.1,
        baseline_fvc=0.08,
        baseline_roof_fraction=0.15, # Low building density
        baseline_impervious_fraction=0.55, # Rail tracks, ballast, open yards
        max_plantable_fraction=0.25, # High perimeter greening capacity
        max_roof_fraction=0.12, # Low roof capacity
        risk_score=71.0,
        risk_category="high",
        vulnerability_score=58.0,
        data_date="2026-01-15",
        data_source="Landsat Collection 2 Level 2 (Synthetic Mock)",
        status=ValueStatus.OBSERVED,
        is_mock=True,
    ),
]


class MockHotspotRepository:
    """
    In-memory mock data repository providing hotspot profiles by ID or Area ID.
    """
    def __init__(self, hotspots: Optional[List[HotspotProfile]] = None):
        self._hotspots: Dict[str, HotspotProfile] = {}
        for hs in (hotspots or MOCK_HOTSPOTS_AOI_001):
            self._hotspots[hs.id] = hs

    def get_by_id(self, hotspot_id: str) -> Optional[HotspotProfile]:
        """Fetch a single hotspot profile by its identifier."""
        return self._hotspots.get(hotspot_id)

    def list_by_area(self, area_id: str = "aoi-001") -> List[HotspotProfile]:
        """Fetch all hotspots belonging to an Area of Interest."""
        # For mock prototype, all default hotspots belong to aoi-001
        return list(self._hotspots.values())

    def add_or_update(self, hotspot: HotspotProfile) -> None:
        """Add or update a hotspot profile in the repository."""
        self._hotspots[hotspot.id] = hotspot


# Global mock repository instance
mock_repository = MockHotspotRepository()
