from pydantic import BaseModel, Field
from typing import Optional

class GlacierMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the glacier")
    name: str = Field(..., description="Glacier name")
    country: str = Field(..., description="Country")
    basin_id: str = Field(..., description="Reference to Basin collection")
    glims_id: Optional[str] = Field(None, description="GLIMS database identifier")
    area_km2: float = Field(..., description="Glacier area in square kilometers")
    latitude: float
    longitude: float
