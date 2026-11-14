# Human-in-the-Loop Agent

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

Then try replying `make it shorter` once, and `approve` the next time.
