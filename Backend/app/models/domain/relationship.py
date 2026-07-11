from pydantic import BaseModel, Field

class LakeRiverRelationship(BaseModel):
    id: str = Field(..., description="Unique identifier for the relationship")
    lake_id: str
    river_id: str
    lake_name: str
    river_name: str
    distance_to_river_km: float = Field(0.0, description="Distance from the lake to the river main stem")
