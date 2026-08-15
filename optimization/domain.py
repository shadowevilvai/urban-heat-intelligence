"""
Domain models and value types for the Mitigation Simulation & Optimization module.

CRITICAL SCIENTIFIC INTEGRITY RULES:
- Distinguishes OBSERVED, PREDICTED, SIMULATED, and RECOMMENDED values.
- Explicitly treats Land Surface Temperature (LST) as radiative skin temperature,
  NOT 2-m ambient air temperature or human thermal comfort.
- Classifies evidence levels: DIRECTLY_VALIDATED (Level A),
  LITERATURE_SUPPORTED (Level B), SCENARIO_ASSUMPTION (Level C).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class ValueStatus(str, Enum):
    """
    Explicit status classification for all data values across the pipeline.
    Prevents confusing observed sensor measurements with AI predictions or scenario simulations.
    """
    OBSERVED = "observed"       # Measured/derived directly from satellite/sensor datasets
    PREDICTED = "predicted"     # Inferred by ML/statistical models (e.g. risk score)
    SIMULATED = "simulated"     # Computed under a hypothetical intervention scenario
    RECOMMENDED = "recommended" # Produced by an optimization algorithm


class EvidenceLevel(str, Enum):
    """
    Scientific validation classification according to docs/RESEARCH_VALIDATION.md.
    """
    DIRECTLY_VALIDATED = "directly_validated"   # Level A: Validated by local ground truth / experimental measurements
    LITERATURE_SUPPORTED = "literature_supported" # Level B: Derived from peer-reviewed urban climate literature
    SCENARIO_ASSUMPTION = "scenario_assumption"   # Level C: Hypothetical exploratory assumption for scenario analysis


class InterventionType(str, Enum):
    """
    Intervention types supported by the system.
    MVP requires TREE_CANOPY and COOL_ROOF. Other interventions are defined for P1 extensibility.
    """
    TREE_CANOPY = "tree_canopy"         # Urban tree canopy / fractional vegetation cover expansion (MVP)
    COOL_ROOF = "cool_roof"             # High-albedo reflective roof coatings (MVP)
    GREEN_ROOF = "green_roof"           # Vegetated rooftop infrastructure (P1)
    COOL_PAVEMENT = "cool_pavement"     # High-albedo / permeable pavement (P1)
    SHADE_STRUCTURE = "shade_structure" # Engineered solar shading canopies (P1)


class SuitabilityCategory(str, Enum):
    """
    Categorical ranking of intervention suitability for a specific hotspot.
    """
    HIGH = "high"             # Highly suitable: ample physical capacity and high heat mitigation need
    MEDIUM = "medium"         # Moderately suitable: acceptable feasibility with moderate impact
    LOW = "low"               # Low suitability: constrained space or low marginal benefit
    UNSUITABLE = "unsuitable" # Infeasible: physical or structural preconditions not met


class TemperatureUnit(str, Enum):
    """Units of temperature."""
    CELSIUS = "celsius"
    KELVIN = "kelvin"


class AreaUnit(str, Enum):
    """Units of spatial area."""
    SQ_METERS = "sq_meters"
    HECTARES = "hectares"


class CurrencyUnit(str, Enum):
    """Units of economic cost."""
    USD = "usd"
    INR = "inr"


class HotspotProfile(BaseModel):
    """
    Geospatial and morphological profile of a candidate heat hotspot.
    Provided by the Geospatial (Person 1) and ML/Risk (Person 2) modules or mock generator.
    """
    id: str = Field(..., description="Unique hotspot identifier (e.g. hs-001)")
    name: Optional[str] = Field(None, description="Human-readable zone/neighborhood name")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Centroid latitude (WGS84)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Centroid longitude (WGS84)")
    area_m2: float = Field(..., gt=0.0, description="Total hotspot surface area in square meters")
    
    # Thermal & Environmental State (Observed / Derived)
    baseline_lst_celsius: float = Field(
        ...,
        ge=-20.0,
        le=80.0,
        description="Baseline Land Surface Temperature in Celsius (Radiative skin temperature, NOT air temp)"
    )
    baseline_fvc: float = Field(
        0.10,
        ge=0.0,
        le=1.0,
        description="Baseline Fractional Vegetation Cover [0.0 - 1.0] derived from NDVI"
    )
    baseline_roof_fraction: float = Field(
        0.30,
        ge=0.0,
        le=1.0,
        description="Fraction of hotspot area occupied by building roofs [0.0 - 1.0]"
    )
    baseline_impervious_fraction: float = Field(
        0.50,
        ge=0.0,
        le=1.0,
        description="Fraction of hotspot area occupied by impervious ground/roads [0.0 - 1.0]"
    )
    
    # Physical Intervention Capacity (Geospatial Constraints)
    max_plantable_fraction: float = Field(
        0.25,
        ge=0.0,
        le=1.0,
        description="Maximum fraction of hotspot area with unbuilt, permeable ground suitable for trees"
    )
    max_roof_fraction: float = Field(
        0.30,
        ge=0.0,
        le=1.0,
        description="Maximum fraction of hotspot area with structurally sound roofs convertible to cool roofs"
    )
    
    # Risk & Vulnerability State (Predicted by ML module)
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Predicted heat-risk score (0 - 100)")
    risk_category: str = Field("high", description="Risk category: high, medium, or low")
    vulnerability_score: float = Field(50.0, ge=0.0, le=100.0, description="Socio-economic vulnerability score (0 - 100)")
    
    # Optional Environmental & Geospatial Context (for safe ingestion of advanced datasets)
    lst_anomaly_c: Optional[float] = Field(None, description="Local thermal anomaly relative to regional mean in °C")
    ndvi_mean: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Mean Normalized Difference Vegetation Index")
    ndbi_mean: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Mean Normalized Difference Built-up Index")
    ndwi_mean: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Mean Normalized Difference Water Index")
    land_cover_class: Optional[str] = Field(None, description="Dominant land-cover classification name")
    
    # Metadata & Scientific Provenance
    data_date: str = Field("2026-01-15", description="Observation or acquisition date (YYYY-MM-DD)")
    data_source: str = Field("Landsat Collection 2 Level 2", description="Data source name")
    status: ValueStatus = Field(ValueStatus.OBSERVED, description="Status classification of baseline data")
    is_mock: bool = Field(False, description="Explicit flag indicating whether values are synthetic/mock")

    @model_validator(mode="after")
    def validate_spatial_fractions(self) -> "HotspotProfile":
        """Verify that physical capacity fractions do not exceed total hotspot bounds."""
        if self.max_plantable_fraction > (1.0 - self.baseline_roof_fraction + 0.001):
            # Plantable area cannot exceed unbuilt area
            raise ValueError(
                f"max_plantable_fraction ({self.max_plantable_fraction}) exceeds "
                f"available unbuilt fraction ({1.0 - self.baseline_roof_fraction:.2f})"
            )
        if self.max_roof_fraction > (self.baseline_roof_fraction + 0.001):
            # Convertible roof area cannot exceed existing roof area
            raise ValueError(
                f"max_roof_fraction ({self.max_roof_fraction}) exceeds "
                f"existing roof fraction ({self.baseline_roof_fraction:.2f})"
            )
        return self


class InterventionSpecification(BaseModel):
    """
    Full scientific parameterization and evidence specification for an intervention.
    """
    intervention_type: InterventionType
    name: str = Field(..., description="Human-readable intervention name")
    description: str = Field(..., description="Scientific description of intervention mechanism")
    cooling_mechanism: str = Field(..., description="Physical mechanism (e.g. shading, albedo, evapotranspiration)")
    
    # Economic Parameters
    unit_cost_currency: CurrencyUnit = Field(CurrencyUnit.USD, description="Currency for unit cost")
    default_cost_per_m2: float = Field(..., gt=0.0, description="Estimated capital + installation cost per m^2")
    cost_range_per_m2: tuple[float, float] = Field(..., description="Uncertainty range for unit cost [min, max]")
    
    # Physical & Thermal Parameters (Literature Benchmark)
    cooling_coefficient_celsius: float = Field(
        ...,
        gt=0.0,
        description="Marginal LST cooling gradient per unit intensity (e.g. °C drop per 100% conversion)"
    )
    cooling_uncertainty_range: tuple[float, float] = Field(
        ...,
        description="Literature uncertainty range [min, max] for cooling gradient"
    )
    max_recommended_intensity: float = Field(
        0.50,
        ge=0.0,
        le=1.0,
        description="Recommended maximum intensity before saturation/diminishing returns dominate"
    )
    diminishing_returns_factor: float = Field(
        0.50,
        ge=0.0,
        le=1.0,
        description="Non-linear damping factor applied as coverage approaches saturation"
    )
    
    # Scientific Evidence & Citations
    evidence_level: EvidenceLevel = Field(EvidenceLevel.LITERATURE_SUPPORTED)
    citations: List[str] = Field(default_factory=list, description="Academic literature citations")
    assumptions: List[str] = Field(default_factory=list, description="Standard scenario assumptions")
    is_mvp_ready: bool = Field(True, description="Whether intervention is supported in the MVP release")


class SuitabilityAssessment(BaseModel):
    """
    Detailed multi-criteria suitability assessment of a specific intervention for a hotspot.
    """
    hotspot_id: str
    intervention: InterventionType
    suitability_score: float = Field(..., ge=0.0, le=100.0, description="Composite suitability score (0 - 100)")
    category: SuitabilityCategory
    
    # Physical Feasibility Metrics
    available_area_fraction: float = Field(..., ge=0.0, le=1.0, description="Fraction of hotspot area physically available")
    max_feasible_area_m2: float = Field(..., ge=0.0, description="Absolute available surface area in m^2")
    estimated_unit_cost: float = Field(..., gt=0.0, description="Expected cost per m^2")
    
    # Multi-Criteria Sub-Scores (0 - 100)
    spatial_feasibility_score: float = Field(..., ge=0.0, le=100.0, description="Spatial capacity sub-score")
    heat_mitigation_need_score: float = Field(..., ge=0.0, le=100.0, description="Thermal deficit & risk sub-score")
    cost_efficiency_score: float = Field(..., ge=0.0, le=100.0, description="Cost-benefit efficiency sub-score")
    
    # Explainability & Traceability
    limiting_factors: List[str] = Field(default_factory=list, description="Physical or economic constraints identified")
    advantages: List[str] = Field(default_factory=list, description="Key favorable conditions for this intervention")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions governing this suitability score")
    evidence_level: EvidenceLevel = Field(EvidenceLevel.LITERATURE_SUPPORTED)
    model_version: str = Field("suitability-v0.1")
    status: ValueStatus = Field(ValueStatus.SIMULATED)


class SpatialConfiguration(str, Enum):
    """Spatial configuration patterns for urban tree planting."""
    DISPERSED = "dispersed"           # Standard distributed street/parcel trees (1.0x baseline)
    CLUSTERED = "clustered"           # Park / dense grove cluster (1.15x park cool island co-benefit)
    LINEAR_CORRIDOR = "linear_corridor" # Linear green corridor / street canyon (1.05x microclimate shading)


class TreeCanopyScenarioParams(BaseModel):
    """
    Configurable microclimate and morphological scenario parameters for tree canopy simulation.
    Allows testing diverse species densities, maturity heights, and spatial layouts.
    """
    canopy_density: float = Field(
        0.80,
        ge=0.10,
        le=1.0,
        description="Fractional foliage crown density / leaf area index factor [0.10 - 1.0]"
    )
    tree_height_m: Optional[float] = Field(
        None,
        ge=1.0,
        le=45.0,
        description="Estimated average tree height in meters (affects mature shading footprint)"
    )
    spatial_configuration: SpatialConfiguration = Field(
        SpatialConfiguration.DISPERSED,
        description="Spatial planting configuration pattern: 'dispersed', 'clustered', 'linear_corridor'"
    )


class CoolRoofScenarioParams(BaseModel):
    """
    Configurable physical surface and optical parameters for cool roof simulation.
    Allows testing specific baseline roof coatings against target high-albedo materials.
    """
    baseline_albedo: float = Field(
        0.18,
        ge=0.05,
        le=0.50,
        description="Baseline solar reflectance / albedo of existing roof materials"
    )
    intervention_albedo: float = Field(
        0.68,
        ge=0.30,
        le=0.95,
        description="Target solar reflectance / albedo of cool roof coating"
    )
    thermal_emissivity: float = Field(
        0.90,
        ge=0.50,
        le=1.0,
        description="Thermal infrared surface emissivity [0.50 - 1.0]"
    )


class SimulationResult(BaseModel):
    """
    Structured domain result of a mitigation scenario simulation.
    Captures complete scientific provenance, physical footprint, thermal projections,
    parameter-driven configuration, uncertainty bounds, assumptions, and limitations.
    """
    hotspot_id: str = Field(..., description="Target hotspot identifier")
    intervention: InterventionType = Field(..., description="Intervention type evaluated")
    intensity: float = Field(..., ge=0.0, le=1.0, description="Intervention implementation intensity")
    
    # Thermal Projections (Observed Baseline vs Simulated Projection)
    baseline_lst_celsius: float = Field(..., description="Baseline observed Land Surface Temperature in °C")
    projected_lst_celsius: float = Field(..., description="Simulated projected Land Surface Temperature in °C")
    estimated_change_celsius: float = Field(..., description="Estimated temperature change in °C (negative indicates cooling)")
    cooling_uncertainty_range_celsius: tuple[float, float] = Field(
        ...,
        description="Uncertainty interval [max_cooling_delta, min_cooling_delta] in °C"
    )
    
    # Spatial & Physical Footprint
    eligible_area_m2: float = Field(..., ge=0.0, description="Physically eligible hotspot surface area in m^2")
    treated_area_m2: float = Field(..., ge=0.0, description="Estimated treated surface area in m^2")
    treated_area_fraction: float = Field(..., ge=0.0, le=1.0, description="Fraction of total hotspot area treated")
    
    # Economic Projections
    estimated_cost: float = Field(..., ge=0.0, description="Estimated capital + installation cost")
    currency: CurrencyUnit = Field(CurrencyUnit.USD, description="Cost currency")
    
    # Parameter Breakdown
    scenario_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Explicit physical, optical, and morphological parameters used in this simulation"
    )
    
    # Scientific Governance & Traceability
    evidence_level: EvidenceLevel = Field(EvidenceLevel.LITERATURE_SUPPORTED)
    assumptions: List[str] = Field(default_factory=list, description="Explicit scenario assumptions and scientific citations")
    limitations: List[str] = Field(default_factory=list, description="Model limitations and boundary conditions")
    model_version: str = Field("simulation-v0.1")
    status: ValueStatus = Field(ValueStatus.SIMULATED, description="Explicit value status: strictly 'simulated'")


class HotspotAllocationDetail(BaseModel):
    """
    Recommended intervention allocation and impact projection for a single hotspot.
    """
    hotspot_id: str
    hotspot_name: Optional[str] = None
    intervention: InterventionType
    allocation_fraction: float = Field(..., ge=0.0, le=1.0, description="Fraction of eligible capacity allocated [0.0 - 1.0]")
    treated_area_m2: float = Field(..., ge=0.0, description="Treated ground or roof area in m^2")
    eligible_area_m2: float = Field(..., ge=0.0, description="Total eligible ground or roof area in m^2")
    estimated_cost: float = Field(..., ge=0.0, description="Estimated implementation cost")
    expected_cooling_celsius: float = Field(..., ge=0.0, description="Magnitude of expected LST cooling in °C")
    projected_lst_celsius: float = Field(..., description="Projected post-intervention LST in °C")
    risk_score: float = Field(..., description="Baseline heat-risk score")
    limiting_constraints: List[str] = Field(default_factory=list, description="Binding constraints for this allocation")


class OptimizationResult(BaseModel):
    """
    Structured domain result of multi-hotspot constrained portfolio optimization.
    Distinguishes RECOMMENDED decision variables from SIMULATED and OBSERVED values.
    """
    status: str = Field(..., description="Optimization status: 'optimal', 'infeasible', 'budget_exceeded'")
    budget: float = Field(..., ge=0.0, description="Total available budget considered in optimization")
    estimated_total_cost: float = Field(..., ge=0.0, description="Total estimated cost across all recommended allocations")
    expected_cooling: float = Field(..., ge=0.0, description="Area-weighted expected LST cooling in °C across target hotspots")
    
    # Portfolio-level Summary (Matches docs/API_CONTRACT.md schema)
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Aggregate portfolio allocation share by intervention type"
    )
    
    # Granular Hotspot Allocations
    hotspot_allocations: List[HotspotAllocationDetail] = Field(
        default_factory=list,
        description="Detailed per-hotspot allocation breakdown"
    )
    
    # Traceability & Governance
    limiting_constraints: List[str] = Field(default_factory=list, description="Binding constraints across the portfolio")
    evidence_level: EvidenceLevel = Field(EvidenceLevel.LITERATURE_SUPPORTED)
    assumptions: List[str] = Field(default_factory=list, description="Assumptions governing the optimization")
    model_version: str = Field("optimizer-v0.1")
    value_status: ValueStatus = Field(ValueStatus.RECOMMENDED, description="Explicit value status: 'recommended'")

