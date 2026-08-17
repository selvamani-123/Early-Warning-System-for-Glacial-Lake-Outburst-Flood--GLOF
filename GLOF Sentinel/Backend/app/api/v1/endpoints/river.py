from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/relationships")
async def get_relationships():
    db = get_db()
    
    # Optimize N+1 queries by fetching all rivers first
    rivers_cursor = db["rivers"].find({}, {"id": 1, "name": 1, "_id": 0})
    rivers_map = {r["id"]: r.get("name", "Unknown River") async for r in rivers_cursor}
    
    lakes_cursor = db["lakes"].find({}, {"id": 1, "name": 1, "river_id": 1, "_id": 0})
    relationships = []
    
    async for lake in lakes_cursor:
        river_id = lake.get("river_id")
        if river_id and river_id in rivers_map:
            relationships.append({
                "lake_id": lake.get("id"),
                "river_id": river_id,
                "lake_name": lake.get("name", "Unknown Lake"),
                "river_name": rivers_map[river_id]
            })
            
    return {"relationships": relationships}

@router.get("/{river_id}/streamflow")
async def get_streamflow(river_id: str, time_window: str = Query("90d")):
    db = get_db()
    
    # Map time_window to days
    window_map = {
        "7d": 7, "30d": 30, "90d": 90,
        "1y": 365, "5y": 365*5, "10y": 365*10
    }
    days = window_map.get(time_window, 90)
    
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    cursor = db["streamflow_history"].find(
        {"river_id": river_id, "date": {"$gte": cutoff_date}},
        {"_id": 0}
    ).sort("date", 1)
    
    records = await cursor.to_list(length=5000)
    
    history = []
    forecast = []
    current = None
    
    for r in records:
        if r["is_forecast"]:
            forecast.append(r)
        else:
            history.append(r)
            if r["date"] == current_date_str:
                current = r
                
    if not current and history:
        current = history[-1]
        
    return {
        "current": current,
        "history": history,
        "forecast": forecast
    }

@router.get("/{river_id}")
async def get_river(river_id: str):
    db = get_db()
    
    river = await db["rivers"].find_one({"id": river_id}, {"_id": 0})
    if not river:
        raise HTTPException(status_code=404, detail="River not found")
        
    basin_id = river.get("basin_id")
    basin = {}
    if basin_id:
        basin_res = await db["basins"].find_one({"id": basin_id}, {"_id": 0})
        if basin_res:
            basin = basin_res
            
    lakes_cursor = db["lakes"].find({"river_id": river_id}, {"_id": 0})
    lakes = await lakes_cursor.to_list(length=100)
    
    settlements_cursor = db["settlements"].find({"river_id": river_id}, {"_id": 0})
    settlements = await settlements_cursor.to_list(length=100)
    
    return {
        "river": river,
        "basin": basin,
        "connected_lakes": lakes,
        "downstream_settlements": settlements
    }
