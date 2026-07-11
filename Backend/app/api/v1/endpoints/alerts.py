from fastapi import APIRouter, Query, HTTPException
from app.core.database import get_db
from typing import List, Optional

router = APIRouter()

@router.get("")
@router.get("/")
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status (e.g., ACTIVE, HISTORICAL)"),
    severity: Optional[str] = Query(None, description="Filter by overall_situation/severity (e.g., CRITICAL, HIGH)"),
    lake_id: Optional[str] = Query(None, description="Filter by specific lake"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    db = get_db()
    
    query = {}
    if status:
        query["status"] = status.upper()
    if severity:
        query["overall_situation"] = severity.upper()
    if lake_id:
        query["lake_id"] = lake_id
        
    cursor = db["alerts"].find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit)
    alerts = await cursor.to_list(length=limit)
    
    total = await db["alerts"].count_documents(query)
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "alerts": alerts
    }
