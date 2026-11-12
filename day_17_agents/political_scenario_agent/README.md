# Political Scenario Agent

A conversational political analysis agent built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `web_search` — real-time search via [DuckDuckGo](https://duckduckgo.com/) (free, no API key)
- **Architecture**: ReAct agent (LangGraph `create_react_agent`)

## Setup

```bash
pip install -r requirements.txt
```

Pull a model (if you haven't already):

```bash
ollama pull llama3.2
```

## Run

```bash
python agent.py
```

## Example Queries

- What is the current political situation in France?
- Analyze the impact of US-China trade tensions.
- What are the key issues in the upcoming UK elections?
- Explain the geopolitical significance of the Taiwan Strait.
- What are the latest developments in Middle East peace talks?

## Switching models

Edit `OLLAMA_MODEL` in `agent.py`:

```python
OLLAMA_MODEL = "mistral"      # or qwen2.5, llama3.2:1b, etc.
```
