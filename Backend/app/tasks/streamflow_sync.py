import asyncio
import logging
import httpx
from datetime import datetime
from app.core.database import get_db

logger = logging.getLogger(__name__)

async def fetch_and_cache_streamflow():
    from app.core.database import get_db
    db = get_db()
    
    # Get all rivers
    rivers_cursor = db["rivers"].find({})
    rivers = await rivers_cursor.to_list(length=1000)
    
    async with httpx.AsyncClient() as client:
        for river in rivers:
            river_id = river["id"]
            
            # Find a connected lake to get coordinates
            lake = await db["lakes"].find_one({"river_id": river_id})
            if not lake:
                continue
                
            lat = lake.get("latitude")
            lng = lake.get("longitude")
            
            if lat is None or lng is None:
                continue
                
            # Fetch past 90 days + 7 day forecast from Open-Meteo
            url = f"https://flood-api.open-meteo.com/v1/flood?latitude={lat}&longitude={lng}&daily=river_discharge&past_days=90&forecast_days=7"
            
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    data = resp.json()
                    daily = data.get("daily", {})
                    times = daily.get("time", [])
                    discharges = daily.get("river_discharge", [])
                    
                    if not times or not discharges:
                        continue
                        
                    current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
                    
                    bulk_ops = []
                    for t, d in zip(times, discharges):
                        if d is None:
                            continue
                            
                        is_forecast = t > current_date_str
                        
                        # Upsert each day's record
                        doc = {
                            "river_id": river_id,
                            "date": t,
                            "discharge": d,
                            "is_forecast": is_forecast
                        }
                        
                        await db["streamflow_history"].update_one(
                            {"river_id": river_id, "date": t},
                            {"$set": doc},
                            upsert=True
                        )
                        
                    logger.info(f"Successfully synced streamflow for river {river_id} ({len(times)} days)")
                else:
                    logger.error(f"Flood API returned {resp.status_code} for river {river_id}")
            except Exception as e:
                logger.error(f"Error fetching streamflow for river {river_id}: {e}")
                
if __name__ == "__main__":
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Mock get_db for testing standalone
    def mock_get_db():
        return AsyncIOMotorClient(os.getenv('MONGODB_URI'))['glof_sentinel']
        
    import app.core.database
    app.core.database.get_db = mock_get_db
    
    asyncio.run(fetch_and_cache_streamflow())
