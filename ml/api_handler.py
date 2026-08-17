from typing import Dict, Any
from schemas import P1Feature
from adapter import adapt_p1_to_p2, is_hotspot, generate_hotspot_id
from preprocessing import preprocess_features
from risk_engine import calculate_risk
from context_classifier import classify_context

MODEL_VERSION = "env-risk-index-v1.0"

def process_hotspot_feature(feature_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a single GeoJSON Feature dictionary matching the P1 finalized contract.
    Returns a dictionary acting as the canonical P2 service output.
    """
    # 1. Input/Schema Validation
    # Pydantic will raise ValidationError if invalid
    feature = P1Feature(**feature_dict)
    props = feature.properties
    
    # 2. Map P1 to P2 Internal Properties
    p2_internal_props = adapt_p1_to_p2(props)

    # 3. Feature Preprocessing (Normalization)
    normalized_features = preprocess_features(p2_internal_props)
    
    # 4. Deterministic Composite Risk Index Calculation
    risk_result = calculate_risk(normalized_features)
    risk_category = risk_result["risk_category"]
    
    # 5. Format canonical P2 service representation
    output = {
        "feature_id": props.feature_id,
        "p1_location": {
            "city": props.city,
            "geometry": {
                "type": feature.geometry.type,
                "coordinates": feature.geometry.coordinates
            }
        },
        "p1_measurements": {
            "lst_c": props.lst_c,
            "lst_anomaly_c": props.lst_anomaly_c,
            "ndvi_mean": props.ndvi_mean,
            "ndbi_mean": props.ndbi_mean,
            "ndwi_mean": props.ndwi_mean,
            "land_cover_class": props.land_cover_class
        },
        "p1_provenance": {
            "schema_version": props.schema_version,
            "source": props.source,
            "satellite": props.satellite,
            "date_period_start": props.date_period_start,
            "date_period_end": props.date_period_end,
            "processing_date": props.processing_date,
            "resolution_m_source": props.resolution_m_source,
            "resolution_m_sample": props.resolution_m_sample,
            "coordinate_reference_system": props.coordinate_reference_system,
            "data_quality": props.data_quality,
            "valid_pixel_percent": props.valid_pixel_percent
        },
        "p2_analysis": {
            "risk_score": round(risk_result["risk_score"], 2),
            "risk_category": risk_category,
            "vulnerability_score": round(risk_result["vulnerability_score"], 2) if risk_result["vulnerability_score"] is not None else None,
            "contributors": [
                {
                    "name": c["name"],
                    "value": round(c["value"], 4),
                    "importance": round(c["importance"], 4)
                }
                for c in risk_result["contributors"]
            ],
            "model_version": MODEL_VERSION,
            "hotspot_context": classify_context(props)
        }
    }
    
    if is_hotspot(risk_category):
        output["hotspot_id"] = generate_hotspot_id(props.feature_id)
        
    return output
