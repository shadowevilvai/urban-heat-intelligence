from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class HotspotProperties(BaseModel):
    # CORE FIELDS
    hotspot_id: str
    city: str
    lst_mean_c: float
    lst_min_c: float
    lst_max_c: float
    lst_anomaly_c: float
    
    # Excluded from risk logic, but part of schema
    heat_class: str
    hotspot_score: float

    # OPTIONAL ENVIRONMENTAL INDICATORS
    ndvi_mean: Optional[float] = None
    ndbi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
    land_cover_class: Optional[str] = None

    # DATA PROVENANCE & QUALITY
    source: str
    satellite: str
    acquisition_date: str
    processing_date: str
    cloud_cover_percent: float
    resolution_m: float
    coordinate_reference_system: str
    data_quality: str
    valid_pixel_percent: float
    confidence: float

    @field_validator('cloud_cover_percent', 'valid_pixel_percent', 'confidence', mode='before')
    @classmethod
    def validate_percentages(cls, v):
        if v < 0.0 or v > 100.0:
            if v <= 1.0 and v >= 0.0:  # Allow 0-1 range for confidence/percentages
                return v
            raise ValueError(f"Value {v} out of bounds")
        return v

class HotspotGeometry(BaseModel):
    type: str
    coordinates: List[float]

class HotspotFeature(BaseModel):
    type: str = "Feature"
    properties: HotspotProperties
    geometry: HotspotGeometry

class HotspotFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[HotspotFeature]
