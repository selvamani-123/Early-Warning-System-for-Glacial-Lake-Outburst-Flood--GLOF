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
                if weather_cache:
                    temp_val = weather_cache.get("temperature_c", 0)
                    min_t = weather_cache.get("min_temperature_c")
                    if min_t is None: min_t = temp_val - 5
                    
                    hum_val = weather_cache.get("humidity_percent", 50)
                    
                    # Calculate Dew Point
                    import math
                    a = 17.27
                    b = 237.7
                    alpha = ((a * temp_val) / (b + temp_val)) + math.log(max(1, hum_val)/100.0)
                    dew_point = (b * alpha) / (a - alpha) if (a - alpha) != 0 else 0
                    
                    # Process Wind Direction
                    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                    wind_dir_deg = weather_cache.get("wind_direction", 0)
                    ix = int((wind_dir_deg + 11.25)/22.5)
                    wind_dir_str = dirs[ix % 16]
                    
                    curr_precip = weather_cache.get("rainfall_mm", 0)
                    precip_24h = weather_cache.get("precip_24h_mm", curr_precip)
                    
                    intensity = "None"
                    if curr_precip > 5: intensity = "High Intensity"
                    elif curr_precip > 0: intensity = "Light"
                    
                    current_weather = {
                        "temperature": temp_val,
                        "min_temp": min_t,
                        "temp_trend": round((temp_val - min_t) / 12.0, 1) if min_t else 0,
                        "rainfall": curr_precip,
                        "precip_24h": precip_24h,
                        "precip_intensity": intensity,
                        "humidity": hum_val,
                        "dew_point": round(dew_point, 1),
                        "wind": weather_cache.get("wind_speed", 0),
                        "gust": weather_cache.get("wind_gusts", weather_cache.get("wind_speed", 0) * 1.5),
                        "wind_dir": wind_dir_str
                    }
                    
            if not current_weather:
                # If absolute failure, return placeholders so the UI doesn't crash, but explicitly label them
                current_weather = {
                    "temperature": 0.0,
                    "min_temp": 0.0,
                    "temp_trend": 0.0,
                    "rainfall": 0.0,
                    "precip_24h": 0.0,
                    "precip_intensity": "DATA UNAVAILABLE",
                    "humidity": 0.0,
                    "dew_point": 0.0,
                    "wind": 0.0,
                    "gust": 0.0,
                    "wind_dir": "N/A"
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
