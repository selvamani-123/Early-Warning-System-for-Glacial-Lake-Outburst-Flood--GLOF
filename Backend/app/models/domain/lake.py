from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class LakeMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the lake")
    name: str = Field(..., description="Name of the glacial lake")
    glacier_id: str = Field(..., description="Reference to Glacier collection")
    river_id: str = Field(..., description="Reference to River collection")
    basin_id: str = Field(..., description="Reference to Basin collection")
    country: str = Field(..., description="Country where the lake is located")
    region: str = Field(..., description="Region or state")
    latitude: float
    longitude: float
    elevation: float
    lake_area: float
    glacier_area: float
    current_risk: str = Field(default="UNKNOWN")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
