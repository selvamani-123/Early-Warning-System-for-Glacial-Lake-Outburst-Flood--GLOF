import httpx

class WeatherService:
    @staticmethod
    async def get_current_weather(lat: float, lon: float):
        """
        Fetches live weather data for a given location using Open-Meteo.
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                current = data.get("current", {})
                
                return {
                    "temperature": current.get("temperature_2m", 0),
                    "humidity": current.get("relative_humidity_2m", 0),
                    "precipitation": current.get("precipitation", 0)
                }
            except Exception as e:
                print(f"Error fetching weather: {e}")
                return None
