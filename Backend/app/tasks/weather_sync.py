import httpx
from datetime import datetime, timezone
import logging
from app.core.database import get_db

logger = logging.getLogger(__name__)

async def fetch_and_cache_weather():
    """
    Runs every 15 minutes.
    Fetches weather data from Open-Meteo for monitored locations and caches in MongoDB.
    """
    logger.info("Starting background job: fetch_and_cache_weather")
    db = get_db()
    if db is None:
        logger.error("Database connection not ready.")
        return

    # In a real implementation, we would fetch coordinates from the `lake_cache` or a monitored locations list.
    # For now, we use a default coordinate (e.g., South Lhonak Lake: 27.75, 88.25)
    target_locations = [{"name": "South Lhonak Lake", "lat": 27.75, "lon": 88.25}]

    async with httpx.AsyncClient() as client:
        for loc in target_locations:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&current=temperature_2m,relative_humidity_2m,precipitation,snowfall,wind_speed_10m,wind_direction_10m,wind_gusts_10m&daily=temperature_2m_min,precipitation_sum&timezone=auto"
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                cache_doc = {
                    "location_name": loc["name"],
                    "latitude": loc["lat"],
                    "longitude": loc["lon"],
                    "timestamp": datetime.now(timezone.utc),
                    "current": data.get("current", {}),
                    "daily": data.get("daily", {}),
                    "source": "Open-Meteo"
                }

                await db.weather_cache.update_one(
                    {"location_name": loc["name"]},
                    {"$set": cache_doc},
                    upsert=True
                )
                logger.info(f"Successfully updated weather cache for {loc['name']}")
            except Exception as e:
                logger.error(f"Failed to fetch weather for {loc['name']}: {e}")
