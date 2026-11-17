# Swarm Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A customer-service desk built with **LangChain + LangGraph + Ollama**: triage → orders → refunds, with agents passing the customer to each other.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `get_order_status`, `issue_refund` (fake order database in `tools.py`)
- **Architecture**: **Swarm (peer-to-peer hand-offs)** — there is no boss — each agent decides who should take over next.

```
START ─► triage ──► orders ──► refunds
             │          │           │
             └──────────┴───────────┴──► DONE ─► END   (every agent can hand off to any other)
```

**Key idea for students:** in a swarm the *routing logic lives inside the agents*. It scales well (add an agent, teach one prompt) but you need guard rails (hop limit, safety net) because nobody supervises.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- Order 5001 arrived broken, I want my money back
- Where is my order 5002?
- I want a refund for order 5003
- Hi, how are you today?
