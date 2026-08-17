from enum import Enum
from typing import List, Tuple, Optional
from pydantic import BaseModel, Field

class ValueStatus(str, Enum):
    OBSERVED = "observed"
    DERIVED = "derived"
    PROXY = "proxy"
    SIMULATED = "simulated"
    RECOMMENDED = "recommended"

class EvidenceLevel(str, Enum):
    DIRECTLY_VALIDATED = "directly_validated"
    LITERATURE_SUPPORTED = "literature_supported"
    SCENARIO_ASSUMPTION = "scenario_assumption"
    PLANNING_PROXY = "planning_proxy"

class InterventionType(str, Enum):
    TREE_CANOPY = "tree_canopy"
    COOL_ROOF = "cool_roof"

class SuitabilityCategory(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNSUITABLE = "unsuitable"

class ResourceUnit(str, Enum):
    PLANNING_UNITS = "planning_units"

class InterventionSpecification(BaseModel):
    intervention_type: InterventionType
    name: str
    description: str
    
    # Cooling Response Parameters
    cooling_coefficient_celsius: float = Field(..., gt=0.0)
    cooling_uncertainty_range: Tuple[float, float]
    
    # Resource Model (Proxy)
    unit_cost_resource_units: float = Field(..., gt=0.0)
    
    # Scientific Traceability
    evidence_level: EvidenceLevel
    source_title: str
    source_year: int
    source_url_or_doi: Optional[str]
    applicability: str
    uncertainty: str
    assumptions: List[str]
    limitations: List[str]
