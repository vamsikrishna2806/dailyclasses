"""
weather_server.py  -  REAL-TIME data: wraps the free Open-Meteo REST API as MCP tools.
No API key needed.  Try it:  mcp dev servers/weather_server.py

This is the most common real-world MCP pattern:
    LLM  ->  MCP tool  ->  your server  ->  existing REST API  ->  live data
"""
import logging

import httpx
from mcp.server.fastmcp import FastMCP

logging.getLogger("httpx").setLevel(logging.WARNING)   # keep the console quiet

mcp = FastMCP("Weather")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WX_URL = "https://api.open-meteo.com/v1/forecast"
CODES = {0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast", 45: "fog", 48: "fog",
         51: "light drizzle", 53: "drizzle", 55: "heavy drizzle", 61: "light rain", 63: "rain",
         65: "heavy rain", 71: "light snow", 73: "snow", 75: "heavy snow", 80: "rain showers",
         81: "rain showers", 82: "violent rain showers", 95: "thunderstorm", 96: "thunderstorm with hail",
         99: "thunderstorm with hail"}


async def _locate(client: httpx.AsyncClient, city: str) -> dict:
    r = await client.get(GEO_URL, params={"name": city, "count": 1})
    r.raise_for_status()
    hits = r.json().get("results")
    if not hits:
        raise ValueError(f"City '{city}' not found")
    return hits[0]


@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """Get the LIVE current weather for a city (temperature in Celsius, wind, conditions)."""
    async with httpx.AsyncClient(timeout=15) as client:
        place = await _locate(client, city)
        r = await client.get(WX_URL, params={
            "latitude": place["latitude"], "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "timezone": "auto"})
        r.raise_for_status()
        cur = r.json()["current"]
    return {"city": place["name"], "country": place.get("country"), "time": cur["time"],
            "temperature_c": cur["temperature_2m"], "humidity_pct": cur["relative_humidity_2m"],
            "wind_kmh": cur["wind_speed_10m"], "conditions": CODES.get(cur["weather_code"], "unknown")}


@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> list[dict]:
    """Get a daily forecast (min/max Celsius, rain chance) for the next 1-7 days."""
    days = max(1, min(days, 7))
    async with httpx.AsyncClient(timeout=15) as client:
        place = await _locate(client, city)
        r = await client.get(WX_URL, params={
            "latitude": place["latitude"], "longitude": place["longitude"], "forecast_days": days,
            "daily": "temperature_2m_min,temperature_2m_max,precipitation_probability_max,weather_code",
            "timezone": "auto"})
        r.raise_for_status()
        d = r.json()["daily"]
    return [{"date": d["time"][i], "min_c": d["temperature_2m_min"][i], "max_c": d["temperature_2m_max"][i],
             "rain_chance_pct": d["precipitation_probability_max"][i],
             "conditions": CODES.get(d["weather_code"][i], "unknown")} for i in range(len(d["time"]))]


if __name__ == "__main__":
    mcp.run(transport="stdio")
