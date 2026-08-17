from .schemas import P1FeatureProperties

def classify_context(props: P1FeatureProperties) -> str:
    """
    Classifies a feature into a contextual layer based on P1 properties.
    This classification does NOT affect the mathematical risk score.
    """
    if props.land_cover_class == "Permanent water bodies":
        return "water"

    # Industrial/Mining Candidate
    # Generic signature: Extremely hot, highly anomalous, lack of vegetation, somewhat built/barren signature, not classified as standard Built-up
    is_extremely_hot = props.lst_c > 45.0
    is_highly_anomalous = props.lst_anomaly_c is not None and props.lst_anomaly_c > 4.0
    is_barren_or_built = props.ndbi_mean is not None and props.ndbi_mean > 0.0
    is_not_standard_urban = props.land_cover_class not in ["Built-up"]

    if is_extremely_hot and is_highly_anomalous and is_barren_or_built and is_not_standard_urban:
        return "industrial_mining_candidate"

    # Urban Heat Context
    # Generic signature: Must be explicitly classified as Built-up land cover AND is a heat hotspot relative to baseline or absolute thresholds.
    is_built_up_land = props.land_cover_class == "Built-up"
    is_hotspot = (props.lst_anomaly_c is not None and props.lst_anomaly_c > 1.0) or props.lst_c > 40.0

    if is_built_up_land and is_hotspot:
        return "urban_heat"

    return "terrestrial_other"
