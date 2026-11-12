# Travel Agent

A conversational travel agent built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `get_destination_info` — real-time weather via [Open-Meteo](https://open-meteo.com/) (free, no API key)
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

## Example

```
You: I'm planning a trip to Paris next week. What's the weather like?

Agent: Here's what to expect in Paris...
```

## Switching models

Edit `OLLAMA_MODEL` in `agent.py`:

```python
OLLAMA_MODEL = "mistral"      # or qwen2.5, llama3.2:1b, etc.
```
