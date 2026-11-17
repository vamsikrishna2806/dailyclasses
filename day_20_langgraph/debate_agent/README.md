# Debate Agent

> 📘 **New here? Follow the step-by-step guide: [HOW_TO_USE.md](HOW_TO_USE.md)** · 🎨 Open [architecture.html](architecture.html) for the animated diagram.

An argument arena built with **LangChain + LangGraph + Ollama**: PRO vs CON for a fixed number of rounds, then a judge.

- **LLM**: Ollama (local, free) — default `llama3.2`
- **Tools**: `trim_words`, `format_transcript`, `parse_winner` (plain Python helpers in `tools.py`)
- **Architecture**: **Debate (adversarial loop)** — two agents with opposite jobs argue in turns and a neutral judge decides.

```
START ─► pro ─► con ─► more rounds? ──yes──► pro …
                          │
                          no
                          ▼
                        judge ─► END
```

**Key idea for students:** opposite roles + a shared transcript force each side to respond to real counter-arguments. Adversarial loops are great for stress-testing ideas, plans and answers.

## Setup
```bash
pip install -r requirements.txt
ollama pull llama3.2
python agent.py
```

## Example inputs
- Homework should be banned
- Cats are better than dogs
- School should start later in the morning
- Everyone should learn to code
