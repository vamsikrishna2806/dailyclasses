import requests
from langchain_core.tools import tool


@tool
def get_country_info(country: str) -> str:
    """
    Get detailed facts about any country: capital, population, area, languages,
    currency, region, and more. Uses RestCountries API — free, no API key.
    """
    r = requests.get(
        f"https://restcountries.com/v3.1/name/{country.strip()}",
        timeout=10
    )
    if r.status_code != 200:
        return f"Country '{country}' not found. Try the full English name."

    data = r.json()[0]
    capital = (data.get("capital") or ["N/A"])[0]
    population = data.get("population", 0)
    area = data.get("area", 0)
    region = data.get("region", "N/A")
    subregion = data.get("subregion", "N/A")
    languages = ", ".join(data.get("languages", {}).values()) or "N/A"
    currencies = ", ".join(
        f"{v['name']} ({v.get('symbol', '')})"
        for v in data.get("currencies", {}).values()
    ) or "N/A"
    timezones = ", ".join(data.get("timezones", [])[:3])
    un_member = "Yes" if data.get("unMember") else "No"
    borders = ", ".join(data.get("borders", [])) or "None / Island nation"

    return (
        f"Country    : {data['name']['common']} ({data['name']['official']})\n"
        f"Capital    : {capital}\n"
        f"Region     : {region} → {subregion}\n"
        f"Population : {population:,}\n"
        f"Area       : {area:,.0f} km²\n"
        f"Languages  : {languages}\n"
        f"Currency   : {currencies}\n"
        f"Timezones  : {timezones}\n"
        f"Borders    : {borders}\n"
        f"UN Member  : {un_member}"
    )
