from fastapi import APIRouter, HTTPException, Query
from app.core.database import get_db
import asyncio

router = APIRouter()

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
        db["risk_assessments"].find({"lake_id": lake_id, "timestamp": {"$gte": cutoff_date}}, {"_id": 0}).sort("timestamp", 1).to_list(10000)
    ]
    
    if river_id:
        tasks.append(db["streamflow_history"].find({"river_id": river_id, "date": {"$gte": cutoff_date_str}, "is_forecast": False}, {"_id": 0}).sort("date", 1).to_list(10000))
    else:
        tasks.append(asyncio.sleep(0, result=[]))
    
    results = await asyncio.gather(*tasks)
    events = results[0] or []
    assessments = results[1] or []
    streamflow = results[2] or []
    
    # Process Risk Assessments to extract weather, area, risk, and stress
    rainfall_history = []
    temperature_history = []
    lake_area_history = []
    glacier_area_history = []
    recent_ai_assessments = []
    environmental_stress = []
    
    for a in assessments:
        ts = a.get("timestamp")
        features = a.get("engineered_features", {})
        
        rain = features.get("rainfall", 0)
        temp = features.get("temperature", 0)
        l_area = features.get("lake_area", 0)
        g_area = features.get("glacier_area", 0)
        
        # Environmental stress derived from temp anomaly and rainfall intensity
        stress = min(100, max(0, (features.get("temp_anomaly", 0) * 2) + (features.get("rainfall_intensity", 0) * 10) + (features.get("water_accumulation_score", 0))))
        
        rainfall_history.append({"date": ts, "value": rain})
        temperature_history.append({"date": ts, "value": temp})
        lake_area_history.append({"date": ts, "value": l_area})
        glacier_area_history.append({"date": ts, "value": g_area})
        environmental_stress.append({"date": ts, "value": stress})
        
        recent_ai_assessments.append({
            "timestamp": ts,
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
