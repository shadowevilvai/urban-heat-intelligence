from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class P1FeatureProperties(BaseModel):
    # CORE FIELDS
    schema_version: str
    feature_id: str
    city: str
    lst_c: float
    lst_anomaly_c: Optional[float] = None
    
    # OPTIONAL ENVIRONMENTAL INDICATORS
    ndvi_mean: Optional[float] = None
    ndbi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
    land_cover_class: Optional[str] = None

    # DATA PROVENANCE & QUALITY
    source: str
    satellite: str
    date_period_start: str
    date_period_end: str
    processing_date: str
    resolution_m_source: int
    resolution_m_sample: int
    coordinate_reference_system: str
    data_quality: str
    valid_pixel_percent: Optional[float] = None

    @field_validator('schema_version')
    @classmethod
    def validate_schema_version(cls, v):
        if v != "1.0":
            raise ValueError(f"Unsupported schema version: {v}")
        return v

    @field_validator('valid_pixel_percent', mode='before')
    @classmethod
    def validate_percentages(cls, v):
        if v is None:
            return v
        if v < 0.0 or v > 100.0:
            raise ValueError(f"Value {v} out of bounds")
        return v

class P1Geometry(BaseModel):
    type: str
    coordinates: List[float]

class P1Feature(BaseModel):
    type: str = "Feature"
    id: Optional[str] = None
    properties: P1FeatureProperties
    geometry: P1Geometry

class P1FeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[P1Feature]

class P2InternalProperties(BaseModel):
    """Internal model for features entering the risk engine."""
    feature_id: str
    lst_c: float
    lst_anomaly_c: Optional[float] = None
    ndvi_mean: Optional[float] = None
    ndbi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
