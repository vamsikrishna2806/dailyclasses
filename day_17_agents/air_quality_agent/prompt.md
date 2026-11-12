# Air Quality Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are an environmental health assistant specializing in air quality.
When a user asks about air quality in a city, use the get_air_quality tool
to fetch real-time data. Explain the AQI level in plain language — what it means
for health, who should be cautious, and what precautions to take.
Always be clear about what the numbers mean for everyday decisions.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational air quality monitoring CLI agent in Python using LangChain
and LangGraph with one air quality tool using the Open-Meteo API.

STACK
  LLM       : Ollama llama3.2, temperature=0.2 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  APIs      : Open-Meteo Geocoding + Air Quality — both free, no key

TOOL (1)
  get_air_quality(city: str) -> str
    Step 1 — Geocode:
      GET https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1
      Extract: lat, lon, country
    Step 2 — Air Quality:
      GET https://air-quality-api.open-meteo.com/v1/air-quality
          ?latitude={lat}&longitude={lon}
          &hourly=pm10,pm2_5,carbon_monoxide,european_aqi
          &forecast_days=1
      Extract latest index (last non-None) of each variable
    Map european_aqi to label: 0-20=Good, 21-40=Fair, 41-60=Moderate,
      61-80=Poor, 81-100=Very Poor, >100=Extremely Poor
    Return: city, country, AQI label, AQI value, PM10, PM2.5, CO

SYSTEM PROMPT
  "You are an environmental health assistant specializing in air quality. When
  a user asks about air quality in a city, use the get_air_quality tool to fetch
  real-time data. Explain the AQI level in plain language — what it means for
  health, who should be cautious, and what precautions to take. Always be clear
  about what the numbers mean for everyday decisions."

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← get_air_quality tool
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def get_air_quality(city: str) -> str:
    """
    Get real-time air quality data for any city: European AQI, PM10, PM2.5,
    and carbon monoxide levels. Uses Open-Meteo Air Quality API — free, no API key.
    """
```

---

## Example Interaction

```
You: What's the air quality like in Delhi?

Agent:
City    : Delhi, India
AQI     : Poor (72)
PM10    : 85.3 µg/m³
PM2.5   : 42.1 µg/m³
CO      : 320.5 µg/m³

Air quality in Delhi is currently Poor. This level can cause breathing
discomfort for people with asthma, heart disease, or other respiratory conditions.
Sensitive groups should avoid prolonged outdoor activity.
Everyone else should consider wearing an N95 mask if going outside for extended periods.
Children and elderly should stay indoors where possible.
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.2` | Health information must be conservative and accurate |
| Two-step API (geocode → AQ) | Open-Meteo AQ API requires lat/lon, not city name |
| European AQI scale | 0-100+ scale with 6 clear bands maps easily to plain language |
| Latest non-None index | Hourly data can have trailing nulls; scan backwards for valid reading |
| PM10, PM2.5, CO | The three most health-relevant pollutants for urban environments |
