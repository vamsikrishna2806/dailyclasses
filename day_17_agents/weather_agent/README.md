# Weather Prediction Agent (LangChain + Ollama)

An AI agent that fetches the last 7 days of real temperatures from a free weather API
(Open-Meteo, no API key needed), works out the trend, and predicts tomorrow's max temperature
using a local Ollama model. At the end it compares its guess with Open-Meteo's official forecast.

| Agent part | In this code |
|---|---|
| 🧠 Brain | `ChatOllama(model="llama3.2")` |
| ✋ Hands | `get_past_temperatures`, `temperature_trend` tools |
| ❤️ Rules | `system_prompt` |
| 🔁 Loop | `create_agent(...)` runs think → act → observe |

## Setup (Windows, PowerShell)

```powershell
ollama pull llama3.2
cd D:\getwork\day_17\weather_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py Hyderabad
```

`ormsgpack` is pinned to 1.13.0 because Windows Smart App Control on this PC blocks 1.13.1.

## Try next
- Try another city: `python main.py Delhi`
- Add a tool that returns humidity or rain (`daily=precipitation_sum` in the API call)
- Swap `llama3.2` for a bigger model and compare the predictions
