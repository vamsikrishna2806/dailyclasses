# Planner-Executor Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A careful problem solver built with **LangChain + LangGraph + Ollama**: plan → execute step by step with a calculator tool → answer.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `calculator` (safe maths), `unit_convert` (bonus tool for experiments)
- **Architecture**: **Plan-and-Execute** — think first and write a plan, then do the plan one step at a time with tools.

```
START ─► planner ─► executor ─► more steps? ──yes──► executor …
                                  │
                                  no
                                  ▼
                              answerer ─► END
```

**Key idea for students:** separating *thinking* (planner) from *doing* (executor) makes long tasks reliable: every step is small, checkable and uses an exact tool instead of the model's guesswork.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- I buy 3 pens at $2 and 4 notebooks at $5, then get a 10% discount on the total. How much do I pay?
- Tickets cost $8 each. I buy 5 tickets and one $3 snack. What is the total?
- I have $50 and spend $12 on a book and $9 on lunch. How much is left?
- A bike costs $200 and a helmet $30, then 10% off the total. What do I pay?
