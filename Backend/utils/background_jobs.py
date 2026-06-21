import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
from datetime import datetime, timezone
from utils.database import get_db

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

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
            url = f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m&hourly=temperature_2m&timezone=auto"
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # Format document
                cache_doc = {
                    "location_name": loc["name"],
                    "latitude": loc["lat"],
                    "longitude": loc["lon"],
                    "timestamp": datetime.now(timezone.utc),
                    "current": data.get("current", {}),
                    "source": "Open-Meteo"
                }

                # Update or insert into MongoDB
                await db.weather_cache.update_one(
                    {"location_name": loc["name"]},
                    {"$set": cache_doc},
                    upsert=True
                )
                logger.info(f"Successfully updated weather cache for {loc['name']}")
            except Exception as e:
                logger.error(f"Failed to fetch weather for {loc['name']}: {e}")

async def fetch_and_cache_glacier_metadata():
    """
    Runs every 24 hours.
    Fetches GLIMS/RGI data and updates `glacier_cache` and `lake_cache`.
    """
    logger.info("Starting background job: fetch_and_cache_glacier_metadata")
    db = get_db()
    if db is None:
        return
    # Placeholder: Implementation for fetching from GLIMS/RGI APIs or static GeoJSON sources
    # Update db.glacier_cache and db.lake_cache
    logger.info("Glacier metadata cache updated.")

async def fetch_and_cache_historical_datasets():
    """
    Runs every 7 days.
    Updates historical GLOF events and long-term trends into `historical_events`.
    """
    logger.info("Starting background job: fetch_and_cache_historical_datasets")
    db = get_db()
    if db is None:
        return
    # Placeholder: Implementation for fetching from ICIMOD or historical databases
    # Update db.historical_events
    logger.info("Historical datasets cache updated.")

def start_scheduler():
    """
    Initializes and starts the APScheduler.
    Registers all background jobs with their respective intervals.
    """
    if not scheduler.running:
        # Every 15 minutes
        scheduler.add_job(fetch_and_cache_weather, 'interval', minutes=15, id='weather_sync', replace_existing=True)
        # Every 24 hours
        scheduler.add_job(fetch_and_cache_glacier_metadata, 'interval', hours=24, id='glacier_sync', replace_existing=True)
        # Every 7 days
        scheduler.add_job(fetch_and_cache_historical_datasets, 'interval', days=7, id='historical_sync', replace_existing=True)
        
        scheduler.start()
        logger.info("APScheduler started with background syncing jobs.")
