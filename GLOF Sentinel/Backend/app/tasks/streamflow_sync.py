import asyncio
import logging
from datetime import datetime
from app.core.database import get_db
from app.services.data_ingestion.glofas_ingestion import GlofasIngestionService
from app.services.data_ingestion.validator import DataValidator

logger = logging.getLogger(__name__)

async def fetch_and_cache_streamflow():
    db = get_db()
    
    # Get all rivers
    rivers_cursor = db["rivers"].find({})
    rivers = await rivers_cursor.to_list(length=1000)
    
    glofas_service = GlofasIngestionService()
    
    for river in rivers:
        river_id = river["id"]
        
        # Find a connected lake to get coordinates as a proxy for the river head
        lake = await db["lakes"].find_one({"river_id": river_id})
        if not lake:
            continue
            
        lat = lake.get("latitude")
        lng = lake.get("longitude")
        
        if not DataValidator.is_valid_location(lat, lng):
            continue
            
        now = datetime.utcnow()
        import datetime as dt
        start = (now - dt.timedelta(days=90)).strftime("%Y-%m-%d")
        end = (now + dt.timedelta(days=7)).strftime("%Y-%m-%d")
        
        try:
            observations = await glofas_service.fetch_historical_discharge(lat, lng, start, end)
            
            if not observations:
                continue
                
            current_date_str = now.strftime("%Y-%m-%d")
            
            for obs in observations:
                t = obs["timestamp"].split("T")[0]
                d = obs["discharge_m3s"]
                
                if not DataValidator.validate_discharge(d):
                    continue
                    
                is_forecast = t > current_date_str
                
                doc = {
                    "river_id": river_id,
                    "date": t,
                    "discharge": d,
                    "is_forecast": is_forecast,
                    "source": obs["source"],
                    "data_type": obs["data_type"]
                }
                
                await db["streamflow_history"].update_one(
                    {"river_id": river_id, "date": t},
                    {"$set": doc},
                    upsert=True
                )
                
            logger.info(f"Successfully synced streamflow for river {river_id} ({len(observations)} days)")
            
        except Exception as e:
            logger.error(f"Error fetching streamflow for river {river_id}: {e}")
            
if __name__ == "__main__":
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    def mock_get_db():
        return AsyncIOMotorClient(os.getenv('MONGODB_URI'))['glof_sentinel']
        
    import app.core.database
    app.core.database.get_db = mock_get_db
    
    asyncio.run(fetch_and_cache_streamflow())
