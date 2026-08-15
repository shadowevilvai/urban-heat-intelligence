"""
Urban Heat Intelligence — Mitigation Simulation & Optimization Module.

Person 3 / Technical Lead: Mitigation Simulation & Optimization
"""

from optimization.domain import (
    AreaUnit,
    CurrencyUnit,
    EvidenceLevel,
    HotspotProfile,
    InterventionSpecification,
    InterventionType,
    SuitabilityAssessment,
    SuitabilityCategory,
    TemperatureUnit,
    ValueStatus,
)
from optimization.config import (
    DEFAULT_INTERVENTIONS,
    MODEL_VERSION_OPTIMIZER,
    MODEL_VERSION_SIMULATION,
    MODEL_VERSION_SUITABILITY,
    MitigationConfig,
    default_config,
)
from optimization.schemas import (
    InterventionAllocation,
    InterventionSuitabilityItem,
    OptimizeRequest,
    OptimizeResponse,
    SimulateRequest,
    SimulateResponse,
    SuitabilityRequest,
    SuitabilityResponse,
)
from optimization.suitability import (
    SuitabilityScorer,
    default_scorer,
)
from optimization.mock_data import (
    MOCK_HOTSPOTS_AOI_001,
    MockHotspotRepository,
    mock_repository,
)

__all__ = [
    # Domain & Enums
    "AreaUnit",
    "CurrencyUnit",
    "EvidenceLevel",
    "HotspotProfile",
    "InterventionSpecification",
    "InterventionType",
    "SuitabilityAssessment",
    "SuitabilityCategory",
    "TemperatureUnit",
    "ValueStatus",
    # Config & Versions
    "DEFAULT_INTERVENTIONS",
    "MODEL_VERSION_OPTIMIZER",
    "MODEL_VERSION_SIMULATION",
    "MODEL_VERSION_SUITABILITY",
    "MitigationConfig",
    "default_config",
    # Schemas
    "InterventionAllocation",
    "InterventionSuitabilityItem",
    "OptimizeRequest",
    "OptimizeResponse",
    "SimulateRequest",
    "SimulateResponse",
    "SuitabilityRequest",
    "SuitabilityResponse",
    # Suitability
    "SuitabilityScorer",
    "default_scorer",
    # Mock Data
    "MOCK_HOTSPOTS_AOI_001",
    "MockHotspotRepository",
    "mock_repository",
]
