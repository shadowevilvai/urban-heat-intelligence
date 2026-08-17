from .schemas import P1FeatureProperties, P2InternalProperties

def adapt_p1_to_p2(p1_props: P1FeatureProperties) -> P2InternalProperties:
    """Maps finalized P1 fields into the P2 internal representation."""
    return P2InternalProperties(
        feature_id=p1_props.feature_id,
        lst_c=p1_props.lst_c,
        lst_anomaly_c=p1_props.lst_anomaly_c,
        ndvi_mean=p1_props.ndvi_mean,
        ndbi_mean=p1_props.ndbi_mean,
        ndwi_mean=p1_props.ndwi_mean
    )

def is_hotspot(risk_category: str) -> bool:
    """Determine if a feature is considered a hotspot based on risk category."""
    return risk_category in ("high", "extreme")

def generate_hotspot_id(feature_id: str) -> str:
    """Deterministically generates a hotspot ID from a P1 feature ID."""
    return f"HS-{feature_id}"
