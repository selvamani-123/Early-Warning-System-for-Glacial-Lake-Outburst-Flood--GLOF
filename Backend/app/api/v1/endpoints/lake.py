from fastapi import APIRouter, HTTPException
from app.core.database import get_db

router = APIRouter()

@router.get("/{lake_id}")
async def get_lake(lake_id: str):
    db = get_db()
    
    # Fetch Lake
    lake = await db["lakes"].find_one({"id": lake_id}, {"_id": 0})
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found")
        
    # Fetch Related Entities concurrently or sequentially
    glacier = await db["glaciers"].find_one({"id": lake.get("glacier_id")}, {"_id": 0})
    basin = await db["basins"].find_one({"id": lake.get("basin_id")}, {"_id": 0})
    river = await db["rivers"].find_one({"id": lake.get("river_id")}, {"_id": 0})
    
    # Fetch Array Entities
    settlements_cursor = db["settlements"].find({"river_id": lake.get("river_id")}, {"_id": 0})
    settlements = await settlements_cursor.to_list(length=100)
    
    history_cursor = db["historical_events"].find({"lake_id": lake_id}, {"_id": 0})
    historical_events = await history_cursor.to_list(length=100)
    
    weather = await db["weather_cache"].find_one({"lake_id": lake_id}, {"_id": 0})
    
    return {
        "lake": lake,
        "glacier": glacier,
        "basin": basin,
        "connected_river": river,
        "downstream_settlements": settlements,
        "historical_events": historical_events,
        "weather_cache": weather
    }
