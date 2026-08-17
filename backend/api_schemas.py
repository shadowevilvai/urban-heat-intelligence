from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# We reuse the core P3 schemas where practical, to preserve the exact semantic definitions.
from ml.optimization.schemas import OptimizeResponse

class MapFeatureProperties(BaseModel):
    feature_id: str
    lst_c: float
    risk_category: str
    hotspot_context: str

class MapFeatureGeometry(BaseModel):
    type: str
    coordinates: List[float]

class MapFeature(BaseModel):
    type: str = "Feature"
    properties: MapFeatureProperties
    geometry: MapFeatureGeometry

class MapFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[MapFeature]

class HotspotDetailResponse(BaseModel):
    feature: Dict[str, Any]
    risk: Dict[str, Any]

class OptimizationTransportRequest(BaseModel):
    city_id: str = Field(..., description="The dataset identifier, e.g., 'mumbai'")
    hotspot_ids: List[str] = Field(..., description="List of target 450m sampling point feature IDs")
    resource_budget: float = Field(..., ge=0.0, description="PROXY: Total available normalized resource units")
    interventions: List[str]
