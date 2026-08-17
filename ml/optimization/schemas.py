from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from .domain import ValueStatus, EvidenceLevel, InterventionType, SuitabilityCategory

# ==============================================================================
# Suitability API Schemas
# ==============================================================================

class SuitabilityRequest(BaseModel):
    hotspot_id: str = Field(..., description="Target 450m sampling point feature ID")
    interventions: Optional[List[str]] = Field(None, description="Optional list of intervention types to evaluate")

class InterventionSuitabilityItem(BaseModel):
    intervention: str
    name: str
    suitability_score: float = Field(..., ge=0.0, le=100.0, description="DERIVED: Suitability score (0-100)")
    category: SuitabilityCategory = Field(..., description="DERIVED: Categorical suitability rating")
    
    # Derivation metrics
    heat_mitigation_need_score: float = Field(..., ge=0.0, le=100.0, description="DERIVED: Thermal deficit & risk sub-score")
    feasibility_score: float = Field(..., ge=0.0, le=100.0, description="DERIVED: Contextual/Environmental feasibility sub-score")
    
    # Traceability
    limiting_factors: List[str] = Field(default_factory=list)
    advantages: List[str] = Field(default_factory=list)
    model_version: str = Field("suitability-v0.2")
    status: ValueStatus = Field(ValueStatus.DERIVED)

class SuitabilityResponse(BaseModel):
    hotspot_id: str
    observed_lst_celsius: float
    risk_score: float
    suitabilities: List[InterventionSuitabilityItem]
    status: ValueStatus = Field(ValueStatus.DERIVED)

# ==============================================================================
# Simulation API Schemas
# ==============================================================================

class SimulateRequest(BaseModel):
    hotspot_id: str
    intervention: str
    intensity: float = Field(..., ge=0.0, le=1.0, description="PROXY: Intervention intensity [0.0 - 1.0]")

    @field_validator("intervention")
    @classmethod
    def validate_intervention(cls, v: str) -> str:
        allowed = [t.value for t in InterventionType]
        if v not in allowed:
            raise ValueError(f"Unsupported intervention '{v}'. Allowed: {allowed}")
        return v

class SimulateResponse(BaseModel):
    observed_lst_celsius: float = Field(..., description="OBSERVED: Baseline LST at 450m sampling point")
    estimated_change_celsius: float = Field(..., description="SIMULATED: Scenario LST change (negative is cooling)")
    scenario_lst_celsius: float = Field(..., description="SIMULATED: Planning-level scenario LST estimate, not a guaranteed future temperature")
    
    # Traceability
    intervention_type: str
    intensity: float = Field(..., description="PROXY: Assumed intervention intensity")
    suitability_factor: float = Field(..., description="DERIVED: Suitability scaling factor applied")
    cooling_coefficient: float = Field(..., description="PROXY: Literature cooling coefficient used")
    cooling_uncertainty_range: List[float] = Field(..., description="PROXY: Uncertainty bounds [min_change, max_change] where min <= max (e.g. [-1.5, -0.9])")
    evidence_level: EvidenceLevel
    source_title: str
    source_year: int
    source_url_or_doi: Optional[str]
    applicability: str
    uncertainty: str
    assumptions: List[str]
    limitations: List[str]
    model_version: str = Field("simulation-v0.2")
    status: ValueStatus = Field(ValueStatus.SIMULATED)
    
    description: str = Field("Planning-level scenario estimate around the 450m sampling point under specified intervention assumptions.")

# ==============================================================================
# Optimization API Schemas
# ==============================================================================

class OptimizeRequest(BaseModel):
    hotspot_ids: List[str] = Field(..., description="List of target 450m sampling point feature IDs")
    resource_budget: float = Field(..., ge=0.0, description="PROXY: Total available normalized resource units")
    interventions: List[str]

    @field_validator("interventions")
    @classmethod
    def validate_interventions(cls, v: List[str]) -> List[str]:
        allowed = [t.value for t in InterventionType]
        return [item for item in v if item in allowed]

class HotspotAllocationDetail(BaseModel):
    hotspot_id: str
    intervention: str
    intensity_allocated: float = Field(..., ge=0.0, le=1.0, description="RECOMMENDED: Allocated intensity [0.0 - 1.0]")
    resource_units_used: float = Field(..., ge=0.0, description="PROXY: Resource units consumed")
    expected_cooling_celsius: float = Field(..., description="SIMULATED: Expected LST cooling magnitude (absolute magnitude of change)")
    scenario_lst_celsius: float = Field(..., description="SIMULATED: Planning-level scenario LST estimate")
    limiting_constraints: List[str] = Field(default_factory=list)

class OptimizeResponse(BaseModel):
    status: str
    resource_budget: float = Field(..., description="PROXY: Initial resource budget")
    total_resources_used: float = Field(..., description="PROXY: Total resource units consumed")
    portfolio_objective_value: float = Field(..., description="DERIVED: Priority-weighted suitability objective value maximized by solver")
    total_expected_cooling_celsius: float = Field(..., description="SIMULATED: Total physical cooling sum across allocated features")
    
    recommendations: List[Dict[str, float]] = Field(..., description="RECOMMENDED: Aggregate portfolio allocation share")
    hotspot_allocations: List[HotspotAllocationDetail]
    
    limiting_constraints: List[str]
    evidence_level: EvidenceLevel = Field(EvidenceLevel.LITERATURE_SUPPORTED)
    assumptions: List[str]
    model_version: str = Field("optimizer-v0.2")
    value_status: ValueStatus = Field(ValueStatus.RECOMMENDED)

