from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class HistoricalEvent(BaseModel):
    id: str = Field(..., description="Unique identifier for the historical event")
    lake_id: str = Field(..., description="Reference to Lake")
    event_date: datetime
    volume_released_m3: Optional[float] = Field(None, description="Estimated volume of water released in cubic meters")
    impact_description: str = Field(..., description="Description of the downstream impact")
    casualties: Optional[int] = Field(None, description="Number of casualties, if known")
