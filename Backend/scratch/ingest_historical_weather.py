import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import datetime
from dotenv import load_dotenv
import sys

sys.path.append("c:/Users/SELVAMANI/Downloads/GLOF Sentinel (1)/GLOF Sentinel/Backend")

from app.services.data_ingestion.weather_ingestion import WeatherIngestionService
from app.services.data_ingestion.validator import DataValidator

load_dotenv("c:/Users/SELVAMANI/Downloads/GLOF Sentinel (1)/GLOF Sentinel/Backend/.env")
client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME", "glof_sentinel")]

async def main():
    service = WeatherIngestionService()
    
    lakes = await db["lakes"].find({}, {"id": 1, "name": 1, "latitude": 1, "longitude": 1}).to_list(100)
    
    now = datetime.datetime.utcnow()
    # 10 years
    start = (now - datetime.timedelta(days=3650)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    
    total_inserted = 0
    
    await db["daily_weather_history_new"].drop()
    
    for lake in lakes:
        lat = lake.get("latitude")
        lon = lake.get("longitude")
        if not DataValidator.is_valid_location(lat, lon):
            continue
            
        print(f"Fetching 10 years of data for {lake['name']}...")
        obs = await service.fetch_historical_weather(lat, lon, start, end)
        
        if not obs:
            print(f"Failed to fetch for {lake['name']}")
            continue
            
        docs = []
        for o in obs:
            docs.append({
                "lake_id": lake["id"],
                "date": o["timestamp"].split("T")[0], # Compatibility
                "temperature": o["temperature_c"], # Compatibility
                "rainfall": o["rainfall_mm"], # Compatibility
                
                "timestamp": o["timestamp"],
                "temperature_c": o["temperature_c"],
                "rainfall_mm": o["rainfall_mm"],
                "snowfall_mm": o["snowfall_mm"],
                "source": o["source"],
                "data_type": o["data_type"]
            })
            
        batch_size = 1000
        for i in range(0, len(docs), batch_size):
            await db["daily_weather_history_new"].insert_many(docs[i:i+batch_size])
            
        total_inserted += len(docs)
        print(f"Inserted {len(docs)} records for {lake['name']}")
        
        await asyncio.sleep(1)
        
    if total_inserted > 0:
        await db["daily_weather_history"].drop()
        await db["daily_weather_history_new"].rename("daily_weather_history")
        print(f"Success! Migrated {total_inserted} 10-year records from Open-Meteo.")
    else:
        print("Failed to fetch any data.")

asyncio.run(main())
