# Supervisor Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)**

A mini newsroom built with **LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `wiki_summary` — facts from the [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/) (free, no key)
- **Architecture**: **Supervisor with workers** — a boss agent delegates to specialists and takes their results back

```
              ┌──────────── researcher (wiki tool) ◄──┐
START ─► supervisor ◄──────── writer                  │  every worker
              │  ◄──────────── proofreader            │  reports back
              └─ FINISH ─► END
```

**Key idea for students:** unlike the Router (one hop, then done), workers always return to the
supervisor, who looks at progress and decides the *next* worker — until it says `FINISH`.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Topics
- Black holes
- The Eiffel Tower
- Photosynthesis
