import pandas as pd
import requests
import time
import numpy as np
from datetime import datetime, timedelta

def get_real_glacier_metadata():
    """
    Simulates fetching from GLIMS/NASA EarthData by returning a curated list 
    of known high-risk glacial lakes in the Himalayas and Andes.
    In a fully productionized system, this would query the NSIDC/GLIMS APIs.
    """
    glaciers = [
        {"name": "Imja Tsho", "lat": 27.89, "lon": 86.92, "elevation": 5010, "lake_area": 1.28, "glacier_area": 4.5},
        {"name": "Tsho Rolpa", "lat": 27.88, "lon": 86.48, "elevation": 4580, "lake_area": 1.54, "glacier_area": 12.0},
        {"name": "South Lhonak", "lat": 27.91, "lon": 88.20, "elevation": 5200, "lake_area": 1.26, "glacier_area": 5.0},
        {"name": "Palcacocha", "lat": -9.39, "lon": -77.38, "elevation": 4566, "lake_area": 0.51, "glacier_area": 2.1},
        {"name": "Thorthormi", "lat": 28.05, "lon": 90.06, "elevation": 4428, "lake_area": 1.28, "glacier_area": 3.8},
        {"name": "Lugge Tsho", "lat": 28.05, "lon": 90.03, "elevation": 4350, "lake_area": 1.10, "glacier_area": 3.2},
        {"name": "Chungar", "lat": 27.99, "lon": 88.10, "elevation": 4800, "lake_area": 0.8, "glacier_area": 4.2},
        {"name": "Merzbacher", "lat": 42.20, "lon": 79.85, "elevation": 3304, "lake_area": 4.5, "glacier_area": 45.0}, # Tien Shan
    ]
    return pd.DataFrame(glaciers)

def fetch_historical_weather(lat, lon, start_date, end_date):
    """
    Fetches real historical weather data from Open-Meteo.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        df = pd.DataFrame({
            "date": daily.get("time", []),
            "temp_max": daily.get("temperature_2m_max", []),
            "temp_min": daily.get("temperature_2m_min", []),
            "rainfall": daily.get("rain_sum", [])
        })
        
        # Approximate average daily temp
        df['temperature'] = (df['temp_max'] + df['temp_min']) / 2.0
        # Basic humidity approximation since historical humidity might not be always available 
        # (we assume 65% base + some randomness, or if rain > 0, 85%)
        df['humidity'] = np.where(df['rainfall'] > 0, np.random.uniform(75, 95, len(df)), np.random.uniform(40, 70, len(df)))
        df['month'] = pd.to_datetime(df['date']).dt.month
        return df[['date', 'month', 'temperature', 'rainfall', 'humidity']]
        
    except Exception as e:
        print(f"Failed to fetch weather for {lat},{lon}: {e}")
        return pd.DataFrame()

def build_dataset(years_back=5):
    """
    Builds the unified dataset.
    """
    print("Fetching glacier metadata...")
    glaciers_df = get_real_glacier_metadata()
    
    end_date = datetime.now() - timedelta(days=5) # open-meteo archive delay
    start_date = end_date - timedelta(days=365 * years_back)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    all_data = []
    
    for _, glacier in glaciers_df.iterrows():
        print(f"Fetching historical weather for {glacier['name']}...")
        weather_df = fetch_historical_weather(glacier['lat'], glacier['lon'], start_str, end_str)
        time.sleep(1) # rate limiting
        
        if not weather_df.empty:
            # Merge
            weather_df['lake_name'] = glacier['name']
            weather_df['elevation'] = glacier['elevation']
            weather_df['lake_area'] = glacier['lake_area']
            weather_df['glacier_area'] = glacier['glacier_area']
            all_data.append(weather_df)
            
    if not all_data:
        raise Exception("Failed to fetch any data.")
        
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Fill any NaNs
    final_df['temperature'] = final_df['temperature'].fillna(final_df['temperature'].mean())
    final_df['rainfall'] = final_df['rainfall'].fillna(0)
    
    return final_df

if __name__ == "__main__":
    df = build_dataset(years_back=3)
    df.to_csv("historical_glof_data.csv", index=False)
    print(f"Saved {len(df)} records to historical_glof_data.csv")
