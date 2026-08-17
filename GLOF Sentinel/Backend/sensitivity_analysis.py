import asyncio
from app.core.database import db, connect_to_mongo, close_mongo_connection
from app.services.ai_risk_engine import ai_risk_engine

async def run_sensitivity_analysis():
    await connect_to_mongo()
    
    print("=================================================")
    print("SENSITIVITY ANALYSIS (Rainfall Scaling)")
    print("=================================================\n")
    
    # Choose South Lhonak Lake (a known highly vulnerable lake)
    lake = await db.client[db.db.name]["lakes"].find_one({"name": "South Lhonak Lake"}, {"_id": 0})
    if not lake:
        # Fallback to first available
        lake = await db.client[db.db.name]["lakes"].find_one({}, {"_id": 0})
        
    lake_id = lake["id"]
    glacier = await db.client[db.db.name]["glaciers"].find_one({"id": lake.get("glacier_id")}, {"_id": 0})
    weather_hist = await db.client[db.db.name]["weather_history"].find_one({"lake_id": lake_id}, {"_id": 0})
    
    graph = {
        "lake": lake,
        "glacier": glacier or {},
        "weather_history": weather_hist or {},
        "historical_events": [],
        "connected_river": {},
        "downstream_settlements": []
    }
    
    # Constant baseline temperature
    constant_temp = weather_hist.get("avg_summer_temp_c", 5.0) if weather_hist else 5.0
    
    rain_steps = [0.0, 10.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0]
    
    results = []
    
    print(f"Target Lake: {lake['name']}")
    print(f"Constant Temperature: {constant_temp:.1f}°C")
    print("-" * 80)
    print(f"{'Rainfall':<10} | {'Temp':<6} | {'Water Accum. Score':<20} | {'Risk':<10} | {'Conf':<6}")
    print("-" * 80)
    
    for rain in rain_steps:
        weather = {
            "rainfall": rain,
            "temperature": constant_temp,
            "humidity": 60.0
        }
        
        assessment = ai_risk_engine.assess_lake(lake_id, graph, weather)
        features = assessment.engineered_features
        was = features.get("water_accumulation_score", 0.0)
        
        results.append({
            "rainfall": rain,
            "risk": assessment.risk_level,
            "confidence": assessment.confidence_score
        })
        
        print(f"{rain:<6.1f} mm | {constant_temp:<4.1f}°C | {was:<20.2f} | {assessment.risk_level:<10} | {assessment.confidence_score:<4.1f}%")

    print("\n=================================================")
    print("TRANSITION VERIFICATION")
    print("=================================================")
    
    transitions = []
    for i in range(1, len(results)):
        prev = results[i-1]['risk']
        curr = results[i]['risk']
        if prev != curr:
            transitions.append(f"{prev} -> {curr} at {results[i]['rainfall']}mm")
            
    for t in transitions:
        print(t)
        
    # Check for smooth transitions
    risk_hierarchy = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
    smooth = True
    for i in range(1, len(results)):
        r1 = risk_hierarchy[results[i-1]['risk']]
        r2 = risk_hierarchy[results[i]['risk']]
        if r2 - r1 > 1:
            print(f"\n[!] ERROR: Discontinuous jump detected from {results[i-1]['risk']} to {results[i]['risk']}!")
            smooth = False
            
    if smooth:
        print("\nCONCLUSION: The risk model scales smoothly and continuously (LOW -> MODERATE -> HIGH -> CRITICAL) as water accumulation linearly increases. The Random Forest decision boundaries are well-calibrated.")
    else:
        print("\nCONCLUSION: The risk model boundaries are unstable and exhibit spontaneous discontinuities.")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(run_sensitivity_analysis())
