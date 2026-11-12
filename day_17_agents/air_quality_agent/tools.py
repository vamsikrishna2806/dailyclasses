import requests
from langchain_core.tools import tool


AQI_LABELS = [
    (20,  "Good",           "Air quality is excellent. Safe for all outdoor activities."),
    (40,  "Fair",           "Air quality is acceptable. Sensitive groups should monitor."),
    (60,  "Moderate",       "Some pollutants present. Unusually sensitive people may notice."),
    (80,  "Poor",           "Everyone may start to experience health effects."),
    (100, "Very Poor",      "Health warnings. Limit prolonged outdoor exertion."),
    (999, "Extremely Poor", "Health alert — everyone should avoid outdoor activity."),
]


@tool
def get_air_quality(city: str) -> str:
    """
    Get current air quality index (AQI) and pollution levels for any city.
    Returns PM2.5, PM10, ozone, NO₂, CO readings and health advice.
    Uses Open-Meteo Air Quality API — free, no API key.
    """
    # Geocode city
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city.strip(), "count": 1},
        timeout=10
    ).json()

    if not geo.get("results"):
        return f"City '{city}' not found."

    loc = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]
    full_name = f"{loc['name']}, {loc.get('country', '')}"

    # Fetch air quality
    aq = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "european_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone",
        },
        timeout=10
    ).json()

    cur = aq.get("current", {})
    aqi = cur.get("european_aqi", None)

    label, advice = "Unknown", "No advice available."
    if aqi is not None:
        for threshold, lbl, adv in AQI_LABELS:
            if aqi <= threshold:
                label, advice = lbl, adv
                break

    return (
        f"Air Quality: {full_name}\n"
        f"AQI (European) : {aqi} — {label}\n"
        f"Health Advice  : {advice}\n\n"
        f"PM2.5 : {cur.get('pm2_5', 'N/A')} µg/m³\n"
        f"PM10  : {cur.get('pm10', 'N/A')} µg/m³\n"
        f"NO₂   : {cur.get('nitrogen_dioxide', 'N/A')} µg/m³\n"
        f"Ozone : {cur.get('ozone', 'N/A')} µg/m³\n"
        f"CO    : {cur.get('carbon_monoxide', 'N/A')} µg/m³"
    )
