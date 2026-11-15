# Hierarchical Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A company org chart built with **LangChain + LangGraph + Ollama**: a manager, two teams, six workers.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `audience_insights` (fake market research data, used by the researcher)
- **Architecture**: **Hierarchical teams (graphs inside a graph)** — a manager delegates to teams, and each team is its own small graph with workers and a lead.

```
            ┌─ product team:   researcher ► spec_writer ► lead ─┐
START ─► manager ◄┤                                                   ├─ report back
    │       └─ marketing team: copywriter ► social_planner ► lead ┘
    └─ FINISH ─► END
```

**Key idea for students:** big systems stay understandable when you *nest* them: the manager reasons about two teams, not six workers. Each team can be built, tested and replaced on its own.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- a note-taking app
- a language learning app
- a fitness app for busy parents
- a budget tracker for students
