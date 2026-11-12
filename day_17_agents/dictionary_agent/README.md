# Dictionary Agent

A vocabulary assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `define_word` — definitions via [Free Dictionary API](https://dictionaryapi.dev/) (free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- What does ephemeral mean?
- Define serendipity
- Give me synonyms for happy
