"""
Pydantic API request and response schemas.

STRICTLY ALIGNED WITH docs/API_CONTRACT.md.
Ensures strong validation, accurate scientific labeling, and robust serialization.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from optimization.domain import InterventionType, ValueStatus, EvidenceLevel


# ==============================================================================
# Simulation API Schemas (docs/API_CONTRACT.md Section 5)
# ==============================================================================

class SimulateRequest(BaseModel):
    """
    Request payload for POST /api/v1/simulate.
    """
    hotspot_id: str = Field(
        ...,
        min_length=1,
        description="Target hotspot identifier (e.g. hs-001)",
        examples=["hs-001"]
    )
    intervention: str = Field(
        ...,
        description="Intervention type to simulate (e.g. tree_canopy, cool_roof)",
        examples=["tree_canopy"]
    )
    intensity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Intervention implementation intensity [0.0 - 1.0] (e.g. 0.2 for 20% conversion)",
        examples=[0.2]
    )

    @field_validator("intervention")
    @classmethod
    def validate_intervention_type(cls, v: str) -> str:
        v_clean = v.strip().lower()
        allowed = [t.value for t in InterventionType]
        if v_clean not in allowed:
            raise ValueError(
                f"Unsupported intervention '{v}'. Must be one of: {allowed}"
            )
        return v_clean


class SimulateResponse(BaseModel):
    """
    Response schema for POST /api/v1/simulate.
    Matches docs/API_CONTRACT.md Section 5 exactly.
    """
    baseline_lst_celsius: float = Field(
        ...,
        description="Baseline observed Land Surface Temperature in Celsius"
    )
    predicted_lst_celsius: float = Field(
        ...,
        description="Simulated post-intervention Land Surface Temperature in Celsius"
    )
    estimated_change_celsius: float = Field(
        ...,
        description="Estimated change in LST in Celsius (negative indicates cooling)"
    )
    evidence_level: str = Field(
        EvidenceLevel.LITERATURE_SUPPORTED.value,
        description="Scientific validation level: directly_validated, literature_supported, scenario_assumption"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit scenario assumptions and scientific citations governing the simulation"
    )
    model_version: str = Field(
        "simulation-v0.1",
        description="Version of the simulation engine"
    )
    status: str = Field(
        ValueStatus.SIMULATED.value,
        description="Explicit value status classification: strictly 'simulated'"
    )


# ==============================================================================
# Optimization API Schemas (docs/API_CONTRACT.md Section 6)
# ==============================================================================

class OptimizeRequest(BaseModel):
    """
    Request payload for POST /api/v1/optimize.
    """
    area_id: str = Field(
        ...,
        min_length=1,
        description="Target Area of Interest identifier (e.g. aoi-001)",
        examples=["aoi-001"]
    )
    budget: float = Field(
        ...,
        ge=0.0,
        description="Total available budget for mitigation interventions",
        examples=[100000000.0]
    )
    interventions: List[str] = Field(
        ...,
        min_length=1,
        description="List of candidate intervention types to include in optimization",
        examples=[["tree_canopy", "cool_roof"]]
    )

    @field_validator("interventions")
    @classmethod
    def validate_interventions(cls, v: List[str]) -> List[str]:
        allowed = [t.value for t in InterventionType]
        cleaned = []
        for item in v:
            item_clean = item.strip().lower()
            if item_clean not in allowed:
                raise ValueError(
                    f"Unsupported intervention '{item}'. Allowed: {allowed}"
                )
            cleaned.append(item_clean)
        return list(dict.fromkeys(cleaned)) # remove duplicates while preserving order


class InterventionAllocation(BaseModel):
    """
    Recommended allocation for a specific intervention type.
    """
    intervention: str = Field(..., description="Intervention type identifier")
    allocation: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized portfolio allocation fraction [0.0 - 1.0]"
    )


class OptimizeResponse(BaseModel):
    """
    Response schema for POST /api/v1/optimize.
    Matches docs/API_CONTRACT.md Section 6 exactly.
    """
    status: str = Field(
        ...,
        description="Optimization status: 'optimal', 'infeasible', 'budget_exceeded'"
    )
    budget: float = Field(
        ...,
        description="Total budget considered in the optimization problem"
    )
    estimated_total_cost: float = Field(
        ...,
        description="Total estimated cost of the recommended intervention portfolio"
    )
    expected_cooling: float = Field(
        ...,
        description="Area-weighted or average expected LST cooling in Celsius across the target hotspots"
    )
    recommendations: List[InterventionAllocation] = Field(
        default_factory=list,
        description="Recommended portfolio allocation by intervention type"
    )
    model_version: str = Field(
        "optimizer-v0.1",
        description="Version of the optimization engine"
    )


# ==============================================================================
# Suitability Assessment API Schemas (Milestone 1 Core Domain Feature)
# ==============================================================================

class SuitabilityRequest(BaseModel):
    """
    Request payload to evaluate intervention suitability for a hotspot.
    """
    hotspot_id: str = Field(..., min_length=1, description="Target hotspot identifier")
    interventions: Optional[List[str]] = Field(
        None,
        description="Optional subset of interventions to evaluate (evaluates all MVP if omitted)"
    )


class InterventionSuitabilityItem(BaseModel):
    """
    Detailed suitability evaluation item for a single intervention on a hotspot.
    """
    intervention: str = Field(..., description="Intervention type identifier")
    name: str = Field(..., description="Human-readable intervention name")
    suitability_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Composite multi-criteria suitability score (0 - 100)"
    )
    category: str = Field(
        ...,
        description="Categorical rating: 'high', 'medium', 'low', 'unsuitable'"
    )
    available_area_fraction: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraction of hotspot area physically available for this intervention"
    )
    max_feasible_area_m2: float = Field(
        ...,
        ge=0.0,
        description="Maximum feasible surface area in square meters"
    )
    estimated_unit_cost: float = Field(
        ...,
        gt=0.0,
        description="Estimated unit cost per m^2"
    )
    spatial_feasibility_score: float = Field(..., ge=0.0, le=100.0)
    heat_mitigation_need_score: float = Field(..., ge=0.0, le=100.0)
    cost_efficiency_score: float = Field(..., ge=0.0, le=100.0)
    limiting_factors: List[str] = Field(default_factory=list)
    advantages: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    evidence_level: str = Field(EvidenceLevel.LITERATURE_SUPPORTED.value)


class SuitabilityResponse(BaseModel):
    """
    Response schema for hotspot suitability assessment.
    """
    hotspot_id: str
    baseline_lst_celsius: float
    risk_score: float
    suitabilities: List[InterventionSuitabilityItem]
    model_version: str = Field("suitability-v0.1")
    status: str = Field(ValueStatus.SIMULATED.value)
