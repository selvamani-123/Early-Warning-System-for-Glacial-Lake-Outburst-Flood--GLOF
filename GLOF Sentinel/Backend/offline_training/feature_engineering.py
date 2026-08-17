import numpy as np
import pandas as pd

def calculate_melt_rate_index(temperature, elevation):
    """
    Estimates melt rate based on temperature and elevation.
    Higher temperature and lower elevation generally lead to higher melt rate,
    but here we assume elevation is a factor where higher altitude has steeper temperature gradients.
    """
    # Simple heuristic: base melt rate on positive temperature
    temp_factor = np.maximum(0, temperature)
    
    # Altitude effect: higher glaciers might melt faster if temperature is still high, 
    # but normally temperature drops with elevation.
    # For a given temperature at the glacier, higher elevation means it's unusually warm.
    elevation_factor = elevation / 5000.0 
    
    return temp_factor * elevation_factor * 0.1

def calculate_rainfall_intensity(current_rainfall, historical_avg_rainfall=5.0):
    """
    Calculates intensity of current rainfall compared to historical average.
    """
    if historical_avg_rainfall <= 0:
        return current_rainfall
    return current_rainfall / historical_avg_rainfall

def calculate_water_accumulation_score(rainfall, lake_area, melt_rate):
    """
    Water accumulation is a function of rainfall, melt inflow, divided by lake area capacity factor.
    Smaller lakes with high inflow fill up faster (higher score).
    """
    # Prevent division by zero
    lake_area_safe = np.maximum(0.1, lake_area)
    
    # Inflow proxy
    inflow = rainfall + (melt_rate * 50)
    
    return inflow / lake_area_safe

def calculate_seasonal_index(month, temperature):
    """
    Melt season is typically summer (months 6-9 in Northern Hemisphere).
    Returns a higher multiplier during melt season.
    """
    # If month is summer (June-Sept), higher index
    season_multiplier = 1.0
    if month in [6, 7, 8, 9]:
        season_multiplier = 1.5
    elif month in [5, 10]:
        season_multiplier = 1.2
        
    # Temperature effect on season
    temp_multiplier = 1.0 + np.maximum(0, temperature) / 20.0
    
    return season_multiplier * temp_multiplier

def apply_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies all feature engineering functions to a dataframe.
    Requires columns: temperature, elevation, rainfall, lake_area, month
    """
    df = df.copy()
    
    # Handle missing historical_avg_rainfall by assuming a default or using rolling mean if available
    historical_avg = 5.0
    
    # Ensure month exists
    if 'month' not in df.columns:
        df['month'] = 7  # Default to peak summer if missing
        
    df['melt_rate_index'] = calculate_melt_rate_index(df['temperature'], df['elevation'])
    df['rainfall_intensity'] = calculate_rainfall_intensity(df['rainfall'], historical_avg)
    df['water_accumulation_score'] = calculate_water_accumulation_score(df['rainfall'], df['lake_area'], df['melt_rate_index'])
    
    # Apply seasonal index
    df['seasonal_index'] = df.apply(lambda row: calculate_seasonal_index(row['month'], row['temperature']), axis=1)
    
    return df
