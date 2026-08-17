from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.core.database import get_db

router = APIRouter()

@router.get("")
@router.get("/")
async def get_live_monitoring():
    return {"message": "Live Monitoring is active via WebSocket at /ws/telemetry"}

@router.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket, lake_id: str = None):
    await websocket.accept()
    db = get_db()
    try:
        while True:
            # Fetch the most recent risk assessment
            query = {}
            if lake_id:
                query["lake_id"] = lake_id
            lake_name = None
            if lake_id:
                lake_obj = await db["lakes"].find_one({"id": lake_id})
                if lake_obj:
                    lake_name = lake_obj.get("name")
                    
            # Fetch weather from weather_cache using lake_name
            current_weather = None
            if lake_name:
                weather_cache = await db["weather_cache"].find_one({"location_name": lake_name})
                if weather_cache and "current" in weather_cache:
                    c = weather_cache["current"]
                    d = weather_cache.get("daily", {})
                    
                    temp_val = c.get("temperature_2m", 0)
                    hum_val = c.get("relative_humidity_2m", 50)
                    
                    import math
                    a = 17.27
                    b = 237.7
                    alpha = ((a * temp_val) / (b + temp_val)) + math.log(max(1, hum_val)/100.0)
                    dew_point = (b * alpha) / (a - alpha) if (a - alpha) != 0 else 0
                    
                    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                    wind_dir_deg = c.get("wind_direction_10m", 0)
                    ix = int((wind_dir_deg + 11.25)/22.5)
                    wind_dir_str = dirs[ix % 16]
                    
                    min_t = d.get("temperature_2m_min", [temp_val - 5])[0]
                    precip_sum = d.get("precipitation_sum", [0])[0]
                    curr_precip = c.get("precipitation") or c.get("rainfall", 0)
                    
                    intensity = "None"
                    if curr_precip > 5: intensity = "High Intensity"
                    elif curr_precip > 0: intensity = "Light"
                    
                    current_weather = {
                        "temperature": temp_val,
                        "min_temp": min_t,
                        "temp_trend": round((temp_val - min_t) / 12.0, 1), # mock trend based on diff
                        "rainfall": curr_precip,
                        "precip_24h": precip_sum,
                        "precip_intensity": intensity,
                        "humidity": hum_val,
                        "dew_point": round(dew_point, 1),
                        "wind": c.get("wind_speed_10m", 0),
                        "gust": c.get("wind_gusts_10m", c.get("wind_speed_10m", 0) * 1.5),
                        "wind_dir": wind_dir_str
                    }
                    
            if not current_weather:
                # Fallback to weather_history
                wh = await db["weather_history"].find_one({"lake_id": lake_id}) or {}
                temp_val = wh.get("avg_summer_temp_c", 0.0)
                current_weather = {
                    "temperature": temp_val,
                    "min_temp": round(temp_val - 4.5, 1),
                    "temp_trend": 0.2,
                    "rainfall": wh.get("annual_precip_mm", 0.0) / 365.0,
                    "precip_24h": wh.get("annual_precip_mm", 0.0) / 365.0,
                    "precip_intensity": "Stable",
                    "humidity": 50.0,
                    "dew_point": round(temp_val - 2.0, 1),
                    "wind": 10.0,
                    "gust": 15.0,
                    "wind_dir": "SW"
                }
                
            # Fetch the most recent risk assessment
            latest_assessment = await db["risk_assessments"].find_one(
                query, sort=[("timestamp", -1)], projection={"_id": 0}
            ) or {}
            
            payload = {
                "temperature": round(current_weather.get("temperature") or 0.0, 1),
                "min_temp": current_weather.get("min_temp"),
                "temp_trend": current_weather.get("temp_trend"),
                "rainfall": round(current_weather.get("rainfall") or 0.0, 1),
                "precip_24h": round(current_weather.get("precip_24h") or 0.0, 1),
                "precip_intensity": current_weather.get("precip_intensity"),
                "humidity": round(current_weather.get("humidity") or 0.0, 1),
                "dew_point": current_weather.get("dew_point"),
                "wind": round(current_weather.get("wind") or 0.0, 1),
                "gust": round(current_weather.get("gust") or 0.0, 1),
                "wind_dir": current_weather.get("wind_dir"),
                
                "water_accumulation": round(latest_assessment.get("engineered_features", {}).get("water_accumulation_score", 0), 1) if latest_assessment else 0.0,
                "ai_risk": latest_assessment.get("risk_level", "UNKNOWN") if latest_assessment else "UNKNOWN",
                "environmental_stress": latest_assessment.get("environmental_stress_category", "UNKNOWN") if latest_assessment else "UNKNOWN",
                "overall_situation": latest_assessment.get("decision_support", {}).get("overall_situation", "UNKNOWN") if latest_assessment else "UNKNOWN",
                "last_updated": latest_assessment.get("timestamp").isoformat() if latest_assessment and latest_assessment.get("timestamp") else None
            }
            await websocket.send_json(payload)
                
            await asyncio.sleep(5) # Poll every 5 seconds
    except WebSocketDisconnect:
        pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"WebSocket error: {e}")
