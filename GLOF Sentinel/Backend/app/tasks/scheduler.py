import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks.weather_sync import fetch_and_cache_weather
from app.tasks.glacier_sync import fetch_and_cache_glacier_metadata
from app.tasks.historical_sync import fetch_and_cache_historical_datasets
from app.tasks.streamflow_sync import fetch_and_cache_streamflow
from app.tasks.risk_sync import assess_all_lakes_risk

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def start_scheduler():
    """
    Initializes and starts the APScheduler.
    Registers all background jobs with their respective intervals.
    """
    if not scheduler.running:
        scheduler.add_job(fetch_and_cache_weather, 'interval', minutes=15, id='weather_sync', replace_existing=True)
        scheduler.add_job(assess_all_lakes_risk, 'interval', minutes=20, id='risk_sync', replace_existing=True)
        scheduler.add_job(fetch_and_cache_glacier_metadata, 'interval', hours=24, id='glacier_sync', replace_existing=True)
        scheduler.add_job(fetch_and_cache_historical_datasets, 'interval', days=7, id='historical_sync', replace_existing=True)
        scheduler.add_job(fetch_and_cache_streamflow, 'interval', hours=6, id='streamflow_sync', replace_existing=True)
        
        scheduler.start()
        logger.info("APScheduler started with background syncing jobs.")
