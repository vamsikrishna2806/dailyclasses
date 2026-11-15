# RAG Team Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A trustworthy handbook assistant built with **LangChain + LangGraph + Ollama**: rewrite → retrieve → answer → fact-check.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `search_docs`, `format_context`, `keywords` (a tiny offline handbook in `tools.py`)
- **Architecture**: **Multi-agent RAG (retrieve · answer · verify)** — one agent finds sources, one answers only from them, and a checker sends unsupported answers back.

```
START ─► rewriter ─► retriever ─► found? ──no──► no_answer ─► END
                               │yes
                               ▼
                    answerer ─► checker ─► grounded? ──yes──► END
                        ▲                     │ no (rounds left)
                        └─────────────────────┘
```

**Key idea for students:** RAG answers are only as good as their *grounding*. A dedicated checker, and an honest "I don't know" path, turn a chatty model into a source-based assistant.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- How many vacation days do I get?
- Can I work from home?
- What is the password policy?
- How much can I claim for meals while travelling?
- What is the CEO's salary?   ← NOT in the handbook on purpose!
