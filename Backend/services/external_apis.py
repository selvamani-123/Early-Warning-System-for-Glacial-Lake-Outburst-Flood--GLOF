import httpx
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional
from utils.database import get_db

logger = logging.getLogger(__name__)

async def fetch_weather_data(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Fetch real-time weather data from Open-Meteo and cache in MongoDB for 15 minutes.
    """
    db = get_db()
    cache_col = db["weather_cache"]
    
    cache_key = f"{round(lat, 4)}_{round(lon, 4)}"
    cached = await cache_col.find_one({"_id": cache_key})
    
    if cached and datetime.utcnow() - cached["timestamp"] < timedelta(minutes=15):
        logger.info(f"Using cached weather data for {lat}, {lon}")
        return cached["data"]
        
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,cloud_cover&hourly=temperature_2m,precipitation&timezone=auto"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            
        await cache_col.update_one(
            {"_id": cache_key},
            {"$set": {"data": data, "timestamp": datetime.utcnow()}},
            upsert=True
        )
        logger.info(f"Fetched new weather data for {lat}, {lon}")
        return data
    except Exception as e:
        logger.error(f"Error fetching weather data from Open-Meteo: {e}")
        # Fallback to expired cache if available
        if cached:
            return cached["data"]
        return None

async def fetch_elevation_data(lat: float, lon: float) -> Optional[float]:
    """
    Fetch elevation data from Open-Meteo Elevation API (uses SRTM/Copernicus under the hood).
    Cache indefinitely as elevation rarely changes.
    """
    db = get_db()
    cache_col = db["elevation_cache"]
    
    cache_key = f"{round(lat, 4)}_{round(lon, 4)}"
    cached = await cache_col.find_one({"_id": cache_key})
    
    if cached:
        return cached["elevation"]
        
    url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lon}"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            
        elevation = data.get("elevation", [0])[0]
        
        await cache_col.update_one(
            {"_id": cache_key},
            {"$set": {"elevation": elevation, "timestamp": datetime.utcnow()}},
            upsert=True
        )
        return elevation
    except Exception as e:
        logger.error(f"Error fetching elevation data: {e}")
        return None
