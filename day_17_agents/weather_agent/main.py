"""Weather Prediction Agent · LangChain + Ollama

The agent gets the last 7 days of real temperatures for a city from a free
weather API (Open-Meteo, no API key), works out the trend, and predicts
tomorrow's max temperature. At the end we compare its guess with
Open-Meteo's official forecast.

Run (with the venv active):
    python main.py                 # asks for a city
    python main.py Hyderabad       # or pass the city directly

Needs Ollama running with:  ollama pull llama3.2
"""

import sys
import requests
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
MODEL = "llama3.2"


# ---------- helpers (plain Python, not tools) ----------

def find_city(city: str) -> dict:
    """Turn a city name into latitude/longitude."""
    r = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=15)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        raise ValueError(f"City '{city}' not found")
    return results[0]


def fetch_daily(city: str, past_days: int, forecast_days: int) -> dict:
    """Get daily max/min temperatures from Open-Meteo."""
    place = find_city(city)
    r = requests.get(WEATHER_URL, params={
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min",
        "past_days": past_days,
        "forecast_days": forecast_days,
        "timezone": "auto",
    }, timeout=15)
    r.raise_for_status()
    return {"place": place, "daily": r.json()["daily"]}


# ---------- TOOLS: the agent's "hands" ----------

@tool
def get_past_temperatures(city: str) -> str:
    """Get the real daily max and min temperatures (°C) for the last 7 days
    in a city, plus today. Use this first to see recent weather."""
    data = fetch_daily(city, past_days=7, forecast_days=1)
    d, p = data["daily"], data["place"]
    lines = [f"{p['name']}, {p.get('country', '')}:"]
    for day, tmax, tmin in zip(d["time"], d["temperature_2m_max"], d["temperature_2m_min"]):
        lines.append(f"{day}: max {tmax}°C, min {tmin}°C")
    return "\n".join(lines)


@tool
def temperature_trend(city: str) -> str:
    """Calculate the trend of the last 7 days of max temperatures in a city:
    how much it changes per day and the next value on the trend line.
    Use this to do the maths instead of guessing."""
    # The tool fetches the numbers itself. Small local models (llama3.2 3B)
    # often break when they have to copy a list of numbers into a tool call.
    max_temps = fetch_daily(city, past_days=7, forecast_days=1)["daily"]["temperature_2m_max"]
    max_temps = [t for t in max_temps if t is not None]
    n = len(max_temps)
    if n < 2:
        return "Need at least 2 temperatures."
    xs = range(n)
    x_mean = sum(xs) / n
    y_mean = sum(max_temps) / n
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, max_temps)) / \
            sum((x - x_mean) ** 2 for x in xs)
    next_value = y_mean + slope * (n - x_mean)
    avg_last3 = sum(max_temps[-3:]) / min(3, n)
    return (f"trend: {slope:+.2f} °C per day | "
            f"straight-line next value: {next_value:.1f} °C | "
            f"average of last 3 days: {avg_last3:.1f} °C")


# ---------- THE AGENT: brain (LLM) + hands (tools) + rules (system prompt) ----------

agent = create_agent(
    model=ChatOllama(model=MODEL, temperature=0),
    tools=[get_past_temperatures, temperature_trend],
    system_prompt=(
        "You are a weather analyst. To predict tomorrow's max temperature:\n"
        "1. Call get_past_temperatures for the city.\n"
        "2. Call temperature_trend for the same city.\n"
        "3. Answer with: the predicted max temperature for tomorrow (one number in °C), "
        "and one or two short sentences explaining why, based on the data.\n"
        "Never invent temperatures. Only use numbers that came from the tools."
    ),
)


def official_forecast(city: str) -> str:
    """Open-Meteo's own forecast for tomorrow, to check the agent's guess."""
    d = fetch_daily(city, past_days=0, forecast_days=2)["daily"]
    return f"{d['time'][1]}: max {d['temperature_2m_max'][1]}°C, min {d['temperature_2m_min'][1]}°C"


if __name__ == "__main__":
    city = " ".join(sys.argv[1:]) or input("City: ").strip() or "Hyderabad"
    question = f"Predict tomorrow's maximum temperature in {city}."
    print(f"\n🧑 You: {question}\n")

    # stream_mode="values" shows each step of the loop as it happens
    seen = 1  # skip our own question (message 0)
    for step in agent.stream({"messages": [{"role": "user", "content": question}]},
                             stream_mode="values"):
        # the agent may call several tools at once, so print every new message
        for msg in step["messages"][seen:]:
            if msg.type == "ai" and msg.tool_calls:
                for call in msg.tool_calls:
                    print(f"🧠 THINK → 🛠️ ACT: call {call['name']}({call['args']})")
            elif msg.type == "tool":
                print(f"🔎 OBSERVE ({msg.name}):\n{msg.content}\n")
            elif msg.type == "ai":
                print(f"🤖 Agent's prediction:\n{msg.content}\n")
        seen = len(step["messages"])

    print(f"📡 Official Open-Meteo forecast for tomorrow → {official_forecast(city)}")
