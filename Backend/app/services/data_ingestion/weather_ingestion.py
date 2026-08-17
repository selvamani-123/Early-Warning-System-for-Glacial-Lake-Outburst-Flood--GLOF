import httpx
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class WeatherIngestionService:
    def __init__(self):
        self.archive_api = "https://archive-api.open-meteo.com/v1/archive"
        self.forecast_api = "https://api.open-meteo.com/v1/forecast"
        
    async def fetch_historical_weather(self, latitude: float, longitude: float, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Fetches historical daily weather from Open-Meteo Archive API.
        start_date and end_date should be 'YYYY-MM-DD'
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_mean", "precipitation_sum", "snowfall_sum"],
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.archive_api, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily", {})
                times = daily.get("time", [])
                temps = daily.get("temperature_2m_mean", [])
                precips = daily.get("precipitation_sum", [])
                snows = daily.get("snowfall_sum", [])
                
                observations = []
                for i in range(len(times)):
                    if temps[i] is None or precips[i] is None:
                        continue
                        
                    obs = {
                        "timestamp": f"{times[i]}T12:00:00Z",
                        "temperature_c": float(temps[i]),
                        "rainfall_mm": float(precips[i]),
                        "snowfall_mm": float(snows[i]) if snows[i] is not None else 0.0,
                        "source": "Open-Meteo",
                        "data_type": "OBSERVED_OR_REANALYSIS"
                    }
                    observations.append(obs)
                return observations
            except Exception as e:
                logger.error(f"Failed to fetch historical weather: {e}")
                return []
                
    async def fetch_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetches current weather from Open-Meteo Forecast API.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "precipitation", "relative_humidity_2m", "snowfall", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
            "daily": ["temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.forecast_api, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                current = data.get("current", {})
                daily = data.get("daily", {})
                
                return {
                    "timestamp": current.get("time"),
                    "temperature_c": current.get("temperature_2m"),
                    "min_temperature_c": daily.get("temperature_2m_min", [None])[0] if daily.get("temperature_2m_min") else None,
                    "rainfall_mm": current.get("precipitation"),
                    "precip_24h_mm": daily.get("precipitation_sum", [None])[0] if daily.get("precipitation_sum") else None,
                    "humidity_percent": current.get("relative_humidity_2m"),
                    "snowfall_mm": current.get("snowfall"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "wind_direction": current.get("wind_direction_10m"),
                    "wind_gusts": current.get("wind_gusts_10m"),
                    "source": "Open-Meteo",
                    "data_type": "OBSERVED"
                }
            except Exception as e:
                logger.error(f"Failed to fetch current weather: {e}")
                return None
