from pydantic import BaseModel, Field
from typing import List, Any

class RiverMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the river")
    name: str = Field(..., description="Name of the river system")
    country: str = Field(..., description="Country where the river flows")
    basin_id: str = Field(..., description="Reference to Basin collection")
    upstream_lake_ids: List[str] = Field(default_factory=list, description="IDs of upstream glacial lakes")
    settlement_ids: List[str] = Field(default_factory=list, description="IDs of settlements along the river")
    geojson_path: Any = Field(default=None, description="GeoJSON LineString")
