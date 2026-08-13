from typing import Dict, List, Optional, Tuple
from schemas import HotspotProperties

# Base weights for features within their groups
EXPOSURE_WEIGHTS = {
    "norm_lst_mean": 0.4,
    "norm_lst_anomaly": 0.6
}

VULNERABILITY_WEIGHTS = {
    "norm_inv_ndvi": 0.4,
    "norm_ndbi": 0.4,
    "norm_inv_ndwi": 0.2
}

def calculate_group_score(normalized_features: Dict[str, float], base_weights: Dict[str, float]) -> Tuple[Optional[float], Dict[str, float]]:
    """
    Calculates a score for a group of features (exposure or vulnerability),
    renormalizing weights if any optional features are missing.
    Returns (score, effective_weights).
    """
    available_weights = {}
    for feature_name, weight in base_weights.items():
        if feature_name in normalized_features:
            available_weights[feature_name] = weight
            
    if not available_weights:
        return None, {}
        
    total_weight = sum(available_weights.values())
    
    score = 0.0
    effective_weights = {}
    for feature_name, original_weight in available_weights.items():
        # Renormalize weight so they sum to 1.0 within the group
        effective_weight = original_weight / total_weight
        effective_weights[feature_name] = effective_weight
        score += normalized_features[feature_name] * effective_weight
        
    return score, effective_weights

def get_risk_category(score: float) -> str:
    """Categorizes a 0-100 risk score."""
    if score >= 80:
        return "extreme"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "moderate"
    else:
        return "low"

def calculate_risk(normalized_features: Dict[str, float]) -> Dict:
    """
    Calculates the deterministic composite risk index, environmental vulnerability score,
    and the contributors list.
    """
    # 1. Calculate Heat Exposure (always present as LST is core)
    exposure_score, exposure_effective_weights = calculate_group_score(normalized_features, EXPOSURE_WEIGHTS)
    if exposure_score is None:
        exposure_score = 0.0 # Fallback, should not happen with valid input
        
    # 2. Calculate Environmental Vulnerability (Optional)
    vuln_score, vuln_effective_weights = calculate_group_score(normalized_features, VULNERABILITY_WEIGHTS)
    
    # 3. Combine into Overall Risk Score (0-100 scale)
    if vuln_score is not None:
        # 50% Exposure, 50% Vulnerability
        overall_risk = (exposure_score * 0.5 + vuln_score * 0.5) * 100.0
        final_exposure_multiplier = 0.5
        final_vuln_multiplier = 0.5
    else:
        # 100% Exposure if no vulnerability data
        overall_risk = exposure_score * 100.0
        final_exposure_multiplier = 1.0
        final_vuln_multiplier = 0.0
        
    # 4. Generate Contributors
    contributors = []
    
    for feature, eff_weight in exposure_effective_weights.items():
        abs_weight = eff_weight * final_exposure_multiplier
        contributors.append({
            "name": feature,
            "value": normalized_features[feature],
            "importance": abs_weight
        })
        
    if vuln_score is not None:
        for feature, eff_weight in vuln_effective_weights.items():
            abs_weight = eff_weight * final_vuln_multiplier
            contributors.append({
                "name": feature,
                "value": normalized_features[feature],
                "importance": abs_weight
            })
            
    # Sort contributors by importance (descending)
    contributors.sort(key=lambda x: x["importance"], reverse=True)
    
    return {
        "risk_score": overall_risk,
        "risk_category": get_risk_category(overall_risk),
        "vulnerability_score": vuln_score * 100.0 if vuln_score is not None else None,
        "contributors": contributors
    }
