import requests
from typing import Optional, Dict, Any

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def geocode_city(city: str, count: int = 5) -> list[dict]:
    """Return a list of matching locations for the given city name."""
    if not city or not city.strip():
        return []
    params = {
        "name": city.strip(),
        "count": count,
        "language": "en",
        "format": "json",
    }
    r = requests.get(GEO_URL, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data.get("results", []) or []

def get_forecast(lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
    """Fetch forecast from Open-Meteo for given coordinates.
    units: "metric" or "imperial"
    """
    temp_unit = "celsius" if units == "metric" else "fahrenheit"
    wind_unit = "kmh" if units == "metric" else "mph"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "windspeed_10m_max"],
        "temperature_unit": temp_unit,
        "windspeed_unit": wind_unit,
        "timezone": "auto",
    }
    r = requests.get(FORECAST_URL, params=params, timeout=60)
    r.raise_for_status()
    return r.json()
