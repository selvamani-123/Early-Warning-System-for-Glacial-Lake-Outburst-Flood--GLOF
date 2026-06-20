import asyncio
import json
import random
import time
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GLOF Sentinel API",
    description="Early Warning System for Glacial Lake Outburst Floods",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Internal Async AI Prediction Queue (Replaces Celery/Redis for local running without Redis Server)
prediction_queue = asyncio.Queue()

async def ai_inference_worker():
    while True:
        telemetry_data = await prediction_queue.get()
        await asyncio.sleep(0.5) # Simulate processing delay
        
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
            
        if risk_level in ["High", "Critical"]:
            alert = {
                "type": "alert",
                "alertLevel": risk_level,
                "message": f"{risk_level} risk detected! Flood Probability: {round(risk_score, 1)}%",
                "lakeId": "N01-WL-A9"
            }
            await manager.broadcast(json.dumps(alert))
        prediction_queue.task_done()

@app.on_event("startup")
async def startup_event():
    # Start AI inference worker
    asyncio.create_task(ai_inference_worker())

    # Simulate hardware sensor pipeline
    async def data_generator():
        while True:
            await asyncio.sleep(2)
            data = {
                "type": "telemetry",
                "waterLevel": round(random.uniform(14.0, 18.5), 1),
                "waterLevelThreshold": 18.0,
                "waterLevelTrend": "+0.1m/h",
                "rainfall24h": round(random.uniform(40.0, 45.0), 1),
                "rainfall1h": round(random.uniform(1.0, 6.0), 1),
                "rainfallPeak": round(random.uniform(4.0, 6.0), 1),
                "temperature": round(random.uniform(-5.0, -3.0), 1),
                "outflowVelocity": int(random.uniform(140, 150)),
                "microTremors": round(random.uniform(1.0, 1.5), 1)
            }
            # Broadcast telemetry to dashboard
            await manager.broadcast(json.dumps(data))
            # Dispatch to async AI worker
            await prediction_queue.put(data)
    
    asyncio.create_task(data_generator())

@app.get("/api/dashboard-summary")
async def get_dashboard_summary():
    return {
        "activeNodes": 128,
        "criticalAlerts": 2,
        "dataLatency": "45ms",
        "systemUptime": "99.98%",
        "lastSync": time.strftime("%H:%M:%S Z", time.gmtime())
    }

@app.get("/api/alerts")
async def get_alerts():
    return [
        {"id": "A-101", "level": "Critical", "message": "Seismic anomaly detected at Moraine Wall C", "time": "14:02:45 Z"},
        {"id": "A-102", "level": "High", "message": "Precipitation exceeds 5mm/hr", "time": "12:30:12 Z"},
        {"id": "A-103", "level": "Moderate", "message": "Node 04 latency spike", "time": "10:15:00 Z"}
    ]

@app.get("/api/predictions")
async def get_predictions():
    return {
        "models": [
            {"name": "XGBoost Flow Prediction", "accuracy": 94.2, "status": "Active"},
            {"name": "Neural Net Seismic", "accuracy": 89.1, "status": "Active"},
            {"name": "Random Forest Weather", "accuracy": 91.5, "status": "Training"}
        ],
        "globalRisk": "High",
        "nextUpdate": "5 mins"
    }

@app.get("/api/map-data")
async def get_map_data():
    return [
        {"id": "N01-WL", "lat": 27.98, "lng": 86.92, "status": "Critical", "value": "14.2m"},
        {"id": "N02-RF", "lat": 27.99, "lng": 86.93, "status": "Warning", "value": "42.5mm"},
        {"id": "N03-TMP", "lat": 28.00, "lng": 86.91, "status": "Normal", "value": "-4.2°C"}
    ]

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."}
    )

# Serve Vanilla HTML Frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
