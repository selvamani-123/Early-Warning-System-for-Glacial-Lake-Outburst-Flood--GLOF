from pydantic import BaseModel, Field

class WeatherHistory(BaseModel):
    id: str = Field(..., description="Unique identifier")
    lake_id: str = Field(..., description="Reference to Lake")
    avg_annual_temp_c: float
    avg_summer_temp_c: float
    annual_precip_mm: float
    historical_source: str = Field(..., description="E.g., Open-Meteo ERA5-Land")
