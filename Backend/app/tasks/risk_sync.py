import logging
import asyncio
from datetime import datetime, timezone
from app.core.database import get_db
from app.services.ai_risk_engine import ai_risk_engine

logger = logging.getLogger(__name__)

async def assess_all_lakes_risk():
    """
    Background job to periodically run the AI risk engine for all lakes,
    save the risk assessments, update the 'current_risk' on the lakes collection,
    and generate necessary alerts.
    """
    try:
        db = get_db()
        lakes = await db["lakes"].find({}, {"_id": 0}).to_list(length=None)
        
        logger.info(f"Starting global AI risk assessment for {len(lakes)} lakes...")
        
        for lake in lakes:
            lake_id = lake["id"]
            
            # Fetch context
            glacier = await db["glaciers"].find_one({"id": lake.get("glacier_id")}, {"_id": 0}) or {}
            basin = await db["basins"].find_one({"id": lake.get("basin_id")}, {"_id": 0}) or {}
            river = await db["rivers"].find_one({"id": lake.get("river_id")}, {"_id": 0}) or {}
            settlements = await db["settlements"].find({"river_id": lake.get("river_id")}, {"_id": 0}).to_list(length=100) if lake.get("river_id") else []
            historical = await db["historical_events"].find({"lake_id": lake_id}, {"_id": 0}).to_list(length=100)
            
            graph = {
                "lake": lake,
                "glacier": glacier,
                "basin": basin,
                "river": river,
                "settlements": settlements,
                "historical_events": historical
            }
            
            # Fetch latest weather cache for the lake's location
            weather_cache = await db["weather_cache"].find_one({"location_name": lake.get("name")})
            current_weather = None
            if weather_cache and "current" in weather_cache:
                current_weather = {
                    "temperature": weather_cache["current"].get("temperature_2m", 0),
                    "rainfall": weather_cache["current"].get("precipitation", 0),
                    "humidity": weather_cache["current"].get("relative_humidity_2m", 50)
                }
            
            if not current_weather:
                weather_hist = await db["weather_history"].find_one({"lake_id": lake_id}) or {}
                current_weather = {
                    "temperature": weather_hist.get("avg_summer_temp_c", 5.0),
                    "rainfall": weather_hist.get("annual_precip_mm", 1000.0) / 365.0,
                    "humidity": 50.0
                }
                
            # Run AI Engine
            assessment = await ai_risk_engine.assess_lake(lake_id, graph, current_weather)
            assessment_dict = assessment.model_dump()
            
            # Save Assessment
            await db["risk_assessments"].insert_one(assessment_dict.copy())
            
            # **CRUCIAL**: Update the current_risk on the lakes collection!
            await db["lakes"].update_one(
                {"id": lake_id},
                {"$set": {"current_risk": assessment.risk_level}}
            )
            
            # Generate Alerts
            overall_situation = assessment_dict.get("decision_support", {}).get("overall_situation", "").upper()
            if overall_situation in ["HIGH", "CRITICAL", "ESCALATING"]:
                alert_doc = {
                    "lake_id": lake_id,
                    "lake_name": lake.get("name"),
                    "glacier_name": glacier.get("name"),
                    "river_name": river.get("name"),
                    "basin_name": basin.get("name"),
                    "affected_settlements": assessment_dict.get("decision_support", {}).get("affected_settlements", []),
                    "risk_level": assessment_dict.get("risk_level"),
                    "environmental_stress_category": assessment_dict.get("environmental_stress_category"),
                    "overall_situation": assessment_dict.get("decision_support", {}).get("overall_situation"),
                    "confidence_score": assessment_dict.get("confidence_score"),
                    "feature_contributions": assessment_dict.get("feature_contributions"),
                    "recommended_actions": assessment_dict.get("decision_support", {}).get("recommended_actions"),
                    "timestamp": assessment_dict.get("timestamp"),
                    "assessment_mode": assessment_dict.get("assessment_mode"),
                    "status": "ACTIVE"
                }
                
                existing = await db["alerts"].find_one({
                    "lake_id": lake_id,
                    "status": "ACTIVE",
                    "overall_situation": alert_doc["overall_situation"]
                })
                if existing:
                    await db["alerts"].update_one(
                        {"_id": existing["_id"]},
                        {"$set": {
                            "timestamp": alert_doc["timestamp"],
                            "recommended_actions": alert_doc["recommended_actions"],
                            "confidence_score": alert_doc["confidence_score"]
                        }}
                    )
                else:
                    await db["alerts"].insert_one(alert_doc)
            
        logger.info("Global AI risk assessment completed.")
    except Exception as e:
        logger.error(f"Error during global risk assessment: {e}")
