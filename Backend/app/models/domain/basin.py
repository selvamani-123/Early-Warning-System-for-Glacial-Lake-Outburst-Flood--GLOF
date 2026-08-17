from pydantic import BaseModel, Field

class BasinMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the basin")
    name: str = Field(..., description="River basin name")
    country: str
    area_km2: float = Field(default=0.0)
