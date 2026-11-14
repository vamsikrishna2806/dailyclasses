# Reflection Agent

A self-improving writer built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `count_words` — reports draft length
- **Architecture**: **Reflection** — write → critique → revise, repeated until approved

```
START ─► write ─► critique ──approved?──► END
                     ▲   │ no
                     │   ▼
                     └─ revise
```

**Key idea for students:** the same LLM plays three roles (writer, critic, reviser) using
three different prompts. The critic says `APPROVED` or gives feedback. `MAX_ROUNDS` stops
the loop from running forever.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Queries
- Write a short email asking my boss for Friday off
- Write a product description for a reusable water bottle
- Explain what an API is to a 10-year-old
