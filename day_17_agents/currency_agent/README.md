# Currency Agent

A live currency converter built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `convert_currency` — live rates via [Frankfurter.app](https://www.frankfurter.app/) (free, no key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Convert 500 USD to INR
- How much is 100 euros in Japanese yen?
- What is the GBP to AUD rate?
