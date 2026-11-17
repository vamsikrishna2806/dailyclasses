# Pipeline Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A tiny content factory built with **LangChain + LangGraph + Ollama**: outline → write → edit → headline → measure.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `count_words`, `reading_time` (plain Python helpers in `tools.py`)
- **Architecture**: **Pipeline (assembly line)** — agents work in a fixed order and each one passes its result to the next.

```
START ─► outliner ─► writer ─► editor ─► headline ─► quality_gate ─► END
          (LLM)      (LLM)     (LLM)     (LLM)      (plain code)
```

**Key idea for students:** there is no decision-making here at all. The *edges* are the manager. Pipelines are the simplest, most predictable and most debuggable multi-agent design — use them whenever the steps are always the same.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- Why sleep matters
- Learning to cook
- Benefits of walking
- How volcanoes work
