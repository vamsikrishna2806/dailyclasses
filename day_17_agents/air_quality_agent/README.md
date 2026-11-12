# Air Quality Agent

An environmental health assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `get_air_quality` — AQI data via [Open-Meteo Air Quality API](https://open-meteo.com/) (free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Is the air safe in Delhi today?
- What is the air quality in London?
- Should I exercise outside in Beijing?
