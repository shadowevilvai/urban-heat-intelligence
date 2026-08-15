"""
Urban Heat Intelligence — Mitigation Simulation & Optimization Module.

Person 3 / Technical Lead: Mitigation Simulation & Optimization
"""

from optimization.domain import (
    AreaUnit,
    CoolRoofScenarioParams,
    CurrencyUnit,
    EvidenceLevel,
    HotspotAllocationDetail,
    HotspotProfile,
    InterventionSpecification,
    InterventionType,
    OptimizationResult,
    SimulationResult,
    SpatialConfiguration,
    SuitabilityAssessment,
    SuitabilityCategory,
    TemperatureUnit,
    TreeCanopyScenarioParams,
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
from optimization.simulator import (
    ScenarioSimulator,
    default_simulator,
    simulate_scenario,
)
from optimization.optimizer import (
    PortfolioOptimizer,
    default_optimizer,
    optimize_interventions,
)
from optimization.mock_data import (
    MOCK_HOTSPOTS_AOI_001,
    MockHotspotRepository,
    mock_repository,
)

__all__ = [
    # Domain & Enums
    "AreaUnit",
    "CoolRoofScenarioParams",
    "CurrencyUnit",
    "EvidenceLevel",
    "HotspotAllocationDetail",
    "HotspotProfile",
    "InterventionSpecification",
    "InterventionType",
    "OptimizationResult",
    "SimulationResult",
    "SpatialConfiguration",
    "SuitabilityAssessment",
    "SuitabilityCategory",
    "TemperatureUnit",
    "TreeCanopyScenarioParams",
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
    # Simulator
    "ScenarioSimulator",
    "default_simulator",
    "simulate_scenario",
    # Optimizer
    "PortfolioOptimizer",
    "default_optimizer",
    "optimize_interventions",
    # Mock Data
    "MOCK_HOTSPOTS_AOI_001",
    "MockHotspotRepository",
    "mock_repository",
]
