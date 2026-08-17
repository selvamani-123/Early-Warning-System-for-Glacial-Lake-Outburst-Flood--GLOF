import asyncio
import logging
from datetime import datetime, timezone
from app.core.database import get_db
from app.services.data_ingestion.weather_ingestion import WeatherIngestionService
from app.services.data_ingestion.validator import DataValidator

logger = logging.getLogger(__name__)

async def fetch_and_cache_weather():
    """
    Fetches real-time current weather data for all lakes from Open-Meteo
    and updates the current weather_cache in MongoDB.
    """
    logger.info("Starting background job: fetch_and_cache_weather")
    db = get_db()
    if db is None:
        logger.error("Database connection not ready.")
        return

    # Dynamically fetch all lakes from DB
    lakes = await db["lakes"].find({}, {"id": 1, "name": 1, "latitude": 1, "longitude": 1}).to_list(length=1000)
    
    weather_service = WeatherIngestionService()
    
    for lake in lakes:
        lat = lake.get("latitude")
        lon = lake.get("longitude")
        lake_id = lake.get("id")
        lake_name = lake.get("name")
        
        if not DataValidator.is_valid_location(lat, lon):
            continue
            
        try:
            current_obs = await weather_service.fetch_current_weather(lat, lon)
            
            if current_obs and DataValidator.validate_weather(current_obs.get("temperature_c"), current_obs.get("rainfall_mm")):
                # Ensure the cache uses the exact schema mandated
                cache_doc = {
                    "lake_id": lake_id,
                    "location_name": lake_name,
                    "latitude": lat,
                    "longitude": lon,
                    "timestamp": current_obs["timestamp"],
                    "temperature_c": current_obs["temperature_c"],
                    "min_temperature_c": current_obs.get("min_temperature_c"),
                    "rainfall_mm": current_obs["rainfall_mm"],
                    "precip_24h_mm": current_obs.get("precip_24h_mm"),
                    "humidity_percent": current_obs.get("humidity_percent"),
                    "snowfall_mm": current_obs.get("snowfall_mm", 0.0),
                    "wind_speed": current_obs.get("wind_speed"),
                    "wind_direction": current_obs.get("wind_direction"),
                    "wind_gusts": current_obs.get("wind_gusts"),
                    "source": current_obs["source"],
                    "data_type": current_obs["data_type"],
                    "last_updated": datetime.now(timezone.utc)
                }

                await db.weather_cache.update_one(
                    {"lake_id": lake_id},
                    {"$set": cache_doc},
                    upsert=True
                )
                logger.info(f"Successfully updated weather cache for {lake_name}")
            else:
                logger.warning(f"Invalid weather observation for {lake_name}")
        except Exception as e:
            logger.error(f"Failed to fetch weather for {lake_name}: {e}")

if __name__ == "__main__":
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    def mock_get_db():
        return AsyncIOMotorClient(os.getenv('MONGODB_URI'))['glof_sentinel']
        
    import app.core.database
    app.core.database.get_db = mock_get_db
    
    asyncio.run(fetch_and_cache_weather())
