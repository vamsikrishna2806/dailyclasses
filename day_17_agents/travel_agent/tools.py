import requests
from langchain_core.tools import tool


WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail",
}


@tool
def get_destination_info(city: str) -> str:
    """
    Get current weather and 3-day travel forecast for any destination city.
    Returns temperature, conditions, humidity, wind speed, and travel tips.
    Uses free Open-Meteo API — no API key required.
    """
    # Step 1: Geocode city → lat/lon
    geo_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    geo_data = geo_resp.json()

    if not geo_data.get("results"):
        return f"Sorry, I could not find the location '{city}'. Please check the city name."

    loc = geo_data["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    country = loc.get("country", "Unknown")
    full_name = f"{loc['name']}, {country}"

    # Step 2: Fetch current weather + 3-day forecast
    weather_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode,apparent_temperature",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "timezone": "auto",
            "forecast_days": 3,
        },
        timeout=10,
    )
    data = weather_resp.json()

    cur = data.get("current", {})
    daily = data.get("daily", {})

    temp = cur.get("temperature_2m", "N/A")
    feels = cur.get("apparent_temperature", "N/A")
    humidity = cur.get("relative_humidity_2m", "N/A")
    wind = cur.get("wind_speed_10m", "N/A")
    condition = WMO_CODES.get(cur.get("weathercode", 0), "Unknown")

    # Build 3-day forecast string
    forecast_lines = []
    for i in range(min(3, len(daily.get("time", [])))):
        date = daily["time"][i]
        hi = daily["temperature_2m_max"][i]
        lo = daily["temperature_2m_min"][i]
        rain = daily["precipitation_probability_max"][i]
        cond = WMO_CODES.get(daily["weathercode"][i], "Unknown")
        forecast_lines.append(f"  {date}: {lo}°C – {hi}°C | {cond} | Rain: {rain}%")

    # Travel tip based on current temp
    try:
        t = float(temp)
        if t < 5:
            tip = "Very cold — pack heavy winter clothing."
        elif t < 15:
            tip = "Cool weather — bring a jacket."
        elif t <= 28:
            tip = "Pleasant weather — great for sightseeing!"
        elif t <= 35:
            tip = "Warm — stay hydrated and use sunscreen."
        else:
            tip = "Extremely hot — limit outdoor activities midday."
    except (ValueError, TypeError):
        tip = "Check local conditions before travelling."

    forecast_text = "\n".join(forecast_lines) if forecast_lines else "  Not available"

    return (
        f"=== Travel Info: {full_name} ===\n"
        f"Current Conditions: {condition}\n"
        f"Temperature: {temp}°C (feels like {feels}°C)\n"
        f"Humidity: {humidity}%  |  Wind: {wind} km/h\n\n"
        f"3-Day Forecast:\n{forecast_text}\n\n"
        f"Travel Tip: {tip}"
    )
