# Stock Agent

A live stock market data assistant built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `get_stock_price` — market data via [yfinance](https://pypi.org/project/yfinance/) (free, no API key)
- **Architecture**: ReAct agent (`create_react_agent`)

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- What is Apple's stock price?
- How is Tesla doing today?
- Show me RELIANCE.NS stock info

> **Note**: Informational only — not financial advice.
