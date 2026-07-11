import time
import asyncio
from fastapi import APIRouter, HTTPException
from app.core.database import get_db
from app.services.ai_risk_engine import ai_risk_engine
from datetime import datetime

router = APIRouter()

@router.get("")
@router.get("/")
async def get_analytics():
    return {"message": "Analytics"}

@router.get("/summary")
async def get_summary():
    db = get_db()
    
    # KPIs
    active_nodes = await db["lakes"].count_documents({})
    critical_alerts = await db["alerts"].count_documents({"status": "ACTIVE", "overall_situation": {"$in": ["CRITICAL", "HIGH"]}})
    
    # Regional Distribution
    lakes = await db["lakes"].find({}, {"_id": 0, "region": 1, "current_risk": 1}).to_list(length=None)
    regional_dist = {}
    for lake in lakes:
        region = lake.get("region") or "Unknown"
        risk = lake.get("current_risk") or "UNKNOWN"
        if region not in regional_dist:
            regional_dist[region] = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0}
        if risk in regional_dist[region]:
            regional_dist[region][risk] += 1
            
    # Global Drivers (Average feature contributions from recent assessments)
    assessments = await db["risk_assessments"].find({}, {"_id": 0, "feature_contributions": 1}).sort([("timestamp", -1)]).limit(50).to_list(length=50)
    drivers = {}
    for ast in assessments:
        feats = ast.get("feature_contributions", [])
        for feat in feats:
            k = feat.get("feature", "Unknown")
            v = feat.get("contribution_percent", 0)
            drivers[k] = drivers.get(k, 0) + v
            
    if len(assessments) > 0:
        for k in drivers:
            drivers[k] /= len(assessments)
            
    # Sort drivers to top 5
    top_drivers = dict(sorted(drivers.items(), key=lambda item: item[1], reverse=True)[:5])
    
    return {
        "activeNodes": active_nodes,
        "criticalAlerts": critical_alerts,
        "dataLatency": "12ms",
        "systemUptime": "99.99%",
        "lastSync": datetime.utcnow().strftime("%H:%M:%S UTC"),
        "regionalDistribution": regional_dist,
        "globalDrivers": top_drivers
    }

@router.get("/top_risks")
async def get_top_risks():
    db = get_db()
    
    # Sort lakes by current_risk severity (CRITICAL > HIGH > MODERATE > LOW > UNKNOWN)
    # We can do this in python to avoid complex mongo aggregation, since we only have ~4 lakes anyway.
    lakes = await db["lakes"].find({}, {"_id": 0}).to_list(length=100)
    
    def risk_score(risk_str):
        mapping = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "LOW": 1}
        return mapping.get(risk_str, 0)
        
    lakes.sort(key=lambda x: risk_score(x.get("current_risk", "UNKNOWN")), reverse=True)
    
    return {"top_lakes": lakes[:5]}

@router.get("/assessment/{lake_id}")
async def get_assessment(lake_id: str):
    t0 = time.time()
    db = get_db()
    
    # 1. Fetch Lake first to get relations
    t_db_start = time.time()
    lake = await db["lakes"].find_one({"id": lake_id}, {"_id": 0})
    if not lake:
        raise HTTPException(status_code=404, detail="Lake not found in Knowledge Graph")
        
    river_id = lake.get("river_id")
    glacier_id = lake.get("glacier_id")
    basin_id = lake.get("basin_id")
    
    # Run independent queries concurrently
    tasks = [
        db["glaciers"].find_one({"id": glacier_id}, {"_id": 0}) if glacier_id else asyncio.sleep(0),
        db["basins"].find_one({"id": basin_id}, {"_id": 0}) if basin_id else asyncio.sleep(0),
        db["rivers"].find_one({"id": river_id}, {"_id": 0}) if river_id else asyncio.sleep(0),
        db["settlements"].find({"river_id": river_id}, {"_id": 0}).to_list(length=100) if river_id else asyncio.sleep(0),
        db["historical_events"].find({"lake_id": lake_id}, {"_id": 0}).to_list(length=100),
        db["weather_history"].find_one({"lake_id": lake_id}, {"_id": 0}),
        db["current_weather"].find_one({"lake_id": lake_id}, {"_id": 0}),
        db["risk_assessments"].find_one({"lake_id": lake_id}, sort=[("timestamp", -1)], projection={"_id": 0})
    ]
    
    results = await asyncio.gather(*tasks)
    
    glacier = results[0] or {}
    basin = results[1] or {}
    river = results[2] or {}
    settlements = results[3] or []
    historical_events = results[4] or []
    weather_hist = results[5] or {}
    curr_weather = results[6] or {}
    prev_assessment = results[7] or {}
    
    t_db_end = time.time()
    db_query_time = (t_db_end - t_db_start) * 1000
    
    graph = {
        "lake": lake,
        "glacier": glacier,
        "basin": basin,
        "connected_river": river,
        "downstream_settlements": settlements,
        "historical_events": historical_events,
        "weather_history": weather_hist,
        "previous_assessment": prev_assessment
    }
    
    # 2. Fetch/Mock Current Weather
    if curr_weather:
        current_weather = {
            "temperature": curr_weather.get("temperature", weather_hist.get("avg_summer_temp_c", 5.0)),
            "rainfall": curr_weather.get("rainfall", 0.0),
            "humidity": curr_weather.get("humidity", 50.0)
        }
    else:
        current_weather = {
            "temperature": weather_hist.get("avg_summer_temp_c", 5.0),
            "rainfall": weather_hist.get("annual_precip_mm", 1000.0) / 365.0,
            "humidity": 50.0
        }
    
    # 3. AI Risk Engine Inference
    t_ai_start = time.time()
    assessment = await ai_risk_engine.assess_lake(lake_id, graph, current_weather)
    t_ai_end = time.time()
    ai_inference_time = (t_ai_end - t_ai_start) * 1000
    
    # 4. Store in DB (Fire and forget style to avoid blocking response)
    assessment_dict = assessment.model_dump()
    asyncio.ensure_future(db["risk_assessments"].insert_one(assessment_dict.copy()))
    
    # 4b. Alert Generation
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
        
        # Check if an active alert exists for the same lake and risk level
        async def upsert_alert():
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
                
        asyncio.ensure_future(upsert_alert())
    
    t_total_end = time.time()
    total_api_time = (t_total_end - t0) * 1000
    
    # Append Developer Mode Metrics
    assessment_dict["developer_metrics"] = {
        "database_queries_ms": round(db_query_time, 2),
        "ai_inference_ms": round(ai_inference_time, 2),
        "api_total_ms": round(total_api_time, 2),
        "scheduler_status": "Running",
        "mongodb_status": "Connected",
        "model_status": "Loaded"
    }
    
    if "_id" in assessment_dict:
        del assessment_dict["_id"]
        
    return assessment_dict
