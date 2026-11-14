# Router Agent

A customer-support triage bot built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `lookup_invoice` (billing), `search_kb` (tech) — fake in-memory data, no API key
- **Architecture**: **Router** — one agent classifies the question, then hands it to the right specialist

```
            ┌──► billing agent (lookup_invoice) ──┐
START ─► router ──► tech agent    (search_kb)  ───┼─► END
            └──► general agent  (no tools)     ──┘
```

**Key idea for students:** the router does *not* answer. It only decides *who* answers
(`add_conditional_edges` is the "if / elif / else" of agents).

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Is invoice 1002 paid?
- My wifi keeps dropping
- What are your opening hours?
