from typing import Dict, Any, Tuple

def normalize(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to a 0.0 - 1.0 scale, capping at boundaries."""
    if value <= min_val:
        return 0.0
    if value >= max_val:
        return 1.0
    return (value - min_val) / (max_val - min_val)

def calculate_environmental_stress(features: Dict[str, float]) -> Tuple[float, str]:
    """
    Calculates the Environmental Stress Index (ESI) (0-100) based strictly on physical indicators.
    This is an independent scientific assessment of environmental instability, NOT a ML prediction.
    """
    
    # Extract features
    temp_anomaly = features.get("temp_anomaly", 0.0)
    rainfall_anomaly = features.get("rainfall_anomaly", 0.0)
    rainfall_intensity = features.get("rainfall_intensity", 0.0)
    melt_rate_index = features.get("melt_rate_index", 0.0)
    water_accum = features.get("water_accumulation_score", 0.0)
    
    # Normalize features to 0-1 scale based on theoretical extremes for high-altitude glacial lakes
    norm_temp = normalize(temp_anomaly, min_val=0.0, max_val=5.0)
    norm_rain_anom = normalize(rainfall_anomaly, min_val=0.0, max_val=100.0)
    norm_rain_int = normalize(rainfall_intensity, min_val=0.0, max_val=15.0)
    norm_melt = normalize(melt_rate_index, min_val=0.0, max_val=3.0)
    norm_water = normalize(water_accum, min_val=0.0, max_val=60.0)
    
    # Weightings (Total = 1.0)
    w_water = 0.35      # Highest weight: direct physical accumulation in lake
    w_rain_int = 0.25   # Immediate shock to the system
    w_temp = 0.15       # Sustained heatwave
    w_melt = 0.15       # Glacial structure weakening
    w_rain_anom = 0.10  # Long-term saturation
    
    # Calculate weighted score (0.0 to 1.0)
    raw_score = (
        (norm_water * w_water) +
        (norm_rain_int * w_rain_int) +
        (norm_temp * w_temp) +
        (norm_melt * w_melt) +
        (norm_rain_anom * w_rain_anom)
    )
    
    # Convert to 0-100 percentage
    esi_score = min(100.0, max(0.0, raw_score * 100.0))
    
    # Categorize
    if esi_score <= 30.0:
        category = "LOW"
    elif esi_score <= 60.0:
        category = "MODERATE"
    elif esi_score <= 85.0:
        category = "HIGH"
    else:
        category = "EXTREME"
        
    return esi_score, category
