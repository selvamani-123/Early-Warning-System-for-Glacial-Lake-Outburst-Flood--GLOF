from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_db
import asyncio

router = APIRouter()

@router.get("")
@router.get("/")
async def get_historical_analysis(lake_id: str = Query(None, description="Filter by lake ID"), time_window: str = Query("30d", description="Time window")):
    db = get_db()
    
    # Map time_window to days
    window_map = {
        "30d": 30, "90d": 90, "1y": 365, "5y": 365*5, "10y": 365*10, "all": 365*50
    }
    days = window_map.get(time_window.lower(), 30)
    
    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
    
    if not lake_id:
        events = await db["historical_events"].find({}, {"_id": 0}).sort("event_date", -1).to_list(100)
        return {"historical_events": events}
        
    lake = await db["lakes"].find_one({"id": lake_id})
    river_id = lake.get("river_id") if lake else None
        
    tasks = [
        db["historical_events"].find({"lake_id": lake_id}, {"_id": 0}).sort("event_date", -1).to_list(100),
        db["daily_weather_history"].find({"lake_id": lake_id, "date": {"$gte": cutoff_date_str}}, {"_id": 0}).sort("date", 1).to_list(10000),
        db["risk_assessments"].find({"lake_id": lake_id, "timestamp": {"$gte": cutoff_date}}, {"_id": 0}).sort("timestamp", 1).to_list(100)
    ]
    
    if river_id:
        tasks.append(db["streamflow_history"].find({"river_id": river_id, "date": {"$gte": cutoff_date_str}, "is_forecast": False}, {"_id": 0}).sort("date", 1).to_list(10000))
    else:
        tasks.append(asyncio.sleep(0, result=[]))
    
    results = await asyncio.gather(*tasks)
    events = results[0] or []
    weather_history = results[1] or []
    assessments = results[2] or []
    streamflow = results[3] or []
    
    # Process Weather History to extract rainfall, temp, area
    rainfall_history = []
    temperature_history = []
    lake_area_history = []
    glacier_area_history = []
    environmental_stress = []
    
    for w in weather_history:
        date_str = w.get("date")
        rain = w.get("rainfall", 0)
        temp = w.get("temperature", 0)
        l_area = w.get("lake_area")
        g_area = w.get("glacier_area")
        
        # Proper Environmental Stress requires full feature engineering. 
        # For history, we will rely on ML models if stored, otherwise skip fake data.
        
        rainfall_history.append({"date": date_str, "value": rain})
        temperature_history.append({"date": date_str, "value": temp})
        if l_area is not None:
            lake_area_history.append({"date": date_str, "value": l_area})
        if g_area is not None:
            glacier_area_history.append({"date": date_str, "value": g_area})
        
    recent_ai_assessments = []
    for a in assessments:
        recent_ai_assessments.append({
            "timestamp": a.get("timestamp"),
            "risk_level": a.get("risk_level"),
            "explanation": a.get("explanation"),
            "probabilities": a.get("probabilities")
        })
        
    return {
        "lake_id": lake_id,
        "historical_events": events,
        "rainfall_history": rainfall_history,
        "temperature_history": temperature_history,
        "lake_area_history": lake_area_history,
        "glacier_area_history": glacier_area_history,
        "environmental_stress": environmental_stress,
        "recent_ai_assessments": recent_ai_assessments,
        "streamflow_history": streamflow
    }
