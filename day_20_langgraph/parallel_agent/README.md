# Parallel Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A trip planner built with **LangChain + LangGraph + Ollama**: three specialists work at the same time and a planner merges their findings.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `search_flights`, `search_hotels`, `search_activities` (fake offline travel data in `tools.py`)
- **Architecture**: **Parallel (fan-out / fan-in)** — independent jobs run at the same time, then one agent merges the results.

```
            ┌─► flights    ─┐
START ──────┼─► hotels     ─┼──► planner ─► END
            └─► activities ─┘
```

**Key idea for students:** *fan-out* starts several nodes together; *fan-in* (an edge from a **list** of nodes) waits for all of them. Independent work should never wait in a queue.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- Paris
- Tokyo
- Goa
- I want to visit New York
