# Fun Facts Agent

An entertainment assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `get_joke` via [JokeAPI](https://jokeapi.dev/) · `get_number_fact` via [NumbersAPI](http://numbersapi.com/) (both free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Tell me a programming joke
- Give me a fun fact about the number 42
- I want a pun joke
