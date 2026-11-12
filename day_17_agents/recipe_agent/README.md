# Recipe Agent

A conversational cooking assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `search_recipe` — dish lookup via [TheMealDB](https://www.themealdb.com/) (free, no API key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- How do I make biryani?
- Give me a pasta recipe
- What ingredients do I need for sushi?
