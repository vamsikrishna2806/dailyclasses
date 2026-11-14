# Human-in-the-Loop Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)**

An email assistant that **never sends anything without your approval**, built with
**LangChain + LangGraph + Ollama**.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tool**: `send_email` — the risky action; saves to `outbox.txt` for the demo
- **Architecture**: **Human-in-the-loop** — the graph pauses with `interrupt()` until a person decides

```
START ─► draft ─► human_review ──"approve"──► send ─► END
            ▲         │  (PAUSED: waits for you)
            └─────────┘  "make it shorter" → redraft
```

**Key idea for students:** `interrupt()` freezes the graph and saves its state (via the
`MemorySaver` checkpointer). Your answer is passed back with `Command(resume=...)` and the graph
continues exactly where it stopped. Use this pattern for anything irreversible: payments,
emails, deleting data.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example Requests
- Ask Priya to move tomorrow's meeting to 3pm
- Thank my teacher for the great class
- Politely decline the invitation to the Saturday event

The agent asks four numbered questions (your name, what to say, recipient email, recipient name)
and re-asks if an answer looks wrong. An empty Enter never sends. It asks for your name once, so drafts are signed
properly (no `[Your Name]` placeholders). Try replying `make it shorter` once, then reply with
just `approve` to send — "change X and approve" is treated as a change, so you review the new draft first.
