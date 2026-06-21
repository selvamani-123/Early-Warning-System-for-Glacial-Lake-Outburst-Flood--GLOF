from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DBAlert(BaseModel):
    severity: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DBPrediction(BaseModel):
    risk: str
    probability: float
    inputs: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
