# Currency Agent — Prompts

---

## System Prompt
> Runtime instruction from `agent.py` → `SYSTEM_PROMPT`

```
You are a helpful currency and finance assistant.
When a user asks to convert money or asks about exchange rates, use the
convert_currency tool with the correct amount and currency codes (e.g. USD, EUR, INR, GBP, JPY).
Present the result clearly, mention the rate date, and add brief context
about the currencies involved if relevant.
```

---

## Build Prompt
> Give this to any AI to recreate this agent from scratch

```
Build a conversational currency converter CLI agent in Python using LangChain
and LangGraph with one live exchange rate tool.

STACK
  LLM       : Ollama llama3.2, temperature=0.1 (via langchain-ollama)
  Framework : LangGraph create_react_agent (prebuilt ReAct loop)
  API       : Frankfurter.app (api.frankfurter.app/latest) — free, no key, ECB rates

TOOL (1)
  convert_currency(amount: float, from_currency: str, to_currency: str) -> str
    - GET https://api.frankfurter.app/latest?from={FROM}&to={TO}
    - Extract rate from response["rates"][to_currency]
    - Calculate: converted = amount * rate
    - Return: "X FROM = Y TO", rate, rate date

SYSTEM PROMPT
  "You are a helpful currency and finance assistant. When a user asks to convert
  money or asks about exchange rates, use the convert_currency tool with the
  correct amount and currency codes (e.g. USD, EUR, INR, GBP, JPY). Present the
  result clearly, mention the rate date, and add brief context about the
  currencies involved if relevant."

ENTRY POINT (agent.py)
  Interactive while-loop CLI chat
  Exit on "quit"/"exit"/"q" or Ctrl+C

FILES
  tools.py          ← convert_currency tool
  agent.py          ← build_agent(), ask(), main()
  requirements.txt  ← langchain, langchain-ollama, langgraph, requests
  .venv/
```

---

## Tool Contract
> Exact `@tool` docstring from `tools.py`

```python
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert an amount between any two currencies using live exchange rates.
    Example: amount=100, from_currency='USD', to_currency='INR'.
    Uses Frankfurter.app — free, no API key, updated daily.
    """
```

---

## Example Interaction

```
You: Convert 500 USD to INR

Agent:
500.00 USD = 41,650.00 INR
Exchange rate : 1 USD = 83.30 INR
Rate date     : 2026-11-12

The US Dollar is the world's primary reserve currency, while the Indian Rupee
is managed by the Reserve Bank of India. Rates are updated each business day
from the European Central Bank.
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| `temperature=0.1` | Near-deterministic — financial data must be precise |
| Single tool | One API call converts any currency pair |
| Frankfurter.app | ECB-sourced rates, completely free, no registration |
| Currency codes uppercase in tool | Avoids API errors from lowercase input |
