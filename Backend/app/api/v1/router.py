from fastapi import APIRouter
from app.api.v1.endpoints import registry, lake, river, history, monitoring, alerts, analytics

api_router = APIRouter()
api_router.include_router(registry.router, prefix="/registry", tags=["Registry"])
api_router.include_router(lake.router, prefix="/lake", tags=["Lake Intelligence"])
api_router.include_router(river.router, prefix="/river", tags=["River Intelligence"])
api_router.include_router(history.router, prefix="/history", tags=["Historical Analysis"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Live Monitoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
