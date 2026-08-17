import httpx
import logging
from typing import List, Dict, Any
import datetime

logger = logging.getLogger(__name__)

class GlofasIngestionService:
    def __init__(self):
        self.flood_api = "https://flood-api.open-meteo.com/v1/flood"
        
    async def fetch_historical_discharge(self, latitude: float, longitude: float, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Fetches historical daily river discharge from Open-Meteo Flood API.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["river_discharge"],
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.flood_api, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()
                
                daily = data.get("daily", {})
                times = daily.get("time", [])
                discharges = daily.get("river_discharge", [])
                
                observations = []
                for i in range(len(times)):
                    if discharges[i] is None:
                        continue
                        
                    obs = {
                        "timestamp": f"{times[i]}T12:00:00Z",
                        "discharge_m3s": float(discharges[i]),
                        "source": "GloFAS",
                        "data_type": "MODELED"
                    }
                    observations.append(obs)
                return observations
            except Exception as e:
                logger.error(f"Failed to fetch historical discharge: {e}")
                return []
                
    async def fetch_current_discharge(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetches current forecast/latest modeled river discharge.
        We'll use a short forecast window to ensure we get today's value.
        """
        now = datetime.datetime.utcnow()
        start = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")
        
        obs = await self.fetch_historical_discharge(latitude, longitude, start, end)
        if obs:
            return obs[-1]
        return None
