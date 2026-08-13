from typing import Dict, Optional
from schemas import HotspotProperties

def clip_and_scale(value: float, min_val: float, max_val: float) -> float:
    """Clips a value to [min_val, max_val] and scales it to [0, 1]."""
    if max_val == min_val:
        return 0.0
    clipped = max(min_val, min(max_val, value))
    return (clipped - min_val) / (max_val - min_val)

def preprocess_features(properties: HotspotProperties) -> Dict[str, float]:
    """
    Normalizes the raw physical features into a 0-1 scale for the risk index.
    Missing optional features are excluded from the result.
    """
    normalized_features = {}
    
    # 1. Heat Exposure Features
    # LST Mean: Assuming typical urban range 25C to 55C
    normalized_features['norm_lst_mean'] = clip_and_scale(properties.lst_mean_c, 25.0, 55.0)
    
    # LST Anomaly: Assuming 0C to 10C anomaly range is critical
    normalized_features['norm_lst_anomaly'] = clip_and_scale(properties.lst_anomaly_c, 0.0, 10.0)

    # 2. Environmental Vulnerability Features (Optional)
    # NDVI: -1 to 1. Lower NDVI = Higher heat retention/vulnerability.
    # Inverse scaling: -1 maps to 1.0 (high vulnerability), 1 maps to 0.0
    if properties.ndvi_mean is not None:
        normalized_features['norm_inv_ndvi'] = 1.0 - clip_and_scale(properties.ndvi_mean, -1.0, 1.0)
        
    # NDBI: -1 to 1. Higher NDBI = Built up = Higher vulnerability.
    # Direct scaling: -1 maps to 0.0, 1 maps to 1.0 (high vulnerability)
    if properties.ndbi_mean is not None:
        normalized_features['norm_ndbi'] = clip_and_scale(properties.ndbi_mean, -1.0, 1.0)
        
    # NDWI: -1 to 1. Lower NDWI = Less water = Higher vulnerability.
    # Inverse scaling: -1 maps to 1.0 (high vulnerability), 1 maps to 0.0
    if properties.ndwi_mean is not None:
        normalized_features['norm_inv_ndwi'] = 1.0 - clip_and_scale(properties.ndwi_mean, -1.0, 1.0)
        
    return normalized_features
