# Weather Prediction Agent — Prompts

---

## System Prompt
> Runtime instruction given to the LLM inside `main.py`

```
You are a weather analyst. To predict tomorrow's max temperature:
1. Call get_past_temperatures for the city.
2. Call temperature_trend for the same city.
3. Answer with: the predicted max temperature for tomorrow (one number in °C),
   and one or two short sentences explaining why, based on the data.

Never invent temperatures. Only use numbers that came from the tools.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a CLI weather prediction agent in Python using LangChain and LangGraph
that predicts tomorrow's max temperature from 7-day historical data.

STACK
  LLM       : Ollama llama3.2, temperature=0 (via langchain-ollama)
  Framework : LangChain create_agent with LangGraph backend
  API       : Open-Meteo (free, no API key)
    Geocoding : https://geocoding-api.open-meteo.com/v1/search
    Weather   : https://api.open-meteo.com/v1/forecast

TOOLS (2)

  get_past_temperatures(city: str) -> str
    - Geocode city name to lat/lon via Open-Meteo Geocoding API
    - Fetch past_days=7, forecast_days=1 with daily temperature_2m_max and
      temperature_2m_min fields
    - Return formatted string: "City, Country:\nDATE: max X°C, min Y°C\n..."

  temperature_trend(city: str) -> str
    - Fetch last 7 days of max temperatures (same API call)
    - Compute linear regression slope (°C per day) with least-squares formula
    - Compute straight-line next value and 3-day moving average
    - Return: "trend: ±X.XX °C per day | straight-line next value: Y.Y°C |
      average of last 3 days: Z.Z°C"

SYSTEM PROMPT
  "You are a weather analyst. To predict tomorrow's max temperature:
  1. Call get_past_temperatures for the city.
  2. Call temperature_trend for the same city.
  3. Answer with: the predicted max temperature for tomorrow (one number in °C),
     and one or two short sentences explaining why, based on the data.
  Never invent temperatures. Only use numbers that came from the tools."

ENTRY POINT (main.py — single file, tools + agent together)
  - Accept city via sys.argv or interactive input(), default "Hyderabad"
  - Build question: "Predict tomorrow's maximum temperature in {city}."
  - Stream agent with stream_mode="values"
  - Print each step:
      🧠 THINK → ACT  : tool call name + args
      🔎 OBSERVE      : tool result
      🤖 Answer       : final LLM response
  - After agent finishes, fetch Open-Meteo official forecast for tomorrow
    and print it for comparison

FILES
  main.py           ← tools + agent + main logic (single file)
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contracts
> Exact `@tool` docstrings the LLM reads to decide when to call each tool

```python
@tool
def get_past_temperatures(city: str) -> str:
    """Get the real daily max and min temperatures (°C) for the last 7 days
    in a city, plus today. Use this first to see recent weather."""

@tool
def temperature_trend(city: str) -> str:
    """Calculate the trend of the last 7 days of max temperatures in a city:
    how much it changes per day and the next value on the trend line.
    Use this to do the maths instead of guessing."""
```

---

## Example Interaction

```
You: Predict tomorrow's maximum temperature in Hyderabad.

🧠 THINK → ACT: call get_past_temperatures({'city': 'Hyderabad'})
🔎 OBSERVE (get_past_temperatures):
Hyderabad, India:
2026-11-05: max 32.4°C, min 21.1°C
...

🧠 THINK → ACT: call temperature_trend({'city': 'Hyderabad'})
🔎 OBSERVE (temperature_trend):
trend: -0.31 °C per day | straight-line next value: 31.1°C | average of last 3 days: 31.6°C

🤖 Agent's prediction:
Tomorrow's predicted maximum temperature in Hyderabad is 31°C.
The slight downward trend over the past week and the 3-day average of 31.6°C
both point to a mild cool-down.

📡 Official Open-Meteo forecast for tomorrow → 2026-11-13: max 31.2°C, min 20.8°C
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0` | Deterministic — the agent must not guess numbers |
| 2 tools instead of 1 | Small models struggle with arithmetic; tool does the maths |
| Tools fetch data themselves | Avoids asking the LLM to pass raw number lists as arguments |
| Single file (`main.py`) | Simple demo — no need to split tools and agent |
| Streaming with `stream_mode="values"` | Shows every ReAct step in real time |
