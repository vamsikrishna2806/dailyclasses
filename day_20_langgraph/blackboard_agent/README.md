# Blackboard Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A meal-planning team built with **LangChain + LangGraph + Ollama**: nutritionist, chef, shopper and auditor share one board.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `price_of`, `parse_list`, `parse_budget`, `pantry_text` (fake grocery prices in `tools.py`)
- **Architecture**: **Blackboard (shared workspace)** — specialists never talk to each other — they watch a shared board and add their part when they can.

```
        nutritionist ◄─┐         ┌─► chef
                       ▼         ▼
                   📋  SHARED BOARD  📋
                       ▲         ▲
        auditor ◄──────┘         └──► shopper
   controller (plain code): who CAN contribute now?
```

**Key idea for students:** coordination through *shared state* instead of messages. Adding or removing a specialist does not change any other specialist — they only look at the board.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- Vegetarian dinners for 3 days under $20
- Cheap high-protein dinners for 3 days under $25
- Kid-friendly dinners for 3 days under $18
