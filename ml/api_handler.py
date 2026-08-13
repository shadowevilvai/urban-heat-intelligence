from typing import Dict, Any
from schemas import HotspotFeature
from preprocessing import preprocess_features
from risk_engine import calculate_risk

MODEL_VERSION = "env-risk-index-v1.0"

def process_hotspot_feature(feature_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a single GeoJSON Feature dictionary matching the P1 hotspot contract.
    Returns a dictionary matching the P2 API_CONTRACT.md format for a hotspot.
    """
    # 1. Input/Schema Validation
    # Pydantic will raise ValidationError if invalid
    feature = HotspotFeature(**feature_dict)
    props = feature.properties
    
    # 2. Feature Preprocessing (Normalization)
    normalized_features = preprocess_features(props)
    
    # 3. Deterministic Composite Risk Index Calculation
    risk_result = calculate_risk(normalized_features)
    
    # 4. Format according to API_CONTRACT.md
    return {
        "id": props.hotspot_id,
        "lst_celsius": props.lst_mean_c,
        "lst_min_c": props.lst_min_c,
        "lst_max_c": props.lst_max_c,
        "lst_anomaly_c": props.lst_anomaly_c,
        "ndvi_mean": props.ndvi_mean,
        "ndbi_mean": props.ndbi_mean,
        "ndwi_mean": props.ndwi_mean,
        "land_cover_class": props.land_cover_class,
        "risk_score": round(risk_result["risk_score"], 2),
        "risk_category": risk_result["risk_category"],
        "vulnerability_score": round(risk_result["vulnerability_score"], 2) if risk_result["vulnerability_score"] is not None else None,
        "contributors": [
            {
                "name": c["name"],
                "value": round(c["value"], 4),
                "importance": round(c["importance"], 4)
            }
            for c in risk_result["contributors"]
        ],
        "data_date": props.acquisition_date,
        "model_version": MODEL_VERSION,
        "status": "predicted"
    }
