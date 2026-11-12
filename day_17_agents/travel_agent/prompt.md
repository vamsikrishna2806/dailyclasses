# Travel Assistant Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a friendly and knowledgeable travel assistant.
When a user asks about a travel destination, use the get_destination_info tool
to fetch real-time weather and conditions. Based on the data, give helpful,
concise travel advice — what to pack, best activities, and anything relevant
for the trip. Always be encouraging and practical.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational travel assistant CLI agent in Python using LangChain
and LangGraph with one real-time weather tool.

STACK
  LLM       : Ollama llama3.2, temperature=0.3 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  API       : Open-Meteo Geocoding + Weather (free, no API key)
    Geocoding : https://geocoding-api.open-meteo.com/v1/search
    Weather   : https://api.open-meteo.com/v1/forecast

TOOL (1)

  get_destination_info(city: str) -> str

  Step 1 — Geocode:
    GET geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en
    Extract: latitude, longitude, country, name

  Step 2 — Fetch weather:
    GET api.open-meteo.com/v1/forecast with params:
      current  = temperature_2m, apparent_temperature,
                 relative_humidity_2m, wind_speed_10m, weathercode
      daily    = temperature_2m_max, temperature_2m_min,
                 precipitation_probability_max, weathercode
      forecast_days=3, timezone=auto

  Step 3 — Format response:
    Map WMO weathercode integers to human-readable labels:
      0→"Clear sky", 1→"Mainly clear", 2→"Partly cloudy", 3→"Overcast",
      45→"Foggy", 51→"Light drizzle", 61→"Light rain", 63→"Moderate rain",
      65→"Heavy rain", 71→"Light snow", 80→"Rain showers", 95→"Thunderstorm"
      (and ~10 more codes)

    Apply travel tip based on current temperature:
      < 5°C  → "Very cold — pack heavy winter clothing."
      < 15°C → "Cool weather — bring a jacket."
      ≤ 28°C → "Pleasant weather — great for sightseeing!"
      ≤ 35°C → "Warm — stay hydrated and use sunscreen."
      > 35°C → "Extremely hot — limit outdoor activities midday."

    Return multi-line string:
      "=== Travel Info: {City}, {Country} ===
      Current Conditions: {condition}
      Temperature: {temp}°C (feels like {feels}°C)
      Humidity: {humidity}%  |  Wind: {wind} km/h

      3-Day Forecast:
        DATE: lo°C – hi°C | condition | Rain: XX%
        DATE: ...
        DATE: ...

      Travel Tip: ..."

SYSTEM PROMPT
  "You are a friendly and knowledgeable travel assistant.
  When a user asks about a travel destination, use the get_destination_info
  tool to fetch real-time weather and conditions. Based on the data, give
  helpful, concise travel advice — what to pack, best activities, and anything
  relevant for the trip. Always be encouraging and practical."

ENTRY POINT (agent.py)
  build_agent() → ChatOllama + create_react_agent + tools=[get_destination_info]
  ask(agent, user_input) →
    invoke with [SystemMessage(SYSTEM_PROMPT), HumanMessage(user_input)]
    return result["messages"][-1].content
  main():
    - Print header: model name + tool name
    - Interactive while-loop, exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← get_destination_info tool definition
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring the LLM reads from `tools.py`

```python
@tool
def get_destination_info(city: str) -> str:
    """
    Get current weather and 3-day travel forecast for any destination city.
    Returns temperature, conditions, humidity, wind speed, and travel tips.
    Uses free Open-Meteo API — no API key required.
    """
```

---

## Example Interaction

```
You: I'm planning a trip to Tokyo next week. What should I expect?

Agent:
Here's the latest for Tokyo, Japan:

Current: 14°C (feels like 11°C), Partly cloudy
Humidity: 68%  |  Wind: 18 km/h

3-Day Forecast:
  2026-11-12: 10°C – 16°C | Mainly clear | Rain: 10%
  2026-11-13: 11°C – 17°C | Partly cloudy | Rain: 20%
  2026-11-14: 9°C  – 15°C | Light rain    | Rain: 65%

Travel Tip: Cool weather — bring a jacket.

Tokyo in mid-November is lovely for sightseeing — expect crisp autumn
weather with beautiful foliage. Pack layers and a light waterproof jacket
for the later part of the week. The Imperial Palace gardens and Shinjuku
Gyoen are stunning this time of year!
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.3` | Slight creativity for warm, helpful travel advice tone |
| Single tool | One well-scoped tool is enough; geocoding + weather combined |
| WMO code mapping in tool | LLM receives human-readable labels, not raw integers |
| Travel tip thresholds in tool | Deterministic packing advice based on actual temperature |
| `create_react_agent` | Simpler than `create_agent`; built-in ReAct loop with tool calling |
