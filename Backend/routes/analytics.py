from fastapi import APIRouter
from models.domain import DashboardSummary
from utils.database import get_db
import time

router = APIRouter()

@router.get("/api/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary():
    db = get_db()
    active_nodes = 128
    critical_alerts = 0
    
    if db is not None:
        # Example dynamic counts
        critical_alerts = await db.alerts.count_documents({"severity": "CRITICAL"})
        
    return DashboardSummary(
        activeNodes=active_nodes,
        criticalAlerts=critical_alerts,
        dataLatency="45ms",
        systemUptime="99.98%",
        lastSync=time.strftime("%H:%M:%S Z", time.gmtime())
    )

@router.get("/api/analytics")
async def get_analytics():
    db = get_db()
    if db is None:
        return {"error": "Database not connected"}
        
    # Aggregation for risk distribution
    pipeline = [{"$group": {"_id": "$risk", "count": {"$sum": 1}}}]
    cursor = db.predictions.aggregate(pipeline)
    risk_distribution = []
    async for doc in cursor:
        risk_distribution.append(doc)
        
    return {
        "models": [
            {"name": "RandomForest Environmental Flow", "accuracy": 99.9, "status": "Active"},
        ],
        "risk_distribution": risk_distribution
    }
