# Wikipedia Agent

A research assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `search_wikipedia` — summaries via [Wikipedia API](https://pypi.org/project/wikipedia/) (free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Who is Marie Curie?
- Explain the French Revolution
- What is quantum computing?
