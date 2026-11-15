# Voting Panel Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

A spam-checking panel built with **LangChain + LangGraph + Ollama**: three jurors vote in parallel, code counts, a judge breaks ties.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `spam_signals` (counts links, urgent/money words, caps), `parse_vote`, `tally`
- **Architecture**: **Voting / ensemble** — several agents with different personalities judge the same input and the majority wins.

```
            ┌─► strict   ─┐
START ──────┼─► friendly ─┼──► tally ──┬─ majority ─► END
            └─► evidence ─┘            └─ split ────► judge ─► END
```

**Key idea for students:** *diverse* opinions + *simple counting* beat a single opinion. Use code (not an LLM) to combine the votes so the rule is transparent and repeatable.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- URGENT!!! You WON a FREE gift card, claim now at http://bit.ly/x1
- Hi Sam, are we still meeting for lunch at 1pm tomorrow?
- Your package delivery is delayed. Confirm your address to reschedule: www.parcel-help.net
- Congratulations! Your invoice 4521 is attached. Please review at www.docs-share.co
