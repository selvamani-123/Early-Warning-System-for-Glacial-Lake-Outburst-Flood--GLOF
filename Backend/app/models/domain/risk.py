from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class FeatureContribution(BaseModel):
    feature: str
    contribution_percent: float

class RiskAssessment(BaseModel):
    id: str = Field(..., description="Unique identifier")
    lake_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_risk: str
    confidence_score: float
    primary_driver: str
    feature_contributions: List[FeatureContribution] = Field(default_factory=list)
