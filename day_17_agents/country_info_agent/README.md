# Country Info Agent

A geography facts assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `get_country_info` — facts via [RestCountries API](https://restcountries.com/) (free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Tell me about Japan
- What language do they speak in Brazil?
- What is the currency of Switzerland?
