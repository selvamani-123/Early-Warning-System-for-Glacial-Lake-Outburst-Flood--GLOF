import os
# pyrefly: ignore [missing-import]
from celery import Celery
import json
# pyrefly: ignore [missing-import]
import redis
import time

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize Celery
celery_app = Celery(
    "glof_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Sync Redis client for the Celery worker
redis_client = redis.Redis.from_url(REDIS_URL)

@celery_app.task(name="process_telemetry")
def process_telemetry(telemetry_data: dict):
    """
    Simulates a Scikit-Learn ML inference task.
    In a real scenario, this would load the .pkl model and call model.predict(features).
    """
    time.sleep(0.5) # Simulate processing delay
    
    # Simple heuristic to simulate ML model based on water level and rainfall
    water_level = telemetry_data.get("waterLevel", 0)
    rainfall = telemetry_data.get("rainfall1h", 0)
    
    risk_score = (water_level / 18.0) * 50 + (rainfall / 5.0) * 50
    
    risk_level = "Low"
    if risk_score > 85:
        risk_level = "Critical"
    elif risk_score > 70:
        risk_level = "High"
    elif risk_score > 50:
        risk_level = "Moderate"
        
    prediction = {
        "lakeId": "N01-WL-A9",
        "probability": round(risk_score, 1),
        "riskLevel": risk_level,
        "recommendation": "Evacuate" if risk_level == "Critical" else "Issue Warning",
        "timestamp": time.time()
    }
    
    # If High or Critical, publish an alert to Redis so FastAPI can broadcast it to WebSockets
    if risk_level in ["High", "Critical"]:
        alert = {
            "type": "alert",
            "alertLevel": risk_level,
            "message": f"{risk_level} risk detected! Flood Probability: {prediction['probability']}%",
            "lakeId": prediction["lakeId"]
        }
        redis_client.publish("alerts", json.dumps(alert))
        
    return prediction
