from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PredictionRequest(BaseModel):
    rainfall: float
    temperature: float
    elevation: float
    lake_area: float
    glacier_area: float
    humidity: float
    month: Optional[int] = None

class PredictionResponse(BaseModel):
    risk: str
    probability: float
    feature_importance: Optional[dict] = None

class AlertResponse(BaseModel):
    id: str
    severity: str
    message: str
    timestamp: str

class MapDataPoint(BaseModel):
    id: str
    lat: float
    lng: float
    status: str
    value: str

class DashboardSummary(BaseModel):
    activeNodes: int
    criticalAlerts: int
    dataLatency: str
    systemUptime: str
    lastSync: str
