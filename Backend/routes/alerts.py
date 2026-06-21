from fastapi import APIRouter
from typing import List
from models.domain import AlertResponse
from utils.database import get_db

router = APIRouter()

@router.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts():
    db = get_db()
    if db is None:
        return []
        
    cursor = db.alerts.find().sort("timestamp", -1).limit(50)
    alerts = []
    async for doc in cursor:
        alerts.append(AlertResponse(
            id=str(doc["_id"]),
            severity=doc["severity"],
            message=doc["message"],
            timestamp=doc["timestamp"].strftime("%H:%M:%S Z")
        ))
        
    return alerts
