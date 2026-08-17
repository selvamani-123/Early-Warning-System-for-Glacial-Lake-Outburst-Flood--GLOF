from pydantic import BaseModel, Field
from typing import Optional

class Settlement(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str
    river_id: str
    population_estimate: Optional[int] = None
    distance_from_source_km: float
